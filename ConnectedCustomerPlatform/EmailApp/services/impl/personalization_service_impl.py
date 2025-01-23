import json
from pathlib import Path
import pandas as pd
from typing import List
import uuid
import os
import mimetypes

from django.db import transaction

from EmailApp.dao.impl.dimension_type_dao_impl import DimensionTypeDaoImpl
from ConnectedCustomerPlatform.responses import CustomResponse
from EmailApp.constant.constants import BOOLEAN_TRUE_STRING, INSTUCTIONS_SHEET_NAME_OF_EXCEL, INTENT_TRAINING_PHRASES_INSTRUCTIONS_TEMPLATE_FILE_NAME, SPREAD_SHEET_CONTENT_TYPE, \
    BulkImportExcelHeaders, ChromaDBParams as ChromaParams, DefaultPaginationValues, ReturnTypes
from EmailApp.DataClasses.response.pagination_data import PaginationResponse
from EmailApp.constant.error_messages import PersonalizationErrorMessages, ErrorMessages
from EmailApp.constant.constants import ChromaDBParams as ChromaParams, DefaultPaginationValues, PaginationParams
from EmailApp.services.interface.personalization_service_interface import IPersonalizationServiceInterface
from EmailApp.dao.impl.dimension_dao_impl import DimensionDaoImpl 
from EmailApp.utils import datetime_to_milliseconds, is_valid_dimension_name, style_header, validate_chroma_results, \
    extract_intent_subintents, update_existing_training_phrase_metadata, remove_intent_and_sub_intents_from_metadata, \
    get_intent_and_sub_intent, get_sub_intent_keys_from_metadata
from EmailApp.constant.constants import CsrChromaDbFields, ChromadbMetaDataParams, CategoriesForPersonalization, UtterancesGeneratorParams, DimensionTypeNames
from Platform.utils import paginate_queryset
from EmailApp.utils import parse_excel_to_list_of_examples,get_metadata_and_presigned_url
from EmailApp.constant.constants import ChannelTypes
import logging
from rest_framework import status
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException, \
    InvalidCollectionException
from AIServices.VectorStore.chromavectorstore import ChromaVectorStore
from datetime import datetime
from django.conf import settings
import openpyxl
from django.http import HttpResponse
from Platform.services.impl.dimension_service_impl import DimensionServiceImpl
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory

logger = logging.getLogger(__name__)

