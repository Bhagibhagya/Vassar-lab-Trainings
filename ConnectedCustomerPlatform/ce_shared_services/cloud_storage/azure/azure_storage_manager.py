import base64
import logging
import os
from asyncio import IncompleteReadError
from io import BytesIO
from typing import Optional, IO
import typing_extensions

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings, ExponentialRetry
from azure.core.exceptions import ResourceNotFoundError, \
    ClientAuthenticationError, ServiceRequestError, ServiceResponseError, \
    StreamConsumedError

from datetime import datetime, timedelta, timezone
import uuid

from ce_shared_services.cloud_storage.interface.cloud_storage_manager import ICloudStorageManager

from .constants import ErrorMessages, ReturnTypes, DateTypes, BLOB_PATTERN  # Assuming this contains your error messages
from .utils import validate_file_path, generate_blob_name, get_content_type, validate_read_permission, \
    handle_azure_exceptions, parse_blob_url, validate_folder_path
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig

TMP_LOCAL_PATH = os.getenv('TMP_LOCAL_PATH')

# Set logging level for Azure SDK and configure the logger
azure_logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy')
azure_logger.setLevel(logging.WARNING)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AzureStorageManager(ICloudStorageManager):
    """Manager class for handling Azure Blob storage operations."""
    def __init__(self,azure_config: AzureBlobConfig):
        if not isinstance(azure_config,AzureBlobConfig):
            logger.error(ErrorMessages.INVALID_AZURE_CONFIGURATION)
            raise ValueError(ErrorMessages.INVALID_AZURE_CONFIGURATION)
        self.azure_config = azure_config
        self._container_name = azure_config.container_name
        self._azure_connection_string = azure_config.azure_connection_string
        self._container_client = self._get_container_client()

    @handle_azure_exceptions(exceptions=(),give_up=())
    def _get_container_client(self):
        """Get container client, raise error if the container doesn't exist."""
        logger.info("In AzureStorageManager :: _get_container_client")
        # Specify retry policy parameters
        #initialbackoff=initial delay after first call
        #increment_base = exponential growth factor
        #next_backoff = initial_backoff * (increment_base ^ retry_attempt)
        logger.info("Attempting to get ContainerClient...")
        retry = ExponentialRetry(initial_backoff=self.azure_config.initial_backoff, increment_base=self.azure_config.increment_base, retry_total=self.azure_config.max_retries)
        container_client = BlobServiceClient.from_connection_string(self.azure_config.azure_connection_string,retry_policy=retry,max_single_get_size=self.azure_config.max_single_get_size,  # 32MB
            max_chunk_get_size=self.azure_config.max_chunk_get_size,    # 4MB
            max_single_put_size=self.azure_config.max_single_put_size,  # 64MB
            max_block_size=self.azure_config.max_block_size,max_concurrency=self.azure_config.max_concurrency).get_container_client(self.azure_config.container_name)
        #this makes api call as above methods just gives instances
        if not container_client.exists():
            logger.error(ErrorMessages.CONTAINER_NOT_FOUND.format(container=self.azure_config.container_name))
            raise ResourceNotFoundError(ErrorMessages.CONTAINER_NOT_FOUND.format(container=self.azure_config.container_name))
        #usually azure closes connection after each call
        if container_client is not None:
            container_client.close()
        return container_client

    @handle_azure_exceptions(exceptions=(),give_up=(FileExistsError,FileNotFoundError,PermissionError))
    def upload_file(self, file_path: str, over_write: bool, customer_uuid: str,
                    application_uuid: str, channel_type: str, max_concurrency: int=None, max_retries: int = None,
                    file_name: Optional[str] = None,
                    content_type: Optional[str] = None, return_type: str = ReturnTypes.BLOB) -> str:
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
        logger.info("In AzureStorageManager :: upload_file")
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not channel_type:
            raise ValueError(ErrorMessages.INVALID_CHANNEL_TYPE)
        if not customer_uuid:
            raise ValueError(ErrorMessages.INVALID_CUSTOMER_UUID)
        if not application_uuid:
            raise ValueError(ErrorMessages.INVALID_APPLICATION_UUID)
        validate_file_path(file_path)

        validate_read_permission(file_path)

        if not file_name:
            file_name = os.path.basename(file_path)
        # Generate blob name and content type
        blob_name = generate_blob_name(file_name, customer_uuid, application_uuid, channel_type)
        content_type = get_content_type(file_name, content_type)
        blob_client = self._container_client.get_blob_client(blob_name)
        # Upload file from file path
        try:
            with open(file_path, "rb") as file_data:
                blob_client.upload_blob(file_data, overwrite=over_write, content_settings=ContentSettings(content_type=content_type),max_concurrency=max_concurrency or self.azure_config.max_concurrency)

            logger.debug(f"File '{file_name}' uploaded successfully as '{blob_name}'.")
            file_data.close()
            return blob_client.url if return_type == ReturnTypes.URL else blob_name

        finally:
            if blob_client is not None:
                blob_client.close()

    @handle_azure_exceptions(exceptions=(),give_up=(FileExistsError,FileNotFoundError,PermissionError))
    def upload_data(self, data: bytes, file_name: str, over_write: bool, customer_uuid: str,
                    application_uuid: str, channel_type: str, max_concurrency: int=None, max_retries: int = None,
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
        logger.info("In AzureStorageManager :: upload_data")
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not data or not isinstance(data,bytes):
            logger.error(ErrorMessages.DATA_REQUIRED)
            raise ValueError(ErrorMessages.DATA_REQUIRED)
        if not file_name:
            raise ValueError(ErrorMessages.INVALID_FILE_NAME)
        if not channel_type:
            raise ValueError(ErrorMessages.INVALID_CHANNEL_TYPE)
        if not customer_uuid:
            raise ValueError(ErrorMessages.INVALID_CUSTOMER_UUID)
        if not application_uuid:
            raise ValueError(ErrorMessages.INVALID_APPLICATION_UUID)
        # Generate blob name and content type
        blob_name = generate_blob_name(file_name, customer_uuid, application_uuid, channel_type)
        content_type = get_content_type(file_name, content_type)
        blob_client = self._container_client.get_blob_client(blob_name)
        try:
            # Upload binary data
            blob_client.upload_blob(data, overwrite=over_write, content_settings=ContentSettings(content_type=content_type),max_concurrency=max_concurrency or self.azure_config.max_concurrency)
            logger.debug(f"Data uploaded successfully as '{blob_name}'.")
            return blob_client.url if return_type == ReturnTypes.URL else blob_name

        finally:
            if blob_client is not None:
                blob_client.close()


    @handle_azure_exceptions(exceptions=(),give_up=(FileNotFoundError,PermissionError,ValueError))
    def update_file(self, blob_name: str, file_path: str, max_concurrency: int=None, max_retries: int = None,
                    return_type: str = ReturnTypes.BLOB) -> str:
        """
        Updates an existing blob with a new file.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the existing blob to be updated.
        :param file_path: Local file path of the new file to upload.
        :param return_type: Specify 'url' to return the blob URL; otherwise, blob name is returned.
        :return: URL or blob name based on return_type.
        """
        logger.info("In AzureStorageManager :: update_file")
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not blob_name:
            raise ValueError(ErrorMessages.INVALID_BLOB_NAME)
        validate_file_path(file_path)
        validate_read_permission(file_path)

        content_type = get_content_type(file_path)

        blob_client = self._container_client.get_blob_client(blob_name)
        try:
            if blob_client.exists():
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type),max_concurrency=max_concurrency or self.azure_config.max_concurrency)
                data.close()
                return blob_client.url if return_type == ReturnTypes.URL else blob_name
            else:
                raise ValueError(ErrorMessages.BLOB_NOT_FOUND)
        finally:
            if blob_client is not None:
                blob_client.close()

    def update_file_with_url(self, blob_url: str, file_path: str, max_concurrency: int=None,
                             max_retries: int = None) -> str:
        """
        Updates a file using its URL.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to be updated.
        :param file_path: Local file path of the new file to upload.
        :return: URL of the updated blob.
        """
        logger.info("In AzureStorageManager :: update_file_with_url")
        blob_name = parse_blob_url(blob_url)
        return self.update_file(blob_name=blob_name, file_path=file_path,max_concurrency=max_concurrency,max_retries=max_retries,return_type=ReturnTypes.URL)

    @handle_azure_exceptions(exceptions=(),give_up=(ClientAuthenticationError,ValueError))
    def update_data(self, blob_name: str, data: bytes, file_name: str, max_concurrency: int=None, max_retries: int = None,
                    return_type: str = ReturnTypes.BLOB) -> str:
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
        logger.info("In AzureStorageManager :: update_data")
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not data:
            logger.error(ErrorMessages.DATA_REQUIRED)
            raise ValueError(ErrorMessages.DATA_REQUIRED)

        content_type = get_content_type(file_name)
        blob_client = self._container_client.get_blob_client(blob_name)

        try:

            if blob_client.exists():
                blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type),max_concurrency=max_concurrency or self.azure_config.max_concurrency)
                return blob_client.url if return_type == ReturnTypes.URL else blob_name
            else:
                raise ValueError(ErrorMessages.BLOB_NOT_FOUND)
        finally:
            if blob_client is not None:
                blob_client.close()

    def update_data_with_url(self, blob_url: str, data: bytes, file_name: str, max_concurrency: int=None,
                             max_retries: int = None) -> str:
        """
        Updates a file using its URL.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to be updated.
        :param data: Binary data to upload to the blob.
        :param file_name: Name of the file (used for determining content type).
        :return: URL of the updated blob.
        """
        logger.info("In AzureStorageManager :: update_data_with_url")
        blob_name = parse_blob_url(blob_url)
        return self.update_data(blob_name=blob_name, data=data, file_name=file_name,max_concurrency=max_concurrency,max_retries=max_retries, return_type=ReturnTypes.URL)


    #TODO Just get the bytes without storing in the local.
    @handle_azure_exceptions(exceptions=(IncompleteReadError,),give_up=(FileNotFoundError,StreamConsumedError,ValueError,ClientAuthenticationError))
    def download_data(self, blob_name: str, max_concurrency: int=None, max_retries: int = None) -> bytes:
        """
        Downloads a file and returns its content as a string.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the blob to download.
        :return: File contents/data as bytes.If encoded with utf-8 then must decode them
        """
        logger.info("In AzureStorageManager :: download_data")
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not blob_name:
            raise ValueError(ErrorMessages.INVALID_BLOB_NAME)
        blob_client = self._container_client.get_blob_client(blob_name)

        try:
            # Get the blob properties to check its size
            blob_size = blob_client.get_blob_properties().size
            # Check if the blob size exceeds the memory limit
            if blob_size > self.azure_config.memory_limit:
                logger.error(f'Blob size:{blob_size} is greater than configured memory_limit :{self.azure_config.memory_limit},use download_blob_to_stream instead')
                raise MemoryError(
                    f"The blob size {blob_size} bytes exceeds the memory limit of {self.azure_config.memory_limit} bytes.")

            return blob_client.download_blob(max_concurrency=max_concurrency or self.azure_config.max_concurrency).readall()
        finally:
            if blob_client is not None:
                blob_client.close()

    def download_data_with_url(self, blob_url: str, max_concurrency: int=None, max_retries: int = None) -> bytes:
        """
        Downloads a file using URL and returns its content as a string.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to download.
        :return: File contents/data as bytes.If encoded with utf-8 then must decode them
        """
        logger.info("In AzureStorageManager :: download_data_with_url")

        blob_name = parse_blob_url(blob_url)
        return self.download_data(blob_name=blob_name,max_concurrency=max_concurrency, max_retries=max_retries)

    @handle_azure_exceptions(exceptions=(IncompleteReadError,),give_up=(FileNotFoundError,StreamConsumedError,ValueError,PermissionError,ClientAuthenticationError))
    @typing_extensions.deprecated(
        'The `download_file` method will be deprecated in upcoming versions; use `download_data` instead.'
    )
    def download_file(self, blob_name: str, max_concurrency: int=None, max_retries: int = None,
                      destination_folder: Optional[str] = None) -> str:
        """
        Downloads a file and saves it to a local folder.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the blob to download.
        :param destination_folder: Destination folder where the file should be saved. Defaults to TMP_LOCAL_PATH.
        :return: Local file path where the file is saved.
        """
        logger.info("In AzureStorageManager :: download_file")
        logger.warning('The `download_file` method will be deprecated in upcoming versions; use `download_data` instead.')
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not destination_folder:
            destination_folder=TMP_LOCAL_PATH
        validate_folder_path(destination_folder)
        if not blob_name:
            raise ValueError(ErrorMessages.INVALID_BLOB_NAME)
        blob_client = self._container_client.get_blob_client(blob_name)

        try:

            file_name = os.path.basename(blob_name)
            folder_name = str(uuid.uuid4())
            file_path = os.path.join(destination_folder, folder_name, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob(max_concurrency=max_concurrency or self.azure_config.max_concurrency).readall())
            download_file.close()
            return file_path
        finally:
            blob_client.close()

    @typing_extensions.deprecated(
        'The `download_file_with_url` method will be deprecated in upcoming versions; use `download_data_with_url` instead.'
    )
    def download_file_with_url(self, blob_url: str, max_concurrency: int=None, max_retries: int = None,
                               destination_folder: Optional[str] = None) -> str:
        """
        Downloads a file using its URL.
        :param max_concurrency: Number of parallel connections(must be greater than 1)
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: URL of the blob to download.
        :param destination_folder: Destination folder where the file should be saved.
        :return: File path where the blob was saved.
        """
        logger.info("In AzureStorageManager :: download_file_with_url")
        blob_name = parse_blob_url(blob_url)
        return self.download_file(blob_name=blob_name, max_concurrency=max_concurrency,max_retries=max_retries,destination_folder=destination_folder)

    def _format_presigned_url(self, blob_name: str, sas_token: str) -> str:
        """Format the presigned URL for a blob."""
        logger.info("In AzureStorageManager :: _format_presigned_url")

        url = f"https://{self._container_client.account_name}.blob.core.windows.net/{self.azure_config.container_name}/{blob_name}?{sas_token}"
        logger.debug(f"Presigned URL generated for blob '{blob_name}'.")
        return url

    #TODO this method should be changed to stream the data instead of sending the URL
    #todo check with baskar
    @handle_azure_exceptions(exceptions=(),give_up=(ValueError,TypeError,AttributeError,ClientAuthenticationError,FileNotFoundError))
    @typing_extensions.deprecated(
        'The `create_presigned_url` method will be deprecated in upcoming versions; use `download_data or other methods` instead.'
    )
    def create_presigned_url(self, blob_name: str, max_retries: int=None, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for a blob.
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: Name of the blob for which to create the presigned URL.
        :param expiration: Expiration time in seconds for the URL defaults to 3600.
        :return: Presigned URL.
        """
        logger.info("In AzureStorageManager :: create_presigned_url")
        logger.warning('The `create_presigned_url` method will be deprecated in upcoming versions; use `download_data` instead.')
        if not blob_name:
            raise ValueError(ErrorMessages.INVALID_BLOB_NAME)
        sas_token = generate_blob_sas(
            account_name=self._container_client.account_name,
            container_name=self.azure_config.container_name,
            blob_name=blob_name,
            account_key=self._container_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(seconds=expiration)
        )

        if sas_token:
            return self._format_presigned_url(blob_name, sas_token)
        else:
            raise ValueError(ErrorMessages.SAS_TOKEN_GENERATION_FAILED)


    @handle_azure_exceptions(exceptions=(IncompleteReadError,),give_up=(FileNotFoundError,StreamConsumedError,ValueError, PermissionError,ClientAuthenticationError))
    def download_blob_to_stream(self, blob_name, buffer: IO[bytes], max_concurrency: int=None, max_retries: int = None,
                                buffer_size=1024, offset=0) -> Optional[IO[bytes]]:
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
        logger.info("In AzureStorageManager :: download_blob_to_stream")
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not blob_name:
            raise ValueError(ErrorMessages.INVALID_BLOB_NAME)
        if not buffer or not isinstance(buffer,BytesIO):
            raise ValueError(ErrorMessages.INVALID_BUFFER)

        blob_client = self._container_client.get_blob_client(blob_name)

        try:
            # Get the properties of the blob to check its size
            blob_size = blob_client.get_blob_properties().size
            # If the offset is greater than or equal to the blob size, return None
            if offset >= blob_size:
                return None
            # Clear the buffer before writing new data
            buffer.seek(0)
            buffer.truncate(0)

            # Download the blob and get the downloader
            blob_client.download_blob(offset=offset,length=buffer_size,max_concurrency=max_concurrency or self.azure_config.max_concurrency).readinto(buffer)
            buffer.seek(0)
            return buffer

        finally:
            if blob_client is not None:
                blob_client.close()

    def download_blob_to_stream_with_url(self, blob_url, buffer: IO[bytes], max_concurrency: int=None,
                                         max_retries: int = None, buffer_size=1024, offset=0) -> Optional[IO[bytes]]:
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
        logger.info("In AzureStorageManager :: download_blob_to_stream_with_url")
        blob_name = parse_blob_url(blob_url)
        return self.download_blob_to_stream(blob_name=blob_name,buffer=buffer,max_concurrency=max_concurrency,max_retries=max_retries,buffer_size=buffer_size,offset=offset)

    @handle_azure_exceptions(exceptions=(),give_up=(ClientAuthenticationError,ValueError))
    def initialize_blob_with_initial_data(self, data: bytes, file_name: str, customer_uuid: str,
                                          application_uuid: str, channel_type: str, max_retries: int=None,
                                          content_type: Optional[str] = None,
                                          return_type: str = ReturnTypes.BLOB) -> tuple:
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
        logger.info("In AzureStorageManager :: initialize_blob_with_initial_data")
        if not channel_type:
            raise ValueError(ErrorMessages.INVALID_CHANNEL_TYPE)
        if not customer_uuid:
            raise ValueError(ErrorMessages.INVALID_CUSTOMER_UUID)
        if not application_uuid:
            raise ValueError(ErrorMessages.INVALID_APPLICATION_UUID)
        content_type = get_content_type(file_name, content_type)
        # Generate blob name and content type
        blob_name = generate_blob_name(file_name, customer_uuid, application_uuid, channel_type)
        blob_client = self._container_client.get_blob_client(blob_name)

        # Generate a unique block ID
        block_id = base64.b64encode(format(0, '032d').encode()).decode()

        try:
            # Upload the new block
            blob_client.stage_block(block_id, data)

            # Get existing block list
            existing_blocks = blob_client.get_block_list()[0]
            block_list = [b.id for b in existing_blocks]

            # Append the new block ID to the list of existing blocks
            block_list.append(block_id)

            # Commit the block list to the blob
            blob_client.commit_block_list(block_list,content_settings=ContentSettings(content_type=content_type))

            logger.debug(f"Data successfully appended to blob: {blob_name}")
            return (blob_client.url,content_type) if return_type == ReturnTypes.URL else (blob_name,content_type)
        finally:
            if blob_client is not None:
                blob_client.close()

    @handle_azure_exceptions(exceptions=(),give_up=(ClientAuthenticationError,ValueError))
    def append_to_block_blob(self, blob_name: str, data: bytes, content_type, max_retries: int=None):
        """
        Appends data to an existing Block Blob.
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param content_type:content type that blob holds initially
        :param blob_name: Name of the blob to append data to.
        :param data: Data to be appended (in bytes).Recommended to provide data with utf-8 encoded bytes if storing strings,etc. if storing strings,etc.
        """
        logger.info("In AzureStorageManager :: append_to_block_blob")
        blob_client = self._container_client.get_blob_client(blob_name)
        if not content_type:
            raise ValueError("Content Type is Required")
        try:
            if blob_client.get_blob_properties().content_settings.content_type!=content_type:
                raise ValueError("Invalid data and content type")

            # Get existing block list
            existing_blocks = blob_client.get_block_list()[0]
            #block_list = [b.id for b in existing_blocks]
            # Get both sum and block IDs in single iteration
            current_offset = 0
            block_ids = []
            for block in existing_blocks:
                current_offset += block.size
                block_ids.append(block.id)

            # Generate a unique block ID
            block_id = base64.b64encode(format(current_offset, '032d').encode()).decode()
            # Upload the new block
            blob_client.stage_block(block_id, data)

            # Append the new block ID to the list of existing blocks
            block_ids.append(block_id)

            # Commit the block list to the blob
            blob_client.commit_block_list(block_ids,content_settings=ContentSettings(content_type=content_type))

            logger.info(f"Data successfully appended to blob: {blob_name}")
        finally:
            blob_client.close()

    def append_to_block_with_url(self, blob_url: str, data: bytes, content_type, max_retries: int=None):
        """
        Appends data to an existing Block Blob with given url.
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param content_type::content type that blob holds initially
        :param blob_url: Url of the blob to append data to.
        :param data: Data to be appended (in bytes).Recommended to provide data with utf-8 encoded bytes if storing strings,etc. if storing strings,etc.
        """
        logger.info("In AzureStorageManager :: append_to_block")
        blob_name = parse_blob_url(blob_url)
        return self.append_to_block_blob(blob_name=blob_name,data=data,content_type=content_type,max_retries=max_retries)

    @handle_azure_exceptions(exceptions=(),give_up=(ClientAuthenticationError,ValueError,FileNotFoundError))
    def delete_blob_with_blob_name(self, blob_name, max_retries: int=None):
        """
        delete blob with blob name
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_name: blob name to be deleted
        """
        logger.info("In AzureStorageManager :: delete_blob_with_blob_name")
        blob_client = self._container_client.get_blob_client(blob_name)
        try:
            # Delete the blob
            blob_client.delete_blob()

            logger.debug(f"Blob '{blob_name}' successfully deleted.")
        finally:
            blob_client.close()

    def delete_blob_with_blob_url(self, blob_url, max_retries: int=None):
        """
        delete blob with blob Url
        :param max_retries: Maximum number of retry attempts in case of failed operations
        :param blob_url: blob Url to be deleted
        """
        logger.info("In AzureStorageManager :: delete_blob_with_blob_url")
        blob_name = parse_blob_url(blob_url)
        self.delete_blob_with_blob_name(blob_name=blob_name,max_retries=max_retries)

    @handle_azure_exceptions(exceptions=(),give_up=(FileExistsError,FileNotFoundError,PermissionError))
    def upload_file_to_existing_structure(self, existing_structure: str, blob_name: str, file_path: str,
                                          over_write: bool, max_concurrency: int=None, max_retries: int = None,
                                          file_name: Optional[str] = None, content_type: Optional[str] = None,
                                          return_type: str = ReturnTypes.BLOB) -> str:
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
        logger.info("In AzureStorageManager :: upload_blob_data_to_existing_structure")
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        validate_file_path(file_path)
        validate_read_permission(file_path)
        if not file_name:
            file_name = os.path.basename(file_path)
        content_type = get_content_type(file_name, content_type)
        complete_blob_name = self.__validate_and_append_blob_name(prepend_blob_name=existing_structure,
                                                                  blob_name=blob_name)
        blob_client = self._container_client.get_blob_client(complete_blob_name)
        # Upload file from file path
        try:
            with open(file_path, "rb") as file_data:
                blob_client.upload_blob(file_data, overwrite=over_write,
                                        content_settings=ContentSettings(content_type=content_type),
                                        max_concurrency=max_concurrency or self.azure_config.max_concurrency)

            logger.debug(f"File '{file_name}' uploaded successfully as '{complete_blob_name}'.")
            file_data.close()
            return blob_client.url if return_type == ReturnTypes.URL else complete_blob_name

        finally:
            if blob_client is not None:
                blob_client.close()

    @handle_azure_exceptions(exceptions=(),give_up=(FileExistsError,FileNotFoundError,PermissionError))
    def upload_data_to_existing_structure(self, data: bytes, existing_structure: str, blob_name: str, over_write: bool,
                                          file_name: str, max_concurrency: int=None, max_retries: int = None,
                                          content_type: Optional[str] = None,
                                          return_type: str = ReturnTypes.BLOB) -> str:
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
        logger.info("In AzureStorageManager :: upload_data_to_existing_structure")
        if not data or not isinstance(data, bytes):
            logger.error(ErrorMessages.DATA_REQUIRED)
            raise ValueError(ErrorMessages.DATA_REQUIRED)
        content_type = get_content_type(file_name, content_type)
        complete_blob_name = self.__validate_and_append_blob_name(prepend_blob_name=existing_structure,
                                                                  blob_name=blob_name)
        blob_client = self._container_client.get_blob_client(complete_blob_name)
        try:
            # Upload binary data
            blob_client.upload_blob(data, overwrite=over_write, content_settings=ContentSettings(content_type=content_type),max_concurrency=max_concurrency or self.azure_config.max_concurrency)
            logger.debug(f"Data uploaded successfully as '{complete_blob_name}'.")
            return blob_client.url if return_type == ReturnTypes.URL else complete_blob_name

        finally:
            if blob_client is not None:
                blob_client.close()

    @handle_azure_exceptions(exceptions=(),give_up=(ValueError,TypeError,AttributeError,ClientAuthenticationError,FileNotFoundError))
    def __validate_and_append_blob_name(self, prepend_blob_name: str, blob_name: str) -> str:
        """
        Constructs the full blob name by appending the given blob_name to the prepend_blob_name.
        Validates the structure, date components, and existence of the prepend_blob_name in the storage.

        :param prepend_blob_name: The initial path or folder structure in the blob container.
        :param blob_name: The specific name of the blob to be appended to the path.
        :return: The fully constructed blob name.
        """
        logger.info("In AzureStorageManager :: __validate_and_append_blob_name")

        if not prepend_blob_name:
            raise ValueError("Prepend_blob_name must be provided")
        if  not blob_name:
            raise ValueError("blob_name must be provided")

        # Clean the inputs
        prepend_blob_name = prepend_blob_name.strip('/')
        blob_name = blob_name.strip('/')

        # Structure validation
        parts = prepend_blob_name.split('/')
        expected_parts = BLOB_PATTERN.count('/')

        if len(parts) != expected_parts:
            error_msg = f"Invalid prepend_blob_name structure. Expected {expected_parts} parts, got {len(parts)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate individual parts
        customer_uuid, application_uuid, channel_type, year, month, day = parts

        if not customer_uuid.strip():
            raise ValueError("Customer UUID cannot be empty")
        if not application_uuid.strip():
            raise ValueError("Application UUID cannot be empty")
        if not channel_type.strip():
            raise ValueError("Channel type cannot be empty")

        # Validate date parts
        try:
            # Validate year/month/day format
            datetime.strptime(f"{year}-{month}-{day}",f"{DateTypes.YEAR}-{DateTypes.MONTH}-{DateTypes.DAY}")
        except ValueError as e:
            raise ValueError(f"Invalid date format in path: {str(e)}")
        # Check if the prepend path exists
        blobs_exist = any(True for _ in self._container_client.list_blobs(name_starts_with=prepend_blob_name))

        if not blobs_exist:
            logger.error(ErrorMessages.PREPEND_BLOB_DOES_NOT_EXIST.format(prepend_blob_name=prepend_blob_name))
            raise ValueError(ErrorMessages.PREPEND_BLOB_DOES_NOT_EXIST.format(prepend_blob_name=prepend_blob_name))

        # Construct the full blob name
        full_blob_name = f"{prepend_blob_name}/{blob_name}"
        logger.info(f"Constructed full blob name: {full_blob_name}")

        return full_blob_name

    @handle_azure_exceptions(exceptions=(IncompleteReadError,),give_up=(FileNotFoundError, StreamConsumedError, ValueError, PermissionError, ClientAuthenticationError))
    def download_blob_chunk_to_stream(self, blob_name, blob_client, blob_size, buffer: IO[bytes], max_concurrency: int = None, 
                            max_retries: int = None, buffer_size = 1024, offset = 0) -> Optional[IO[bytes]]:
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
        logger.info("In AzureStorageManager :: download_blob_chunk_to_stream")
        
        if max_concurrency and not isinstance(max_concurrency, int):
            raise ValueError(ErrorMessages.INVALID_MAX_CONCURRENCY_PARAM)
        if not blob_name:
            raise ValueError(ErrorMessages.INVALID_BLOB_NAME)
        if not buffer or not isinstance(buffer, BytesIO):
            raise ValueError(ErrorMessages.INVALID_BUFFER)

        try:
            # If the offset is greater than or equal to the blob size, return None
            if offset >= blob_size:
                return None
            
            # Clear the buffer before writing new data
            buffer.seek(0)
            buffer.truncate(0)

            # Download the blob and get the downloader
            blob_client.download_blob(offset=offset, length=buffer_size, max_concurrency=max_concurrency or self.azure_config.max_concurrency).readinto(buffer)
            buffer.seek(0)
            return buffer

        finally:
            # Ensure blob client closure if needed (assuming the client needs to be closed manually)
            if blob_client is not None:
                blob_client.close()
