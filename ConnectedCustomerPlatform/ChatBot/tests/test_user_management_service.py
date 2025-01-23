import unittest
from unittest.mock import patch, Mock
from ChatBot.user_management_services import UserManagementServices
from EmailApp.Exceptions.api_exception import InvalidValueProvidedException
from EmailApp.constant.error_messages import ErrorMessages
import requests

class TestUserManagementServices(unittest.TestCase):

    def setUp(self):
        self.service = UserManagementServices()
        self.api_url = "https://api.example.com/test"
        self.headers = {"Authorization": "Bearer token"}
        self.data = {"key": "value"}
        self.query_params = {"param1": "value1"}

    @patch('requests.get')
    def test_make_request_get(self, mock_get):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"statusCode": 200, "data": "test"}
        mock_get.return_value = mock_response

        # Act
        result = self.service.make_request("GET", self.api_url, headers=self.headers, query_params=self.query_params)

        # Assert
        mock_get.assert_called_once_with(f"{self.api_url}?param1=value1", headers=self.headers)
        self.assertEqual(result, {"statusCode": 200, "data": "test"})

    @patch('requests.post')
    def test_make_request_post(self, mock_post):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"statusCode": 201, "data": "created"}
        mock_post.return_value = mock_response

        # Act
        result = self.service.make_request("POST", self.api_url, headers=self.headers, data=self.data)

        # Assert
        mock_post.assert_called_once_with(self.api_url, json=self.data, headers=self.headers)
        self.assertEqual(result, {"statusCode": 201, "data": "created"})

    @patch('requests.put')
    def test_make_request_put(self, mock_put):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"statusCode": 200, "data": "updated"}
        mock_put.return_value = mock_response

        # Act
        result = self.service.make_request("PUT", self.api_url, headers=self.headers, data=self.data)

        # Assert
        mock_put.assert_called_once_with(self.api_url, json=self.data, headers=self.headers)
        self.assertEqual(result, {"statusCode": 200, "data": "updated"})

    def test_make_request_invalid_method(self):
        # Act & Assert
        with self.assertRaises(InvalidValueProvidedException) as context:
            self.service.make_request("DELETE", self.api_url)

        self.assertEqual(str(context.exception), ErrorMessages.INVALID_HTTP_METHOD)

    @patch('requests.get')
    def test_make_request_no_status_code(self, mock_get):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"message": {"info": "test message"}}
        mock_get.return_value = mock_response

        # Act
        result = self.service.make_request("GET", self.api_url, headers=self.headers)

        # Assert
        self.assertEqual(result, {"info": "test message"})

