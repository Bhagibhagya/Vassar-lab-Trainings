import logging

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException
from DatabaseApp.models import Customers, LLMConfigurationCustomerMapping
from Platform.constant.error_messages import ErrorMessages
from Platform.dao.interface.assign_organization_dao_interface import IAssignOrganizationDAO

logger = logging.getLogger(__name__)

class AssignOrganizationDaoImpl(IAssignOrganizationDAO):
    """
    Data Access Object (DAO) for LLM Configuration operations.
    Implements the Singleton pattern to ensure only one instance of this class is created.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(AssignOrganizationDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of LLMConfigurationDAO")
        return cls._instance
    
    def __init__(self, **kwargs):
        """
        Initialize the LLMConfigurationDAO instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside LLMConfigurationDAO - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def llm_configuration_customer_mapping(self, llm_configuration_customer_mapping_data):
        """
        Create a new mapping between an LLM configuration and a customer.

        This method takes in the mapping data and creates a new entry in the database
        for associating a customer with a specific LLM configuration.

        :param llm_configuration_customer_mapping_data

        :return: The newly created LLMConfigurationCustomerMapping instance.
        :raises: Potentially raises validation errors if the data does not conform to model constraints.
        """
        return LLMConfigurationCustomerMapping.objects.bulk_create(llm_configuration_customer_mapping_data)
    
    def get_customer_names_for_llm_configuration(self, llm_configuration_uuid: str):
        """
        Retrieve all customer names related to a specific LLM configuration.

        :param llm_configuration_uuid: UUID of the LLM configuration.
        :return: A queryset of customer names related to the given LLM configuration.
        """
        return Customers.objects.filter(
            llmconfigurationcustomermapping__llm_configuration_uuid=llm_configuration_uuid,
            llmconfigurationcustomermapping__llm_configuration_uuid__is_default=True
        ).values('cust_name','cust_uuid')  # Retrieves only the customer names
    
    def get_customer_uuids_for_llm_configuration(self, llm_configuration_uuid: str):
        """
        Retrieve the customer UUIDs associated with a specific LLM configuration.

        This method queries the database to find all customer UUIDs that are linked to the
        given LLM configuration UUID. It returns a list of these UUIDs.

        :param llm_configuration_uuid: The UUID of the LLM configuration for which to retrieve
                                    associated customer UUIDs.
        :return: A list of customer UUIDs associated with the specified LLM configuration.
                The list is flat, containing only the customer UUIDs.
        """
        return LLMConfigurationCustomerMapping.objects.filter(
            llm_configuration_uuid=llm_configuration_uuid,
        ).values_list('customer_uuid', flat=True)

    
    def delete_organization(self, llm_configuration_uuid, customer_uuid):
        """
        Remove the mapping of an organization from the LLM configuration in the database.

        This method attempts to find the existing mapping between the specified LLM configuration
        and customer organization, and deletes it if found.

        :param llm_configuration_uuid: The UUID of the LLM configuration.
        :param customer_uuid: The UUID of the customer organization to remove.
        :raises InvalidValueProvidedException: If no mapping exists for the given LLM configuration
                                            and customer UUID.
        """
        try:
            # Attempt to retrieve the mapping object based on the provided UUIDs
            llm_config_customer_map = LLMConfigurationCustomerMapping.objects.get(llm_configuration_uuid=llm_configuration_uuid,customer_uuid=customer_uuid)
            llm_config_customer_map.delete()
        except LLMConfigurationCustomerMapping.DoesNotExist:
            # Handle case where no record is found
            raise InvalidValueProvidedException(
                ErrorMessages.LLM_CONFIGURATION_CUSTOMER_MAPPING_NOT_FOUND
            )