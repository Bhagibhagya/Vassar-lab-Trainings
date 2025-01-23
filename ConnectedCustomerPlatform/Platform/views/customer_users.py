import inspect
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import ClientUserSerializer, ClientUsersModelSerializer
from Platform.services.impl.customer_user_service_impl import CustomerUserServiceImpl
from Platform.utils import get_headers

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import F

from Platform.utils import get_headers_and_validate

logger = logging.getLogger(__name__)


# ViewSet for Customer users apis
class CustomerUsersViewSet(ViewSet):
    """
        ViewSet for managing CustomerUsers, providing methods to add, edit,
        delete, and retrieve configurations.
        """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerUsersViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.customer_user_service = CustomerUserServiceImpl()
            print(f"Inside CustomerClientViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Api to add the customer-client-user
    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_USERS_TAG,
        operation_description="Add a Customer-Client-User",
        request_body=ClientUserSerializer,
        manual_parameters=[constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_CUSTOMER_USER_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['post'])
    def add_customer_user(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """ 
        This method is used to add a customer client user.
        
        Parameters:
            - customer_uuid : header value
            - user_uuid : header value
            - payload (request.data): request body
        """
        # Extract headers
        logger.debug("Extracting customer_uuid and user_uuid from headers.")
        user_uuid = request.headers.get(constants.USER_ID)

        # Validate request data
        logger.debug("Validating request data with CustomerClientSerializer.")
        serializer = ClientUserSerializer(data=request.data)
        if not serializer.is_valid():
            # Log validation errors and raise an exception
            logger.error(f"Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors)
        logger.info("Request data is valid.")
        # Call service method to add the customer user
        self.customer_user_service.add_customer_user(serializer.validated_data,user_uuid)

        # Return success response
        logger.info("Customer client user added successfully.")
        return CustomResponse(SuccessMessages.ADD_CUSTOMER_USER_SUCCESS)

    # Api to edit the customer-client-user
    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_USERS_TAG,
        operation_description="Edit a Customer-Client-User",
        request_body=ClientUserSerializer,
        manual_parameters=[constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_CUSTOMER_USER_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['put'])
    def edit_customer_user(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            This method is used to edit an existing customer client user.
        
            Parameters:
                - customer_uuid: The unique identifier of the customer (provided in headers).
                - payload (request.data): A dictionary containing the updated customer client user data.
        
            Returns:
                - CustomResponse: A response indicating success or failure.
        """

        # Extract headers
        logger.debug("Extracting customer_uuid and user_uuid from headers.")
        user_uuid = request.headers.get(constants.USER_ID)

        # Validate request data
        logger.debug("Validating request data with CustomerClientSerializer.")
        serializer = ClientUserSerializer(data=request.data,is_edit=True)
        if not serializer.is_valid():
            # Log validation errors and raise an exception
            logger.error(f"Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors)
        logger.info("Request data is valid.")
        # Call the service layer to edit the customer client
        self.customer_user_service.edit_customer_user(serializer.validated_data,user_uuid)

        # Log success message
        logger.info("Successfully updated customer user")
        return CustomResponse(SuccessMessages.UPDATE_CUSTOMER_USER_SUCCESS)


    # Api to delete customer-client-user
    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_USERS_TAG,
        operation_description="Delete Customer-Client-User",
        manual_parameters=[constants.user_id_header,
                           openapi.Parameter(name='client_user_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Customer Client User UUID')],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_CUSTOMER_USER_SUCCESS
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_customer_user(self, request,client_user_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            This Method is used to delete customer client user

            Parameters:
                -user-uuid (required):header
                -client-user-uuid (request.param):request_param
        """
        if client_user_uuid is None:
            raise CustomException(ErrorMessages.INVALID_DATA, status_code=status.HTTP_400_BAD_REQUEST)

        # Retrieve user_uuid from request headers
        user_uuid = request.headers.get(constants.USER_ID)
        logger.info(f"delete_customer :: user_uuid: {user_uuid}, customer_user_uuid: {client_user_uuid}")

        # Call service to delete the customer user and log the action
        self.customer_user_service.delete_customer_user(client_user_uuid, user_uuid)

        logger.info(f"delete_customer_user :: Customer user successfully deleted: {client_user_uuid}")
        return CustomResponse(SuccessMessages.DELETE_CUSTOMER_USER_SUCCESS)

    # Api to get customer-client-users by customer-clients
    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_USERS_TAG,
        operation_description="Get Customer-Clients-Users by customer-client",
        manual_parameters=[constants.user_id_header,
                           openapi.Parameter(name='customer_client_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Customer Client uuid')],
        responses={
            status.HTTP_200_OK: ClientUsersModelSerializer
        }
    )
    @action(detail=False, methods=['get'])
    def get_customer_users(self, request,customer_client_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            This method is to retrieve customer client users information based on the provided customer_client_uuid.
        
            Args:
                request (Request): The HTTP request object containing the headers.
        
            Returns:
                CustomResponse: A response containing the customer client users details.
        """

        customer_uuid, _, _ = get_headers_and_validate(request.headers)

        # Fetching the customer client users under customer client
        result = self.customer_user_service.get_customer_users(customer_client_uuid, customer_uuid)

        logger.info(f"Successfully retrieved customer clients for customer_client_uuid:{customer_client_uuid}")

        # Return the customer user details in a custom response
        return CustomResponse(result)
