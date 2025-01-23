import uuid
from unittest.mock import patch, MagicMock

from django.db import DatabaseError, IntegrityError
from django.utils import timezone
from dotenv import load_dotenv
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import EmailServer, EmailServerCustomerApplicationMapping, UserEmailSetting
from EmailApp.constant.constants import MicrosoftSecretDetailsKeys, ServerType
from Platform.tests.test_data import create_email_server_test_data, create_customer_application_instances
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from datetime import datetime, timedelta


load_dotenv()


class BaseTestCase(TestCase):

    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        self.email_server, self.email_server2, self.email_server_mapping = create_email_server_test_data()

        # Common headers
        self.headers = {
            'customer-uuid': self.email_server_mapping.customer_uuid_id,
            'application-uuid': self.email_server_mapping.application_uuid_id,
            'user-uuid': self.email_server.created_by,
        }


####
# =========================== Tests for EmailServerSettingsViewSet ===================================
####
class EmailServerSettingsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.server_type = self.email_server.server_type
        self.server_url = self.email_server.server_url
        self.email_provider_name = self.email_server.email_provider_name
        self.port = self.email_server.port
        self.is_ssl_enabled = self.email_server_mapping.is_ssl_enabled
        self.sync_time_interval = self.email_server_mapping.sync_time_interval
        self.email_server_uuid = self.email_server.email_server_uuid
        self.email_server_uuid2 = self.email_server2.email_server_uuid
        self.email_server_uuid3 = uuid.uuid4()

    ###
    # ========= Tests for "add_email_server" API ==========
    ###

    # 1. With all correct values
    def test_add_email_server_success(self):
        response = self.client.post(
            reverse("Platform:email_server"),
            data={"0" : {
                "email_server_uuid" : self.email_server_uuid2,
                "server_type": self.server_type,
                "server_url": self.server_url,
                "email_provider_name": self.email_provider_name,
                "port": self.port,
                "is_ssl_enabled": self.is_ssl_enabled,
                "sync_time_interval": self.sync_time_interval
            }},
            headers=self.headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.ADD_EMAIL_SERVER_SUCCESS, response.data.get('result'))

    # 2. Missing required headers
    def test_add_email_server_missing_headers(self):
        response = self.client.post(
            reverse("Platform:email_server"),
            data={"0": {
                'email_server_uuid': self.email_server_uuid2,
                'server_type': self.server_type,
                'server_url': self.server_url,
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval
            }},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.CUSTOMER_ID_NOT_NULL, response.data.get('result'))

    # 3. Missing payload data
    def test_add_email_server_missing_server_type(self):
        response = self.client.post(
            reverse("Platform:email_server"),
            {"0": {
                'email_server_uuid': self.email_server_uuid2,
                'server_type': "",
                'server_url': self.server_url,
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval
            }},
            headers=self.headers,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', str(response.data.get('result')[0]['server_type']))

    # 4. Unique constraint violation
    def test_add_email_server_unique_constraint_violation(self):
        response = self.client.post(
            reverse("Platform:email_server"),
            data={"0" : {
                "email_server_uuid" : self.email_server_uuid,
                "server_type": self.server_type,
                "server_url": self.server_url,
                "email_provider_name": self.email_provider_name,
                "port": self.port,
                "is_ssl_enabled": self.is_ssl_enabled,
                "sync_time_interval": self.sync_time_interval
            }},
            headers=self.headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_SERVER_EXISTS, response.data.get('result'))

    # 5. Default server not found
    def test_add_email_server_default_server_not_found(self):
        response = self.client.post(
            reverse("Platform:email_server"),
            data={"0" : {
                "email_server_uuid" : uuid.uuid4(),
                "server_type": self.server_type,
                "server_url": self.server_url,
                "email_provider_name": self.email_provider_name,
                "port": self.port,
                "is_ssl_enabled": self.is_ssl_enabled,
                "sync_time_interval": self.sync_time_interval
            }},
            headers=self.headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_SERVER_NOT_FOUND, response.data.get('result'))

    ###
    # ========= Tests for "get_email_server_by_customer" API ==========
    ###
    # 1. With all correct values
    def test_get_email_server_by_customer_success(self):
        response = self.client.get(
            reverse('Platform:email_server'),
            headers=self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.data.get('result'):
            self.assertIn('SMTP', response.data.get('result'))

    # 2. With missing customer uuid
    def test_get_email_server_by_customer_missing_customer_uuid(self):
        response = self.client.get(
            reverse('Platform:email_server'),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ErrorMessages.CUSTOMER_ID_NOT_NULL, response.data.get('result'))

    ###
    # ========= Tests for "edit_email_server" API ==========
    ###
    # 1. With all correct values
    def test_edit_email_server_success(self):

        response = self.client.put(
            reverse("Platform:email_server"),
            data={"0": {
                'mapping_uuid': self.email_server_mapping.mapping_uuid,
                'email_server_uuid': self.email_server_uuid2,
                'server_type': self.server_type,
                'server_url': self.server_url,
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval,
            }},
            format="json",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.UPDATE_EMAIL_SERVER_SUCCESS, response.data.get('result'))

    # 2. With missing headers
    def test_edit_email_server_missing_headers(self):
        response = self.client.put(
            reverse("Platform:email_server"),
            data={"0": {
                'mapping_uuid': self.email_server_mapping.mapping_uuid,
                'email_server_uuid': self.email_server_uuid2,
                'server_type': self.server_type,
                'server_url': self.server_url,
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval
            }},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.CUSTOMER_ID_NOT_NULL, response.data.get('result'))

    # 3. With missing email_server_uuid
    def test_edit_email_server_missing_email_server_uuid(self):
        response = self.client.put(
            reverse("Platform:email_server"),
            data={"0": {
                'mapping_uuid': self.email_server_mapping.mapping_uuid,
                'email_server_uuid': "",
                'server_type': self.server_type,
                'server_url': self.server_url,
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval
            }},
            format="json",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Must be a valid UUID.', response.data.get('result')[0]['email_server_uuid'])

    # 4. With missing required fields in payload
    def test_edit_email_server_missing_server_url(self):
        response = self.client.put(
            reverse("Platform:email_server"),
            data={"0": {
                'mapping_uuid': self.email_server_mapping.mapping_uuid,
                'email_server_uuid': self.email_server_uuid2,
                'server_type': self.server_type,
                'server_url': '',
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval
            }},
            format="json",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', str(response.data.get('result')[0]['server_url']))


    def test_edit_email_server_with_no_server_exists(self):
        response = self.client.put(
            reverse("Platform:email_server"),
            data={"0": {
                'mapping_uuid': self.email_server_mapping.mapping_uuid,
                'email_server_uuid': self.email_server_uuid3,
                'server_type': self.server_type,
                'server_url': 'imap.gmail.com',
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval
            }},
            format="json",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_SERVER_NOT_FOUND, str(response.data.get('result')))

    # 4. Invalid mapping uuid
    def test_edit_email_server_unique_constraint_violation(self):
        response = self.client.put(
            reverse("Platform:email_server"),
            data={"0": {
                'mapping_uuid': uuid.uuid4(),
                'email_server_uuid': self.email_server_uuid,
                'server_type': self.server_type,
                'server_url': self.server_url,
                'email_provider_name': self.email_provider_name,
                'port': self.port,
                'is_ssl_enabled': self.is_ssl_enabled,
                'sync_time_interval': self.sync_time_interval,
            }},
            format="json",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_SERVER_NOT_FOUND, response.data.get('result'))

    # 5. Default server not found
    def test_edit_email_server_default_server_not_found(self):
        response = self.client.put(
            reverse("Platform:email_server"),
            data={"0": {
                "mapping_uuid": self.email_server_mapping.mapping_uuid,
                "email_server_uuid": self.email_server_uuid3,
                "server_type": self.server_type,
                "server_url": self.server_url,
                "email_provider_name": self.email_provider_name,
                "port": self.port,
                "is_ssl_enabled": self.is_ssl_enabled,
                "sync_time_interval": self.sync_time_interval
            }},
            headers=self.headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_SERVER_NOT_FOUND, response.data.get('result'))




class GetOutlookServerTestCase(BaseTestCase):
    def setUp(self):
        """Setup test data and mocks"""
        super().setUp()

        # Additional setup specific to outlook server
        self.mapping_uuid = uuid.uuid4()
        self.microsoft_client_id = "test_client_id"
        self.microsoft_tenant_id = "test_tenant_id"
        self.microsoft_client_secret = "test_client_secret"
        self.secret_created_ts = datetime.now().isoformat()
        self.secret_expiry = (datetime.now() + timedelta(days=30)).isoformat()

        # Mock secret data that would come from KeyVault
        self.secret_details = {
            MicrosoftSecretDetailsKeys.CLIENT_SECRET.value: self.microsoft_client_secret,
            MicrosoftSecretDetailsKeys.SECRET_CREATED_TS.value: self.secret_created_ts,
            MicrosoftSecretDetailsKeys.SECRET_EXPIRY.value: self.secret_expiry
        }

        # Create test email server for Outlook (MSAL)
        self.outlook_server = EmailServer.objects.create(
            email_server_uuid=uuid.uuid4(),
            server_type=ServerType.MSAL.value,
            created_by=self.email_server.created_by
        )

        # Create mapping for outlook server
        self.outlook_mapping = EmailServerCustomerApplicationMapping.objects.create(
            mapping_uuid=self.mapping_uuid,
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid,
            email_server_uuid=self.outlook_server,
            microsoft_client_id=self.microsoft_client_id,
            microsoft_tenant_id=self.microsoft_tenant_id,
            sync_time_interval=30
        )

    @patch('Platform.azure_key_vault_utils.KeyVaultService.get_secret_details_from_redis_or_keyvault')
    def test_get_outlook_server_success(self, mock_get_secret):
        """Test successful retrieval of outlook server details"""
        # Mock KeyVault response
        mock_get_secret.return_value = self.secret_details

        response = self.client.get(
            reverse("Platform:outlook_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('result')

        # Verify response structure and values
        self.assertEqual(data['mapping_uuid'], str(self.mapping_uuid))
        self.assertEqual(data['email_server_uuid'], str(self.outlook_server.email_server_uuid))
        self.assertEqual(data['microsoft_client_id'], self.microsoft_client_id)
        self.assertEqual(data['microsoft_tenant_id'], self.microsoft_tenant_id)
        self.assertEqual(data['microsoft_client_secret'], self.microsoft_client_secret)
        self.assertEqual(data['microsoft_secret_created_ts'], self.secret_created_ts)
        self.assertEqual(data['microsoft_secret_expiry'], self.secret_expiry)

    def test_get_outlook_server_no_server_configured(self):
        """Test when no outlook server is configured"""
        # Delete the outlook mapping
        self.outlook_mapping.delete()

        response = self.client.get(
            reverse("Platform:outlook_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('result'), {})

    def test_get_outlook_server_deleted_server(self):
        """Test when outlook server is marked as deleted"""
        # Mark the server as deleted
        self.outlook_server.is_deleted = True
        self.outlook_server.save()

        response = self.client.get(
            reverse("Platform:outlook_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('result'), {})

    @patch('Platform.azure_key_vault_utils.KeyVaultService.get_secret_details_from_redis_or_keyvault')
    def test_get_outlook_server_keyvault_error(self, mock_get_secret):
        """Test handling of KeyVault service errors"""
        # Mock KeyVault service to raise an exception
        mock_get_secret.side_effect = Exception("KeyVault error")

        response = self.client.get(
            reverse("Platform:outlook_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_outlook_server_missing_headers(self):
        """Test API behavior with missing required headers"""
        # Remove required headers
        headers = self.headers.copy()
        del headers['customer-uuid']

        response = self.client.get(
            reverse("Platform:outlook_server"),
            headers=headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_outlook_server_non_msal_type(self):
        """Test when server type is not MSAL"""
        # Change server type to non-MSAL
        self.outlook_server.server_type = "SMTP"
        self.outlook_server.save()

        response = self.client.get(
            reverse("Platform:outlook_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('result'), {})

    @patch('Platform.azure_key_vault_utils.KeyVaultService.get_secret_details_from_redis_or_keyvault')
    def test_get_outlook_server_partial_secret_details(self, mock_get_secret):
        """Test handling of partial secret details from KeyVault"""
        # Mock incomplete secret details
        incomplete_secret_details = {
            MicrosoftSecretDetailsKeys.CLIENT_SECRET.value: self.microsoft_client_secret,
            # Missing other fields
        }
        mock_get_secret.return_value = incomplete_secret_details

        response = self.client.get(
            reverse("Platform:outlook_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)



class SaveOutlookServerTestCase(BaseTestCase):
    def setUp(self):
        """Setup test data and mocks"""
        super().setUp()

        # Create default MSAL server
        self.default_outlook_server = EmailServer.objects.create(
            email_server_uuid=uuid.uuid4(),
            server_type=ServerType.MSAL.value,
            is_default=True,
            created_by=self.email_server.created_by
        )

        # Test data for outlook server
        self.mapping_uuid = str(uuid.uuid4())
        self.microsoft_data = {
            "microsoft_client_id": "test_client_id",
            "microsoft_tenant_id": "test_tenant_id",
            "microsoft_client_secret": "test_client_secret",
            "secret_created_ts": 4732234,
            "secret_expiration_time": 647382,
            "sync_time_interval": 2
        }

        # Mock access token
        self.access_token = "mock_access_token"

        # Prepare secret details
        self.secret_details = {
            MicrosoftSecretDetailsKeys.ACCESS_TOKEN.value: self.access_token,
            MicrosoftSecretDetailsKeys.CLIENT_SECRET.value: self.microsoft_data["microsoft_client_secret"],
            MicrosoftSecretDetailsKeys.SECRET_EXPIRY.value: self.microsoft_data["secret_expiration_time"],
            MicrosoftSecretDetailsKeys.SECRET_CREATED_TS.value: self.microsoft_data["secret_created_ts"]
        }

    @patch('Platform.azure_key_vault_utils.KeyVaultService.update_secret_in_redis_keyvault')
    @patch('Platform.services.impl.email_server_service_impl.get_access_token')
    def test_add_outlook_server_success(self, mock_get_access_token, mock_update_secret):
        """Test successful addition of new outlook server"""
        # Mock access token generation
        mock_get_access_token.return_value = self.access_token

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=self.microsoft_data,
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('result'), SuccessMessages.ADD_EMAIL_SERVER_SUCCESS)

        # Verify mock calls
        mock_get_access_token.assert_called_once_with(
            self.microsoft_data["microsoft_client_secret"],
            self.microsoft_data["microsoft_client_id"],
            self.microsoft_data["microsoft_tenant_id"]
        )
        mock_update_secret.assert_called_once()

    @patch('Platform.azure_key_vault_utils.KeyVaultService.update_secret_in_redis_keyvault')
    @patch('Platform.services.impl.email_server_service_impl.get_access_token')
    def test_update_outlook_server_success(self, mock_get_access_token, mock_update_secret):
        """Test successful update of existing outlook server"""
        # Create existing mapping
        mapping = EmailServerCustomerApplicationMapping.objects.create(
            mapping_uuid=self.mapping_uuid,
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid,
            email_server_uuid=self.default_outlook_server,
            microsoft_client_id=self.microsoft_data["microsoft_client_id"],
            microsoft_tenant_id=self.microsoft_data["microsoft_tenant_id"],
            sync_time_interval=30
        )

        # Add mapping_uuid for update
        update_data = {**self.microsoft_data, "mapping_uuid": self.mapping_uuid}
        mock_get_access_token.return_value = self.access_token

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=update_data,
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('result'), SuccessMessages.UPDATE_EMAIL_SERVER_SUCCESS)

    def test_save_outlook_server_invalid_data(self):
        """Test validation error handling"""
        # Remove required field
        invalid_data = self.microsoft_data.copy()
        del invalid_data["microsoft_client_id"]

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=invalid_data,
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('Platform.services.impl.email_server_service_impl.get_access_token')
    def test_save_outlook_server_invalid_credentials(self, mock_get_access_token):
        """Test handling of invalid Microsoft credentials"""
        mock_get_access_token.side_effect = CustomException("Invalid credentials")

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=self.microsoft_data,
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Please recheck details provided", str(response.data))

    def test_save_outlook_server_no_default_server(self):
        """Test when no default MSAL server exists"""
        # Delete default server
        self.default_outlook_server.delete()

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=self.microsoft_data,
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Default email server for Outlook not found", str(response.data))

    @patch('Platform.azure_key_vault_utils.KeyVaultService.update_secret_in_redis_keyvault')
    @patch('Platform.services.impl.email_server_service_impl.get_access_token')
    def test_save_outlook_server_keyvault_error(self, mock_get_access_token, mock_update_secret):
        """Test handling of KeyVault service errors"""
        mock_get_access_token.return_value = self.access_token
        mock_update_secret.side_effect = Exception("KeyVault error")

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=self.microsoft_data,
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.ADD_EMAIL_SERVER_FAILED, str(response.data))

    @patch('Platform.azure_key_vault_utils.KeyVaultService.update_secret_in_redis_keyvault')
    @patch('Platform.services.impl.email_server_service_impl.get_access_token')
    def test_save_outlook_server_duplicate_error(self, mock_get_access_token, mock_update_secret):
        """Test handling of duplicate server mappings"""
        # Create existing mapping
        mapping = EmailServerCustomerApplicationMapping.objects.create(
            mapping_uuid=uuid.uuid4(),
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid,
            email_server_uuid=self.default_outlook_server,
            microsoft_client_id=self.microsoft_data["microsoft_client_id"],
            microsoft_tenant_id=self.microsoft_data["microsoft_tenant_id"],
            sync_time_interval=30
        )

        mock_get_access_token.return_value = self.access_token

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=self.microsoft_data,
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email Server already exists", str(response.data))

    def test_save_outlook_server_missing_headers(self):
        """Test API behavior with missing required headers"""
        headers = self.headers.copy()
        del headers['customer-uuid']

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=self.microsoft_data,
            headers=headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('Platform.azure_key_vault_utils.KeyVaultService.update_secret_in_redis_keyvault')
    @patch('Platform.services.impl.email_server_service_impl.get_access_token')
    def test_update_nonexistent_mapping(self, mock_get_access_token, mock_update_secret):
        """Test updating a non-existent mapping"""
        update_data = {**self.microsoft_data, "mapping_uuid": str(uuid.uuid4())}
        mock_get_access_token.return_value = self.access_token

        response = self.client.post(
            reverse("Platform:outlook_server"),
            data=update_data,
            headers=self.headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class DeleteEmailServerTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create test email servers and mappings
        self.user_uuid = str(uuid.uuid4())
        self.current_time = timezone.now()

        # Different server - should succeed
        different_server = EmailServer.objects.create(
            email_server_uuid=uuid.uuid4(),
            server_type=ServerType.MSAL.value
        )
        different_server_mapping = EmailServerCustomerApplicationMapping.objects.create(
            mapping_uuid=uuid.uuid4(),
            email_server_uuid=different_server,
            application_uuid=self.email_server_mapping.application_uuid,
            customer_uuid=self.email_server_mapping.customer_uuid,
            sync_time_interval=30
        )

        # Create user email settings
        self.user_email_setting1 = UserEmailSetting.objects.create(
            user_email_uuid=uuid.uuid4(),
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid,
            created_by=self.user_uuid,
            email_id="test1@example.com"
        )

        self.user_email_setting2 = UserEmailSetting.objects.create(
            user_email_uuid=uuid.uuid4(),
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid,
            created_by=self.user_uuid,
            email_id="test2@example.com"
        )

    def test_delete_email_server_success(self):
        """Test successful deletion of email servers and settings"""
        response = self.client.delete(
            reverse("Platform:email_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('result'), SuccessMessages.DELETE_EMAIL_SERVER_SUCCESSFUL)

        # Verify user email settings are soft deleted
        user_settings = UserEmailSetting.objects.filter(
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid
        )
        for setting in user_settings:
            self.assertTrue(setting.is_deleted)
            self.assertEqual(str(setting.updated_by), str(self.headers['user-uuid']))

        # Verify email server mappings are hard deleted
        mappings_count = EmailServerCustomerApplicationMapping.objects.filter(
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid
        ).count()
        self.assertEqual(mappings_count, 0)

    def test_delete_email_server_no_data(self):
        """Test deletion when no data exists"""
        # Delete existing data
        EmailServerCustomerApplicationMapping.objects.all().delete()
        UserEmailSetting.objects.all().delete()

        response = self.client.delete(
            reverse("Platform:email_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('result'), ErrorMessages.DELETE_EMAIL_SERVER_FAILED)

    def test_delete_email_server_missing_headers(self):
        """Test API behavior with missing required headers"""
        headers = self.headers.copy()
        del headers['customer-uuid']

        response = self.client.delete(
            reverse("Platform:email_server"),
            headers=headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('DatabaseApp.models.UserEmailSetting.objects.filter')
    def test_delete_email_server_user_settings_error(self, mock_user_settings):
        """Test handling of database error during user settings deletion"""
        mock_user_settings.side_effect = Exception("Database error")

        response = self.client.delete(
            reverse("Platform:email_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.DELETE_EMAIL_SERVER_FAILED, str(response.data))

    @patch('DatabaseApp.models.EmailServerCustomerApplicationMapping.objects.filter')
    def test_delete_email_server_mapping_error(self, mock_mapping):
        """Test handling of database error during server mapping deletion"""
        mock_mapping.side_effect = DatabaseError("Database error")

        response = self.client.delete(
            reverse("Platform:email_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.DELETE_EMAIL_SERVER_FAILED, str(response.data))

    def test_delete_email_server_partial_deletion(self):
        """Test scenario where only some records are deleted"""
        # Create records for different customer/application
        different_customer_uuid = uuid.uuid4()
        different_application_uuid = uuid.uuid4()
        application2, customer2 = create_customer_application_instances()
        different_mapping = EmailServerCustomerApplicationMapping.objects.create(
            mapping_uuid=uuid.uuid4(),
            customer_uuid=customer2,
            application_uuid=application2,
            email_server_uuid=self.email_server,
            sync_time_interval=30
        )

        different_setting = UserEmailSetting.objects.create(
            user_email_uuid=uuid.uuid4(),
            customer_uuid=customer2,
            application_uuid=application2,
            created_by=self.user_uuid,
            email_id="different@example.com"
        )

        response = self.client.delete(
            reverse("Platform:email_server"),
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only target records are deleted
        # Original records should be deleted/updated
        original_mappings = EmailServerCustomerApplicationMapping.objects.filter(
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid
        )
        self.assertEqual(original_mappings.count(), 0)

        original_settings = UserEmailSetting.objects.filter(
            customer_uuid=self.email_server_mapping.customer_uuid,
            application_uuid=self.email_server_mapping.application_uuid
        )
        for setting in original_settings:
            self.assertTrue(setting.is_deleted)

        # Different customer/application records should remain unchanged
        different_mappings = EmailServerCustomerApplicationMapping.objects.filter(
            customer_uuid=customer2,
            application_uuid=application2
        )
        self.assertEqual(different_mappings.count(), 1)

        different_settings = UserEmailSetting.objects.filter(
            customer_uuid=customer2,
            application_uuid=application2,
            is_deleted=False
        )
        self.assertEqual(different_settings.count(), 1)