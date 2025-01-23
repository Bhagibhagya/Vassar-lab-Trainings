from abc import ABC, abstractmethod
class IDimensionTypeDao(ABC):
    @abstractmethod
    def get_dimension_type_uuid_by_name(dimension_type_name : str,customer_uuid : str,application_uuid : str)->str:
        """
        returns dimension_type_uuid by dimension_type_name for given customer_uuid and application_uuid
        """
        pass
