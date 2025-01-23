import inspect
import logging
from datetime import datetime

import pytz
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.serializers import ChatConfigurationSerializer, ActiveChatConfigurationSerializer
from Platform.services.impl.chat_configuration_service_impl import ChatConfigurationServiceImpl
from Platform.utils import validate_headers, validate_input, get_headers

logger = logging.getLogger(__name__)
indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class ChatConfigurationBaseViewSet(ViewSet):
    """API View for managing chat configurations"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatConfigurationBaseViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside DimensionViewSet")
            self.chat_configuration_service = ChatConfigurationServiceImpl()
            print(f"Inside DimensionViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True


    @swagger_auto_schema(
        tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
        operation_description="Get All Chat Configuration",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: openapi.Response(
                type=openapi.TYPE_ARRAY,
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=constants.chat_configuration_properties)
                    )
                )
        }
    )
    @action(detail=False, method='get')
    def get_all_chat_configurations(self, request):
        """
            Method to retrieve all chat configurations for a specific application and customer.
            Query Parameters:
                chat_configuration_type : type of chat configuration to filter by.
            Headers:
                Application-Uuid: UUID of the application.
                Customer-Uuid: UUID of the customer.
            Returns:
                CustomResponse: A list of chat configurations.
            """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        start_time = datetime.now()
        logger.info(f"Time profile :: before processing request :: {format_indian_time(start_time)}")

        customer_uuid, application_uuid, _ = get_headers(request.headers)
        logger.debug(f"Received Headers - Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        chat_configuration_type = request.query_params.get('chat_configuration_type')
        if not validate_input(chat_configuration_type):
            raise CustomException(ErrorMessages.CHAT_CONFIGURATION_TYPE_NOT_NULL)
        service_start_time = datetime.now()
        logger.info(f"Time profile :: before calling service :: {format_indian_time(service_start_time)}")

        template_data = self.chat_configuration_service.get_all_chat_configurations(
            application_uuid,
            customer_uuid,
            chat_configuration_type
        )

        service_end_time = datetime.now()
        logger.info(f"Time profile :: after calling service :: {format_indian_time(service_end_time)}")
        logger.info(
            f"Total time taken for chat configuration service call: {(service_end_time - service_start_time).total_seconds() * 1000:.4f} ms")

        end_time = datetime.now()
        logger.info(f"Time profile :: after processing request :: {format_indian_time(end_time)}")
        logger.info(
            f"Total time taken for get_all_chat_configurations method: {(end_time - start_time).total_seconds() * 1000:.4f} ms")

        return CustomResponse(template_data)



    @swagger_auto_schema(
        tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
        operation_description="Delete a specific Chat configuration by UUID.",
        manual_parameters=[constants.chat_configuration_properties.get("chat_configuration_uuid"),constants.customer_uuid_header, constants.application_uuid_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.CHAT_CONFIGURATION_DELETED_SUCCESSFULLY
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_chat_configuration(self, request,chat_configuration_uuid):
        """
            Method to delete a specific Chat configuration by UUID.
            Query Parameters:
                chat_configuration_uuid (required):  UUID of the chat configuration to delete.
            Returns:
                Response: HTTP 204 No Content if deletion is successful,
                          HTTP 400 Bad Request if UUID is invalid or configuration not found.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        customer_uuid, application_uuid, _ = get_headers(request.headers)
        logger.debug(f"Received Headers - Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        self.chat_configuration_service.delete_chat_configuration(chat_configuration_uuid,customer_uuid, application_uuid)
        return CustomResponse(SuccessMessages.CHAT_CONFIGURATION_DELETED_SUCCESSFULLY)


    @swagger_auto_schema(
        tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
        operation_description="Get active Chat configurations for a specific customer and application.",
        manual_parameters=[openapi.Parameter('application_uuid', openapi.IN_QUERY, description="UUID of the application.", type=openapi.TYPE_STRING),
                           openapi.Parameter('customer_uuid', openapi.IN_QUERY, description="UUID of the customer.",type=openapi.TYPE_STRING),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Active chat configurations retrieved successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,properties={
                        'chat_details_json': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additionalProperties=openapi.Schema(type=openapi.TYPE_OBJECT),
                            description="Active chat configurations merged from customer-specific and default templates." )}))
        }
    )
    @action(detail=False, methods=['get'])
    def get_active_chat_configurations(self, request):
        """
        Method to get active Chat configuration.
        Query Parameters:
            application_uuid (required):  UUID of the application.
            customer_uuid (required): UUID of the customer
        Returns:
            Response: Active chat configurations.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        serializer = ActiveChatConfigurationSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(f"Invalid parameters: {serializer.errors}")
            raise CustomException(serializer.errors)
        validated_data = serializer.validated_data
        customer_uuid = str(validated_data['customer_uuid'])
        application_uuid = str(validated_data['application_uuid'])
        logger.debug(f"Received Params - Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        result = self.chat_configuration_service.get_active_chat_configurations(application_uuid,customer_uuid)
        return CustomResponse(result)



    @swagger_auto_schema(
        tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
        operation_description="Update Activation Status.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'chat_configuration_uuid': constants.chat_configuration_properties.get("chat_configuration_uuid"),
                'chat_configuration_type': constants.chat_configuration_properties.get("chat_configuration_type")},
            required=['chat_configuration_uuid','chat_configuration_type']
        ),
        responses={
            status.HTTP_200_OK: SuccessMessages.CHAT_CONFIGURATION_STATUS_UPDATED_SUCCESSFULLY,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.SAVE_CONFIGURATION_BEFORE_PUBLISHING
        }
    )
    def update_activation_status(self, request):
        """
        Method to update the activation status of a specific chat configuration.
        Data from Request:
            - chat_configuration_uuid (required): UUID of the chat configuration to activate.
            - chat_configuration_type (required): Type of the chat configuration.
        Headers:
            - Application-Uuid: UUID of the application.
            - Customer-Uuid: UUID of the customer.
        Returns:
            CustomResponse: Success message if the activation status is updated successfully.
        """
        logger.info("In views.py :: :: ::  ChatConfigurationViewSet :: :: :: update_activation_status ")
        data = request.data
        chat_configuration_uuid = data.get('chat_configuration_uuid')
        customer_uuid, application_uuid, user_id = get_headers(request.headers)
        if not validate_input(chat_configuration_uuid):
            raise CustomException(ErrorMessages.CHAT_CONFIGURATION_UUID_NOT_NULL,
                                  status_code=status.HTTP_400_BAD_REQUEST)
        response =self.chat_configuration_service.update_activation_status(chat_configuration_uuid,
                                                                 application_uuid, customer_uuid, user_id)
        return CustomResponse(response)


    @swagger_auto_schema(
        tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
        operation_description="Get Chat Configuration",
        manual_parameters=[constants.chat_configuration_properties.get("chat_configuration_uuid"),constants.customer_uuid_header, constants.application_uuid_header],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="A chat configuration",
                schema=ChatConfigurationSerializer()
            )
        }
    )
    @action(detail=False, methods=['get'])
    def get_chat_configuration(self, request,chat_configuration_uuid):
        """
        Method to get a specific Chat configuration by UUID.
        Headers:
            chat_configuration-uuid (required): UUID of the chat_configuration,
        """
        logger.info("In views.py :: ChatConfigurationViewSet :: get_chat_configuration")
        start_time = datetime.now()
        logger.info(f"\nTime profile :: get_chat_configuration :: Start time :: {format_indian_time(start_time)}\n")

        customer_uuid, application_uuid, _ = get_headers(request.headers)
        service_start_time = datetime.now()
        logger.info(
            f"\nTime profile :: get_chat_configuration :: Time before calling service :: {format_indian_time(service_start_time)}\n")

        configuration_object = self.chat_configuration_service.get_chat_configuration(chat_configuration_uuid,customer_uuid,application_uuid)
        service_end_time = datetime.now()
        logger.info(
            f"\nTime profile :: get_chat_configuration :: Time after service call :: {format_indian_time(service_end_time)}\n")
        logger.info(
            f"\nTime profile :: get_chat_configuration :: Total time for service call :: {(service_end_time - service_start_time).total_seconds() * 1000:.4f} ms\n")
        end_time = datetime.now()
        logger.info(f"\nTime profile :: get_chat_configuration :: End time :: {format_indian_time(end_time)}\n")
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(
            f"\nTime profile :: get_chat_configuration :: Total time for entire method :: {total_time:.4f} ms\n")

        return CustomResponse(configuration_object)


    @swagger_auto_schema(
        tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
        operation_description="Update chat configuration.",
        request_body=ChatConfigurationSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.CHAT_CONFIGURATION_UPDATED_SUCCESSFULLY
        }
    )
    @action(detail=False, methods=['post'])
    def create_or_update_chat_configuration(self, request):

        logger.info("In views.py :: ChatConfigurationViewSet :: update_chat_configuration ")
        start_time = datetime.now()
        logger.info(
            f"Time profile :: create_or_update_chat_configuration :: Time before calling service:: {format_indian_time(start_time)}\n")
        data = request.data
        customer_uuid, application_uuid, user_id = get_headers(request.headers)
        response = self.chat_configuration_service.create_or_update_chat_configuration(data,application_uuid, customer_uuid, user_id)
        end_time = datetime.now()
        logger.info(
            f"Time profile :: create_or_update_chat_configuration :: Time after service call:: {format_indian_time(end_time)}\n")
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(
            f"\nTime profile :: create_or_update_chat_configuration :: Total time for entire method :: {total_time:.4f} ms\n")

        return CustomResponse(response)
