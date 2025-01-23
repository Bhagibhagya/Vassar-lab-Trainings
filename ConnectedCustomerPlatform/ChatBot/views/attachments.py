import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from ChatBot.services.impl.attachments_service_impl import AttachmentServiceImpl
from ChatBot.dataclasses.attachment_dataclass import AttachmentUploadParams, AttachmentMetadata
from ConnectedCustomerPlatform.exceptions import CustomException
from typing import List
from ChatBot.constant.constants import Constants
from ChatBot.utils import validate_input
from ChatBot.constant.error_messages import ErrorMessages

from ConnectedCustomerPlatform.responses import CustomResponse
from ConnectedCustomerPlatform.utils import Utils

# Configure logging
logger = logging.getLogger(__name__)

class AttachmentsViewSet(ViewSet):
    """
    ViewSet for handling attachment uploads to Azure Blob Storage.
    Implements the Singleton pattern to ensure a single instance.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of AttachmentsViewSet exists.
        """
        if cls._instance is None:
            cls._instance = super(AttachmentsViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the service only once for the singleton instance.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info("Initializing AttachmentsViewSet Singleton Instance")
            self.attachment_service = AttachmentServiceImpl()
            logger.info(f"AttachmentsViewSet Singleton Instance ID: {id(self)}")
            self.initialized = True


    @action(detail=False, methods=['post'])
    def upload_attachment(self, request):
        """
        Handle the uploading of attachments.

        Args:
            request: The HTTP request containing the attachments and metadata.

        Returns:
            Response: The response containing the metadata of uploaded attachments or an error message.
        """
        # Retrieve metadata from the request headers and bod
        customer_uuid, application_uuid, _ = Utils.get_headers(request.headers)
        chat_channel_uuid = Constants.CHAT_CHANNEL_TYPE_UUID
        conversation_uuid = request.data.get('chat_conversation_uuid')
        if not validate_input(conversation_uuid):
            raise CustomException(ErrorMessages.CONVERSATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        # Create an instance of AttachmentUploadParams
        upload_params = AttachmentUploadParams(
            files=request.FILES,
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            chat_channel_uuid=chat_channel_uuid,
            conversation_uuid=conversation_uuid
        )

        try:
            logger.info("Starting attachment upload process.")
            # Call the service to process and upload attachments
            attachment_metadata = self.attachment_service.upload_attachments(upload_params)
            logger.info("Attachments uploaded successfully.")
            return CustomResponse(attachment_metadata)
        except CustomException as e:
            logger.error(f"Error uploading attachments: {str(e)}")
            raise CustomException({"error": str(e)})

