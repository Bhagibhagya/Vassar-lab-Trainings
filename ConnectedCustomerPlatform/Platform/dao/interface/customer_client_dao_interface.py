from abc import ABC, abstractmethod


class ICustomerClientDao(ABC):

    @abstractmethod
    def save_customer_client(self, customer_client):
        """
            Saves customer client object in the database.
            :param customer_client: The customer client instance object to be created.
            :return: can raise an exception.
        """

    @abstractmethod
    def delete_customer_client_by_customer_client_id(self,customer_client_uuid, user_id):
        """
            :param customer_client_uuid:
            :param user_id:
            :return: Number of rows updated (i.e., customer client marked as deleted)
        """

    @abstractmethod
    def get_customers_by_customer_uuid(self,customer_uuid):
        """

        :param customer_uuid:
        :return:  return customer client object list
        """

    @abstractmethod
    def get_customer_client_by_customer_client_uuid(self, customer_client_uuid):
        """
        :param customer_client_uuid:
        :return: return customer client object.
        """