from abc import ABC, abstractmethod


class IEmailSettingsService(ABC):
    @abstractmethod
    def add_email_settings(self, customer_uuid, application_uuid, user_id, email_settings):
        """
            Creates new user email settings in the database.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param user_id: The unique identifier of the user performing the operation.
            :param email_settings: A dictionary containing the email settings data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_email_settings(self, customer_uuid, application_uuid):
        """
            Fetches all email settings or filters them by email type for the specified application.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :return: A list of UserEmailSettings matching the criteria.
        """

    @abstractmethod
    def edit_email_settings(self, customer_uuid, application_uuid, user_id, email_settings):
        """
            Updates existing user email settings in the database.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param user_id: The unique identifier of the user performing the operation.
            :param email_settings: A dictionary containing the updated email settings data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def delete_email_settings(self, customer_uuid, application_uuid, user_email_uuid, user_uuid):
        """
            Deletes user email settings from the database.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param user_email_uuid: The unique identifier of the user email settings to be deleted.
            :param user_uuid: The unique identifier of the user performing the operation.
            :return: None
        """

    @abstractmethod
    def test_connection_gmail(self, email_uuid, server_url, port, email, password, use_ssl, is_encrypted):
        """
            Tests IMAP connection for Gmail or Outlook
            :param email_uuid: uuid of user email setting
            :param server_url: url of IMAP server (Gmail and Outlook)
            :param port: IMAP server port
            :param email: email address
            :param password:
            :param use_ssl: is ssl enabled or not
            :param is_encrypted: is password encrypted or not
            :return: Successful response or error message.
        """
    @abstractmethod
    def test_connection_outlook(self,user_email, client_id, tenant_id, client_secret) -> tuple:
        """Test the connection by decoding the access token to check for Mail.Read and Mail.Send permissions.
        :param user_email : Outlook email id of the user
        :param client_id : microsoft client_id
        :param tenant_id: microsoft tenant id
        :param client_secret: microsoft client secret

        Returns a message with status code
        """

