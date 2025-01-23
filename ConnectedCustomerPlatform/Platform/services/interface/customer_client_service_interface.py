from abc import ABC, abstractmethod


class ICustomerClientService(ABC):

    @abstractmethod
    def add_customer_client(self, customer_uuid, user_id, data):
        """
            Creates new customer client in the database.
            :param customer_uuid: The unique identifier of the customer.
            :param user_id: The unique identifier of the user performing the operation.
            :param data: A dictionary containing the customer client data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def edit_customer_client(self, customer_uuid, user_id, data):
        """
            Edits the existing customer client in the database.
            :param customer_uuid: The unique identifier of the customer.
            :param user_id: The unique identifier of the user performing the operation.
            :param data: A dictionary containing the customer clients data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_customer_client(self, customer_uuid):
        """
            gets the existing customer client in the database.
            :param customer_uuid:
            :return:A response containing the customer client details.
        """

    @abstractmethod
    def delete_customer_client(self,customer_client_uuid, user_id):
        """
            :param customer_client_uuid:
            :param user_id:
            :return: Number of rows updated (i.e., customer client marked as deleted)
        """