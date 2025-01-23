import logging

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import PromptSerializer, PromptModelSerializer
from Platform.services.impl.prompt_service_impl import PromptServiceImpl
from Platform.utils import get_headers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import inspect
from datetime import datetime
import pytz



logger = logging.getLogger(__name__)


indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


# ViewSet for Prompt apis
class PromptViewSet(ViewSet):
    """
        ViewSet for managing Prompt, providing methods to add, edit,
        delete, and retrieve.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the PromptViewSet is created.
            Args:
                cls: The class reference.
                *args: Positional arguments for initialization.
                **kwargs: Keyword arguments for initialization.
            Returns:
                PromptViewSet: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(PromptViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
            Initialize the PromptViewSet.
            This method is called only once due to the singleton pattern. It initializes the
            PromptViewSet for handling business logic related to Prompts.
            Args:
                **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.__prompt_service = PromptServiceImpl()
            logger.info(f"Inside PromptViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    @swagger_auto_schema(
        tags=constants.PROMPT_TAG,
        operation_description="Add a Prompt",
        request_body=PromptSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_PROMPT_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['post'])
    def add_prompt(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started creating a prompt.")
        """
            Handles the addition of new prompt.
            :param request: The HTTP request object containing headers and other request data.
             Parameters:
                -customer_uuid (required):header
                -application_uuid (required):header
                -user_uuid (required):header
                -payload (request.data):request_body
            :return: Response object with success or error messages.
        """
        start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt :: time before add_prompt :: {format_indian_time(start_time)}\n")

        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        # validate the request data
        logger.info("Validating request data with PromptSerializer.")
        prompt_serializer_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt :: time before PromptSerializer :: {format_indian_time(prompt_serializer_start_time)}\n")
        serializer = PromptSerializer(data=request.data,status=constants.ADD_KEY)
        if not serializer.is_valid():
            logger.error(f"Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors)
        prompt_serializer_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt :: time after PromptSerializer :: {format_indian_time(prompt_serializer_end_time)}\n")
        logger.info(
            f"\nTime profile :: Add Prompt :: Total time taken PromptSerializer :: {((prompt_serializer_end_time - prompt_serializer_start_time).total_seconds() * 1000):.4f}\n")

        logger.info("Request data is valid.")
        # Call service to create prompt
        prompt_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt :: time before Prompt Service :: {format_indian_time(prompt_service_start_time)}\n")
        self.__prompt_service.create_prompt(customer_uuid, application_uuid, user_uuid , serializer.validated_data)
        prompt_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt :: time after Prompt Service :: {format_indian_time(prompt_service_end_time)}\n")
        logger.info(
            f"\nTime profile :: Add Prompt :: Total time taken Prompt Service :: {(prompt_service_end_time - prompt_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Add Prompt API execution: {total_time:.4f} ms")

        # Send successful response
        logger.info("Prompt added successfully.")
        return CustomResponse(SuccessMessages.ADD_PROMPT_SUCCESS)

    # Api to edit the prompt for application of a customer
    @swagger_auto_schema(
        tags=constants.PROMPT_TAG,
        operation_description="Edit a Prompt",
        request_body=PromptSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_PROMPT_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['put'])
    def edit_prompt(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started editing a prompt.")
        """
            Edit existing prompt based on the provided data.

            :param request: The HTTP request object containing headers and other request data.
             Parameters:
                -customer_uuid (required):header
                -application_uuid (required):header
                -user_uuid (required):header
                -payload (request.data):request_body
            :return: Response object with success or error messages.
        """

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt :: time before update_prompt :: {format_indian_time(start_time)}\n")

        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        # validate the request data
        logger.info("Validating request data with PromptSerializer.")
        prompt_serializer_start_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt :: time before PromptSerializer :: {format_indian_time(prompt_serializer_start_time)}\n")
        serializer = PromptSerializer(data=request.data,status=constants.EDIT_KEY)
        if not serializer.is_valid():
            logger.error(f"Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors)
        prompt_serializer_end_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt :: time after PromptSerializer :: {format_indian_time(prompt_serializer_end_time)}\n")
        logger.info(
            f"\nTime profile :: Update Prompt :: Total time taken PromptSerializer :: {((prompt_serializer_end_time - prompt_serializer_start_time).total_seconds() * 1000):.4f}\n")

        logger.info("Request data is valid.")

        prompt_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt :: time before Prompt Service :: {format_indian_time(prompt_service_start_time)}\n")

        # Call service to update prompt
        self.__prompt_service.update_prompt(customer_uuid, application_uuid, user_uuid, serializer.validated_data)

        prompt_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt :: time after Prompt Service :: {format_indian_time(prompt_service_end_time)}\n")
        logger.info(
            f"\nTime profile :: Update Prompt :: Total time taken Prompt Service :: {(prompt_service_end_time - prompt_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Update Prompt API execution: {total_time:.4f} ms")

        # Send successful response
        logger.info("Prompt updated successfully.")
        return CustomResponse(SuccessMessages.UPDATE_PROMPT_SUCCESS)

    # Api to get all prompts
    @swagger_auto_schema(
        tags=constants.PROMPT_TAG,
        operation_description="Get Prompts",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: PromptModelSerializer
        }
    )
    @action(detail=False, methods=['get'])
    def get_prompts(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started getting prompts.")
        """
            Retrieve all prompts of customer-application

            :param request: The HTTP request object containing headers and other request data.
             Parameters:
                -customer_uuid (required):header
                -application_uuid (required):header
                -user_uuid (required):header
            :return: Response object with prompts.
        """
        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts :: time before get_prompts :: {format_indian_time(start_time)}\n")

        customer_uuid, application_uuid, _ = get_headers(request.headers)

        prompt_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts :: time before Prompt Service :: {format_indian_time(prompt_service_start_time)}\n")
        # Returns the Prompts
        response_data = self.__prompt_service.get_prompts(customer_uuid,application_uuid)
        prompt_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts :: time after Prompt Service :: {format_indian_time(prompt_service_end_time)}\n")
        logger.info(
            f"\nTime profile :: Get Prompts :: Total time taken Prompt Service :: {(prompt_service_end_time - prompt_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Prompts API execution: {total_time:.4f} ms")

        return CustomResponse(response_data)

    # Api to get prompt by ID
    @swagger_auto_schema(
        tags=constants.PROMPT_TAG,
        operation_description="Get Prompt by ID",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='prompt_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Prompt UUID')],
        responses={status.HTTP_200_OK: PromptModelSerializer}
    )
    @action(detail=False, methods=['get'])
    def get_prompt_by_id(self, request,prompt_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started getting prompt by its id.")
        """ 
            Retrieve prompt by prompt_uuid

            :param request: The HTTP request object containing headers and other request data.
            :param prompt_uuid: The unique identifier of the prompt to be fetched.
            :return: A response containing the filtered prompts of application
        """
        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt By Id :: time before get_prompt_by_id :: {format_indian_time(start_time)}\n")

        prompt_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts By Id :: time before Prompt Service :: {format_indian_time(prompt_service_start_time)}\n")
        prompt = self.__prompt_service.get_prompt_by_id(prompt_uuid)
        prompt_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts By Id :: time after Prompt Service :: {format_indian_time(prompt_service_end_time)}\n")
        logger.info(f"\nTime profile :: Get Prompts By Id :: Total time taken Prompt Service :: {(prompt_service_end_time - prompt_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Prompt by Id API execution: {total_time:.4f} ms")
        return CustomResponse(prompt)

    # Api to delete prompt by ID
    @swagger_auto_schema(
        tags=constants.PROMPT_TAG,
        operation_description="Delete Prompt",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='prompt_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Prompt UUID')],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_PROMPT_SUCCESS
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_prompt(self, request,prompt_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started deleting prompt by its id.")
        """
            Delete prompt based on the provided UUID.

            :param request: The HTTP request object containing the request data.
            :param prompt_uuid: The unique identifier of the prompt to be deleted.
            :return: A response indicating the success or failure of the delete operation.
        """
        _,_,user_uuid = get_headers(request.headers)
        logger.info(f"delete_prompt :: user_uuid: {user_uuid}, prompt_uuid: {prompt_uuid}")
        # Call service to delete the prompt and log the action
        self.__prompt_service.delete_prompt(prompt_uuid, user_uuid)

        logger.info("Prompt deleted successfully")
        return CustomResponse(SuccessMessages.DELETE_PROMPT_SUCCESS)