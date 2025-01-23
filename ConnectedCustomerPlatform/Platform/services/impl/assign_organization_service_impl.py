import logging
from ConnectedCustomerPlatform.utils import create_new_uuid_4
from DatabaseApp.models import Customers, LLMConfiguration, LLMConfigurationCustomerMapping
from Platform.dao.impl.assign_organization_dao_impl import AssignOrganizationDaoImpl
from Platform.services.interface.assign_organization_service_interface import IAssignOrganizationService

logger = logging.getLogger(__name__)

class AssignOrganizationServiceImpl(IAssignOrganizationService):
    """
    Service layer for handling LLM configuration logic such as adding, editing, deleting,
    and retrieving LLM configurations. Interacts with the DAO layer and manages
    integration with Azure Key Vault for securely storing API keys.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AssignOrganizationServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside LLMConfigurationService - Singleton Instance ID: {id(self)}")
            self.__assign_org_dao = AssignOrganizationDaoImpl()
            self.initialized = True

    def add_organizations(self, user_uuid: str, data: dict):
        """
        Add organizations to the specified LLM configuration.

        This method handles the addition of new organizations for a given LLM configuration.
        It checks for existing mappings and creates new mappings only if they do not already exist.

        :param user_uuid: The UUID of the user performing the operation. This is used for tracking
                        who created or updated the organization mappings.
        :param data: A dictionary containing the organization data. Expected keys are:
                    - llm_configuration_uuid: The UUID of the LLM configuration to which the organizations
                    will be added.
                    - organizations: A list of organizations (customer UUIDs) to be associated with
                    the specified LLM configuration.
        :raises CustomException: If there are issues during the retrieval of existing mappings or if the organization mapping process encounters errors.
        """
        llm_configuration_uuid = data.get('llm_configuration_uuid')
        organizations = data.get('organizations')

        # Retrieve all existing mappings for the given llm_configuration_uuid and customer UUIDs
        existing_mappings = self.__assign_org_dao.get_customer_uuids_for_llm_configuration(llm_configuration_uuid)
        
        # Convert the existing mappings to a set for quick lookup
        existing_mappings_set = set(existing_mappings)
        
        # List to hold new mappings for bulk creation
        new_mappings = []

        # Create a set of customer UUIDs from the incoming organizations
        incoming_customer_uuids = {str(Customers(org).cust_uuid) for org in organizations}

        # Iterate over the list of organizations to add them to the LLM configuration
        for organization in organizations:
            mapping_uuid = create_new_uuid_4()
            llm_configuration_instance = LLMConfiguration(llm_configuration_uuid)
            # Retrieve a customer instance by UUID
            customer_instance = Customers(organization)
            
            # Check if the mapping already exists in the set
            if str(customer_instance.cust_uuid) not in existing_mappings_set:
                new_mapping_data = {
                    'mapping_uuid': mapping_uuid,
                    'llm_configuration_uuid': llm_configuration_instance,
                    'customer_uuid': customer_instance,
                    'created_by': user_uuid,
                    'updated_by': user_uuid
                }
                new_mappings.append(LLMConfigurationCustomerMapping(**new_mapping_data))
            else:
                logger.debug(f"Mapping already exists for organization {organization} and llm_configuration {llm_configuration_uuid}. Skipping creation.")
        
        # Handle removal of mappings for customer UUIDs that are no longer present
        customer_uuids_to_remove = existing_mappings_set - incoming_customer_uuids
        for customer_uuid in customer_uuids_to_remove:
            self.__assign_org_dao.delete_organization(llm_configuration_uuid, customer_uuid)
            logger.info(f"Removed organization mapping for customer_uuid: {customer_uuid} from llm_configuration_uuid: {llm_configuration_uuid}")

        if new_mappings:
            self.__assign_org_dao.llm_configuration_customer_mapping(new_mappings)
        logger.info("Assigned organizations for LLM configuration successfully")
    
    def get_organizations(self, llm_configuration_uuid: str):
        """
        Fetch the list of organizations associated with the specified LLM configuration.

        This method interacts with the data access object (DAO) to retrieve customer names
        linked to the provided LLM configuration UUID. It also hardcodes communication channels
        that are available for each customer.

        :param llm_configuration_uuid: The UUID of the LLM configuration for which to retrieve organizations.
        :return: A list of dictionaries containing organization details, including:
                - customer_name: The name of the customer organization.
                - customer_uuid: The UUID of the customer organization.
                - channels: A hardcoded list of available communication channels for the organization.
        """
        organizations = self.__assign_org_dao.get_customer_names_for_llm_configuration(llm_configuration_uuid)

        # Hardcode the channels
        channels = ["Email", "Chat", "Phone"]

        result = [{
            "customer_name": org['cust_name'],
            "customer_uuid": org['cust_uuid'],
            "channels": channels  # Add the hardcoded channels
        } for org in organizations]

        return result
    
    def delete_organization(self, llm_configuration_uuid: str, customer_uuid: str):
        """
        Delegate the deletion of an organization associated with a specified LLM configuration.

        This method calls the data access object (DAO) to remove the organization mapping
        based on the provided LLM configuration UUID and customer UUID.

        :param llm_configuration_uuid: The UUID of the LLM configuration from which to remove the organization.
        :param customer_uuid: The UUID of the customer organization to be deleted from the mapping.
        """
        self.__assign_org_dao.delete_organization(llm_configuration_uuid, customer_uuid)

    def get_organization_by_id(self, customer_uuid : str, channel : str | None):
        """
        Fetch organization details associated with a specific customer UUID.

        This method returns a list of organization details. If a channel is specified, the results
        are filtered to include only those organizations that match the given channel.

        :param customer_uuid: The UUID of the customer organization for which to retrieve details.
        :param channel: The communication channel to filter the results (optional).
        :return: A list of dictionaries containing organization details, including applications,
                channels, and associated services.
        """
        organization_data = [
            {
                "Application": "Finance",
                "Channel": "Email",
                "Services": ["Intent Classification", "Intent Identification"]
            },
            {
                "Application": "Insurance",
                "Channel": "Chat",
                "Services": ["PDF Parsing"]
            },
            {
                "Application": "HR",
                "Channel": "Phone",
                "Services": ["All"]
            }
        ]

        # If a channel is provided, filter the organization data based on that channel
        if channel:
            filtered_organization_data = [
                data for data in organization_data if data["Channel"] == channel
            ]
            return filtered_organization_data

        # If no channel is provided, return all organization data
        return organization_data