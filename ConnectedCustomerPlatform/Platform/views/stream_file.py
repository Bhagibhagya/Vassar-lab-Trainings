import inspect
import logging
from rest_framework.decorators import action

from rest_framework import status
from rest_framework.viewsets import ViewSet

from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.constants import BLOB_URL
from Platform.services.impl.stream_file_service_impl import StreamFileServiceImpl
from Platform.utils import validate_input
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)


class StreamFileViewSet(ViewSet):
    """
    ViewSet for handling streaming bytes data of files present in Azure Blob Storage.
    Implements the Singleton pattern to ensure a single instance.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of StreamFileViewSet exists.
        """
        if cls._instance is None:
            cls._instance = super(StreamFileViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the service only once for the singleton instance.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info("Initializing StreamFileViewSet Singleton Instance")
            self.stream_file_service = StreamFileServiceImpl()
            logger.info(f"StreamFileViewSet Singleton Instance ID: {id(self)}")
            self.initialized = True

    @swagger_auto_schema(
        operation_description="Streams the file data from Azure Blob Storage based on the provided blob name or blob URL.",
        responses={
            200: openapi.Response(
                description="File data is being streamed successfully",
                examples={
                    'application/octet-stream': 'This will represent a chunk of the binary data streamed from Azure Blob Storage.'
                }
            ),
            400: openapi.Response(
                description="Bad Request if blob name or URL is missing or invalid."
            ),
            404: openapi.Response(
                description="File Not Found if blob URL or blob name is not found in Azure Storage."
            ),
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'blob_url': openapi.Schema(type=openapi.TYPE_STRING, description="The URL or name of the blob file in Azure Storage")
            },
            required=['blob_url'],
        )
    )
    @action(detail=False, methods=['post'])
    def stream_file_data(self, request):
        """
            method to stream file data present in azure storage with blob_name or blob_url
            Args:
                request (str): http request
            Returns:
                chunks data of the file
        """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Decode the blob name or blob url
        blob_url = request.data.get(BLOB_URL)
        if not validate_input(data=blob_url):
            raise CustomException(detail="blob name cannot null or empty", status_code=status.HTTP_400_BAD_REQUEST)
        return self.stream_file_service.stream_blob_file(blob_url)