import inspect
import logging
import os
from io import BytesIO


from django.conf import settings
from django.http import StreamingHttpResponse


from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig

from Platform.constant.constants import AZURE_STORAGE_MANAGER
from Platform.services.interface.stream_file_service_interface import IStreamFileService
from Platform.utils import parse_blob_url
from ConnectedCustomerPlatform.exceptions import CustomException
from rest_framework import status

logger = logging.getLogger(__name__)


class StreamFileServiceImpl(IStreamFileService):
    """
    ViewSet for handling streaming bytes data of files present in Azure Blob Storage.
    Implements the Singleton pattern to ensure a single instance.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of class StreamFileServiceImpl(IStreamFileService): exists.
        """
        if cls._instance is None:
            cls._instance = super(StreamFileServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the service only once for the singleton instance.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            self.initialized = True

    def stream_blob_file(self, blob_name_or_url):
        """
        Streams file data from Azure Storage using the download_blob_to_stream method.
        
        Args:
            blob_name_or_url (str): Unique identifier of the file or URL to the blob.
            
        Returns:
            StreamingHttpResponse: Chunks of the file being streamed.
        """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"Parsing blob name or URL: {blob_name_or_url}")

        blob_client = None

        try:
            # Check if input is a URL and extract container_name and blob_name
            if blob_name_or_url.startswith("http://") or blob_name_or_url.startswith("https://"):
                container_name, blob_name = parse_blob_url(blob_name_or_url)
            else:
                # Default case: Use predefined container and treat input as blob_name
                container_name = settings.AZURE_CONTAINER
                blob_name = blob_name_or_url

            # Get STORAGE_CONFIG from settings
            STORAGE_CONFIG = settings.STORAGE_CONFIG.copy()
            STORAGE_CONFIG['container_name'] = container_name

            # Initialize Azure Blob service manager
            self.azure_blob_service = CloudStorageFactory.instantiate(AZURE_STORAGE_MANAGER, AzureBlobConfig(**STORAGE_CONFIG))

            # Create an in-memory buffer to stream data into
            buffer = BytesIO()

            # Use the download_blob_to_stream method to download the data in chunks
            offset = 0
            chunk_size = 5*1024*1024  # 5 MB chunk size 
            max_concurrency = 5  # Set based on the expected load

            # Retrieve the Blob client for the specific blob (file) identified by `blob_name`
            blob_client = self.azure_blob_service._container_client.get_blob_client(blob_name)

            # Fetch the properties of the blob (file) including metadata such as size and content type
            blob_properties = blob_client.get_blob_properties()

            # Extract the content type (MIME type) from the blob's properties, which indicates the type of file (e.g., 'application/pdf', 'image/jpeg')
            content_type = blob_properties.content_settings.content_type

            # Extract the size of the blob (file) in bytes from its properties, which is useful for calculating the total file size for streaming
            blob_size = blob_properties.size


            # Create StreamingHttpResponse with chunks
            response = StreamingHttpResponse(
                self._download_chunks(blob_name, blob_client, blob_size, buffer, max_concurrency, chunk_size, offset),
                content_type=content_type
            )

            # Set the Content-Disposition header to prompt a file download
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(blob_name)}"'

            logger.debug(f"Successfully streamed chunk of data to client")

            # Return the streaming response (this should be inside the loop for large files)
            return response

        except (Exception, ValueError, FileNotFoundError) as e:
            logger.error(f"Error occurred while streaming the file: {e}")
            raise CustomException(detail="Error occurred while streaming the file", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Ensure blob client closure if needed (assuming the client needs to be closed manually)
            if blob_client is not None:
                blob_client.close()
        
    
    def _download_chunks(self, blob_name, blob_client, blob_size, buffer, max_concurrency, buffer_size, offset):
        """
        Helper method to download blob in chunks and return as an iterable for StreamingHttpResponse.
        """
        while True:
            # Download the next chunk and store it in the buffer
            buffer = self.azure_blob_service.download_blob_chunk_to_stream(
                blob_name=blob_name,
                blob_client=blob_client,
                blob_size=blob_size, 
                buffer=buffer,
                max_concurrency = max_concurrency,
                offset=offset,
                buffer_size=buffer_size
            )
            
            if not buffer:  # If no more data to download, stop
                break

            # Update the offset for the next chunk
            offset += buffer_size

            # Reset the buffer cursor to the start and yield each chunk for StreamingHttpResponse
            buffer.seek(0)
            yield buffer.read(buffer_size)  # Yielding each chunk of the blob data
