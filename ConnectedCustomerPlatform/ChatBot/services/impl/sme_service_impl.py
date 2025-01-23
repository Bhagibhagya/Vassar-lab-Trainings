import logging


from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.dao.impl.knowledge_sources_dao_impl import KnowledgeSourcesDaoImpl
from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException, \
    UnauthorizedByScopeException
from AIServices.VectorStore.chromavectorstore import chroma_obj
from django.conf import settings
from ChatBot.services.interface.sme_service_interface import ISMEService
from ChatBot.dataclasses.sme_data import Question, Answer, Draft

from ChatBot.dao.impl.sme_dao_impl import SMEDaoImpl
from ChatBot.dao.impl.user_activity_dao_impl import UserActivityDaoImpl
from ChatBot.dao.impl.customer_application_mapping_dao_impl import CustomerApplicationMappingDaoImpl
from ChatBot.dao.interface.customer_application_mapping_dao_interface import ICustomerApplicationMappingDao

from ChatBot.constant.constants import Constants
from ChatBot.constant.error_messages import ErrorMessages
from uuid import uuid4
from rest_framework import status
from typing import Union

from ce_shared_services.factory.vectordb.vectordb_factory import VectorDBFactory
from ce_shared_services.factory.embedding.embedding_factory import EmbeddingModelFactory

from ce_shared_services.vectordb.interface.vectordb import VectorDB
from ce_shared_services.embedding.interface.embedding import EmbeddingModel

from ce_shared_services.datatypes import Chunk

from django.db import transaction, IntegrityError

from EventHub.send_sync import EventHubProducerSync

from ChatBot.utils import get_collection_names, convert_html_to_markdown, convert_signed_url_to_blob_name_in_attachments
from Platform.utils import paginate_queryset

import re

logger = logging.getLogger(__name__)


