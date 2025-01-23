import logging
import uuid
from dataclasses import asdict
import jwt
from django.db import transaction, IntegrityError
from rest_framework import status

from DatabaseApp.models import UserEmailSetting, Customers, Applications
from ConnectedCustomerPlatform.exceptions import CustomException
from EmailApp.constant.constants import OutlookUrlsEndPoints, MicrosoftGraphPermissions
from EmailApp.utils import get_access_token, call_api
from Platform.constant.success_messages import SuccessMessages
from Platform.dao.impl.email_settings_dao_impl import EmailSettingsDaoImpl
from Platform.services.interface.email_settings_service_interface import IEmailSettingsService
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
from Platform.utils import encrypt_password, get_email_provider, decrypt_password, test_imap_connection

logger = logging.getLogger(__name__)

class EmailSettingsServiceImpl(IEmailSettingsService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmailSettingsServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)

            print("Inside EmailSettingsServiceImpl")
            self.email_settings_dao = EmailSettingsDaoImpl()
            print(f"Inside EmailSettingsServiceImpl - Singleton Instance ID: {id(self)}")

            self.initialized = True

    # Inserts a new user email settings record in the database.
    @transaction.atomic
    def add_email_settings(self, customer_uuid, application_uuid, user_uuid, email_settings):
        try:
            headers = (customer_uuid, application_uuid, user_uuid)

            logger.info("Received email settings data: %s", email_settings)

            email_id = email_settings.get('email_id')
            email_type = email_settings.get('email_type')
            cust_email_provider = email_settings.get('cust_email_provider')

            password = email_settings.get('encrypted_password')
            hashed_password = encrypt_password(password)
            if email_type == constants.EMAIL_TYPE_GROUP:
                logger.info("Handling group email")
                hashed_password, email_details_json = self.__handle_primary_email_add(email_settings, headers, hashed_password)

                # Add group email
                logger.info("Adding group email to database")
                self.__add_email_setting(email_id, hashed_password, constants.EMAIL_TYPE_GROUP, headers, cust_email_provider, email_details_json)
            else:
                # If email type is individual
                logger.info("Adding individual email to database")
                self.__add_email_setting(email_id, hashed_password, constants.EMAIL_TYPE_INDIVIDUAL, headers, cust_email_provider)

        except IntegrityError as ie:
            if 'unique constraint' in str(ie):
                raise CustomException(ErrorMessages.EMAIL_EXISTS)
            logger.error("Error adding email: %s", str(ie))
            raise CustomException(ErrorMessages.ADD_EMAIL_FAILED)
        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise CustomException(ErrorMessages.ADD_EMAIL_FAILED)

    # Retrieves email settings from the database based on the specified filters.
    def get_email_settings(self, customer_uuid, application_uuid):
        logger.info(f"Retrieving email settings for customer: {customer_uuid}, application: {application_uuid}")
        user_email_settings = self.email_settings_dao.get_user_email_settings(customer_uuid, application_uuid)

        return user_email_settings

    # Modifies the existing user email settings record in the database.
    @transaction.atomic
    def edit_email_settings(self, customer_uuid, application_uuid, user_uuid, email_settings):
        try:
            headers = (customer_uuid, application_uuid, user_uuid)
            logger.info("Received email settings data: %s", email_settings)
            user_email_uuid = email_settings.get('user_email_uuid')

            # Check if user email settings not found
            user_email_settings = self.email_settings_dao.get_user_email_settings_by_id(user_email_uuid, customer_uuid, application_uuid)
            if user_email_settings is None:
                raise CustomException(ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND)

            email_type = email_settings.get('email_type')
            email_id = email_settings.get('email_id')
            cust_email_provider = email_settings.get('cust_email_provider')

            # Ensure the email address provider matches the provider specified in the channel settings
            self.__validate_email_provider(email_id, cust_email_provider)

            # Avoid updating individual email address if it is associated with any group email
            if user_email_settings.email_id != email_id:
                self.__check_individual_email_association(user_email_settings, headers)

            password = email_settings.get('encrypted_password')
            hashed_password = encrypt_password(password)
            if email_type == constants.EMAIL_TYPE_GROUP:
                hashed_password, email_details_json = self.__handle_primary_email_add(email_settings, headers, hashed_password)

                user_email_settings.email_details_json = email_details_json

            elif password is None:
                # If email type is Individual and password not edited
                logger.info("Password not edited for individual email")
                hashed_password = user_email_settings.encrypted_password

            # Update each field
            self.__update_email_settings(email_settings, headers, user_email_settings, email_id, hashed_password)

            # Save updated instance of user email settings
            logger.info("Saving updated email settings")
            self.email_settings_dao.save_user_email_settings(user_email_settings)

        except IntegrityError as ie:
            if 'unique constraint' in str(ie):
                raise CustomException(ErrorMessages.EMAIL_EXISTS)
            logger.error("Error adding email: %s", str(ie))
            raise CustomException(ErrorMessages.UPDATE_EMAIL_FAILED)
        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise CustomException(ErrorMessages.UPDATE_EMAIL_FAILED)


    # Removes the specified user email settings record from the database.
    def delete_email_settings(self, customer_uuid, application_uuid, user_email_uuid, user_uuid):
        headers = (customer_uuid, application_uuid, None)

        logger.info("Received request to delete email settings for user_email_uuid: %s", user_email_uuid)

        user_email_settings = self.email_settings_dao.get_user_email_settings_by_id(user_email_uuid, customer_uuid, application_uuid)
        if user_email_settings is None:
            raise CustomException(ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND)

        # Avoid deleting individual email if it is associated with any group email
        self.__check_individual_email_association(user_email_settings, headers)

        # Delete user email settings
        logger.info("Deleting user email settings")
        self.email_settings_dao.delete_user_email_settings(user_email_settings, user_uuid)

    # Tests IMAP connection for Gmail
    def test_connection_gmail(self, email_uuid, server_url, port, email, password, use_ssl, is_encrypted):
        logger.info(f"Testing IMAP connection for email: {email}")

        # While updating email if password not edited
        if password is None and is_encrypted:
            logger.info("Fetching encrypted password from database")
            # Fetch password from db based on email
            user_email_settings = self.email_settings_dao.get_user_email_settings_by_id(email_uuid)
            if user_email_settings is None:
                raise CustomException(ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND)
            password = decrypt_password(user_email_settings.encrypted_password)

        logger.info(f"Establishing IMAP connection to {server_url}:{port}")
        connection = test_imap_connection(server_url, port, email, password, use_ssl)

        logger.info("IMAP connection successful")
        return connection

    def test_connection_outlook(self, user_email, client_id, tenant_id, client_secret) -> tuple:
        """
        Test the connection by decoding the access token and verifying the required permissions and user email.

        :param user_email: Outlook email ID of the user.
        :param client_id: Microsoft client ID.
        :param tenant_id: Microsoft tenant ID.
        :param client_secret: Microsoft client secret.

        :returns: Tuple with message and status code.
        """
        logger.info(f"Testing MSAL connection for email: {user_email}")

        try:
            # Retrieve the access token
            access_token = get_access_token(client_secret, client_id, tenant_id)
        except Exception as e:
            logger.error(f"Access token retrieval failed: {e}")
            raise CustomException(ErrorMessages.INVALID_SERVER_DETAILS, status_code=status.HTTP_400_BAD_REQUEST)

        # Test for required permissions
        message, status_code = self.__test_for_permissions(access_token)
        if status_code == status.HTTP_200_OK:
            # Proceed to verify user email only if permissions are valid
            return self.__test_for_user_email(access_token, user_email)

        return message, status_code


    def __test_for_user_email(self, access_token, user_email):
        """
        Test the connection by verifying the user email against the Microsoft Graph API.

        :param access_token: The access token to authenticate the request.
        :param user_email: The email address to verify.

        :returns: Tuple with message and status code.
        """
        logger.info("In __test_for_user_email")

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Endpoint to fetch the user profile from Graph API
        end_point = OutlookUrlsEndPoints.USER_PROFILE_URL.value.format(EMAIL_ID=user_email)

        try:
            # Make the API call to get user profile.
            response = call_api(headers=headers, endpoint=end_point, method="GET")
            logger.info("Successfully fetched response from Graph API")

            if response.ok:
                # If the response is successful, return success message.
                return SuccessMessages.CONNECTION_SUCCESSFUL, response.status_code
            else:
                # If response is not successful, return error message.
                return ErrorMessages.INTERNAL_ERROR_TEST_CONNECTION, status.HTTP_500_INTERNAL_SERVER_ERROR

        except CustomException as e:
            # Map status codes to messages using a dictionary.
            status_messages = {
                status.HTTP_401_UNAUTHORIZED: ErrorMessages.UNAUTHORISED_TEST_CONNECTION,
                status.HTTP_403_FORBIDDEN: ErrorMessages.PERMISSIONS_NOT_GRANTED,
                status.HTTP_404_NOT_FOUND: ErrorMessages.USER_EMAIL_NOT_FOUND.format(user_email=user_email)
            }

            # Default error message for unhandled status codes.
            default_message = ErrorMessages.CONNECTION_FAILED_WITH_EXCEPTION_MESSAGE.format(e=e)

            # Get the appropriate message from the dictionary or use the default message.
            message = status_messages.get(e.status_code, default_message)

            return message, e.status_code

        except Exception as e:
            # Raise custom exception for any unexpected errors.
            raise CustomException(ErrorMessages.INTERNAL_ERROR_TEST_CONNECTION,
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __test_for_permissions(self, access_token: str) -> tuple:
        """
        Validate that the access token contains the required application permissions (Mail.Read and Mail.Send).

        :param access_token: The access token to validate.
        :returns: Tuple with message and status code.
        """
        logger.info("In __test_for_permissions")

        try:
            # Decode the JWT token without verifying the signature
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            app_permissions = set(decoded_token.get("roles", []))

            # Define permission sets
            read_permissions = {MicrosoftGraphPermissions.MAIL_READ_ALL.value,
                                MicrosoftGraphPermissions.MAIL_READ_WRITE.value}
            send_permission = MicrosoftGraphPermissions.MAIL_SEND.value

            # Check if read and send permissions are granted
            read_permission_flag = bool(read_permissions & app_permissions)  # Intersection check for read permissions
            send_permission_flag = send_permission in app_permissions

            if read_permission_flag and send_permission_flag:
                # All required permissions are granted
                return SuccessMessages.SUCCESS_PERMISSIONS_GRANTED, status.HTTP_200_OK
            else:
                # Identify missing permissions for better debugging
                missing_permissions = []
                if not read_permission_flag:
                    missing_permissions.append("Read permissions (Mail.ReadWrite or Mail.Read.All)")
                if not send_permission_flag:
                    missing_permissions.append("Mail.Send")

                # Construct detailed error message
                missing_message = ErrorMessages.MISSING_PERMISSIONS.format(permissions=', '.join(missing_permissions))
                return missing_message, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            # Handle unexpected errors gracefully
            logger.error(f"Error validating permissions: {e}")
            return ErrorMessages.INTERNAL_ERROR_TEST_CONNECTION.format(e=e), status.HTTP_400_BAD_REQUEST

    # Helper methods
    def __add_email_setting(self, email_address, encrypted_password, email_type, headers, cust_email_provider, email_details_json=None):
        """This Method builds new user_email_setting and calls dao to create in the database."""

        customer_uuid, application_uuid, user_uuid = headers

        # Ensure the email address provider matches the provider specified in the channel settings
        self.__validate_email_provider(email_address, cust_email_provider)

        # Build user email settings instance
        user_email_settings = UserEmailSetting(
            user_email_uuid=str(uuid.uuid4()),
            email_id=email_address,
            encrypted_password=encrypted_password,
            email_type=email_type,
            email_details_json=email_details_json,
            customer_uuid=Customers(customer_uuid),
            application_uuid=Applications(application_uuid),
            created_by=user_uuid,
            updated_by=user_uuid,
        )

        # Call dao to add user email settings to db
        self.email_settings_dao.save_user_email_settings(user_email_settings)

    def __check_individual_email_association(self, user_email_settings, headers):
        """Checks if the given individual email is associated with any group email settings."""

        if user_email_settings.email_type == constants.EMAIL_TYPE_INDIVIDUAL:
            customer_uuid, application_uuid, _ = headers

            # Check if the email is associated with any group email settings using JSONB query
            is_associated = self.email_settings_dao.check_email_association_with_group(customer_uuid, application_uuid, user_email_settings.email_id)

            if is_associated:
                raise CustomException(ErrorMessages.INDIVIDUAL_EMAIL_ASSOCIATED_WITH_GROUP)

    def __validate_email_provider(self, email_address, cust_email_provider):
        """
        Validates that the domain of the email address being added matches the email provider specified in the server settings.
        """

        email_provider = get_email_provider(email_address)
        if email_provider is None:
            raise CustomException(ErrorMessages.INVALID_EMAIL_DOMAIN)
        elif email_provider != cust_email_provider:
            raise CustomException(ErrorMessages.EMAIL_PROVIDER_MISMATCH)

    def __update_email_settings(self, email_settings, headers, user_email_settings, email_id, hashed_password):
        """Updates each field of user email settings instance."""
        customer_uuid, application_uuid, user_uuid = headers

        user_email_settings.email_id = email_id
        user_email_settings.encrypted_password = hashed_password

        # Check if it needs to be marked as primary sender
        is_primary_sender_address = email_settings.get('is_primary_sender_address', False)
        if is_primary_sender_address:
            # Deactivate all existing primary email senders
            self.email_settings_dao.deactivate_primary_senders(customer_uuid, application_uuid)

            # Mark the selected email as primary sender
            user_email_settings.is_primary_sender_address = is_primary_sender_address
        user_email_settings.updated_by = user_uuid

    def __handle_primary_email_add(self, email_settings, headers, hashed_password):
        """Handles adding a primary email address."""

        customer_uuid, application_uuid, _ = headers
        email_details = email_settings.get('email_details_json')
        cust_email_provider = email_settings.get('cust_email_provider')
        primary_email_address = email_details.primary_email_address

        # Fetch the primary email present in the customer-application
        logger.info("Fetching primary email from database")
        primary_email = self.email_settings_dao.get_user_email_settings_by_email_id(primary_email_address, customer_uuid, application_uuid).first()

        # If primary email (indi email) exists for customer-application
        if primary_email is not None:
            logger.info("Primary email already exists")
            hashed_password = primary_email.encrypted_password
        else:
            # If primary email doesn't exist, create a new individual email entry
            logger.info("Creating new individual email")
            self.__add_email_setting(primary_email_address, hashed_password, constants.EMAIL_TYPE_INDIVIDUAL, headers, cust_email_provider)

        return hashed_password, asdict(email_details)
