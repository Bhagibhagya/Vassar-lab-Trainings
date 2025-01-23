import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from django.http import StreamingHttpResponse
from rest_framework import status
from Platform.services.impl.stream_file_service_impl import StreamFileServiceImpl
from ConnectedCustomerPlatform.exceptions import CustomException
from django.urls import reverse
from rest_framework.test import APIClient



class TestStreamFileService(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment.
        """
        self.client = APIClient()
        self.service = StreamFileServiceImpl()
        self.blob_name = "test_blob.mp4"
        self.blob_url = f"https://storageaccount.blob.core.windows.net/container/{self.blob_name}"
        self.buffer_size = 5 * 1024 * 1024  # 5 MB
        self.max_concurrency = 5
        self.offset = 0

        # Mock Azure Blob service and attach it to the service
        self.mock_azure_blob_service = MagicMock()
        self.service.azure_blob_service = self.mock_azure_blob_service

    @patch("Platform.services.impl.stream_file_service_impl.CloudStorageFactory.instantiate")
    def test_stream_blob_file_success(self, mock_storage_factory):
        """
        Test the stream_blob_file method for a successful response.
        """
        # Mock CloudStorageFactory and blob client
        mock_blob_client = MagicMock()
        mock_blob_client.get_blob_properties.return_value.content_settings.content_type = "video/mp4"
        mock_blob_client.get_blob_properties.return_value.size = 10 * 1024 * 1024  # 10 MB
        mock_storage_manager = MagicMock()
        mock_storage_manager._container_client.get_blob_client.return_value = mock_blob_client
        mock_storage_factory.return_value = mock_storage_manager

        # Mock _download_chunks to return a generator
        self.service._download_chunks = MagicMock(return_value=(chunk for chunk in [b"chunk1", b"chunk2"]))

        response = self.service.stream_blob_file(self.blob_url)

        # Assert the response
        self.assertIsInstance(response, StreamingHttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="{self.blob_name}"')
    
    @patch.object(StreamFileServiceImpl, "stream_blob_file")
    def test_stream_file_data(self, mock_stream_blob_file):
        """
        Test the stream_file_data endpoint in the ViewSet.
        """
        mock_stream_blob_file.return_value = StreamingHttpResponse()

        payload = {"blob_url": self.blob_url}

        response = self.client.post(
            reverse("Platform:stream_file_data"),
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        mock_stream_blob_file.assert_called_once_with(self.blob_url)

    @patch("Platform.services.impl.stream_file_service_impl.CloudStorageFactory.instantiate")
    def test_stream_blob_file_error(self, mock_storage_factory):
        """
        Test the stream_blob_file method when an error occurs.
        """
        # Mock the factory to raise a FileNotFoundError
        mock_storage_factory.side_effect = FileNotFoundError("Container or blob not found")

        with self.assertRaises(CustomException) as context:
            self.service.stream_blob_file(self.blob_url)

        self.assertEqual(context.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(context.exception.detail, "Error occurred while streaming the file")

    def test_download_chunks_success(self):
        """
        Test the _download_chunks method for successful chunked download.
        """
        # Mock the behavior of download_blob_chunk_to_stream
        self.mock_azure_blob_service.download_blob_chunk_to_stream.side_effect = [
            BytesIO(b"chunk1"),  # First chunk
            BytesIO(b"chunk2"),  # Second chunk
            None                 # No more data
        ]

        # Create a consistent mock blob_client
        mock_blob_client = MagicMock()

        buffer = BytesIO()
        chunks = list(self.service._download_chunks(
            blob_name=self.blob_name,
            blob_client=mock_blob_client,
            blob_size=10 * 1024 * 1024,  # 10 MB
            buffer=buffer,
            max_concurrency=self.max_concurrency,
            buffer_size=self.buffer_size,
            offset=self.offset
        ))

        # Verify the chunks
        self.assertEqual(chunks, [b"chunk1", b"chunk2"])

        # Ensure the mocked method was called with the correct arguments
        self.mock_azure_blob_service.download_blob_chunk_to_stream.assert_any_call(
            blob_name=self.blob_name,
            blob_client=mock_blob_client,
            blob_size=10 * 1024 * 1024,
            buffer=buffer,
            max_concurrency=self.max_concurrency,
            offset=self.offset,
            buffer_size=self.buffer_size
        )

    def test_download_chunks_empty_blob(self):
        """
        Test the _download_chunks method for an empty blob.
        """
        # Mock the behavior of download_blob_chunk_to_stream to return no data
        self.mock_azure_blob_service.download_blob_chunk_to_stream.return_value = None

        # Create a consistent mock blob_client
        mock_blob_client = MagicMock()

        buffer = BytesIO()
        chunks = list(self.service._download_chunks(
            blob_name=self.blob_name,
            blob_client=mock_blob_client,
            blob_size=0,  # Empty blob
            buffer=buffer,
            max_concurrency=self.max_concurrency,
            buffer_size=self.buffer_size,
            offset=self.offset
        ))

        # Verify no chunks are returned
        self.assertEqual(chunks, [])

        # Ensure the mocked method was called once
        self.mock_azure_blob_service.download_blob_chunk_to_stream.assert_called_once_with(
            blob_name=self.blob_name,
            blob_client=mock_blob_client,
            blob_size=0,
            buffer=buffer,
            max_concurrency=self.max_concurrency,
            offset=self.offset,
            buffer_size=self.buffer_size
        )

    def test_download_chunks_partial_blob(self):
        """
        Test the _download_chunks method for a partial blob download.
        """
        # Mock the behavior of download_blob_chunk_to_stream for partial data
        self.mock_azure_blob_service.download_blob_chunk_to_stream.side_effect = [
            BytesIO(b"partial_chunk"),  # Partial chunk
            None                        # No more data
        ]

        # Create a consistent mock blob_client
        mock_blob_client = MagicMock()

        buffer = BytesIO()
        chunks = list(self.service._download_chunks(
            blob_name=self.blob_name,
            blob_client=mock_blob_client,
            blob_size=10 * 1024 * 1024,  # 10 MB
            buffer=buffer,
            max_concurrency=self.max_concurrency,
            buffer_size=self.buffer_size,
            offset=self.offset
        ))

        # Verify the chunks
        self.assertEqual(chunks, [b"partial_chunk"])

        # Ensure the mocked method was called with the correct arguments
        self.mock_azure_blob_service.download_blob_chunk_to_stream.assert_any_call(
            blob_name=self.blob_name,
            blob_client=mock_blob_client,
            blob_size=10 * 1024 * 1024,
            buffer=buffer,
            max_concurrency=self.max_concurrency,
            offset=self.offset,
            buffer_size=self.buffer_size
        )

