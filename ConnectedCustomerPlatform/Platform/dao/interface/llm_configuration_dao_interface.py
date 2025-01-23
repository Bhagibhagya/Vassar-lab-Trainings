from abc import ABC, abstractmethod


class ILLMConfigurationDAO(ABC):
    """
    Interface for managing data access operations related to LLM configurations.
    This defines methods for creating, retrieving, and updating LLM configurations
    in the database. It follows the Data Access Object (DAO) pattern.
    """

    @abstractmethod
    def create_llm_configuration(self, llm_configuration_data: dict):
        """
        Create a new LLM configuration in the database.

        Args:
            llm_configuration_data (dict): Dictionary containing the LLM configuration details to be saved.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def create_llm_configuration_customer_mapping(self, mapping_data):
        """
        Create a new LLM configuration,customer mapping record in the database.

        :param mapping_data: Dictionary containing mapping data.
        """

    @abstractmethod
    def check_llm_configuration_exists(self, llm_configuration_name: str, customer_uuid: str) -> bool:
        """
        Check if an LLM configuration with a given name already exists for a customer.

        Args:
            llm_configuration_name (str): Name of the LLM configuration.
            customer_uuid (str): Unique identifier for the customer.

        Returns:
            bool: True if the configuration exists, False otherwise.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def get_customer_name(self, customer_uuid: str) -> str:
        """
        Retrieve the name of the customer based on the customer UUID.

        Args:
            customer_uuid (str): Unique identifier for the customer.

        Returns:
            str: The name of the customer if found, otherwise None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def update_llm_configuration(self, llm_configuration_uuid: str, updated_data: dict,customer_uuid: str):
        """
             Update an existing LLM configuration with the provided data.

             Args:
                 llm_configuration_uuid (str): The UUID of the LLM configuration to update.
                 updated_data (dict): A dictionary containing the updated configuration data.
                     This may include fields such as configuration name, details, API key, etc.
                 customer_uuid: Unique identifier for the customer.

             Raises:
                 CustomException: If the LLM configuration does not exist, or if an error occurs during the update process.

             Returns:
                 bool: True if the update was successful, False otherwise.

             """

    @abstractmethod
    def get_llm_configuration_by_uuid(self, llm_configuration_uuid: str, customer_uuid: str | None):
        """
        Retrieve an LLM configuration based on its unique identifier (UUID).

        Args:
            llm_configuration_uuid (str): Unique identifier for the LLM configuration.

        Returns:
            dict: A dictionary containing the configuration details, or None if not found.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def check_llm_configuration_exists_excluding_current(self, llm_configuration_name: str, customer_uuid: str,
                                                         llm_configuration_uuid: str) -> bool:
        """
        Check if an LLM configuration with a given name exists for a customer, excluding the current one by UUID.

        Args:
            llm_configuration_name (str): Name of the LLM configuration.
            customer_uuid (str): Unique identifier for the customer.
            llm_configuration_uuid (str): UUID of the LLM configuration to exclude.

        Returns:
            bool: True if a different configuration with the same name exists, False otherwise.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def mark_llm_configuration_as_deleted(self, llm_configuration_uuid: str, user_uuid: str):
        """
        Mark an LLM configuration as deleted by updating its status in the database.

        Args:
            llm_configuration_uuid (str): UUID of the LLM configuration to delete.
            user_uuid (str): UUID of the user performing the deletion.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def get_llm_configurations_by_customer_uuid(self, customer_uuid: str | None):
        """
        Retrieve all LLM configurations for a specific customer.

        Args:
            customer_uuid (str): Unique identifier for the customer.

        Returns:
            list: A list of dictionaries, where each dictionary contains LLM configuration details.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def get_llm_configuration_by_id(self, customer_uuid: str | None, llm_configuration_uuid: str):
        """
        Retrieve a specific LLM configuration by its UUID.

        Args:
            llm_configuration_uuid (str): UUID of the LLM configuration.

        Returns:
            dict: A dictionary containing the LLM configuration details if found, otherwise None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abstractmethod
    def get_llm_provider_meta_data(self) -> list:
        """
        Retrieve metadata for all LLM providers.

        Returns:
            list: A list of dictionaries, where each dictionary contains metadata about an LLM provider.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        
    @abstractmethod
    def delete_mapping_by_llm_configuration_uuid(self, llm_configuration_uuid: str):
        """
            Deletes the llm_configuration_customer_mapping using llm_configuration_uuid
            :param : llm_configuration_uuid whose mappings need to be deleted
        """
    
    @abstractmethod
    def update_llm_status_by_id(self, customer_uuid, status):
        """
        Updates the status field in LLMConfiguration based on the given customer_uuid.
        If customer_uuid is None, updates status for configurations where is_default=True.
        Otherwise, updates status for configurations mapped to the given customer_uuid.
        Handles database exceptions gracefully.
        """
