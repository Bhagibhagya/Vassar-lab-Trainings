from abc import ABC, abstractmethod

class IAssignOrganizationDAO(ABC):
    """
    Interface for managing data access operations related to Assign organizations.
    This defines methods for creating, retrieving, and deleting LLM configurations
    in the database. It follows the Data Access Object (DAO) pattern.
    """
    @abstractmethod
    def llm_configuration_customer_mapping(self, llm_configuration_customer_mapping_data):
        """
        Create a new mapping between an LLM configuration and a customer.

        This method takes in the mapping data and creates a new entry in the database
        for associating a customer with a specific LLM configuration.

        :param llm_configuration_customer_mapping_data

        :return: The newly created LLMConfigurationCustomerMapping instance.
        :raises: Potentially raises validation errors if the data does not conform to model constraints.
        """

    @abstractmethod
    def get_customer_names_for_llm_configuration(self, llm_configuration_uuid: str):
        """
        Retrieve all customer names related to a specific LLM configuration.

        :param llm_configuration_uuid: UUID of the LLM configuration.
        :return: A queryset of customer names related to the given LLM configuration.
        """

    @abstractmethod
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

    @abstractmethod
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