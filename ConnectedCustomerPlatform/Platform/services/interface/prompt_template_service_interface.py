from abc import ABC, abstractmethod

class IPromptTemplateService(ABC):
    @abstractmethod
    def create_prompt_template(self, customer_uuid, application_uuid, user_uuid, prompt_data):
        """
            Creates new prompt in the database.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param user_uuid: The unique identifier of the user performing the operation.
            :param prompt_data: A dictionary containing the prompt data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def update_prompt_template(self, customer_uuid, application_uuid, user_uuid, prompt_template):
        """
            Updates existing prompt_template in the database.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param user_uuid: The unique identifier of the user performing the operation.
            :param prompt_template: A dictionary containing the updated prompt_template data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_prompt_templates(self,customer_uuid,application_uuid,prompt_category_uuid):
        """
            Fetches all prompt_templates for the specified customer-application.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param prompt_category_uuid: The unique identifier of the prompt_category
            :return: None
        """

    @abstractmethod
    def get_prompt_template_by_id(self, mapping_uuid):
        """
            Fetches all prompt_templates for the specified customer-application.

            :param mapping_uuid: The unique identifier of the prompt_templates.
            :return: None
        """

    @abstractmethod
    def delete_prompt_template(self, prompt_template_uuid,user_uuid):
        """
            Deletes prompt_template_customer_application_mapping from the database.

            :param prompt_template_uuid: The unique identifier of the prompt_template to be deleted.
            :param user_uuid : user uuid who deleting the prompt_template
            :return: None
        """

    @abstractmethod
    def get_prompt_categories(self):
        """
            Fetches all prompt_categories .
            :return: None
        """

