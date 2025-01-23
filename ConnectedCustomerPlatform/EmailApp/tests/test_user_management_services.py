from django.test import TestCase
from unittest.mock import patch, Mock
from EmailApp.Exceptions.api_exception import InvalidValueProvidedException
from ConnectedCustomerPlatform.exceptions import CustomException
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.user_management_services import UserManagementServices
class UserManagementServicesTestCase(TestCase):

    def setUp(self):
        self.service = UserManagementServices()
        self.headers = {'Authorization': 'Bearer some_token'}
        self.api_url = 'https://example.com/api/resource'
        self.query_params = {'param1': 'value1', 'param2': 'value2'}
        self.data = {'key': 'value'}


    @patch('EmailApp.user_management_services.requests.get')
    def test_get_request_success(self, mock_get):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'response': {'key': 'value'}}
        mock_get.return_value = mock_response

        response = self.service.make_request('GET', self.api_url, self.headers, query_params=self.query_params)
        mock_get.assert_called_once_with(f"{self.api_url}?param1=value1&param2=value2", headers=self.headers)
        self.assertEqual(response, {'key': 'value'})

    @patch('EmailApp.user_management_services.requests.post')
    def test_post_request_success(self, mock_post):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'response': {'key': 'value'}}
        mock_post.return_value = mock_response

        response = self.service.make_request('POST', self.api_url, self.headers, data=self.data)
        mock_post.assert_called_once_with(self.api_url, json=self.data, headers=self.headers)
        self.assertEqual(response, {'key': 'value'})

    def test_invalid_http_method(self):
        with self.assertRaises(InvalidValueProvidedException) as context:
            self.service.make_request('PATCH', self.api_url, self.headers)
        self.assertEqual(str(context.exception.detail), ErrorMessages.INVALID_HTTP_METHOD)

    @patch('EmailApp.user_management_services.requests.get')
    def test_request_failure_with_message(self, mock_get):
        # Mock response object
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {'message': 'Bad Request'}
        mock_get.return_value = mock_response

        # Assert that CustomException is raised with the correct details
        with self.assertRaises(CustomException) as context:
            self.service.make_request('GET', self.api_url, self.headers, query_params=self.query_params)
        self.assertEqual(context.exception.detail, 'Bad Request')
        self.assertEqual(context.exception.status_code, 401)

    @patch('EmailApp.user_management_services.requests.get')
    def test_request_failure_with_status_code_description(self, mock_get):
        # Mock response object
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.json.return_value = {'statusCodeDescription': 'Forbidden'}
        mock_get.return_value = mock_response

        # Assert that CustomException is raised with the correct details
        with self.assertRaises(CustomException) as context:
            self.service.make_request('GET', self.api_url, self.headers, query_params=self.query_params)
        self.assertEqual(context.exception.detail, 'Forbidden')
        self.assertEqual(context.exception.status_code, 403)

    @patch('EmailApp.user_management_services.requests.get')
    def test_request_failure_with_generic_error(self, mock_get):
        # Mock response object
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # Assert that CustomException is raised with the correct details
        with self.assertRaises(CustomException) as context:
            self.service.make_request('GET', self.api_url, self.headers, query_params=self.query_params)
        self.assertEqual(context.exception.detail, ErrorMessages.ERROR_FROM_USERMGMT_API)
        self.assertEqual(context.exception.status_code, 500)

