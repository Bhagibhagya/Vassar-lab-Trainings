import logging

from ChatBot.services.interface.dimensions_intents_service_interface import IDimensionsIntentsService
from ChatBot.dao.impl.dimensions_intent_dao_impl import DimensionsIntentDaoImpl

logger = logging.getLogger(__name__)

class DimensionsIntentServiceImpl(IDimensionsIntentsService):
    """
    Singleton class for handling IntentService related operations.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DimensionsIntentServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.dimensions_intent_dao = DimensionsIntentDaoImpl()  # Assuming an IntentDaoImpl class is defined elsewhere
            logger.info(f"Inside IntentServiceImpl - Singleton Instance ID: {id(self)}")
            print(f"Inside IntentServiceImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_all_dimensions_by_dimension_type_name(self, dimension_type_name,application_uuid,customer_uuid):
        """
            Fetches all dimensions associated with a specific dimension type name for a given application and customer.

            :param dimension_type_name: The name of the dimension type (e.g., 'INTENT').
            :param application_uuid: The unique identifier for the application.
            :param customer_uuid: The unique identifier for the customer.
            :return: A list of dimensions matching the given dimension type name, application, and customer.
        """
        logger.info(f"Fetching dimensions for dimension type: {dimension_type_name}")
        logger.debug(f"Application UUID: {application_uuid}, Customer UUID: {customer_uuid}")

        # Fetch dimensions from DAO
        dimensions = self.dimensions_intent_dao.get_all_dimensions_by_dimension_type_name(
            dimension_type_name, application_uuid, customer_uuid
        )

        # Log the fetched dimensions
        logger.debug(f"Fetched dimensions: {dimensions}")

        # Return the dimensions
        return dimensions