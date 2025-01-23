import inspect
import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import UserEmailSettingSerializer, TestConnectionSerializer, UserEmailSettingModelSerializer, \
    TestConnectionSerializerOutlook
from Platform.utils import get_headers_and_validate
from Platform.services.impl.email_settings_service_impl import EmailSettingsServiceImpl

logger = logging.getLogger(__name__)


class UserEmailSettingsViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserEmailSettingsViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)

            print("Inside UserEmailSettingsViewSet")
            self.email_settings_service = EmailSettingsServiceImpl()
            print(f"Inside UserEmailSettingsViewSet - Singleton Instance ID: {id(self)}")

            self.initialized = True


    @swagger_auto_schema(
        tags=constants.USER_EMAIL_SETTINGS_TAG,
        operation_description="Add user email settings",
        request_body=UserEmailSettingSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_USER_EMAIL_SETTINGS_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['POST'])
    def add_user_email_settings(self, request):
        """
            Handles the addition of new user email settings.
            :param request: The request object containing user email settings data.
            :return: Response indicating success or failure of the add operation.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Validate email settings data
        serializer = UserEmailSettingSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call service to create user email settings
        self.email_settings_service.add_email_settings(customer_uuid, application_uuid, user_uuid, serializer.validated_data)

        # Send successful response
        return CustomResponse(SuccessMessages.ADD_USER_EMAIL_SETTINGS_SUCCESS)


    @swagger_auto_schema(
        tags=constants.USER_EMAIL_SETTINGS_TAG,
        operation_description="Get User Email Settings",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='email_type', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                                             description='Type of email settings to retrieve')],
        responses={status.HTTP_200_OK: UserEmailSettingModelSerializer()}
    )
    @action(detail=False, methods=['GET'])
    def get_user_email_settings(self, request):
        """
            Retrieve all user email settings returns of customer-application

            :param request: The HTTP request object containing headers and other request data.
            :return: A response containing the filtered user email settings of application
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract information from headers
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)

        # Call service to get user email settings
        response_data = self.email_settings_service.get_email_settings(customer_uuid, application_uuid)

        return CustomResponse(response_data)


    @swagger_auto_schema(
        tags=constants.USER_EMAIL_SETTINGS_TAG,
        operation_description="Edit User Email Settings",
        request_body=UserEmailSettingSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.EDIT_USER_EMAIL_SETTINGS_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA,
            status.HTTP_404_NOT_FOUND: ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND
        }
    )
    @action(detail=False, methods=['PUT'])
    def edit_user_email_settings(self, request):
        """
            Edit existing user email settings based on the provided data.

            :param request: The HTTP request object containing the data to update user email settings.
            :return: A response indicating the success or failure of the update operation.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Validate email settings data
        serializer = UserEmailSettingSerializer(data=request.data, is_edit=True)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call service to update user email settings
        self.email_settings_service.edit_email_settings(customer_uuid, application_uuid, user_uuid, serializer.validated_data)

        return CustomResponse(SuccessMessages.EDIT_USER_EMAIL_SETTINGS_SUCCESS)


    @swagger_auto_schema(
        tags=constants.USER_EMAIL_SETTINGS_TAG,
        operation_description="Delete User Email Settings",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='user_email_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                                             description='UUID of the user email')],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_USER_EMAIL_SETTINGS_SUCCESS,
            status.HTTP_404_NOT_FOUND: ErrorMessages.USER_EMAIL_SETTINGS_NOT_FOUND
        }
    )
    @action(detail=False, methods=['DELETE'])
    def delete_user_email_settings(self, request, user_email_uuid):
        """
            Delete user email settings based on the provided UUID.

            :param request: The HTTP request object containing the request data.
            :param user_email_uuid: The unique identifier of the user email settings to be deleted.
            :return: A response indicating the success or failure of the delete operation.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Call service to delete user email settings
        self.email_settings_service.delete_email_settings(customer_uuid, application_uuid, user_email_uuid, user_uuid)

        return CustomResponse(SuccessMessages.DELETE_USER_EMAIL_SETTINGS_SUCCESS)


    @swagger_auto_schema(
        tags=constants.USER_EMAIL_SETTINGS_TAG,
        operation_description="Test Connection",
        request_body=TestConnectionSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.CONNECTION_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['POST'])
    def test_connection_gmail(self, request):
        """
        This method is used to test the IMAP connection to an email server.

        Parameters:
            - server_url : The URL of the email server.
            - port : The port number of the email server.
            - user_name : The email address used for testing the connection.
            - password : The password for the email address.
            - use_ssl : (Optional) Indicates whether to use SSL/TLS. Default is True.

        Returns:
            - response (Response): A JSON response indicating the success or failure of the connection test.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        email_uuid = request.data.get('email_uuid')
        server_url = request.data.get('server_url')
        port = request.data.get('port')
        email = request.data.get('email')
        password = request.data.get('password')
        use_ssl = request.data.get('is_ssl_enabled', True)
        is_encrypted = request.data.get('is_encrypted')

        # Validate test connection details
        serializer = TestConnectionSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call service to test IMAP connection
        connection = self.email_settings_service.test_connection_gmail(email_uuid, server_url, port, email, password, use_ssl, is_encrypted)

        if connection['success']:
            return CustomResponse(connection['message'])
        else:
            raise CustomException(connection['message'])

    @swagger_auto_schema(
        tags=constants.USER_EMAIL_SETTINGS_TAG,
        operation_description="Test Connection",
        request_body=TestConnectionSerializerOutlook,
        responses={
            status.HTTP_200_OK: SuccessMessages.CONNECTION_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['POST'])
    def test_connection_outlook(self, request):
        """
        This method is used to test the IMAP connection to an email server.

        Parameters:
            - microsoft_client_id : microsoft_client_id of the email server
            - microsoft_tenant_id : microsoft_tenant_id of the email server
            - microsoft_client_secret : microsoft_client_secret of the email server
            - user_email : The email address used for testing the connection.

        Returns:
            - response (Response): A JSON response indicating the success or failure of the connection test.
        """
        logger.info(f"Entering {self.__class__.__name__}.test_connection_outlook")

        user_email = request.data.get('user_email')
        microsoft_client_id = request.data.get('microsoft_client_id')
        microsoft_tenant_id = request.data.get('microsoft_tenant_id')
        microsoft_client_secret = request.data.get('microsoft_client_secret')

        # Validate test connection details
        serializer = TestConnectionSerializerOutlook(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call service to test connection
        message,status_code = self.email_settings_service.test_connection_outlook(user_email,microsoft_client_id,microsoft_tenant_id,microsoft_client_secret)

        return CustomResponse(message,code=status_code)
