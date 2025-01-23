from abc import ABC, abstractmethod
import logging
from typing import Union

logger = logging.getLogger(__name__)


class ISMEService(ABC):
    """
    Abstract base class for the SME service, defining the interface for
    managing questions and answers, drafts, feedback, and other related
    operations.
    """

    @abstractmethod
    def get_questions(self, filter, customer_uuid, application_uuid, entity_uuids_list):
        """
        Retrieve a list of questions based on the provided filter,
        customer UUID, application UUID, entity uuids list.

        :param filter: The criteria to filter questions.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.
        :param entity_uuids_list: entities scope
        :return: List of questions matching the criteria.
        """

    @abstractmethod
    def get_question_details(self, question_uuid, entity_uuids_list):
        """
        Retrieve a specific question using its UUID.

        :param question_uuid: Unique identifier for the question.
        :param entity_uuids_list: entities scope
        :return: Question object corresponding to the UUID.
        """

    @abstractmethod
    def add_question(self, data, customer_uuid, application_uuid, user_uuid):
        """
        Add a new question to the database.

        :param data: The data containing the details of the question.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.
        :param user_uuid: Unique identifier for the user adding the question.
        :return: Confirmation of the operation.
        """

    @abstractmethod
    def delete_answer(self, answer_uuid, customer_uuid, application_uuid, entity_uuids_list):
        """
        Delete an answer using its UUID.

        :param answer_uuid: Unique identifier for the answer to be deleted.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.
        :param entity_uuids_list: entities scope
        :return: Confirmation of the deletion operation.
        """

    @abstractmethod
    def update_answer(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Update an existing answer in the database.

        :param data: The updated answer content and associated details.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.
        :param entity_uuids_list: entities scope
        :param user_uuid: Unique identifier for the user updating the answer.
        :return: Confirmation of the update operation.
        """

    @abstractmethod
    def verify_answer(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Verify the correctness of an answer.

        :param data: The verification details and associated content.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.
        :param user_uuid: Unique identifier for the user verifying the answer.
        :param entity_uuids_list: entities scope
        :return: Confirmation of the verification operation.
        """

    @abstractmethod
    def update_feedback(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Update feedback for an existing answer.

        :param data: The updated feedback content and associated details.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.
        :param user_uuid: Unique identifier for the user updating the feedback.
        :param entity_uuids_list: entities scope
        :return: Confirmation of the update operation.
        """

    @abstractmethod
    def generate_qa(self, data, customer_uuid, application_uuid, user_uuid, entity_uuids_list):
        """
        Generate a question and answer pair based on the provided data.

        :param data: The input data for generating the QA pair.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.
        :param user_uuid: Unique identifier for the user generating the QA.
        :param entity_uuids_list: entities scope
        :return: The generated question and answer pair.
        """

    @abstractmethod
    def get_entity_ids_from_request(self, requst):
        """
        Get the entity uuids from scope if present in request by chekcing the scope type.
        :param request: api request
        """

    @abstractmethod
    def get_relevant_chunks(
        self,
        customer_uuid: str,
        application_uuid: str,
        query: str,
        entity_filter: Union[dict, None],
        n: int,
        sort_by_sequence: bool,
        metadata_keys: list
    ) -> list[dict]:
        
        """
        Retrieve the most relevant data chunks based on the provided query and filters.

        Args:
            customer_uuid (str): Unique identifier for the customer to scope the data retrieval.
            application_uuid (str): Unique identifier for the application to further scope the data.
            query (str): The search query used to identify relevant chunks.
            entity_filter (dict): Additional filters to narrow down the search (e.g., entity type, attributes).
            n (int): The maximum number of relevant chunks to return.
            sort_by_sequence (bool): A flag indicating whether the retrieved chunks should be sorted by their sequence order. 
            metadata_keys (list): A list of metadata keys to include in the response. This specifies which metadata fields should be extracted for each chunk.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a relevant data chunk
            with associated metadata.
        """
        pass
    
    @abstractmethod
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

    @abstractmethod
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
        pass


