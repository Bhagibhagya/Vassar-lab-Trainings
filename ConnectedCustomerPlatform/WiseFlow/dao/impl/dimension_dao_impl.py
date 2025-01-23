import logging

from WiseFlow.dao.interface.dimension_dao_interface import IDimensionDao
from DatabaseApp.models import DimensionsView

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class DimensionDaoImpl(IDimensionDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DimensionDaoImpl, cls).__new__(cls)
        return cls._instance


    def fetch_parent_and_child_dimension_details(self,customer_uuid,application_uuid,parent_dimension_type_name):
        logger.info("In DimensionDaoImpl :: fetch_parent_and_child_dimension_details")
        try:
            return DimensionsView.objects.filter(customer_uuid=customer_uuid,application_uuid=application_uuid,dimension_type_name=parent_dimension_type_name)

        except Exception as e:
            logger.exception(f"Error in fetching parent and child dimensions :: {e}")
            raise