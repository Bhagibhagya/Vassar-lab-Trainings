from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AttachmentUploadParams:
    """
    Data class for holding parameters for uploading attachments.

    Attributes:
        files (Dict[str, Any]): The files to be uploaded.
        customer_id (str): The UUID of the customer.
        app_id (str): The UUID of the application.
        channel_id (str): The UUID of the channel type.
        conversation_id (str): The UUID of the conversation.
    """
    files: Dict[str, Any]
    customer_uuid: str
    application_uuid: str
    chat_channel_uuid: str
    conversation_uuid: str


@dataclass
class AttachmentMetadata:
    """
    Data class for holding metadata of uploaded attachments.

    Attributes:
        blob_name (str): The name of the blob in Azure Blob Storage.
        file_name (str): The original name of the uploaded file.
    """
    blob_name: str
    file_name: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the AttachmentMetadata instance to a dictionary.
        """
        return {
            'blob_name': self.blob_name,
            'file_name': self.file_name
        }
