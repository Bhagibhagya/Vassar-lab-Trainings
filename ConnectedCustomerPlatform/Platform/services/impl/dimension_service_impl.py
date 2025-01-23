import base64
import logging
import uuid
from datetime import datetime
from uuid import uuid4
from io import BytesIO
from django.conf import settings
import pandas as pd
import pytz
from dataclasses import asdict
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework import status
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from ConnectedCustomerPlatform.responses import CustomResponse
from EmailApp.DataClasses.response.pagination_data import PaginationResponse
from Platform.chroma_utils import map_intent_sub_intents_for_query, get_duplicate_rows, \
    update_or_skip_examples, get_current_unix_timestamp, update_dimension_wise_count, prepare_metadata
from Platform.constant.constants import ChromaExcelSheet, EXPECTED_COLUMNS, DOWNLOAD_INTENT_EXCEL_NAME, \
    DIMENSION_TYPE_INTENT, SPREAD_SHEET_MACRO_ENABLED, ChromaUtils
from Platform.services.interface.dimension_service_interface import IDimensionService
from Platform.dao.impl.dimension_dao_impl import DimensionDaoImpl
from Platform.dao.impl.dimension_cam_dao_impl import DimensionCAMDaoImpl
from Platform.constant.error_messages import ErrorMessages
from Platform.serializers import DimensionCAMModelSerializer
from EmailApp.utils import  validate_chroma_results, update_existing_training_phrase_metadata, \
    remove_intent_and_sub_intents_from_metadata, get_metadata_for_fetching, \
    get_sub_intent_keys_from_metadata, get_metadata_for_creation, get_intent_and_sub_intent, compare_chroma_metadatas, \
    check_intent_present_in_metadata
from EmailApp.constant.constants import ChromadbMetaDataParams, UtterancesGeneratorParams, \
    CategoriesForPersonalization, PaginationParams, ChromaParams, DimensionTypeNames
from AIServices.VectorStore.chromavectorstore import ChromaVectorStore
from Platform.utils import get_current_unix_timestamp, paginate_queryset

