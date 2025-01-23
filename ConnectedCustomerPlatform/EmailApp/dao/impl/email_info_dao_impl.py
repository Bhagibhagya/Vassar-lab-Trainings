from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import EmailInfoDetail
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.dao.interface.email_info_dao_interface import EmailInfoDaoInterface
from rest_framework import status

import logging
logger = logging.getLogger(__name__)

class EmailInfoDaoImpl(EmailInfoDaoInterface):

    def get_conversation_info(self, email_uuid):

        # This will return a tuple (sender_name, subject) or None if no record is found
        result = EmailInfoDetail.objects.filter(email_uuid=email_uuid).values_list(
            'sender_name',
            'email_subject'
        ).first()
        
        # Check if result is None
        if result is None:
            return None, None  

        return result  # This will return a tuple (sender_name, subject)
    
    def get_email_info(self, email_uuid):
        try:
            # Fetch the extracted_order_details in the email info detail using the provided email_uuid
            return EmailInfoDetail.objects.get(email_uuid=email_uuid)
        except EmailInfoDetail.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.EMAIL_INFO_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
    
        
    def get_email_info_attachments(self, email_uuid):

        try:
            # Fetch the attachments in email info detail using the provided email_uuid
            return EmailInfoDetail.objects.values_list('attachments', flat=True).get(email_uuid=email_uuid)
        except EmailInfoDetail.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.EMAIL_INFO_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
    def get_email_info_body_url(self, email_uuid):

        try:
            # Fetch the attachments in email info detail using the provided email_uuid
            return EmailInfoDetail.objects.values_list('email_body_url', flat=True).get(email_uuid=email_uuid)
        except EmailInfoDetail.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.EMAIL_INFO_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    def save_verified(self, email_uuid):

        email_info = EmailInfoDetail.objects.get(email_uuid=email_uuid).first()
        email_info.verified = False
        email_info.save()

    def save_email_info(self, email, email_info_json):
        email_info_detail = EmailInfoDetail.objects.create(
            email_uuid=email,
            email_info_uuid = email_info_json['email_info_uuid'],
            email_subject = email_info_json['email_subject'],
            email_body_url = email_info_json['email_body_url'],
            email_meta_body = email_info_json['email_meta_body'],
            attachments = email_info_json['attachments'],
            sender = email_info_json['sender'],
            sender_name = email_info_json['sender_name'],
            email_type = email_info_json['email_type'],
            recipient = email_info_json['recipient'],
            recipients = email_info_json['recipients'],
            cc_recipients = email_info_json['cc_recipients'],
            bcc_recipients = email_info_json['bcc_recipients']
        )
        email_info_detail.save()

        logger.debug("EmailInfo created and saved successfully in the db! %s",email_info_detail.email_info_uuid)
        return email_info_detail