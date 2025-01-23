from abc import ABC, abstractmethod


class IAssignOrganizationService(ABC):
    """
    Interface for managing Assigning organizations.

    This interface provides abstract methods for adding, deleting,
    and retrieving Assigned Organizations based on LLM Configuration ID.
    """

    @abstractmethod
    def add_organizations(self, user_uuid: str, data: dict):
        """
        Add the new organizations for a specific llm configuration.

        Args:
            customer_uuid (str): Unique identifier for the customer.
            user_uuid (str): Unique identifier for the user performing the action.
            data (dict): Dictionary containing LLM configuration UUID, customer UUIDs.

        Raises:
            CustomException: If there is an error adding the configuration (e.g.,
                             if a configuration with the same name already exists).
        """

    @abstractmethod
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
    
    @abstractmethod
    def delete_organization(self, llm_configuration_uuid: str, customer_uuid: str):
        """
        Delegate the deletion of an organization associated with a specified LLM configuration.

        This method calls the data access object (DAO) to remove the organization mapping
        based on the provided LLM configuration UUID and customer UUID.

        :param llm_configuration_uuid: The UUID of the LLM configuration from which to remove the organization.
        :param customer_uuid: The UUID of the customer organization to be deleted from the mapping.
        """
    
    @abstractmethod
    def get_organization_by_id(self, customer_uuid : str, channel : str | None):
        """
         Get Organization by ID
        """
    