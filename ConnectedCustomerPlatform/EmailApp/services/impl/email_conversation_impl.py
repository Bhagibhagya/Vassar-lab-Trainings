import base64
from datetime import datetime
import json
import uuid
from django.conf import settings
from AIServices.VectorStore.chromavectorstore import ChromaVectorStore
from EmailApp.DataClasses.response.pagination_data import PaginationResponse
from EmailApp.constant.constants import Action, CategeriesForPersonalization, CsrChromaDbFields, EmailActionFlowStatus, \
    EmailDraftParams, EmailReplyParams, EmailTaskStatus, EmailType, TimelineTypes, ChannelTypes, EmailProvider, \
    OutlookUrlsEndPoints, SECRET_NAME_FORMAT_PREFIX, PDF_PROCESSING_STEP_NAME, ChannelTypesUUID, FileUploadNames, FileContentTypes, ReturnTypes
from EmailApp.constant.success_messages import SuccessMessages
from EmailApp.dao.impl.customers_dao_impl import CustomersDaoImpl
from EmailApp.dao.impl.email_conversation_dao_impl import EmailConversationDaoImpl
from EmailApp.dao.impl.email_dao_impl import EmailDaoImpl
from EmailApp.dao.impl.email_info_dao_impl import EmailInfoDaoImpl
from EmailApp.dao.impl.email_server_dao_impl import EmailServerDaoImpl
from EmailApp.dao.impl.ticket_dao_impl import TicketDaoImpl
from EmailApp.dao.impl.user_email_setting_dao_impl import UserEmailSettingDaoImpl
from EmailApp.dao.impl.users_dao_impl import UsersDaoImpl
from EmailApp.dao.impl.wise_flow_dao_impl import WiseFlowDaoImpl
from EmailApp.serializers import EmailSerializer
from Platform.dao.impl.email_server_cam_dao_impl import EmailServerCAMDaoImpl
from Platform.utils import decrypt_password, paginate_queryset
from EmailApp.utils import  authenticate_smtp_credentials, check_profanity, datetime_to_milliseconds, \
    generate_email_summary, generate_message_id, get_current_date_str, get_current_timestamp, \
    get_metadata_presigned_url, get_timestamp_from_date, send_or_reply_email, generate_detailed_summary, \
    hit_and_retry_with_new_token
from ConnectedCustomerPlatform.exceptions import CustomException
from EmailApp.constant.error_messages import ErrorMessages
from rest_framework import status

from EmailApp.services.interface.email_conversation_interface import IEmailConversationService
from ce_shared_services.factory.queuing_service.queuing_service_factory import QueuingServiceFactory

from django.db import transaction
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


import logging
logger = logging.getLogger(__name__)

