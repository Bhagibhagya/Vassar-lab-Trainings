from abc import ABC, abstractmethod
class IChatConfigurationMappingDAO(ABC):

    @abstractmethod
    def get_or_create_mapping_by_publishing(self, chat_configuration_instance, application_uuid, customer_uuid, user_id):
        """
        Get or create a ChatConfigurationCustomerApplicationMapping instance.
        :param chat_configuration_instance: The chat configuration object.
        :param application_uuid: The application UUID object.
        :param customer_uuid: The customer UUID object.
        :param user_id: ID of the user
        :return: A tuple (instance, created), where `instance` is the ChatConfigurationCustomerApplicationMapping
                 and `created` is a boolean indicating if a new object was created.
        """


    @abstractmethod
    def update_mapping_status(self, mapping, status, user_id):
        """
        Update the status of a specific mapping.
        :param mapping: The ChatConfigurationCustomerApplicationMapping instance.
        :param status: The new status (boolean).
        :param user_id: ID of the user
        """



    @abstractmethod
    def deactivate_other_configurations(self, application_uuid, customer_uuid, chat_configuration_type, exclude_uuid, user_id):
        """
        Deactivate all configurations in ChatConfigurationCustomerApplicationMapping
        except the one published.
        """


    @abstractmethod
    def check_mapping_exists(self, chat_configuration_uuid: str, customer_uuid: str, application_uuid: str) -> bool:
        """
        Check if a mapping exists between the given chat_configuration_uuid, customer_uuid, and application_uuid.

        :param chat_configuration_uuid: UUID of the chat configuration
        :param customer_uuid: UUID of the customer
        :param application_uuid: UUID of the application
        :return: True if mapping exists, False otherwise
        """
