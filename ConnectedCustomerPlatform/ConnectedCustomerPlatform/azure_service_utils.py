import re
import logging
from azure.storage.blob import BlobServiceClient

from django.conf import settings
from urllib.parse import unquote

# Set the logging level for the Azure SDK to WARNING to prevent INFO level logs from being printed
azure_logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy')
azure_logger.setLevel(logging.WARNING)
# Configure the logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory

class AzureBlobManager:
    def __init__(self, connection_string):
        logger.info("Azure connection established")
        logger.debug(f"Connection string azure :: {connection_string}")
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.account_key = self.blob_service_client.credential.account_key
        self.azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

        logger.debug(f"account key :: {self.account_key}")

    def parse_blob_url(self, url):
        """
        Parses the URL to extract the container and blob names.

        :param url: URL of the blob.
        :return: Tuple containing container name and blob name.
        """
        match = re.match(r"https://[^/]+/([^/]+)/(.+)", url)
        if match:
            container_name = match.group(1)
            blob_name = match.group(2)
            blob_name = unquote(blob_name)
            logger.debug(f"container_name:: {container_name}")
            logger.debug(f"blob_name:: {blob_name}")
            return container_name, blob_name
        else:
            raise ValueError("Invalid Blob URL")

    def create_presigned_url_for_media_url(self, container_name, media_url, expiration=3600):
        """
        Generate a presigned URL to share an Azure Blob Storage object.

        :param container_name: Name of the Azure Blob Storage container.
        :param media_url: list of objects with url and name  [ {"name":"", "url": "" }, {}]
        :param expiration: Time in seconds for the presigned URL to remain valid.
        :return: list of objects with name and public url
        """
        logger.info("azuer_service.py :: AzureBlobManager :: create_presigned_url_for_media_url")
        logger.info(f"container_name :: {container_name} :: media_url :: {media_url}")
        new_media_url_object = []
        if isinstance(media_url, list):
            for media_url_object in media_url:
                if isinstance(media_url_object, dict):
                    private_url = media_url_object.get("url", None)
                    name = media_url_object.get("name", None)
                    if isinstance(private_url, str):
                        # unquote the private_url before creating presigned url
                        blob_name = unquote(private_url)
                        public_url = self.azure_blob_manager.create_presigned_url(blob_name=blob_name)
                        new_media_url_object.append({"name": name, "url": public_url})
        return new_media_url_object

    def delete_blob(self, folder_name):
        """
        Deletes all blobs in the specified folder within the Azure container.
        """
        # Retrieve blob client for the specified Azure container
        blob_client = self.blob_service_client.get_container_client(settings.AZURE_CONTAINER)

        # Iterate through blobs with names starting with the specified folder name and delete blob
        for blob in blob_client.list_blobs(name_starts_with=folder_name):
                blob_client.delete_blob(blob.name)
        logger.info("Successfully deleted blobs in folder: %s", folder_name)

