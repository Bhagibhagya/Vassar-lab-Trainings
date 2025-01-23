from abc import ABC, abstractmethod
from typing import Set


class IDimensionCAMDao(ABC):
    @abstractmethod
    def save_dimension_mapping(self, dimension_mapping):
        """
        Saves a dimension type mapping to the database.

        :param dimension_mapping: The DimensionTypeCustomerApplicationMapping instance to save.
        """

    @abstractmethod
    def get_or_create_dimension_mapping(self, uuid_data, validated_data, dimension, parent_dimension=None):
        """
        Gets or creates a dimension mapping.

        :param uuid_data: A tuple containing the customer UUID, application UUID, and user ID.
        :param validated_data: A dictionary containing validated data for the dimension mapping.
        :param dimension: The Dimension instance associated with the mapping.
        :param parent_dimension: The parent dimension (optional).

        :return: The DimensionCustomerApplicationMapping instance.
        """

    @abstractmethod
    def get_dimensions_by_dimension_type(self, customer_uuid, application_uuid, dimension_type_uuid):
        """
        Retrieves all dimensions associated with a given dimension type.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param dimension_type_uuid: The UUID of the dimension type.

        :return: A list of Dimension instances.
        """

    @abstractmethod
    def get_dimension_mapping_by_id(self, customer_uuid, application_uuid, mapping_uuid, fetch_is_parent=False):
        """
        Retrieves a dimension type mapping by its mapping UUID.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param mapping_uuid: The UUID of the dimension type mapping.
        :param fetch_is_parent: To retrieve whether the dimension is parent or not (optional).

        :return: The DimensionTypeCustomerApplicationMapping instance if found, or None if not found.
        """

    @abstractmethod
    def get_geography_dimensions(self, customer_uuid, application_uuid, parent_dimension_uuid=None):
        """
        Retrieves geography dimensions based on the specified parent dimension.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param parent_dimension_uuid: The UUID of the parent dimension (optional).

        :return: A list of Dimension instances representing geography dimensions.
        """

    @abstractmethod
    def get_dimensions_for_scope_by_dimension_type_name(self, customer_uuid, application_uuid, dimension_type_name):
        """
        Retrieves dimensions for a specific scope based on the dimension type name for the given customer and application.

        :param customer_uuid: UUID of the customer to filter dimensions.
        :param application_uuid: UUID of the application to filter dimensions.
        :param dimension_type_name: The name of the dimension type (e.g., 'GEOGRAPHY', 'INTENT', etc.) to filter dimensions.
        :return: A list of dictionaries containing dimension details such as 'dimension_uuid' and 'dimension_name'.
        """

    @abstractmethod
    def get_entities_for_scope_by_application_uuid(self, customer_uuid, application_uuid):
        """
        Retrieves Entities for a specific scope for the given customer and application.

        :param customer_uuid: UUID of the customer to filter dimensions.
        :param application_uuid: UUID of the application to filter dimensions.
        :return: A list of dictionaries containing Entities details such as 'entity_uuid' and 'entity_name'.
        """

    @abstractmethod
    def delete_dimension_mapping(self, dimension_mapping):
        """
        Deletes a dimension type mapping.

        :param dimension_mapping: The DimensionTypeCustomerApplicationMapping instance to delete.
        """

    @abstractmethod
    def delete_dimension_from_user_scope(self,dimension_uuid,application_uuid,customer_uuid):
        """
        Delete the dimension from user_scope in usermgmt

        :param dimension_uuid : The dimension uuid to be deleted from user scope.
        :param customer_uuid: UUID of the customer to filter users.
        :param application_uuid: UUID of the application to filter users.
        """

    @abstractmethod
    def fetch_dimension_mappings_with_dimension_names(self, application_uuid : str, customer_uuid : str, dimension_names : Set[str]):
        """
                Fetch dimension mappings and organize them into a dictionary in a single ORM call.

                Args:
                    application_uuid (str): The application UUID.
                    customer_uuid (str): The customer UUID.
                    dimension_names (set): Set of dimension names to filter.

                Returns:
                    dict: A dictionary mapping (parent_dimension_name, child_dimension_name) to mapping objects.
        """
        ...

    @abstractmethod
    def perform_bulk_update(self, dimension_updates : list):
        """
            Performs a bulk update on DimensionCustomerApplicationMapping objects.

            Updates the `dimension_details_json` and `updated_ts` fields for the given list of
            DimensionCustomerApplicationMapping objects in a single query.

            Args:
                dimension_updates (list): List of objects to be updated with new values.

            Returns:
                None
        """
        ...


    @abstractmethod
    def update_dimension_details_json_in_dimension_mapping(self, mapping_uuid, dimension_details_json):
        """
        updates email_activity in email_conversation
        Args:
            mapping_uuid:
            dimension_details_json:

        Returns:

        """
        pass

    @abstractmethod
    def fetch_dimension_mapping_by_parent_child_names(self, customer_uuid, application_uuid, parent_dimension_name,
                                                      child_dimension_name):
        """
        Fetch dimension mapping based on customer, application, and dimension names.

        Args:
            customer_uuid: UUID of the customer
            application_uuid: UUID of the application
            parent_dimension_name: Name of the parent dimension (can be None)
            child_dimension_name: Name of the child dimension

        Returns:
            DimensionCustomerApplicationMapping object
        """
        pass

    @abstractmethod
    def fetch_dimension_name_by_mapping_uuid(self,mapping_uuid):
        pass


    @abstractmethod
    def fetch_dimension_parent_dimension_name_by_dimension_uuid(self,mapping_uuid,customer_uuid,application_uuid):
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

    @abstractmethod
    def delete_dimension_mappings(self, parent_dimension_uuid, customer_uuid, application_uuid):
        """
        Deletes all records in DimensionCustomerApplicationMapping that match the given
        parent_dimension_uuid, customer_uuid, and application_uuid.

        Args:
            parent_dimension_uuid (str): The UUID of the parent dimension.
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            int: Number of records deleted.
        """

    def delete_parent_dimension_mappings(self, parent_dimension_uuid, dimension_type_name, customer_uuid, application_uuid):
        """
        Deletes parent dimensions of a specific type for a given customer and application.
    
        Args:
            parent_dimension_uuid (str): The UUID of the parent dimension to delete.
            dimension_type_name (str): The name of the dimension type.
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.
        """
        

    @abstractmethod
    def update_parent_dimension_in_dimension_mapping(self, parent_dimension_uuid,updated_parent_dimension_uuid,customer_uuid,application_uuid):
        """
        updates parent_dimension
        Args:
            parent_dimension_uuid:
            customer_uuid:
            application_uuid:

        Returns:

        """
