from abc import ABC, abstractmethod


class IEmailServerService(ABC):
    @abstractmethod
    def add_email_server(self, customer_uuid, application_uuid, user_id, server_data):
        """
            Adds a new email server entry to the database.
            :param customer_uuid: UUID of the customer.
            :param application_uuid: UUID of the application.
            :param user_id: ID of the user performing the action.
            :param server_data: Data for the new email server.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_email_server(self, customer_uuid, application_uuid):
        """
            Fetches the email server settings for a specific customer-application.

            :param customer_uuid: UUID of the customer.
            :param application_uuid: UUID of the application.
            :return: Email server settings for the specified customer-application.
        """

    @abstractmethod
    def edit_email_server(self, customer_uuid, application_uuid, user_id, server_data):
        """
            Updates the details of an existing email server for a specific customer-application.

            :param customer_uuid: UUID of the customer.
            :param application_uuid: UUID of the application.
            :param user_id: ID of the user making the update.
            :param server_data: Data containing the updated email server details.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_outlook_server(self, customer_uuid, application_uuid):
        """
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns configured outlook server details
        """

    @abstractmethod
    def save_outlook_server(self, customer_uuid, application_uuid, user_uuid, email_server_data, update=False):
        """
        Save (create or update) an Outlook server for the given customer, application, and user.
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param user_uuid: UUID of the user making the request.
        :param email_server_data: Dictionary containing email server data.
        :param update: Boolean flag indicating if it's an update operation (True for update, False for add).
        Returns Success message or error message
        """

    @abstractmethod
    def delete_email_server(self,customer_uuid,application_uuid,user_uuid):
        """Deletes all email server and user_email_setting for customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param user_uuid:UUID of logged in user
        Returns Success message or error message
        """

    @abstractmethod
    def get_server_provider_name(self,customer_uuid,application_uuid):
        """
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        Returns provider name for email server"""