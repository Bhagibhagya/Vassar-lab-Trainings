from venv import logger
from DatabaseApp.models import Customers, Dimension, Email, EmailConversation, EmailConversationView, EmailInfoDetail, EmailServer, Step, UserEmailSetting, UserMgmtUsers
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException, ResourceNotFoundException
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.dao.interface.get_emails_by_client_id_dao_interface import EmailConversationDaoInterface
from django.db.models import Q
from EmailApp.constant.constants import EmailConversationParams,EmailActionFlowStatus
from EmailApp.constant.constants import EmailTaskStatus
from rest_framework import status

from EmailApp.utils import get_current_timestamp

class EmailConversationDaoImpl(EmailConversationDaoInterface):

    def query_email_conversation(self, customer_uuid, application_uuid, validated_data):
        """
        Fetch email conversations based on customer_uuid, application_uuid, and date range.

        This method filters email conversations within the specified date range (start_date, end_date) for 
        a given customer and application. It further narrows down results based on the conversation flow status:
        
        - AI_ASSISTED: Fetches conversations marked as either 'AI_ASSISTED' or 'NEED_ASSISTANCE'.
        - MANUALLY_HANDLED: Fetches conversations marked as either 'MANUALLY_HANDLED' or 'NEED_ATTENTION'.
        - Otherwise, fetches conversations with the specific status provided.
        
        The result is ordered by the 'inserted_ts' field in descending order and returns relevant conversation details.

        Parameters:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.
            validated_data (dict): Dictionary containing start_date, end_date, and email_conversation_flow_status.

        Returns:
            QuerySet: Filtered and ordered queryset containing 'email_conversation_uuid', 'inserted_ts', and 'updated_ts'.
        """
        email_conversation_queryset = EmailConversation.objects.filter(
            customer_uuid = customer_uuid,
            application_uuid = application_uuid,
            inserted_ts__gte=validated_data['start_date'],
            inserted_ts__lte=validated_data['end_date'],
            customer_client_uuid__is_deleted=False
        ).order_by(f'-{EmailConversationParams.INSERTED_TS.value}')
    
        if validated_data['email_conversation_flow_status'] == EmailActionFlowStatus.AI_ASSISTED.value:
            email_conversation_queryset = email_conversation_queryset.filter(
                Q(email_conversation_flow_status=EmailActionFlowStatus.AI_ASSISTED.value) |
                Q(email_conversation_flow_status=EmailActionFlowStatus.NEED_ASSISTANCE.value)
            )
        elif validated_data['email_conversation_flow_status'] == EmailActionFlowStatus.MANUALLY_HANDLED.value:
            email_conversation_queryset = email_conversation_queryset.filter(
                Q(email_conversation_flow_status=EmailActionFlowStatus.MANUALLY_HANDLED.value) |
                Q(email_conversation_flow_status=EmailActionFlowStatus.NEED_ATTENTION.value)
            )
        elif validated_data['email_conversation_flow_status'] != EmailActionFlowStatus.TOTAL_EMAIL_RECEIVED.value:
            email_conversation_queryset = email_conversation_queryset.filter(email_conversation_flow_status=validated_data['email_conversation_flow_status'])

        return email_conversation_queryset.values(
            'email_conversation_uuid', 
            'inserted_ts', 
            'updated_ts'
        )

    def get_parent_emails(self,email_conversation_uuids):

        return Email.objects.filter(email_conversation_uuid__in=email_conversation_uuids,parent_uuid__isnull=True).order_by(EmailConversationParams.INSERTED_TS.value).values(
            'email_conversation_uuid',
            'email_uuid'
        )
    
    def get_conversation_info(self, email_uuid):

        # This will return a tuple (sender_name, subject) or None if no record is found
        result = EmailInfoDetail.objects.filter(email_uuid=email_uuid).values_list('sender_name', 'email_subject').first()
        
        # Check if result is None
        if result is None:
            return None, None  

        return result  # This will return a tuple (sender_name, subject)
    
    def get_dimension(self,dimension_uuid):

        return Dimension.objects.filter(dimension_uuid=dimension_uuid).only('dimension_uuid','dimension_name','dimension_type_uuid')
    
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

    def get_emails_by_conversation_uuid(self, email_conversation_uuid):

        return Email.objects.filter(email_conversation_uuid=email_conversation_uuid).order_by(EmailConversationParams.INSERTED_TS.value).values('email_uuid','email_subject','email_status','parent_uuid','dimension_action_json','inserted_ts','updated_ts')
    

    def get_email_conversation_create_draft_mail(self, email_uuid):

        # Using select_related to perform an inner join with EmailConversation based on email_uuid
        email_conversation = EmailConversation.objects.filter(email__email_uuid=email_uuid).first()
        if email_conversation is None:
            raise CustomException(
                ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        return email_conversation

    
    def get_email_info_order_details(self, email_uuid):

        try:
            # Fetch the extracted_order_details in the email info detail using the provided email_uuid
            return EmailInfoDetail.objects.values_list('extracted_order_details', flat=True).get(email_uuid=email_uuid)
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

    def get_email(self,email_uuid):
        try:
            # Fetch the email details using the provided email_uuid
            return Email.objects.get(email_uuid=email_uuid)
        except Email.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.EMAIL_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    def get_parent_email(self, parent_uuid):
        try:
            # Fetch the email details using the provided email_uuid
            return Email.objects.get(parent_uuid=parent_uuid)
        except Email.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.PARENT_EMAIL_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )

    def get_step_details(self, step_uuid):

        return Step.objects.get(step_uuid=step_uuid).step_details_json
    
    def save_verified(self, email_uuid):

        email_info = EmailInfoDetail.objects.get(email_uuid=email_uuid).first()
        email_info.verified = False
        email_info.save()

    def get_email_conversation_queryset(self,email_conversation_queryset):

        return email_conversation_queryset.values(
            'email_conversation_uuid', 
            'email_conversation_flow_status', 
            'dimension_uuid', 
            'inserted_ts', 
            'updated_ts'
        )


    def delete_draft(self, email_uuid):

        try:
            draft_mail = Email.objects.get(email_uuid=email_uuid,email_status=EmailTaskStatus.DRAFT.value)
            # Delete the draft conversation
            draft_mail.delete()

        except Email.DoesNotExist:
            # Handle case where no record is found
            raise InvalidValueProvidedException(
                ErrorMessages.DRAFT_MAIL_NOT_FOUND
            )
        
        
    def get_user_email_setting(self, customer_uuid, from_email_id, application_uuid):

        return UserEmailSetting.objects.filter(
                customer_uuid=customer_uuid,
                email_id=from_email_id,
                application_uuid=application_uuid
            ).exists()
    
    def get_primary_email_setting(self, customer_uuid, application_uuid):
        
        try:
            return UserEmailSetting.objects.values_list('email_id', flat=True).get(
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
    
    def get_customer_name(self, customer_uuid):

        try:
            return Customers.objects.values_list('cust_name', flat=True).get(cust_uuid=customer_uuid)

        except Customers.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.CUSTOMER_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
    def get_user(self, user_uuid):
        
        try:
             # Retrieve only first_name and last_name fields as a tuple
            return UserMgmtUsers.objects.values_list('first_name', 'last_name').get(user_id=user_uuid)

        except Customers.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.USER_NOT_FOUND_IN_USERMGMT,
                status_code=status.HTTP_404_NOT_FOUND
            )

    def get_email_conversation_uuid_from_email_uuid(self, in_reply_to):
        
        try:
            return Email.objects.values_list('email_conversation_uuid').get(email_uuid=in_reply_to)

        except Email.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.PARENT_EMAIL_ID_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
    def get_parent_email_create_draft_mail(self, in_reply_to):

        try:
            return Email.objects.get(email_uuid=in_reply_to)
        
        except Email.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.PARENT_EMAIL_ID_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
    def save_email_conversation_to_db(self, email_conversation_uuid, customer_uuid, customer_client_uuid, email_conversation_flow_status,
                     email_activity=None, inserted_ts=None, updated_ts=None,
                     application_uuid=None):
        """
        Saving email conversation into the db
        """
        logger.info(" In save_email_conversation_to_db")
        try:
            # Create the email object
            email_conversation_obj = EmailConversation.objects.create(
                email_conversation_uuid=email_conversation_uuid,
                customer_uuid=customer_uuid,
                customer_client_uuid=customer_client_uuid,
                email_conversation_flow_status=email_conversation_flow_status,
                email_activity=email_activity,
                inserted_ts=inserted_ts,
                updated_ts=updated_ts,  
                application_uuid=application_uuid
            )
            email_conversation_obj.save()
            logger.info("Email conversation object created and saved successfully!")
            return email_conversation_obj
        except Exception as e:
            logger.error(f"Error occurred while saving email object: {e}", exc_info=True)
            return None
    
    def save_email_data(self, email_uuid, email_conversation_uuid, email_flow_status, email_status,
                                dimension_action_json, insert_ts, updated_ts, parent_uuid=None):
        logger.info("In save email data to db ")
        # Create a new EmailConversations object
        print("email_uuid",email_uuid,"email_conversation_uuid",email_conversation_uuid)
        email = Email.objects.create(
            email_uuid=email_uuid,  
            email_conversation_uuid=email_conversation_uuid,
            email_flow_status=email_flow_status,
            email_status=email_status,
            dimension_action_json=dimension_action_json,
            inserted_ts=insert_ts,
            updated_ts=updated_ts,
            parent_uuid=parent_uuid if parent_uuid else None
        )
        # Save the object into the database
        email.save()

        logger.debug("Email created and saved successfully in the db! %s",email.email_uuid)

        return email
    
    def save_email_info(self, email, email_info_json):
        email_info_detail = EmailInfoDetail.objects.create(
            email_uuid=email,
            email_info_uuid = email_info_json['email_info_uuid'],
            email_subject = email_info_json['email_subject'],
            email_body_url = email_info_json['email_body_url'],
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

    def update_email_conversation_data(self, email_conversation_obj):

        email_conversation_obj.email_conversation_flow_status = EmailTaskStatus.IN_PROGRESS.value
        email_conversation_obj.updated_ts = get_current_timestamp()
        email_conversation_obj.save()

    def get_email_conversation(self, email_conversation_uuid):

        email_conversation = EmailConversationView.objects.filter(
            email_conversation_uuid=email_conversation_uuid
        )
        if not email_conversation:
            raise ResourceNotFoundException(ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND)
        return email_conversation
            
    
    def get_email_server(self, smtp_filter):
        try:
            # Filtering based on the related EmailServerCustomerApplicationMapping fields
            return EmailServer.objects.filter(
                emailservercustomerapplicationmapping__application_uuid=smtp_filter.get('application_uuid'),
                emailservercustomerapplicationmapping__customer_uuid=smtp_filter.get('customer_uuid'),
                emailservercustomerapplicationmapping__status=True,
                status=True  # Ensures only active servers are returned
            ).values_list('server_url', 'port').get()
        except EmailServer.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.SMTP_SERVER_DETAILS_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
    def user_email_setting_reply_mail(self, application_uuid, user_email_filter):
        try:
            # Attempt to get the user email setting based on the filter
            return UserEmailSetting.objects.values_list('encrypted_password', 'email_id').get(**user_email_filter)
        
        except UserEmailSetting.DoesNotExist:
            # If the user email setting is not found, look for a primary sender address
            primary_filter = {**user_email_filter, 'is_primary_sender_address': True}
            if application_uuid:
                primary_filter['application_uuid'] = application_uuid
            
            try:
                return UserEmailSetting.objects.values_list('encrypted_password', 'email_id').get(**primary_filter)
            
            except UserEmailSetting.DoesNotExist:
                # Handle case where no record is found
                raise CustomException(
                    ErrorMessages.USER_EMAIL_SETTING_NOT_FOUND,
                    status_code=status.HTTP_404_NOT_FOUND
                )

        