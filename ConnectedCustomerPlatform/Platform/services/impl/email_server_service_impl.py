import json
import logging
from datetime import datetime
import pytz
import uuid
from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone
from rest_framework import status

from DatabaseApp.models import EmailServerCustomerApplicationMapping, Applications, Customers
from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException, \
    InvalidValueProvidedException
from EmailApp.constant.constants import SECRET_NAME_FORMAT_PREFIX, MicrosoftSecretDetailsKeys, EmailProvider
from EmailApp.utils import get_access_token
from ConnectedCustomerPlatform.azure_key_vault_utils import KeyVaultService
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.dao.impl.email_settings_dao_impl import EmailSettingsDaoImpl
from Platform.services.interface.email_server_service_interface import IEmailServerService
from Platform.dao.impl.email_server_dao_impl import EmailServerDaoImpl
from Platform.dao.impl.email_server_cam_dao_impl import EmailServerCAMDaoImpl

logger = logging.getLogger(__name__)


indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
class EmailServerServiceImpl(IEmailServerService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmailServerServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)

            print("Inside EmailServerServiceImpl")
            self.email_server_dao = EmailServerDaoImpl()
            self.user_email_dao = EmailSettingsDaoImpl()
            self.email_server_cam_dao = EmailServerCAMDaoImpl()
            print(f"Inside EmailServerServiceImpl - Singleton Instance ID: {id(self)}")

            self.initialized = True

    # Handles the creation of a list of new email server entries.
    @transaction.atomic
    def add_email_server(self, customer_uuid, application_uuid, user_uuid, email_server_data):
        try:
            logger.info("Received email server data: %s", email_server_data)

            # Call service to add email servers
            extract_default_server_uuids_st = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time before Extracting default email server uuids from payload:: {format_indian_time(extract_default_server_uuids_st)}\n")
            # Extract all the UUIDs of default email servers from the input email server data.
            default_email_server_uuids = [str(email_server.get('email_server_uuid')) for email_server in email_server_data]
            extract_default_server_uuids_et = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time after Extracting default email server uuids from payload:: {format_indian_time(extract_default_server_uuids_et)}\n")
            logger.info(f"\nTime profile :: Add Email Server :: Total time taken Extracting default email server uuids from payload:: {(extract_default_server_uuids_et - extract_default_server_uuids_st).total_seconds() * 1000:.4f} ms\n")
            
            # Retrieve the actual default email server records from the database based on the extracted UUIDs.
            extract_default_servers_st = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time before fetching default email server from DB:: {format_indian_time(extract_default_servers_st)}\n")
            default_email_servers = self.email_server_dao.get_default_email_servers_by_ids(default_email_server_uuids)
            extract_default_server_et = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time after fetching default email server from DB:: {format_indian_time(extract_default_server_et)}\n")
            logger.info(f"\nTime profile :: Add Email Server :: Total time taken fetching default email server from DB:: {(extract_default_server_et - extract_default_servers_st).total_seconds() * 1000:.4f} ms\n")

            # Convert the list of default email server objects into a dictionary for quick lookup.
            default_servers_dict_st = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time before Creating default email servers dict:: {format_indian_time(default_servers_dict_st)}\n")
            default_email_servers_dict = {default_email_server.email_server_uuid: default_email_server for default_email_server in default_email_servers}
            default_servers_dict_et = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time after  Creating default email servers dict:: {format_indian_time(default_servers_dict_et)}\n")
            logger.info(f"\nTime profile :: Add Email Server :: Total time taken  Creating default email servers dict:: {(default_servers_dict_et - default_servers_dict_st).total_seconds() * 1000:.4f} ms\n")

            # Create Mapping instances
            server_mappings_st = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time before Creating Server mapping instances:: {format_indian_time(server_mappings_st)}\n")
            email_server_mappings = [
                self._build_email_server_mapping_entity(customer_uuid, application_uuid, user_uuid, validated_server, default_email_servers_dict)
                for validated_server in email_server_data
            ]
            server_mappings_et = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time after  Creating Server mapping instances:: {format_indian_time(server_mappings_et)}\n")
            logger.info(f"\nTime profile :: Add Email Server :: Total time taken Creating Server mapping instances:: {(server_mappings_et - server_mappings_st).total_seconds() * 1000:.4f} ms\n")

            # Create email servers in bulk
            logger.info("Creating email server mappings in bulk")
            create_bulk_mappings_st = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time before Creating Server mapping in bulk:: {format_indian_time(create_bulk_mappings_st)}\n")
            self.email_server_cam_dao.bulk_create_server_mappings(email_server_mappings)
            create_bulk_mappings_et = datetime.now()
            logger.info(f"\nTime profile :: Add Email Server :: time after Creating Server mapping in bulk:: {format_indian_time(create_bulk_mappings_et)}\n")
            logger.info(f"\nTime profile :: Add Email Server :: Total time taken Creating Server mapping in bulk:: {(create_bulk_mappings_et - create_bulk_mappings_st).total_seconds() * 1000:.4f} ms\n")

        except IntegrityError as ie:
            if 'unique constraint' in str(ie):
                logger.error("Unique constraint violation occurred: %s", str(ie))
                raise CustomException(ErrorMessages.EMAIL_SERVER_EXISTS)
            logger.error("Database integrity error: %s", str(ie))
            raise CustomException(ErrorMessages.ADD_EMAIL_SERVER_FAILED)
        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise CustomException(ErrorMessages.ADD_EMAIL_SERVER_FAILED)

    # Retrieves email server configurations for the given customer and application.
    def get_email_server(self, customer_uuid, application_uuid):
        logger.info("Retrieving email servers for customer: %s, application: %s", customer_uuid, application_uuid)
        # Format of response data
        response_data = {
            "SMTP": {
                "customer_configured": None,
                "available_options": []
            },
            "IMAP": {
                "customer_configured": None,
                "available_options": []
            }
        }

        # Fetch customer configured servers
        fetch_customer_servers_st = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time before Fetching customer servers from mapping table:: {format_indian_time(fetch_customer_servers_st)}\n")
        configured_servers = self.email_server_cam_dao.get_mapped_servers_with_join(customer_uuid, application_uuid)
        fetch_customer_servers_et = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time after Fetching customer servers from mapping table:: {format_indian_time(fetch_customer_servers_et)}\n")
        logger.info(f"\nTime profile :: Get Email Server :: Total time taken Fetching customer servers from mapping table:: {(fetch_customer_servers_et - fetch_customer_servers_st).total_seconds() * 1000:.4f} ms\n")

        extract_customer_server_uuids_st = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time before Extracting customer servers uuids:: {format_indian_time(extract_customer_server_uuids_st)}\n")
        configured_server_uuids = [server.get('email_server_uuid') for server in configured_servers]
        extract_customer_server_uuids_et = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time after Extracting customer servers uuids:: {format_indian_time(extract_customer_server_uuids_et)}\n")
        logger.info(f"\nTime profile :: Get Email Server :: Total time taken Extracting customer servers uuids:: {(extract_customer_server_uuids_et - extract_customer_server_uuids_st).total_seconds() * 1000:.4f} ms\n")

        # Fetch default servers by excluding customer configured
        fetch_default_servers_st = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time before Fetching default servers from server table:: {format_indian_time(fetch_default_servers_st)}\n")
        default_servers = self.email_server_dao.get_default_email_servers_by_ids_excluded(configured_server_uuids)
        fetch_default_servers_et = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time after Fetching default servers from server table:: {format_indian_time(fetch_default_servers_et)}\n")
        logger.info(f"\nTime profile :: Get Email Server :: Total time taken Fetching default servers from server table:: {(fetch_default_servers_et - fetch_default_servers_st).total_seconds() * 1000:.4f} ms\n")

        # Generate response data
        loop_customer_servers_st = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time before Looping customer servers:: {format_indian_time(loop_customer_servers_st)}\n")
        for server in configured_servers:
            if server is not None and server.get('server_type') in response_data:
                response_data[server.get('server_type')]['customer_configured'] = server
        loop_customer_servers_et = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time after Looping customer servers:: {format_indian_time(loop_customer_servers_et)}\n")
        logger.info(f"\nTime profile :: Get Email Server :: Total time taken Looping customer servers:: {(loop_customer_servers_et - loop_customer_servers_st).total_seconds() * 1000:.4f} ms\n")

        loop_defaut_servers_st = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time before Looping default servers:: {format_indian_time(loop_defaut_servers_st)}\n")
        for server in default_servers:
            if server is not None and server.get('server_type') in response_data:
                response_data[server.get('server_type')]['available_options'].append(server)
        loop_default_servers_et = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time after Looping default servers:: {format_indian_time(loop_default_servers_et)}\n")
        logger.info(f"\nTime profile :: Get Email Server :: Total time taken Looping default servers:: {(loop_default_servers_et - loop_defaut_servers_st).total_seconds() * 1000:.4f} ms\n")

        logger.info("Retrieved email servers successfully")
        return response_data

    # Modifies the email server settings based on provided data for the specified customer and application.
    @transaction.atomic
    def edit_email_server(self, customer_uuid, application_uuid, user_uuid, email_server_data):
        try:
            logger.info("Received email server data for update: %s", email_server_data)

            # Fetch Default servers and mapped servers of the customer to bulk update
            mapping_server_uuids = []
            email_server_uuids = []
            for server in email_server_data:
                email_server_uuids.append(str(server.get('email_server_uuid')))
                mapping_server_uuids.append(str(server.get('mapping_uuid')))

            # Fetch and Convert default servers and mapped servers to dict for fast access
            logger.info("Fetching default and mapped email servers")
            default_email_servers = self.email_server_dao.get_default_email_servers_by_ids(email_server_uuids)
            mapped_email_servers = self.email_server_cam_dao.get_mapped_servers(customer_uuid, application_uuid, mapping_server_uuids)

            default_email_servers_dict = {server.email_server_uuid: server for server in default_email_servers}
            mapped_email_servers_dict = {server.mapping_uuid: server for server in mapped_email_servers}

            # Update each server mapping instance
            updated_server_data = self.__update_email_server(email_server_data, default_email_servers_dict, mapped_email_servers_dict, user_uuid)

            # Bulk update the Mapping table instances
            logger.info("Updating email server mappings in bulk")
            self.email_server_cam_dao.bulk_update_server_mappings(updated_server_data)
        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise CustomException(ErrorMessages.UPDATE_EMAIL_SERVER_FAILED)

    # Helper methods
    def _build_email_server_mapping_entity(self, customer_uuid, application_uuid, user_uuid, validated_server, default_email_servers_dict):
        """Private helper method to build an EmailServer instance."""

        email_server = default_email_servers_dict.get(str(validated_server.get('email_server_uuid')))
        if email_server is None:
            raise CustomException(ErrorMessages.EMAIL_SERVER_NOT_FOUND)

        return EmailServerCustomerApplicationMapping(
            mapping_uuid=str(uuid.uuid4()),
            email_server_uuid=email_server,
            is_ssl_enabled=validated_server.get('is_ssl_enabled'),
            sync_time_interval=validated_server.get('sync_time_interval'),
            application_uuid=Applications(application_uuid),
            customer_uuid=Customers(customer_uuid),
            created_by=user_uuid,
            updated_by=user_uuid,
            inserted_ts=timezone.now(),
            updated_ts=timezone.now()
        )

    def __update_email_server(self, email_server_data, default_email_servers_dict, mapped_email_servers_dict, user_uuid):
        """
        Updates the email server mapping data with the provided new values.
        Returns:
            list: List of updated email server mapping instances.
        """

        # List to hold updated instances of mapping
        updated_server_data = []
        for email_server in email_server_data:
            default_email_server = default_email_servers_dict.get(str(email_server.get('email_server_uuid')))
            mapped_email_server = mapped_email_servers_dict.get(str(email_server.get('mapping_uuid')))
            if default_email_server is None or mapped_email_server is None:
                raise CustomException(ErrorMessages.EMAIL_SERVER_NOT_FOUND)

            mapped_email_server.email_server_uuid = default_email_server
            mapped_email_server.sync_time_interval = email_server.get('sync_time_interval')
            mapped_email_server.is_ssl_enabled = email_server.get('is_ssl_enabled')
            mapped_email_server.updated_ts = timezone.now()
            mapped_email_server.updated_by = user_uuid
            updated_server_data.append(mapped_email_server)

        return updated_server_data


    # Retrieves outlook server configurations for the given customer and application.
    def get_outlook_server(self, customer_uuid, application_uuid):
        """
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns configured outlook server details
        """
        logger.info("Retrieving email servers for customer: %s, application: %s", customer_uuid, application_uuid)
        # Format of response data

        # Fetch customer configured servers
        configured_server = self.email_server_cam_dao.get_mapped_servers_for_outlook(customer_uuid, application_uuid)
        # Check if configured server exists
        if configured_server is not None:
            #  Fetch the secret details associated with the server
            secret_name = SECRET_NAME_FORMAT_PREFIX + str(configured_server.mapping_uuid)
            secret_details = KeyVaultService().get_secret_details_from_redis_or_keyvault(secret_name=secret_name,expiry_for_redis=3500)

            # Convert configured_server model to a dictionary
            configured_server_dict = {"mapping_uuid": configured_server.mapping_uuid,
                                      "email_server_uuid": configured_server.email_server_uuid.email_server_uuid,
                                      "sync_time_interval": configured_server.sync_time_interval,
                                      "microsoft_client_id": configured_server.microsoft_client_id,
                                      "microsoft_tenant_id": configured_server.microsoft_tenant_id,
                                      "microsoft_client_secret": secret_details[
                                          MicrosoftSecretDetailsKeys.CLIENT_SECRET.value],
                                      "microsoft_secret_created_ts": secret_details[
                                          MicrosoftSecretDetailsKeys.SECRET_CREATED_TS.value],
                                      "microsoft_secret_expiry": secret_details[
                                          MicrosoftSecretDetailsKeys.SECRET_EXPIRY.value]}
            logger.info("Retrieved email servers successfully")
            return configured_server_dict
        return {}

    @transaction.atomic
    def save_outlook_server(self, customer_uuid, application_uuid, user_uuid, email_server_data, update=False):
        logger.info("In EmailServerServiceImpl :: save_outlook_server")
        """
        Save (create or update) an Outlook server for the given customer, application, and user.
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param user_uuid: UUID of the user making the request.
        :param email_server_data: Dictionary containing email server data.
        :param update: Boolean flag indicating if it's an update operation (True for update, False for add).
        """
        try:
            # Get the default email server
            default_outlook_server = self.email_server_dao.get_default_msal_server()
            if not default_outlook_server:
                raise ResourceNotFoundException("Default email server for Outlook not found")

            mapping_uuid = email_server_data.get('mapping_uuid') if update else str(uuid.uuid4())
            secret_name = SECRET_NAME_FORMAT_PREFIX + str(mapping_uuid)
            try:
                access_token=get_access_token(email_server_data.get('microsoft_client_secret'),
                                 email_server_data.get('microsoft_client_id'),
                                 email_server_data.get('microsoft_tenant_id'))
            except CustomException as e:
                logger.error(f"Exception occurred while saving server {e}")
                raise InvalidValueProvidedException("Please recheck details provided")
            # Prepare secret details
            secret_details = {
                MicrosoftSecretDetailsKeys.ACCESS_TOKEN.value: access_token,
                MicrosoftSecretDetailsKeys.CLIENT_SECRET.value: email_server_data.get('microsoft_client_secret'),
                MicrosoftSecretDetailsKeys.SECRET_EXPIRY.value: email_server_data.get('secret_expiration_time'),
                MicrosoftSecretDetailsKeys.SECRET_CREATED_TS.value: email_server_data.get('secret_created_ts')
            }
            logger.info(f"Creating secret with secret name {secret_name}  {secret_details}")
            #Update in redis and keyvault
            secret_details=json.dumps(secret_details)
            KeyVaultService().update_secret_in_redis_keyvault(secret_name=secret_name, secret_value=secret_details,expiry_for_redis=3500)
            # Directly create or update the server mapping in the database
            if update:
                self.email_server_cam_dao.update_email_server_mapping(
                    mapping_uuid, email_server_data, application_uuid, customer_uuid, user_uuid
                )
            else:
                self.email_server_cam_dao.create_email_server_mapping(
                    default_outlook_server, mapping_uuid, email_server_data, application_uuid, customer_uuid, user_uuid
                )

        except IntegrityError as ie:
            if 'unique constraint' in str(ie):
                logger.error("Unique constraint violation occurred: %s", str(ie))
                raise CustomException("Email Server already exists",status_code=status.HTTP_400_BAD_REQUEST)

            logger.error("Database integrity error: %s", str(ie))
            raise CustomException(ErrorMessages.ADD_EMAIL_SERVER_FAILED if not update else ErrorMessages.UPDATE_EMAIL_SERVER_FAILED)

        except ResourceNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to save outlook server: {str(e)}")
            raise CustomException((ErrorMessages.ADD_EMAIL_SERVER_FAILED if not update else ErrorMessages.UPDATE_EMAIL_SERVER_FAILED)+". "+str(e))


    @transaction.atomic
    def delete_email_server(self,customer_uuid,application_uuid,user_uuid):
        """Deletes all email server and user_email_setting for customer and application"""
        try:

            # Get server provider name
            server_provider = self.email_server_cam_dao.get_server_provider_name(customer_uuid, application_uuid)
            # raise exception if server does not exist for the customer and application
            if server_provider is None:
                raise CustomException(
                    f"Email Server does not exist for customer {customer_uuid} and application {application_uuid}")

            # delete related secrets in keyvault and redis cache if the server provider is outlook
            if server_provider.lower() == EmailProvider.OUTLOOK.value.lower():
                mapping_uuid = self.email_server_cam_dao.get_outlook_server_uuid(customer_uuid, application_uuid)
                secret_name = SECRET_NAME_FORMAT_PREFIX + str(mapping_uuid)
                KeyVaultService().delete_in_redis_key_vault(secret_name)

            logger.info(f"Attempting to delete user_email_settings for {customer_uuid} {application_uuid}")
            # soft delete user email settings
            self.user_email_dao.delete_all_mapped_user_email_settings(customer_uuid,application_uuid, user_uuid)
            logger.info(f"Attempting to delete email server customer application mapping for {customer_uuid} {application_uuid}")
            # hard delete email_Server_customer_application_mapping
            self.email_server_cam_dao.delete_all_mapped_email_server(customer_uuid,application_uuid)
            logger.info(SuccessMessages.DELETE_EMAIL_SERVER_SUCCESSFUL)
        except Exception as e:
            logger.error(f"Failed to delete email_server: {str(e)}")
            raise CustomException(ErrorMessages.DELETE_EMAIL_SERVER_FAILED)

    def get_server_provider_name(self,customer_uuid,application_uuid):
        """Returns provider name for email server"""
        provider_name=self.email_server_cam_dao.get_server_provider_name(customer_uuid,application_uuid)
        return provider_name