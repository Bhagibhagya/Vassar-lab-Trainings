import uuid
from typing import List, Union


from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException, CustomException,InvalidCollectionException
from django.conf import settings

from EmailApp.constant.constants import PREFIX_FOR_EMAIL_CHROMA_COLLECTION_NAME, ChromadbMetaDataParams, \
    CsrChromaDbFields, CategeriesForPersonalization
from EmailApp.constant.error_messages import ErrorMessages
from Platform.constant.error_messages import ErrorMessages as Platform_ErrorMessages
from EmailApp.utils import validate_input, get_current_timestamp, \
    remove_intent_and_sub_intents_from_metadata, get_metadata_for_creation, get_sub_intent_keys_from_metadata
from EmailApp.dao.impl.customer_application_mapping_dao_impl import CustomerApplicationMappingDaoImpl
from Platform.constant.error_messages import ErrorMessages as Platform_ErrorMessages


__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from chromadb.errors import InvalidCollectionException as InvalidChromaCollectionException

import chromadb
from chromadb.config import Settings
from uuid import uuid4
from AIServices.LLM.llm import embeddings

from ChatBot.constant.constants import EntityConstants

import json
import logging
logger = logging.getLogger(__name__)

class ChromaVectorStore:
    def __init__(self):
        self.client = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT,
                                          settings=Settings(anonymized_telemetry=False), database=settings.CHROMADB_NAME)
        self.customer_app_mapping_dao=CustomerApplicationMappingDaoImpl()

    def delete_docs_from_collection(self, collection_name, source_file):

        collection = self.client.get_or_create_collection(name=collection_name)
        ids = collection.get()['ids']
        metadatas = collection.get()['metadatas']

        delete_indices = []
        for i in range(len(metadatas)):
            meta = metadatas[i]
            if meta['source'] == source_file:
                delete_indices.append(i)

        delete_ids = []
        for index in delete_indices:
            delete_ids.append(ids[index])

        if len(delete_ids) > 0:
            collection.delete(delete_ids)

    def update_entity_name_by_entity_uuid(self, collection_name, entity_uuid, new_entity_name):
        collection = self.client.get_or_create_collection(collection_name)
        data = collection.get(include=['metadatas'], where={'entity_uuid': str(entity_uuid)})
        ids = data['ids']
        metadatas = data['metadatas']

        for i in range(len(ids)):
            metadatas[i]['entity']['entity_name'] = new_entity_name

        if len(ids) != 0:
            collection.update(ids=ids, metadatas=metadatas)

    def update_entity_to_default(self, collection_name, entity_uuid, default_entity_uuid):
        collection = self.client.get_collection(collection_name)
        data = collection.get(include=['metadatas'], where={'entity_uuid': entity_uuid})
        ids = data['ids']
        metadatas = data['metadatas']


        for i in range(len(ids)):
            metadatas[i]['entity_uuid'] = default_entity_uuid
            metadatas[i]['entity_name'] = EntityConstants.DEFAULT_ENTITY_NAME
            metadatas[i][EntityConstants.DEFAULT_ATTRIBUTE_NAME] = EntityConstants.DEFAULT_ATTRIBUTE_VALUE


        if len(ids) != 0:
            collection.update(ids=ids, metadatas=metadatas)

    def update_entity_of_knowledge_source(self, collection_name, knowledge_source_uuid, entity_uuid, attribute_details_json):
        try:
            collection = self.client.get_collection(collection_name)
        except Exception as e:
            # collection does not exist means no file has been reviewed yet, so no update required
            if f"ValueError('Collection {collection_name} does not exist.')" in str(e):
                logger.debug(f"Collection {collection_name} does not exist.")
                return
            raise e
        data = collection.get(include=['metadatas'], where={'knowledge_source_uuid': str(knowledge_source_uuid)})
        ids = data['ids']
        metadatas = data['metadatas']
        new_metadata = [{}] * len(ids)

        for i in range(len(ids)):
            new_metadata[i]['knowledge_source_uuid'] = metadatas[i].get('knowledge_source_uuid', '')
            new_metadata[i]['page'] = metadatas[i].get('page', '')
            new_metadata[i]['start_time'] = metadatas[i].get('start_time', '')
            new_metadata[i]['end_time'] = metadatas[i].get('end_time', '')
            new_metadata[i]['source'] = metadatas[i].get('source', '')
            new_metadata[i]['entity_uuid'] = str(entity_uuid)
            new_metadata[i]['entity_name'] = attribute_details_json['entity_name']
            new_metadata[i].update(attribute_details_json['attributes'])

        if ids:
            collection.update(ids=ids, metadatas=new_metadata)

    def remove_metadata(self, file_name, collection_name, assigned_attribute_vals):

        collection = self.client.get_collection(collection_name)
        data = collection.get(include=['metadatas'])

        ids = data['ids']
        metadatas = data['metadatas']

        select_ids = []
        select_metas = []

        for i in range(len(ids)):

            meta = metadatas[i]

            if meta['source'] == file_name:
                for attr_val in assigned_attribute_vals:
                    if meta.get(attr_val):
                        meta.pop(attr_val)

                select_ids.append(ids[i])
                select_metas.append(meta)

        if len(select_ids) > 0:
            collection.update(ids=select_ids, metadatas=select_metas)

    def add_metadata(self, file_name, collection_name, assigned_attribute_vals):

        collection = self.client.get_collection(collection_name)
        data = collection.get(include=['metadatas'])

        ids = data['ids']
        metadatas = data['metadatas']

        select_ids = []
        select_metas = []

        for i in range(len(ids)):

            meta = metadatas[i]

            if meta['source'] == file_name:
                for attr_val in assigned_attribute_vals:
                    meta[attr_val] = assigned_attribute_vals[attr_val]

                select_ids.append(ids[i])
                select_metas.append(meta)

        if len(select_ids) > 0:
            collection.update(ids=select_ids, metadatas=select_metas)

    # cache updates
    def put_in_cache(self, question_uuid, answer_uuid, query, collection_name, deleted):
        collection = self.client.get_or_create_collection(name=collection_name)
        query_embedding = embeddings.embed_query(query)

        collection.add(
            embeddings=[query_embedding],
            documents=[query],
            metadatas=[{"deleted": deleted, 'answer_uuid': str(answer_uuid)}],
            ids=[str(question_uuid)]
        )

    def update_deleted_metadata_in_cache(self, question_uuids, answer_uuid, collection_name, deleted):
        collection = self.client.get_collection(name=collection_name)
        collection.update(
            ids=question_uuids,
            metadatas=[{"deleted": deleted, 'answer_uuid': str(answer_uuid)}] * len(question_uuids)
        )

    def updating_deleted_metadata_in_cache(self, question_uuids, answer_uuids, collection_name, deleted):
        # Check if question_uuids or answer_uuids are empty
        if not question_uuids or not answer_uuids:
            logger.info("No UUIDs provided for update in cache. Skipping update.")
            return
        collection = self.client.get_collection(name=collection_name)
        metadata = [{"deleted": deleted, "answer_uuid": str(answer_uuid)} for answer_uuid in answer_uuids]
        collection.update(
            ids=question_uuids,
            metadatas=metadata
        )    

    def mark_deleted_in_cache(self, question_id, collection_name):
        collection = self.client.get_collection(name=collection_name)
        collection.update(
            ids=[str(question_id)],
            metadatas=[{"deleted": True}]
        )

    def unmark_deleted_in_cache(self, question_id, collection_name):
        collection = self.client.get_collection(name=collection_name)
        collection.update(
            ids=[str(question_id)],
            metadatas=[{"deleted": False}]
        )

    def delete_from_cache(self, answer_uuid, collection_name):
        collection = self.client.get_collection(name=collection_name)
        collection.delete(
            where={'answer_uuid': str(answer_uuid)}
        )
        
    def delete_cache_by_answer_uuids(self, cache_collection_name: str, answer_uuids: list[str]) -> None:
        
        if len(answer_uuids) > 0:
            collection = self.client.get_collection(cache_collection_name)
            collection.delete(where={
                'answer_uuid' : {
                    '$in' : answer_uuids
                }
            })


    def add_emails_and_metadata(self,metadata,emails,collection_name):
        if not validate_input(emails):
            return

        collection = self.client.get_or_create_collection(name=collection_name)
        emails = json.dumps(emails)
        if self.duplicate_check(metadata,emails,collection_name):
            logger.error(f"Duplicate record found :: {emails} .Cannot add the same record again.")
            return

        question_id = str(uuid4())
        email_embedding = embeddings.embed_query(emails) #todo embeddings.embed_documents() for batch processing

        collection.add(
            embeddings=[email_embedding],
            documents=[emails],
            metadatas=[metadata],
            ids=[question_id]
        )
        return question_id

    def duplicate_check(self,metadata,email,collection_name):
        logger.debug("Inside chroma_vector_store :: duplicate_check")
        search_criteria = metadata.copy()
        search_criteria.pop(ChromadbMetaDataParams.CREATED_TIMESTAMP.value, None)
        search_criteria.pop(ChromadbMetaDataParams.UPDATED_TIME_STAMP.value, None)
        search_criteria = [{key: value} for key, value in search_criteria.items()]
        logger.debug(f"metadata {search_criteria}")
        # Check if email already exists
        existing_emails = ChromaVectorStore().get_records_by_metadata(
            metadata_combination=search_criteria,collection_name=collection_name)  # Get all documents
        for doc in existing_emails['documents']:
            if doc == email:
                return True
        return False

    def get_records_by_metadata(self, metadata_combination, collection_name):
        logger.debug("Inside chroma_vector_store :: get_records_by_metadata")
        try:
            collection = self.client.get_collection(name=collection_name)
        except InvalidChromaCollectionException as e :
            raise InvalidCollectionException(e)
        except ValueError as e:
            raise InvalidCollectionException(e)

        # Convert metadata_combination to a list of conditions for $and
        where_conditions=metadata_combination
        if(len(metadata_combination)>1):
            where_conditions = {"$and": metadata_combination}
        elif(len(metadata_combination)==1):
            where_conditions=metadata_combination[0]
        result = collection.get(
            include=["metadatas", "documents"],
            where=where_conditions
        )

        return result

    def get_records_by_metadata_include_embeddings(self, metadata_combination, collection_name):
        logger.debug("Inside chroma_vector_store :: get_records_by_metadata")
        try:
            collection = self.client.get_collection(name=collection_name)
        except InvalidChromaCollectionException as e :
            raise InvalidCollectionException(e)
        except ValueError as e:
            raise InvalidCollectionException(e)

        # Convert metadata_combination to a list of conditions for $and
        where_conditions=metadata_combination
        if(len(metadata_combination)>1):
            where_conditions = {"$and": metadata_combination}
        elif(len(metadata_combination)==1):
            where_conditions=metadata_combination[0]
        result = collection.get(
            include=["metadatas", "documents","embeddings"],
            where=where_conditions
        )

        return result

    def get_records_by_metadata_with_specific_fields(self, mandatory_fields, optional_fields=None, collection_name=None):
        """
        Retrieve records from Chroma based on mandatory and optional metadata conditions.

        :param mandatory_fields: List of mandatory metadata conditions
        :param optional_fields: List of optional metadata conditions
        :param collection_name: Name of the Chroma collection to query
        :return: Retrieved records matching the metadata criteria
        """
        logger.debug("Inside chroma_vector_store :: get_records_by_metadata")

        try:
            # Validate collection name
            if not collection_name:
                raise ValueError("Collection name must be provided")

            collection = self.client.get_collection(name=collection_name)
        except InvalidChromaCollectionException as e:
            raise InvalidCollectionException(e)
        except ValueError as e:
            raise InvalidCollectionException(e)

        # Construct where conditions
        where_conditions = []

        # Add mandatory fields
        if mandatory_fields:
            if len(mandatory_fields) > 1:
                where_conditions.append({"$and": mandatory_fields})
            else:
                where_conditions.extend(mandatory_fields)

        # Add optional fields
        if optional_fields:
            if len(optional_fields) > 1:
                where_conditions.append({"$or": optional_fields})
            else:
                where_conditions.extend(optional_fields)

        # Construct final where clause
        final_where_conditions = where_conditions[0] if len(where_conditions) == 1 else {"$and": where_conditions}

        # Execute the query
        result = collection.get(
            include=["metadatas", "documents"],
            where=final_where_conditions
        )

        return result

    def find_similar_records(self, collection_name : str, query_embeddings : list, n_results : int = 5, similarity_threshold : float = 95) -> list:
        """
        Find near-duplicate documents using Chroma's query method.

        Args:
        - collection: Chroma collection
        - query_embedding: Embedding of the document to find duplicates for
        - similarity_threshold: Minimum similarity score (default 95%)
        - n_results : no_of records to fetch (default 5)

        Returns:
        - List of near-duplicate documents with their similarity scores
        """
        try:
            # Get the collection
            collection = self.client.get_or_create_collection(name=collection_name)
            near_duplicates = []
            # Perform query
            #todo batching, timeout exception
            query_result = collection.query(
                query_embeddings=query_embeddings,
                where = {ChromadbMetaDataParams.CATEGORY.value : CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value},
                n_results=n_results,  # Adjust based on your collection size
                include=['metadatas', 'distances']
            )

            for document_ids, metadatas, distances in zip(query_result['ids'], query_result['metadatas'], query_result['distances']):

                temp = []
                #iterate over each similar record for a training phrase
                for doc_id, metadata, distance in zip(document_ids, metadatas,distances):

                    similarity_score = (1 - distance) * 100
                    #check the similarity threshold
                    if similarity_score >= similarity_threshold:
                        near_duplicate = {
                            "document_id": doc_id,
                            "metadata": metadata,
                            "distance": distance,
                            "similarity_score": similarity_score
                        }
                        temp.append(near_duplicate)
                #returns list of lists in order
                near_duplicates.append(temp)

        except Exception as e:
            logger.error(f"Exception Occurred while finding Near Duplicates :: {e}")
            raise CustomException("Exception Occurred while finding Near Duplicates")

        return near_duplicates

    def get_or_create_collection_cosine_metric(self, name : str):

        collection = self.client.create_collection(
            name= name,
            metadata={"hnsw:space": "cosine"},
            get_or_create = True
        )

        return collection
    
    @staticmethod
    def embed_query_list(queries : List[str]) -> list:
        #TODO Need R&D
        return embeddings.embed_documents(queries)

    def delete_emails_by_metadata(self, metadata, collection_name):
        
        # Get the collection
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            raise InvalidValueProvidedException("Collection does not exist")
        # Retrieve documents that match the given metadata using the 'where' filter
        matching_docs = self.get_records_by_metadata(metadata,collection_name)
        
        # Extract the IDs of the matching documents
        ids_to_delete = matching_docs['ids']
        
        if ids_to_delete:
            # Delete the matching documents by their IDs
            collection.delete(ids=ids_to_delete)
            print(f"Deleted emails with ids: {ids_to_delete}")
        else:
            print("No matching emails found with the given metadata.")
        
        return ids_to_delete

    def delete_record_by_id(self,id_,collection_name):
        """
        :param id_:
        :param collection_name:
        :return: None if deleted successfully else raises corresponding exception
        """
        logger.info("Inside chroma_vector_store :: delete_email_by_id")
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            raise InvalidValueProvidedException("Collection does not exist")
        try:
            collection.delete(ids=id_)
        except Exception as e:
            logger.error(f'Error in deleting Utterance :: {e}')
            raise CustomException(ErrorMessages.ERROR_IN_DELETING_UTTERANCE)
        #checking if successfully deleted or not
        if collection.get(ids=id_)['ids']:
            raise CustomException("Error in deletion in chroma")
        logger.debug(f'{id_} deleted successfully')

    def update_email_document_embedding(self,email,id_,collection_name,metadata):
        logger.info("Inside chroma_vector_store :: update_email_document_embedding")

        collection = self.client.get_or_create_collection(name=collection_name)
        #email=json.dumps(email) #Converting to json since json format is more suitable for embeddings
        email_embedding = embeddings.embed_query(email)
        
        collection.update(
            ids=[id_],
            embeddings=[email_embedding],
            documents=[email],
            metadatas=[metadata]
        )

    def delete_collection(self, collection_name):

        # Now delete the collection
        self.client.delete_collection(name=collection_name)

        print(f"Collection '{collection_name}' deleted successfully!")

        
    def get_chroma_collection_name_by_customer_application(self,customer_uuid, application_uuid):
        '''
        Method to get the collection name of chroma vector for a given customer and application
        '''
        logger.info("In ChromaVectorStore :: get_chroma_collection_name_by_customer_application")
        #Get the customer application mapping Id
        cust_app_map_id = self.customer_app_mapping_dao.get_cust_app_mapping_uuid(customer_uuid=customer_uuid,application_uuid=application_uuid)
        if cust_app_map_id is None:
            logger.error(f"customer application mapping not found for customer_uuid{customer_uuid} and application_uuid {application_uuid}")
            raise InvalidValueProvidedException(detail=f"customer application mapping not found for customer_uuid{customer_uuid} and application_uuid {application_uuid}")
        #Collection name will be Prefix + cust_app_map_id
        custom_chroma_collection_name = PREFIX_FOR_EMAIL_CHROMA_COLLECTION_NAME+str(cust_app_map_id)
        logger.debug(f"collection name is {custom_chroma_collection_name}")
        return custom_chroma_collection_name

    def insert_test_knowledge_chunks(self, chunks, collection_name):
        collection = self.client.get_or_create_collection(name=collection_name)

        chunk_documents = [chunk['document'] for chunk in chunks]
        chunk_embeddings = embeddings.embed_documents(chunk_documents)

        collection.add(
            embeddings=chunk_embeddings,
            documents=chunk_documents,
            metadatas=[chunk['metadata'] for chunk in chunks],
            ids=[str(uuid4()) for _ in range(len(chunks))]
        )

    def update_the_metadatas_with_document_ids(self, new_metadatas : List[dict], doc_ids : List[str], collection_name : str) -> int:
        """
        Update the metadata of a specific document in a given collection.

        Parameters:
            new_metadata (dict): A dictionary containing the new metadata to associate with the document.
            doc_id (str): The unique identifier of the document to update.
            collection_name (str): The name of the collection where the document resides.
        """
        collection = self.client.get_or_create_collection(name = collection_name)
        collection.update(
                          ids = doc_ids ,
                          metadatas=  new_metadatas
                          )
        logger.info(f"Metadata successfully updated for {len(doc_ids)} documents")

        return len(doc_ids)

    def update_training_phrases(self,ids, documents,embeddings,metadatas, collection_name):
        """
        Updates specific fields in the metadata for documents matching the old metadata in the collection.

        :param metadata_to_get: A list of dictionaries representing the old metadata to search for.
        :param new_metadata: A dictionary containing only the fields to update (e.g., updated_timestamp).
        :param collection_name: The name of the collection where the documents exist.

        """
        try:

            collection = self.client.get_collection(name=collection_name)

            collection.delete(ids=ids)
            new_ids = [str(uuid.uuid4()) for _ in range(len(ids))]
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=new_ids
            )

            logger.info(f"Successfully updated specified metadata fields for {len(ids)} document(s).")
            
        except Exception as e:
            logger.error(f"Error updating metadata for documents :: {str(e)}")
            raise CustomException("Cannot update Training phrases")


    def get_record_by_id(self,collection_name,id):
        logger.info("In ChromaVectorStore :: get_record_by_id")
        collection = self.client.get_or_create_collection(name=collection_name)
        return collection.get(
            include=["metadatas", "documents","embeddings"],
            ids=[id]
        )

    def update_metadata_by_id(self, id_,metadata,document, embedding, collection_name):
        logger.info("Inside chroma_vector_store :: update_metadata_by_id")

        collection = self.client.get_or_create_collection(name=collection_name)
        collection.delete(ids=[id_])
        collection.add(
            ids=[str(uuid.uuid4())],
            metadatas=[metadata],
            documents=[document],
            embeddings=[embedding]
        )

    def update_metadata_and_record_by_id(self, id_, metadata, document, collection_name):
        logger.info("Inside chroma_vector_store :: update_metadata_by_id")

        collection = self.client.get_or_create_collection(name=collection_name)
        collection.delete(ids=[id_])
        self.add_emails_and_metadata(metadata=metadata,emails=document,collection_name=collection_name)

    def delete_record_by_ids(self,ids,collection_name):
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            collection.delete(ids=ids)
        except Exception as e:
            logger.error(f"Error occurred while deleting training phrases :: {e}")
            raise

    @staticmethod
    def embed_query_list(queries: List[str]) -> list:
        # TODO Need R&D
        return embeddings.embed_documents(queries)

    def find_similar_records(self, collection_name : str, query_embeddings : list, n_results : int = 5, similarity_threshold : float = 95) -> list:
        """
        Find near-duplicate documents using Chroma's query method.

        Args:
        - collection: Chroma collection
        - query_embedding: Embedding of the document to find duplicates for
        - similarity_threshold: Minimum similarity score (default 95%)
        - n_results : no_of records to fetch (default 5)

        Returns:
        - List of near-duplicate documents with their similarity scores
        """
        try:
            # Get the collection
            collection = self.client.get_or_create_collection(name=collection_name)
            near_duplicates = []
            # Perform query
            #todo batching, timeout exception
            query_result = collection.query(
                query_embeddings=query_embeddings,
                where = {ChromadbMetaDataParams.CATEGORY.value : CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value},
                n_results=n_results,  # Adjust based on your collection size
                include=['metadatas', 'distances']
            )

            for document_ids, metadatas, distances in zip(query_result['ids'], query_result['metadatas'], query_result['distances']):

                temp = []
                #iterate over each similar record for a training phrase
                for doc_id, metadata, distance in zip(document_ids, metadatas,distances):

                    similarity_score = (1 - distance) * 100
                    #check the similarity threshold
                    if similarity_score >= similarity_threshold:
                        near_duplicate = {
                            "document_id": doc_id,
                            "metadata": metadata,
                            "distance": distance,
                            "similarity_score": similarity_score
                        }
                        temp.append(near_duplicate)
                #returns list of lists in order
                near_duplicates.append(temp)

        except Exception as e:
            logger.error(f"Exception Occurred while finding Near Duplicates :: {e}")
            raise CustomException("Exception Occurred while finding Near Duplicates")

        return near_duplicates

    def update_the_metadata_with_document_id(self, new_metadata : dict, doc_id : str, collection_name : str ):
        """
        Update the metadata of a specific document in a given collection.

        Parameters:
            new_metadata (dict): A dictionary containing the new metadata to associate with the document.
            doc_id (str): The unique identifier of the document to update.
            collection_name (str): The name of the collection where the document resides.
        """
        collection = self.client.get_or_create_collection(name = collection_name)
        collection.update(
                          ids = [doc_id],
                          metadatas=  new_metadata
                          )
        logger.info(f"Metadata successfully updated for document ID : {doc_id}")

    def upload_utterances_at_once(self, ids_list : list, vector_embeddings_list : list, metadata_list : List[dict], training_phrases_list : list, collection_name : str):

        """
            Uploads utterances (IDs, vector embeddings, metadata, and training phrases) to a specified collection.

            Args:
                ids_list (list): A list of unique IDs for the utterances.
                vector_embeddings_list (list): A list of vector embeddings corresponding to the utterances.
                metadata_list (list): A list of metadata dictionaries for each utterance.
                training_phrases_list (list): A list of training phrases (documents).
                collection_name (str): The name of the collection to which the data should be uploaded.

            Raises:
                CustomException: If the lengths of the provided lists (IDs, embeddings, metadata, and training phrases) are not equal.

            Returns:
                row_count: returns the no of rows inserted.

            Example:
                upload_utterances_at_once(
                    ids_list=["id1", "id2"],
                    vector_embeddings_list=[[0.1, 0.2], [0.3, 0.4]],
                    metadata_list=[{"key": "value1"}, {"key": "value2"}],
                    training_phrases_list=["phrase1", "phrase2"],
                    collection_name="example_collection"
                )
            """

        if len(ids_list) == 0:
            logger.error(Platform_ErrorMessages.IDS_LIST_SHOULD_NOT_BE_EMPTY)
            raise CustomException(Platform_ErrorMessages.IDS_LIST_SHOULD_NOT_BE_EMPTY)

        if not (len(ids_list) == len(vector_embeddings_list) == len(metadata_list) == len( training_phrases_list)):
            logger.error(Platform_ErrorMessages.LIST_LENGTHS_MISMATCH)
            raise CustomException(Platform_ErrorMessages.LIST_LENGTHS_MISMATCH)

        logger.info("Starting upload to collection '%s'", collection_name)

        collection = self.client.get_or_create_collection(name=collection_name)
        try:
            collection.add(
                embeddings = vector_embeddings_list,
                documents = training_phrases_list,
                metadatas = metadata_list,
                ids = ids_list
            )

            logger.info(f"A total of {len(ids_list)}, Training Phrases has been uploaded successfully")

        except Exception as e:
            logger.error(f"Exception occurred : {e}")
            raise CustomException(Platform_ErrorMessages.FAILED_TO_ADD_INTO_COLLECTION)

        return len(ids_list)

    def upsert_utterances_at_once(self, collection_name, ids : List[str], documents : List[Union[str, None]] = None,

                                  metadatas : List[Union[dict, None]] = None, embeddings : list = None):
        if len(ids) == 0:
            logger.error(Platform_ErrorMessages.IDS_LIST_SHOULD_NOT_BE_EMPTY)
            raise CustomException(Platform_ErrorMessages.IDS_LIST_SHOULD_NOT_BE_EMPTY)

        if not (len(ids) == len(embeddings) == len(metadatas) == len(documents )):
            logger.error(Platform_ErrorMessages.LIST_LENGTHS_MISMATCH)
            raise CustomException(Platform_ErrorMessages.LIST_LENGTHS_MISMATCH)

        collection = self.client.get_or_create_collection(collection_name)
        try:
            collection.upsert(
                ids= ids,
                documents= documents,
                metadatas= metadatas,
                embeddings= embeddings
            )
        except Exception as e:
            logger.error(f"Exception occurred : {e}")
            raise CustomException(Platform_ErrorMessages.FAILURE_IN_UPDATING_UTTERANCES)

        return len(ids)






    def upload_utterances_at_once(self, ids_list : list, vector_embeddings_list : list, metadata_list : List[dict], training_phrases_list : list, collection_name : str):

        """
            Uploads utterances (IDs, vector embeddings, metadata, and training phrases) to a specified collection.

            Args:
                ids_list (list): A list of unique IDs for the utterances.
                vector_embeddings_list (list): A list of vector embeddings corresponding to the utterances.
                metadata_list (list): A list of metadata dictionaries for each utterance.
                training_phrases_list (list): A list of training phrases (documents).
                collection_name (str): The name of the collection to which the data should be uploaded.

            Raises:
                CustomException: If the lengths of the provided lists (IDs, embeddings, metadata, and training phrases) are not equal.

            Returns:
                row_count: returns the no of rows inserted.

            Example:
                upload_utterances_at_once(
                    ids_list=["id1", "id2"],
                    vector_embeddings_list=[[0.1, 0.2], [0.3, 0.4]],
                    metadata_list=[{"key": "value1"}, {"key": "value2"}],
                    training_phrases_list=["phrase1", "phrase2"],
                    collection_name="example_collection"
                )
            """

        if len(ids_list) == 0:
            logger.error(Platform_ErrorMessages.IDS_LIST_SHOULD_NOT_BE_EMPTY)
            raise CustomException(Platform_ErrorMessages.IDS_LIST_SHOULD_NOT_BE_EMPTY)

        if not (len(ids_list) == len(vector_embeddings_list) == len(metadata_list) == len( training_phrases_list)):
            logger.error(Platform_ErrorMessages.LIST_LENGTHS_MISMATCH)
            raise CustomException(Platform_ErrorMessages.LIST_LENGTHS_MISMATCH)

        logger.info("Starting upload to collection '%s'", collection_name)

        collection = self.client.get_or_create_collection(name=collection_name)
        try:
            collection.add(
                embeddings = vector_embeddings_list,
                documents = training_phrases_list,
                metadatas = metadata_list,
                ids = ids_list
            )

            logger.info(f"A total of {len(ids_list)}, Training Phrases has been uploaded successfully")

        except Exception as e:
            logger.error(f"Exception occurred : {e}")
            raise CustomException(Platform_ErrorMessages.FAILED_TO_ADD_INTO_COLLECTION)

        return len(ids_list)



chroma_obj = ChromaVectorStore()



