from abc import ABC, abstractmethod

class IDimensionService(ABC):
    @abstractmethod
    def add_dimension_and_mapping(self, customer_uuid, application_uuid, user_uuid,  validated_data):
        """
        Adds a new dimension and its mapping for a given customer and application.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param user_uuid: The UUID of the user.
        :param validated_data: The validated data for the dimension and mapping.

        :return: A success message on success, or an error message on failure.
        """

    @abstractmethod
    def get_dimensions_by_dimension_type(self, customer_uuid, application_uuid, dimension_type_uuid,paginated_params):
        """
        Retrieves all dimensions associated with a given dimension type.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param dimension_type_uuid: The UUID of the dimension type.

        :return: A list of Dimension instances.
        """

    @abstractmethod
    def get_dimension_mapping_by_id(self, customer_uuid, application_uuid, mapping_uuid):
        """
        Retrieves a dimension type mapping by its mapping UUID.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param mapping_uuid: The UUID of the dimension type mapping.

        :return: The DimensionTypeCustomerApplicationMapping instance if found, or None if not found.
        """

    @abstractmethod
    def get_geography_dimensions(self, customer_uuid, application_uuid, parent_dimension_uuid):
        """
        Retrieves geography dimensions based on the specified parent dimension.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param parent_dimension_uuid: The UUID of the parent dimension (optional).

        :return: A list of Dimension instances representing geography dimensions.
        """

    @abstractmethod
    def get_countries_or_states(self, parent_dimension_uuid):
        """
        Retrieves countries or states based on the specified parent dimension.

        :param parent_dimension_uuid: The UUID of the parent dimension (optional).

        :return: A list of Dimension instances representing countries or states.
        """


    @abstractmethod
    def delete_dimension_mapping(self, customer_uuid, application_uuid, user_uuid,  mapping_uuid):
        """
        Deletes a dimension type mapping.

        :param customer_uuid: The UUID of the customer.
        :param application_uuid: The UUID of the application.
        :param user_uuid: The UUID of the user.
        :param mapping_uuid: The UUID of the dimension type mapping.

        :return: A success message on success, or an error message on failure.
        """

    @abstractmethod
    def upload_intent_utterances_to_chroma_server(self, mapping_uuid,dimensions_details_json,application_uuid, customer_uuid, utterances,metadata):
        """
        Uploads intent utterances to the Chroma server.

        :param application_uuid: The UUID of the application.
        :param customer_uuid: The UUID of the customer.
        :param user_uuid: The UUID of the user.
        :param utterances: A list of utterance strings.
        :param intent_uuid: The UUID of the intent.
        :param intent_name: The name of the intent.

        :return: A success message on success, or an error message on failure.
        """

    @abstractmethod
    def update_intent_utterances_to_chroma_server(self, parent_dimension_mapping,application_uuid, customer_uuid, utterances,child_dimension_mapping,child_dimension_name,parent_dimension_name=None):
        """
        Updates intent utterances in the Chroma server.

        :param application_uuid: The UUID of the application.
        :param customer_uuid: The UUID of the customer.
        :param user_uuid: The UUID of the user.
        :param utterances: A list of utterance strings.
        :param intent_uuid: The UUID of the intent.
        :param intent_name: The name of the intent.

        :return: A success message on success, or an error message on failure.
        """
