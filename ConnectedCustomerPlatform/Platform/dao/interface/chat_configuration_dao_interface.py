from abc import ABC, abstractmethod

class IChatConfigurationDao(ABC):
    @abstractmethod
    def get_all_chat_configurations(self, application_uuid, customer_uuid,chat_configuration_type):
        """
        Retrieve chat configurations for a specific application and customer.

        Args:
            application_uuid (str): UUID of the application.
            customer_uuid (str): UUID of the customer.
            chat_configuration_type(srt) : intent_page or landing_page

        Returns:
            List[ChatConfiguration]: A list of ChatConfiguration instances.
        """


    @abstractmethod
    def get_configuration_by_uuid(self, chat_configuration_uuid):
        """
        Retrieve a ChatConfiguration by its UUID.

        Args:
            chat_configuration_uuid (str): The UUID of the chat configuration.

        Returns:
            ChatConfiguration: The corresponding ChatConfiguration object or None if not found.
        """


    @abstractmethod
    def delete_configuration_by_uuid(self, chat_configuration_uuid: str) -> int:
        """
        Deletes a chat configuration by its UUID.

        Args:
            chat_configuration_uuid (str): UUID of the chat configuration to delete.

        Returns:
            int: The number of rows deleted.
        """


    @abstractmethod
    def get_active_configurations(self, application_uuid, customer_uuid) :
        """
        Get active chat configurations based on application and customer UUIDs.

        Args:
            application_uuid (str): The UUID of the application.
            customer_uuid (str): The UUID of the customer.

        Returns:
            List: A list of active ChatConfiguration objects.
        """


    @abstractmethod
    def get_default_template_by_type(self, chat_configuration_type):
        """
        Get the default template based on the configuration type.

        Args:
            chat_configuration_type (str): The type of the chat configuration.

        Returns:
            Optional[Any]: The default ChatConfiguration object or None if not found.
        """



    @abstractmethod
    def create_configuration(self, data,application_uuid, customer_uuid, user_id,chat_configuration_data) :
        """
        Retrieve or create a ChatConfiguration instance.

        Args:
            data (dict): A dictionary containing configuration data.
            application_uuid (str): The UUID of the application.
            customer_uuid (str): The UUID of the customer.
            user_id (str): The ID of user
            chat_configuration_data (dict): Processed chat configuration
        Returns:
            Any: The ChatConfiguration instance retrieved or created.
        """


    @abstractmethod
    def update_configuration(self, instance):
        """
        Update the ChatConfiguration instance.

        Args:
            instance: The ChatConfiguration instance to be saved.

        Returns:
            None
        """


    @abstractmethod
    def get_default_templates(self):
        """
        Retrieve all default ChatConfiguration templates.

        Returns:
            List: A list of default ChatConfiguration objects.
        """


    @abstractmethod
    def get_configuration_templates_and_name_count(self, application_uuid: str, customer_uuid: str,
                                                   chat_configuration_type: str, chat_configuration_name: str,
                                                   chat_configuration_provider: str):
        """
        Fetches the count of configurations and the count of configurations with the specified name.

        :param application_uuid: UUID of the application
        :param customer_uuid: UUID of the customer
        :param chat_configuration_type: Type of chat configuration
        :param chat_configuration_name: Name of the chat configuration
        :param chat_configuration_provider: Provider of the chat configuration
        :return: A tuple of (configuration_count, name_count)
        """

