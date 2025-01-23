import logging

from drf_yasg.utils import swagger_auto_schema
from nltk.sem.hole import Constants
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from Platform.services.impl.llm_configuration_service_impl import LLMConfigurationServiceImpl
from Platform.serializers import LLMConfigurationSerializer,LLMConfigurationModelSerializer, VerifyLLMConfigurationSerializer
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform .utils import validate_input
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant import constants
from drf_yasg import openapi
logger = logging.getLogger(__name__)


class LLMConfigurationViewSet(ViewSet):
    """
    ViewSet for managing LLM configurations.

    This ViewSet provides methods to add, edit, delete, and retrieve LLM configurations
    for customers. It ensures that only a single instance is created using the Singleton pattern.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the LLMConfigurationViewSet is created.

        Args:
            cls: The class reference.
            *args: Positional arguments for initialization.
            **kwargs: Keyword arguments for initialization.

        Returns:
            LLMConfigurationViewSet: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(LLMConfigurationViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the LLMConfigurationViewSet.

        This method is called only once due to the singleton pattern. It initializes the
        LLMConfigurationService for handling business logic related to LLM configurations.

        Args:
            **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.__llm_config_service = LLMConfigurationServiceImpl()  # Instantiate the service to handle business logic
            logger.info(f"Inside LLMConfigurationViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    @swagger_auto_schema(
        tags=constants.LLM_CONFIGURATION_TAG,
        operation_description="Add LLM Configuration",
        request_body=LLMConfigurationSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_LLM_CONFIGURATION_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['post'])
    def add_llm_configuration(self, request):
        logger.info("In llm_configuration.py :: :: ::  LLMConfigurationViewSet :: :: :: add_llm_configuration ")
        """
        Handle adding a new LLM configuration.

        :param request: DRF request object containing the data to add a configuration.
             Parameters:
                -customer_uuid (required):header
                -user_uuid (required):header
                -payload (request.data):request_body
        :return: Response object with success or error messages.
        """
        # Extract customer and user UUID from request headers
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)
        user_uuid = request.headers.get(constants.USER_ID)

        logger.info(f"Attempting to add LLM configuration for customer {customer_uuid} by user {user_uuid}")

        #  Validate user UUID
        if not validate_input(user_uuid):
            raise CustomException(ErrorMessages.USER_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        # Validate incoming request data using serializer
        serializer = LLMConfigurationSerializer(data=request.data,status="Add")
        if serializer.is_valid():
            llm_configuration_uuid = self.__llm_config_service.add_llm_configuration(customer_uuid, user_uuid, serializer.validated_data)
            logger.info(f"Successfully added LLM configuration for customer {customer_uuid}")
            result_message = {"message": SuccessMessages.ADD_LLM_CONFIGURATION_SUCCESS}
            result_message['llm_configuration_uuid'] = llm_configuration_uuid
            return CustomResponse(result = result_message)
        else:
            logger.error(f"Invalid data for LLM configuration: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=constants.LLM_CONFIGURATION_TAG,
        operation_description="Edit LLM Configuration",
        request_body=LLMConfigurationSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_LLM_CONFIGURATION_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['put'])
    def edit_llm_configuration(self, request):
        logger.info("In llm_configuration.py :: :: :: LLMConfigurationViewSet :: :: :: edit_llm_configuration ")
        """
        Handle editing an existing LLM configuration.

        :param request: DRF request object containing the data to edit a configuration.
             Parameters:
                -customer_uuid (required):header
                -user_uuid(required):header
                -payload (request.data):request_body
        :return: Response object with success or error messages.
        """
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)
        user_uuid = request.headers.get(constants.USER_ID)

        logger.info(f"Attempting to edit LLM configuration for customer {customer_uuid} by user {user_uuid}")

        #  Validate user UUID
        if not validate_input(user_uuid):
            raise CustomException(ErrorMessages.USER_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        # Validate incoming request data using serializer
        serializer = LLMConfigurationSerializer(data=request.data,status="Edit")
        if serializer.is_valid():
            # Edit LLM configuration using the service layer
            self.__llm_config_service.edit_llm_configuration(customer_uuid, user_uuid, serializer.validated_data)
            logger.info(f"Successfully edited LLM configuration for customer {customer_uuid}")
            return CustomResponse(SuccessMessages.UPDATE_LLM_CONFIGURATION_SUCCESS)
        else:
            logger.error(f"Invalid data for LLM configuration: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=constants.LLM_CONFIGURATION_TAG,
        operation_description="Delete LLM Configuration",
        manual_parameters=[constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_LLM_CONFIGURATION_SUCCESS,
            status.HTTP_404_NOT_FOUND: ErrorMessages.LLM_CONFIGURATION_NOT_FOUND
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_llm_configuration(self, request,llm_configuration_uuid):
        logger.info("In llm_configuration.py :: :: :: LLMConfigurationViewSet :: :: :: delete_llm_configuration ")
        """
        Handle deleting an existing LLM configuration.

        :param request: DRF request object containing the UUID of the configuration to delete.
              Parameters:
                -customer_uuid (required):header
                -user_uuid(required):header
                -llm_configuration_uuid (required) : query_param
        :return: Response object with success or error messages.
        """
        user_uuid = request.headers.get(constants.USER_ID)
        # Validate user UUID
        if not validate_input(user_uuid):
            raise CustomException(ErrorMessages.USER_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Attempting to delete LLM configuration {llm_configuration_uuid} by user {user_uuid}")

        # Delete the LLM configuration using the service layer
        self.__llm_config_service.delete_llm_configuration(llm_configuration_uuid, user_uuid)
        logger.info(f"Successfully deleted LLM configuration {llm_configuration_uuid}")
        return CustomResponse(SuccessMessages.DELETE_LLM_CONFIGURATION_SUCCESS)

    @swagger_auto_schema(
        tags=constants.LLM_CONFIGURATION_TAG,
        operation_description="Get LLM Configurations",
        manual_parameters=[constants.customer_uuid_header],
        responses={status.HTTP_200_OK: LLMConfigurationModelSerializer}
    )
    @action(detail=False, methods=['get'])
    def get_llm_configurations(self, request):
        logger.info("In llm_configuration.py :: :: :: LLMConfigurationViewSet :: :: :: get_llm_configurations ")

        """
        Retrieve all LLM configurations for a given customer.

        :param request: DRF request object containing the customer UUID.
             Parameters:
                -customer_uuid (required):header
        :return: Response object with a list of configurations.
        """
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)

        logger.info(f"Retrieving LLM configurations for customer {customer_uuid}")
        # Retrieve LLM configurations using the service layer
        configurations = self.__llm_config_service.get_llm_configurations(customer_uuid)
        logger.info(f"Successfully retrieved LLM configurations for customer {customer_uuid}")
        return CustomResponse(configurations)

    @swagger_auto_schema(
        tags=constants.LLM_CONFIGURATION_TAG,
        operation_description="Get LLM Configuration by ID",
        responses={status.HTTP_200_OK: LLMConfigurationModelSerializer}
    )
    @action(detail=False, methods=['get'])
    def get_llm_configuration_by_id(self, request, llm_configuration_uuid):
        logger.info("In llm_configuration.py :: :: :: LLMConfigurationViewSet :: :: :: get_llm_configuration_by_id ")

        """
        Retrieve a specific LLM configuration by its UUID.

        :param request: DRF request object containing the configuration UUID.
            -customer_uuid (required):header
                -application_uuid (required) : header
                -llm_configuration_uuid (required) : query_param
        :return: Response object with the requested configuration data.
        """
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)

        logger.info(f"Retrieving LLM configurations for customer {customer_uuid}")

        llm_configuration = self.__llm_config_service.get_llm_configuration_by_id(customer_uuid, llm_configuration_uuid)
        if len(llm_configuration):
            logger.info(f"Successfully retrieved LLM configuration {llm_configuration_uuid}")
            return CustomResponse(llm_configuration)
        else:
            return CustomResponse(None)
    @swagger_auto_schema(
        tags=constants.LLM_CONFIGURATION_TAG,
        operation_description="Get LLM Provider Meta Data",
        responses={
            status.HTTP_200_OK: 'List of LLM Provider Meta Data'
        }
    )
    @action(detail=False, methods=['get'])
    def get_llm_provider_meta_data(self, request):
        logger.info("In llm_configuration.py :: :: :: LLMConfigurationViewSet :: :: :: llm_configuration_for_channel")
        """
        Retrieve metadata for LLM providers.
        """
        llm_provider_meta_data = self.__llm_config_service.get_llm_provider_meta_data()
        return CustomResponse(llm_provider_meta_data)

    @action(detail=False, methods=['post'])
    def verify_llm_configuration(self, request):
        logger.info("In llm_configuration.py :: :: ::  LLMConfigurationViewSet :: :: :: verify_llm_configuration ")
        """
        Handle verifying the LLM configuration.

        :param request: DRF request object containing the data to verify a llm configuration.
             Parameters:
                -payload (request.data):request_body
        :return: Response object with success or error messages.
        """

        logger.info("Attempting to verify LLM configuration")

        # Validate incoming request data using serializer
        serializer = VerifyLLMConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            self.__llm_config_service.verify_llm_configuration(serializer.validated_data)
            logger.info("Successfully verified LLM configuration")
            return CustomResponse(SuccessMessages.VERIFY_LLM_CONFIGURATION_SUCCESS)
        else:
            logger.error(f"Invalid data for LLM configuration: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def update_llm_status(self, request):
        logger.info("In llm_configuration.py :: :: :: LLMConfigurationViewSet :: :: :: update_llm_status ")

        """
        Updates the specific LLM configuration status by its customer_uuid.

        -customer_uuid (required):header
        :return: Response object with the success message.
        """
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)
        status = request.query_params.get(constants.LLM_STATUS)
        
        # Validate user UUID
        if status is None or status.lower() not in ['true', 'false']:
            raise CustomException(ErrorMessages.LLM_STATUS_ERROR, status_code=status.HTTP_400_BAD_REQUEST)
        logger.info(f"Retrieving LLM configurations for customer {customer_uuid}")

        # Convert is_read to boolean
        status = status.lower() == 'true'

        self.__llm_config_service.update_llm_status_by_id(customer_uuid,status)
        logger.info(f"Successfully updated LLM status for {customer_uuid}")
        return CustomResponse(SuccessMessages.UPDATE_LLM_STATUS)

    @action(detail=False, methods=['get'])
    def get_llm_status(self, request):
        logger.info("In llm_configuration.py :: :: :: LLMConfigurationViewSet :: :: :: get_llm_status ")

        """
        Get the specific LLM configuration status by its customer_uuid.

        -customer_uuid (required):header
        :return: Response object with the status value.
        """
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)
        logger.info(f"Retrieving LLM configurations for customer {customer_uuid}")

        status = self.__llm_config_service.get_llm_status_by_id(customer_uuid)
        return CustomResponse(status)