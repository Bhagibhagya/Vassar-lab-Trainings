
from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import UserEmailSetting
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.dao.interface.user_email_setting_dao_interface import UserEmailSettingDaoInterface
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class UserEmailSettingDaoImpl(UserEmailSettingDaoInterface):

    def is_user_email_setting_exists(self, customer_uuid, from_email_id, application_uuid):
        """
        Checks if a user email setting exists based on the given customer UUID, email ID, and application UUID.

        Args:
            customer_uuid (str): The UUID of the customer.
            from_email_id (str): The email ID to check.
            application_uuid (str): The UUID of the application.

        Returns:
            bool: Returns True if the user email setting exists and is not marked as deleted, otherwise False.
        """
        return UserEmailSetting.objects.filter(
                customer_uuid=customer_uuid,
                email_id=from_email_id,
                application_uuid=application_uuid,
                is_deleted = False
            ).exists()
    
    def get_primary_email_setting(self, customer_uuid, application_uuid):
        """
        Retrieves the primary email setting for a customer and application.

        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            str: The primary sender email ID if found.

        Raises:
            CustomException: If no primary email setting is found, a custom exception is raised.
        """
        try:
            return UserEmailSetting.objects.values_list('email_id', flat=True).get(
                is_deleted = False,
                is_primary_sender_address=True,
                customer_uuid=customer_uuid,
                application_uuid=application_uuid
            )
        
        except UserEmailSetting.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.PRIMARY_EMAIL_SETTING_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
    def get_mail_and_password(self, customer_uuid, application_uuid, from_email_id):
        """
        Method to fetch emailid and password for sending an email, If not found fetch primary email address
        """
        try:
            # Attempt to get the user email setting based on the filter
            return UserEmailSetting.objects.values_list('encrypted_password', 'email_id').get(
                customer_uuid=customer_uuid,
                email_id=from_email_id,
                application_uuid=application_uuid,
                is_deleted = False
            )
        
        except UserEmailSetting.DoesNotExist:
            # If the user email setting is not found, look for a primary sender address
            try:
                return UserEmailSetting.objects.values_list('encrypted_password', 'email_id').get(
                    customer_uuid=customer_uuid,
                    application_uuid=application_uuid,
                    is_primary_sender_address=True,
                    is_deleted = False
                )
            
            except UserEmailSetting.DoesNotExist:
                # Handle case where no record is found
                raise CustomException(
                    ErrorMessages.PRIMARY_EMAIL_SETTING_NOT_FOUND,
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        except Exception as e:
            # Generic exception handling
            logger.error(f"An error occurred while fetching email and password: {e}", exc_info=True)
            raise CustomException(
                ErrorMessages.UNABLE_TO_FETCH_EMAIL_DETAILS,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )