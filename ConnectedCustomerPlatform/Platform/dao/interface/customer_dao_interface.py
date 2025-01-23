from abc import ABC, abstractmethod

class ICustomerDAO(ABC):
    """
    Interface for managing data access operations related to Assign organizations.
    This defines methods for creating, retrieving, and deleting LLM configurations
    in the database. It follows the Data Access Object (DAO) pattern.
    """
    @abstractmethod
    def get_customers_id_and_name(self):
        """
        Retrieve the customers Id and name from customers table.
        """