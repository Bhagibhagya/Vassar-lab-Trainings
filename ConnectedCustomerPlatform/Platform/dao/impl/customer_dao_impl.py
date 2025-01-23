import logging

from DatabaseApp.models import Customers
from Platform.dao.interface.customer_dao_interface import ICustomerDAO
logger = logging.getLogger(__name__)

class CustomerDaoImpl(ICustomerDAO):
    """
    Data Access Object (DAO) for customer operations.
    Implements the Singleton pattern to ensure only one instance of this class is created.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(CustomerDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of CustomerDao")
        return cls._instance
    
    def __init__(self, **kwargs):
        """
        Initialize the CustomerDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside CustomerDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_customers_id_and_name(self):
        """
        Retrieve the customers Id and name from customers table.
        """
        return Customers.objects.values_list('cust_uuid','cust_name')