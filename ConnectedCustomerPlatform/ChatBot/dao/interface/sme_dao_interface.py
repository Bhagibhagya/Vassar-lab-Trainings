from abc import ABC, abstractmethod
from ChatBot.dataclasses.sme_data import Question, Answer, Draft

class ISMEDao(ABC):

    @abstractmethod
    def update_entity_uuid_in_answer(self, old_entity_uuid, new_entity_uuid, user_uuid):
        """Updates answer entity details json having old entity_uuid to new entity uuid"""

    # Retrieve all questions for a specific customer and application, with pagination.
    @abstractmethod
    def get_questions(self, customer_uuid, application_uuid, filter, entity_uuids_list):
        """prepares queryset all questions for a specific customer and application and feedback filter."""

    # Retrieve a specific question using its UUID.
    @abstractmethod
    def get_question_details(self, question_uuid, entity_uuids_list):
        """Fetch question details by its UUID and entity_uuids scope."""

    # Create a new question and associate it with the given user.
    @abstractmethod
    def create_question(self, question: Question, user_uuid):
        """Create a new question in the system."""

    # Create a new answer and associate it with the given user.
    @abstractmethod
    def create_answer(self, answer: Answer, user_uuid):
        """Create a new answer in the system."""

    # Retrieve the list of question UUIDs related to a specific answer UUID.
    @abstractmethod
    def get_question_uuids_by_answer_uuid(self, answer_uuid):
        """Get all question UUIDs associated with a given answer UUID."""

    # Delete an answer from the system using its UUID.
    @abstractmethod
    def delete_answer_by_answer_uuid(self, answer_uuid, entity_uuids_list):
        """Delete an answer from the system by its UUID if the answer is user scope by comparing entity_uuids_list."""

    # Retrieve the question UUIDs that are already cached for a given answer UUID.
    @abstractmethod
    def get_question_uuids_by_answer_uuid_and_cache(self, answer_uuid, cache, entity_uuids_list):
        """Fetch question UUIDs for a given answer cache status and in scope of list of entity_uuids."""

    # Save a draft to the database.
    @abstractmethod
    def save_draft(self, draft: Draft, user_uuid):
        """Save a draft to the system."""

    # Set all questions related to an answer as cached.
    @abstractmethod
    def update_question_cache_details(self, answer_uuid, user_uuid, cache):
        """updates all associated questions for a specific answer with given cache status"""

    # Update an existing answer with new details.
    @abstractmethod
    def update_answer(self, answer: Answer, user_uuid):
        """Update an answer's details in the system."""

    # Set the verification details for a specific answer.
    @abstractmethod
    def update_answer_verification_details(self, answer_uuid, is_verified, verifier_role_uuid, user_uuid, entity_uuids_list):
        """Update verification status and verifier details for a given answer UUID and in scope of list of entity uuids."""

    # Set feedback for an answer.
    @abstractmethod
    def update_answer_feedback_and_cache(self, answer_uuid, feedback, in_cache, user_uuid):
        """updates feedback, cache for a specific answer UUID."""

    @abstractmethod
    def delete_draft_by_answer_uuid(self, answer_uuid):
        """delete draft with given answer uuid"""

    # Create a test answer for testing purposes.
    @abstractmethod
    def create_test_answer(self, customer_uuid, application_uuid, user_uuid, entity_details_json):
        """Create a test answer for testing scenarios."""

    # Create a test question for testing purposes.
    @abstractmethod
    def create_test_question(self, question_uuid, answer_uuid, customer_uuid, application_uuid, user_uuid):
        """Create a test question for testing scenarios."""

    @abstractmethod
    def questions_answers_of_knowledge_source(self, knowledge_source_uuid):
        """
           returns questions and answers        
        Args:
            knowledge_source_uuid (str): The knowledge_source_uuid of the knowledge source to update.
        """   

    @abstractmethod
    def in_cache_update_for_answers_of_knowledge_source(self, answer_list):
        """
        Updates the 'in_cache' status to False for all answers linked to the specified knowledge source name.
        Args:
            answer_list (str): list of answers will  update.
        """  
    @abstractmethod
    def delete_answers_of_knowledge_source(self, knowledge_source_uuid):
        """
           deletes answers based on knowledge_source_uuid
        Args:
            knowledge_source_uuid (str): The knowledge_source_uuid of the knowledge source to update.
        """       

    @abstractmethod
    def get_answer_uuids_by_source(self, knowledge_source_name: str, customer_uuid: str, application_uuid: str) -> list[str]:
        
        """
        Fetches the list of answer uuids which are answered from the given knowledge source.

        :param knowledge_source_name: The name of the knowledge source.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.

        :return: list of answer uuids.
        """
        pass
    
    
    @abstractmethod
    def delete_by_answer_uuids(self, answer_uuids: list[str]) -> None:
        
        """
        Delete answers by the given list of answer uuids

        :param answer_uuids: The list of answer uuids to delete.

        :return: None
        """
        pass