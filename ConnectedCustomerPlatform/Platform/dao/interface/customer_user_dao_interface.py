from abc import ABC, abstractmethod


class ICustomerUserDao(ABC):

    @abstractmethod
    def save_customer_user(self, customer_user):
        """
            Saves customer user object in the database.
            :param customer_user: The customer user instance object to be created.
            :return: can raise an exception.
        """

    @abstractmethod
    def delete_customer_user_by_id(self,customer_user_uuid, user_uuid):
        """
            :param customer_user_uuid:
            :param user_uuid:
            :return: Number of rows updated (i.e., customer user marked as deleted)
        """

    @abstractmethod
    def get_customer_users_by_customer_client_uuid(self, customer_client_uuid, customer_uuid):
        """

        :param customer_uuid:
        :param customer_client_uuid:
        :return:  return customer client object list
        """

    @abstractmethod
    def update_customer_user(self,client_user_uuid,first_name,last_name,email_id,user_info_json_dict,customer_client_uuid,geography_uuid,user_uuid):
        """
            :param client_user_uuid : unique identifier of customer client user
            :param first_name : updated customer_client_user first_name
            :param last_name : updated customer_client_user last_name
            :param email_id : updated customer_client_user email_id
            :param user_info_json_dict : updated customer_client_user user_info_json
            :param customer_client_uuid : uuid of the customer client under whom user is.
            :param geography_uuid : updated geography
            :param user_uuid : uuid of user who updating the customer client user
        """