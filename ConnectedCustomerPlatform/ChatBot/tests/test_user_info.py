import json
import unittest
from unittest.mock import patch, Mock
from ChatBot.user_management_services import UserManagementServices
from ChatBot.views.user_info import UserInfoViewSet
from ChatBot.constant.constants import Constants

from ChatBot.constant.constants import AgentDashboardConstants
from django.conf import settings

class TestUserInfoViewSet(unittest.TestCase):

    def setUp(self):
        self.user_info_viewset = UserInfoViewSet()
        self.role_id = 123
        self.mock_response_data = [
            {'userId': 1, 'firstName': 'John', 'lastName': 'Doe'},
            {'userId': 2, 'firstName': 'Jane', 'lastName': 'Smith'}
        ]
        self.expected_users = [
            {Constants.USER_ID: 1, Constants.NAME: 'John Doe'},
            {Constants.USER_ID: 2, Constants.NAME: 'Jane Smith'}
        ]
        self.user_id = "user_id"
        self.valid_status = "Online"
        self.invalid_user_id = "invalid-user-id"
    ####
    # =========================== Tests for UserInfoViewSet ===================================
    ####

    # 1. with valid response from usermgmt API for getting the CSR Details
    @patch.object(UserManagementServices, 'make_request')
    def test_get_online_users_success(self, mock_make_request):
        mock_make_request.return_value = {'response': self.mock_response_data}

        users = self.user_info_viewset.get_online_users(self.role_id)

        mock_make_request.assert_called_once_with(
            'GET',
            f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{self.role_id}"
        )
        self.assertEqual(users, self.expected_users)

    # 1. with empty response from usermgmt API for getting the CSR Details
    @patch.object(UserManagementServices, 'make_request')
    def test_get_online_users_empty_response(self, mock_make_request):
        mock_make_request.return_value = {'response': []}

        users = self.user_info_viewset.get_online_users(self.role_id)

        mock_make_request.assert_called_once_with(
            'GET',
            f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{self.role_id}"
        )
        self.assertEqual(users, [])


    # 3. Invalid response response from usermgmt API for getting the CSR Details
    @patch.object(UserManagementServices, 'make_request')
    def test_get_online_users_no_response_key(self, mock_make_request):
        mock_make_request.return_value = {}

        users = self.user_info_viewset.get_online_users(self.role_id)

        mock_make_request.assert_called_once_with(
            'GET',
            f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{self.role_id}"
        )
        self.assertEqual(users, [])


    # 4.not provided valid Role_id
    @patch.object(UserManagementServices, 'make_request')
    def test_get_online_users_without_role_id(self, mock_make_request):
        # Simulate calling the method without providing role_id
        mock_make_request.return_value = {}

        users = self.user_info_viewset.get_online_users(None)

        mock_make_request.assert_not_called()

        self.assertEqual(users,AgentDashboardConstants.ROLE_ID_NOT_GIVEN)



    # 1. Test with valid user_id and status, expecting successful update
    @patch.object(UserManagementServices, 'make_request')
    def test_update_user_success(self, mock_make_request):
        # Arrange
        mock_response = {
            "result": True,
            "statusCode": 200,
            "statusCodeDescription": "OK",
            "message": "status updated successfully",
            "response": None
        }
        mock_make_request.return_value = mock_response

        # Act
        response = self.user_info_viewset.update_user(self.user_id, self.valid_status)

        # Assert
        mock_make_request.assert_called_once_with(
            'GET',
            f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{self.user_id}/{self.valid_status}"
        )
        self.assertEqual(response, mock_response)

    # 2. Test with invalid user_id, expecting failure with 500 error
    @patch.object(UserManagementServices, 'make_request')
    def test_update_user_invalid_user_id(self, mock_make_request):
        # Arrange
        mock_response = {
            "result": False,
            "statusCode": 500,
            "statusCodeDescription": "Internal Server Error",
            "message": f"User not found for userId: {self.invalid_user_id}",
            "response": None
        }
        mock_make_request.return_value = mock_response

        # Act
        response = self.user_info_viewset.update_user(self.invalid_user_id, self.valid_status)

        # Assert
        mock_make_request.assert_called_once_with(
            'GET',
            f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{self.invalid_user_id}/{self.valid_status}"
        )
        self.assertEqual(response, mock_response)


    # 3. Test with expecting exception
    @patch.object(UserManagementServices, 'make_request')
    @patch('ChatBot.views.user_info.logger')
    def test_update_user_exception(self, mock_logger, mock_make_request):
        # Mocking an exception
        mock_make_request.side_effect = Exception("API request failed")

        # Call the method
        response = self.user_info_viewset.update_user(self.user_id, self.valid_status)

        # Assertions
        mock_make_request.assert_called_once_with(
            'GET',
            f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{self.user_id}/{self.valid_status}"
        )
        mock_logger.debug.assert_called_once_with("Exception occurred: API request failed")
        self.assertIsNone(response)  # The method should return None when an exception occurs
