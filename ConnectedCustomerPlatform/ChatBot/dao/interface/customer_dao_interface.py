from abc import ABC, abstractmethod

from ChatBot.dataclasses.customer_data import CustomerData


class ICustomerDao(ABC):
    """
        Interface for managing Customers.
        This interface provides abstract methods for creating, updating, deleting, retrieving applications
    """
    @abstractmethod
    def create_customer(self, customer_data: CustomerData):
        """
            create a customer record in user customer table
            Args:
                customer_data (CustomerData): CustomerData dataclass instance
            Returns:
                returns created customer queryset
        """