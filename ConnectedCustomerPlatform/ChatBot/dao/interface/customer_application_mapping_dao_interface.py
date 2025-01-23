from abc import ABC, abstractmethod



class ICustomerApplicationMappingDao(ABC):
    """
        Interface for managing Customers.
        This interface provides abstract methods for creating, updating, deleting, retrieving applications
    """
    @abstractmethod
    def get_customer_application_mapping_id(self, customer_uuid: str, application_uuid: str) -> str:
        """get customer application mapping id for given customer uuid and application uuid"""