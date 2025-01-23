from abc import ABC, abstractmethod


class IStreamFileService(ABC):
    """
        Interface for handling streaming bytes data of files present in Azure Blob Storage
    """
    @abstractmethod
    def stream_blob_file(self, blob_name_or_url):
        """
            method to stream file data present in azure storage with blob_name
            Args:
                blob_name or blob_url (str): unique identifier of file
            Returns:
                chunks data of the file
        """