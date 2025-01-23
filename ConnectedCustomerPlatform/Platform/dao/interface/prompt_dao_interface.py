from abc import ABC, abstractmethod

class IPromptDao(ABC):

    @abstractmethod
    def get_prompt_by_uuid(self, prompt_uuid):
        """
            Fetches a single prompt by its UUID.

            :param prompt_uuid: The unique identifier of the prompt.
            :return: An instance of Prompt if found, otherwise None.
        """

    @abstractmethod
    def get_prompts(self, customer_uuid, application_uuid):
        """
            Fetches all prompts for the specified customer-application.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :return: None
        """

    @abstractmethod
    def save_prompt(self, prompt):
        """
            Saves the provided prompt object in the database.

            :param prompt: An instance of Prompt to be saved.
            :return: The saved instance of Prompt.
        """

    @abstractmethod
    def delete_prompt(self, prompt_uuid,user_uuid):
        """
            Deletes the specified prompt from the database.

            :param prompt_uuid: The unique identifier of the prompt.
            :param user_uuid: The unique identifier of the user.
            :return: None
        """

    @abstractmethod
    def get_prompt_count_mapped_to_prompt_template(self, prompt_template_uuid):
        """
            Fetch the count of prompts mapped to prompt_template.

            :param prompt_template_uuid: The unique identifier of the prompt_template.
            :return: None.
        """

    @abstractmethod
    def update_prompt(self,prompt_uuid,prompt_name,prompt_category_uuid,prompt_details_json_dict,user_uuid,customer_uuid,application_uuid):
        """
            updates the provided prompt by prompt_uuid.

            :param prompt_uuid: UUID of the prompt need to be updated.
            :param prompt_name :updated prompt_name
            :param prompt_category_uuid : updated prompt_category
            :param prompt_details_json_dict : updated json
            :param user_uuid : uuid of the user who updating the prompt
            :return: Count of rows updated.
        """