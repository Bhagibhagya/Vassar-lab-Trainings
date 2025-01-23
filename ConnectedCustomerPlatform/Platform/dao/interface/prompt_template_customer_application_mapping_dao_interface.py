from abc import ABC, abstractmethod

class IPromptTemplateCustomerApplicationMappingDao(ABC):

    @abstractmethod
    def save_mapping(self, mapping):
        """
            Saves the provided mapping object in the database.

            :param mapping: An instance of PromptTemplateCustomerApplicationMapping to be saved.
            :return: The saved instance of PromptTemplateCustomerApplicationMapping.
        """

    @abstractmethod
    def get_mappings(self,customer_uuid,application_uuid,prompt_category_uuid):
        """
            Fetches all prompt_template_customer_application_mappings for the specified application.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param prompt_category_uuid: The unique identifier of the prompt_category
            :return: A list of PromptTemplateCustomerApplicationMapping matching the criteria.
        """

    @abstractmethod
    def get_mapping_by_id(self,mapping_uuid):
        """
            Fetches all prompt_template_customer_application_mapping by mapping_uuid.

            :param mapping_uuid: The unique identifier of the prompt_template_customer_application_mapping.
            :return: PromptTemplateCustomerApplicationMapping matching the criteria.
        """

    @abstractmethod
    def delete_mapping_by_template_uuid(self, prompt_template_uuid):
        """
            Deletes the specified prompt_template_customer_application_mapping from the database.

            :param prompt_template_uuid: An unique identifier of the PromptTemplate whose mappings to be deleted.
            :return: None
        """

    @abstractmethod
    def get_mapping_by_template_name(self,prompt_template_name, customer_uuid, application_uuid,exclude_uuid):
        """
            Fetches all prompt_template_customer_application_mappings for the specified application.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param prompt_template_name: Prompt template name whose mapping to be fetched
            :param exclude_uuid : prompt_template_uuid need to be excluded from the list (required for update api)
            :return: PromptTemplateCustomerApplicationMapping matching the criteria.
        """