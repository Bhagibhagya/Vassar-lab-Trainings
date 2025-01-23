import inspect
import logging

from ChatBot.dao.interface.customer_dao_interface import ICustomerDao

from ChatBot.dataclasses.customer_data import CustomerData

from DatabaseApp.models import Customers

logger = logging.getLogger(__name__)


class CustomerDaoImpl(ICustomerDao):
    """
            Data Access Object (DAO) for Customer operations.
            Implements the Singleton pattern to ensure only one instance of this class is created.
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(CustomerDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
                Initialize the CustomerDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside CustomerDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def create_customer(self, customer_data: CustomerData):
        """
            create a customer record in user customer table
            Args:
                customer_data (CustomerData): CustomerData dataclass instance
            Returns:
                returns created customer queryset
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.info(f"creating a customer:: customer_data :: {customer_data.to_dict()}")
        # Use the CustomerData fields to create a new Customer record
        customer_create_response = Customers.objects.create(
            cust_uuid=customer_data.customer_uuid,
            cust_name=customer_data.customer_name,
            purchased_plan=customer_data.purchased_plan,
            email=customer_data.email,
            primary_contact=customer_data.primary_contact,
            secondary_contact=customer_data.secondary_contact,
            address=customer_data.address,
            billing_address=customer_data.billing_address,
            customer_details_json=customer_data.customer_details_json,
            status=customer_data.status,
            created_by=customer_data.created_by,
            updated_by=customer_data.updated_by
        )
        return customer_create_response
