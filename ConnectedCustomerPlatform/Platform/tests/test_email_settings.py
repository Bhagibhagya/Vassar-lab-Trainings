import os
import uuid
from dotenv import load_dotenv
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.tests.test_data import create_email_settings_test_data
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages

from EmailApp.constant.constants import MicrosoftGraphPermissions
from unittest.mock import patch
from rest_framework.test import APITestCase
load_dotenv()


class BaseTestCase(TestCase):

    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        self.user_email_settings, self.user_email_settings2 = create_email_settings_test_data()

        # Common headers
        self.headers = {
            'customer-uuid': self.user_email_settings.customer_uuid_id,
            'application-uuid': self.user_email_settings.application_uuid_id,
            'user-id': self.user_email_settings.created_by,
        }

####
# =========================== Tests for UserEmailSettingsViewSet ===================================
####
class UserEmailSettingsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.email_id = self.user_email_settings.email_id
        self.encrypted_password = self.user_email_settings.encrypted_password
        self.email_type = self.user_email_settings.email_type

    ###
    # ========= Tests for "add_user_email_settings" API ==========
    ###

    # 1. With all correct values Individual email
    def test_add_user_email_settings_indi_success(self):
        email_id2 = "test_user2@gmail.com"
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': email_id2,
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.ADD_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 2. With all correct values Group Email - New primary Email
    def test_add_user_email_settings_group_new_primary_success(self):
        email_id2 = "test_user6@gmail.com"
        email_details_json = {'primary_email_address': 'new_primary_email@gmail.com'}
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': email_id2,
                'encrypted_password': self.encrypted_password,
                'email_type': self.user_email_settings2.email_type,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            format='json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.ADD_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 3. With all correct values Group Email - Existing primary Email
    def test_add_user_email_settings_group_exist_primary_success(self):
        email_id2 = "test_user6@gmail.com"
        email_details_json = {'primary_email_address': self.email_id}
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': email_id2,
                'email_type': self.user_email_settings2.email_type,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            format='json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.ADD_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 4. With already existing email address
    def test_add_user_email_settings_email_exists(self):
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': self.email_id,
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_EXISTS, response.data.get('result'))

    # 5. Missing required headers
    def test_add_user_email_settings_missing_headers(self):
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': self.email_id,
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'cust_email_provider': 'Gmail'
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.CUSTOMER_ID_NOT_NULL, response.data.get('result'))

    # 6. Missing payload data
    def test_add_user_email_settings_missing_email_id(self):
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': "",
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', str(response.data.get('result')['email_id']))

    # 7. With all correct values Group Email - New primary Email missing password
    def test_add_user_email_settings_group_new_primary_missing_password(self):
        email_id2 = "test_user7@gmail.com"
        email_details_json = {'primary_email_address': 'new_primary_email2@gmail.com'}
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': email_id2,
                'email_type': self.user_email_settings2.email_type,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            format='json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.ADD_EMAIL_FAILED, response.data.get('result'))

    # 8. Invalid Email Provider
    def test_add_user_email_settings_invalid_email_provider(self):
        email_id2 = "test_user2@jsoifd.com"
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': email_id2,
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.INVALID_EMAIL_DOMAIN, response.data.get('result'))

    # 8. Email Provider Mismatch
    def test_add_user_email_settings_email_provider_mismatch(self):
        email_id2 = "test_user2@outlook.com"
        response = self.client.post(
            reverse("Platform:user_email_settings"),
            {
                'email_id': email_id2,
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_PROVIDER_MISMATCH, response.data.get('result'))

    ###
    # ========= Tests for "get_user_email_settings_by_type" API ==========
    ###
    # 1. With all correct values
    def test_get_user_email_settings_by_type_success(self):
        response = self.client.get(
            reverse("Platform:user_email_settings"),
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.data.get('result'):
            self.assertIn('user_email_uuid', response.data.get('result')[0])

    ###
    # ========= Tests for "edit_user_email_settings" API ==========
    ###
    # 1. With all correct values Individual Email
    def test_edit_user_email_settings_indi_success(self):
        new_email_id = "test_user2@gmail.com"
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings.user_email_uuid,
                'email_id': new_email_id,
                'encrypted_password': 'new_password',
                'email_type': self.email_type,
                'is_primary_sender_address': True,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.EDIT_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 2. With all correct values Individual Email
    def test_edit_user_email_settings_indi_password_not_edited_success(self):
        new_email_id = "test_user2@gmail.com"
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings.user_email_uuid,
                'email_id': new_email_id,
                'email_type': self.email_type,
                'is_primary_sender_address': True,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.EDIT_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 3. With all correct values Group Email - Existing Primary Email
    def test_edit_user_email_settings_group_primary_email_exist_success(self):
        new_email_id = "test_user2@gmail.com"
        email_details_json = {'primary_email_address': self.email_id}
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings2.user_email_uuid,
                'email_id': new_email_id,
                'email_type': self.user_email_settings2.email_type,
                'is_primary_sender_address': False,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            format='json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.EDIT_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 4. With all correct values Group Email - New Primary Email
    def test_edit_user_email_settings_group_primary_email_new_success(self):
        new_email_id = "test_user2@gmail.com"
        email_details_json = {'primary_email_address': 'newemail@gmail.com'}
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings2.user_email_uuid,
                'email_id': new_email_id,
                'encrypted_password': self.encrypted_password,
                'email_type': self.user_email_settings2.email_type,
                'is_primary_sender_address': False,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            format='json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.EDIT_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 5. Missing required headers
    def test_edit_user_email_settings_missing_headers(self):
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings.user_email_uuid,
                'email_id': self.email_id,
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'is_primary_sender_address': False,
                'cust_email_provider': 'Gmail'
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.CUSTOMER_ID_NOT_NULL, response.data.get('result'))

    # 6. Missing query param data
    def test_edit_user_email_settings_missing_user_email_uuid(self):
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'email_id': self.email_id,
                'encrypted_password': self.encrypted_password,
                'email_type': self.email_type,
                'is_primary_sender_address': False,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field is required.', str(response.data.get('result')['user_email_uuid']))

    # 7. Missing payload data
    def test_edit_user_email_settings_missing_email_type(self):
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings.user_email_uuid,
                'email_id': self.email_id,
                'encrypted_password': self.encrypted_password,
                'email_type': "",
                'is_primary_sender_address': False,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', str(response.data.get('result')['email_type']))

    # 8. Unique constraint violation
    def test_edit_user_email_settings_unique_constraint_violation(self):
        email_details_json = {'primary_email_address': 'newemail@gmail.com'}
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings2.user_email_uuid,
                'encrypted_password': self.encrypted_password,
                'email_id': self.email_id,
                'email_type': self.user_email_settings2.email_type,
                'is_primary_sender_address': False,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.EMAIL_EXISTS, str(response.data.get('result')))

    # 9. Missing password for new primary email
    def test_edit_user_email_settings_missing_password_for_new_primary_email(self):
        email_details_json = {'primary_email_address': 'newemail@gmail.com'}
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': self.user_email_settings2.user_email_uuid,
                'email_id': self.user_email_settings2.email_id,
                'email_type': self.user_email_settings2.email_type,
                'is_primary_sender_address': False,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.UPDATE_EMAIL_FAILED, str(response.data.get('result')))

    # 10. User email settings does not exist
    def test_edit_user_email_settings_user_email_settings_not_found(self):
        email_details_json = {'primary_email_address': 'newemail@gmail.com'}
        response = self.client.put(
            reverse("Platform:user_email_settings"),
            {
                'user_email_uuid': uuid.uuid4(),
                'email_id': self.user_email_settings2.email_id,
                'email_type': self.user_email_settings2.email_type,
                'is_primary_sender_address': False,
                'email_details_json': email_details_json,
                'cust_email_provider': 'Gmail'
            },
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND, str(response.data.get('result')))

    ###
    # ========= Tests for "delete_user_email_settings" API ==========
    ###
    # 1. With all correct values
    def test_delete_user_email_settings_success(self):
        url = reverse('Platform:user_email_settings_by_id', args=[self.user_email_settings.user_email_uuid])
        response = self.client.delete(
            url,
            headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.DELETE_USER_EMAIL_SETTINGS_SUCCESS, response.data.get('result'))

    # 2. Missing user_email_uuid
    def test_delete_user_email_settings_missing_user_email_uuid(self):
        url = reverse('Platform:user_email_settings_by_id', args=[uuid.uuid4()])
        response = self.client.delete(
            url,
            headers=self.headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND, response.data.get('result'))

    # 3. Missing required headers
    def test_delete_user_email_settings_missing_headers(self):
        user_email_uuid = str(self.user_email_settings.user_email_uuid),
        url = reverse('Platform:user_email_settings_by_id', args=[user_email_uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.CUSTOMER_ID_NOT_NULL, response.data.get('result'))

    # 4.

    ###
    # ========= Tests for "test_connection" API ==========
    ###
    # 1. With all correct values
    def test_test_connection_success(self):
        response = self.client.post(
            reverse("Platform:test_connection_gmail"),
            {
                "server_url": "imap.gmail.com",
                "port": 993,
                "email": "bot.helpdesk.vl@gmail.com",
                "password": os.getenv('TEST_EMAIL_APP_PASSWORD'),
                "is_ssl_enabled": True
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.CONNECTION_SUCCESS, response.data.get('result'))

    # 2. With missing password
    def test_test_connection_missing_password_success(self):
        response = self.client.post(
            reverse("Platform:test_connection_gmail"),
            {
                "server_url": "imap.gmail.com",
                "port": 993,
                "email": "bot.helpdesk.vl@gmail.com",
                "is_ssl_enabled": True,
                "is_encrypted": True,
                "email_uuid": self.user_email_settings.user_email_uuid
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(SuccessMessages.CONNECTION_SUCCESS, response.data.get('result'))

    # 3. Missing required fields
    def test_test_connection_missing_payload(self):
        response = self.client.post(
            reverse("Platform:test_connection_gmail"),
            {
                "server_url": "",
                "port": 993,
                "email": "bot.helpdesk.vl@gmail.com",
                "password": os.getenv('TEST_EMAIL_APP_PASSWORD'),
                "is_ssl_enabled": True
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', str(response.data.get('result')['server_url']))

    # 4. With Invalid email credentials
    def test_test_connection_invalid_credentials(self):
        response = self.client.post(
            reverse("Platform:test_connection_gmail"),
            {
                "server_url": "imap.gmail.com",
                "port": 993,
                "email": "bot.helpdesk.vl@gmail.com",
                "password": os.getenv('TEST_EMAIL_APP_PASSWORD_INCORRECT'),
                "is_ssl_enabled": True
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 5. With missing password and invalid user email settings does not exist
    def test_test_connection_missing_pwd_user_email_not_found(self):
        response = self.client.post(
            reverse("Platform:test_connection_gmail"),
            {
                "server_url": "imap.gmail.com",
                "port": 993,
                "email": "bot.helpdesk.vl@gmail.com",
                "is_ssl_enabled": True,
                "is_encrypted": True,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND, response.data.get('result'))



class TestConnectionOutlookAPITest(APITestCase):
    def setUp(self):
        """Set up test data and mocks"""
        super().setUp()
        self.user_email = "testuser@example.com"
        self.microsoft_client_id = str(uuid.uuid4())
        self.microsoft_tenant_id = str(uuid.uuid4())
        self.microsoft_client_secret = "dummy_client_secret"

        self.payload = {
            "user_email": self.user_email,
            "microsoft_client_id": self.microsoft_client_id,
            "microsoft_tenant_id": self.microsoft_tenant_id,
            "microsoft_client_secret": self.microsoft_client_secret,
        }

        self.url = reverse("test_connection")

    @patch("Platform.services.impl.email_settings_service_impl.call_api")
    @patch("jwt.decode")
    @patch("Platform.services.impl.email_settings_service_impl.get_access_token")
    def test_successful_connection(self, mock_get_access_token, mock_decode, mock_call_api):
        """Test a successful connection with all permissions and valid email"""
        # Mock responses
        mock_get_access_token.return_value = "dummy_access_token"
        mock_decode.return_value = {"roles": [MicrosoftGraphPermissions.MAIL_READ_ALL.value, MicrosoftGraphPermissions.MAIL_SEND.value]}
        mock_call_api.return_value.ok = True
        mock_call_api.return_value.status_code=status.HTTP_200_OK
        response = self.client.post(self.url, data=self.payload, format="json")

        # Assertions
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"], "Connection successful!")
        mock_get_access_token.assert_called_once()
        mock_decode.assert_called_once()
        mock_call_api.assert_called_once()

    @patch("Platform.services.impl.email_settings_service_impl.call_api")
    @patch("jwt.decode")
    @patch("Platform.services.impl.email_settings_service_impl.get_access_token")
    def test_invalid_token_permission_error(self, mock_get_access_token, mock_decode, mock_call_api):
        """Test connection failure due to missing permissions in access token"""
        # Mock responses
        mock_get_access_token.return_value = "dummy_access_token"
        mock_decode.return_value = {"roles": []}  # Missing permissions
        mock_call_api.return_value.ok = True

        response = self.client.post(self.url, data=self.payload, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Missing permissions", response.data["result"])
        mock_get_access_token.assert_called_once()
        mock_decode.assert_called_once()

    @patch("Platform.services.impl.email_settings_service_impl.call_api")
    @patch("jwt.decode")
    @patch("Platform.services.impl.email_settings_service_impl.get_access_token")
    def test_user_email_not_found(self, mock_get_access_token, mock_decode, mock_call_api):
        """Test connection failure due to user email not found"""
        # Mock responses
        mock_get_access_token.return_value = "dummy_access_token"
        mock_decode.return_value = {"roles": [MicrosoftGraphPermissions.MAIL_READ_ALL.value, MicrosoftGraphPermissions.MAIL_SEND.value]}

        # Raise CustomException when the email is not found (404)
        mock_call_api.side_effect = CustomException("Resource not found", status_code=status.HTTP_404_NOT_FOUND)

        response = self.client.post(self.url, data=self.payload, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("does not exist", response.data["result"])

    def test_serializer_validation_error(self):
        """Test connection failure due to invalid payload"""
        # Remove required field to simulate validation error
        invalid_payload = self.payload.copy()
        invalid_payload.pop("user_email")

        response = self.client.post(self.url, data=invalid_payload, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user_email", response.data["result"])

    @patch("Platform.services.impl.email_settings_service_impl.call_api")
    @patch("jwt.decode")
    @patch("Platform.services.impl.email_settings_service_impl.get_access_token")
    def test_invalid_access_token(self, mock_get_access_token, mock_decode, mock_call_api):
        """Test connection failure due to invalid access token"""
        # Mock get_access_token to raise an exception
        mock_get_access_token.side_effect = Exception("Invalid token")

        response = self.client.post(self.url, data=self.payload, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("valid server details", response.data["result"])
        mock_get_access_token.assert_called_once()

    @patch("Platform.services.impl.email_settings_service_impl.call_api")
    @patch("jwt.decode")
    @patch("Platform.services.impl.email_settings_service_impl.get_access_token")
    def test_forbidden_error(self, mock_get_access_token, mock_decode, mock_call_api):
        """Test connection failure due to forbidden error"""
        # Mock responses
        mock_get_access_token.return_value = "dummy_access_token"
        mock_decode.return_value = {"roles": [MicrosoftGraphPermissions.MAIL_READ_ALL.value, MicrosoftGraphPermissions.MAIL_SEND.value]}
        mock_call_api.side_effect = CustomException("Forbidden", status_code=status.HTTP_403_FORBIDDEN)

        response = self.client.post(self.url, data=self.payload, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Please grant API permissions to access user profile.", response.data["result"])

    @patch("Platform.services.impl.email_settings_service_impl.call_api")
    @patch("jwt.decode")
    @patch("Platform.services.impl.email_settings_service_impl.get_access_token")
    def test_unauthorized_error(self, mock_get_access_token, mock_decode, mock_call_api):
        """Test connection failure due to unauthorized error"""
        # Mock responses
        mock_get_access_token.return_value = "dummy_access_token"
        mock_decode.return_value = {"roles": [MicrosoftGraphPermissions.MAIL_READ_ALL.value, MicrosoftGraphPermissions.MAIL_SEND.value]}
        mock_call_api.side_effect = CustomException("Unauthorised", status_code=status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(self.url, data=self.payload, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Unauthorized", response.data["result"])

    @patch("Platform.services.impl.email_settings_service_impl.call_api")
    @patch("jwt.decode")
    @patch("Platform.services.impl.email_settings_service_impl.get_access_token")
    def test_generic_connection_error(self, mock_get_access_token, mock_decode, mock_call_api):
        """Test connection failure due to generic error"""
        # Mock get_access_token to raise a general exception
        mock_get_access_token.return_value = "dummy_access_token"
        mock_call_api.side_effect = Exception("Unauthorised")
        mock_decode.return_value = {"roles": [MicrosoftGraphPermissions.MAIL_READ_ALL.value, MicrosoftGraphPermissions.MAIL_SEND.value]}

        response = self.client.post(self.url, data=self.payload, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Cannot complete test connection", response.data["result"])
        mock_get_access_token.assert_called_once()
