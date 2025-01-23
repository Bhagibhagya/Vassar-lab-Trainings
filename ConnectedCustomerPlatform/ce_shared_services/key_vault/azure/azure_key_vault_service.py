import logging
import time
import json

from aiohttp.web_fileresponse import content_type
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import AzureError, ResourceNotFoundError, HttpResponseError
from torch.backends.mkldnn import enabled
from datetime import datetime, timedelta, timezone

from ce_shared_services.key_vault.interface.key_vault import IKeyVault
from ce_shared_services.key_vault.azure import constants
from ce_shared_services.configuration_models.configuration_models import AzureKeyVaultConfig

logger = logging.getLogger(__name__)

def default_expires_on():
    return datetime.now(timezone.utc) + timedelta(days=5 * 365.25)  # 5 years from now

class AzureKeyVaultService(IKeyVault):

    def __init__(self, keyvault_config: AzureKeyVaultConfig):
        if not isinstance(keyvault_config, AzureKeyVaultConfig):
            logger.error(ErrorMessages.INVALID_AZURE_CONFIGURATION)
            raise ValueError(ErrorMessages.INVALID_AZURE_CONFIGURATION)
        self.keyvault_config = keyvault_config
        self._client = self._create_client()


    def _create_client(self):
        logger.info("In AzureKeyVaultService :: _create_client")
        try:
            #credential = DefaultAzureCredential()
            credential = ManagedIdentityCredential(client_id=self.keyvault_config.client_id)
            return SecretClient(vault_url=self.keyvault_config.vault_url, credential=credential)
        except AzureError as e:
            logger.error(f"Failed to create SecretClient: {str(e)}")
            raise  # Raise the exception for handling
        except Exception as e:
            logger.error(f"Unexpected error while creating SecretClient: {str(e)}")
            raise  # Raise the exception for handling


    def set_secret(self, secret_name, secret_value, expires_on=None):
        if expires_on is None:
            expires_on = default_expires_on()
        try:
            result = self._client.set_secret(secret_name, secret_value, expires_on=expires_on)
            logger.info(f"Secret '{secret_name}' set successfully.")
            return result
        except Exception as e:
            logger.error(f"Failed to set secret '{secret_name}': {str(e)}")
            raise  # Raise other exceptions for handling


    def get_secret(self, secret_name):
        try:
            secret = self._client.get_secret(secret_name)
            logger.info(f"Secret '{secret_name}' fetched successfully.")
            return secret.value
        except ResourceNotFoundError as e:
            logger.error(f"Secret '{secret_name}' not found: {str(e)}")
            raise  # Raise the exception to let the caller handle it
        except HttpResponseError as e:
            logger.error(f"Http response error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch secret '{secret_name}': {str(e)}")
            raise  # Raise other exceptions for handling


    def get_secret_as_json(self, secret_name):
        try:
            secret = self._client.get_secret(secret_name)
            secret_json = json.loads(secret.value)
            logger.info(f"Secret '{secret_name}' fetched successfully.")
            return secret_json
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from secret '{secret_name}': {str(e)}")
            raise  # Raise the exception to let the caller handle it
        except ResourceNotFoundError as e:
            logger.error(f"Secret '{secret_name}' not found: {str(e)}")
            raise
        except HttpResponseError as e:
            logger.error(f"Http response error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch secret '{secret_name}': {str(e)}")
            raise  # Raise other exceptions for handling

    def delete_secret(self, secret_name):
        try:
            # Start the delete operation
            logger.info(f"Initiating delete operation for secret '{secret_name}'.")
            delete_operation = self._client.begin_delete_secret(secret_name)
            deleted_secret = delete_operation.result()  # Wait for the delete operation to complete
            logger.info(f"Secret '{secret_name}' deleted successfully.")

            # Retry mechanism for purging the secret
            retries = constants.MAX_RETRIES
            while retries > 0:
                try:
                    # Purge the deleted secret
                    logger.info(f"Attempting to purge secret '{secret_name}'.")
                    self._client.purge_deleted_secret(secret_name)
                    logger.info(f"Secret '{secret_name}' purged successfully.")
                    break
                except Exception as e:
                    # Secret is still in the process of being deleted, retry after waiting
                    logger.warning(f"Conflict error encountered while purging secret: {e}. Retrying in 5 seconds...")
                    time.sleep(3*(constants.MAX_RETRIES - retries + 1))
                    retries -= 1

            return deleted_secret

        except ResourceNotFoundError as e:
            logger.error(f"Secret '{secret_name}' not found: {str(e)}")
            raise
        except HttpResponseError as e:
            logger.error(f"Http response error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_name}': {str(e)}")
            raise
