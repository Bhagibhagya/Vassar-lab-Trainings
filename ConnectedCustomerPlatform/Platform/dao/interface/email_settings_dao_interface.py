from abc import ABC, abstractmethod

class IEmailSettingsDao(ABC):
    """Interface for UserEmailSetting model."""
    @abstractmethod
    def get_user_email_settings_by_email_id(self, email_id, customer_uuid=None, application_uuid=None):
        """
            Fetches user email settings based on the provided username (email address).

            :param email_id: The email address whose settings are to be fetched.
            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :return: An instance of UserEmailSettings if found, otherwise None.
        """

    @abstractmethod
    def get_user_email_settings(self, customer_uuid, application_uuid, email_type=None):
        """
            Fetches user email settings for a specific customer-application, optionally filtered by email type.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :param email_type: (Optional) The type of email settings to filter by.
            :return: A queryset of UserEmailSettings matching the criteria.
        """

    @abstractmethod
    def get_user_email_settings_by_id(self, email_setting_uuid, customer_uuid=None, application_uuid=None):
        """
            Fetches a single user email setting by its UUID.

            :param email_setting_uuid: The unique identifier of the user email setting.
            :param customer_uuid: (Optional) The unique identifier of the customer.
            :param application_uuid: (Optional) The unique identifier of the application.
            :return: An instance of UserEmailSettings if found, otherwise None.
        """

    @abstractmethod
    def deactivate_primary_senders(self, customer_uuid, application_uuid):
        """
            Deactivates primary sender email settings for the specified customer-application.

            :param customer_uuid: The unique identifier of the customer.
            :param application_uuid: The unique identifier of the application.
            :return: None
        """

    @abstractmethod
    def save_user_email_settings(self, user_email_settings):
        """
            Saves the provided user email settings object in the database.

            :param user_email_settings: An instance of UserEmailSettings to be saved.
            :return: The saved instance of UserEmailSettings.
        """

    @abstractmethod
    def delete_user_email_settings(self, user_email_settings, user_uuid):
        """
            Deletes the specified user email settings from the database.

            :param user_email_settings: An instance of UserEmailSettings to be deleted.
            :param user_uuid: The unique identifier of the user performing the operation.
            :return: None
        """

    @abstractmethod
    def check_email_association_with_group(self, customer_uuid, application_uuid, email_id):
        """
        Checks if the given individual email is associated with any group email settings for the specified customer and application.

        :param customer_uuid: The UUID of the customer to check for group email settings.
        :param application_uuid: The UUID of the application associated with the group email settings.
        :param email_id: The email address (ID) to check for association with any group email settings.

        :return: True if the email is associated with any group email setting for the specified customer and application;
                 False otherwise.
        """

    @abstractmethod
    def delete_all_mapped_user_email_settings(self, customer_uuid, application_uuid, user_uuid):
        """
        Soft delete all user email setting for the customer and application

        :param customer_uuid: The UUID of the customer to check for group email settings.
        :param application_uuid: The UUID of the application associated with the group email settings.
        :param user_uuid: The UUID of logged in user

        Raises Exception is not able to delete
        """
