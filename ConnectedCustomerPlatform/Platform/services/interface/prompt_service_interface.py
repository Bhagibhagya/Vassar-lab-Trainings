from abc import ABC, abstractmethod

class IPromptService(ABC):
    @abstractmethod
    def create_prompt(self, customer_uuid, application_uuid, user_uuid, prompt_data):
        """
            Creates new prompt in the database.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param user_uuid: The unique identifier of the user performing the operation.
            :param prompt_data: A dictionary containing the prompt data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_prompts(self, customer_uuid, application_uuid):
        """
            Fetches all prompts for the specified application.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :return: A list of Prompts matching the criteria.
        """

    @abstractmethod
    def get_prompt_by_id(self, prompt_uuid):
        """
            Fetches prompt by prompt_uuid.

            :param prompt_uuid The unique identifier of the prompt to be fetched.
            :return: Prompt matching the criteria.
        """

    @abstractmethod
    def update_prompt(self, customer_uuid, application_uuid, user_uuid, prompt):
        """
            Updates existing prompt in the database.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param user_uuid: The unique identifier of the user performing the operation.
            :param prompt: A dictionary containing the updated prompt data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def delete_prompt(self, prompt_uuid):
        """
            Deletes prompt from the database.

            :param prompt_uuid: The unique identifier of the prompt to be deleted.
            :return: None
        """

