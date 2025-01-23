from abc import ABC, abstractmethod
from typing import Any, List,Dict
class IDimensionDaoInterface(ABC):

    @abstractmethod
    def get_dimensions_list_by_dimension_type_name(self, dimension_type_name: str, customer_uuid: str,application_uuid: str) -> List:
        """
        Gets dimensions names list for specific application and customer by dimension_type_name
        """
        pass
    @abstractmethod
    def get_intent_subintents_for_customer_application(self,customer_uuid:str,application_uuid:str) -> Dict[str,List]:
        """
        dao for getting intents and sub_intents for the perticular customer and application
        """
        pass
    @abstractmethod
    def get_dimension_uuid_dimension_name_description(self,customer_uuid:str,application_uuid:str,dimension_type_name:str) -> List[Any]:
        """
        Gets dimension_uuid,dimension_name, description details list for specific application and customer by dimension_type_name
        """
        pass
    @abstractmethod
    def get_mapping_dimension_uuid_dimension_name_list(self,dimension_type_name : str,customer_uuid : str,application_uuid :str) ->List[Any]:
        """
        Gets mapping_uuid, dimension_uuid, dimension_name details list for specific application and customer by dimension_type_name
        """
        pass

    @abstractmethod
    def update_description_of_dimension(self,mapping_uuid, new_description,updated_by):
        """Update the description for the given mapping_uuid"""
        pass

    @abstractmethod
    def fetch_dimension_parent_dimension_name_by_dimension_uuid(self,dimension_uuid,customer_uuid,application_uuid):
        """
        Fetches the names of a dimension and its parent dimension based on the given dimension UUID,
        customer UUID, and application UUID.

        Args:
            dimension_uuid (str): The unique identifier of the dimension.
            customer_uuid (str): The unique identifier of the customer.
            application_uuid (str): The unique identifier of the application.

        Returns:
            tuple: A tuple containing the names of the dimension and its parent dimension if found,
                   or None if no matching record is found.

        Raises:
            CustomException: If an exception occurs during the query execution.
        """
        pass

    @abstractmethod
    def fetch_parent_and_child_dimension_details(self, customer_uuid, application_uuid, parent_dimension_type_name):
        """
        Fetches parent and child dimensions names and description from dimensions view
        Args:
            customer_uuid:
            application_uuid:
            parent_dimension_type_name:

        Returns:

        """
        pass

    @abstractmethod
    def reduce_training_phrase_count_for_dimensions(self, dimension_names,parent_dimension_name, customer_uuid, application_uuid):
        """
        Reduces the training_phrases_count by 1 for specified dimension names (case insensitive).

        Args:
            dimension_names (list): List of dimension names to update
            parent_dimension_name
            customer_uuid: UUID of the customer
            application_uuid: UUID of the application

        Returns:
            int: Number of records updated
        """
        pass