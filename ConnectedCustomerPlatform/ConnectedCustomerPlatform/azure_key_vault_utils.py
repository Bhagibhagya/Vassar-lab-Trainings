import json
import logging
from typing import Optional

from azure.core.exceptions import ResourceNotFoundError
from ce_shared_services.factory.key_vault.keyvault_factory import KeyVaultFactory
from ce_shared_services.configuration_models.configuration_models import AzureKeyVaultConfig
from django.conf import settings
from redis import RedisError
from rest_framework import status

from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException, CustomException
from Platform.dao.impl.redis_dao_impl import RedisDaoImpl

logger=logging.getLogger(__name__)
class KeyVaultService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KeyVaultService, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        config = {
            "vault_url": settings.AZURE_KEY_VAULT_URL,
            "client_id": settings.IDENTITY_CLIENT_ID
        }

        # Uncomment this block for debugging in local environments without managed identity.
        # config = {"vault_url": settings.AZURE_KEY_VAULT_URL}

        # Instantiate the Azure Key Vault service using the KeyVaultFactory.
        self.key_vault_service = KeyVaultFactory.instantiate("AzureKeyVaultService", AzureKeyVaultConfig(**config))


    def get_secret_details(self,secret_name:str):
        logger.info("In microsoft_graph_utils :: get_secret_details")

        """
        Retrieves the details of a secret stored in Azure Key Vault.
    
        Args:
            secret_name (str): The name of the secret in Azure Key Vault.
    
        Returns:
            str: The value of the secret retrieved from Azure Key Vault.
    
        Raises:
            ResourceNotFoundException: If the specified secret name does not exist in Azure Key Vault.
        """

        # Configure settings for connecting to Azure Key Vault.

        try:
            # Retrieve the secret value using the Azure Key Vault service.
            secret_value = self.key_vault_service.get_secret(secret_name)

            # Return the retrieved secret value.
            return secret_value

        except ResourceNotFoundError as e:
            # Log an error if the specified secret name does not exist in Azure Key Vault.
            logger.error(f"Client Secret for secret name {secret_name} is not found, {str(e)}")

            # Raise a custom exception indicating the resource was not found.
            raise ResourceNotFoundException(
                f"Client Secret with secret name {secret_name} is not found, {str(e)}"
            )


    def update_secret_details(self,secret_name:str, secret_details:str) ->bool:
        logger.info("In microsoft_graph_utils :: update_token_in_secret")

        """
        Updates the Azure Key Vault secret with a new token.
    
        Args:
            secret_name (str): The name of the secret in Azure Key Vault.
            new_token (str): The new access token to be stored.
            previous_secret_details (dict): Existing secret details that need to be updated with the new token.
    
        Raises:
            ResourceNotFoundException: If the specified secret name does not exist in Azure Key Vault.
        """
        try:
            # Store the updated secret back to Azure Key Vault.
            update_status=self.key_vault_service.set_secret(secret_name, secret_details)
            if not update_status:
                logger.error(f"Cannot update secret details for with secret name {secret_name}")
                raise CustomException(f"Cannot update secret details for with secret name {secret_name}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return update_status
        except ResourceNotFoundError as e:
            # Log an error if the secret name does not exist in Azure Key Vault.
            logger.error(f"Client Secret with secret name {secret_name} is not found, {str(e)}")

            # Raise a custom exception indicating the resource was not found.
            raise ResourceNotFoundException(
                f"Client Secret with secret name {secret_name} is not found, {str(e)}"
            )

    def delete_secret_details(self,secret_name:str):
        """Deletes secret from keyvault with secret name"""
        try:
            self.key_vault_service.delete_secret(secret_name)
        except Exception as e:
            logger.error(f"Exception occurred while deleting secret with secret_name {secret_name} {e}")
            raise

    def get_secret_details_from_redis_or_keyvault(self,secret_name:str,expiry_for_redis:Optional[int]=None):
        logger.info("In microsoft_graph_utils :: get_secret_details")

        """
            Retrieves the value of a secret from Redis cache or Azure Key Vault.And update in redis
        
            Args:
                secret_name (str): The name of the secret to retrieve.
                expiry_for_redis (Optional[int]): Expiry time in seconds for caching the secret in Redis (optional).
        
            Returns:
                str: The value of the secret retrieved from Redis or Azure Key Vault.
        
            Raises:
                ResourceNotFoundException: If the secret is not found in Azure Key Vault.
        
            Logs:
                - Info: If the secret is not cached in Redis and is being fetched from Key Vault.
                - Error: If Redis operations fail or if a general exception occurs.
         """
        try:
            # Get secret details from redis
            secret_value_str = RedisDaoImpl().get_data_by_key(secret_name)
            if secret_value_str:
                return json.loads(secret_value_str)
            else:
                # Retrieve the secret value using the Azure Key Vault service.
                secret_value_str = self.get_secret_details(secret_name)
                if expiry_for_redis:
                    try:
                        # Update in cache
                        set_status = RedisDaoImpl().set_data_by_key_with_expiry(secret_name, secret_value_str, expiry_for_redis)
                        if not set_status:
                            logger.info("Cannot save secret details in cache")
                    except RedisError as e:
                        logger.error(f"Failed to perform set Redis operation for {secret_name} key: {str(e)}")
                else:
                    try:
                        set_status = RedisDaoImpl().set_data_by_key(secret_name, secret_value_str)
                        if not set_status:
                            logger.info("Cannot save secret details in cache")
                    except RedisError as e:
                        logger.error(f"Failed to perform set Redis operation for {secret_name} key: {str(e)}")
                # Return the retrieved secret value.
                return json.loads(secret_value_str)

        except ResourceNotFoundError as e:
            logger.error(f"Client Secret for secret name {secret_name} is not found, {str(e)}")

            # Raise a custom exception indicating the resource was not found.
            raise ResourceNotFoundException(
                f"Client Secret with secret name {secret_name} is not found, {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error occurred {str(e)}")
            raise

    def update_secret_in_redis_keyvault(self,secret_name:str,secret_value:str,expiry_for_redis:Optional[int]=None):
        """
    Updates the secret in both Azure Key Vault and Redis cache.

    Args:
        secret_name (str): The name of the secret to be updated.
        secret_value (str): The value of the secret to be updated.
        expiry_for_redis (int): Expiry time in seconds for caching the secret in Redis. None if no expiry needed

    Raises:
        CustomException: If the secret update in Azure Key Vault fails.
        Exception: For any general exceptions encountered during the update process.

    Logs:
        - Info: If the update to Azure Key Vault fails.
        - Error: If an error occurs while updating Key Vault or Redis.
    """
        try:
            update_status = self.update_secret_details(secret_name=secret_name,
                                                                   secret_details=secret_value)
            if not update_status:
                logger.info("Failed to update Keyvault with the secret")
                raise CustomException("Failed to update secret details", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Failed to update details in keyvault {str(e)}")
            raise
        try:
            if expiry_for_redis:
                set_status_flag = RedisDaoImpl().set_data_by_key_with_expiry(secret_name, secret_value, expiry_for_redis)
            else:
                set_status_flag = RedisDaoImpl().set_data_by_key(secret_name, secret_value)
            if not set_status_flag:
                logger.error("Failed to add secret to Cache")
        except Exception as e:
            logger.error(f"Failed to update details in redis cache for key {secret_name} {str(e)}")
            raise

    def delete_in_redis_key_vault(self,secret_name):
        try:
            self.delete_secret_details(secret_name)
        except Exception as e:
            logger.error(f"Exception occurred while deleting in keyvault {e}")
            raise
        try:
            RedisDaoImpl().delete_data_by_key(secret_name)
        except Exception as e:
            logger.error(f"Exception occurred while deleting in redis cache {e}")