class SMEServiceImpl(ISMEService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Implementing Singleton pattern to ensure only one instance of the service exists.
        if cls._instance is None:
            cls._instance = super(SMEServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        # Initializing dependencies and setting up the service.
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            
            self.__sme_dao = SMEDaoImpl()
            self.__knowledge_source_dao = KnowledgeSourcesDaoImpl()
            self.__user_activity_dao = UserActivityDaoImpl()
            
            self._cam_dao: ICustomerApplicationMappingDao = CustomerApplicationMappingDaoImpl()
            
            self.__event_producer = EventHubProducerSync(settings.LLM_AGENT_EVENT_TOPIC)
            
            self._embedder: EmbeddingModel = EmbeddingModelFactory.instantiate(settings.EMBEDDING_CLASS_NAME, settings.EMBEDDING_CONFIG)
            
            vectordb_config = {
                'embedding_model' : self._embedder,
                'host' : settings.CHROMADB_HOST,
                'port' : settings.CHROMADB_PORT,
                'database' : settings.CHROMADB_NAME
            }
            self._vectordb: VectorDB = VectorDBFactory.instantiate(settings.VECTORDB_CLASS_NAME, vectordb_config)
            
            self.initialized = True
            logger.info("SMEServiceImpl initialized.")

    def get_questions(self, filter, customer_uuid, application_uuid, entity_uuids_list):
        """Retrieve questions based on filters such as feedback and pagination."""
        question_type = filter.get('question_type')
        if not question_type:
            question_type='all'

        logger.debug(f"Fetching questions with for customer_uuid: {customer_uuid}, application : {application_uuid}, question_type:, {question_type}, entity_uuids:, {entity_uuids_list}")

        questions_queryset = self.__sme_dao.get_questions(customer_uuid, application_uuid, filter, entity_uuids_list)

        page, paginator = paginate_queryset(questions_queryset, filter)

        response = {
            'total_entries': paginator.count,
            'data': page.object_list
        }

        logger.debug("Questions retrieved: %d", paginator.count)
        return response

    def get_question_details(self, question_uuid, entity_uuids_list):
        """Fetch a question and its associated answer details by question UUID."""
        logger.debug("Fetching question details for question_uuid: %s", question_uuid)
        question_details = self.__sme_dao.get_question_details(question_uuid=question_uuid, entity_uuids_list=entity_uuids_list)

        if question_details is None:
            logger.error("Question not found for question_uuid: %s", question_uuid)
            raise CustomException(ErrorMessages.QUESTION_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)

        logger.debug("Question details retrieved for question_uuid: %s", question_uuid)
        return question_details

    @transaction.atomic
    def add_question(self, data, customer_uuid, application_uuid, user_uuid):
        
        """Add a new question and its answer, then store it in cache."""
        logger.debug(f"Adding new question for customer_uuid: {customer_uuid}, application: {application_uuid}")
        answer_uuid = uuid4()
        author_role_uuid = data.get('author_role_uuid')
        attachments = data.get('attachments')
        is_draft = data.get('is_draft')
        attachments = convert_signed_url_to_blob_name_in_attachments(attachments)
        answer_text = convert_html_to_markdown(data.get('answer'))

        # Prepare answer and question objects
        answer_details = Answer(
            answer_uuid=answer_uuid,
            answer_text=answer_text,
            attachment_details_json=attachments,
            entity_details_json=data.get('entity_uuids'),
            is_system_generated=False,
            in_cache=not is_draft,
            author_user_uuid=user_uuid,
            author_role_uuid=author_role_uuid,
            application_uuid=application_uuid,
            customer_uuid=customer_uuid
        )

        question_uuid = uuid4()
        question_details = Question(
            question_uuid=question_uuid,
            question_text=data.get('question'),
            answer_uuid=answer_uuid,
            is_system_generated=False,
            author_user_uuid=user_uuid,
            author_role_uuid=author_role_uuid,
            application_uuid=application_uuid,
            customer_uuid=customer_uuid
        )

        # Persisting the question and answer
        self.__sme_dao.create_answer(answer_details, user_uuid)
        self.__sme_dao.create_question(question_details, user_uuid)

        logger.debug(f"Question, answer created and saved successfully for answer UUID: {answer_uuid}.")


        if is_draft:
            # Create draft object
            draft = Draft(draft_uuid=uuid4(),
                          answer_uuid=answer_uuid,
                          draft_content=answer_text,
                          attachment_details_json=attachments,
                          application_uuid=application_uuid,
                          customer_uuid=customer_uuid,
                          author_user_uuid=user_uuid,
                          author_role_uuid=author_role_uuid)

            self.__sme_dao.save_draft(draft, user_uuid)

            logger.debug(f"draft created and saved successfully for answer UUID: {answer_uuid}.")


        # Cache the new question
        _, cache_collection_name = get_collection_names(customer_uuid, application_uuid)

        # if question is added as draft , is deleted is set to true in chroma cache
        chroma_obj.put_in_cache(question_uuid, answer_uuid, data.get('question'), cache_collection_name, deleted = is_draft)

        logger.debug("Question added successfully with question_uuid: %s", question_uuid)
        if is_draft:
            return SuccessMessages.DRAFT_ADD_SUCCESS
        return SuccessMessages.QUESTION_ADDED_SUCCESS

    @transaction.atomic
    def delete_answer(self, answer_uuid, customer_uuid, application_uuid, entity_uuids_list):
        """
        Deletes an answer along with its associated questions from the database and the Chroma vector store cache.
        """
        logger.debug(
            f"Deleting answer with UUID: {answer_uuid} for customer: {customer_uuid}, application: {application_uuid}.")

        # Get the cache collection name
        _, cache_collection_name = get_collection_names(customer_uuid, application_uuid)

        # Remove the questions from the cache
        chroma_obj.delete_from_cache(answer_uuid, cache_collection_name)

        # Delete the answer from the database
        rows_deleted = self.__sme_dao.delete_answer_by_answer_uuid(answer_uuid, entity_uuids_list)

        if rows_deleted == 0:
            raise ResourceNotFoundException(ErrorMessages.ANSWER_NOT_FOUND)

        logger.debug("Answer and associated questions deleted successfully from the cache and database.")

    @transaction.atomic
    def update_answer(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Updates an existing answer, including its content and attachments.
        """
        logger.debug(f"Updating answer UUID: {data.get('answer_uuid')} by user: {user_uuid}.")
        # Retrieve and process data
        answer_uuid = data.get('answer_uuid')
        attachments = convert_signed_url_to_blob_name_in_attachments(data.get('attachments'))
        answer = convert_html_to_markdown(data.get('answer'))
        entity_details = data.get('entity_uuids')
        source = data.get("source")

        is_draft = data.get("is_draft")
        draft_uuid = data.get('draft_uuid')
        # Fetch the author's role UUID
        author_role_uuid = data.get('author_role_uuid')

        if is_draft:
            if draft_uuid is None:
                draft_uuid = uuid4()
            # Create draft object
            draft = Draft(answer_uuid=answer_uuid,
                          draft_uuid=draft_uuid,
                          draft_content=answer,
                          attachment_details_json=attachments,
                          customer_uuid=customer_uuid,
                          application_uuid=application_uuid,
                          author_user_uuid=user_uuid,
                          author_role_uuid=author_role_uuid)

            # Save the draft to the database
            try:
                self.__sme_dao.save_draft(draft, user_uuid)
            except IntegrityError as e:
                error_message = str(e)
                if "duplicate key value violates unique constraint" in error_message and f"({answer_uuid}) already exists" in error_message:
                    logger.debug(f"Draft for answer already exists {answer_uuid} already exists : {e}")
                    raise CustomException(ErrorMessages.BAD_REQUEST)
                raise e

            return SuccessMessages.DRAFT_SAVE_SUCCESS

        # Create updated answer object
        answer_data = Answer(answer_uuid=answer_uuid,
                             answer_text=answer,
                             attachment_details_json=attachments,
                             author_user_uuid=user_uuid,
                             author_role_uuid=author_role_uuid,
                             application_uuid=application_uuid,
                             customer_uuid=customer_uuid,
                             is_system_generated=False,
                             entity_details_json=entity_details)

        # getting question is with given answer uuid which are not in cache
        question_uuids = self.__sme_dao.get_question_uuids_by_answer_uuid_and_cache(answer_uuid, False, entity_uuids_list)
        question_uuids = list(question_uuids)

        # Update the answer in the database
        rows_matched = self.__sme_dao.update_answer(answer_data, user_uuid)
        if rows_matched == 0:
            raise ResourceNotFoundException(ErrorMessages.ANSWER_NOT_FOUND)
        logger.debug(f"Answer UUID: {answer_uuid} updated successfully.")

        # deletes draft associated with answer if any
        self.__sme_dao.delete_draft_by_answer_uuid(answer_uuid)

        if question_uuids:
            _, cache_collection_name = get_collection_names(customer_uuid, application_uuid)

            chroma_obj.update_deleted_metadata_in_cache(question_uuids, answer_uuid, cache_collection_name, True)
            logger.debug(
                f"Question UUIDs {question_uuids} marked as deleted False in cache collection {cache_collection_name}")


        # Handle specific update based on the source
        if source == Constants.CHAT:
            logger.info(f"Answer UUID: {answer_uuid} update triggered via chat.")
            # TODO: Call update conversation service

        return SuccessMessages.ANSWER_UPDATED_SUCCESS

    @transaction.atomic
    def verify_answer(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Verifies an answer based on the provided details.
        Raises CustomException if the user has invalid permissions.
        """
        logger.debug(f"Verifying answer for customer_uuid={customer_uuid}, application_uuid={application_uuid}")

        answer_uuid = data.get('answer_uuid')
        verified = data.get('verified')
        source = data.get("source")
        conversation_uuid = data.get('conversation_uuid')
        message_id = data.get('message_id')

        verifier_role_uuid = data.get('verifier_role_uuid')

        rows_matched = self.__sme_dao.update_answer_verification_details(answer_uuid, verified, verifier_role_uuid, user_uuid, entity_uuids_list)
        if rows_matched == 0:
            raise ResourceNotFoundException(ErrorMessages.ANSWER_NOT_FOUND)

        if source == Constants.CHAT:
            # TODO: Call update conversation service when chat source is detected
            logger.debug(f"Update conversation service required for source={source}")


    @transaction.atomic
    def update_feedback(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Updates the feedback for a given answer, marking or unmarking it in cache based on dislike status.
        """
        answer_uuid = data.get('answer_uuid')
        dislike = data.get('dislike')
        feedback = data.get('feedback', "").strip()
        conversation_uuid = data.get("conversation_uuid")
        message_id = data.get("message_id")
        source = data.get("source")

        logger.debug(f"Updating feedback for answer_uuid={answer_uuid} with dislike={dislike}")

        in_cache = not dislike
        if in_cache:
            feedback = None

        question_uuids = self.__sme_dao.get_question_uuids_by_answer_uuid_and_cache(answer_uuid, in_cache, entity_uuids_list)
        question_uuids = list(question_uuids)

        rows_matched = self.__sme_dao.update_answer_feedback_and_cache(answer_uuid, feedback, in_cache, user_uuid)

        if rows_matched == 0:
            raise ResourceNotFoundException(ErrorMessages.ANSWER_NOT_FOUND)

        self._track_feedback_activity(user_uuid, customer_uuid, application_uuid, answer_uuid, feedback)

        if question_uuids:
            
            _, cache_collection_name = get_collection_names(customer_uuid, application_uuid)

            chroma_obj.update_deleted_metadata_in_cache(question_uuids, answer_uuid, cache_collection_name,
                                                        not in_cache)
            logger.debug(
                f"Question UUIDs {question_uuids} marked as deleted: {not in_cache} in cache collection {cache_collection_name}")



        logger.debug(f"Feedback updated for answer_uuid={answer_uuid}")


        if source == Constants.CHAT:
            # TODO: Call update conversation service when chat source is detected
            logger.debug(f"Update conversation service required for source={source}")

    def _track_feedback_activity(self, user_uuid, customer_uuid, application_uuid, answer_uuid, feedback):
        
        question_uuids = self.__sme_dao.get_question_uuids_by_answer_uuid(answer_uuid)
            
        self.__user_activity_dao.add_feedback_activity(
            user_id=user_uuid,
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            question_uuid=question_uuids[0],
            answer_uuid=answer_uuid,
            feedback=feedback
        )

    @transaction.atomic
    def generate_qa(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Triggers the generation of question-answer pairs based on provided knowledge sources.
        """
        knowledge_sources = data.get('knowledge_sources')
        knowledge_sources = [str(knowledge_source_id) for knowledge_source_id in knowledge_sources]

        logger.debug(f"Starting QA generation for customer_uuid={customer_uuid}, application_uuid={application_uuid}")

        rows_matched = self.__knowledge_source_dao.update_qa_generation_status(knowledge_sources, user_uuid, entity_uuids_list)
        if rows_matched == 0:
            logger.debug(f"QA generation Failed because user is not in scope of entities list {entity_uuids_list} for all knowledge_sources={knowledge_sources}")
            raise UnauthorizedByScopeException(ErrorMessages.BEYOND_SCOPE)
        if rows_matched != len(knowledge_sources):
            logger.debug(f"QA generation already in progress or completed for some or all knowledge_sources={knowledge_sources}")
            raise CustomException(ErrorMessages.CANNOT_GENERATE_QA, status_code=status.HTTP_403_FORBIDDEN)

        #update qa done alteast once status for the knowledge sources
        for ks in knowledge_sources:
            
            meta = self.__knowledge_source_dao.get_metadata(ks)
            meta.update({'qa_reached' : True})

            self.__knowledge_source_dao.update_metadata(ks, meta)

        logger.debug(f"QA generation status updated for knowledge_sources={knowledge_sources}")

        chunk_collection, cache_collection = get_collection_names(customer_uuid, application_uuid)
        event = {
            'request_name': 'qa_generation',
            'knowledge_sources': knowledge_sources,
            'chunk_collection': chunk_collection,
            'cache_collection': cache_collection,
            'user_uuid': str(user_uuid),
            'author_role_uuid': str(data.get('author_role_uuid'))
        }
        self.__event_producer.send_event_data_batch(event)
        logger.debug(f"QA generation event sent for customer_uuid={customer_uuid}, application_uuid={application_uuid}, knowledge sources: {knowledge_sources}")

    def __update_questions_metadata(self, answer_uuid, customer_uuid, application_uuid, in_cache):
        """
        Unmarks questions in cache by their UUIDs.
        """
        logger.debug(f"Unmarking questions in cache for answer_uuid={answer_uuid}")
        question_uuids = self.__sme_dao.get_question_uuids_by_answer_uuid_and_cache(answer_uuid, in_cache,[])
        question_uuids = list(question_uuids)

        if len(question_uuids):
            _, cache_collection_name = get_collection_names(customer_uuid, application_uuid)

            chroma_obj.update_deleted_metadata_in_cache(question_uuids, answer_uuid, cache_collection_name, not in_cache)
            logger.debug(f"Question UUIDs {question_uuids} marked as deleted: {not in_cache} in cache collection {cache_collection_name}")

    # Function to get the entity ids form user scope from request
    def get_entity_ids_from_request(self, request):
        """
        Get the entity IDs from the user role scope of scope name ENTITY.
        Returns an empty list if no ENTITY scope is found.
        """
        logger.debug("Getting the entity IDs from the user role scope of scopeName ENTITY.")

        scope = getattr(request, 'scope', [])
        entity_scope = next((item for item in scope if item['scopeName'] == 'ENTITY'), None)

        if entity_scope:
            logger.debug(f"Found entity scope with value: {entity_scope['scopeValue']}")
            return entity_scope['scopeValue']

        logger.debug("No ENTITY scope found.")
        return []

    def _get_where_clause(self, entity_filter: Union[dict, None]) -> Union[dict, None]:
        
        """
        Constructs a where clause for filtering entities based on the provided entity filter.

        Args:
            entity_filter (Union[dict, None]): A dictionary representing the filter criteria for entities.

        Returns:
            Union[dict, None]: A dictionary representing the where clause, or None if no filter is provided.
        """
        
        logger.debug("In SMEServiceImpl class :: _get_where_clause method")

        logger.info(f'entity filter in request :: {entity_filter}')
        
        if entity_filter is None:
            return None
            
        if len(entity_filter) == 0:
            return None

        elif len(entity_filter) == 1:
            name = list(entity_filter.keys())[0]
            ands = [{'entity_name': name}]

            for key, value in entity_filter[name].items():
                ands.append({key: value})

            if len(ands) == 1:
                return ands[0]
            
            return {
                "$and": ands
            }

        else:
            ors = []
            for key, value in entity_filter.items():
                ors.append(self._get_where_clause({key: value}))

            if len(ors) == 1:
                return ors[0]
            return {
                "$or": ors
            }

    def _format(self, chunks: list[dict], sort_by_sequence: bool, metadata_keys: list) -> list[dict]:
        
        """
        Format the chunks by sort_by_sequence value and including only the metadata keys provided.
        
        Args:
            chunks : list[dict] : A list of dictionaries where each dictionary represents a chunk containing metadata.
            sort_by_sequence : bool : If True, sorts the chunks based on the 'document_id' key in the metadata.
            metadata_keys : list : A list of keys to include in the metadata of each chunk. All other keys will be excluded.

        Returns:
            list[dict] : A list of formatted chunks with sorted and filtered metadata.
                
        """
        
        if sort_by_sequence:
            chunks = sorted(chunks, key=lambda x : x['metadata']['document_id'])
        
        for chunk in chunks:
            
            meta: dict = chunk['metadata']
            all_keys = list(meta.keys())
            
            exclude_keys = set(all_keys).difference(set(metadata_keys))
            for key in exclude_keys:
                meta.pop(key)
        
        return chunks

    def get_relevant_chunks(
        self,
        customer_uuid: str,
        application_uuid: str,
        query: str,
        entity_filter: Union[dict, None],
        top_n: int,
        sort_by_sequence: bool,
        metadata_keys: list
    ) -> list[dict]:
        
        """
        Retrieves relevant chunks of data based on the provided query and filter criteria.

        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.
            query (str): The query string for similarity search.
            entity_filter (Union[dict, None]): A dictionary representing the filter criteria for entities.
            top_n (int): The maximum number of relevant chunks to retrieve.
            sort_by_sequence (bool): A flag indicating whether the retrieved chunks should be sorted by their sequence order. 
            metadata_keys (list): A list of metadata keys to include in the response. This specifies which metadata fields should be extracted for each chunk.

        Returns:
            list[dict]: A list of dictionaries representing the relevant chunks.
        """
        
        logger.debug("In SMEServiceImpl class :: get_relevant_chunks method")

        cam_id = self._cam_dao.get_customer_application_mapping_id(customer_uuid, application_uuid)
        chunk_collection_name = 'cw_' + cam_id
        mvr_collection_name = 'mvr_' + cam_id

        mvr_count = self._vectordb.get_collection_count_sync(mvr_collection_name)

        if mvr_count != 0:
            logger.debug('Data found in multi vector collection')
            relevant_chunks = self._multivector_retrieval(mvr_collection_name, chunk_collection_name, query, entity_filter, top_n)

        else:
            logger.debug('No records found in multi vector collection')
            relevant_chunks = self._retrieval(chunk_collection_name, query, entity_filter, top_n)
        
        return self._format(relevant_chunks, sort_by_sequence, metadata_keys)

    def _retrieval(self, chunk_collection_name: str, query: str, entity_filter: Union[dict, None], top_n: int) -> list[dict]:
        
        """
        Performs a similarity search and retrieves relevant chunks from a single collection.

        Args:
            chunk_collection_name (str): The name of the collection containing chunk data.
            query (str): The query string for similarity search.
            entity_filter (Union[dict, None]): A dictionary representing the filter criteria for entities.
            top_n (int): The maximum number of relevant chunks to retrieve.

        Returns:
            list[dict]: A list of dictionaries representing the retrieved chunks.
        """
        
        logger.info("In SMEServiceImpl class :: _retrieval method")

        where = self._get_where_clause(entity_filter)
        logger.info(f"where :: {where}")
        
        chunks = self._vectordb.similarity_search_sync(chunk_collection_name, query, where, top_n)

        return [
            {
                'id': chunk.id,
                'document': chunk.document,
                'metadata': chunk.metadata
            }
            for chunk in chunks
        ]

    def _multivector_retrieval(self, mvr_collection_name: str, chunk_collection_name: str, query: str, entity_filter: Union[dict, None], top_n: int) -> list[dict]:
        
        """
        Performs a multi-vector similarity search and retrieves relevant chunks.

        Args:
            mvr_collection_name (str): The name of the multi-vector collection.
            chunk_collection_name (str): The name of the collection containing chunk data.
            query (str): The query string for similarity search.
            entity_filter (Union[dict, None]): A dictionary representing the filter criteria for entities.
            top_n (int): The maximum number of relevant chunks to retrieve.

        Returns:
            list[dict]: A list of dictionaries representing the retrieved chunks.
        """
        
        logger.info("In SMEServiceImpl class :: _multivector_retrieval method")

        where = self._get_where_clause(entity_filter)
        logger.info(f"where :: {where}")
        
        child_chunks = self._vectordb.similarity_search_sync(mvr_collection_name, query, where, top_n * 4)
        logger.info([ch.metadata['document_id'] for ch in child_chunks])
        logger.info(f'No. of child chunks fetched :: {len(child_chunks)}')
        
        parent_ids = []
        
        for child_chunk in child_chunks:
            
            if child_chunk.metadata['parent_id'] not in parent_ids:
                parent_ids.append(child_chunk.metadata['parent_id'])

        parent_ids = parent_ids[:top_n]
        logger.info(f'Parent chunk ids :: {parent_ids}')
        
        logger.info(parent_ids)
        chunks = self._vectordb.get_by_ids_sync(chunk_collection_name, parent_ids)
        
        logger.info([ch.metadata['document_id'] for ch in chunks])
        logger.info([ch.id for ch in chunks])
        
        logger.info(f'No. of parent chunks fetched :: {len(chunks)}')

        return [
            {
                'id': chunk.id,
                'document': chunk.document,
                'metadata': chunk.metadata
            }
            for chunk in chunks
        ]
    
    def _get_reference_links(self, text: str) -> list[str]:

        logger.debug('In SMEServiceImpl class :: _get_reference_links method')
        
        pattern = r"http://.*\.png"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        
        return matches
    
    def get_parent_chunks(
        self,
        customer_uuid: str,
        application_uuid: str,
        chunk_id: str ,
        sort_by_sequence: bool,
        metadata_keys: list
    ) -> list[dict]:
        
        """
        Retrieve the parent data chunks based on the chunk_id.

        Args:
            customer_uuid (str): Unique identifier for the customer to scope the data retrieval.
            application_uuid (str): Unique identifier for the application to further scope the data.
            chunk_id (str) : Unique identifier of a chunk
            sort_by_sequence (bool): A flag indicating whether the retrieved chunks should be sorted by their sequence order. 
            metadata_keys (list): A list of metadata keys to include in the response. This specifies which metadata fields should be extracted for each chunk.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a parent data chunk.
        """
        
        logger.info("In SMEServiceImpl class :: get_parent_chunks method")
        
        cam_id = self._cam_dao.get_customer_application_mapping_id(customer_uuid, application_uuid)
        chunk_collection_name = 'cw_' + cam_id

        chunks = self._vectordb.get_by_ids_sync(chunk_collection_name, [chunk_id])
        if len(chunks) == 0:
            
            logger.error(f'No chunks with chunk_id :: {chunk_id}')
            raise ResourceNotFoundException(f"No chunks with chunk_id :: {chunk_id}")
        
        chunk = chunks[0]
        
        reference_links = self._get_reference_links(chunk.document)
        logger.info(f'Reference links :: {reference_links}')
        
        data_chunks = self._vectordb.get_by_filter_sync(chunk_collection_name, {'chunk_type' : 'table'})
        logger.info(f'No. of table/image chunks :: {len(data_chunks)}')
        
        parent_chunks = []
        
        for chunk in data_chunks:
            
            if any([ref_link in chunk.document for ref_link in reference_links]):
                parent_chunks.append({
                    'id': chunk.id,
                    'document': chunk.document,
                    'metadata': chunk.metadata
                })
        
        return self._format(parent_chunks, sort_by_sequence, metadata_keys)

    def get_neighbouring_chunks(
        self,
        customer_uuid: str,
        application_uuid: str,
        chunk_ids: list[str],
        sort_by_sequence: bool,
        metadata_keys: list[str]
    ) -> list[dict]:
        
        """
        Retrieve the neighboring chunks of the specified document chunks.

        Args:
            customer_uuid (str): Unique identifier for the customer to scope the data retrieval.
            application_uuid (str): Unique identifier for the application to further scope the data.
            chunk_ids (list[str]): A list of document chunk IDs for which neighboring chunks should be retrieved.
            sort_by_sequence (bool): A flag indicating whether the retrieved chunks should be sorted by their sequence order.
            metadata_keys (list): A list of metadata keys to include in the response. This specifies which metadata fields should be extracted for each chunk.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a neighboring data chunk 
            with associated metadata.
        """
        
        logger.info("In SMEServiceImpl class :: get_neighouring_chunks method")
        
        cam_id = self._cam_dao.get_customer_application_mapping_id(customer_uuid, application_uuid)
        chunk_collection_name = 'cw_' + cam_id
        logger.info(f'chunks collection name :: {chunk_collection_name}')

        chunks = self._vectordb.get_by_ids_sync(chunk_collection_name, chunk_ids)
        
        neighbouring_chunk_map = {}
        for chunk in chunks:
            
            doc_id = chunk.metadata['document_id']
            source = chunk.metadata['source']
            
            where = {
                "$and" : [
                    {
                        "source" : source
                    },
                    {
                        "document_id" : {
                            "$in" : [doc_id-1, doc_id, doc_id + 1]
                        }
                    }
                ]
            }
            logger.debug(f'where :: {where}')
            
            neighbours = self._vectordb.get_by_filter_sync(chunk_collection_name, filter=where)
            neighbouring_chunk_map.update(
                {neighbour.id : neighbour for neighbour in neighbours}
            )

        neighbouring_chunk_uuids = list(neighbouring_chunk_map.keys())
        neighbouring_chunks = list(neighbouring_chunk_map.values())

        logger.info(f'length of neighbouring chunk uuids :: {len(neighbouring_chunk_uuids)}')
        logger.info(f"doc ids of retrieved chunks :: {[c.metadata['document_id'] for c in neighbouring_chunks]}")
        
        neighbouring_chunks = [
            {
                'id': chunk.id,
                'document': chunk.document,
                'metadata': chunk.metadata
            }
            for chunk in neighbouring_chunks
        ]

        return self._format(neighbouring_chunks, sort_by_sequence, metadata_keys)


