from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException
from DatabaseApp.models import Applications, Customers, EmailConversation, EmailConversationView
from EmailApp.constant.constants import EmailActionFlowStatus, EmailConversationParams, EmailTaskStatus
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.dao.interface.email_conversation_dao_interface import EmailConversationDaoInterface
from rest_framework import status
from django.db.models import Q
from EmailApp.utils import get_current_timestamp, is_user_admin

import logging
logger = logging.getLogger(__name__)

class EmailConversationDaoImpl(EmailConversationDaoInterface):

    def get_email_conversation_by_email_uuid(self, email_uuid):

        # Using select_related to perform an inner join with EmailConversation based on email_uuid
        email_conversation = EmailConversation.objects.filter(email__email_uuid=email_uuid,is_deleted=False).first()
        if email_conversation is None:
            raise CustomException(
                ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
        return email_conversation
    
    def save_email_conversation(self, email_conversation_uuid, customer_uuid, customer_client_uuid, email_conversation_flow_status,
                     email_activity=None, inserted_ts=None, updated_ts=None,
                     application_uuid=None):
        """
        Saving email conversation into the db
        """
        logger.info(" In save_email_conversation_to_db")
        try:
            
            # Fetch the Applications instance using the application_uuid
            application = Applications.objects.get(application_uuid=application_uuid)
            # Fetch the Customers instance using the customer_uuid
            customer = Customers.objects.get(cust_uuid=customer_uuid)

            # Create the email object
            email_conversation_obj = EmailConversation.objects.create(
                email_conversation_uuid=email_conversation_uuid,
                customer_uuid=customer,
                customer_client_uuid=customer_client_uuid,
                email_conversation_flow_status=email_conversation_flow_status,
                email_activity=email_activity,
                inserted_ts=inserted_ts,
                updated_ts=updated_ts,  
                application_uuid=application
            )
            email_conversation_obj.save()
            logger.info("Email conversation object created and saved successfully!")
            return email_conversation_obj
        except Applications.DoesNotExist:
            logger.error("Application with the given UUID does not exist.", exc_info=True)
        except Customers.DoesNotExist:
            logger.error("Customer with the given UUID does not exist.", exc_info=True)
        except Exception as e:
            logger.error(f"Error occurred while saving email conversation: {e}", exc_info=True)
        
        return None
        
    def get_email_conversation(self, email_conversation_uuid):
        email_conversation = EmailConversationView.objects.filter(
            email_conversation_uuid=email_conversation_uuid,is_deleted=False
        )
        if not email_conversation:
            raise ResourceNotFoundException(ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND)
        return email_conversation
    
    def update_email_conversation(self, email_conversation_obj):

        email_conversation_obj.email_conversation_flow_status = EmailTaskStatus.IN_PROGRESS.value
        email_conversation_obj.updated_ts = get_current_timestamp()
        email_conversation_obj.save()

    def get_email_conversation_obj(self, email_conversation_uuid):
        email_conversation = EmailConversation.objects.filter(
            email_conversation_uuid=email_conversation_uuid,is_deleted=False
        )
        if not email_conversation:
            raise ResourceNotFoundException(ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND)
        return email_conversation
    
    def update_email_flow_status(self, parent_email_obj, status):
        parent_email_obj.email_flow_status = status
        parent_email_obj.update_ts = get_current_timestamp()
        parent_email_obj.save()
    
    def update_email_activity_in_email_conversation(self, conversation_uuid,email_activity):
        """
        updates email_activity in email_conversation
        Args:
            conversation_uuid:
            email_activity:

        Returns:

        """
        logger.info("In EmailConversationDaoImpl :: update_email_activity_in_email_conversation")

        try:
            updated_count = EmailConversation.objects.filter(email_conversation_uuid=conversation_uuid,is_deleted=False).update(email_activity=email_activity)

            if updated_count == 0:
                logger.error(f"Email with UUID {conversation_uuid} does not exist.")
                raise ResourceNotFoundException(f"EmailConversation with UUID {conversation_uuid} does not exist.")
        except Exception as e:
            logger.error(f"An error occurred while fetching email_activity: {e}")
            raise CustomException(f"Error in updating email activity with email uuid :: {conversation_uuid}")

    def get_email_conversation_by_ticket_uuid(self, ticket_uuid):
        email_conversation = EmailConversationView.objects.filter(
            ticket_uuid=ticket_uuid,is_deleted=False
        )
        if not email_conversation:
            raise ResourceNotFoundException(ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND)
        return email_conversation

    def update_timeline(self, email_conversation_uuid: str, email_activity: dict, email_uuid: str, status: str, timestamp, user_uuid):
        """
        Update the timeline of an email conversation in the new dictionary format.

        This method updates the timeline for a specific email identified by
        the email_uuid within a conversation identified by email_conversation_uuid.

        Parameters:
        - email_conversation_uuid (str): EmailConversation uuid.
        - email_activity (dict): email_activity of email_conversation
        - email_uuid (str): The UUID of the email whose status is being updated.
        - status (str): The status to set for the email (e.g., 'sent', 'received').
        - timestamp: The timestamp to associate with the given status.
        - user (str, optional): The user performing the operation.

        Returns:
        - Updated email_activity (dict) or None if an error occurs.
        """
        try:
            # Retrieve existing email activity or initialize a new one
            email_activity = email_activity if email_activity else {}

            # Retrieve or initialize the timeline as a dictionary
            timeline = email_activity.get("timeline", {})

            # Retrieve or initialize the operations list for the given email_uuid
            email_operations = timeline.get(email_uuid, [])

            # Add the new operation with timestamp (and user if provided)
            operation_entry = {"operation": status, "timestamp": timestamp, "user": user_uuid}

            email_operations.append(operation_entry)

            # Update the timeline with the new operations
            timeline[email_uuid] = email_operations
            email_activity["timeline"] = timeline

            # Save the updated email_activity back to the database
            self.update_email_activity_in_email_conversation(email_conversation_uuid, email_activity)

            logger.info(f"Timeline updated successfully for email UUID: {email_uuid} in conversation UUID: {email_conversation_uuid}")
            return email_activity

        except Exception as e:
            logger.error(f"Error updating timeline for conversation UUID: {email_conversation_uuid}, email UUID: {email_uuid}. Error: {str(e)}")
            return None

    def update_timestamp(self, email_conv_obj, updated_ts):
        """
        Updates the `updated_ts` field of the given EmailConversation object.
        
        Args:
            email_conv_obj (EmailConversation): The EmailConversation object to update.
            updated_ts (datetime): The timestamp to set in the `updated_ts` field.
        """
        email_conv_obj.updated_ts = updated_ts
        email_conv_obj.save(update_fields=['updated_ts'])  # Optimize query to update only the `updated_ts` field


    def get_email_conversation_by_ticket_id(self, ticket_uuid):
        email_conversation = EmailConversation.objects.filter(
            ticket_uuid=ticket_uuid,is_deleted=False
        ).first()
        return email_conversation

    def save_email_conversation_instance(self,email_conversation,user_uuid):
        email_conversation.updated_by = user_uuid
        email_conversation.save()
