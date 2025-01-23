from abc import ABC, abstractmethod
from typing import Optional, IO
import typing_extensions

from ce_shared_services.cloud_storage.azure.constants import ReturnTypes


class ICloudStorageManager(ABC):

    @abstractmethod
    def upload_file(self, file_path: str, over_write: bool, customer_uuid: str,
                    application_uuid: str, channel_type: str,max_concurrency :int=None,max_retries: int=None, file_name: Optional[str] = None,
                    content_type: Optional[str] = None, return_type: str = ReturnTypes.BLOB,) -> str:
        """
        Uploads a file from the given file path to Azure Blob Storage.

        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param file_path: Path to the local file to be uploaded.
        :param over_write: To overwrite in the existing blob(if present) or not
        :param file_name: Name of the file (used for blob naming) or a path for further organization within the blob structure.
        :param customer_uuid: UUID of the customer(mandatory).
        :param application_uuid: UUID of the application(mandatory).
        :param channel_type: Channel type (used for blob organization)mandatory.
        :param content_type: Optional content type.
        :param return_type: Specify 'url' to return the blob URL; otherwise, blob name is returned.
        :return: URL or blob name based on return_type.
        """

        pass

    @abstractmethod
    def upload_data(self, data: bytes, file_name: str, over_write: bool, customer_uuid: str,
                    application_uuid: str, channel_type: str,max_concurrency :int=None,max_retries: int=None,
                    content_type: Optional[str] = None, return_type: str = ReturnTypes.BLOB) -> str:
        """
        Uploads binary data to Azure Blob Storage.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param data: Binary data to be uploaded.Recommended to provide data with utf-8 encoded bytes if storing strings,etc. if storing strings,etc
        :param file_name: Name of the file or a path for further organization within the blob structure.
        :param over_write: To overwrite in the existing blob(if present) or not
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param channel_type: Channel type (used for blob organization).
        :param content_type: Optional content type.
        :param return_type: Specify 'url' to return the blob URL; otherwise, blob name is returned.
        :return: URL or blob name based on return_type.
        """

        pass


    @abstractmethod
    def update_file(self, blob_name: str, file_path: str,max_concurrency :int=None,max_retries: int=None, return_type: str = ReturnTypes.BLOB) -> str:
        """
        Updates an existing blob with a new file.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the existing blob to be updated.
        :param file_path: Local file path of the new file to upload.
        :param return_type: Specify 'url' to return the blob URL; otherwise, blob name is returned.
        :return: URL or blob name based on return_type.
        """

        pass


    @abstractmethod
    def update_file_with_url(self, blob_url: str, file_path: str,max_concurrency :int=None,max_retries: int=None) -> str:
        """
        Updates a file using its URL.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to be updated.
        :param file_path: Local file path of the new file to upload.
        :return: URL of the updated blob.
        """

        pass

    @abstractmethod
    def update_data(self, blob_name: str, data: bytes, file_name: str, max_concurrency :int=None,max_retries: int=None,return_type: str = ReturnTypes.BLOB) -> str:
        """
        Updates an existing blob with new binary data.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the existing blob to be updated.
        :param data: Binary data to upload to the blob.Recommended to provide data with utf-8 encoded bytes if storing strings,etc. if storing strings,etc
        :param file_name: Name of the file (used for determining content type).
        :param return_type: Specify 'url' to return the blob URL; otherwise, blob name is returned.
        :return: URL or blob name based on return_type.
        """
        pass

    @abstractmethod
    def update_data_with_url(self, blob_url: str, data: bytes, file_name: str,max_concurrency :int=None,max_retries: int=None) -> str:
        """
        Updates a file using its URL.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to be updated.
        :param data: Binary data to upload to the blob.
        :param file_name: Name of the file (used for determining content type).
        :return: URL of the updated blob.
        """
        pass

    
    @abstractmethod
    @typing_extensions.deprecated(
        'The `download_file` method will be deprecated in upcoming versions; use `download_data` instead.'
    )
    def download_file(self, blob_name: str,max_concurrency :int=None,max_retries: int=None, destination_folder: Optional[str] = None) -> str:
        """
        Downloads a file and saves it to a local folder.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the blob to download.
        :param destination_folder: Destination folder where the file should be saved. Defaults to TMP_LOCAL_PATH.
        :return: Local file path where the file is saved.
        """
        pass


    @abstractmethod
    @typing_extensions.deprecated(
        'The `download_file_with_url` method will be deprecated in upcoming versions; use `download_data_with_url` instead.'
    )
    def download_file_with_url(self, blob_url: str,max_concurrency :int=None,max_retries: int=None, destination_folder: Optional[str] = None) -> str:
        """
        Downloads a file using its URL.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to download.
        :param destination_folder: Destination folder where the file should be saved.
        :return: File path where the blob was saved.
        """

        pass

    @abstractmethod
    def download_data(self, blob_name: str,max_concurrency :int=None,max_retries: int=None) -> bytes:
        """
        Downloads a file and returns its content as a string.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the blob to download.
        :return: File contents/data as bytes.If encoded with utf-8 then must decode them
        """
        pass

    @abstractmethod
    def download_data_with_url(self, blob_url: str,max_concurrency :int=None,max_retries: int=None) -> bytes:
        """
        Downloads a file using URL and returns its content as a string.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to download.
        :return: File contents/data as bytes.If encoded with utf-8 then must decode them
        """
        pass

    @abstractmethod
    @typing_extensions.deprecated(
        'The `create_presigned_url` method will be deprecated in upcoming versions; use `download_data or other methods` instead.'
    )
    def create_presigned_url(self, blob_name: str,max_retries: int=None, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for a blob.
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the blob for which to create the presigned URL.
        :param expiration: Expiration time in seconds for the URL defaults to 3600.
        :return: Presigned URL.
        """
        pass

    @abstractmethod
    def download_blob_to_stream(self,blob_name,buffer: IO[bytes],max_concurrency :int=None,max_retries: int=None,buffer_size=1024,offset=0)->Optional[IO[bytes]]:
        """
        Streams the data from the blob
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param buffer: buffer to load the bytes from blob
        :param blob_name: Name of the blob to be downloaded.
        :param buffer_size: The amount of data to be read in each chunk (default is 1024 bytes).
        :param offset: The starting point (in bytes) for downloading the blob. Defaults to 0 (start from the beginning).For every calling to this method need to update offset
        :return: A chunk of the blob data, up to `buffer_size` bytes in the provided.If encoded with utf-8 then decode them
                Returns None after successful download of all bytes or offset is greater than or equal to blob size
        """
        pass
    @abstractmethod
    def download_blob_to_stream_with_url(self,blob_url,buffer: IO[bytes],max_concurrency :int=None,max_retries: int=None,buffer_size=1024,offset=0)->Optional[IO[bytes]]:
        """
        Streams the data from the blob with given url
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param buffer: buffer to load the bytes from blob
        :param blob_url: Url of the blob to be downloaded.
        :param buffer_size: The amount of data to be read in each chunk (default is 1024 bytes).
        :param offset: The starting point (in bytes) for downloading the blob. Defaults to 0 (start from the beginning).For every calling to this method need to update offset
        :return: A chunk of the blob data, up to `buffer_size` bytes in the provided.If encoded with utf-8 then decode them.
                Returns None after successful download of all bytes or offset is greater than or equal to blob size
        """
        pass
    @abstractmethod
    def initialize_blob_with_initial_data(self, data: bytes, file_name: str,customer_uuid: str,
                application_uuid: str, channel_type: str,max_retries: int=None,
                    content_type: Optional[str] = None, return_type: str = ReturnTypes.BLOB) -> tuple:
        """
        Appends data to an existing Block Blob.
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param file_name: Name of the file (used for blob naming) or a path for further organization within the blob structure.
        :param customer_uuid: UUID of the customer(mandatory).
        :param application_uuid: UUID of the application(mandatory).
        :param channel_type: Channel type (used for blob organization)mandatory.
        :param content_type: Optional content type.
        :param return_type: Specify 'url' to return the blob URL; otherwise, blob name is returned.
        :param data: Data to be appended (in bytes).Recommended to provide data with utf-8 encoded bytes if storing strings,etc. if storing strings,etc
        :return: URL or blob name based on return_type.(blob_url,content_type) or (blob_name,content_type)
        """
        pass
    @abstractmethod
    def append_to_block_blob(self, blob_name: str, data: bytes,content_type,max_retries: int=None):
        """
        Appends data to an existing Block Blob.
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param content_type:content type that blob holds initially
        :param blob_name: Name of the blob to append data to.
        :param data: Data to be appended (in bytes).Recommended to provide data with utf-8 encoded bytes if storing strings,etc. if storing strings,etc.
        """
        pass
    @abstractmethod
    def append_to_block_with_url(self, blob_url: str, data: bytes,content_type,max_retries: int=None):
        """
        Appends data to an existing Block Blob with given url.
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param content_type::content type that blob holds initially
        :param blob_url: Url of the blob to append data to.
        :param data: Data to be appended (in bytes).Recommended to provide data with utf-8 encoded bytes if storing strings,etc. if storing strings,etc.
        """
        pass

    @abstractmethod
    def delete_blob_with_blob_name(self,blob_name,max_retries: int=None):
        """
        delete blob with blob name
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: blob name to be deleted
        """
        pass
    @abstractmethod
    def delete_blob_with_blob_url(self,blob_url,max_retries: int=None):
        """
        delete blob with blob Url
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: blob Url to be deleted
        """
        pass

    @abstractmethod
    def upload_file_to_existing_structure(self,existing_structure: str, blob_name: str,file_path: str,over_write: bool,max_concurrency :int=None,max_retries: int=None,file_name: Optional[str] = None,content_type: Optional[str] = None, return_type: str = ReturnTypes.BLOB)->str:
        """
        Uploads a file to an existing blob structure in Azure Blob Storage.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param existing_structure: The existing blob structure or prefix in the blob storage where the file will be uploaded.
        :param blob_name: The name of the blob to be appended to the existing structure.(mandatory)
        :param file_path: The local file path of the file to be uploaded.
        :param over_write: Flag to determine whether the existing blob should be overwritten.
        :param file_name: (Optional) Name of the file being uploaded; defaults to the file name extracted from `file_path`.(this file_name won't be used in blob creation)
        :param content_type: (Optional) Content type of the file; inferred if not provided.
        :param return_type: Determines whether the method returns the URL of the blob or the blob name.
                            Options: `ReturnTypes.URL` or `ReturnTypes.BLOB`.
        :return: The URL of the uploaded blob or its blob name, based on the `return_type`.
        """
        pass

    @abstractmethod
    def upload_data_to_existing_structure(self,data: bytes,existing_structure: str, blob_name: str,over_write: bool,file_name: str,max_concurrency :int=None,max_retries: int=None,content_type: Optional[str] = None, return_type: str = ReturnTypes.BLOB)->str:
        """
        Upload binary data to a blob in an existing structure in Azure Blob Storage.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param data: Binary data to be uploaded.
        :param existing_structure:  The existing blob structure or prefix in the blob storage.
        :param blob_name: The name of the blob to be appended to the existing structure.(mandatory)
        :param over_write: Whether to overwrite the blob if it already exists.
        :param file_name: The name of the file for determining content type.(this file_name won't be used in blob creation)
        :param content_type: (Optional)The content type of the file .
                             If not provided, it will be derived from the file name.
        :param return_type: Determines whether to return the blob's URL or its complete name in the storage.
        :return: URL or complete name of the uploaded blob based on the return_type parameter.
        """
        pass

    @abstractmethod
    def download_blob_chunk_to_stream(self, blob_name, blob_client, blob_size, buffer: IO[bytes], max_concurrency: int = None, max_retries: int = None, buffer_size = 1024, offset = 0) -> Optional[IO[bytes]]:
        """
        Streams the data from the blob.
        
        :param blob_name: Name of the blob to be downloaded.
        :param blob_client: Azure BlobClient for the specific blob.
        :param blob_size: Size of the blob.
        :param max_concurrency: Number of parallel connections (must be greater than 1).
        :param max_retries: Maximum number of retry attempts in case of failed operations.
        :param buffer: Buffer to load the bytes from blob.
        :param buffer_size: The amount of data to be read in each chunk (default is 1024 bytes).
        :param offset: The starting point (in bytes) for downloading the blob. Defaults to 0 (start from the beginning).
        :return: A chunk of the blob data, up to `buffer_size` bytes in the provided buffer. 
                Returns None after successful download of all bytes or if offset is greater than or equal to blob size.
        """
        pass