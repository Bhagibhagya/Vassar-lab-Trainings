from abc import ABC, abstractmethod

class IDimensionsIntentDao(ABC):
    """
    Interface for Intent Data Access Object (DAO)
    """
    @abstractmethod
    def get_all_dimensions_by_dimension_type_name(self, dimension_type_name,application_uuid,customer_uuid):
        """
        :param dimension_type_name:
        :param application_uuid:
        :param customer_uuid:
        :return: A list of dimensions matching the given dimension type name, application, and customer.
        """