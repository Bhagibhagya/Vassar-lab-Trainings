from abc import ABC, abstractmethod

class IDimensionDao(ABC):
    @abstractmethod
    def get_or_create_dimension(self, dimension_name, dimension_type_uuid, user_uuid):
        """
        Gets or creates a dimension.

        :param dimension_name: The name of the dimension.
        :param dimension_type_uuid: The UUID of the dimension type.
        :param user_uuid: The UUID of the user.

        :return: A tuple containing the Dimension instance and a boolean indicating whether it was created (True) or retrieved (False).
        """

    @abstractmethod
    def get_countries_or_states(self, country_id):
        """
        Retrieves countries or states based on the specified parent dimension.

        :param country_id: The UUID of the parent dimension (optional).

        :return: A list of Dimension instances representing countries or states.
        """

    @abstractmethod
    def fetch_parent_and_child_dimension_details(self, customer_uuid, application_uuid, parent_dimension_type_uuid):
        """
            fetch_parent_and_child_dimension_details
        """

