import inspect
import logging
import uuid
from typing import List, Dict
from ChatBot.constant.constants import Constants, FileUploadNames
from ChatBot.services.interface.attachments_service_interface import AttachmentServiceInterface
from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.dataclasses.attachment_dataclass import AttachmentUploadParams, AttachmentMetadata
from django.conf import settings

from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory

logger = logging.getLogger(__name__)

class AttachmentServiceImpl(AttachmentServiceInterface):
    """
    ViewSet for handling attachment uploads to Azure Blob Storage.
    Implements the Singleton pattern to ensure a single instance.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of class AttachmentServiceImpl(AttachmentServiceInterface): exists.
        """
        if cls._instance is None:
            cls._instance = super(AttachmentServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the service only once for the singleton instance.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info("Initializing AttachmentServiceImpl Singleton Instance")
            self.azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))
            logger.info(f"AttachmentServiceImpl Singleton Instance ID: {id(self)}")
            self.initialized = True

    def upload_attachments(self, upload_params: AttachmentUploadParams):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
        Upload multiple attachments and return their metadata.
        """
        if not upload_params.files:
            raise CustomException(Constants.NO_FILE_PROVIDED)

        attachment_metadata = []
        for key, attachment in upload_params.files.items():
            file_name = FileUploadNames.ATTACHMENTS_FILE_NAME.value.format(chat_uuid=upload_params.conversation_uuid, attachment_name=attachment.name)
            blob_name = self.azure_blob_manager.upload_data(data=attachment.read(),file_name=file_name,over_write=True,customer_uuid=upload_params.customer_uuid,
                                                         application_uuid=upload_params.application_uuid,channel_type=Constants.CHAT)

            upload_result = {
                Constants.BLOB_NAME: blob_name
            }
            attachment_metadata.append(self.create_attachment_metadata(upload_result, attachment.name))

        return attachment_metadata

    def create_attachment_metadata(self, upload_result: Dict[str, str], file_name: str) -> AttachmentMetadata:
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
        Create and return the metadata for the uploaded attachment.
        """
        attachment = AttachmentMetadata(
            blob_name=upload_result[Constants.BLOB_NAME],
            file_name=file_name
        )
        return attachment.to_dict()
