from abc import ABC, abstractmethod

class IDimensionTypeService(ABC):
    @abstractmethod
    def add_dimension_type(self, customer_uuid, application_uuid, user_id, dimension_type_data):
        """
        Adds a new dimension type and map it to the customer-application.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param user_id: The ID of the user creating the dimension type.
        :param dimension_type_data: A dictionary containing the dimension type data.

        :return: Successful response, or an error message on failure.
        """

    @abstractmethod
    def get_dimension_types(self, customer_uuid, application_uuid):
        """
        Retrieves all dimension types for a given customer and application.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.

        :return: A list of DimensionType instances.
        """

    @abstractmethod
    def get_dimension_type_by_id(self, customer_uuid, application_uuid, mapping_uuid):
        """
        Retrieves a dimension type by its mapping UUID.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid : The UUID of the application.
        :param mapping_uuid : The UUID of the dimension type mapping.

        :return: The DimensionType instance if found, or None if not found.
        """

    @abstractmethod
    def edit_dimension_type(self, customer_uuid, application_uuid, user_id, dimension_type_data):
        """
        Edits an existing dimension type.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param user_id: The ID of the user updating the dimension type.
        :param dimension_type_data: The updated dimension type data.

        :return: Successful response, or an error message on failure.
        """

    @abstractmethod
    def edit_status_for_default_types(self, headers, dimension_type_data):
        """
        Edits the status of default dimension types and maps default dimension values to this dimension type.

        :param headers: A tuple containing the customer UUID, application UUID, and user ID.
        :param dimension_type_data: The updated dimension type data.

        :return: Successful response, or an error message on failure.
        """

    @abstractmethod
    def delete_dimension_type_mapping(self, customer_uuid, application_uuid, mapping_uuid):
        """
        Deletes a dimension type mapping.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param mapping_uuid: The UUID of the dimension type mapping.

        :return: Successful response, or an error message on failure.
        """
