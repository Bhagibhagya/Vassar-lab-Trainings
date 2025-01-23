from abc import ABC, abstractmethod

class IChatConfigurationService(ABC):
    @abstractmethod
    def get_all_chat_configurations(
        self,
        application_uuid: str,
        customer_uuid: str,
        chat_configuration_type: str
    ):
        """
        Fetches and processes chat configurations based on application and customer UUIDs.

        Args:
            application_uuid (str): UUID of the application.
            customer_uuid (str): UUID of the customer.
            chat_configuration_type (str): Type of chat configuration to filter by.

        Returns:
            List[Dict[str, Any]]: A list of processed chat configuration data.
        """

    @abstractmethod
    def delete_chat_configuration(self, chat_configuration_uuid,customer_uuid, application_uuid):
        """
        Deletes a ChatConfiguration by its UUID.

        Args:
            chat_configuration_uuid (str): The UUID of the chat configuration to delete.
            application_uuid (str): UUID of the application.
            customer_uuid (str): UUID of the customer.

        Raises:
            CustomException: If the configuration is not found or if it is the default configuration.
        """


    @abstractmethod
    def get_active_chat_configurations(self, application_uuid, customer_uuid) :
        """
        Get active chat configurations specific to application and customer.

        Args:
            application_uuid (str): The UUID of the application.
            customer_uuid (str): The UUID of the customer.

        Returns:
            Dict[str, Any]: A dictionary containing the active chat details.
        """


    @abstractmethod
    def update_activation_status(self, chat_configuration_uuid, chat_configuration_type,
                                                                 application_uuid, customer_uuid ,user_id):
        """
        Make a configuration active.

        Args:
            chat_configuration_uuid (str): The UUID of the chat configuration.
            chat_configuration_type (str): The type of the chat configuration.
            application_uuid (str): The UUID of the application.
            customer_uuid (str): The UUID of the customer.
            user_id (str): The ID of user.

        Returns:
            None
        """


    @abstractmethod
    def get_chat_configuration(self, chat_configuration_uuid,customer_uuid,application_uuid):
        """
        Get configuration based on configuration UUID.

        Args:
            chat_configuration_uuid (str): The UUID of the chat configuration.
            application_uuid (str): The UUID of the application.
            customer_uuid (str): The UUID of the customer.
        Returns:
            Any: The configuration object or raises an exception if not found.
        """




    @abstractmethod
    def create_or_update_chat_configuration(self, data, application_uuid, customer_uuid, user_id) :
        """
        Main method to update the chat configuration.

        Args:
            data (Dict[str, Any]): The data for updating the chat configuration.
            application_uuid (str): The UUID of the application.
            customer_uuid (str): The UUID of the customer.
            user_id (str): The ID of user.

        Returns:
            Union[str, Any]: Success message or chat configuration JSON.
        """


    @abstractmethod
    def process_web_configuration(self, data) :
        """
        Process the configuration specific to web.

        Args:
            data (Dict[str, Any]): The data for processing the web configuration.

        Returns:
            Any: The processed chat configuration data.
        """

