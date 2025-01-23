from django.db import connection
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from DatabaseApp.models import Email, EmailConversation
from EmailApp.constant.constants import EmailConversationParams, EmailTaskStatus
from EmailApp.dao.interface.email_dao_interface import EmailDaoInterface
from EmailApp.constant.error_messages import ErrorMessages
from rest_framework import status
from django.db import IntegrityError, connection , transaction

import logging

from EmailApp.utils import get_current_timestamp
logger = logging.getLogger(__name__)

class EmailDaoImpl(EmailDaoInterface):
    
    def get_parent_emails(self,email_conversation_uuids):

        return Email.objects.filter(email_conversation_uuid__in=email_conversation_uuids,parent_uuid__isnull=True).order_by(EmailConversationParams.INSERTED_TS.value).values(
            'email_conversation_uuid',
            'email_uuid'
        )
    
    def get_email(self,email_uuid):
        # Fetch the email details using the provided email_uuid
        return Email.objects.filter(email_uuid=email_uuid).first()
 
        
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
    
    
    def save_email(self, email_uuid, email_conversation_uuid, email_flow_status, email_status,
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
    
    def update_email_conversation_flow_status(self, email_conversation_obj, status):
        email_conversation_obj.email_conversation_flow_status = status
        email_conversation_obj.updated_ts = get_current_timestamp()
        email_conversation_obj.save()
    
    def get_emails(self,email_uuids):
        # Raw SQL query to fetch emails based on email uuids
        query = """SELECT 
                    e.email_uuid,
                    e.email_status,
                    e.email_flow_status,
                    e.dimension_action_json,
                    e.parent_uuid,
                    e.inserted_ts,
                    e.updated_ts,
                    eid.email_info_uuid,
                    eid.email_subject,
                    eid.email_body_url,
                    eid.html_body,
                    eid.attachments,
                    eid.sender,
                    eid.sender_name,
                    eid.recipient,
                    eid.recipients,
                    eid.cc_recipients,
                    eid.bcc_recipients,
                    eid.email_body_summary,
                    eid.email_meta_body,
                    eid.extracted_order_details,
                    eid.validated_details,
                    eid.verified
                FROM 
                    email e
                JOIN 
                    email_info_detail eid ON e.email_uuid = eid.email_uuid
                WHERE 
                    e.email_uuid = ANY(%s)
                ORDER BY
                    e.inserted_ts;"""
 
        with connection.cursor() as cursor:
            cursor.execute(query, [email_uuids])
            columns = [col[0] for col in cursor.description]  # Get column names
            emails = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Format results as a list of dictionaries

        return emails

    def get_parent_emails_by_tickets(self,ticket_uuids):

        query = """
        SELECT e.email_uuid , ec.ticket_uuid 
        FROM email e join email_conversation ec on e.email_conversation_uuid=ec.email_conversation_uuid
        WHERE ec.ticket_uuid = ANY(%s) and e.parent_uuid is null 
        ORDER BY e.inserted_ts
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [ticket_uuids])
            columns = [col[0] for col in cursor.description]  # Get column names
            emails = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Format results as a list of dictionaries

        return emails

    def map_emails_to_primary_conversation(self,primary_conversation_uuid,secondary_conversation_uuid):
        logger.info("In :: EmailApp :: email_dao_impl ::  get_emails_by_conversation_uuids")

        conversation_uuids_list = [primary_conversation_uuid,secondary_conversation_uuid]

        emails = Email.objects.filter(email_conversation_uuid__in=conversation_uuids_list).order_by('inserted_ts')

        # Update parent_uuid relationships
        with transaction.atomic():  # Ensure atomicity of updates
            for email in emails:
                email.email_conversation_uuid = EmailConversation(primary_conversation_uuid)
            # Use bulk_update to save changes in one query
            Email.objects.bulk_update(emails, ['email_conversation_uuid'])

    def get_latest_conversation_uuid(self,conversation_uuids):
        logger.info("In :: EmailApp :: email_dao_impl ::  get_latest_email_time_by_conversation_uuid")
        return Email.objects.filter(email_conversation_uuid__in=conversation_uuids).order_by('-inserted_ts').values_list('email_conversation_uuid', flat=True).first()

    def get_latest_conversation_time(self,conversation_uuid):
        logger.info("In :: EmailApp :: email_dao_impl ::  get_latest_email_time_by_conversation_uuid")
        return Email.objects.filter(email_conversation_uuid=conversation_uuid).order_by('-inserted_ts').values_list('inserted_ts', flat=True).first()
