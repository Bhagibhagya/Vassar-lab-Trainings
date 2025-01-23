from abc import ABC, abstractmethod
from typing import List
class ICustomerApplicationMappingDaoInterface(ABC):

    @abstractmethod
    def get_cust_app_mapping_uuid(self, customer_uuid: str,application_uuid: str) -> List:
        """
        Gets customer_application_mapping_uuid for specific application and customer
        """
        pass