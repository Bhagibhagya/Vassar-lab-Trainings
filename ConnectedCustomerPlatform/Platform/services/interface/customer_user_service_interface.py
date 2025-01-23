from abc import ABC, abstractmethod


class ICustomerUserService(ABC):

    @abstractmethod
    def add_customer_user(self, data , user_uuid):
        """
            Creates new customer user in the database.
            :param user_uuid: The unique identifier of the user performing the operation.
            :param data: A dictionary containing the customer user data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def edit_customer_user(self,data,user_uuid):
        """
            Edits the existing customer user in the database.
            :param user_uuid: The unique identifier of the user performing the operation.
            :param data: A dictionary containing the customer user data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_customer_users(self, customer_client_uuid, customer_uuid):
        """
            :param customer_uuid: UUID of the customer.
            :param customer_client_uuid: uuid of customer client whose users need to be fetched
            :return:list of customer client users
        """

    @abstractmethod
    def delete_customer_user(self,client_user_uuid, user_uuid):
        """
            :param client_user_uuid: uuid of the customer client user to be deleted
            :param user_uuid: uuid of the user who deleting the customer client user
            :return: Number of rows updated (i.e., customer user marked as deleted)
        """