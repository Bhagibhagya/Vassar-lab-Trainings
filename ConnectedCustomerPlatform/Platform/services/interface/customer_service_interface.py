from abc import ABC, abstractmethod


class ICustomerService(ABC):

    @abstractmethod
    def get_customers(self):
        """
        Retrieve customer IDs and names from the database.

        :return: A dictionary containing a list of customers with their IDs and names.
        """