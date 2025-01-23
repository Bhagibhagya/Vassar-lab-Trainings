from abc import ABC, abstractmethod
from typing import List, Dict
from ChatBot.dataclasses.attachment_dataclass import AttachmentUploadParams, AttachmentMetadata

class AttachmentServiceInterface(ABC):
    @abstractmethod
    def upload_attachments(self, upload_params: AttachmentUploadParams):
        """
        Upload multiple attachments and return their metadata.
        """
        pass

    @abstractmethod
    def create_attachment_metadata(self, upload_result: Dict[str, str], file_name: str):
        """
        Create and return the metadata for the uploaded attachment.
        """
        pass
