from datetime import datetime

from django.db.models import Q
from django.utils import timezone

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import UserEmailSetting
from Platform.dao.interface.email_settings_dao_interface import IEmailSettingsDao
from Platform.constant.constants import EMAIL_TYPE_GROUP


import logging
logger=logging.getLogger(__name__)
class EmailSettingsDaoImpl(IEmailSettingsDao):

    # Queries the database for user email settings by username.
    def get_user_email_settings_by_email_id(self, email_id, customer_uuid=None, application_uuid=None):
        return UserEmailSetting.objects.filter(email_id=email_id, customer_uuid=customer_uuid,
                                               application_uuid=application_uuid, is_deleted=False)

    # Retrieves user email settings based on customer and application UUIDs, filtering by email type if provided.
    def get_user_email_settings(self, customer_uuid, application_uuid, email_type=None):
        filter_query = Q(customer_uuid=customer_uuid, application_uuid=application_uuid, is_deleted=False)
        if email_type is not None:
            filter_query &= Q(email_type=email_type, is_deleted=False)

        return (UserEmailSetting.objects.filter(filter_query).order_by('-updated_ts')
                .defer('encrypted_password', 'inserted_ts', 'updated_ts', 'created_by', 'updated_by', 'status')
                .values('user_email_uuid', 'email_id', 'email_type', 'email_details_json', 'is_primary_sender_address',
                    'application_uuid', 'customer_uuid', 'is_deleted', 'last_read_ts', 'in_queue'
                ))

    # Queries the database for a user email setting using the specified UUID.
    def get_user_email_settings_by_id(self, user_email_uuid, customer_uuid=None, application_uuid=None):
        if customer_uuid is not None and application_uuid is not None:
            return UserEmailSetting.objects.filter(customer_uuid=customer_uuid,
                                                    application_uuid=application_uuid,
                                                    user_email_uuid=user_email_uuid, is_deleted=False).first()
        return UserEmailSetting.objects.filter(user_email_uuid=user_email_uuid, is_deleted=False).first()

    # Updates the database to set primary sender addresses to inactive.
    def deactivate_primary_senders(self, customer_uuid, application_uuid):
        UserEmailSetting.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            is_primary_sender_address=True,
            is_deleted=False
        ).update(is_primary_sender_address=False)

    # Inserts or updates the user email settings in the database.
    def save_user_email_settings(self, user_email_settings):
        user_email_settings.save()

    # Removes the user email settings record from the database.
    def delete_user_email_settings(self, user_email_settings, user_uuid):
        user_email_settings.is_deleted = True
        user_email_settings.updated_by = user_uuid
        user_email_settings.updated_ts = datetime.now()
        self.save_user_email_settings(user_email_settings)

    # Perform the query on the JSONB field to check if the individual email is associated with a group email
    def check_email_association_with_group(self, customer_uuid, application_uuid, email_id):
        return UserEmailSetting.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            email_type=EMAIL_TYPE_GROUP,
            email_details_json__primary_email_address=email_id,
            is_deleted=False
        ).exists()


    def delete_all_mapped_user_email_settings(self, customer_uuid, application_uuid, user_uuid):
        logger.info("In EmailSettingsDaoImpl :: delete_all_user_email_settings")
        try:
            rows_affected = UserEmailSetting.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid).update(
                is_deleted=True,
                updated_by=user_uuid,
                updated_ts=timezone.now()
            )

            logger.info(f"Updated {rows_affected} no of user_email_Settings for customer_uuid {customer_uuid} and application_uuid {application_uuid}")

        except Exception as e:
            logger.error(f"Error updating user_email_settings {str(e)}")
            raise CustomException(f"Error updating user_email_settings {str(e)}")