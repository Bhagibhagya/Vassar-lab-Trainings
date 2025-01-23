from ChatBot.dao.interface.customer_application_mapping_dao_interface import ICustomerApplicationMappingDao
from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException
from DatabaseApp.models import CustomerApplicationMapping

import logging
logger = logging.getLogger(__name__)


class CustomerApplicationMappingDaoImpl(ICustomerApplicationMappingDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerApplicationMappingDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.initialized = True
            logger.info("CustomerApplicationMappingDaoImpl initialized")

    def get_customer_application_mapping_id(self, customer_uuid, application_uuid):
        """get customer application mapping id for given customer uuid and application uuid"""
        cam_id = CustomerApplicationMapping.objects.filter(customer_id=customer_uuid, application_id=application_uuid).values_list('customer_application_id', flat=True).first()
        # Check if the mapping ID was found; if not, raise an exception
        if cam_id is None:
            logger.error(f"Customer Application Mapping UUID not found for customer UUID '{customer_uuid}' and application UUID '{application_uuid}'.")
            raise ResourceNotFoundException("Customer Application Mapping UUID not found for the given customer and application UUIDs.")
        return cam_id