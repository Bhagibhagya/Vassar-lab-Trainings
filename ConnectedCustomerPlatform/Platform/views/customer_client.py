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
from Platform.serializers import CustomerClientSerializer, CustomerClientModelSerializer, CustomerClientTierMappingSerializer
from Platform.services.impl.customer_client_service_impl import CustomerClientServiceImpl
from drf_yasg.utils import swagger_auto_schema
from Platform.utils import get_headers
from drf_yasg import openapi

logger = logging.getLogger(__name__)


# ViewSet for Customer apis
class CustomerClientViewSet(ViewSet):
    """
    ViewSet for managing CustomerClientViewSet, providing methods to add, edit,
    delete, and retrieve configurations.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerClientViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.customer_client_service = CustomerClientServiceImpl()
            print(f"Inside CustomerClientViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Add a Customer-Client",
        request_body=CustomerClientSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_CUSTOMER_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['POST'])
    def add_customer_client(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """ 
        This method is used to add a customer client.
        
        Parameters:
            - customer_uuid (required): header value
            - user_uuid (required): header value
            - payload (request.data): request body
        """

        # Extract headers
        logger.debug("Extracting customer_uuid and user_id from headers.")
        customer_uuid, _, user_uuid = get_headers(request.headers)

        # Validate request data
        logger.debug("Validating request data with CustomerClientSerializer.")
        serializer = CustomerClientSerializer(data=request.data)
        if serializer.is_valid():
            logger.info("Request data is valid.")
            data = serializer.validated_data

            # Call service method to add the customer client
            logger.info(f"Adding customer client for customer_uuid: {customer_uuid} by user_id: {user_uuid}")
            self.customer_client_service.add_customer_client(customer_uuid, user_uuid, data)

            # Return success response
            logger.info("Customer client added successfully.")
            return CustomResponse(SuccessMessages.ADD_CUSTOMER_SUCCESS)
        else:
            # Log validation errors and raise an exception
            logger.error(f"Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Edit a Customer-Client",
        request_body=CustomerClientSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_CUSTOMER_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['PUT'])
    def edit_customer_client(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            This method is used to edit an existing customer client.
        
            Parameters:
                - customer_uuid (required): The unique identifier of the customer (provided in headers).
                - payload (request.data): A dictionary containing the updated customer client data.
        
            Returns:
                - CustomResponse: A response indicating success or failure.
        """
        # Extract the customer_uuid and user_id from request headers
        customer_uuid, _, user_id = get_headers(request.headers)


        # Initialize serializer with request data
        serializer = CustomerClientSerializer(data=request.data,is_edit = True)

        # Validate the serializer data
        if serializer.is_valid():
            data = serializer.validated_data

            logger.info(f"Editing customer: {customer_uuid} by user: {user_id}")

            # Call the service layer to edit the customer client
            self.customer_client_service.edit_customer_client(customer_uuid, user_id, data)

            # Log success message
            logger.info(f"Successfully updated customer: {customer_uuid}")
            return CustomResponse(SuccessMessages.UPDATE_CUSTOMER_SUCCESS)
        else:
            # Log the validation errors
            logger.error(f"Validation errors: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Delete Customer-Client",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='customer_client_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Customer Client UUID')],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_CUSTOMER_SUCCESS
        }
    )
    @action(detail=False, methods=['DELETE'])
    def delete_customer_client(self, request, customer_client_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        """ 
        This method is used to delete a customer client.
    
        Parameters:
            - user_id (required): header containing the user identifier.
            - customer_client_uuid (required): path variable containing the customer client UUID.
        """
        # Retrieve user_id from request headers
        _, _, user_id = get_headers(request.headers)
        logger.info(f"delete_customer :: user_id: {user_id}, customer_client_uuid: {customer_client_uuid}")

        # Call service to delete the customer client and log the action
        updated_rows = self.customer_client_service.delete_customer_client(customer_client_uuid, user_id)

        # Check if any rows were updated (i.e., customer client deleted), otherwise raise exception
        if updated_rows == 0:
            logger.error(f"delete_customer :: Customer client not found: {customer_client_uuid}")
            raise CustomException(ErrorMessages.CUSTOMER_NOT_FOUND)

        logger.info(f"delete_customer :: Customer client successfully deleted: {customer_client_uuid}")
        return CustomResponse(SuccessMessages.DELETE_CUSTOMER_SUCCESS)


    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Get Customer-Clients",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: CustomerClientModelSerializer
        }
    )
    @action(detail=False, methods=['GET'])
    def get_customer_client(self, request):
        """
        API endpoint to retrieve customer client information based on the provided customer_uuid.

        Args:
            request (Request): The HTTP request object containing the headers.

        Returns:
            CustomResponse: A response containing the customer client details.
        """
        # Extract headers (customer_uuid) from the request
        customer_uuid, _, _ = get_headers(request.headers)

        # Log the beginning of the customer client fetching process
        logger.info("Fetching customer client details for customer_uuid: %s", customer_uuid)

        result = self.customer_client_service.get_customer_client(customer_uuid)

        logger.info(f"Successfully retrieved customer clients for customer_uuid:{customer_uuid}")

        # Return the customer client details in a custom response
        return CustomResponse(result)