class EmailConversationServiceImpl(IEmailConversationService):
    
    def __init__(self):
        self.email_conversation_dao = EmailConversationDaoImpl()
        self.email_dao = EmailDaoImpl()
        self.email_info_dao = EmailInfoDaoImpl()
        self.user_email_setting_dao = UserEmailSettingDaoImpl()
        self.email_server_cam_platform_dao=EmailServerCAMDaoImpl()
        self.customers_dao = CustomersDaoImpl()
        self.users_dao = UsersDaoImpl()
        self.email_server_dao = EmailServerDaoImpl()
        self.azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))
        self.chroma_vector_store=ChromaVectorStore()
        self.ticket_dao = TicketDaoImpl()
        self.wiseflow = WiseFlowDaoImpl()

    def get_email_conversations(self, customer_uuid, application_uuid,user_uuid, validated_data):
        """
        Fetches paginated email conversations for a specific customer and application.

        Args:
            customer_uuid (str): Unique identifier for the customer.
            application_uuid (str): Unique identifier for the application.
            validated_data (dict): Data used for filtering and pagination.
        
        Returns:
            dict: A response containing paginated email conversations and metadata.
        """
        logger.info("Fetching email conversations for customer: %s, application: %s", customer_uuid, application_uuid)

        # Fetch email conversations from database with optimized pagination
        email_conversation_queryset = self.email_conversation_dao.query_email_conversation(customer_uuid, application_uuid,user_uuid, validated_data)

        # Paginate the queryset and fetch the email conversations for the requested page
        page, paginator = paginate_queryset(email_conversation_queryset, validated_data)

        paginated_emails = self.build_email_conversation_list(page.object_list)

        # Build and return the response
        return self.build_response(paginated_emails, paginator.count, paginator.num_pages, validated_data)


    def build_email_conversation_list(self, email_conversation_obj):
        """
        Builds a list of email conversations with necessary details.

        Args:
            email_conversation_queryset (QuerySet): QuerySet of email conversations.

        Returns:
            list: A list of dictionaries containing email conversation details.
        """

        # Extract email conversation UUIDs
        email_conversation_uuids = [email['email_conversation_uuid'] for email in email_conversation_obj]

        # Fetch parent emails for the matching email conversations
        parent_emails = self.email_dao.get_parent_emails(email_conversation_uuids)

        # Build a dictionary for quick lookup of parent emails
        emails_dict = {email['email_conversation_uuid']: email for email in parent_emails}

        # Build the list of email conversations
        mails_list = [
            self.build_parent_email_dict(email_conversation, emails_dict.get(email_conversation['email_conversation_uuid']))
            for email_conversation in email_conversation_obj
        ]

        return mails_list

    def build_parent_email_dict(self, email_conversation, email):
        """
        Builds a dictionary with details of a parent email.

        Args:
            email_conversation (dict): Email conversation details.
            email (dict): Parent email details.

        Returns:
            dict: Dictionary containing email conversation details.
        """

        # Retrieve sender name and sender email from email info by email_uuid
        sender_name, subject = self.email_info_dao.get_conversation_info(email['email_uuid'])


        # Build and return the dictionary
        return {
            'conversation_id': email_conversation['email_conversation_uuid'],
            'is_read': email_conversation['is_read'],
            'sender_name': sender_name,
            'subject': subject,
            'inserted_ts': datetime_to_milliseconds(email_conversation['inserted_ts']),
            'updated_ts': datetime_to_milliseconds(email_conversation['updated_ts']),
        }


    def build_response(self, paginated_emails, total_mails, total_pages, validated_data):
        """
        Builds the response containing paginated email conversations and metadata.

        Args:
            paginated_emails (list): List of paginated email conversations.
            total_mails (int): Total number of email conversations.
            validated_data (dict): Data containing pagination info.

        Returns:
            dict: Response with email conversations and pagination metadata.
        """
        return PaginationResponse(
            page_num=validated_data['page_number'],
            total_entry_per_page=validated_data['total_entry_per_page'],
            total_entries=total_mails,
            total_pages=total_pages,
            data=paginated_emails
        ).model_dump()


    def get_mail_conversation_by_ticket_uuid(self, ticket_uuid):
        """
        Retrieves the email conversation and associated activity for the given ticket uuid.
        
        Parameters:
            ticket_uuid (str): UUID of the ticket.

        Returns:
            dict: Dictionary containing email conversation data, email summary, and timeline.
        """
        logger.info(f"Fetching email conversation for ticket UUID: {ticket_uuid}")
        #Get all the email records for the given email_conversation
        email_conversation = self.email_conversation_dao.get_email_conversation_by_ticket_uuid(ticket_uuid)

        email_conversation_data = self.build_email_conversation_data(email_conversation)

        result = {"email_conversation_data": email_conversation_data}

        # Get the email activity from view (Since all rows will have same activity so fetching first one)
        email_activity = email_conversation.first().email_activity if email_conversation.first().email_activity else {}
        # Get email_summary from activity json
        result['email_summary'] = email_activity.get('email_summary', "")

        # Get the timeline
        timeline = email_activity.get('timeline', {})
        # Sort the timeline
        if timeline:
            # Extract all unique user UUIDs from the operations
            user_uuids = {
                operation['user']
                for operations in timeline.values()
                for operation in operations
                if 'user' in operation
            }

            # Fetch user details for all UUIDs in one database call and create a lookup dictionary
            user_lookup = {
                uuid: username
                for uuid, username in self.users_dao.get_users_name(user_uuids)  # Assume get_users returns [(uuid, first_name, last_name), ...]
            }
            # Sort the operations within each email's timeline
            for email_uuid, operations in timeline.items():
                # Replace user UUID with first and last names
                for operation in operations:
                    if 'user' in operation:
                        operation['user'] = user_lookup.get(operation['user'])  #Get the value from dictionary directly

                # Sort the operations by timestamp
                timeline[email_uuid] = sorted(
                    operations,
                    key=lambda operation: operation.get('timestamp', float('inf'))
                )

            result['timeline'] = timeline
        else:
            result['timeline'] = {}  # Set an empty dictionary if no timeline exists

        return result

    
    def build_email_conversation_data(self, email_conversation):
        """
        Build structured data for each email conversation.
        
        Parameters:
            email_conversation (QuerySet): Queryset containing email conversation records.

        Returns:
            list: List of structured email conversation data.
        """
        email_conversations_list = list(email_conversation.values())

        # Get the last inserted record based on inserted_ts
        last_inserted_record = max(email_conversations_list, key=lambda x: x['inserted_ts'])
        email_conversation_data = []
        for email in email_conversations_list:
            conversation_data = self.build_conversation_data(email, last_inserted_record)

            # Check if this record is a draft
            if email['email_status'] == "Draft":
                self.add_draft_conversation(email_conversation_data, conversation_data)
            else:
                email_conversation_data.append(conversation_data)

        return email_conversation_data
    
    def get_email_info(self, email_info_detail,last_inserted_record):
        """
        Get detailed information for an email, including its body and metadata.
        
        Parameters:
            email_info_detail (dict): Details of the email record.
            last_inserted_record (object): The last inserted email record.

        Returns:
            dict: Dictionary containing the email's information.
        """
        email_body = email_info_detail['email_body_url']

        #Getting email_body for the last email record and for other records onlu URL will be enough
        if email_body and last_inserted_record['email_uuid']==email_info_detail['email_uuid']:
            email_body = self.get_content_from_url(email_info_detail['email_body_url'])

        # Check if html_body is None, and set it to an None
        html_body = email_info_detail['html_body'] if email_info_detail['html_body'] else None

        return {
            'email_body_url': email_body,
            'html_body_url': html_body,
            'attachments': self.json_field_parser(email_info_detail['attachments']),
            'sender': email_info_detail['sender'],
            'sender_name': email_info_detail['sender_name'],
            'recipient': email_info_detail['recipient'],
            'recipients': self.json_field_parser(email_info_detail['recipients']),
            'cc_recipients': self.json_field_parser(email_info_detail['cc_recipients']),
            'bcc_recipients': self.json_field_parser(email_info_detail['bcc_recipients']),
            'email_body_summary': email_info_detail['email_body_summary'],
            'email_meta_body': email_info_detail['email_meta_body'],
            'extracted_order_details': email_info_detail['extracted_order_details'],
            'validated_details': email_info_detail['validated_details'],
            'verified': email_info_detail['verified']
        }
        

    def build_conversation_data(self, email, last_inserted_record):
        """
        Build structured conversation data for an email record.

        Parameters:
            email (dict): Dictionary containing email details.
            last_inserted_record (object): The last inserted email record.

        Returns:
            dict: Dictionary with structured email conversation data.
        """
        return {
            "email_uuid": email['email_uuid'],
            "sender_name": email['sender_name'],
            "email_subject": email['email_subject'],
            "email_flow_status": email['email_flow_status'],
            "email_task_status": email['email_status'],
            "parent_uuid": email['parent_uuid'],
            "email_info_json": self.get_email_info(email,last_inserted_record),
            "dimension_action_json": self.json_field_parser(email['dimension_action_json']),
            "inserted_ts": datetime_to_milliseconds(email['inserted_ts']),
            "updated_ts": datetime_to_milliseconds(email['updated_ts']),
            "draft": None
        }
    
    def json_field_parser(self, field):
        """
        Parse a field if it is a JSON-encoded string.

        Parameters:
            field (str or any): The field to parse.

        Returns:
            dict or list or any: Parsed JSON object or the original field if not JSON.
        """
        if isinstance(field, str):
            try:
                return json.loads(field)
            except json.JSONDecodeError:
                return field  # Return as-is if it's not valid JSON
            
        return field
    
    def add_draft_conversation(self, email_data, draft_mail):
        '''
        Find the asscoiated parent email and add this as draft for that email
        if not found add as new record
        '''
        # Convert the email_data list into a dictionary for faster lookups
        email_data_dict = {email['email_uuid']: email for email in email_data}

        # Retrieve the parent email directly by accessing the dictionary
        parent_email = email_data_dict.get(draft_mail.get("parent_uuid"))
        
        # If a parent conversation is found, add the draft conversation to it.
        if parent_email:
            email_body_url = parent_email.get('email_info_json').get('email_body_url') #Extract the body of the parent email as well
            #TODO temp fix bug
            if "http" in email_body_url:
                parent_email['email_info_json']['email_body_url'] = self.get_content_from_url(email_body_url)
            else:
                parent_email['email_info_json']['email_body_url'] = email_body_url
            parent_email[EmailDraftParams.DRAFT.value] = draft_mail
        else:
            # If no parent conversation is found, add the draft conversation as a new entry in the email data.
            email_data.append(draft_mail)

    
    def get_content_from_url(self, file_url):
        """
        Fetches the file content for a given File URL by downloading the content.

        Parameters:
            file_url (str): The File url for which the content needs to be fetched.

        Returns:
            str: The content, if found.
        """

        # Download and return the content using the retrieved file URL.
        file_content = self.azure_blob_manager.download_data_with_url(file_url).decode('utf-8')
        if '.json' in file_url:
            file_content = json.loads(file_content)
        return file_content
        
    

    @transaction.atomic
    def post_order_details_info(self, email_uuid, details_extracted_json, file_path, attachment_id, user_uuid):
        """
        Method to Update the order details and uploads into storage and pushes data to eventhub to trigger generate response
        """
        #Safely handle the case for empty spaces with '+'
        email_uuid = email_uuid.replace(' ', '+')

        #To update the status to processing we need email object
        email = self.email_dao.get_email(email_uuid)
        if email is None:
            raise CustomException(ErrorMessages.EMAIL_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)
        
        # Fetch the record matching the email_uuid
        email_info_detail = self.email_info_dao.get_email_info(email_uuid)
        
        #Fetch the email conversation record with email_uuid
        email_conversation = self.email_conversation_dao.get_email_conversation_obj(email.email_conversation_uuid.email_conversation_uuid)
        email_conversation = email_conversation.first()
        # Check if extracted_order_details is None
        if not email_info_detail.attachments:
            raise CustomException(detail=ErrorMessages.EXTRACTED_ORDER_DETAILS_NOT_FOUND,
                                  status_code=status.HTTP_404_NOT_FOUND)
        file_name = self.__get_file_name_from_url(file_path)
        data = json.dumps(details_extracted_json)
        self.azure_blob_manager.update_data_with_url(file_path,data.encode('utf-8'),file_name)

        email.email_status = EmailActionFlowStatus.PROCESSING.value
        email.save()
        attachments = email_info_detail.attachments
        init_count = len(attachments)
        count = 0
        for attachment in attachments:
            if attachment.get("attachment_id", "") == attachment_id:
                attachment.update({"is_verified": True})
                count += 1
            elif attachment.get("is_verified"):
                count += 1
        # #execute the query to update the attachment is_verified = True
        # self.email_conversation_dao.update_the_verified_to_True(email_uuid, attachment_id)
        # Check whether all are verified, if verified make email level verified = True
        if count == init_count:
            email_info_detail.verified = True
        email_info_detail.attachments = attachments
        email_info_detail.save()

        # Fetch the email conversation record with email_uuid
        email_conversation = self.email_conversation_dao.get_email_conversation_obj(
            email.email_conversation_uuid.email_conversation_uuid)

        email_conversation = email_conversation.first()
        # Update the email timeline for document validated and by which user
        self.email_conversation_dao.update_timeline(email_conversation.email_conversation_uuid,
                                                    email_conversation.email_activity, email_uuid,
                                                    TimelineTypes.Validated_document.value,
                                                    datetime_to_milliseconds(datetime.now()), user_uuid)
        # TODO need to trigger Email microservice
        # self.continue_flow_to_event_hub(email,email_info_detail)

        return SuccessMessages.POST_ORDER_SUCCESS

    def __get_file_name_from_url(self,file_url):
        names = file_url.split('/')
        if len(names)>0:
            return names[-1]
        else:
            return None

    # def continue_flow_to_event_hub(self,email,email_info_detail):
    #     try:
    #         email_process_details = email_conversation.email_process_details
    #         # Check if email_process_details is a list and contains at least one element:
    #         if isinstance(email_process_details, list) and len(email_process_details) > 0:
    #             last_detail = email_process_details[-1]
    #             step_uuid = last_detail.get('step_uuid', '')
    #             if not step_uuid:
    #                 raise CustomException(ErrorMessages.STEP_UUID_NOT_FOUND)
    #             # step = Step.objects.filter(step_uuid=step_uuid).first()
    #             step_details_json = self.email_conversation_dao.get_step_details(step_uuid)
    #             if not step_details_json:
    #                 logger.error(f"No step found with UUID {step_uuid}")
    #                 raise CustomException(ErrorMessages.STEP_DETAILS_NOT_FOUND)
    #             next_step_info = step_details_json.get('default_next_step_info','')
    #             if not next_step_info:
    #                 raise CustomException(ErrorMessages.NEXT_STEP_INFO_NOT_FOUND)
    #             output_data = last_detail.get('output_data', '')
    #             if not output_data:
    #                 raise CustomException(ErrorMessages.OUTPUT_DATA_NOT_FOUND)
    #             send_to_event_hub(next_step_info, output_data)
    #             self.email_conversation_dao.save_verified(email.email_uuid)

    #             email_info_detail.verified = True
    #             email_info_detail.save()

    #         else:
    #             raise CustomException(ErrorMessages.EMAIL_PROCESS_DETAILS_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error in Post order details :: {e}")
    #         self.email_conversation_dao.save_verified(email.email_uuid)

    #         email_info_detail.verified = False
    #         email_info_detail.save()

    #         raise CustomException(ErrorMessages.VERIFICATION_FAILED_RETRY_AGAIN)
        


    def get_downloadable_urls(self, list_of_file_urls):
        """
        Returns the presigned url and metadata of the files url
        """
        
        # Initialize an empty list to store the presigned URL data and metadata for each file.
        files_data = []
        # Iterate through each file URL in the input list.

        for file_data_dict in list_of_file_urls:

            # Call a function to generate the presigned URL and fetch metadata for the file.
            # The `get_metadata_presigned_url` function returns a dictionary containing metadata and the presigned URL.

            #TODO once prem updated meta data in attachments use that and only retrieve pre signed URL
            file_data=get_metadata_presigned_url(file_data_dict)

            # If the presigned URL and metadata are successfully generated, append them to the `url_data_list`.
            if file_data:
                files_data.append(file_data)

        # Prepare the final response data containing all the presigned URLs and their corresponding metadata.
        response_data = {
            "files_data": files_data
        }
        return response_data
        

    def delete_draft_mail(self, email_uuid):

         # Call DAO method to delete the draft email
        self.email_dao.delete_draft(email_uuid)
    


    @transaction.atomic
    def create_draft_mail(self, customer_uuid, application_uuid, user_uuid, validated_data):
        """
        This function creates a draft mail.
        """
        # Extracting necessary fields from validated_data
        from_email_id = validated_data['from_email_id']
        in_reply_to = validated_data.get('in_reply_to', None)  # in_reply_to could be None
        to = validated_data['to']
        cc = validated_data.get('cc', [])
        bcc = validated_data.get('bcc', [])
        subject = validated_data.get('subject', "")
        body = validated_data.get('body', None)
        attachments = validated_data.get('attachments', [])

        from_email_id, sender_name = self.get_sender_name_and_from_email_id(customer_uuid, from_email_id, application_uuid, user_uuid)

        # If this is a reply (in_reply_to exists), retrieve the email conversation and parent email
        if in_reply_to:
            # Retrieve the email conversation for a reply draft
            email_conversation = self.email_conversation_dao.get_email_conversation_by_email_uuid(in_reply_to)
            # Get the parent email based on in_reply_to (email_uuid)
            parent_email = self.email_dao.get_email(in_reply_to)
            if parent_email is None:
                raise CustomException(ErrorMessages.EMAIL_NOT_FOUND,status_code=status.HTTP_404_NOT_FOUND)
            
        else:
            # If there's no in_reply_to, it means this is the first email in the conversation
            email_conversation = None
            parent_email = None

        # Save the new email draft with provided details
        saved_email, saved_email_info, email_conversation_uuid = self.process_and_save_email_details(
            customer_uuid, 
            application_uuid, 
            email_conversation, 
            parent_email,
            from_email_id, 
            sender_name, 
            to, 
            cc, 
            bcc, 
            subject, 
            body, 
            attachments
        )

        # Build and return drafted response with the saved conversation data
        return self.build_draft_conversation_response(body, saved_email, saved_email_info, email_conversation_uuid)


    def get_sender_name_and_from_email_id(self, customer_uuid, from_email_id, application_uuid, user_uuid):
        '''
        Returns from_email_id and sender_name,using email_uuid from user_email_settings
        If user_email_setting does not exist Get the from_email_id and sender_name from primary_email_setting 
        '''
        logger.info("In Create draft mail :: :: :: :: :: :: get_sender_name")
        # Check if the user's email setting exists for the given customer and app
        user_email_setting_exists = self.user_email_setting_dao.is_user_email_setting_exists(customer_uuid, from_email_id, application_uuid)

        # If the email setting doesn't exist, use the primary email setting of the user
        if user_email_setting_exists is False:
            from_email_id = self.user_email_setting_dao.get_primary_email_setting(customer_uuid, application_uuid)
            sender_name = self.customers_dao.get_customer_name(customer_uuid)  # Set the sender name using customer name
        else:
            # If email setting exists, retrieve first and last name of the user
            first_name, last_name = self.users_dao.get_user(user_uuid)
            # Construct the sender_name using user's first and last name
            sender_name = f"{first_name} {last_name}"
        
        return from_email_id, sender_name

    def process_and_save_email_details(self, customer_uuid, application_uuid, email_conversation_obj: object, parent_email_obj, from_email_id,
                   sender_name: str|None = None, to: list[dict]|None = None, cc: list[dict]|None = None, 
                   bcc: list[dict]|None = None, email_subject: str|None = None, email_body: str|None = None, 
                   attachments: list[dict]|None = None):
    
        # Log to track the entry into the save_new_email function
        logger.info("In Create draft mail :: :: :: :: :: :: save_new_email")

        # Generate email_uuid
        email_uuid = generate_message_id()

        # Upload the email body to Azure Blob Storage if email_body is provided
        if email_body:
            email_body_url = self.azure_blob_manager.upload_data(
                data = email_body.encode('utf-8'),
                file_name = FileUploadNames.EMAIL_BODY_FILE_NAME.value.format(email_uuid=email_uuid,content_type=FileContentTypes.TEXT.value),
                over_write = True,
                customer_uuid = customer_uuid,
                application_uuid = application_uuid,
                channel_type = ChannelTypes.EMAIL.value,
                return_type = ReturnTypes.URL.value
            )

        #Save Email Conversation
          # If this is the first email in the conversation, create a new email conversation object
        if not email_conversation_obj:
            email_conversation_obj = self.email_conversation_dao.save_email_conversation(
                str(uuid.uuid4()),  # Generate a UUID for the email conversation
                customer_uuid, 
                None, 
                Action.need_assistance.value,  # Set an initial action (e.g., need assistance)
                None, 
                get_current_timestamp(),  # Set the current timestamp for creation
                get_current_timestamp(),  # Set the current timestamp for last updated time
                application_uuid
            )

        #Save Email 
        # Process parent email's dimension_action_json if parent_email_obj is provided
        if parent_email_obj:
             # If there's a parent email, prepend "RE: " to the subject line (indicating a reply)
            email_subject = "RE: " + email_subject
            data_json = parent_email_obj.dimension_action_json
            # Ensure that the data_json is converted to a dictionary (if it's a string)
            if data_json:
                if not isinstance(data_json, dict):
                    data_json = json.loads(data_json)
                
                # Remove specific keys from the dictionary (if present)
                data_json.pop("comment", None)
                data_json.pop("action", None)
            else:
                # Initialize data_json as an empty dictionary if None
                data_json = {}
        else:
            # If there's no parent email, set data_json to an empty dictionary
            data_json = {}

       
        # Save the email object to the database
        email_obj = self.email_dao.save_email(
            email_uuid ,   #Generate a unique message ID for the new email
            email_conversation_obj, 
            EmailActionFlowStatus.MANUALLY_HANDLED.value,  # Set email action flow status to manually handled
            EmailTaskStatus.DRAFT.value,  # Set email task status to draft
            data_json, 
            get_current_timestamp(),  # Set current timestamp for creation
            get_current_timestamp(),  # Set current timestamp for last updated time
            parent_email_obj  # Link the parent email object (if any)
        )

        #Save Email Info
        # Create the email info dictionary
        email_info = {
            'email_info_uuid': generate_message_id(),  # Generate a unique message ID for the email info
            'email_subject': email_subject,  # Set the email subject
            'email_body_url': email_body_url if email_body else None,  # Upload the email body and store the URL
            'attachments': attachments if attachments else [],  # Set attachments if any
            'sender': from_email_id,  # Set the sender email ID
            'sender_name': sender_name,  # Set the sender name
            'email_type': EmailType.NEW.value,  # Email type is set to NEW
            'email_meta_body': str(email_body[:255]) if email_body else None,
            'recipient': to[0].get('email'),  # Set the primary recipient (first one in the "to" list)
            'recipients': to,  # All recipients in the "to" field
            'cc_recipients': cc,  # Set CC recipients if any
            'bcc_recipients': bcc  # Set BCC recipients if any
        }

        # Save the email info object (storing metadata about the email)
        email_info_obj = self.email_info_dao.save_email_info(email_obj, email_info)

         # Update the email flow status if necessary (for both parent and conversation)
        self.__update_flow_statuses(email_obj, parent_email_obj, email_conversation_obj)

        # Return the email object, email info object, and the UUID of the email conversation
        return email_obj, email_info_obj, email_conversation_obj.email_conversation_uuid

    def __update_flow_statuses(self, email_obj, parent_email_obj, email_conversation_obj):
        # Update the email flow status if necessary (for both parent and conversation)
        if email_obj:
            # If there's a parent email and its status is OPEN, change it to PROCESSING
            if parent_email_obj and parent_email_obj.email_flow_status == EmailTaskStatus.OPEN.value:
                self.email_conversation_dao.update_email_flow_status(parent_email_obj, EmailActionFlowStatus.PROCESSING.value)
            
            # If the email conversation's flow status is OPEN, update it
            if email_conversation_obj.email_conversation_flow_status == EmailTaskStatus.OPEN.value:
                self.email_dao.update_email_conversation_flow_status(email_conversation_obj, EmailActionFlowStatus.PROCESSING.value)


            self.email_conversation_dao.update_timestamp(email_conversation_obj, get_current_timestamp())
            if email_conversation_obj.ticket_uuid:
                self.ticket_dao.update_timestamp(email_conversation_obj.ticket_uuid, get_current_timestamp())
    
    def build_draft_conversation_response(self, email_body, email: object, email_info: object, email_conversation_uuid: str):
        # Log entry for tracking function call
        logger.info("In build_conversation_response")

        # Retrieve sender's name if available
        if email_info.sender_name:
            sender_name = email_info.sender_name

        # Build the email info dictionary with various attributes from the email_info object
        email_info_dict = {
            'email_body_url': email_body,  # Downloaded email body content or the URL
            'attachments': email_info.attachments,  # Attachments associated with the email
            'sender': email_info.sender,  # Sender's email address
            'sender_name': email_info.sender_name,  # Sender's name (if provided)
            'email_type': email_info.email_type,  # Email type (e.g., new, reply, etc.)
            'recipient': email_info.recipient,  # Primary recipient
            'recipients': email_info.recipients,  # All recipients
            'cc_recipients': email_info.cc_recipients,  # CC recipients
            'bcc_recipients': email_info.bcc_recipients,  # BCC recipients
            "email_body_summary": email_info.email_body_summary,  # Summary of the email body (if applicable)
            "email_meta_body": email_info.email_meta_body,  # Metadata related to the email body
            "html_body": email_info.html_body,  # HTML version of the email body
            "extracted_order_details": email_info.extracted_order_details,  # Any extracted order details
            "validated_details": email_info.validated_details,  # Validated details from the email
            "verified": email_info.verified  # Flag indicating whether the email was verified
        }

        # Serialize the email object using the EmailSerializer
        serializer = EmailSerializer(email)
        serialized_data = serializer.data  # Serialized email data
        
        # Build the final email data dictionary
        email_data = {
            "email_conversation_uuid": email_conversation_uuid,  # UUID for the email conversation
            "email_uuid": serialized_data['email_uuid'],  # UUID for the email itself
            "sender_name": sender_name,  # Sender's name (set earlier)
            "email_subject": email_info.email_subject,  # Email subject
            "email_flow_status": serialized_data['email_flow_status'],  # Flow status of the email
            "email_status": serialized_data['email_status'],  # Status of the email (e.g., draft, sent)
            "parent_uuid": serialized_data['parent_uuid'],  # UUID of the parent email (if it's a reply)
            "email_info_json": email_info_dict,  # Detailed email info JSON (built earlier)
            "dimension_action_json": serialized_data['dimension_action_json'] if serialized_data['dimension_action_json'] else None,  # Action-related data (if any)
            "inserted_ts": serialized_data['inserted_ts'],  # Timestamp when the email was inserted
            "updated_ts": serialized_data['updated_ts'],  # Timestamp when the email was last updated
            "draft": None  # Placeholder for draft (can be set later if needed)
        }

        # Return the constructed email data dictionary
        return email_data

    @transaction.atomic
    def reply_to_mail(self, customer_uuid, application_uuid, user_uuid, validated_data):
        """
        This function is used to send the drafted mail as well as to edit the drafted mail(NU usecase).
        """
        # Extract values from the validated_data dictionary
        send = validated_data.get('send', None)
        email_uuid = validated_data.get('email_uuid')
        from_email_id = validated_data['from_email_id']
        in_reply_to = validated_data.get('in_reply_to', None)
        to = validated_data['to']
        cc = validated_data.get('cc', [])
        bcc = validated_data.get('bcc', [])
        subject = validated_data.get('subject', "")
        body = validated_data.get('body', None)
        attachments = validated_data.get('attachments', [])
        #For removing from Db (In Nu Use case)
        remove_attachments = validated_data.get('remove_attachments', [])

        # Retrieve email, parent email, and email conversation objects for the email being replied to
        email, email_conversation = self.get_email_and_conv(email_uuid)
        email_info_obj = self.email_info_dao.get_email_info(email.email_uuid)
        # Get the current date
        date = get_current_date_str()

        # If send is None or True - Send an email
        if send is None or send is True:
            
            # Authenticate SMTP and get server object and sender email
            #TODO Use Prem function

            # Perform profanity check only if send is None
            if send is None:
                profanity_response = check_profanity(body)
                if profanity_response is not True:
                    return profanity_response, False  # Early return if profanity check fails
            
            #Just the to email-ids as list
            email_to = [email_to_dict.get('email') for email_to_dict in to]
            #Just the cc email-ids as list
            cc_emails = [cc_dict.get('email') for cc_dict in cc]
            #Just the bcc email-ids as list
            bcc_emails = [bcc_dict.get('email') for bcc_dict in bcc]
            # Handle email body
            if not body and email_info_obj.email_body_url:
                body = self.azure_blob_manager.download_data_with_url(
                    email_info_obj.email_body_url).decode('utf-8')
            provider_name=self.email_server_cam_platform_dao.get_server_provider_name(customer_uuid=customer_uuid,application_uuid=application_uuid)
            if provider_name.lower()==EmailProvider.GMAIL.value.lower():
                smtp_server_obj, from_email_id = self.fetch_email_server_and_authenticate_smtp(customer_uuid,
                                                                                               from_email_id,application_uuid)


                # Attempt to send or reply to the email
                email_sent = send_or_reply_email(
                    email_info=email_info_obj,
                    smtp_server=smtp_server_obj,
                    message_id=email_uuid,
                    sender_email=from_email_id,
                    email_to=email_to,
                    subject=subject,
                    email_body=body,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                    attachments=attachments,
                    in_reply_to=in_reply_to,
                    date=date
                )
            elif provider_name.lower()==EmailProvider.OUTLOOK.value.lower():
                email_sent = self.__send_or_reply_outlook(
                    email_info=email_info_obj,
                    message_id=email_uuid,
                    sender_email=from_email_id,
                    email_to=email_to,
                    customer_uuid=customer_uuid,
                    application_uuid=application_uuid,
                    subject=subject,
                    email_body=body,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                    attachments=attachments,
                    in_reply_to=in_reply_to,
                    date=date
                )
            else:
                logger.info(f"Provider is other than Gmail and outlook {provider_name}")
                raise CustomException(f"Unknown provider for the customer {customer_uuid} and application {application_uuid}")

            # If sending fails, raise an error
            if not email_sent:
                raise CustomException(ErrorMessages.EMAIL_SENT_FAILED, status_code=status.HTTP_400_BAD_REQUEST)
            
            #Update the email timeline sent and by which user
            self.email_conversation_dao.update_timeline(email_conversation.email_conversation_uuid,email_conversation.email_activity,email.email_uuid,TimelineTypes.EmailSent.value,datetime_to_milliseconds(datetime.now()),user_uuid)
            # Process the email as sent (log, update status, etc.)
            self.process_and_save_email(send, customer_uuid, application_uuid, email_info_obj, email, email_conversation, body, attachments, from_email_id, to, cc, bcc, date)

            # If send=None, store the response as an example
            if send is None:
                self.add_response_as_example(email, body, user_uuid, customer_uuid, application_uuid)

            return SuccessMessages.EMAIL_SENT_SUCCESS, True  # Email sent successfully

        # If `send=False`, save the edited email as a draft(NU usecase)
        if self.save_edited_email(email_info_obj, email, date, subject, body, attachments, from_email_id, to, cc, bcc, remove_attachments,customer_uuid,application_uuid):
            return SuccessMessages.DRAFT_MAIL_UPDATED_SUCCESS, True  # Return success response for draft update
        else:
            # Raise exception if saving the draft fails
            raise CustomException(ErrorMessages.DRAFT_UPDATE_FAILED, status_code=status.HTTP_400_BAD_REQUEST)


    def __send_or_reply_outlook(self,email_info, message_id, sender_email, email_to, customer_uuid,application_uuid,subject=None, email_body=None,
                              cc_emails=None,
                              bcc_emails=None, attachments=None, in_reply_to=None, date=None):
        """
        This method replies to an email with attachments or sends a new email if message_id is None.

        :param sender_email: Sender's email address
        :param email_body: Body of the email
        :param cc_emails: List of CC email addresses
        :param bcc_emails: List of BCC email addresses
        :param attachments: List of attachment file paths
        :param in_reply_to: Message-ID of the email being replied to
        :param date: Date and time of the email
        :
        """
        pass
        logger.info("Sending or replying to email using Microsoft Graph API...")

        if subject is None:
            subject = email_info.email_subject

        # Case 1: Handle the scenario when attachments are present in email info but no attachments sent
        if email_info.attachments and not attachments:
            attachments = email_info.attachments  # Use the existing attachments from the record

        # Case 2: Append existing attachments with new attachments
        elif attachments and email_info.attachments:
            attachments = email_info.attachments + attachments  # Append new attachments

        # Prepare the attachment list
        attachment_list = []
        if attachments:
            for attachment in attachments:
                with open(attachment, 'rb') as file:
                    file_content = file.read()
                    base64_content = base64.b64encode(file_content).decode('utf-8')
                    attachment_list.append({
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": attachment.split("/")[-1],
                        "contentBytes": base64_content
                    })

        # Create the email message object
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": email_body
                },
                "toRecipients": [{"emailAddress": {"address": recipient}} for recipient in email_to],
                "ccRecipients": [{"emailAddress": {"address": recipient}} for recipient in (cc_emails or [])],
                "bccRecipients": [{"emailAddress": {"address": recipient}} for recipient in (bcc_emails or [])],
                "attachments": attachment_list
            }
        }

        if message_id and in_reply_to:
            # If replying, add headers (use 'X-' prefix as required by Microsoft Graph)
            email_data["message"]["internetMessageHeaders"] = [
                {"name": "X-In-Reply-To", "value": in_reply_to},
                {"name": "X-References", "value": in_reply_to}
            ]
        # Send the email using Graph API
        end_point = f"{OutlookUrlsEndPoints.BASE_URL.value}/users/{sender_email}/sendMail"
        mapping_id,microsoft_client_id,microsoft_tenant_id=self.email_server_cam_platform_dao.get_outlook_server_details(customer_uuid,application_uuid)
        secret_name = SECRET_NAME_FORMAT_PREFIX + str(mapping_id)
        response = hit_and_retry_with_new_token(end_point,secret_name,microsoft_client_id,microsoft_tenant_id,email_data,"POST")
        if response.ok:
            return True
        return False

    def add_response_as_example(self,email,response_body,user_uuid,customer_uuid,application_uuid):
        logger.info("In EmailConversationViewSet :: add_response_as_example")
        dimension_action_json=email.dimension_action_json
        metadata= {CsrChromaDbFields.CATEGORY.value:CategeriesForPersonalization.RESPONSE_GENERATION_CATEGORY.value,
                CsrChromaDbFields.CSR_UUID.value:user_uuid,
                CsrChromaDbFields.INTENT.value:str(dimension_action_json["intent"]["name"]),
                CsrChromaDbFields.SUB_INTENT.value:str(dimension_action_json["intent"]["sub_intent"]["name"]),
                CsrChromaDbFields.SENTIMENT.value:str(dimension_action_json["sentiment"]["name"]),
                CsrChromaDbFields.FILE_URL.value:'',
                CsrChromaDbFields.IS_DEFAULT.value:False,
                CsrChromaDbFields.TIME_STAMP.value:datetime_to_milliseconds(datetime.now())}
        
        try:

            collection_name=self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid=customer_uuid,application_uuid=application_uuid)
            ids = self.chroma_vector_store.add_emails_and_metadata(metadata=metadata,emails=response_body,collection_name=collection_name)
            logger.debug(f"Successfully added mail conversation to chromadb {metadata} {response_body}")

            self.__delete_older_response(collection_name=collection_name,no_of_responses_to_store=3,user_uuid=user_uuid)

            return ids
        except Exception as error:
            logger.error(f"Error while adding mail conversation to chromadb {error}")
            return None
        
    def __delete_older_response(self,collection_name,no_of_responses_to_store,user_uuid):
        logger.info("In EmailConversationViewSet :: delete_older_response")
        metadata=[{CsrChromaDbFields.CATEGORY.value:CategeriesForPersonalization.RESPONSE_GENERATION_CATEGORY.value},
                  {CsrChromaDbFields.CSR_UUID.value: user_uuid},
                  {CsrChromaDbFields.FILE_URL.value:''},
                  {CsrChromaDbFields.IS_DEFAULT.value:False}]
        chromadb_output_of_responses=self.chroma_vector_store.get_records_by_metadata(metadata_combination=metadata,collection_name=collection_name)
        # Extract IDs and timestamps in a single step
        responses = [
            (int(metadata[CsrChromaDbFields.TIME_STAMP.value]), chromadb_output_of_responses['ids'][i])
            for i, metadata in enumerate(chromadb_output_of_responses['metadatas'])
        ]

        # Sort emails by timestamp (latest first)
        responses.sort(key=lambda x: x[0], reverse=True)

        if len(responses) <= no_of_responses_to_store:
            logger.debug("Number of emails is less than or equal to the number of responses to keep. No emails deleted.")
            return  # No emails to delete

        # Get IDs to delete using slicing (keeping the latest n emails)
        ids_to_delete = [email[1] for email in responses[no_of_responses_to_store:]]  # Deletes emails after the first n

        # Delete emails by ID
        if ids_to_delete:
            self.chroma_vector_store.delete_record_by_id(ids_to_delete,collection_name)
            logger.info(f"Deleted emails with IDs: {ids_to_delete}")
        else:
            logger.info("No emails to delete.")


    def save_edited_email(self, email_info_obj, email, date, subject=None, body=None, attachments=None, from_email_id=None, to=None, cc=None, bcc=None, remove_attachments=None,customer_uuid=None,application_uuid=None):
        try:
            # Update the timestamp if date is provided
            email.updated_ts = get_timestamp_from_date(date)
            
            # Update the subject if provided
            if subject:
                email_info_obj.email_subject = subject

            # Update the body and upload it to storage if provided
            if body:
                body_url = self.upload_or_update_email_body(body, email_info_obj.email_body_url,customer_uuid,application_uuid,email.email_uuid)
            else:
                body_url = email_info_obj.email_body_url  # Keep the existing body URL
            
            # Initialize updated_attachments with current attachments
            updated_attachments = email_info_obj.attachments
            # Case 1: Remove any attachments that are flagged for removal
            if remove_attachments:
                updated_attachments = [att for att in email_info_obj.attachments if att.get('file_attachment_uuid') not in remove_attachments]
                #TODO confirm with lavan to delete from azure storage or they are deleting it
                if len(updated_attachments)==len(email_info_obj.attachments):
                    raise CustomException(ErrorMessages.ATTACHMENTS_NOT_REMOVED, status_code=status.HTTP_400_BAD_REQUEST)

            # Case 2: Append new attachments if provided
            if attachments:
                updated_attachments.extend(attachments)
            
            # Update other fields if provided, otherwise keep the existing ones
            
            email_info_obj.email_body_url = body_url
            email_info_obj.attachments = updated_attachments
            email_info_obj.sender = from_email_id or email_info_obj.sender
            email_info_obj.recipients = to or email_info_obj.recipients
            email_info_obj.cc_recipients = cc or email_info_obj.cc_recipients
            email_info_obj.bcc_recipients = bcc or email_info_obj.bcc_recipients
            email_info_obj.email_meta_body = str(body[:255]) if body else None
            # Update the email conversation with the modified email info
            email_info_obj.save()

            # Save only if changes were made
            email.save()

            return True

        except Exception as e:
            # Log the error if necessary
            logger.error(f"Error saving edited email: {e}", exc_info=True)
            return False 

    def get_email_and_conv(self, email_uuid):
        # Retrieve the email object using its UUID from the email_conversation_dao
        email = self.email_dao.get_email(email_uuid)
        if email is None:
            raise CustomException(ErrorMessages.EMAIL_NOT_FOUND,status_code=status.HTTP_404_NOT_FOUND)
        
        # Retrieve the email conversation object using the email conversation UUID from the email
        email_conversation = self.email_conversation_dao.get_email_conversation_obj(email.email_conversation_uuid.email_conversation_uuid)
        email_conversation = email_conversation.first()
        # Raise an exception if the email conversation doesn't exist
        if email_conversation is None:
            raise CustomException(ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)

        # Return the retrieved email, parent email, and email conversation
        return email, email_conversation


    def fetch_email_server_and_authenticate_smtp(self, customer_uuid, from_email_id, application_uuid):
        """
        Method to fetch email server details and authenticate 
        """
        server_type = EmailReplyParams.SMTP.value
        #Fetch the associated SMTP Server Details for Customer and Application 
        smtp_server_url,smtp_server_port  = self.email_server_dao.get_email_server(server_type, customer_uuid, application_uuid)

        #Fetch the associated Email Settings  Details (emailId and Password) for Customer and Application 
        encrypted_password, email_id = self.user_email_setting_dao.get_mail_and_password(customer_uuid, application_uuid, from_email_id)

        # Decrypt the password and authenticate
        password = decrypt_password(encrypted_password)
        #TODO Use Prem Code
        smtp_server_obj = authenticate_smtp_credentials(
            smtp_server_url,
            smtp_server_port,
            email_id,
            password
        )

        if smtp_server_obj is None:
            raise CustomException(ErrorMessages.SMTP_AUTHENTICATION_FAILED, status_code=status.HTTP_400_BAD_REQUEST)

        return smtp_server_obj, email_id
    
    def process_and_save_email(self, send, customer_uuid, application_uuid, email_info_obj, email, email_conversation, body, attachments, from_email_id, to, cc, bcc, date):
        """
        Processes and updates the details of a sent email, including the body, attachments, 
        and metadata, and updates the status of the associated email conversation.
        """
        # Set email status to SENT and update the timestamps based on the current date
        email.email_status = EmailTaskStatus.SENT.value
        inserted_ts = get_timestamp_from_date(date)
        email.inserted_ts = inserted_ts
        email.updated_ts = inserted_ts
        self.email_conversation_dao.update_timestamp(email_conversation, inserted_ts)
        if email_conversation.ticket_uuid:
            self.ticket_dao.update_timestamp(email_conversation.ticket_uuid, inserted_ts)

        # If a new email body is provided, upload or update the body in Azure Blob Storage
        if body:
            body_url = self.upload_or_update_email_body(body, email_info_obj.email_body_url,customer_uuid,application_uuid,email.email_uuid)
        else:
            # If no new body, retain the existing email body URL
            body_url = email_info_obj.email_body_url

        # Case 1: Handle the scenario when no attachments are present in email info and but no attachments sent
        if email_info_obj.attachments and not attachments:
            attachments = email_info_obj.attachments  # Use the existing attachments from the record

        # Case 2: Append existing attachments with new attachments
        elif attachments and email_info_obj.attachments:
            attachments = email_info_obj.attachments + attachments  # Append new attachments
        
        # Update the email info
        email_info_obj.email_body_url = body_url
        email_info_obj.attachments = attachments
        email_info_obj.sender = from_email_id
        email_info_obj.recipients = to
        email_info_obj.cc_recipients = cc
        email_info_obj.bcc_recipients = bcc
        email_info_obj.email_meta_body = str(body[:255]) if body else None
        # Update the flow status of the email and the email conversation based on the current status
        self.update_email_flow_status(email, email_conversation)
        # Save the updated email info object to the database
        email_info_obj.save()

        
        # If the send is None(product case), generate a summary for the email
        if send is None:
            #TODO use the refactored code from EmailMicroservice
            conversation_uuid, email_activity = generate_email_summary(body, email_info_obj.sender_name,
                       email_info_obj.recipient,
                       email.email_conversation_uuid.email_conversation_uuid,customer_uuid,application_uuid,email_conversation
                    )
            email_summary = generate_detailed_summary(email_body=body,customer_uuid=customer_uuid,application_uuid=application_uuid)
            if email_summary is not None:
                email_info_obj.email_body_summary=email_summary
                email_info_obj.save()
            self.email_conversation_dao.update_email_activity_in_email_conversation(conversation_uuid=conversation_uuid,email_activity=email_activity)

    def upload_or_update_email_body(self, body, email_body_url,customer_uuid,application_uuid,email_uuid):
        # If the email body URL already exists, update the existing body in Azure Blob Storage
        if email_body_url:
            file_name = self.__get_file_name_from_url(email_body_url)
            return self.azure_blob_manager.update_data_with_url(email_body_url, body.encode('utf-8'), file_name)
        else:
            # If no body URL exists, upload the new email body to Azure Blob Storage
            email_body_url = self.azure_blob_manager.upload_data(
                data=body.encode('utf-8'),
                file_name=FileUploadNames.EMAIL_BODY_FILE_NAME.value.format(email_uuid=email_uuid, content_type=FileContentTypes.TEXT.value),
                over_write=True,
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                channel_type=ChannelTypes.EMAIL.value,
                return_type=ReturnTypes.URL.value
            )
            return email_body_url

    def update_email_flow_status(self, email, email_conversation):

        # If the email flow status is 'NEED_ASSISTANCE', mark both the email and conversation as 'AI_ASSISTED'
        if email.email_flow_status == EmailActionFlowStatus.NEED_ASSISTANCE.value:
            email.email_flow_status = EmailActionFlowStatus.AI_ASSISTED.value
            email_conversation.email_conversation_flow_status = EmailActionFlowStatus.AI_ASSISTED.value
            if email_conversation.ticket_uuid:
                self.ticket_dao.update_ticket_status(email_conversation.ticket_uuid.ticket_uuid, EmailActionFlowStatus.AI_ASSISTED.value)

        # If the email flow status is 'NEED_ATTENTION', mark both the email and conversation as 'MANUALLY_HANDLED'
        elif email.email_flow_status == EmailActionFlowStatus.NEED_ATTENTION.value or email.email_flow_status == EmailActionFlowStatus.MANUALLY_HANDLED.value:
            email.email_flow_status = EmailActionFlowStatus.MANUALLY_HANDLED.value
            email_conversation.email_conversation_flow_status = EmailActionFlowStatus.MANUALLY_HANDLED.value
            if email_conversation.ticket_uuid:
                self.ticket_dao.update_ticket_status(email_conversation.ticket_uuid.ticket_uuid, EmailActionFlowStatus.MANUALLY_HANDLED.value)
        
        # Save the updated objects to the database
        email.save()
        email_conversation.save()
        
    def get_mail_conversation_count_by_ticket_uuid(self, ticket_uuid):
        """
        Retrieves the count of email records associated with a given conversation UUID.
        
        Parameters:
            ticket_uuid (str): UUID of the ticket.

        Returns:
            int: Count of email records associated with the provided UUID.
        """
        logger.info(f"Fetching email conversation for UUID: {ticket_uuid}")
        #Get all the email records for the given email_conversation
        email_conversation = self.email_conversation_dao.get_email_conversation_by_ticket_uuid(ticket_uuid)
        #Count of total email records
        conversation_count = len(email_conversation)
        logger.info(f"Email conversation count: {conversation_count}")
        result = {"email_conversation_count": conversation_count}

        return result

    def get_mails_by_email_uuids(self,email_uuids_list):

        """
        Build structured data for each email.
        
        Parameters:
            email_uuids_list (List): List containing email records.

        Returns:
            list: List of structured emails data.
        """
        emails = self.email_dao.get_emails(email_uuids_list)
        # Get the last inserted record based on inserted_ts
        last_inserted_record = max(emails, key=lambda x: x['inserted_ts'])
        emails_data = []
        for email in emails:
            email_data = self.build_conversation_data(email, last_inserted_record)

            # Check if this record is a draft
            if email['email_status'] == "Draft":
                self.add_draft_conversation(emails_data, email_data)
            else:
                emails_data.append(email_data)

        result = {"emails_data": emails_data}

        return result


    def process_attachment_by_blob_url(self, customer_uuid, application_uuid, blob_url):
        """
        Processes a PDF file from the provided Azure Blob Storage URL by sending its details 
        to an Azure Event Hub for further processing.

        Args:
            customer_uuid (str): Unique identifier for the customer.
            application_uuid (str): Unique identifier for the application.
            blob_url (list): List of URLs of the PDF files stored in Azure Blob Storage.

        Raises:
            Exception: If any error occurs while sending data to the Event Hub.
        """
        wise_flow_uuid = self.wiseflow.get_wiseflow(customer_uuid, application_uuid,ChannelTypesUUID.EMAIL.value)

        step_uuid = self.wiseflow.get_step_uuid(wise_flow_uuid = wise_flow_uuid, step_name = PDF_PROCESSING_STEP_NAME)

        # Prepare the event data to be sent to the Event Hub
        eventhub_json = {
            "step_uuid": step_uuid,
            "data": {
                "customer_uuid": customer_uuid,
                "application_uuid": application_uuid,
                "urls": blob_url
            }
        }
        # Retrieve configuration settings for Event Hub and Blob Storage
        producer_eventhub_name = settings.EMAIL_PDF_PROCESSING_EVENTHUB_TOPIC
        eventhub_connection_string = settings.EVENTHUB_CONNECTION_STR
        eventhub_blob_container_name = settings.BLOB_CONTAINER_NAME
        checkpoint_storage_connection_string = settings.CHECKPOINT_STORAGE_CONNECTION_STR
        
        try:
            # Create a dictionary with configuration details for the Event Hub
            # producing data into eventhub
            key_word_args = dict()
            key_word_args.update({"producer_eventhub_name": producer_eventhub_name,
                                  "consumer_eventhub_name": None,
                                  "connection_string": eventhub_connection_string,
                                  "blob_container_name": eventhub_blob_container_name,
                                  "storage_connection_string": checkpoint_storage_connection_string
                                })
            logger.debug(f"eventhub config :: {key_word_args}")
            # Instantiate the Azure Event Hub service using the configuration
            azure_eventhub_service = QueuingServiceFactory.instantiate("AzureEventHubService", key_word_args)
            # Create a producer for the Event Hub
            event_hub_producer = azure_eventhub_service.create_producer()
            # Send the event data (PDF file details) to the Event Hub
            event_hub_producer.send_event_data_batch(eventhub_json)

        except Exception as e:
            logger.error(
                f"error while producing data into EventHub with topic: {producer_eventhub_name} for customer_uuid:{customer_uuid} and application_uuid:{application_uuid} with error: {e}")
            raise e 