logger = logging.getLogger(__name__)

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class DimensionServiceImpl(IDimensionService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DimensionServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside DimensionServiceImpl")
            self.dimension_dao = DimensionDaoImpl()
            self.dimension_cam_dao = DimensionCAMDaoImpl()
            self.chroma_vector_store = ChromaVectorStore()
            self.azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager",AzureBlobConfig(**settings.STORAGE_CONFIG))
            print(f"Inside DimensionServiceImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Adds a new dimension and its associated mapping to the database.
    @transaction.atomic
    def add_dimension_and_mapping(self, customer_uuid, application_uuid, user_uuid, validated_data):
        uuid_data = (customer_uuid, application_uuid, user_uuid)
        # [parent, child, child of child...]
        dimension_names = validated_data.get('dimension_names')
        dimension_type_uuid = validated_data.get('dimension_type_uuid')
        utterances = validated_data.get('utterances')
        dimension_names_len = len(dimension_names)

        # Check for duplicate names
        if len(dimension_names) != len(set(dimension_names)):
            raise CustomException(ErrorMessages.DIMENSION_NAMES_SHOULD_UNIQUE)

        try:
            duplicates = None
            parent_dimension = parent_dimension_mapping = None
            for ind, dimension_name in enumerate(dimension_names):
                logger.info("Starting to add dimension: %s", dimension_name)

                # If multiple dimensions exist, the first (index 0) is the parent.
                if dimension_names_len > 1 and ind == 0:
                    parent_dimension, parent_dimension_mapping = self.__handle_parent_dimension_creation(dimension_name, dimension_type_uuid, uuid_data, validated_data)
                    continue

                # Create or get the main (child or single) dimension
                dimension, _ = self.dimension_dao.get_or_create_dimension(dimension_name, dimension_type_uuid, user_uuid)
                # Create or get the dimension mapping, with parent_dimension (None if not geography case)
                dimension_mapping, mapping_created = self.dimension_cam_dao.get_or_create_dimension_mapping(uuid_data, validated_data, dimension, parent_dimension)

                # Raise error if the dimension mapping already exists
                if not mapping_created and ind == dimension_names_len - 1:
                    logger.error("Dimension mapping already exists for dimension: %s", dimension_name)
                    raise CustomException(ErrorMessages.DIMENSION_EXISTS)

                # If dimension was created and utterances exist, upload them to the chroma DB
                if utterances is not None and len(utterances) > 0:
                    parent_dimension_name = parent_dimension.dimension_name if parent_dimension is not None else None
                    duplicates =self.upload_intent_utterances_to_chroma_server(parent_dimension_mapping=parent_dimension_mapping,application_uuid=application_uuid, customer_uuid=customer_uuid, utterances=utterances,child_dimension_mapping=dimension_mapping,parent_dimension_name = parent_dimension_name,child_dimension_name = dimension_name)

                logger.info("Successfully added dimension: %s", dimension_name)

                # Update parent dimension and its mapping for the next iteration (child of current dimension)
                parent_dimension, parent_dimension_mapping = dimension, dimension_mapping
            return duplicates
        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error("Error adding dimension: %s", str(e))
            raise CustomException(ErrorMessages.DIMENSION_ADD_FAILED)

    def add_training_phrases(self,utterances,parent_dimension_name,dimension_name,customer_uuid,application_uuid):
        logger.info("Inside DimensionServiceImpl :: add_training_phrases")

        try:
            # Fetch parent_dimension if exists or by creating
            parent_dimension_mapping=None
            if parent_dimension_name is not None:
                parent_dimension_mapping = self.dimension_cam_dao.fetch_dimension_mapping_by_parent_child_names(parent_dimension_name=None,child_dimension_name=parent_dimension_name,customer_uuid=customer_uuid,application_uuid=application_uuid)
            # Create or get the dimension mapping, with parent_dimension (None if not geography case)
            child_dimension_mapping = self.dimension_cam_dao.fetch_dimension_mapping_by_parent_child_names(
                parent_dimension_name=parent_dimension_name, child_dimension_name=dimension_name,
                customer_uuid=customer_uuid, application_uuid=application_uuid)

            # If dimension was created and utterances exist, upload them to the chroma DB
            if utterances is not None and len(utterances) > 0:
                return self.upload_intent_utterances_to_chroma_server(
                    parent_dimension_mapping=parent_dimension_mapping, application_uuid=application_uuid,
                    customer_uuid=customer_uuid, utterances=utterances, child_dimension_mapping=child_dimension_mapping,
                    parent_dimension_name=parent_dimension_name, child_dimension_name=dimension_name)

        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error("Error adding dimension: %s", str(e))
            raise CustomException(ErrorMessages.ERROR_WHILE_ADDING_TRAINING_PHRASES)

    # Edits existing dimension and its associated mappings.
    @transaction.atomic
    def edit_dimension(self, customer_uuid, application_uuid, user_uuid, validated_data):
        # Extract uuid_data and necessary fields
        uuid_data = (customer_uuid, application_uuid, user_uuid)
        dimension_name = validated_data.get('dimension_name')
        parent_dimension_name = validated_data.get('parent_dimension_name', None)
        dimension_type_uuid = validated_data.get('dimension_type_uuid')
        mapping_uuid = validated_data.get('mapping_uuid')
        utterances = validated_data.get('utterances')

        try:
            logger.info(f"Starting dimension edit process for mapping_uuid: {mapping_uuid}")

            # Retrieve the current dimension mapping
            curr_dimension_mapping = self.dimension_cam_dao.get_dimension_mapping_by_id(customer_uuid, application_uuid, mapping_uuid, fetch_is_parent=True)
            if curr_dimension_mapping is None:
                raise CustomException(ErrorMessages.DIMENSION_NOT_FOUND)
            curr_dimension = curr_dimension_mapping.dimension_uuid
            existing_dimension_name = curr_dimension.dimension_name



            # # If the dimension is a parent and the name has changed, raise an exception
            # if curr_dimension_mapping.is_parent and (parent_dimension_name if parent_dimension_name else dimension_name) != curr_dimension.dimension_name:
            #     raise CustomException(ErrorMessages.DIMENSION_HAS_DEPENDENTS)

            collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(application_uuid=application_uuid, customer_uuid=customer_uuid)
            logger.info(f"chroma collection name :: {collection_name}")

            # Handle parent dimension creation or fetch
            parent_dimension_mapping=None
            parent_dimension = curr_dimension_mapping.parent_dimension_uuid
            if parent_dimension_name is not None:
                parent_dimension,parent_dimension_mapping = self.__handle_parent_dimension_creation(parent_dimension_name, dimension_type_uuid, uuid_data, validated_data)
                parent_dimension_name = parent_dimension.dimension_name

            dimension,child_dimension_mapping = self.__handle_dimension_update(parent_dimension, curr_dimension, curr_dimension_mapping,
                                                       dimension_name, dimension_type_uuid, validated_data, user_uuid,collection_name,existing_dimension_name,parent_dimension_name,customer_uuid,application_uuid)

            if utterances is not None and len(utterances) > 0:
                updated_dimension = dimension if dimension is not None else curr_dimension
                #self.update_intent_utterances_to_chroma_server(utterances=utterances, intent_name=updated_dimension.dimension_name,collection_name=collection_name)
                duplicates = self.update_intent_utterances_to_chroma_server(
                    parent_dimension_mapping=parent_dimension_mapping, application_uuid=application_uuid,
                    customer_uuid=customer_uuid, utterances=utterances, child_dimension_mapping=child_dimension_mapping,
                    parent_dimension_name=parent_dimension_name, child_dimension_name=updated_dimension.dimension_name)
                return duplicates



        # Handle unique constraint violation
        except IntegrityError as ie:
            if 'unique constraint' in str(ie):
                logger.error(f"Unique constraint error for dimension mapping: {mapping_uuid}")
                raise CustomException(ErrorMessages.DIMENSION_EXISTS)
            logger.error(f"Integrity error: {str(ie)}")
            raise CustomException(ErrorMessages.DIMENSION_UPDATE_FAILED)

        # Handle known custom exceptions
        except CustomException as ce:
            logger.error(f"Custom exception raised: {str(ce)}")
            raise ce

        # Handle any other unexpected exceptions
        except Exception as e:
            logger.error(f"Unexpected error during dimension update: {str(e)}")
            raise CustomException(ErrorMessages.DIMENSION_UPDATE_FAILED)

    # Retrieves dimensions by their type for the given customer and application.
    def get_dimensions_by_dimension_type(self, customer_uuid, application_uuid, dimension_type_uuid,paginated_params):
        logger.info("Fetching dimensions for customer: %s, application: %s, dimension type: %s", customer_uuid, application_uuid, dimension_type_uuid)

        # Query to fetch the dimensions and their mappings in one go
        get_dimension_mappings_st = datetime.now()
        logger.info(f"\nTime profile :: Get Dimension by DimensionTypes :: time before Fetching dimensions by dimension type from Dimension mapping table:: {format_indian_time(get_dimension_mappings_st)}\n")
        #dimension_mappings = self.dimension_cam_dao.get_dimensions_by_dimension_type(customer_uuid, application_uuid, dimension_type_uuid)
        dimension_mappings=self.dimension_dao.fetch_parent_and_child_dimension_details(
            customer_uuid=customer_uuid, application_uuid=application_uuid,
            parent_dimension_type_uuid=dimension_type_uuid)
        get_dimension_mappings_et = datetime.now()
        logger.info(f"\nTime profile :: Get Dimension by DimensionTypes :: time after Fetching dimensions by dimension type from Dimension mapping table :: {format_indian_time(get_dimension_mappings_et)}\n")
        logger.info(f"\nTime profile :: Get Dimension by DimensionTypes :: Total time taken Fetching dimensions by dimension type from Dimension mapping table :: {(get_dimension_mappings_et - get_dimension_mappings_st).total_seconds() * 1000:.4f} ms\n")

        logger.info("Successfully retrieved %d dimensions for customer: %s, application: %s", len(dimension_mappings), customer_uuid, application_uuid)
        paginated_data, paginator = paginate_queryset(dimension_mappings, paginated_params)

        paginated_Response = PaginationResponse(page_num=paginated_data.number, total_entry_per_page=paginated_params[
            PaginationParams.TOTAL_ENTRY_PER_PAGE.value], total_entries=paginator.count,
                                                total_pages=paginated_data.paginator.num_pages,
                                                data=paginated_data.object_list).model_dump()
        return paginated_Response

    # Retrieves the dimension mapping by its ID for the given customer and application.
    def get_dimension_mapping_by_id(self, customer_uuid, application_uuid, mapping_uuid):
        logger.info(f"Fetching dimension mapping for customer: {customer_uuid}, application: {application_uuid}, mapping ID: {mapping_uuid}")

        # Get the dimension mapping by ID
        dimension_mapping = self.dimension_cam_dao.get_dimension_mapping_by_id(customer_uuid, application_uuid,
                                                                               mapping_uuid)

        # Serialize the result
        serializer = DimensionCAMModelSerializer(dimension_mapping, context={'include_dimension_type_name': True})

        logger.info( f"Successfully retrieved dimension mapping for customer: {customer_uuid}, application: {application_uuid}, mapping ID: {mapping_uuid}")

        return serializer.data if dimension_mapping else None

    # Retrieves geography dimensions(countries / states with app name) for the given customer and application.
    def get_geography_dimensions(self, customer_uuid, application_uuid, parent_dimension_uuid):
        logger.info(f"Fetching geography dimensions for customer: {customer_uuid}, application: {application_uuid}, parent dimension ID: {parent_dimension_uuid}")

        # Get the geography dimensions
        get_geography_dimensions_st = datetime.now()
        logger.info(f"\nTime profile :: Get Geography Dimensions :: time before Fetching geography dimensions from Dimension mapping table:: {format_indian_time(get_geography_dimensions_st)}\n")
        geography_dimensions = self.dimension_cam_dao.get_geography_dimensions(customer_uuid, application_uuid, parent_dimension_uuid)
        get_geography_dimensions_et = datetime.now()
        logger.info(f"\nTime profile :: Get Geography Dimensions :: time after Fetching geography dimensions from Dimension mapping table :: {format_indian_time(get_geography_dimensions_et)}\n")
        logger.info(f"\nTime profile :: Get Geography Dimensions :: Total time taken Fetching geography dimensions from Dimension mapping table :: {(get_geography_dimensions_et - get_geography_dimensions_st).total_seconds() * 1000:.4f} ms\n")

        return geography_dimensions

    # Retrieves list of countries or states based on the provided parent dimension UUID.
    def get_countries_or_states(self, country_name=None):
        logger.info(f"Retrieving countries or states for parent dimension: {country_name}")

        # Fetch countries or states using the DAO
        get_country_or_state_st = datetime.now()
        logger.info(f"\nTime profile :: Get Country State DropDown :: time before Fetching countries or states from Countries or States table :: {format_indian_time(get_country_or_state_st)}\n")
        countries_or_states = self.dimension_dao.get_countries_or_states(country_name)
        get_country_or_state_et = datetime.now()
        logger.info(f"\nTime profile :: Get Country State DropDown :: time after Fetching countries or states from Countries or States table :: {format_indian_time(get_country_or_state_et)}\n")
        logger.info(f"\nTime profile :: Get Country State DropDown :: Total time taken Fetching countries or states from Countries or States table :: {(get_country_or_state_et - get_country_or_state_st).total_seconds() * 1000:.4f} ms\n")

        logger.info(f"Successfully retrieved countries or states for {country_name}. Number of records: {len(countries_or_states)}")

        return countries_or_states

    # Deletes a dimension type mapping based on the provided customer, application, and mapping UUID.
    @transaction.atomic
    def delete_dimension_mapping(self, customer_uuid, application_uuid, user_uuid, mapping_uuid):
        logger.info(f"Attempting to delete dimension mapping: {mapping_uuid} for customer: {customer_uuid}, application: {application_uuid}")

        # Retrieve the mapping and check if it's a parent in a single query
        try:
            dimension_mapping = self.dimension_cam_dao.get_dimension_mapping_by_id(customer_uuid, application_uuid, mapping_uuid, fetch_is_parent=True)
            # If mapping does not exist
            if dimension_mapping is None:
                logger.error(f"Dimension mapping not found: {mapping_uuid} for customer: {customer_uuid}, application: {application_uuid}")
                raise CustomException(ErrorMessages.DIMENSION_NOT_FOUND)
            parent_dimension = dimension_mapping.parent_dimension_uuid
            child_dimension = dimension_mapping.dimension_uuid

            # Check if this dimension is a parent for any other dimensions
            # if dimension_mapping.is_parent:
            #     logger.error(f"Attempt to delete a parent dimension mapping: {mapping_uuid} for customer: {customer_uuid}, application: {application_uuid}")
            #     raise CustomException(ErrorMessages.DIMENSION_HAS_DEPENDENTS)

            # Delete the mapping
            self.dimension_cam_dao.delete_dimension_mapping(dimension_mapping)
            dimension_type_name = child_dimension.dimension_type_uuid.dimension_type_name
            if parent_dimension is None:
                self.dimension_cam_dao.delete_dimension_mappings(parent_dimension_uuid=child_dimension.dimension_uuid,customer_uuid=customer_uuid,application_uuid=application_uuid)
            else:
                self.dimension_cam_dao.delete_parent_dimension_mappings(
                    parent_dimension_uuid=parent_dimension,
                    dimension_type_name=dimension_type_name,
                    customer_uuid=customer_uuid, application_uuid=application_uuid)

            # update the scope for roles in this application
            self.dimension_cam_dao.delete_dimension_from_user_scope(mapping_uuid, application_uuid, customer_uuid)

            if dimension_type_name not in ["INTENT", "SUB_INTENT"]:
                return

            parent_dimension_name=parent_dimension.dimension_name if parent_dimension else None
            child_dimension_name = child_dimension.dimension_name
            collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(application_uuid=application_uuid, customer_uuid=customer_uuid)
            existing_metadata = get_metadata_for_fetching(parent_dimension_name=parent_dimension_name,child_dimension_names=[child_dimension_name])
            existing_records=self.chroma_vector_store.get_records_by_metadata_include_embeddings(existing_metadata, collection_name)
            document_ids = existing_records.get("ids")
            current_metadatas = existing_records.get("metadatas")
            embeddings = existing_records.get("embeddings")
            documents = existing_records.get("documents")
            new_metadatas=[]
            new_documents=[]
            new_embeddings=[]
            new_ids = []
            deleted_ids=[]
            for id,metadata,embedding,document in zip(document_ids,current_metadatas,embeddings,documents):
                intent,sub_intent=get_intent_and_sub_intent(parent_dimension_name,child_dimension_name)
                metadata = remove_intent_and_sub_intents_from_metadata(metadata,intent,sub_intent,remove_intent=parent_dimension_name is None)
                are_there_other_intents,metadata=update_existing_training_phrase_metadata(metadata)
                if not are_there_other_intents:
                    deleted_ids.append(id)
                else:
                    new_ids.append(id)
                    new_documents.append(document)
                    new_embeddings.append(embedding)
                    new_metadatas.append(metadata)

            #update dimension name and uuid for the training phrases
            if new_ids:
                self.chroma_vector_store.update_training_phrases(metadatas=new_metadatas,embeddings=new_embeddings,ids=new_ids,documents=new_documents,collection_name=collection_name)
            if deleted_ids:
                self.chroma_vector_store.delete_record_by_ids(deleted_ids,collection_name=collection_name)

            logger.info(f"Successfully deleted utterances for mapping: {mapping_uuid}")
        except CustomException as ce:
            logger.error(f"Collection does not exist. Error: {str(ce)}")
            if ErrorMessages.COLLECTION_NOT_EXIST in str(ce):
                return
            raise ce
        except Exception as e:
            logger.error(f"Failed to delete utterances for mapping: {mapping_uuid}. Error: {str(e)}")
            raise CustomException(ErrorMessages.UTTERANCES_DELETION_FAILED)

        logger.info(f"Successfully deleted dimension mapping: {mapping_uuid} for customer: {customer_uuid}, application: {application_uuid}")

    # Uploads the given utterances to the Chroma server for the specified intent, associated with the given customer, application.
    def upload_intent_utterances_to_chroma_server(self, parent_dimension_mapping,application_uuid, customer_uuid, utterances,child_dimension_mapping,child_dimension_name,parent_dimension_name=None):
        logger.info("In DimensionServiceImpl :: upload_intent_utterances_to_chroma_server")
        metadata=None
        try:
            # Generate the collection name based on application and customer UUIDs
            collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(application_uuid=application_uuid, customer_uuid=customer_uuid)
            logger.info(f"collection_name :: {collection_name}")
            # Prepare metadata for the utterances
            metadata=get_metadata_for_creation(parent_dimension_name=parent_dimension_name,child_dimension_names=[child_dimension_name])

            logger.info(f"Uploading intent utterances for metadata :: {metadata}")


            # Iterate through the provided utterances and upload each one
            child_dimension_mapping.dimension_details_json=child_dimension_mapping.dimension_details_json or {}

            child_training_phrases_count = child_dimension_mapping.dimension_details_json.get('training_phrases_count', 0)
            parent_training_phrases_count=0
            if parent_dimension_name:
                parent_dimension_mapping.dimension_details_json = parent_dimension_mapping.dimension_details_json or {}
                parent_training_phrases_count = parent_dimension_mapping.dimension_details_json.get('training_phrases_count', 0)
            utterances=set(utterances)
            #for email in utterances:
            intent_count,sub_intent_count,duplicates=self.add_training_phrase_to_chroma(metadata=metadata,collection_name=collection_name,utterances=utterances,intent_identified=parent_dimension_name)
            # if example_status is None:
            #     duplicates.append(email)
            if intent_count>0 and parent_dimension_name:
                parent_training_phrases_count+=intent_count
                parent_dimension_mapping.dimension_details_json['training_phrases_count'] = parent_training_phrases_count
                self.dimension_cam_dao.save_dimension_mapping(parent_dimension_mapping)
            if sub_intent_count>0:
                child_training_phrases_count+=sub_intent_count
                child_dimension_mapping.dimension_details_json['training_phrases_count']=child_training_phrases_count
                self.dimension_cam_dao.save_dimension_mapping(child_dimension_mapping)

            #self.dimension_cam_dao.update_dimension_details_json_in_dimension_mapping(mapping_uuid,dimensions_details_json)

            logger.info(f"Successfully uploaded {len(utterances)} utterances for metadata: {metadata}")

            return duplicates

        except Exception as error:
            logger.error(f"Error uploading utterances for metadata: {metadata}. Error: {str(error)}")
            raise CustomException(ErrorMessages.ADD_UTTERANCE_FAILED)

    def edit_training_phrase(self,utterance,parent_dimension_name,child_dimensions,customer_uuid,application_uuid):
        logger.info("Inside DimensionServiceImpl :: edit_training_phrase")
        logger.info(f"Updating utterance for intent: {child_dimensions}, parent_intent: {parent_dimension_name}")

        try:
            # Generate the collection name based on application and customer UUIDs
            collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(
                application_uuid=application_uuid, customer_uuid=customer_uuid)
            metadata=get_metadata_for_creation(parent_dimension_name=parent_dimension_name,child_dimension_names=child_dimensions)
            metadata[ChromadbMetaDataParams.CREATED_TIMESTAMP.value]=metadata[ChromadbMetaDataParams.UPDATED_TIME_STAMP.value]=get_current_unix_timestamp()
            # # Prepare metadata for the utterances
            # metadata combination to get utterances from chroma db
            logger.info(f"Metadata Key :: {metadata}")
            if not utterance.get(UtterancesGeneratorParams.ID.value):
                raise InvalidValueProvidedException("Utterance ID not provided")
            chroma_example = self.chroma_vector_store.get_record_by_id(
                id=utterance.get(UtterancesGeneratorParams.ID.value), collection_name=collection_name)
            document, existing_metadata, embedding = validate_chroma_results(chroma_example)
            intents,sub_intents = get_intent_and_sub_intent(parent_dimension_name,child_dimensions)
            if isinstance(intents,list) and len(intents)>0:
                intents=intents[0]
            sub_intents=get_sub_intent_keys_from_metadata(existing_metadata,intents)
            existing_metadata=remove_intent_and_sub_intents_from_metadata(existing_metadata,intents,sub_intents,remove_intent=True)
            are_there_other_intents,existing_metadata=update_existing_training_phrase_metadata(existing_metadata)
            #get vector embeddings of updated training phrase
            vector_embeddings = self.chroma_vector_store.embed_query_list([utterance.get(UtterancesGeneratorParams.UTTERANCE.value)])

            similar_training_phrases = self.chroma_vector_store.find_similar_records(
                collection_name=collection_name,
                query_embeddings=vector_embeddings)
            is_duplicate, is_updated,_ = self.check_duplicate_and_insert_training_phrase(metadata=metadata, chroma_record=similar_training_phrases[0], collection_name=collection_name)
            if is_duplicate:
                return utterance.get(UtterancesGeneratorParams.UTTERANCE.value)

            if  not are_there_other_intents:

                if not is_updated:
                    self.chroma_vector_store.update_email_document_embedding(
                        email=utterance.get(UtterancesGeneratorParams.UTTERANCE.value),
                        id_=utterance.get(UtterancesGeneratorParams.ID.value),
                        collection_name=collection_name,
                        metadata={ChromadbMetaDataParams.UPDATED_TIME_STAMP.value: get_current_unix_timestamp()})
                    return
                self.chroma_vector_store.delete_record_by_id(utterance.get(UtterancesGeneratorParams.ID.value),collection_name)
                return
            self.chroma_vector_store.update_metadata_by_id(
                utterance.get(UtterancesGeneratorParams.ID.value), existing_metadata, document, embedding,
                collection_name)
            if is_updated:
                return
            self.chroma_vector_store.upload_utterances_at_once(ids_list=[str(uuid4())],
                                                               vector_embeddings_list=vector_embeddings,
                                                               metadata_list=[metadata],
                                                               training_phrases_list=[utterance.get(UtterancesGeneratorParams.UTTERANCE.value)],
                                                               collection_name=collection_name)

            #_,_,duplicates = self.add_training_phrase_to_chroma(metadata=metadata,utterances=[utterance.get(UtterancesGeneratorParams.UTTERANCE.value)],collection_name=collection_name)

        except Exception as e:
            logger.error(
                f"Error occurred while updating utterances for intent: {child_dimensions}, parent_intent: {parent_dimension_name}. Error: {str(e)}")
            raise CustomException(ErrorMessages.UPDATE_UTTERANCE_FAILED)

    def add_training_phrase_to_chroma(self,metadata,utterances,collection_name,intent_identified=None):
        logger.info("In DimensionServiceImpl :: add_training_phrase_to_chroma")
        metadata[ChromadbMetaDataParams.CREATED_TIMESTAMP.value] = metadata[
            ChromadbMetaDataParams.UPDATED_TIME_STAMP.value] = get_current_unix_timestamp()
        vector_embeddings = self.chroma_vector_store.embed_query_list(utterances)

        similar_training_phrases = self.chroma_vector_store.find_similar_records(collection_name=collection_name,
                                                                                 query_embeddings=vector_embeddings)
        filtered_embeddings = []
        filtered_queries = []
        doc_ids_list = []
        metadata_list = []
        duplicates = []
        intent_count=0
        sub_intent_count=0
        for idx, training_phrase in enumerate(utterances):
            is_duplicate,is_updated,intent_key_identified = self.check_duplicate_and_insert_training_phrase(metadata=metadata,chroma_record=similar_training_phrases[idx],collection_name=collection_name,intent_identified=intent_identified)
            if is_duplicate:
                logger.warning("Duplicate training phrase detected: '%s'. Skipping update.", training_phrase)
                duplicates.append(training_phrase)
                continue
            sub_intent_count+=1
            if intent_identified and not intent_key_identified:
                intent_count+=1
            if not is_updated:
                filtered_queries.append(training_phrase)
                filtered_embeddings.append(vector_embeddings[idx])
                doc_ids_list.append(str(uuid4()))
                metadata_list.append(metadata)


        if doc_ids_list:
            self.chroma_vector_store.upload_utterances_at_once(ids_list=doc_ids_list,
                                                                           vector_embeddings_list=filtered_embeddings,
                                                                           metadata_list=metadata_list,
                                                                           training_phrases_list=filtered_queries,
                                                                           collection_name=collection_name)
            # sub_intent_count+=count
            # intent_count+=count
        return intent_count,sub_intent_count,duplicates

        #     example_status = self.chroma_vector_store.add_emails_and_metadata(metadata=metadata, emails=record,
        #                                                            collection_name=collection_name)
        # if not example_status:
        #     return None
        # return example_status
    def check_duplicate_and_insert_training_phrase(self,metadata,chroma_record,collection_name,intent_identified=None):
        logger.info("In DimensionServiceImpl :: check_duplicate_and_insert_training_phrase")
        is_updated=False
        intent_key_identified=False
        for nearest_document in chroma_record:
            doc_metadata = nearest_document.get('metadata')

            if compare_chroma_metadatas(current_metadata=metadata, existing_metadata=doc_metadata):
                return True,is_updated,True

            if intent_identified and check_intent_present_in_metadata(intent_identified, doc_metadata):
                intent_key_identified=True
            # Update the record
            doc_id = nearest_document.get('document_id')
            doc_metadata.update(metadata)
            doc_metadata.update({
                ChromadbMetaDataParams.UPDATED_TIME_STAMP.value: get_current_unix_timestamp()
            })
            is_updated = True
            self.chroma_vector_store.update_the_metadata_with_document_id(doc_metadata, doc_id, collection_name)
            logger.info("Updated metadata for document ID '%s' in collection '%s'.", doc_id, collection_name)
        return False,is_updated,intent_key_identified




    # Updates the given utterances to the Chroma server for the specified intent, associated with the given customer, application.
    def update_intent_utterances_to_chroma_server(self, parent_dimension_mapping,application_uuid, customer_uuid, utterances,child_dimension_mapping,child_dimension_name,parent_dimension_name=None):
        logger.info(f"Updating intent utterances for intent: {child_dimension_name}, parent_intent: {parent_dimension_name}")

        try:
            # Generate the collection name based on application and customer UUIDs
            collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(
                application_uuid=application_uuid, customer_uuid=customer_uuid)

            new_utterances=[]
            child_dimension_mapping.dimension_details_json = child_dimension_mapping.dimension_details_json or {}
            child_training_phrases_count = child_dimension_mapping.dimension_details_json.get('training_phrases_count',0)
            # parent_training_phrases_count=0
            # if parent_dimension_name:
            #     parent_dimension_mapping.dimension_details_json = parent_dimension_mapping.dimension_details_json or {}
            #     parent_training_phrases_count = parent_dimension_mapping.dimension_details_json.get('training_phrases_count', 0)
            for utterance in utterances:
                if not utterance.get(UtterancesGeneratorParams.ID.value):
                    # need to addd new record
                    new_utterances.append(utterance.get(UtterancesGeneratorParams.UTTERANCE.value))
                    continue
                chroma_example = self.chroma_vector_store.get_record_by_id(id=utterance.get(UtterancesGeneratorParams.ID.value),collection_name=collection_name)
                document, existing_metadata, embedding = validate_chroma_results(chroma_example)

                intent,sub_intents=get_intent_and_sub_intent(parent_dimension_name,child_dimension_name)
                existing_metadata=remove_intent_and_sub_intents_from_metadata(existing_metadata, intent,sub_intents,remove_intent=parent_dimension_name is None)

                metadata_has_other_intents, modified_metadata = update_existing_training_phrase_metadata(metadata=existing_metadata)

                if metadata_has_other_intents:
                    # modified_metadata[ChromadbMetaDataParams.CREATED_TIMESTAMP.value]=existing_metadata.get(ChromadbMetaDataParams.CREATED_TIMESTAMP.value,str(get_current_unix_timestamp()))
                    # modified_metadata[ChromadbMetaDataParams.UPDATED_TIME_STAMP.value]=str(get_current_unix_timestamp())
                    self.chroma_vector_store.update_metadata_by_id(utterance.get(UtterancesGeneratorParams.ID.value), modified_metadata, document, embedding,
                                                                   collection_name)
                    #need to add new record
                    new_utterances.append(utterance.get(UtterancesGeneratorParams.UTTERANCE.value))
                    # if parent_dimension_name:
                    #     parent_training_phrases_count -= 1
                    child_training_phrases_count -= 1
                else:
                    self.chroma_vector_store.update_email_document_embedding(
                        email=utterance.get(UtterancesGeneratorParams.UTTERANCE.value),
                        id_=utterance.get(UtterancesGeneratorParams.ID.value),
                        collection_name=collection_name,metadata={ChromadbMetaDataParams.UPDATED_TIME_STAMP.value:get_current_unix_timestamp()})

            child_dimension_mapping.dimension_details_json['training_phrases_count'] = child_training_phrases_count
            # if parent_dimension_name:
            #     parent_dimension_mapping.dimension_details_json[
            #         'training_phrases_count'] = parent_training_phrases_count
            if not new_utterances and child_training_phrases_count>0:
                self.dimension_cam_dao.save_dimension_mapping(child_dimension_mapping)
                # if parent_dimension_name:
                #     self.dimension_cam_dao.save_dimension_mapping(parent_dimension_mapping)
                return
            return self.upload_intent_utterances_to_chroma_server(
                parent_dimension_mapping=parent_dimension_mapping, application_uuid=application_uuid,
                customer_uuid=customer_uuid, utterances=new_utterances, child_dimension_mapping=child_dimension_mapping,
                parent_dimension_name=parent_dimension_name, child_dimension_name=child_dimension_name)

        except Exception as e:
            logger.error(f"Error occurred while updating utterances for intent: {child_dimension_name}, parent_intent: {parent_dimension_name}. Error: {str(e)}")
            raise CustomException(ErrorMessages.UPDATE_UTTERANCE_FAILED)

    def __handle_parent_dimension_creation(self, parent_dimension_name, dimension_type_uuid, uuid_data, validated_data):
        """
        Handles the creation or retrieval of a parent dimension and its associated mapping.
        :param parent_dimension_name: The name of the parent dimension to be created or retrieved.
        :param dimension_type_uuid: The UUID of the dimension type associated with the parent dimension.
        :param uuid_data: A tuple containing customer_uuid, application_uuid, and user_uuid.
        :param validated_data: The validated data containing information required for the dimension mapping.
        :return: Dimension: The parent dimension that was created or retrieved.
        """

        # Create or get the parent dimension
        parent_dimension,_ = self.dimension_dao.get_or_create_dimension(parent_dimension_name, dimension_type_uuid, uuid_data[2])

        # Create or get the parent dimension mapping
        parent_dimension_mapping,_=self.dimension_cam_dao.get_or_create_dimension_mapping(uuid_data, validated_data, parent_dimension)

        return parent_dimension,parent_dimension_mapping

    def __handle_dimension_update(self, parent_dimension, curr_dimension, curr_dimension_mapping, dimension_name, dimension_type_uuid, validated_data, user_uuid,collection_name,existing_dimension_name,parent_dimension_name,customer_uuid,application_uuid):
        """
        Handles updating a dimension and its associated mapping.

        :param parent_dimension: The parent dimension of the dimension being updated (can be None).
        :param curr_dimension: The current Dimension instance representing the dimension to update.
        :param curr_dimension_mapping: The current DimensionCustomerApplicationMapping instance for the dimension.
        :param dimension_name: The new name for the dimension (if updated).
        :param dimension_type_uuid: The UUID of the dimension type.
        :param validated_data: A dictionary containing validated data for the dimension update.
        :param user_uuid: The UUID of the user performing the update.

        :return: The updated Dimension instance if the dimension name was changed, or None otherwise.
        """
        # Update dimension if the name has changed
        dimension = None
        if curr_dimension.dimension_name != dimension_name:
            dimension, _ = self.dimension_dao.get_or_create_dimension(dimension_name, dimension_type_uuid, user_uuid)
            if not parent_dimension_name:
                self.dimension_cam_dao.update_parent_dimension_in_dimension_mapping(customer_uuid=customer_uuid,application_uuid=application_uuid,parent_dimension_uuid=curr_dimension.dimension_uuid,updated_parent_dimension_uuid=dimension.dimension_uuid)
            curr_dimension_mapping.dimension_uuid = dimension
            curr_dimension_mapping.parent_dimension_uuid = parent_dimension
            #fetch existing metadata for training phrases
            existing_metadata = get_metadata_for_fetching(parent_dimension_name=parent_dimension_name,child_dimension_names=[existing_dimension_name])
            existing_records=self.chroma_vector_store.get_records_by_metadata_include_embeddings(existing_metadata, collection_name)
            document_ids = existing_records.get("ids")
            current_metadatas = existing_records.get("metadatas")
            embeddings = existing_records.get("embeddings")
            documents = existing_records.get("documents")
            new_metadatas=[]
            for metadata in current_metadatas:
                if not parent_dimension_name:
                    child_dimension_names = get_sub_intent_keys_from_metadata(intent_identified=curr_dimension.dimension_name,sub_intent_metadata=metadata)
                    modified_metadata = get_metadata_for_creation(parent_dimension_name=dimension_name,child_dimension_names=child_dimension_names)
                    required_other_metadata = remove_intent_and_sub_intents_from_metadata(metadata,curr_dimension.dimension_name,None,remove_intent=True)
                    modified_metadata.update(required_other_metadata)
                else:
                    modified_metadata = get_metadata_for_creation(parent_dimension_name=parent_dimension_name,
                                                                   child_dimension_names=[dimension_name])
                    required_other_metadata = remove_intent_and_sub_intents_from_metadata(metadata, parent_dimension_name,curr_dimension.dimension_name,remove_intent=False)
                    modified_metadata.update(required_other_metadata)
                _,modified_metadata=update_existing_training_phrase_metadata(modified_metadata)
                new_metadatas.append(modified_metadata)


            #update dimension name and uuid for the training phrases
            if document_ids:
                self.chroma_vector_store.update_training_phrases(metadatas=new_metadatas,embeddings=embeddings,ids=document_ids,documents=documents,collection_name=collection_name)

        # Update mapping details
        dimension_details = validated_data.get('dimension_details_json')
        dimension_details_json = asdict(dimension_details) if dimension_details is not None else curr_dimension_mapping.dimension_details_json
        curr_dimension_mapping.dimension_details_json = dimension_details_json

        curr_dimension_mapping.description = validated_data.get('description')
        curr_dimension_mapping.updated_by = user_uuid

        # Save updated dimension mapping
        self.dimension_cam_dao.save_dimension_mapping(curr_dimension_mapping)

        logger.info(f"Successfully updated dimension mapping for mapping_uuid: {curr_dimension_mapping.mapping_uuid}")

        return dimension,curr_dimension_mapping

    def __validate_training_phrases_sheet_headers(self, sheet_headers : list, expected_headers : list):
        """
           Validates that the Excel sheet contains the expected headers.

           Args:
               - sheet_headers (List[str]): Headers of Excel sheet (First row of Excel).
               - Expected Headers (List[str]): Headers you would like to compare

           Raises Exception if there is a mismatch between Expected and sheet headers.

        """

        logger.info(f"In  __validate_excel_sheet_headers :: Sheet Headers: {sheet_headers}")
        for column, expected_column in zip(sheet_headers, expected_headers):
            if column.strip() != expected_column.strip():
                raise InvalidValueProvidedException(detail= f"Invalid Sheet Headers : {sheet_headers}. Expected Headers : {expected_headers}")

    def __preprocess_dataframe(self, dataframe : pd.DataFrame):

        """
        Preprocesses the input DataFrame by replacing empty cells and normalizing newline characters.

        Parameters:
            dataframe (pd.DataFrame): The DataFrame to preprocess.

        Modifies:
            dataframe (pd.DataFrame):
                - Replaces empty cells with empty strings.
                - Converts escaped newline characters ('\\n') to actual newlines ('\n').
        """

        # Replace Empty cells in Excel with Empty string
        dataframe.fillna("", inplace=True)
        # pandas reads '\n' as '\\n', so replace '\\n' with '\n'
        dataframe.replace(r'\\n', '\n', regex=True, inplace=True)

    def __find_all_duplicate_rows(self, df : pd.DataFrame) -> pd.DataFrame:
        """
        Finds all duplicate rows in the given DataFrame.

        Parameters:
            df (pd.DataFrame): The DataFrame to search for duplicate rows.

        Returns:
            pd.DataFrame: A DataFrame containing all rows that are duplicates (including their first occurrence),
                          based on the columns in EXPECTED_COLUMNS[1:], after stripping and converting strings to lowercase.
        """

        df_lower = df[EXPECTED_COLUMNS[1:]].map(lambda x: x.strip().lower() if isinstance(x, str) else x)
        # Find duplicates based on the converted DataFrame
        duplicates = df[df_lower.duplicated(keep=False)]

        return duplicates

    def __read_excel(self, excel_file_obj, sheet_name = None, header = None):
        """
        Tries to read the excel, if any error occured raises exception
        """
        logger.info("In DimensionServiceImpl :: __read_excel")
        try:
            # Load Excel sheet using Pandas for efficient processing
            excel_data = pd.read_excel(excel_file_obj, sheet_name= sheet_name, header= header)  # Load all sheets into a dictionary without any headers
            return excel_data
        except Exception as e:
            logger.error(f"Error while processing Excel file: {str(e)}")
            return CustomResponse(f"Error while processing Excel file: {str(e)}", code=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def __delete_rows_by_row_numbers(self, dataframe, row_numbers):
        """
        Deletes rows from the DataFrame based on the provided row numbers.

        Args:
            dataframe (pd.DataFrame): The input DataFrame.
            row_numbers (list): A list of row indices to be removed.

        Performs inplace operations
        """
        # Drop rows by index, ignore errors for non-existent indices
        dataframe.drop(index=row_numbers, inplace= True, errors= "ignore")
        dataframe.reset_index(drop=True, inplace= True)


    def __handle_duplicates(self, dataframe, error_rows):
        """
        Handle duplicate rows by identifying them and removing them from the dataframe.

        Args:
            dataframe (pd.DataFrame): The input dataframe.
            error_rows (list): The list to store errors for duplicate rows.

        Returns:
            list: The indices of the duplicate rows.
        """
        duplicates_df = self.__find_all_duplicate_rows(dataframe)
        duplicate_row_indices = get_duplicate_rows(duplicates_df, error_rows)

        if duplicate_row_indices:
            self.__delete_rows_by_row_numbers(dataframe, duplicate_row_indices)

    def __get_the_dimension_updates(self,dimension_mappings,dimension_wise_count ):
        """
            Generates a list of DimensionCustomerApplicationMapping objects with updated training phrase counts.

            Args:
                dimension_mappings (dict):
                    Maps (dimension_uuid, parent_dimension_uuid) to DimensionCustomerApplicationMapping objects.
                dimension_wise_count (dict):
                    Maps intents to dimension names and their counts.

            Returns:
                list: Updated DimensionCustomerApplicationMapping objects.
            """
        dimension_updates = []
        for intent, count_dict in dimension_wise_count.items():

            parent_dimension_name = intent.upper()

            for dimension_name, count in count_dict.items():

                if dimension_name == intent:
                    # build key -> "parent_dimension_name,child_dimension_name"
                    key = (None, parent_dimension_name)
                    dimension_mapping = dimension_mappings.get(key)
                else:
                    key = (parent_dimension_name, dimension_name.upper())
                    dimension_mapping = dimension_mappings.get(key)

                if dimension_mapping:
                    details_json = dimension_mapping.dimension_details_json or {}
                    details_json['training_phrases_count'] = details_json.get('training_phrases_count', 0) + count
                    dimension_mapping.dimension_details_json = details_json
                    dimension_mapping.updated_ts = timezone.now()
                    dimension_updates.append(dimension_mapping)

        return dimension_updates

    @transaction.atomic
    def __update_dimension_counts(self, dimension_wise_count, customer_uuid, application_uuid):
        """
        Update the count for each dimension in the database.

        Args:
            dimension_wise_count (dict): A dictionary with dimension counts.
            customer_uuid (str): The customer UUID.
            application_uuid (str): The application UUID.
        """
        logger.info("In update_dimension_counts")
        all_dimensions = set()
        for _, count_dict in dimension_wise_count.items():
            all_dimensions.update(set(count_dict.keys()))

        # all_dimensions = {dimension.upper() for dimension in all_dimensions}

        dimension_mappings = self.dimension_cam_dao.fetch_dimension_mappings_with_dimension_names(application_uuid=application_uuid, customer_uuid=customer_uuid, dimension_names=all_dimensions)

        dimension_updates = self.__get_the_dimension_updates(dimension_mappings, dimension_wise_count)

        #Bulk upload
        self.dimension_cam_dao.perform_bulk_update(dimension_updates)


    def __group_error_rows(self, error_rows : list):

        temp = dict()
        for each_row in error_rows:
            training_phrase  = each_row.get(ChromaExcelSheet.TRAINING_PHRASE.value)
            temp.setdefault(training_phrase, []).append(each_row)

        groups = []

        for _, similar_group in temp.items():
            groups.append(similar_group)

        return groups
    def __build_customer_intent_sub_intent_map(self,customer_uuid, application_uuid) -> dict:

        """
            Builds a mapping of customer-specific intents to their sub-intents.

            Args:
                customer_uuid (str): The unique identifier for the customer.
                application_uuid (str): The unique identifier for the application.

            Returns:
                dict: A dictionary mapping intents to their respective sub-intents, where:
                      - Keys are parent intents (str).
                      - Values are lists of sub-intents (list of str).
        """

        base_intent_sub_intent_map = self.dimension_cam_dao.fetch_intent_with_sub_intents(customer_uuid, application_uuid)

        #sample output = {'ORDER_STATUS': ['SHIPPING_UPDATES'], 'PURCHASE_ORDER': ['CHECK_PO_STATUS', 'NEW_PO']}
        logger.info(f"base_intent_sub_intent_map:\n {base_intent_sub_intent_map}")
        if not base_intent_sub_intent_map:
            raise InvalidValueProvidedException('Intents not found in DB.')

        return base_intent_sub_intent_map

    def __check_missing_intent_sub_intents(self,base_intent_sub_intent_map,intent_to_subintents_map_excel):
        """
            Identifies missing intents and sub-intents by comparing the base intent-to-sub-intent map
            with the provided intent-to-sub-intents from Excel.

            Args:
                base_intent_sub_intent_map (dict): A dictionary mapping intents to their sub-intents.
                intent_to_subintents_map_excel (dict): A dictionary mapping intents to sub-intents from the Excel file.

            Returns:
                tuple: A tuple containing two lists:
                    - missing_intents (list): Intents in Excel not present in the base map.
                    - missing_sub_intents (list): Sub-intents in Excel not found in the base map for corresponding intents.
        """

        missing_intents, missing_sub_intents = [], []
        for intent, sub_intents in intent_to_subintents_map_excel.items():

            sub_intents_list = base_intent_sub_intent_map.get(intent)
            if sub_intents_list is None:
                missing_intents.append(intent)
            else:
                for sub_intent in sub_intents:
                    if sub_intent not in sub_intents_list:
                        missing_sub_intents.append(sub_intent)

        return missing_intents, missing_sub_intents

    def __validate_intents_subintents(self, base_intent_sub_intent_map: dict, drop_down_sheet_df : pd.DataFrame, excel_intents_column, headers):
        """
        Checks if intents and sub-intents from the Excel sheet match the provided mapping.
        Identifies and raises errors for missing intents or sub-intents.

       Args:
           base_intent_sub_intent_map (dict): Mapping of intents to their respective sub-intents.
           drop_down_sheet_df (pd.DataFrame): DataFrame containing dropdown table data.
           excel_intents_column (list): List of intents extracted from the Excel sheet.
           headers (list) : List of headers from DropDownSheet

       Raises:
           CustomException: If invalid intents or sub-intents are found.
        """
        # Prepare the dictionary to hold intents and their corresponding sub-intents
        intent_to_subintents_map_excel = {}
        for intent in excel_intents_column:
            if intent not in headers:
                intent_to_subintents_map_excel[intent.upper()] = []
                continue
            sub_intents = drop_down_sheet_df[intent].dropna().tolist()
            sub_intents = [sub_intent.strip().upper() for sub_intent in sub_intents]
            intent_to_subintents_map_excel[intent.upper()] = sub_intents


        missing_intents,missing_sub_intents =  self.__check_missing_intent_sub_intents(base_intent_sub_intent_map,intent_to_subintents_map_excel)


        if missing_intents or missing_sub_intents:
            invalid_intent_sub_intents = dict()
            invalid_intent_sub_intents['missing_intents'] = missing_intents
            invalid_intent_sub_intents['missing_sub_intents'] = missing_sub_intents
            raise CustomException(detail= invalid_intent_sub_intents, status_code= status.HTTP_400_BAD_REQUEST)

    def __validate_dropdowntable_sheet(self, drop_down_sheet_df : pd.DataFrame, base_intent_sub_intent_map : dict):
        """
        Ensures all intents in the specified column of the DataFrame exist as headers and delegates intent-sub-intent validation.

       Args:
           drop_down_sheet_df (pd.DataFrame): DataFrame representing the dropdown table sheet.
           base_intent_sub_intent_map (dict): Mapping of intents to their respective sub-intents.

       Raises:
           CustomException: If any intent in the Excel sheet is not present in the headers.
       """
        headers = drop_down_sheet_df.columns.dropna().tolist()
        excel_intents_column = drop_down_sheet_df[ChromaExcelSheet.INTENT_COLUMN.value].dropna().tolist()

        if not excel_intents_column:
            logger.error(ErrorMessages.NO_INTENTS_FOUND)
            raise CustomException(ErrorMessages.NO_INTENTS_FOUND, status_code= status.HTTP_400_BAD_REQUEST)

        headers = [value.strip() for value in headers]
        excel_intents_column = [value.strip() for value in excel_intents_column]

        #no need as of now, macro will handle it
        # for intent in excel_intents_column:
        #     if intent not in headers:
        #         raise InvalidValueProvidedException("Invalid Intents in Excel Sheet")

        # validate intent, sub intents w.r.t db
        self.__validate_intents_subintents(base_intent_sub_intent_map, drop_down_sheet_df, excel_intents_column, headers[1:])




    def upload_examples_to_chromadb(self, excel_file_obj, customer_uuid, application_uuid):

        """
            Uploads examples from an Excel file to a ChromaDB collection after validating the data.

            Args:
                excel_file_obj (File-like object): An Excel file containing multiple sheets, where each sheet
                                                   represents a collection of examples for intent classification.
                customer_uuid (str): The unique identifier for the customer.
                application_uuid (str): The unique identifier for the application.
            Returns:
                CustomResponse: A response object indicating the status of the operation, with HTTP 201 Created code on success.
        """
        #Read Training Phrases sheet
        training_phrases_df = self.__read_excel(excel_file_obj= excel_file_obj, sheet_name= ChromaExcelSheet.TRAINING_PHRASES.value)

        drop_down_sheet_df = self.__read_excel(excel_file_obj, sheet_name= ChromaExcelSheet.DROP_DOWN_TABLE_SHEET.value, header = 0)

        base_intent_sub_intent_map = self.__build_customer_intent_sub_intent_map(customer_uuid, application_uuid)

        self.__validate_dropdowntable_sheet(drop_down_sheet_df, base_intent_sub_intent_map)

        if training_phrases_df.iloc[2:].empty:
            raise CustomException(ErrorMessages.TRAINING_PHRASES_SHEET_EMPTY, status_code= status.HTTP_400_BAD_REQUEST)

        # Refer to Excel Template
        training_phrases_df.columns = training_phrases_df.iloc[1]  # Set the second row as the header

        training_phrases_df = training_phrases_df[2:].reset_index(drop=True)  # Drop the first two rows and reset the index

        sheet_headers = training_phrases_df.columns.tolist()
        #Match the sheet headers with expected headers
        self.__validate_training_phrases_sheet_headers(sheet_headers, EXPECTED_COLUMNS)
        #filter NaN values and replace \\n with \n
        self.__preprocess_dataframe(training_phrases_df)

        error_rows = []

        self.__handle_duplicates(dataframe= training_phrases_df, error_rows= error_rows)

        #prepare intent, sub intent map for unique training phrases and find out if there is any invalid rows
        #Ex invalid row - query present but no intent, sub intent etc
        resultant_map = map_intent_sub_intents_for_query(training_phrases_df)

        queries = list(resultant_map.keys())
        similar_training_phrases = None

        # fetch collection_name mapped to the respective customer application
        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid,
                                                                                                application_uuid)
        vector_embeddings = []

        if queries:
            vector_embeddings = self.chroma_vector_store.embed_query_list(queries)
            similar_training_phrases = self.chroma_vector_store.find_similar_records(collection_name= collection_name, query_embeddings= vector_embeddings)

        # If similar training phrases found then we will skip those if and only if their metadata is similar
        #keep track of unique documents and return

        updated_count = 0
        row_count = 0

        if similar_training_phrases:
            result = update_or_skip_examples(similar_training_phrases, resultant_map, vector_embeddings, collection_name, error_rows)
            dimension_wise_count = result.get(ChromaUtils.DIMENSION_WISE_COUNT.value)
            updated_doc_ids = result.get(ChromaUtils.UPDATED_DOC_IDS.value)
            updated_metadata_list = result.get(ChromaUtils.UPDATED_METADATA_LIST.value)
            doc_ids_list = result.get(ChromaUtils.DOC_IDS_LIST.value)
            filtered_embeddings = result.get(ChromaUtils.FILTERED_EMBEDDINGS.value)
            metadata_list = result.get(ChromaUtils.METADATA_LIST.value)
            filtered_queries = result.get(ChromaUtils.FILTERED_QUERIES.value)

            if updated_doc_ids:
                updated_count = self.chroma_vector_store.update_the_metadatas_with_document_ids(doc_ids= updated_doc_ids, new_metadatas= updated_metadata_list, collection_name= collection_name)
            if doc_ids_list:
                row_count = self.chroma_vector_store.upload_utterances_at_once(ids_list= doc_ids_list, vector_embeddings_list= filtered_embeddings, metadata_list= metadata_list, training_phrases_list= filtered_queries, collection_name= collection_name)

            if dimension_wise_count:
                self.__update_dimension_counts(dimension_wise_count, customer_uuid, application_uuid)

        error_groups = self.__group_error_rows(error_rows)

        return CustomResponse( {"insertion_count" :  row_count,"updated_count" : updated_count, "error_rows" : error_groups} , code= status.HTTP_201_CREATED)


    def _extract_intents_and_subintents(self, metadata):
        intents_subintents_map = {}
        for key, value in metadata.items():
            if not value:
                continue
            if key.startswith(ChromadbMetaDataParams.INTENT.value):  # "INTENT,<intent_name>"
                intent_name = key.split(",")[1]
                if intent_name not in intents_subintents_map:
                    intents_subintents_map[intent_name] = set()
            elif key.startswith(ChromadbMetaDataParams.SUB_INTENT.value):  # "SUBINTENT,<intent_name>,<sub_intent_name>"
                parts = key.split(",")
                intent_name, sub_intent_name = parts[1], parts[2]
                intents_subintents_map.setdefault(intent_name, set()).update({sub_intent_name})

        return intents_subintents_map

    def _create_row(self, row_id, document, intents_subintents_map):

        row = [row_id, document]  # ID and Training Phrase
        for idx, (intent, sub_intents) in enumerate(intents_subintents_map.items(), start=1):
            if idx > 5:  # Limit to Intent 1-5 and Sub Intent 1-5
                break
            row.extend([intent, ", ".join(sub_intents)])  # Intent and comma-separated sub-intents
        while len(row) < len(EXPECTED_COLUMNS):  # Pad remaining columns with empty strings
            row.append("")
        return row

    def _generate_training_phrase_rows(self, metadatas, documents):
        rows = []
        for i, (metadata, doc) in enumerate(zip(metadatas, documents)):
            intents_subintents_map = self._extract_intents_and_subintents(metadata)
            row = self._create_row(i + 1, doc, intents_subintents_map)
            rows.append(row)
        return rows

    def download_training_phrases(self, application_uuid, customer_uuid):
        """
            Downloads the training phrases for a specific application and customer as an Excel file.

            This method retrieves metadata and documents from the Chroma vector store for the specified
            application and customer. It processes the data into rows suitable for training phrases,
            writes the data to an Excel file, encodes the file in base64 format, and returns it in the response.

            Args:
                application_uuid (str): The unique identifier for the application.
                customer_uuid (str): The unique identifier for the customer.

            Raises:
                Exception: Any exceptions encountered during file creation, encoding, or cleanup are logged
                           and should be handled by the calling code.

            Returns:
                CustomResponse: A response object containing:
                    - filename (str): The name of the generated Excel file.
                    - filedata (str): The base64-encoded content of the Excel file.
        """

        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid,
                                                                                                      application_uuid)

        metadata = {   ChromadbMetaDataParams.CATEGORY.value:
                       CategoriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value}
        records = self.chroma_vector_store.get_records_by_metadata(metadata_combination=[metadata],
                                                                   collection_name=collection_name)

        # Parse metadata and documents
        documents, metadatas = records['documents'], records['metadatas']

        rows = self._generate_training_phrase_rows(metadatas, documents)


        try:
            # Generate the DataFrame
            df = pd.DataFrame(rows, columns=EXPECTED_COLUMNS)

            # Write the Excel file to memory
            output_buffer = BytesIO()
            df.to_excel(output_buffer, index=False, engine='openpyxl')

            output_buffer.seek(0)  # Reset the buffer position to the beginning

            # Encode the content to Base64
            excel_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

            # Close the buffer
            output_buffer.close()

            # Prepare a response with metadata
            response = {
                "file_name": DOWNLOAD_INTENT_EXCEL_NAME,  # Provide a suggested file name
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "file_content": excel_base64
            }

            # Example: You can return or send the response as needed
            logger.info("File generated successfully!")

            return CustomResponse(result=response, code=status.HTTP_200_OK)


        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise CustomException(f"An unexpected error occurred: {e}")

    def resolve_duplicates(self, application_uuid : str, customer_uuid : str, utterances : list):

        """
            Resolves duplicates in training phrases by embedding them into a vector store
            and uploading them with metadata.

            Args:
                application_uuid (str): Unique identifier for the application.
                customer_uuid (str): Unique identifier for the customer.
                utterances (list): List of dictionaries, each containing
                    'training_phrase', 'doc_id', and 'metadata' keys.

            Returns:
                CustomResponse: A response object indicating the number of rows successfully inserted.
        """

        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid, application_uuid)

        doc_ids, training_phrases_list, metadata_list = [], [], []

        dimension_wise_count = dict()

        for utterance in utterances:

            intent_sub_intent_map = utterance.get(ChromaExcelSheet.INTENT_SUBINTENT_MAP.value, {})

            #If doc_id is present then it is present in ChromaDB
            doc_id = utterance.get(ChromaExcelSheet.DOC_ID.value)

            training_phrase = utterance.get(ChromaExcelSheet.TRAINING_PHRASE.value)

            if doc_id:
                metadata = None
            else:
                doc_id = str(uuid.uuid4())

                current_timestamp = get_current_unix_timestamp()
                metadata = prepare_metadata(intent_sub_intent_map= intent_sub_intent_map)
                # Update metadata with necessary fields
                metadata.update({
                    ChromadbMetaDataParams.CATEGORY.value: CategoriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value,
                    ChromadbMetaDataParams.CREATED_TIMESTAMP.value: current_timestamp,
                    ChromadbMetaDataParams.UPDATED_TIME_STAMP.value: current_timestamp
                })

                update_dimension_wise_count(intent_sub_intent_map, dimension_wise_count)

            # Append data to respective lists
            doc_ids.append(doc_id)
            training_phrases_list.append(training_phrase)
            metadata_list.append(metadata)

        # Generate embeddings for training phrases
        embedding_vectors = self.chroma_vector_store.embed_query_list(queries= training_phrases_list)

        # Upsert data to the vector store
        row_count = self.chroma_vector_store.upsert_utterances_at_once(collection_name, ids= doc_ids, documents= training_phrases_list,
                                                                       metadatas = metadata_list, embeddings= embedding_vectors)

        if dimension_wise_count:
            self.__update_dimension_counts(dimension_wise_count, customer_uuid, application_uuid)

        return CustomResponse(result= f"Successfully inserted/ updated {row_count} rows.", code = status.HTTP_201_CREATED)



    def download_template(self):

        try:
            blob_template_url = settings.TRAINING_PHRASES_IMPORT_TEMPLATE
            #download and send the bytes stream to UI
            content_bytes = self.azure_blob_manager.download_data_with_url(blob_url= blob_template_url)

            content_base64 = base64.b64encode(content_bytes).decode('utf-8')

            file_name = blob_template_url.split('/')[-1]
            # Send the binary content directly as a file download
            return CustomResponse(
                result={"file_content": content_base64, "mime_type" : SPREAD_SHEET_MACRO_ENABLED, "file_name" : file_name},
                code=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error occured while downloading the template : {e}")
            raise CustomException(f"Error occured while downloading the template : {e}", status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)

