import logging

from Platform.dao.impl.customer_dao_impl import CustomerDaoImpl
from Platform.services.interface.customer_service_interface import ICustomerService
logger = logging.getLogger(__name__)

class CustomerServiceImpl(ICustomerService):
    """
    Service layer for handling retrieving customers logic. Interacts with the DAO layer.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside LLMConfigurationService - Singleton Instance ID: {id(self)}")
            self.__customer_org_dao = CustomerDaoImpl()
            self.initialized = True

    def get_customers(self):
        """
        Retrieve customer IDs and names from the database.

        :return: A dictionary containing a list of customers with their IDs and names.
        """
        # Fetch customer IDs and names from the data access object (DAO)
        customers = self.__customer_org_dao.get_customers_id_and_name()

        # Initialize a list to hold customer dictionaries
        response_data = []

        # Iterate through the fetched customer tuples (customer_id, customer_name)
        for customer_id, customer_name in customers:
            # Append a dictionary for each customer to the result list
            response_data.append({
                'customer_id': customer_id, 
                'customer_name': customer_name
            })
            
        # Return the structured response data containing all customers
        return response_data