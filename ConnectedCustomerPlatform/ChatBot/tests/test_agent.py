import json
import uuid
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase
from urllib.parse import urlencode

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ChatBot.constant.error_messages import ErrorMessages

from ChatBot.tests.test_data import create_agents_test_data

from ChatBot.constant.constants import ApiRequestHeadersConstants, UserConstants


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()


####
# =========================== Tests for AgentViewSetViewSet ===================================
####
class AgentViewSetTestCase(BaseTestCase):
    ###
    # ========= Tests for "get_all_online_agents" API ==========
    ###
    def setUp(self):
        super().setUp()  # Call the base setup
        self.get_all_agents_url = reverse('ChatBot:get_all_online_agents')
        (
            self.application_uuid,
            self.customer_uuid,
            self.user_uuid
        ) = create_agents_test_data()
        self.headers = {
            ApiRequestHeadersConstants.APPLICATION_UUID: self.application_uuid,
            ApiRequestHeadersConstants.CUSTOMER_UUID: self.customer_uuid,
            ApiRequestHeadersConstants.USER_UUID: self.user_uuid
        }
        print(f"test headers:: {self.headers}")

    # 1 with success-full fetching
    @patch('ChatBot.dao.impl.user_details_dao_impl.execute_to_dict')
    def test_get_all_online_agents_success(self, mock_execute):
        mock_execute.return_value = [{"user_id": 1, "user_name": "Test User"}]
        response = self.client.get(self.get_all_agents_url, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.data.get('result'):
            self.assertIn(UserConstants.USER_ID, response.data.get('result')[0])

    # 2 without application_uuid in headers
    def test_get_all_online_agents_missing_application_uuid(self):
        headers_without_application_uuid = {key: value for key, value in self.headers.items() if
                                            key != ApiRequestHeadersConstants.APPLICATION_UUID}
        response = self.client.get(self.get_all_agents_url, headers=headers_without_application_uuid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.APPLICATION_ID_NOT_NULL, response.data['result'])

    # 3 without customer_uuid in headers
    def test_get_all_online_agents_missing_customer_uuid(self):
        headers_without_customer_uuid = {key: value for key, value in self.headers.items() if key != ApiRequestHeadersConstants.CUSTOMER_UUID}
        response = self.client.get(self.get_all_agents_url, headers=headers_without_customer_uuid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.CUSTOMER_ID_NOT_NULL, response.data['result'])

    # 4 without user_uuid in headers
    def test_get_all_online_agents_missing_user_uuid(self):
        headers_without_customer_uuid = {key: value for key, value in self.headers.items() if key != ApiRequestHeadersConstants.USER_UUID}
        response = self.client.get(self.get_all_agents_url, headers=headers_without_customer_uuid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.USER_ID_NOT_NULL, response.data['result'])

    # 5 response is empty list
    @patch('ChatBot.dao.impl.user_details_dao_impl.execute_to_dict')
    def test_get_all_online_agents_empty_response(self, mock_execute):
        mock_execute.return_value = []
        headers_with_wrong_application_and_customer_id = {
            ApiRequestHeadersConstants.APPLICATION_UUID: str(uuid.uuid4()),
            ApiRequestHeadersConstants.CUSTOMER_UUID: str(uuid.uuid4()),
            ApiRequestHeadersConstants.USER_UUID: str(uuid.uuid4())
        }
        response = self.client.get(self.get_all_agents_url, headers=headers_with_wrong_application_and_customer_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('result'), [])  # Ensure result is an empty list

    # 6 invalid uuid value of application
    def test_get_all_online_agents_invalid_application_uuid(self):
        headers_with_wrong_uuid_value_of_application = {
            ApiRequestHeadersConstants.APPLICATION_UUID: "test",
            ApiRequestHeadersConstants.CUSTOMER_UUID: str(uuid.uuid4()),
            ApiRequestHeadersConstants.USER_UUID: str(uuid.uuid4())
        }
        response = self.client.get(self.get_all_agents_url, headers=headers_with_wrong_uuid_value_of_application)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f"application_uuid : {ErrorMessages.NOT_VALID_UUID}", response.data['result'])

    # 7 invalid uuid value of customer
    def test_get_all_online_agents_invalid_customer_uuid(self):
        headers_with_wrong_uuid_value_of_customer = {
            ApiRequestHeadersConstants.APPLICATION_UUID: str(uuid.uuid4()),
            ApiRequestHeadersConstants.CUSTOMER_UUID: "test",
            ApiRequestHeadersConstants.USER_UUID: str(uuid.uuid4())
        }
        response = self.client.get(self.get_all_agents_url, headers=headers_with_wrong_uuid_value_of_customer)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f"customer_uuid : {ErrorMessages.NOT_VALID_UUID}", response.data['result'])

    # 8 invalid uuid value of customer
    def test_get_all_online_agents_invalid_user_uuid(self):
        headers_with_wrong_uuid_value_of_user = {
            ApiRequestHeadersConstants.APPLICATION_UUID: str(uuid.uuid4()),
            ApiRequestHeadersConstants.CUSTOMER_UUID: str(uuid.uuid4()),
            ApiRequestHeadersConstants.USER_UUID: "test"
        }
        response = self.client.get(self.get_all_agents_url, headers=headers_with_wrong_uuid_value_of_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f"user_uuid : {ErrorMessages.NOT_VALID_UUID}", response.data['result'])
