from django.db import DatabaseError
from django.db.models import F
from django.utils import timezone

from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException, CustomException
from DatabaseApp.models import EmailServerCustomerApplicationMapping, Applications, Customers
from EmailApp.constant.constants import ServerType
from Platform.dao.interface.email_server_cam_dao_interface import IEmailServerCAMDao
import logging
logger=logging.getLogger(__name__)
class EmailServerCAMDaoImpl(IEmailServerCAMDao):
    # Inserts a batch of email server records into the database.
    def bulk_create_server_mappings(self, email_server_mappings):
        EmailServerCustomerApplicationMapping.objects.bulk_create(email_server_mappings)

    # Retrieves mapped email servers for the specified customer and application, excluding the provided server UUIDs.
    def get_mapped_servers(self, customer_uuid, application_uuid, mapped_server_uuids):
        return EmailServerCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,
                                                                    application_uuid=application_uuid,
                                                                    mapping_uuid__in=mapped_server_uuids)

    # Retrieves mapped email servers for the specified customer and application, performing a join on the email server table.
    def get_mapped_servers_with_join(self, customer_uuid, application_uuid):
        return (EmailServerCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,
                                                                     application_uuid=application_uuid)
                .filter(email_server_uuid__is_deleted=False)
                .annotate(server_type=F('email_server_uuid__server_type'), port=F('email_server_uuid__port'),
                          server_url=F('email_server_uuid__server_url'), email_provider_name=F('email_server_uuid__email_provider_name'))
                .values('mapping_uuid', 'email_server_uuid', 'sync_time_interval', 'application_uuid', 'customer_uuid',
                        'server_type', 'is_ssl_enabled', 'port', 'email_provider_name', 'server_url'))

    # Processes updates for the given email server entries.
    def bulk_update_server_mappings(self, updated_servers):
       EmailServerCustomerApplicationMapping.objects.bulk_update(
           updated_servers,
           ['email_server_uuid', 'is_ssl_enabled', 'sync_time_interval', 'updated_by', 'updated_ts']
       )

    # Retrieves mapped email servers for the specified customer and application, performing a join on the email server table.
    def get_mapped_servers_for_outlook(self, customer_uuid, application_uuid):
        """ Get mapped outlook server for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns Email Server CAM object
        """
        logger.info("In get_mapped_servers_for_outlook")
        return EmailServerCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,
                                                                    application_uuid=application_uuid,email_server_uuid__is_deleted=False, email_server_uuid__server_type=ServerType.MSAL.value).first()


    def create_email_server_mapping(self, default_outlook_server,mapping_uuid, email_server_data, application_uuid, customer_uuid, user_uuid):
        """ Create new email server mapping directly with parameters
        :param email_server_data: dict containing sync_time_interval,microsoft_client_id,microsoft_tenant_id
        :param : default_outlook_server: default email server object
        :param : mapping_uuid: uuid of the new record
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param user_uuid: UUID of logged in user
        """
        try:
            logger.info(f"Creating new email server with mapping UUID {mapping_uuid}")

            # Directly call create with required parameters
            EmailServerCustomerApplicationMapping.objects.create(
                mapping_uuid=mapping_uuid,
                email_server_uuid=default_outlook_server,
                sync_time_interval=email_server_data.get('sync_time_interval'),
                application_uuid=Applications(application_uuid),
                customer_uuid=Customers(customer_uuid),
                microsoft_client_id=email_server_data.get('microsoft_client_id'),
                microsoft_tenant_id=email_server_data.get('microsoft_tenant_id'),
                created_by=user_uuid,
                updated_by=user_uuid,
                inserted_ts=timezone.now(),
                updated_ts=timezone.now()
            )
        except Exception as e:
            logger.error(f"Error creating email server mapping with UUID {mapping_uuid}: {str(e)}")
            raise

    def update_email_server_mapping(self, mapping_uuid, email_server_data, application_uuid, customer_uuid, user_uuid):
        """ Update sync_time_interval,microsoft_client_id,microsoft_tenant_id of existing email server mapping directly with parameters
        :param email_server_data: dict containing sync_time_interval,microsoft_client_id,microsoft_tenant_id
        :param : mapping_uuid: uuid of the new record
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param user_uuid: UUID of logged in user
        """
        logger.info(f"Updating email server mapping with UUID: {mapping_uuid}")
        try:
            # Directly call update with the necessary fields
            rows_affected = EmailServerCustomerApplicationMapping.objects.filter(
                mapping_uuid=mapping_uuid
            ).update(
                sync_time_interval=email_server_data.get('sync_time_interval'),
                microsoft_client_id=email_server_data.get('microsoft_client_id'),
                microsoft_tenant_id=email_server_data.get('microsoft_tenant_id'),
                updated_by=user_uuid,
                updated_ts=timezone.now()
            )
        except Exception as e:
            logger.error(f"Error updating email server mapping with UUID {mapping_uuid}: {str(e)}")
            raise CustomException(f"Error updating email server mapping with UUID {mapping_uuid}: {str(e)}")

        if rows_affected == 0:
            logger.error(f"Email server mapping with UUID {mapping_uuid} not found")
            raise ResourceNotFoundException(f"Email server mapping with UUID {mapping_uuid} not found")

        # Log successful update
        logger.info(f"Successfully updated email server mapping with UUID: {mapping_uuid}")


    def delete_all_mapped_email_server(self, customer_uuid, application_uuid):
        """
        Deletes all the mapped email servers for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Raises exception if any exception occurred
        """
        logger.info("In EmailSettingsDaoImpl :: delete_all_mapped_email_server")
        try:
            rows_affected, _ = EmailServerCustomerApplicationMapping.objects.filter(
                customer_uuid=customer_uuid, application_uuid=application_uuid
            ).delete()

            logger.info(
                f"Deleted {rows_affected} EmailServerCustomerApplicationMapping records for customer_uuid {customer_uuid} and application_uuid {application_uuid}")
        except DatabaseError as e:
            logger.error(f"Database error deleting EmailServerCustomerApplicationMapping: {e}")
            raise CustomException(f"Database error updating EmailServerCustomerApplicationMapping: {e}") from e

    def get_server_provider_name(self,customer_uuid,application_uuid):
        """ Fetch provider name for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns provider name, None if the customer and application not mapped
        """
        logger.info("In EmailSettingsDaoImpl :: get_server_provider_name")
        return EmailServerCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,application_uuid=application_uuid,status=True).values_list('email_server_uuid__email_provider_name',flat=True).first()

    def get_outlook_server_details(self,customer_uuid,application_uuid):
        """
        Fetches outlook server details for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns only mapping uuid,microsoft_client_id,microsoft_tenant_id as a tuple"""
        logger.info("In EmailSettingsDaoImpl :: get_outlook_server_details")
        return EmailServerCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,
                                                                    application_uuid=application_uuid,
                                                                    status=True).values_list(
            'mapping_uuid','microsoft_client_id','microsoft_tenant_id').first()
    def get_outlook_server_uuid(self,customer_uuid,application_uuid):
        """
        Fetches outlook server details for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns only mapping uuid"""
        logger.info("In EmailSettingsDaoImpl :: get_outlook_server_uuid")
        return EmailServerCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,
                                                                    application_uuid=application_uuid,
                                                                    status=True).values_list(
            'mapping_uuid',flat=True).first()
