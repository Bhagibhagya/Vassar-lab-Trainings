from abc import ABC, abstractmethod


class ICustomerClientTierService(ABC):

    @abstractmethod
    def add_customer_client_tier_mapping(self,user_uuid, data):
        """
        :param user_uuid:
        :param data:
        :return: - A custom success response if the mapping is added successfully.
        """

    @abstractmethod
    def delete_customer_client_tier_mapping(self,mapping_uuid):
        """
        Request (HttpRequest): The request object containing headers.
        :param mapping_uuid (str): The unique identifier of the mapping to delete
        """

    @abstractmethod
    def get_customers_client_by_tier_mapping(self,tier_mapping_uuid):
        """
        get list of customer_client_tier
        :param tier_mapping_uuid:
        :return:A list of customer clients linked to the specified tier mapping.
        """

    @abstractmethod
    def edit_customer_client_tier_mapping(self,user_uuid, data):
        """
        :param user_uuid:
        :param data:
        :return:Success message if the update is successful.
        """

    @abstractmethod
    def get_customer_client_dropdown_in_tier(self,application_uuid,customer_uuid):
        """
            Retrieves customer clients not already mapped to a tier under the given
            application and customer.

            :param application_uuid: The UUID of the application.
            :param customer_uuid: The UUID of the customer.
            :return: List of customer-client data excluding already mapped ones.
        """
