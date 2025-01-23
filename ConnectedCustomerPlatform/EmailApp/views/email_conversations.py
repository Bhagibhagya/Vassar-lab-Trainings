from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from EmailApp.utils import  validate_input, validate_uuids_dict
from EmailApp.constant.error_messages import AzureBlobErrorMessages,ErrorMessages
import logging
from django.db.models import Q
from EmailApp.serializers import DraftMailSerializer, EmailConversationSerializer, SendMailSerializer
from EmailApp.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException, ResourceNotFoundException
from ConnectedCustomerPlatform.responses import CustomResponse
from EmailApp.constant.success_messages import SuccessMessages
from EmailApp.constant.constants import EmailDashboardParams, EmailConversationParams, TicketParams,BlobConstants


logger = logging.getLogger(__name__)

from EmailApp.services.impl.email_conversation_impl import EmailConversationServiceImpl
class EmailConversationViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmailConversationViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print(f"Inside EmailConversationViewSet - Singleton Instance ID: {id(self)}")
            self.email_conversation_service = EmailConversationServiceImpl()
            self.initialized = True

    @action(detail=False, methods=['post'])
    def get_email_conversations(self, request):
        """
        API to retrieve email conversations based on customer uuid, application uuid , email_conversation_flow_status and other filters
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: :: get_email_conversations ")

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        validate_uuids_dict({
                EmailDashboardParams.APPLICATION_UUID.value:application_uuid,
                EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid,
                EmailDashboardParams.USER_UUID.value : user_uuid
        })

        email_conversation_serializer = EmailConversationSerializer(data=request.data)

        if not email_conversation_serializer.is_valid():
            raise CustomException(email_conversation_serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        response_data = self.email_conversation_service.get_email_conversations(customer_uuid, application_uuid,user_uuid, email_conversation_serializer.validated_data)

        return CustomResponse(result=response_data,code=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_mail_conversation_by_ticket_uuid(self, request):
        """
        API endpoint to retrieve emails (thread) by email conversation UUID.
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: :: get_mail_conversation_by_ticket_uuid")
        
        ticket_uuid = request.GET.get(TicketParams.TICKET_UUID.value)


        if ticket_uuid is None:
            raise InvalidValueProvidedException(ErrorMessages.TICKET_UUID_NOT_NULL)

        response_data = self.email_conversation_service.get_mail_conversation_by_ticket_uuid(ticket_uuid)

        return CustomResponse(result=response_data,code=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'])
    def get_content_from_url(self, request):
        """
        API endpoint to retrieve content from url.
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: :: get_content_from_url")

        file_url = request.GET.get(EmailConversationParams.FILE_URL.value)

        if not file_url:
            raise InvalidValueProvidedException(ErrorMessages.FILE_URL_NULL_ERROR)
        
        file_content = self.email_conversation_service.get_content_from_url(file_url)

        return CustomResponse(result=file_content, code=status.HTTP_200_OK)


    @action(detail=False, methods=['post'])
    def post_order_details_info(self, request):
        """ 
        Updates the order details and uploads into storage and pushes data to eventhub to trigger generate response
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: :: post_order_details ")

        email_uuid = request.data.get('email_uuid')
        details_extracted_json = request.data.get('details_extracted_json')
        attachment_id = request.data.get("attachment_id")
        file_url = request.data.get("file_url")
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        # Validate user UUID
        if not validate_input(user_uuid):
            raise CustomException(ErrorMessages.USER_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        if not email_uuid:
            raise CustomException(ErrorMessages.EMAIL_UUID_NULL_ERROR, status_code=status.HTTP_400_BAD_REQUEST)

        if not details_extracted_json:
            raise CustomException(detail=ErrorMessages.DETAILS_EXTRACTED_NULL_ERROR,status_code=status.HTTP_400_BAD_REQUEST)
        if not attachment_id:
            raise CustomException(detail= ErrorMessages.ATTACHMENT_ID_NOT_FOUND, status_code= status.HTTP_400_BAD_REQUEST)
        if not file_url:
            raise CustomException(detail= ErrorMessages.FILE_URL_NULL_ERROR, status_code= status.HTTP_400_BAD_REQUEST)

        response_data = self.email_conversation_service.post_order_details_info(email_uuid,details_extracted_json,file_url, attachment_id, user_uuid)

        return CustomResponse(result={"message": response_data}, code=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def get_downloadable_urls(self, request):
        """ 
        Parameters (query params):
            -List of urls (required): "file_urls"

        Returns:
           list of downloadable url(presigned urls) and the metadata of the attachments
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: :: get_downloadable_urls ")

        files_url_list = request.data.get(EmailConversationParams.FILES_URL_LIST.value)

        if files_url_list is None or not isinstance(files_url_list, list) or len(files_url_list)==0:
            raise InvalidValueProvidedException(ErrorMessages.FILES_URL_LIST_NULL_ERROR)
        
        files_data = self.email_conversation_service.get_downloadable_urls(files_url_list)

        return CustomResponse(result=files_data, code=status.HTTP_200_OK)
    

    @action(detail=False, methods=['delete'])
    def delete_draft_mail(self, request):
        """
        This Method is to Delete a draft mail.
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: ::delete_draft_mail")
        
        email_uuid = request.GET.get(EmailConversationParams.EMAIL_UUID.value)

        if not email_uuid:
            raise ResourceNotFoundException(ErrorMessages.EMAIL_UUID_NULL_ERROR)
        
        self.email_conversation_service.delete_draft_mail(email_uuid)

        return CustomResponse(result = SuccessMessages.DRAFT_MAIL_DELETED_SUCCESS,code=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['post'])
    def create_draft_mail(self, request):
        """
        This function creates a draft mail.
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: ::create_draft_mail")

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)

        validate_uuids_dict({
                EmailDashboardParams.USER_UUID.value:user_uuid,
                EmailDashboardParams.APPLICATION_UUID.value:application_uuid,
                EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid
        })

        serializer = DraftMailSerializer(data=request.data)
    
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        response_data = self.email_conversation_service.create_draft_mail(customer_uuid, application_uuid, user_uuid, serializer.validated_data)

        return CustomResponse(result={"message": response_data}, code=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def reply_to_mail(self, request):
        """
        This function is used to send the drafted mail as well as to edit the drafted mail(NU usecase).

        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: ::reply_to_mail")

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        #Validate Headers
        validate_uuids_dict({
                EmailDashboardParams.USER_UUID.value:user_uuid,
                EmailDashboardParams.APPLICATION_UUID.value:application_uuid,
                EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid
        })
        #Validate Payload using serialiser
        serializer = SendMailSerializer(data=request.data)
    
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        response_data, is_email_sent = self.email_conversation_service.reply_to_mail(customer_uuid, application_uuid, user_uuid, serializer.validated_data)
        #If the mail is sent successfully
        if is_email_sent is True:
            return CustomResponse(result=response_data, code=status.HTTP_201_CREATED)
        #If the mail is not sent
        return CustomResponse(result=response_data, status=False, code=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def get_mail_conversation_count_by_ticket_uuid(self, request):
        """
        API endpoint to retrieve the count of emails associated with a given email conversation UUID.
        """
        logger.info("In email_conversations.py :: EmailConversationViewSet :: get_mail_conversation_count_by_ticket_uuid")
        
        ticket_uuid = request.GET.get(TicketParams.TICKET_UUID.value)

        if ticket_uuid is None or len(ticket_uuid.strip()) == 0:
            raise InvalidValueProvidedException(ErrorMessages.TICKET_UUID_NOT_NULL)

        # Retrieve the count using the service function
        response_data = self.email_conversation_service.get_mail_conversation_count_by_ticket_uuid(ticket_uuid)

        return CustomResponse(result=response_data, code=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def get_mails_by_email_uuids(self, request):
        """
        API endpoint to retrieve emails (thread) by email UUIDs List.
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: :: get_mails_by_email_uuids")
        
        email_uuids_list = request.data.get(EmailConversationParams.EMAIL_UUIDS_LIST.value)

        if email_uuids_list is None or not isinstance(email_uuids_list, list) or len(email_uuids_list)==0:
            raise InvalidValueProvidedException(ErrorMessages.EMAIL_UUID_LIST_ERROR)

        response_data = self.email_conversation_service.get_mails_by_email_uuids(email_uuids_list)
        
        return CustomResponse(result=response_data,code=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def process_attachment_by_blob_url(self, request):
        #TODO add swagger code
        """
        API endpoint to raise event using blob url containing attachment.
        """
        logger.info("In email_conversations.py :: :: ::  EmailConversationViewSet :: :: :: process_pdf_by_url")

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        #Validate Headers
        validate_uuids_dict({
                EmailDashboardParams.APPLICATION_UUID.value:application_uuid,
                EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid
        })
        
        blob_url_list = request.data.get(BlobConstants.BLOB_URL_LIST)

        if blob_url_list is None or not isinstance(blob_url_list, list) or len(blob_url_list)==0:
            logger.error("Invalid blob_url provided: %s", blob_url_list)
            raise InvalidValueProvidedException(AzureBlobErrorMessages.BLOB_URL_NULL_ERROR)
        self.email_conversation_service.process_attachment_by_blob_url(customer_uuid, application_uuid, blob_url_list)
        
        return CustomResponse(result=SuccessMessages.EVENT_RAISED_SUCCESSFULLY,code=status.HTTP_200_OK)
