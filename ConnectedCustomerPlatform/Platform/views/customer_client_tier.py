import inspect
import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant import constants
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import CustomerClientSerializer, CustomerClientModelSerializer, CustomerClientTierMappingSerializer
from drf_yasg.utils import swagger_auto_schema
from Platform.utils import get_headers
from drf_yasg import openapi
from Platform.services.impl.customer_client_tier_service_impl import CustomerClientTierServiceImpl

logger = logging.getLogger(__name__)


# ViewSet for Customer apis
class CustomerClientTierViewSet(ViewSet):
    """
    ViewSet for managing CustomerClientTierViewSet, providing methods to add, edit,
    delete, and retrieve configurations.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerClientTierViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.customer_client_tier_service = CustomerClientTierServiceImpl()
            print(f"Inside CustomerClientViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Add customer to tier",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_CUSTOMER_TIER_APPLICATION_MAPPING_SUCCESS
        }
    )
    @action(detail=False, methods=['POST'])
    def add_customer_client_tier_mapping(self, request):
        """
            Adds a customer client tier mapping.
            This method processes a request to add a new customer client tier mapping.
            Parameters:
                - request: The HTTP request containing headers and request data (payload).
            Returns:
                - A custom success response if the mapping is added successfully.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        _, _, user_uuid = get_headers(request.headers)

        # Validate the incoming request data with the serializer
        serializer = CustomerClientTierMappingSerializer(data=request.data)
        print(request.data)
        # json for Extraction Template Json = {}
        if serializer.is_valid():
            data = serializer.validated_data
            logger.info(f"add_customer_client_tier_mapping :: Validated data: {data}")

            # Call the service method to handle adding the tier mapping
            self.customer_client_tier_service.add_customer_client_tier_mapping(user_uuid, data)

            # Log the success of the operation
            logger.info("add_customer_client_tier_mapping :: Successfully added customer client tier mapping.")
            return CustomResponse(SuccessMessages.ADD_CUSTOMER_TIER_APPLICATION_MAPPING_SUCCESS)
        else:
            # Log the validation errors
            logger.error(f"add_customer_client_tier_mapping :: Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Edit extraction template in tier",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.CUSTOMER_CLIENT_TIER_UPDATED_SUCCESS
        }
    )
    @action(detail=False, methods=['PUT'])
    def edit_customer_client_tier_mapping(self, request):
        """
        Edits an existing customer client tier mapping.
        Parameters:
            - request (HttpRequest): Contains headers and data.
        Returns:
            - CustomResponse: Success message if the update is successful.
            - Raises CustomException for validation errors or failure.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        _, _, user_uuid = get_headers(request.headers)

        # Validate the incoming request data using the serializer
        serializer = CustomerClientTierMappingSerializer(data=request.data,is_edit=True)
        if serializer.is_valid():
            data = serializer.validated_data
            logger.info(f"Valid data: {data}")

            self.customer_client_tier_service.edit_customer_client_tier_mapping(user_uuid, data)
            logger.info("Customer client tier mapping updated successfully")

            return CustomResponse(SuccessMessages.CUSTOMER_CLIENT_TIER_UPDATED_SUCCESS)
        else:
            logger.error(f"Validation errors: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Delete Customer-Client_tier--mapping",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='mapping_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Mapping UUID')],
        responses={
            status.HTTP_200_OK: SuccessMessages.CUSTOMER_TIER_APPLICATION_MAPPING_DELETE_SUCCESS
        }
    )
    @action(detail=False, methods=['DELETE'])
    def delete_customer_client_tier_mapping(self, request, mapping_uuid):
        """
        Deletes a customer tier application mapping.
        Parameters:
            - request (HttpRequest): The request object containing headers.
            - mapping_uuid (str): The unique identifier of the mapping to delete.
        Returns:
            CustomResponse: A success message indicating the deletion was successful.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.info(f"Attempting to delete customer tier mapping with UUID: {mapping_uuid}")

        # Call the service to delete the mapping
        self.customer_client_tier_service.delete_customer_client_tier_mapping(mapping_uuid)

        logger.info(f"Successfully deleted customer tier mapping with UUID: {mapping_uuid}")
        return CustomResponse(SuccessMessages.CUSTOMER_TIER_APPLICATION_MAPPING_DELETE_SUCCESS)


    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Get Customer-Clients by tier",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='tier_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Tier UUID')],
        responses={
            status.HTTP_200_OK: CustomerClientModelSerializer
        }
    )
    @action(detail=False, methods=['GET'])
    def get_customers_client_by_tier_mapping(self, request, tier_mapping_uuid):
        """
        Retrieves customers associated with a specific tier mapping.
        Parameters:
            - tier_mapping_uuid (str): The unique identifier of the tier mapping.
        """
        # Log the class name and the current method name for better traceability
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Retrieve the list of customer clients associated with the provided tier mapping UUID
        customer_client_tier_list = self.customer_client_tier_service.get_customers_client_by_tier_mapping(tier_mapping_uuid)

        # Log the successful retrieval of customer clients and the count retrieved
        logger.info(f"Successfully retrieved {len(customer_client_tier_list)} customers for tier mapping UUID: {tier_mapping_uuid}")

        # Return the list of customer clients in a custom response format
        return CustomResponse(customer_client_tier_list)


    @swagger_auto_schema(
        tags=constants.CUSTOMER_CLIENTS_TAG,
        operation_description="Get Customer-Clients for dropdown",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: CustomerClientModelSerializer
        }
    )
    @action(detail=False, methods=['GET'])
    def get_customer_client_dropdown_in_tier(self, request):
        """
        Retrieves customer-clients that are not already mapped to a tier under the given
        application and customer.

        :param request: HTTP request object with necessary headers.
        :return: CustomResponse with customer-client data or error response.
        """

        # Extract application_uuid and customer_uuid from headers
        logger.info("Extracting headers from the request.")
        customer_uuid, application_uuid, _ = get_headers(request.headers)
        logger.debug(f"customer_uuid: {customer_uuid}, application_uuid: {application_uuid}")

        # Fetch customer-client dropdown data
        logger.info("Fetching customer-client dropdown data.")
        customer_clients = self.customer_client_tier_service.get_customer_client_dropdown_in_tier(application_uuid, customer_uuid)

        # Return customer-client data
        return CustomResponse(customer_clients)
