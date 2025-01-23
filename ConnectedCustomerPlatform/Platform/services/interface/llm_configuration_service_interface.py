from abc import ABC, abstractmethod


class ILLMConfigurationService(ABC):
    """
    Interface for managing LLM configurations.

    This interface provides abstract methods for adding, editing, deleting,
    and retrieving LLM configurations based on customer or configuration ID.
    """

    @abstractmethod
    def add_llm_configuration(self, customer_uuid: str | None, user_uuid: str, data: dict):
        """
        Add a new LLM configuration for a specific customer.

        Args:
            customer_uuid (str): Unique identifier for the customer.
            user_uuid (str): Unique identifier for the user performing the action.
            data (dict): Dictionary containing configuration details, including
                         name, details in JSON format, etc.

        Raises:
            CustomException: If there is an error adding the configuration (e.g.,
                             if a configuration with the same name already exists).
        """

    @abstractmethod
    def edit_llm_configuration(self, customer_uuid: str | None, user_uuid: str, data: dict):
        """
        Edit an existing LLM configuration for a specific customer.

        Args:
            customer_uuid (str): Unique identifier for the customer.
            user_uuid (str): Unique identifier for the user performing the action.
            data (dict): Dictionary containing updated configuration details.

        Raises:
            CustomException: If the configuration to edit does not exist or if there
                             is an error during the update process.
        """

    @abstractmethod
    def delete_llm_configuration(self, llm_configuration_uuid: str, user_uuid: str):
        """
        Delete an LLM configuration by its unique identifier.

        Args:
            llm_configuration_uuid (str): Unique identifier for the LLM configuration to be deleted.
            user_uuid (str): Unique identifier for the user performing the action.

        Raises:
            CustomException: If the configuration to delete does not exist.
        """

    @abstractmethod
    def get_llm_configurations(self, customer_uuid: str | None) -> list:
        """
        Retrieve all LLM configurations for a specific customer.

        Args:
            customer_uuid (str): Unique identifier for the customer.

        Returns:
            list: A list of dictionaries containing LLM configuration details for the customer.

        Raises:
            CustomException: If there is an error retrieving configurations.
        """

    @abstractmethod
    def get_llm_configuration_by_id(self, customer_uuid: str | None, llm_configuration_uuid: str):
        """
        Retrieve a specific LLM configuration by its unique identifier.

        Args:
            llm_configuration_uuid (str): Unique identifier for the LLM configuration.

        Returns:
            dict: A dictionary containing the configuration details.

        Raises:
            CustomException: If the configuration does not exist.
        """

    @abstractmethod
    def get_llm_provider_meta_data(self) -> list:
        """
        Retrieve metadata for all LLM providers.

        Returns:
            list: A list of dictionaries containing metadata for each LLM provider.

        Raises:
            CustomException: If there is an error retrieving the metadata.
        """

    @abstractmethod
    def update_llm_status_by_id(self, customer_uuid: str | None, status: bool):
        """
        :param customer_uuid: UUID of the customer to which the configurations status values has to be updated.
        :param status: Boolean value to update the status of the configurations.
        """

    @abstractmethod
    def get_llm_status_by_id(self, customer_uuid: str | None):
        """
        :param customer_uuid: UUID of the customer to which the configurations status values has to be fetched.
        """
