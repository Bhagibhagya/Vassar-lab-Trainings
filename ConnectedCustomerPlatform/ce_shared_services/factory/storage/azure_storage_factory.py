import logging

from ce_shared_services.cloud_storage.azure.azure_storage_manager import AzureStorageManager
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.cloud_storage.interface.cloud_storage_manager import ICloudStorageManager

from ce_shared_services.factory.scope.singleton import Singleton

logger = logging.getLogger(__name__)


class CloudStorageFactory(Singleton):
    CLASSNAME_CLASS_MAP = {
        AzureStorageManager.__name__: AzureStorageManager
    }
    @classmethod
    def instantiate(cls, class_name: str, azure_blob_config: AzureBlobConfig) -> ICloudStorageManager:
        """
        Instantiate or retrieve a singleton instance of an Azure Blob Manager class.

        :param class_name: Name of the Azure Blob Manager class to instantiate.
        :param azure_blob_config: An instance of `AzureBlobConfig` containing the necessary configuration
                              settings for Azure Blob Storage. This includes connection details, retry
                              mechanisms, memory limits, and operation size constraints.

        Configuration Attributes (config):
            - azure_connection_string (str): Connection string to access the Azure storage account.
            - container_name (str): Name of the blob container within the Azure storage account.
            - max_retries (int): Maximum number of retry attempts (must be > 0).
            - initial_backoff (int): Initial backoff delay in seconds before retry (must be > 0).
            - increment_base (int): Exponential growth factor for retry backoff (must be > 0).
            - memory_limit (int): Max memory for buffer/cache in bytes (must be > 0).
            - max_single_put_size (int): Max size (bytes) for single put operation (min 1024 bytes).
            - max_single_get_size (int): Max size (bytes) for single get operation (min 1024 bytes).
            - max_chunk_get_size (int): Chunk size (bytes) for partial downloads (min 1024 bytes).
            - max_block_size (int): Block size (bytes) for uploading in blocks (min 1024 bytes).

        :return: Singleton instance of the requested Azure Blob Manager class.
        :raises ValueError: If the specified class name is not found in `CLASSNAME_CLASS_MAP`.
        :raises Exception: If instantiation fails for other reasons.
    """
        if not cls.CLASSNAME_CLASS_MAP:
            logger.error("CLASSNAME_CLASS_MAP must be defined by sub-classes.")
            raise ValueError("CLASSNAME_CLASS_MAP must be defined by sub-classes.")

        if class_name not in cls.CLASSNAME_CLASS_MAP:
            logger.error(f"class_name :: {class_name} not available for instantiation.")
            raise ValueError(f"class_name :: {class_name} not available for instantiation.")


        if class_name not in cls._instances:
            cls._instances[class_name] = {}

        with cls._lock:

            if azure_blob_config in cls._instances[class_name]:
                return cls._instances[class_name][azure_blob_config]

            else:

                try:
                    instance = cls.CLASSNAME_CLASS_MAP[class_name](azure_blob_config)
                    cls._instances[class_name][azure_blob_config] = instance
                    return instance

                except Exception as exception:

                    logger.error(str(exception))
                    raise exception