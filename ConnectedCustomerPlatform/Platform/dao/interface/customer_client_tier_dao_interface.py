from abc import ABC, abstractmethod


class ICustomerClientTierDao(ABC):

    @abstractmethod
    def save_customer_client_tier_mapping(self,customer_client_tier):
        """
            Saves customer client tier object in the database.
            :param customer_client: The customer client tier instance object to be created.
            :return: can raise an exception.
        """

    @abstractmethod
    def delete_customer_client_tier_mapping(self,mapping_uuid):
        """
            Deletes customer client tier object from the database.
            :param mapping_uuid:
            :return: can raise an exception
        """

    @abstractmethod
    def get_customer_client_by_tier_mapping(self,tier_mapping_uuid):
        """
        get_customer_client_by_mapping_tier
        :param tier_mapping_uuid:
        :return:can raise an exception
        """

    @abstractmethod
    def get_customer_client_list_by_exclude_customer_client_list(self,application_uuid,customer_uuid):

        """
        :param application_uuid:
        :param customer_uuid:
        :return: A list of dictionaries containing customer client details, excluding those
                present in the tier mapping.
        """