class PersonalizationServiceImpl(IPersonalizationServiceInterface):
    def __init__(self):
        self.dimension_dao = DimensionDaoImpl()
        self.chroma_vector_store= ChromaVectorStore()
        self.dimension_type_dao=DimensionTypeDaoImpl()
        self.dimension_service_impl_platform=DimensionServiceImpl()
        self.azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

    
    def delete_response_configurations(self, customer_uuid: str, application_uuid: str, response_config_uuid: str) -> List[str]:
        """
        Delete email responses with response_config_uuid which is stored in metadata
        """

        logger.info("In PersonalizationServiceImpl ::  delete_response_configurations")
        #get chroma collection name
        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid=customer_uuid, application_uuid=application_uuid)
        
        response_config_uuid_metadata = [{CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: response_config_uuid}]
        
        #deletes email responses documents by fetching with metadata
        deleted_ids=self.chroma_vector_store.delete_emails_by_metadata(metadata=response_config_uuid_metadata, collection_name=collection_name)
        return deleted_ids

    def fetch_intents_subintents_sentiment(self, customer_uuid, application_uuid,include_sentiments=False):
        """
        fetches intents, subintents and sentiments for given customer and application

        response format:
        {'intent_subintent':{intent1:[subintent1,subintent2]}
        'sentiment':[sentiment1,sentiment2]}
        """
        logger.info("In PersonalizationServiceImpl ::  fetch_intents_subintents_sentiment")
        #Intents and subintents
        #intents_subintents=self.dimension_dao.get_intent_subintents_for_customer_application(customer_uuid,application_uuid)
        intent_and_sub_intents = self.dimension_dao.fetch_parent_and_child_dimension_details(
            customer_uuid=customer_uuid, application_uuid=application_uuid,
            parent_dimension_type_name=DimensionTypeNames.INTENT.value)
        # Format the results in {intent:[sub_intents]} format from [(intent1,[subintents1,sub_intent2])]
        result = {}
        intents_subintents_dict = {}
        for row in intent_and_sub_intents:
            intent_name = row.dimension_name
            sub_intent_names = [row.get('child_dimension_name',None) for row in row.child_dimensions]

            intents_subintents_dict[intent_name] = sub_intent_names
        # Fetch List of Sentiments
        result['intent_subintent']=intents_subintents_dict
        if include_sentiments:
            sentiments = self.dimension_dao.get_dimensions_list_by_dimension_type_name(DimensionTypeNames.SENTIMENT.value,customer_uuid,application_uuid)
            result['sentiment']=list(sentiments)

        return result


    def save_response_configurations(self, customer_uuid,application_uuid,user_uuid,excel_file_data,payload_metadata):
        """
        Saves response configurations by processing request data and uploaded files.
        :param : customer_uuid
        :param : application_uuid
        :param: user_uuid
        :param files: The uploaded excel file
        :param validated_data: The validated request data(intent,sub_intent,sentiment,response_config_uuid,is_default).
        :return: Success status
        """
        logger.info("In PersonalizationServiceImpl :: save_response_configurations")
        intent = payload_metadata.get(CsrChromaDbFields.INTENT.value)
        sub_intent =payload_metadata.get(CsrChromaDbFields.SUB_INTENT.value)
        sentiment = payload_metadata.get(CsrChromaDbFields.SENTIMENT.value)
        response_config_uuid=payload_metadata.get(CsrChromaDbFields.RESPONSE_CONFIG_UUID.value)
        is_default=payload_metadata.get(CsrChromaDbFields.IS_DEFAULT.value)
        text_to_show=payload_metadata.get(CsrChromaDbFields.TEXT_TO_SHOW.value)
        #parses responses from excel file and upload in azure
        excel_url,responses=self.__process_and_upload_excel_file(excel_file_data,customer_uuid,application_uuid)

        collection_name=self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid=customer_uuid,application_uuid=application_uuid)
        logger.debug(f"Chroma collection name:{collection_name}")
        #if none create response_config_uuid and save with it
        if response_config_uuid is None or response_config_uuid=="":
            response_config_uuid=str(uuid.uuid4())

        #if not it means to edit the same response_config(delete previous one and save new one)
        else:
            deleted_ids = self.chroma_vector_store.delete_emails_by_metadata(metadata=[{CsrChromaDbFields.RESPONSE_CONFIG_UUID.value:response_config_uuid}],collection_name=collection_name)
        
            if deleted_ids:
                logger.debug(f"Deleted existing documents with ids for updating the same row {deleted_ids}")
            else:
                logger.error(PersonalizationErrorMessages.RESPONSE_CONFIG_NOT_PRESENT)
                raise InvalidValueProvidedException(PersonalizationErrorMessages.RESPONSE_CONFIG_NOT_PRESENT)
        
        metadata_for_saving={CsrChromaDbFields.CATEGORY.value:CategoriesForPersonalization.RESPONSE_GENERATION_CATEGORY.value,
                    CsrChromaDbFields.RESPONSE_CONFIG_UUID.value:response_config_uuid,
                    CsrChromaDbFields.CSR_UUID.value:user_uuid,
                    CsrChromaDbFields.IS_DEFAULT.value:is_default,
                    CsrChromaDbFields.INTENT.value: intent,
                    CsrChromaDbFields.SUB_INTENT.value: sub_intent,
                    CsrChromaDbFields.SENTIMENT.value: sentiment,
                    CsrChromaDbFields.FILE_URL.value:excel_url,
                    CsrChromaDbFields.TIME_STAMP.value:datetime_to_milliseconds(datetime.now()),
                    CsrChromaDbFields.TEXT_TO_SHOW.value:text_to_show #added for UI
                    }
        #add each example response with metadata seperatly in chromadb
        for response in responses:
            ids =  self.chroma_vector_store.add_emails_and_metadata(metadata=metadata_for_saving,emails=response,collection_name=collection_name)
            logger.debug(f"Added documents with ids -{ids}")

    def __process_and_upload_excel_file(self,excel_file_data,customer_uuid,application_uuid):
        """
        parse excel to get responses and upload the excel to azure
        """
        logger.info("In PersonalizationServiceImpl :: __process_and_upload_excel_file")
        #parses excel to list of examples
        responses=parse_excel_to_list_of_examples(excel_file_data['data'])
        logger.debug(f"Emails and responses retrived from excel file{responses}")
        # Upload the excel file to azure
        response_urls_list=self.upload_attachments_to_azure_blob(customer_uuid,application_uuid,[excel_file_data] ,ChannelTypes.EMAIL.value) #returns as list
        
        if response_urls_list is None or not response_urls_list:
            logger.error('Error occured while uploading the file')
            raise CustomException('Error occured while uploading the file', status_code=status.HTTP_404_NOT_FOUND)
        excel_url=response_urls_list[0]
        logger.debug(f"File uploaded successfully to url - {excel_url}")
        return excel_url,responses

    def upload_attachments_to_azure_blob(self,customer_uuid,application_uuid,attachments,channel_type):
        if not attachments:
            raise InvalidValueProvidedException(detail=ErrorMessages.BAD_REQUEST, status_code=400)
        blob_urls = []
        for attachment in attachments:
            file_name = attachment["filename"] or "attachment"
            content_type = attachment["content_type"]
            data = attachment["data"]

            # Handle missing file extension
            _, ext = os.path.splitext(file_name)
            if not ext:
                extension = mimetypes.guess_extension(content_type)
                file_name += extension or ''

            # Ensure filename uniqueness
            file_name = str(uuid.uuid4()) + '_' + file_name
            blob_url = self.azure_blob_manager.upload_data(
                data = data.encode('utf-8'),
                file_name = file_name,
                over_write = True,
                customer_uuid = customer_uuid,
                application_uuid = application_uuid,
                channel_type = channel_type,
                return_type = ReturnTypes.URL.value,
                content_type = content_type
            )
            blob_urls.append(blob_url)
        return blob_urls


    def fetch_dimension_utterances_for_customer_application(self,params: dict,customer_uuid: str,application_uuid: str, user_uuid: str,dimension_names,parent_dimension_name):

        """
        This method is to fetch utterances of given intent with  specified collection(customer, application)

        :param params:
        :param customer_uuid:
        :param application_uuid:
        :param mapping_uuid:
        :param user_uuid:
        :return:  A dictionary containing paginated utterance data.
        """

        logger.info("In PersonalizationServiceImpl :: fetch_intent_utterances_for_customer_application")
        #child_dimension_name,parent_dimension_name=self.dimension_dao.fetch_dimension_parent_dimension_name_by_dimension_uuid(mapping_uuid,customer_uuid,application_uuid)
        #child_dimensions = dimension_names.split(ChromadbMetaDataParams.SEPARATOR.value)
        mandatory_metadata = {ChromadbMetaDataParams.CATEGORY.value: CategoriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value}
        metadata=[]
        for dimension in dimension_names:
            if not parent_dimension_name:
                metadata.append({ChromadbMetaDataParams.INTENT.value+ChromadbMetaDataParams.SEPARATOR.value+dimension.lower():True})
            else:
                metadata.append({ChromadbMetaDataParams.SUB_INTENT.value+ChromadbMetaDataParams.SEPARATOR.value+parent_dimension_name.lower()+ChromadbMetaDataParams.SEPARATOR.value+dimension.lower():True})
        #metadata combination to get utterances from chroma db
        logger.info(f"Metadata Key :: {metadata}")

        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(application_uuid=application_uuid,
                                                                             customer_uuid=customer_uuid)

        logger.debug(f"collection_name :: {collection_name}")
        try:
            if not parent_dimension_name:
                metadata.append(mandatory_metadata)
                #fetch utterances list from chroma db based on given metadata
                utterances_list = self.chroma_vector_store.get_records_by_metadata(metadata, collection_name=collection_name)
            else:

                utterances_list = self.chroma_vector_store.get_records_by_metadata_with_specific_fields(collection_name=collection_name,mandatory_fields=[mandatory_metadata,{ChromadbMetaDataParams.SUB_INTENT_FILTER.value:True}],optional_fields=metadata)
        except InvalidCollectionException as e:
            logger.error(f"Exception in fetching utterances:: {e}")
            #instead of throwing error incase of exception returning empty page
            paginated_Response= PaginationResponse(page_num=DefaultPaginationValues.PAGE_NUM.value, total_entry_per_page=params[
                PaginationParams.TOTAL_ENTRY_PER_PAGE.value], total_entries=DefaultPaginationValues.TOTAL_ENTRIES.value,
                                      total_pages=DefaultPaginationValues.TOTAL_PAGES.value,
                                      data=[]).model_dump()
            paginated_Response['count_of_utterences']=0

            return paginated_Response

        except Exception as e:
            logger.error(f"Exception in fetching utterances :: {e}")
            if f"Collection {collection_name} does not exist" in str(e):
                paginated_Response= PaginationResponse(page_num=DefaultPaginationValues.PAGE_NUM.value, total_entry_per_page=params[
                PaginationParams.TOTAL_ENTRY_PER_PAGE.value], total_entries=DefaultPaginationValues.TOTAL_ENTRIES.value,
                                      total_pages=DefaultPaginationValues.TOTAL_PAGES.value,
                                      data=[]).model_dump()
                paginated_Response['count_of_utterences']=0

                return paginated_Response
            raise CustomException(ErrorMessages.ERROR_IN_FETCHING_UTTERANCES)
        #converting/mapping chroma raw response to dictionary containing the Utterance ID, content, intent name and timestamps (created and updated) for each document
        utterances_list = self.__extract_utterance_data_from_chroma_response(utterances_list,parent_dimension_name,dimension_names)
        paginated_data, paginator = paginate_queryset(utterances_list, params)

        paginated_Response= PaginationResponse(page_num=paginated_data.number,total_entry_per_page=params[PaginationParams.TOTAL_ENTRY_PER_PAGE.value],total_entries=paginator.count,total_pages=paginated_data.paginator.num_pages,data=paginated_data.object_list).model_dump()
        paginated_Response['count_of_utterences']=len(utterances_list)

        return paginated_Response
    #Todo for now getting whole data from chroma server and applying pagination and check if possible to get the paginated data instead of getting whole data
    def __extract_utterance_data_from_chroma_response(self,chroma_response,parent_dimension_name,child_dimensions):
        """

        :param chroma_response:
        :return: A sorted list of dictionaries, each containing the Utterance ID, content, intent name,
            and timestamps (created and updated) for each document.
        """
        logger.info("In PersonalizationServiceImpl :: __create_id_utterance_mapping")
        utterance_ids = chroma_response.get(ChromaParams.IDS.value, [])
        documents = chroma_response.get(ChromaParams.DOCUMENTS.value, [])
        metadata = chroma_response.get(ChromaParams.METADATA.value, [])

        # Create a list of dictionaries with 'id', 'content', and 'time_stamp'
        id_document_map = [
            {
                UtterancesGeneratorParams.ID.value: utterance_id,
                UtterancesGeneratorParams.CONTENT.value: "" if not utterance or utterance.strip() == "" else utterance,
                ChromadbMetaDataParams.CREATED_TIMESTAMP.value: metadata.get(ChromadbMetaDataParams.CREATED_TIMESTAMP.value),
                ChromadbMetaDataParams.UPDATED_TIME_STAMP.value: metadata.get(ChromadbMetaDataParams.UPDATED_TIME_STAMP.value),
                "Dimensions":extract_intent_subintents(metadata,parent_dimension_name,child_dimensions)
            }
            for utterance_id, utterance, metadata in zip(utterance_ids, documents, metadata)
        ]
        #sorting utterances based on updated_ts in descending order
        return sorted(id_document_map, key=lambda x: x[ChromadbMetaDataParams.UPDATED_TIME_STAMP.value], reverse=True)

    def delete_utterance_from_chroma_server(self, customer_uuid: str, application_uuid: str, utterance_id: str,mapping_uuid: str,child_dimension_names,parent_dimension_name):
        """
        Deletes a specific utterance from the Chroma DB for a given customer and application.

        :param customer_uuid:
        :param application_uuid:
        :param utterance_id:
        """


        logger.info("PersonalizationServiceImpl :: delete_utterance_from_chroma_server")
        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(application_uuid=application_uuid,
                                                                             customer_uuid=customer_uuid)

        logger.info(f"chroma collection name :: {collection_name}")
        if mapping_uuid:
            child_dimension_names, parent_dimension_name = self.dimension_dao.fetch_dimension_parent_dimension_name_by_dimension_uuid(
                mapping_uuid, customer_uuid, application_uuid)
            child_dimension_names=[child_dimension_names]
        chroma_example=self.chroma_vector_store.get_record_by_id(collection_name=collection_name,id=utterance_id)
        document,metadata,embedding=validate_chroma_results(chroma_example)
        if not document or not metadata or not embedding:
            raise CustomException("Invalid dimension combination")
        if parent_dimension_name:
            child_dimension_names = get_sub_intent_keys_from_metadata(intent_identified=parent_dimension_name,sub_intent_metadata=metadata)
        intent, sub_intents = get_intent_and_sub_intent(parent_dimension_name=parent_dimension_name, child_dimension_name=child_dimension_names)
        if isinstance(intent,list) and len(intent)>0:
            intent=intent[0]
        modified_metadata=remove_intent_and_sub_intents_from_metadata(metadata, intent=intent, sub_intents=sub_intents,remove_intent=True)
        metadata_has_other_intents,modified_metadata = update_existing_training_phrase_metadata(metadata=modified_metadata)
        if metadata_has_other_intents:
            self.chroma_vector_store.update_metadata_by_id(utterance_id,modified_metadata,document,embedding,collection_name)
        else:
            self.chroma_vector_store.delete_record_by_id([utterance_id], collection_name=collection_name)
        if not parent_dimension_name:
            if isinstance(child_dimension_names, list) and len(child_dimension_names) == 1:
                parent_dimension_name = child_dimension_names[0]
            else:
                raise InvalidValueProvidedException("Invalid Dimension names")
            sub_intent_names=get_sub_intent_keys_from_metadata(intent_identified=parent_dimension_name,sub_intent_metadata=metadata)
            if sub_intent_names:
                self.dimension_dao.reduce_training_phrase_count_for_dimensions(customer_uuid=customer_uuid,
                                                                               application_uuid=application_uuid,
                                                                               parent_dimension_name=parent_dimension_name,
                                                                               dimension_names=sub_intent_names)
            self.dimension_dao.reduce_training_phrase_count_for_dimensions(customer_uuid=customer_uuid,
                                                                           application_uuid=application_uuid,
                                                                           parent_dimension_name=None,
                                                                           dimension_names=child_dimension_names)
            return
        self.dimension_dao.reduce_training_phrase_count_for_dimensions(customer_uuid=customer_uuid,application_uuid=application_uuid,parent_dimension_name=parent_dimension_name,dimension_names=child_dimension_names)
        self.dimension_dao.reduce_training_phrase_count_for_dimensions(customer_uuid=customer_uuid,
                                                                       application_uuid=application_uuid,
                                                                       parent_dimension_name=None,
                                                                       dimension_names=[parent_dimension_name])

    
    def download_template(self):
        """
        Downloads the default template which is stored in azure and the url is stored in settings
        """
        try:
            default_template_data=get_metadata_and_presigned_url(settings.RESPONSE_CONFIGS_TEMPLATE_URL)
            logger.debug("Successfully fetched the file url of template")
            return default_template_data
        
        except Exception as e:
            logger.error(PersonalizationErrorMessages.ERROR_DOWNLOADING_TEMPLATE.format(e))
            raise CustomException(PersonalizationErrorMessages.ERROR_DOWNLOADING_TEMPLATE.format(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def fetch_response_configurations(self,customer_uuid,application_uuid,user_uuid,is_default):

        """
        Fetch the saved response configuration (metadata_combination and excel file url)
        if is_default is True fetch configurations of csr_Admin
        else: fetch configurations uploaded by the csr user
        """
        logger.info("In :: PersonalizationServiceImpl :: fetch_response_configurations")
        
        if is_default is True: #default csr(csr admin) case
            metadata=[{CsrChromaDbFields.IS_DEFAULT.value:is_default},
                      {CsrChromaDbFields.CATEGORY.value:CategoriesForPersonalization.RESPONSE_GENERATION_CATEGORY.value}]
            
        else: #csr_usr case
            metadata=[{CsrChromaDbFields.CSR_UUID.value:user_uuid},
                      {CsrChromaDbFields.CATEGORY.value:CategoriesForPersonalization.RESPONSE_GENERATION_CATEGORY.value}]
        
        #gets chroma collection name
        collection_name=self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid,application_uuid)
        logger.debug(f"Chroma collection name:{collection_name}")
        try:
            metadatas_of_example_response_configs = self.chroma_vector_store.get_records_by_metadata(metadata,collection_name=collection_name)['metadatas']
        except InvalidCollectionException as e:
            logger.error(f"Exception in fetching responses ,collection not found :: {e}") 
            return [] 
        #TODO :: remove the manual check of exception
        except Exception as e:
            if f"Collection {collection_name} does not exist" in str(e):
                return []
            raise CustomException(f"Error occurd while fetching records {e}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Since we are storing each response as seperate document, we will get duplicate responses for same metadata_combination. So adding only unique ones. 
        response_data = []

        for metadata in metadatas_of_example_response_configs:
            #if file_url is None it means the example is not added by response_configurations UI
            if metadata.get(CsrChromaDbFields.FILE_URL.value, '') != '':  # Check if file_url key does not exists or the file_url is empty
                
                # Create a Response object
                response = ResponseConfiguration(
                    response_config_uuid = metadata.get(CsrChromaDbFields.RESPONSE_CONFIG_UUID.value, None),
                    intent = metadata.get(CsrChromaDbFields.INTENT.value, None),
                    sub_intent = metadata.get(CsrChromaDbFields.SUB_INTENT.value, None),
                    sentiment = metadata.get(CsrChromaDbFields.SENTIMENT.value, None),
                    downloadable_url = get_metadata_and_presigned_url(metadata.get(CsrChromaDbFields.FILE_URL.value, '')),
                    text_to_show = metadata.get(CsrChromaDbFields.TEXT_TO_SHOW.value, None),
                    time_stamp=metadata.get(CsrChromaDbFields.TIME_STAMP.value,0)
                )

                # Only add unique responses
                if response.to_dict() not in response_data:
                    response_data.append(response.to_dict())  # Convert to dict before appending
                        
        # Sort the responses by timestamp in descending order
        sorted_response_data = sorted(response_data, key=lambda x: x.get(CsrChromaDbFields.TIME_STAMP.value, 0), reverse=True)

        logger.info("Successfully fetched the unique configurations")
        return sorted_response_data
    

    def download_intents_with_training_phrases(self, customer_uuid, application_uuid, user_uuid,Dimension_type_name):
        """
        Generates an Excel file containing intents as separate sheets, 
        with each sheet listing training phrases and their corresponding descriptions.

        :param customer_uuid: UUID of the customer for which intents are to be fetched.
        :param application_uuid: UUID of the application associated with the intents.
        :param user_uuid: UUID of the user requesting the download.
        :return: An HTTP response containing the generated Excel file as a byte stream.
        """
        logger.info("In PersonalizationServiceImpl :: download_intents_with_training_phrases")
        try:
            # Load the instructions template
            instructions_template_path = Path(settings.BASE_DIR) / settings.STATIC_URL.strip("/") / INTENT_TRAINING_PHRASES_INSTRUCTIONS_TEMPLATE_FILE_NAME
            workbook = openpyxl.load_workbook(instructions_template_path)

            # Fetch all intents details [(intent_uuid, intent_name, description)]
            intent_details = self.dimension_dao.get_dimension_uuid_dimension_name_description(
                customer_uuid, application_uuid, Dimension_type_name
            )
            logger.debug("Dimension details fetched succesfully")

            # Fetch training phrases from ChromaDB for each intent
            for dimension in intent_details:
                dimension_uuid,dimension_name,description = dimension

                # Fetch training phrases from ChromaDB for this intent
                training_phrases = self.__fetch_dimension_utterances_for_customer_application(
                    customer_uuid, application_uuid, dimension_uuid, user_uuid
                )

                # Create a new sheet for each intent
                sheet = workbook.create_sheet(title=dimension_name)
                
                sheet['A1'] = BulkImportExcelHeaders.DESCRIPTION_HEADER     # Add headers for description at row 1
                sheet['A4'] = BulkImportExcelHeaders.TRAINING_PHRASES_HEADER # Add headers for training phrases at row 4

                # Add the description value in the second row
                sheet['A2'] = description 
                
                #style the two headers
                style_header(sheet['A4'])
                style_header(sheet['A1'])
               
                # Write the training phrases row by row
                for idx, phrase in enumerate(training_phrases,start=5):
                    sheet[f'A{idx}'] = json.loads(phrase)  #Convert the phrase because while adding training phrases in chroma it is converting as json

                # Set column width for training phrases to max length of characters
                sheet.column_dimensions['A'].width = 250  
            
            logger.debug("Excel prepared as response")
            # Prepare the HTTP response with appropriate content type
            response = HttpResponse(content_type=SPREAD_SHEET_CONTENT_TYPE)
            response['Content-Disposition'] = f'attachment; filename={customer_uuid}_intents_training_phrases.xlsx'

            # Save the workbook directly to the response (streaming)
            workbook.save(response)

            return response
        except Exception as e:
            logger.error(f"Error occurred while generating the Excel file: {str(e)}")
            return None
        finally:
            if 'workbook' in locals():
                workbook.close()  # Close the workbook

    def __fetch_dimension_utterances_for_customer_application(self,customer_uuid: str,application_uuid: str, dimension_uuid: str, user_uuid: str):

        """
        This method is to fetch utterances of given intent with  specified collection(customer, application)

        :param params:
        :param customer_uuid:
        :param application_uuid:
        :param dimension_uuid:
        :param user_uuid:
        :return:  A list of documents fetched from chromadb.
        """

        logger.info("In PersonalizationServiceImpl :: fetch_dimension_utterances_for_customer_application")

        #metadata combination to get training phrases from chroma db
        metadata = [{ChromadbMetaDataParams.DIMENSION_UUID.value: dimension_uuid},
                    {ChromadbMetaDataParams.CATEGORY.value: CategoriesForPersonalization.CLASSIFICATION_CATEGORY.value}]

        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(application_uuid=application_uuid,
                                                                             customer_uuid=customer_uuid)

        logger.debug(f"collection_name :: {collection_name}")
        try:
            #fetch utterances list from chroma db based on given metadata
            utterances_list = self.chroma_vector_store.get_records_by_metadata(metadata, collection_name=collection_name).get(ChromaParams.DOCUMENTS.value, [])
            return utterances_list
        except InvalidCollectionException as e:
            logger.error(f"Exception in fetching utterances:: {e}")
            #instead of throwing error incase of exception returning empty
            return []

        except Exception as e:
            logger.error(f"Exception in fetching utterances :: {e}")
            if f"Collection {collection_name} does not exist" in str(e):
                return  []
            else:
                raise

            
    @transaction.atomic
    def bulk_import_training_phrases(self, excel_file_obj, customer_uuid, application_uuid, user_uuid):
        logger.info("In PersonalizationServiceImpl :: bulk_import_training_phrases")
        excel_data = self.__read_excel(excel_file_obj)
        logger.info("Excel reading successful")
        #validate sheet names as dimensions
        logger.info("Validating sheet names")
        for sheet_name, _sheet_data in excel_data.items():
            if not is_valid_dimension_name(sheet_name):
                logger.error(f"Name of sheet {sheet_name} is Invalid.\n Only alphanumeric characters and hyphens are allowed. The value must be 2-64 characters long and cannot start or end with a hyphen.")
                raise InvalidValueProvidedException(f"Name of sheet {sheet_name} is Invalid.\n Only alphanumeric characters and hyphens are allowed. The value must be 2-64 characters long and cannot start or end with a hyphen.")
        logger.info("Successfully validated sheet names")
        # Retrieve existing intents dimension_uuid and dimension_name and convert it to dictionary
        existing_intents = self.dimension_dao.get_mapping_dimension_uuid_dimension_name_list(
            DimensionTypeNames.INTENT.value, customer_uuid, application_uuid
        )
        #Preparing the dictionary of above data
        existing_intents_dict = {intent_name.lower(): (mapping_uuid,intent_uuid) for mapping_uuid, intent_uuid, intent_name in existing_intents}

        #Get dimension_uuid for INTENT dimension_type for adding dimension
        dimension_type_uuid = self.dimension_type_dao.get_dimension_type_uuid_by_name(
                    DimensionTypeNames.INTENT.value, customer_uuid, application_uuid
                )
        if not dimension_type_uuid:
            logger.error(f"Dimension type uuid not found for type: {DimensionTypeNames.INTENT.value}, customer_uuid: {customer_uuid} and application_uuid: {application_uuid}")
            return CustomResponse(f"Dimension type not found for {DimensionTypeNames.INTENT.value}.", code=status.HTTP_400_BAD_REQUEST)

        # Iterate over all sheets (intents) in the Excel file
        for sheet_name, sheet_data in excel_data.items():
            if sheet_name == INSTUCTIONS_SHEET_NAME_OF_EXCEL:
                continue  # Skip the 'Instructions' sheet
            try:
                # Ensure sheet has required columns at cell A1, A4
                if (sheet_data.iloc[0, 0],sheet_data.iloc[3, 0]) != (BulkImportExcelHeaders.DESCRIPTION_HEADER,BulkImportExcelHeaders.TRAINING_PHRASES_HEADER,):
                    return CustomResponse(
                        f"Sheet '{sheet_name}' has incorrect headers. Expected [{BulkImportExcelHeaders.DESCRIPTION_HEADER},{BulkImportExcelHeaders.TRAINING_PHRASES_HEADER} in cells A1,A4 respectively",
                        code=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                raise InvalidValueProvidedException(f"Failed - Cannot find data as specified format in sheet: {sheet_name}")
            training_phrases = self.__extract_validate_training_phrases(sheet_data, sheet_name)
            # Check if intent already exists
            mapping_uuid,intent_uuid = existing_intents_dict.get(sheet_name.lower(),("",""))
            try:
                description = sheet_data.iloc[1, 0]  # Fetch description value from A2 cell
            except Exception as e:
                raise InvalidValueProvidedException(f"Cannot find description for sheet: {sheet_name}")
            if intent_uuid:
                self.__update_existing_intent(customer_uuid, application_uuid, user_uuid, sheet_name, intent_uuid, training_phrases,mapping_uuid,description)
            
                # Remove the processed intent from the dictionary. Any intents remaining in the dictionary after processing
                # indicate that they are no longer present in the uploaded Excel file, suggesting they have been deleted.
                # These remaining intents should therefore be removed from the database.
                existing_intents_dict.pop(sheet_name.lower())
            else:
                if pd.isna(description) or not description:
                    return CustomResponse(f"Sheet '{sheet_name}' is newly added intent and requires a description.", code=status.HTTP_400_BAD_REQUEST)

                # Create a new dimension and add training phrases
                self.dimension_service_impl_platform.add_dimension_and_mapping(
                    customer_uuid, application_uuid, user_uuid,
                    {"utterances": training_phrases, "dimension_type_uuid": dimension_type_uuid, "dimension_name": sheet_name, "description": description}
                )
        logger.info(f"Deleting dimensions for intents :{existing_intents_dict.keys()}")
        for mapping_uuid,_intent_uuid in existing_intents_dict.values():
            #calling delete dimension to delete the intent which also deletes their training phases
            self.dimension_service_impl_platform.delete_dimension_mapping(customer_uuid,application_uuid,user_uuid,mapping_uuid)

        return CustomResponse("Intents/Training phrases successfully saved", code=status.HTTP_201_CREATED)

    def __read_excel(self, excel_file_obj):
        """
        Tries to read the excel, if any error occured raises exception
        """
        logger.info("In PersonalizationServiceImpl :: __read_excel")
        try:
            # Load Excel sheet using Pandas for efficient processing
            excel_data = pd.read_excel(excel_file_obj, sheet_name=None, header=None)  # Load all sheets into a dictionary without any headers
            return excel_data
        except Exception as e:
            logger.error(f"Error while processing Excel file: {str(e)}")
            return CustomResponse(f"Error while processing Excel file: {str(e)}", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def __extract_validate_training_phrases(self, sheet_data, sheet_name):
        """
        Returns training phrases extracted for particular sheet.
        Validated weather they are less than 3 or each  training phrase is > 250 chars.
        If not validated returns CustomResponse with HTTP_400_BAD_REQUEST status code
        """
        # Extract training phrases and started from A5
        try:
            training_phrases = sheet_data.iloc[4:, 0].dropna().tolist()  # Start from row 5, skipping initial rows since description is saved
        except Exception as e:
            logger.error(f"Exception occurred while fetching Training phases {e}")
            raise CustomException("Exception occurred while fetching Training phases")
        # Validate training phrases
        if len(training_phrases) < 3:
            logger.error(f"Sheet '{sheet_name}' has less than 3 training phrases.")
            raise InvalidValueProvidedException(f"Sheet '{sheet_name}' has less than 3 training phrases.")
        if any(len(phrase) > 250 for phrase in training_phrases):
            logger.error(f"Some training phrases in sheet '{sheet_name}' exceed 250 characters.")
            raise InvalidValueProvidedException(f"Some training phrases in sheet '{sheet_name}' exceed 250 characters.")
        return training_phrases

    
    def __update_existing_intent(self, customer_uuid, application_uuid, user_uuid, sheet_name, intent_uuid, training_phrases,mapping_uuid,description):
        """
        Updates description and Overrides training phrases for the intent in chromadb
        """

        #Update description of existing intents
        self.dimension_dao.update_description_of_dimension(mapping_uuid=mapping_uuid,new_description=description,updated_by=user_uuid)

        # Delete existing training phrases
        metadata_to_delete = [
            {ChromadbMetaDataParams.DIMENSION_UUID.value: intent_uuid},
            {ChromadbMetaDataParams.DIMENSION_NAME.value: sheet_name},
            {ChromadbMetaDataParams.CATEGORY.value: CategoriesForPersonalization.CLASSIFICATION_CATEGORY.value}
        ]
        deleted_ids = self.chroma_vector_store.delete_emails_by_metadata(
            metadata=metadata_to_delete,
            collection_name=self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid, application_uuid)
        )
        if deleted_ids:
            logger.debug("Successfully deleted existing training phrases")

        # Add new training phrases to existing intent
        self.dimension_service_impl_platform.upload_intent_utterances_to_chroma_server(
            application_uuid, customer_uuid, user_uuid, training_phrases, intent_uuid, sheet_name
        )

    def __validate_excel_sheet_headers(self, sheet_headers : list,  expected_headers : list):
        """
           Validates that the Excel sheet contains the expected headers.

           Args:
               - sheet_headers (List[str]): Headers of Excel sheet (First row of Excel).
               - Expected Headers (List[str]): Headers you would like to compare

           Raises Exception if there is a mismatch between Expected and sheet headers.

        """

        logger.info(f"In  __validate_excel_sheet_headers :: Sheet Headers: {sheet_headers}")

        if sheet_headers != expected_headers:
            raise InvalidValueProvidedException(detail= f"Invalid Sheet Headers : {sheet_headers}. Expected Headers : {expected_headers}")


    def __build_customer_intent_sub_intent_map(self,customer_uuid, application_uuid, parent_dimension_type_name) -> dict:

        """
            Builds a mapping of customer-specific intents to their sub-intents.

            Args:
                customer_uuid (str): The unique identifier for the customer.
                application_uuid (str): The unique identifier for the application.
                parent_dimension_type_name (str): The name of the parent dimension type (e.g., "Intent").

            Returns:
                dict: A dictionary mapping intents to their respective sub-intents, where:
                      - Keys are parent intents (str).
                      - Values are lists of sub-intents (list of str).

            Dimension View Object Structure:
            Each `dimension_view` in `dimension_view_objects` is expected to have the following attributes:
            - `dimension_name` (str): The name of the parent dimension (e.g., "RETURNS").
            - `child_dimensions` (list of dict): A list of child dimension details, where each dictionary contains:
               Sample Value : [
               {"child_dimension_name" : "CHECK_PO_STATUS", "child_dimension_description" : "Checking the status of a purchase order"},
               {"child_dimension_name" : "NEW_PO", "child_dimension_description" : "Creating a new purchase order."}
               ]
        """
        #TODO Raise Exception, comment
        dimension_view_objects = self.dimension_dao.fetch_parent_and_child_dimension_details(customer_uuid, application_uuid, parent_dimension_type_name)
        base_intent_sub_intent_map = dict()
        if dimension_view_objects:
            for dimension_view in dimension_view_objects:
                temp = []
                for each_sub_intent in dimension_view.child_dimensions:
                    temp.append(each_sub_intent.get('child_dimension_name'))
                base_intent_sub_intent_map[dimension_view.dimension_name] = temp
        logger.debug(f"CUSTOMER INTENT SUB INTENT MAP :\n {base_intent_sub_intent_map}")
        return base_intent_sub_intent_map





class ResponseConfiguration:
    def __init__(self, response_config_uuid, intent, sub_intent, sentiment, downloadable_url,text_to_show,time_stamp):
        self.response_config_uuid = response_config_uuid
        self.intent = intent
        self.sub_intent = sub_intent
        self.sentiment = sentiment
        self.downloadable_url = downloadable_url
        self.text_to_show=text_to_show
        self.time_stamp=time_stamp
    #To convert to dict before sending as response
    def to_dict(self):
        return {
            'response_config_uuid': self.response_config_uuid,
            'intent': self.intent,
            'sub_intent': self.sub_intent,
            'sentiment': self.sentiment,
            'downloadable_url': self.downloadable_url,
            'text_to_show':self.text_to_show,
            'time_stamp':self.time_stamp
        }
    #overridden __eq__ to check equal or not with only response_config_uuid
    def __eq__(self, other):
        if not isinstance(other,ResponseConfiguration):
            return False
        return self.response_config_uuid == other.response_config_uuid

    #generate hash only with response_config_uuid
    def __hash__(self):
        return hash(self.response_config_uuid)
