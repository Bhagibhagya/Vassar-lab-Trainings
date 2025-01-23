import logging

from DatabaseApp.models import CustomerApplicationMapping
from EmailApp.dao.interface.customer_application_mapping_dao_interface import ICustomerApplicationMappingDaoInterface

logger = logging.getLogger(__name__)

class CustomerApplicationMappingDaoImpl(ICustomerApplicationMappingDaoInterface):

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(CustomerApplicationMappingDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of CustomerApplicationMappingDaoImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the CustomerApplicationMappingDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside CustomerApplicationMappingDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_cust_app_mapping_uuid(self, customer_uuid,application_uuid):
        """
        Get mapping uuid for customer and application
        """
        return CustomerApplicationMapping.objects.filter(customer_id=customer_uuid, application_id=application_uuid).values_list('customer_application_id', flat=True).first()

