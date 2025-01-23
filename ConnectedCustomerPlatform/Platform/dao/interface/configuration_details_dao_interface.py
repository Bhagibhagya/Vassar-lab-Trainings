from abc import ABC, abstractmethod


class IConfigurationDetailsDAO(ABC):

    @abstractmethod
    def update_llm_status(self, customer_uuid: str | None, status: bool):
        """
        Create or update the LLM configuration status in the database.

        Args:
            customer_uuid (str|None): UUID of customer for which the llm configuration status details to be saved.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """ 
    @abstractmethod
    def get_llm_status_by_id(self, customer_uuid: str | None):
        """
        Retrieve the LLM configuration status for a specific customer.

        Args:
            customer_uuid (str|None): UUID of the customer.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """