import json
import unittest
from unittest.mock import patch, MagicMock
from azure.core.exceptions import ResourceNotFoundError

from redis.exceptions import RedisError

from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException, CustomException
from ConnectedCustomerPlatform.azure_key_vault_utils import KeyVaultService


class TestGet_Secret_details(unittest.TestCase):
    @patch("Platform.azure_key_vault_utils.KeyVaultFactory")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_get_secret_details_successful(self, mock_logger, mock_KeyVaultFactory):
        """Test successful retrieval of a secret from Azure Key Vault."""
        # Arrange
        secret_name = "test-secret"
        expected_secret_value = "test-secret-value"

        # Mock KeyVaultFactory service instance
        mock_key_vault_service = MagicMock()
        mock_key_vault_service.get_secret.return_value = expected_secret_value
        mock_KeyVaultFactory.instantiate.return_value = mock_key_vault_service

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        result = service.get_secret_details(secret_name)

        # Assert
        self.assertEqual(result, expected_secret_value)
        mock_key_vault_service.get_secret.assert_called_once_with(secret_name)
        mock_logger.info.assert_any_call("In microsoft_graph_utils :: get_secret_details")

    @patch("Platform.azure_key_vault_utils.KeyVaultFactory")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_get_secret_details_resource_not_found(self, mock_logger, mock_KeyVaultFactory):
        """Test handling of ResourceNotFoundError when the secret is not found."""
        # Arrange
        secret_name = "missing-secret"
        mock_key_vault_service = MagicMock()
        mock_key_vault_service.get_secret.side_effect = ResourceNotFoundError("Secret not found")
        mock_KeyVaultFactory.instantiate.return_value = mock_key_vault_service

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act & Assert
        with self.assertRaises(ResourceNotFoundException) as context:
            service.get_secret_details(secret_name)

        self.assertIn(f"Client Secret with secret name {secret_name} is not found", str(context.exception))
        mock_key_vault_service.get_secret.assert_called_once_with(secret_name)
        mock_logger.error.assert_called_once_with(
            f"Client Secret for secret name {secret_name} is not found, Secret not found"
        )


class TestUpdateSecretDetails(unittest.TestCase):
    @patch("Platform.azure_key_vault_utils.KeyVaultFactory")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_details_successful(self, mock_logger, mock_KeyVaultFactory):
        """Test successful update of a secret in Azure Key Vault."""
        # Arrange
        secret_name = "test-secret"
        secret_details = '{"access_token": "new-access-token"}'

        # Mock KeyVaultFactory service instance
        mock_key_vault_service = MagicMock()
        mock_key_vault_service.set_secret.return_value = True
        mock_KeyVaultFactory.instantiate.return_value = mock_key_vault_service

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        result = service.update_secret_details(secret_name, secret_details)

        # Assert
        self.assertTrue(result)
        mock_key_vault_service.set_secret.assert_called_once_with(secret_name, secret_details)
        mock_logger.info.assert_any_call("In microsoft_graph_utils :: update_token_in_secret")

    @patch("Platform.azure_key_vault_utils.KeyVaultFactory")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_details_failure_to_update(self, mock_logger, mock_KeyVaultFactory):
        """Test failure to update secret when set_secret returns False."""
        # Arrange
        secret_name = "test-secret"
        secret_details = '{"access_token": "new-access-token"}'

        # Mock KeyVaultFactory service instance
        mock_key_vault_service = MagicMock()
        mock_key_vault_service.set_secret.return_value = False
        mock_KeyVaultFactory.instantiate.return_value = mock_key_vault_service

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            service.update_secret_details(secret_name, secret_details)

        self.assertIn(f"Cannot update secret details for with secret name {secret_name}", str(context.exception))
        mock_key_vault_service.set_secret.assert_called_once_with(secret_name, secret_details)
        mock_logger.error.assert_called_once_with(
            f"Cannot update secret details for with secret name {secret_name}"
        )

    @patch("Platform.azure_key_vault_utils.KeyVaultFactory")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_details_resource_not_found(self, mock_logger, mock_KeyVaultFactory):
        """Test handling of ResourceNotFoundError when secret name does not exist."""
        # Arrange
        secret_name = "missing-secret"
        secret_details = '{"access_token": "new-access-token"}'

        # Mock KeyVaultFactory service instance
        mock_key_vault_service = MagicMock()
        mock_key_vault_service.set_secret.side_effect = ResourceNotFoundError("Secret not found")
        mock_KeyVaultFactory.instantiate.return_value = mock_key_vault_service

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act & Assert
        with self.assertRaises(ResourceNotFoundException) as context:
            service.update_secret_details(secret_name, secret_details)

        self.assertIn(f"Client Secret with secret name {secret_name} is not found", str(context.exception))
        mock_key_vault_service.set_secret.assert_called_once_with(secret_name, secret_details)
        mock_logger.error.assert_called_once_with(
            f"Client Secret with secret name {secret_name} is not found, Secret not found"
        )




class TestGetSecretDetailsFromRedisOrKeyVault(unittest.TestCase):
    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.KeyVaultService.get_secret_details")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_get_secret_details_from_redis_success(self, mock_logger, mock_get_secret_details, mock_RedisDaoImpl):
        """Test when the secret is successfully retrieved from Redis."""
        secret_name = "test-secret"
        secret_value = {"key": "value"}

        # Mock Redis to return the secret
        mock_RedisDaoImpl.return_value.get_data_by_key.return_value = json.dumps(secret_value)

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        result = service.get_secret_details_from_redis_or_keyvault(secret_name)

        # Assert
        self.assertEqual(result, secret_value)
        mock_RedisDaoImpl.return_value.get_data_by_key.assert_called_once_with(secret_name)
        mock_get_secret_details.assert_not_called()
        mock_logger.info.assert_any_call("In microsoft_graph_utils :: get_secret_details")

    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.KeyVaultService.get_secret_details")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_get_secret_details_from_keyvault_and_update_redis(self, mock_logger, mock_get_secret_details,
                                                               mock_RedisDaoImpl):
        """Test when the secret is retrieved from Azure Key Vault and updated in Redis."""
        secret_name = "test-secret"
        secret_value = json.dumps({"key": "value"})
        expiry_for_redis = 3600

        # Mock Redis to return None, forcing Key Vault retrieval
        mock_RedisDaoImpl.return_value.get_data_by_key.return_value = None
        # Mock Key Vault to return the secret
        mock_get_secret_details.return_value = secret_value
        # Mock Redis set operation to succeed
        mock_RedisDaoImpl.return_value.set_data_by_key_with_expiry.return_value = True

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        result = service.get_secret_details_from_redis_or_keyvault(secret_name, expiry_for_redis)

        # Assert
        self.assertEqual(result, json.loads(secret_value))
        mock_RedisDaoImpl.return_value.get_data_by_key.assert_called_once_with(secret_name)
        mock_get_secret_details.assert_called_once_with(secret_name)
        mock_RedisDaoImpl.return_value.set_data_by_key_with_expiry.assert_called_once_with(secret_name, secret_value,
                                                                                           expiry_for_redis)
        mock_logger.info.assert_any_call("In microsoft_graph_utils :: get_secret_details")

    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.KeyVaultService.get_secret_details")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_get_secret_details_keyvault_failure(self, mock_logger, mock_get_secret_details, mock_RedisDaoImpl):
        """Test when the secret is not found in Key Vault."""
        secret_name = "missing-secret"

        # Mock Redis to return None, forcing Key Vault retrieval
        mock_RedisDaoImpl.return_value.get_data_by_key.return_value = None
        # Mock Key Vault to raise a ResourceNotFoundError
        mock_get_secret_details.side_effect = ResourceNotFoundError("Secret not found")

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act & Assert
        with self.assertRaises(ResourceNotFoundException) as context:
            service.get_secret_details_from_redis_or_keyvault(secret_name)

        self.assertIn(f"Client Secret with secret name {secret_name} is not found", str(context.exception))
        mock_RedisDaoImpl.return_value.get_data_by_key.assert_called_once_with(secret_name)
        mock_get_secret_details.assert_called_once_with(secret_name)
        mock_logger.error.assert_called_once_with(
            f"Client Secret for secret name {secret_name} is not found, Secret not found"
        )

    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.KeyVaultService.get_secret_details")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_redis_error_handling(self, mock_logger, mock_get_secret_details, mock_RedisDaoImpl):
        """Test when a RedisError occurs during the set operation."""
        secret_name = "test-secret"
        secret_value = json.dumps({"key": "value"})

        # Mock Redis to return None, forcing Key Vault retrieval
        mock_RedisDaoImpl.return_value.get_data_by_key.return_value = None
        # Mock Key Vault to return the secret
        mock_get_secret_details.return_value = secret_value
        # Mock Redis set operation to raise a RedisError
        mock_RedisDaoImpl.return_value.set_data_by_key_with_expiry.side_effect = RedisError("Redis error")

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        result = service.get_secret_details_from_redis_or_keyvault(secret_name, expiry_for_redis=3600)

        # Assert
        self.assertEqual(result, json.loads(secret_value))
        mock_RedisDaoImpl.return_value.get_data_by_key.assert_called_once_with(secret_name)
        mock_get_secret_details.assert_called_once_with(secret_name)
        mock_logger.error.assert_called_once_with(
            f"Failed to perform set Redis operation for {secret_name} key: Redis error"
        )

    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.KeyVaultService.get_secret_details")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_general_exception_handling(self, mock_logger, mock_get_secret_details, mock_RedisDaoImpl):
        """Test when a general exception occurs."""
        secret_name = "test-secret"

        # Mock Redis to raise an unexpected exception
        mock_RedisDaoImpl.return_value.get_data_by_key.side_effect = Exception("Unexpected error")

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act & Assert
        with self.assertRaises(Exception) as context:
            service.get_secret_details_from_redis_or_keyvault(secret_name)

        self.assertIn("Unexpected error", str(context.exception))
        mock_RedisDaoImpl.return_value.get_data_by_key.assert_called_once_with(secret_name)
        mock_logger.error.assert_called_once_with("Error occurred Unexpected error")

    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.KeyVaultService.get_secret_details")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_else_case_no_expiry_for_redis(self, mock_logger, mock_get_secret_details, mock_RedisDaoImpl):
        """Test when expiry_for_redis is not provided (else case)."""
        secret_name = "test-secret"
        secret_value = json.dumps({"key": "value"})

        # Mock Redis to return None, forcing Key Vault retrieval
        mock_RedisDaoImpl.return_value.get_data_by_key.return_value = None
        # Mock Key Vault to return the secret
        mock_get_secret_details.return_value = secret_value
        # Mock Redis set operation to succeed
        mock_RedisDaoImpl.return_value.set_data_by_key.return_value = True

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        result = service.get_secret_details_from_redis_or_keyvault(secret_name)

        # Assert
        self.assertEqual(result, json.loads(secret_value))
        mock_RedisDaoImpl.return_value.get_data_by_key.assert_called_once_with(secret_name)
        mock_get_secret_details.assert_called_once_with(secret_name)
        mock_RedisDaoImpl.return_value.set_data_by_key.assert_called_once_with(secret_name, secret_value)
        mock_logger.error.assert_not_called()

class TestUpdateSecretDetailsKeyvaultRedis(unittest.TestCase):
    @patch("Platform.azure_key_vault_utils.KeyVaultService.update_secret_details")
    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_in_redis_keyvault_success_with_expiry(self, mock_logger, mock_RedisDaoImpl,
                                                                 mock_update_secret_details):
        """Test successful update of secret in both Key Vault and Redis with expiry."""
        secret_name = "test-secret"
        secret_value = "test-value"
        expiry = 3600  # Expiry time in seconds

        # Mock successful update in Key Vault
        mock_update_secret_details.return_value = True
        # Mock successful set in Redis with expiry
        mock_RedisDaoImpl.return_value.set_data_by_key_with_expiry.return_value = True

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        service.update_secret_in_redis_keyvault(secret_name, secret_value, expiry)

        # Assert
        mock_update_secret_details.assert_called_once_with(secret_name=secret_name, secret_details=secret_value)
        mock_RedisDaoImpl.return_value.set_data_by_key_with_expiry.assert_called_once_with(secret_name, secret_value,
                                                                                           expiry)
        mock_logger.error.assert_not_called()

    @patch("Platform.azure_key_vault_utils.KeyVaultService.update_secret_details")
    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_in_redis_keyvault_success_without_expiry(self, mock_logger, mock_RedisDaoImpl,
                                                                    mock_update_secret_details):
        """Test successful update of secret in both Key Vault and Redis without expiry."""
        secret_name = "test-secret"
        secret_value = "test-value"

        # Mock successful update in Key Vault
        mock_update_secret_details.return_value = True
        # Mock successful set in Redis without expiry
        mock_RedisDaoImpl.return_value.set_data_by_key.return_value = True

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        service.update_secret_in_redis_keyvault(secret_name, secret_value)

        # Assert
        mock_update_secret_details.assert_called_once_with(secret_name=secret_name, secret_details=secret_value)
        mock_RedisDaoImpl.return_value.set_data_by_key.assert_called_once_with(secret_name, secret_value)
        mock_logger.error.assert_not_called()

    @patch("Platform.azure_key_vault_utils.KeyVaultService.update_secret_details")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_in_redis_keyvault_keyvault_failure(self, mock_logger, mock_update_secret_details):
        """Test failure in updating secret in Key Vault."""
        secret_name = "test-secret"
        secret_value = "test-value"

        # Mock Key Vault update failure
        mock_update_secret_details.return_value = False

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            service.update_secret_in_redis_keyvault(secret_name, secret_value)

        self.assertEqual(str(context.exception), "Failed to update secret details")
        mock_update_secret_details.assert_called_once_with(secret_name=secret_name, secret_details=secret_value)
        mock_logger.info.assert_called_once_with("Failed to update Keyvault with the secret")

    @patch("Platform.azure_key_vault_utils.KeyVaultService.update_secret_details")
    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_in_redis_keyvault_redis_failure_with_expiry(self, mock_logger, mock_RedisDaoImpl,
                                                                       mock_update_secret_details):
        """Test failure in updating secret in Redis with expiry."""
        secret_name = "test-secret"
        secret_value = "test-value"
        expiry = 3600  # Expiry time in seconds

        # Mock successful Key Vault update
        mock_update_secret_details.return_value = True
        # Mock Redis set failure with expiry
        mock_RedisDaoImpl.return_value.set_data_by_key_with_expiry.return_value = False

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        service.update_secret_in_redis_keyvault(secret_name, secret_value, expiry)

        # Assert
        mock_update_secret_details.assert_called_once_with(secret_name=secret_name, secret_details=secret_value)
        mock_RedisDaoImpl.return_value.set_data_by_key_with_expiry.assert_called_once_with(secret_name, secret_value,
                                                                                           expiry)
        mock_logger.error.assert_called_once_with("Failed to add secret to Cache")

    @patch("Platform.azure_key_vault_utils.KeyVaultService.update_secret_details")
    @patch("Platform.azure_key_vault_utils.RedisDaoImpl")
    @patch("Platform.azure_key_vault_utils.logger")
    def test_update_secret_in_redis_keyvault_redis_failure_without_expiry(self, mock_logger, mock_RedisDaoImpl,
                                                                          mock_update_secret_details):
        """Test failure in updating secret in Redis without expiry."""
        secret_name = "test-secret"
        secret_value = "test-value"

        # Mock successful Key Vault update
        mock_update_secret_details.return_value = True
        # Mock Redis set failure without expiry
        mock_RedisDaoImpl.return_value.set_data_by_key.return_value = False

        # Create KeyVaultService instance
        service = KeyVaultService()

        # Act
        service.update_secret_in_redis_keyvault(secret_name, secret_value)

        # Assert
        mock_update_secret_details.assert_called_once_with(secret_name=secret_name, secret_details=secret_value)
        mock_RedisDaoImpl.return_value.set_data_by_key.assert_called_once_with(secret_name, secret_value)
        mock_logger.error.assert_called_once_with("Failed to add secret to Cache")

