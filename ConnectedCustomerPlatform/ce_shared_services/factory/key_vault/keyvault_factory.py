import logging

from ce_shared_services.key_vault.azure.azure_key_vault_service import AzureKeyVaultService
from ce_shared_services.key_vault.interface.key_vault import IKeyVault
from ce_shared_services.configuration_models.configuration_models import AzureKeyVaultConfig

from ce_shared_services.factory.scope.singleton import Singleton

logger = logging.getLogger(__name__)


class KeyVaultFactory(Singleton):

    CLASSNAME_CLASS_MAP = {
        AzureKeyVaultService.__name__: AzureKeyVaultService
    }

    @classmethod
    def instantiate(cls, class_name: str, keyvault_config: AzureKeyVaultConfig) -> IKeyVault:
        """
        Instantiate or retrieve a singleton instance of an Azure Keyvault Config class.

        :param class_name: Name of the Azure Keyvault class to instantiate.
        :param keyvault_config: An instance of `AzureKeyVaultConfig` containing the necessary configuration
                              settings for Azure Keyvault. This includes connection details, client_id, etc.

        Configuration Attributes (config):
            - keyvault_url (str): The keyvault url to connect.
            - client_id (str): Managed Identity credential client id.


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

            if keyvault_config in cls._instances[class_name]:
                return cls._instances[class_name][keyvault_config]

            else:

                try:
                    instance = cls.CLASSNAME_CLASS_MAP[class_name](keyvault_config)
                    cls._instances[class_name][keyvault_config] = instance
                    return instance

                except Exception as exception:

                    logger.error(str(exception))
                    raise exception