from abc import ABC, abstractmethod


class IDimensionDao(ABC):


    def fetch_parent_and_child_dimension_details(self,customer_uuid,application_uuid,parent_dimension_type_name):
        """
        Fetches parent and child dimensions names and description from dimensions view
        Args:
            customer_uuid:
            application_uuid:
            parent_dimension_type_name:

        Returns:

        """
        pass