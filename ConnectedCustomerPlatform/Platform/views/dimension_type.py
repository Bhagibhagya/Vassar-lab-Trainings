import logging
import inspect
import threading
from datetime import datetime
import pytz

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant.error_messages import ErrorMessages
from Platform.constant import constants
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import DimensionTypeSerializer, DimensionTypeCAMModelSerializer
from Platform.utils import get_headers_and_validate
from Platform.services.impl.dimension_type_service_impl import DimensionTypeServiceImpl

logger = logging.getLogger(__name__)

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

# ViewSet for Dimension Type apis
class DimensionTypeViewSet(ViewSet):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DimensionTypeViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside DimensionTypeViewSet")
            self.dimension_type_service = DimensionTypeServiceImpl()
            print(f"Inside DimensionTypeViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Api to add the dimension type for application of a customer
    @swagger_auto_schema(
        tags=constants.DIMENSION_TYPES_TAG,
        operation_description="Add a dimension type",
        request_body=DimensionTypeSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_DIMENSION_TYPE_SUCCESS,
            status.HTTP_400_BAD_REQUEST:ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['post'])
    def add_dimension_type(self, request):
        """
        Add a new dimension type for a customer and application.

        Parameters:
            - customer_uuid (required, str): Header parameter, unique identifier for the customer.
            - application_uuid (required, str): Header parameter, unique identifier for the application.
            - user_uuid (required, str): Header parameter, unique identifier for the user.
            - payload (dict): Body of the request containing dimension type data.

        Returns:
            CustomResponse: Success message indicating that the dimension type has been added.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Extract headers for customer, application, and user
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Serialize and validate the incoming data
        serializer = DimensionTypeSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call the service to add the dimension type, passing necessary parameters
        self.dimension_type_service.add_dimension_type(
            customer_uuid, application_uuid, user_uuid, serializer.validated_data
        )

        # Return success response
        logger.info(f"Dimension type added successfully for customer {customer_uuid} and application {application_uuid}")
        return CustomResponse(SuccessMessages.ADD_DIMENSION_TYPE_SUCCESS)

    # Api to edit the dimension type for application of a customer
    @swagger_auto_schema(
        tags=constants.DIMENSION_TYPES_TAG,
        operation_description="Edit a dimension type",
        request_body=DimensionTypeSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
            responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_DIMENSION_TYPE_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['put'])
    def edit_dimension_type(self, request):
        """
        This method is used to edit a dimension type.

        Parameters:
            - customer_uuid (required, str): Header parameter, unique identifier for the customer.
            - application_uuid (required, str): Header parameter, unique identifier for the application.
            - user_uuid (required, str): Header parameter, unique identifier for the user.
            - payload (request.data): request body

        Returns:
            CustomResponse: Success message indicating that the dimension type has been updated.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Extract headers for customer, application, and user
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Serialize and validate the incoming data
        serializer = DimensionTypeSerializer(data=request.data, is_edit=True)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call the service to edit the dimension type, passing necessary parameters
        self.dimension_type_service.edit_dimension_type(customer_uuid, application_uuid, user_uuid, serializer.validated_data)

        # Return success response
        logger.info(f"Dimension type updated successfully for customer {customer_uuid} and application {application_uuid}")
        return CustomResponse(SuccessMessages.UPDATE_DIMENSION_TYPE_SUCCESS)

    # Api to get all dimension_types
    @swagger_auto_schema(
        tags=constants.DIMENSION_TYPES_TAG,
        operation_description="Get dimension types",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: DimensionTypeCAMModelSerializer()
        }
    )
    @action(detail=False, methods=['get'])
    def get_dimension_types(self, request):
        """
        This method retrieves all dimension types.

        Parameters:
            - customer_uuid (required, str): Header parameter, unique identifier for the customer.
            - application_uuid (required, str): Header parameter, unique identifier for the application.
            - user_uuid (required, str): Header parameter, unique identifier for the user.

        Returns:
            A list of dimension types associated with the given customer and application
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before get_dimension_types :: {format_indian_time(start_time)}\n")

        # Extract customer_uuid and application_uuid from the request headers.
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)
        logger.debug(f"Received Headers - Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")

        # Call the service method to get dimension types based on the provided customer and application UUIDs.
        get_dimension_types_service_st = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before Calling Get dimension type service :: {format_indian_time(get_dimension_types_service_st)}\n")
        response_data = self.dimension_type_service.get_dimension_types(customer_uuid, application_uuid)
        get_dimension_types_service_et = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time after Calling Get dimension type service:: {format_indian_time(get_dimension_types_service_et)}\n")
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: Total time taken Calling Get dimension type service :: {(get_dimension_types_service_et - get_dimension_types_service_st).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution :: Thread ID: {threading.get_ident()} :: Total time taken for Get DimensionTypes:: {total_time:.4f} ms")

        # Return a custom response containing the retrieved dimension types.
        logger.info(f"Dimension types retrieved successfully for customer {customer_uuid} and application {application_uuid}")
        return CustomResponse(response_data)

    # Api to get dimension_type by ID
    @swagger_auto_schema(
        tags=constants.DIMENSION_TYPES_TAG,
        operation_description="Get Dimension Type by ID",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='dimension_type_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Dimension Type UUID')],
        responses={status.HTTP_200_OK: DimensionTypeCAMModelSerializer()}
    )
    @action(detail=False, methods=['get'])
    def get_dimension_type_by_id(self, request, mapping_uuid):
        """
        This method retrieves all dimension types.

        Parameters:
            - customer_uuid (required, str): Header parameter, unique identifier for the customer.
            - application_uuid (required, str): Header parameter, unique identifier for the application.
            - user_uuid (required, str): Header parameter, unique identifier for the user.
            - mapping_uuid (required): The UUID of the dimension type mapping to retrieve
        Returns:
            A list of dimension types associated with the given customer and application
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Extract customer_uuid and application_uuid from the request headers.
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)
        logger.debug(f"Received Headers - Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")

        # Call the service method to get dimension type based on the provided customer, application and mapping UUIDs.
        response_data = self.dimension_type_service.get_dimension_type_by_id(customer_uuid, application_uuid, mapping_uuid)

        # Return a custom response containing the retrieved dimension type.
        logger.info(f"Dimension type retrieved successfully for customer {customer_uuid} and application {application_uuid}")
        return CustomResponse(response_data)


    @swagger_auto_schema(
        tags=constants.DIMENSION_TYPES_TAG,
        operation_description='Soft deletes a dimension type.',
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header,
                           openapi.Parameter('dimension_type_uuid', openapi.IN_QUERY, description='Dimension type UUID',
                                             type=openapi.TYPE_STRING, required=True)],
        responses={
            status.HTTP_200_OK: openapi.Response(description=SuccessMessages.DIMENSION_TYPE_DELETE_SUCCESS),
            status.HTTP_400_BAD_REQUEST: openapi.Response(description=ErrorMessages.DIMENSION_TYPE_UUID_NOT_NULL),
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_dimension_type(self, request, mapping_uuid):
        """
        This endpoint deletes a dimension type mapping by its UUID.

        Args:
            request (HttpRequest): The incoming request containing headers for customer and application UUIDs.
            mapping_uuid (str): The UUID of the dimension type mapping to be deleted.

        Returns:
            CustomResponse: A success message indicating that the dimension type has been deleted.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Extract customer_uuid and application_uuid from the request headers.
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)
        logger.debug(f"Received Headers - Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")

        # Call the service method to delete the dimension type mapping.
        self.dimension_type_service.delete_dimension_type_mapping(customer_uuid, application_uuid, mapping_uuid)

        # Return a success response.
        logger.info(f"Dimension type deleted successfully for customer {customer_uuid} and application {application_uuid}")
        return CustomResponse(SuccessMessages.DIMENSION_TYPE_DELETE_SUCCESS)
