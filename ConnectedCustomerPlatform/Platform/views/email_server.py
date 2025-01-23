import logging
import inspect
from datetime import datetime
import pytz

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import EmailServerSerializer, EmailServerModelSerializer, EmailServerOutlookSerializer
from Platform.services.impl.email_server_service_impl import EmailServerServiceImpl
from Platform.utils import get_headers_and_validate

logger = logging.getLogger(__name__)

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class EmailServerSettingsViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmailServerSettingsViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)

            print("Inside EmailServerSettingsViewSet")
            self.email_server_service = EmailServerServiceImpl()
            print(f"Inside EmailServerSettingsViewSet - Singleton Instance ID: {id(self)}")

            self.initialized = True


    @swagger_auto_schema(
        tags=constants.EMAIL_SETTINGS_TAG,
        operation_description="Add an email server",
        request_body=EmailServerSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_EMAIL_SERVER_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        },
    )
    @action(detail=False, methods=['POST'])
    def add_email_server(self, request):
        """
            Adds a new email server for the specified customer and application.

            :param request: HTTP request containing server details.
            :return: Response indicating success or failure of the operation.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Email Server :: time before add_email_server :: {format_indian_time(start_time)}\n")

        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        email_server_serializer_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Email Server :: time before EmailServerSerializer :: {format_indian_time(email_server_serializer_start_time)}\n")
        # Serialize the request payload
        serializer = EmailServerSerializer(data=list(request.data.values()), many=True)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)
        email_server_serializer_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Email Server :: time after EmailServerSerializer :: {format_indian_time(email_server_serializer_end_time)}\n")
        logger.info(f"\nTime profile :: Add Email Server :: Total time taken EmailServerSerializer :: {((email_server_serializer_end_time - email_server_serializer_start_time).total_seconds() * 1000):.4f}\n")

        # Call service to add email servers
        email_server_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Email Server :: time before Email Server Service :: {format_indian_time(email_server_service_start_time)}\n")
        self.email_server_service.add_email_server(customer_uuid, application_uuid, user_uuid, serializer.validated_data)
        email_server_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Email Server :: time after Email Server Service :: {format_indian_time(email_server_service_end_time)}\n")
        logger.info(f"\nTime profile :: Add Email Server :: Total time taken Email Server Service :: {(email_server_service_end_time - email_server_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Ad Email Server API execution: {total_time:.4f} ms")

        # Send successful response
        return CustomResponse(SuccessMessages.ADD_EMAIL_SERVER_SUCCESS)


    @swagger_auto_schema(
        tags=constants.EMAIL_SETTINGS_TAG,
        operation_description="Fetch email servers by customer",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        responses={status.HTTP_200_OK: EmailServerModelSerializer()}
    )
    @action(detail=False, methods=['GET'])
    def get_email_server(self, request):
        """
            Retrieves email servers associated with the specified customer-application.

            :param request: HTTP request to fetch email servers.
            :return: List of email servers for the customer-application.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time before get_email_server :: {format_indian_time(start_time)}\n")

        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)

        # Call service to fetch email servers
        get_email_server_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time before calling get service :: {format_indian_time(get_email_server_service_start_time)}\n")
        response_data = self.email_server_service.get_email_server(customer_uuid, application_uuid)
        get_email_server_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Email Server :: time after calling get service :: {format_indian_time(get_email_server_service_end_time)}\n")
        logger.info(f"\nTime profile :: Get Email Server :: Total time taken  calling get service :: {(get_email_server_service_end_time - get_email_server_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Email Server API execution: {total_time:.4f} ms")
        # Send response data - additional servers and customer configured
        return CustomResponse(response_data)


    @swagger_auto_schema(
        tags=constants.EMAIL_SETTINGS_TAG,
        operation_description="Update an email server",
        request_body=EmailServerSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_EMAIL_SERVER_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        },
    )
    @action(detail=False, methods=['PUT'])
    def edit_email_server(self, request):
        """
            Updates the details of an existing email server.

            :param request: HTTP request containing updated email server data.
            :return: Response indicating success or failure of the operation.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Serialize the request payload
        serializer = EmailServerSerializer(data=list(request.data.values()), many=True, is_edit=True)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call service to edit email servers
        self.email_server_service.edit_email_server(customer_uuid, application_uuid, user_uuid, serializer.validated_data)

        # Send successful response
        return CustomResponse(SuccessMessages.UPDATE_EMAIL_SERVER_SUCCESS)

    @swagger_auto_schema(
        tags=constants.EMAIL_SETTINGS_TAG,
        operation_description="Fetch outlook servers by customer",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        responses={status.HTTP_200_OK: EmailServerModelSerializer()}
    )
    @action(detail=False, methods=['GET'])
    def get_outlook_server(self, request):
        """
            Retrieves email servers associated with the specified customer-application.

            :param request: HTTP request to fetch email servers.
            :return: List of email servers for the customer-application.
        """
        logger.info(f"Entering {self.__class__.__name__} :: get_outlook_server")

        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)

        # Call service to fetch email servers
        response_data = self.email_server_service.get_outlook_server(customer_uuid, application_uuid)
        return CustomResponse(response_data,code=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=constants.EMAIL_SETTINGS_TAG,
        operation_description="Add/edit an outlook server",
        request_body=EmailServerOutlookSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_EMAIL_SERVER_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        },
    )
    @action(detail=False, methods=['POST'])
    def save_outlook_server(self, request):
        """
        Handles adding or updating an Outlook email server.

        :param request: HTTP request containing server details.
        :return: Response indicating success or failure of the operation.
        """
        # Extract customer, application, and user info from request headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Pass request data to serializer
        serializer = EmailServerOutlookSerializer(data=request.data)

        # Validate the data
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Check if this is an update or add based on the presence of mapping_uuid and email_server_uuid
        update = 'mapping_uuid' in request.data and request.data.get('mapping_uuid')

        # Call the service to save the email server (add or update)
        self.email_server_service.save_outlook_server(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            user_uuid=user_uuid,
            email_server_data=serializer.validated_data,
            update=update
        )

        success_message = SuccessMessages.UPDATE_EMAIL_SERVER_SUCCESS if update else SuccessMessages.ADD_EMAIL_SERVER_SUCCESS
        return CustomResponse(success_message,code=status.HTTP_200_OK)


    @swagger_auto_schema(
        tags=constants.EMAIL_SETTINGS_TAG,
        operation_description="delete an email server",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_EMAIL_SERVER_SUCCESSFUL,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.DELETE_EMAIL_SERVER_FAILED
        },
    )
    @action(detail=False, methods=['DELETE'])
    def delete_email_server(self,request):
        """
        Handles deletion of email server also delete user_email_settings.

        :param request: HTTP request containing server details.
        :return: Response indicating success or failure of the operation.
        """
        # Extract customer, application, and user info from request headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)
        self.email_server_service.delete_email_server(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            user_uuid=user_uuid)

        return CustomResponse(SuccessMessages.DELETE_EMAIL_SERVER_SUCCESSFUL,code=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=constants.EMAIL_SETTINGS_TAG,
        operation_description="get server provider name",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_EMAIL_SERVER_SUCCESSFUL,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.DELETE_EMAIL_SERVER_FAILED
        },
    )
    @action(detail=False,method=['GET'])
    def get_server_provider_name(self,request):
        """
        Retrieves provider name of server
        :param request: HTTP request containing server details.
        :return: Response with provider name.
        """
        # Extract customer, application, and user info from request headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)
        provider_name=self.email_server_service.get_server_provider_name(customer_uuid,application_uuid)
        return CustomResponse(provider_name,code=status.HTTP_200_OK)