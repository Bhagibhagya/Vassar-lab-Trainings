from abc import ABC, abstractmethod

class IDimensionTypeDao(ABC):
    @abstractmethod
    def get_default_dimension_types(self):
        """
        Retrieves all default dimension types.

        :return: A list of DimensionType instances.
        """

    @abstractmethod
    def get_default_dimensions(self, dimension_type_uuid):
        """
        Retrieves all default dimensions for a given dimension type.

        :param dimension_type_uuid: The UUID of the dimension type.
        :return: A list of Dimension instances.
        """

    @abstractmethod
    def save_dimension_type(self, dimension_type):
        """
        Saves a dimension type to the database.

        :param dimension_type: The DimensionType instance to save.
        """

    @abstractmethod
    def bulk_create_dimensions(self, dimension_mappings):
        """
        Bulk creates a list of dimension mappings.

        :param dimension_mappings: A list of DimensionCustomerApplicationMapping instances.
        """

    @abstractmethod
    def get_or_create_dimension_type(self, dimension_type_name, user_id):
        """
        Retrieves or creates a DimensionType instance.

        :param dimension_type_name: The name of the dimension type.
        :param user_id: The ID of the user creating or retrieving the dimension type.
        :return: A tuple (DimensionType instance, created), where 'created' is a boolean indicating if a new instance was created.
        """
