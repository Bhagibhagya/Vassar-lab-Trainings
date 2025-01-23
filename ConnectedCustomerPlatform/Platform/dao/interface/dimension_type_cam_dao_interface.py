from abc import ABC, abstractmethod

class IDimensionTypeCAMDao(ABC):

    @abstractmethod
    def get_mapped_dimension_type_by_id_or_all(self, customer_uuid, application_uuid, mapping_uuid=None):
        """
        Retrieves a dimension type mapping by mapping UUID with joined data or all mappings for customer-application.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param mapping_uuid: The UUID of the mapping (optional).

        :return: The DimensionTypeCustomerApplicationMapping instance with joined data, or list of mappings.
        """

    @abstractmethod
    def save_dimension_type_mapping(self, dimension_type_mapping):
        """
        Saves a dimension type mapping to the database.

        :param dimension_type_mapping: The DimensionTypeCustomerApplicationMapping instance to save.
        """

    @abstractmethod
    def delete_dimension_type_mapping(self, customer_uuid, application_uuid, mapping_uuid):
        """
        Deletes a dimension type mapping.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param mapping_uuid: The DimensionTypeCustomerApplicationMapping uuid to delete.
        """
