import inspect
import logging
from datetime import datetime
import pytz

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import PromptTemplateSerializer, PromptTemplateModelSerializer , PromptCategoryModelSerializer
from Platform.services.impl.prompt_template_service_impl import PromptTemplateServiceImpl
from Platform.utils import get_headers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import json

logger = logging.getLogger(__name__)


indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
# ViewSet for Prompt Template apis
class PromptTemplateViewSet(ViewSet):
    """
        ViewSet for managing Prompt Templates, providing methods to add, edit,
        delete, and retrieve.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the PromptTemplateViewSet is created.
            Args:
                cls: The class reference.
                *args: Positional arguments for initialization.
                **kwargs: Keyword arguments for initialization.
            Returns:
                PromptViewSet: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(PromptTemplateViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
            Initialize the PromptTemplateViewSet.
            This method is called only once due to the singleton pattern. It initializes the
            PromptTemplateViewSet for handling business logic related to Prompts.
            Args:
                **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside PromptTemplateViewSet - Singleton Instance ID: {id(self)}")
            self.prompt_template_service = PromptTemplateServiceImpl()
            self.initialized = True


    # Api to add the prompt template for application of a customer
    @swagger_auto_schema(
        tags=constants.PROMPT_TEMPLATE_TAG,
        operation_description="Add a Prompt Template",
        request_body=PromptTemplateSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_PROMPT_TEMPLATE_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['post'])
    def add_prompt_template(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started adding a prompt template.")
        """
            Handles the addition of new prompt template.
            :param request: The HTTP request object containing headers and other request data.
             Parameters:
                -customer_uuid (required):header
                -application_uuid (required):header
                -user_uuid (required):header
                -payload (request.data):request_body
            :return: Response object with success or error messages.
        """

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template :: time before add_prompt_template :: {format_indian_time(start_time)}\n")

        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)

        # validate the request data
        logger.info("Validating request data with PromptTemplateSerializer.")
        prompt_template_serializer_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template :: time before PromptTemplateSerializer :: {format_indian_time(prompt_template_serializer_start_time)}\n")
        serializer = PromptTemplateSerializer(data=request.data,status=constants.ADD_KEY)
        if not serializer.is_valid():
            logger.error(f"Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors)
        prompt_template_serializer_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template :: time after PromptTemplateSerializer :: {format_indian_time(prompt_template_serializer_end_time)}\n")
        logger.info(f"\nTime profile :: Add Prompt Template :: Total time taken PromptTemplateSerializer :: {((prompt_template_serializer_end_time - prompt_template_serializer_start_time).total_seconds() * 1000):.4f}\n")

        logger.info("Request data is valid.")
        # Call service to create prompt
        prompt_template_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template :: time before Prompt Template Service :: {format_indian_time(prompt_template_service_start_time)}\n")
        self.prompt_template_service.create_prompt_template(customer_uuid, application_uuid, user_uuid, serializer.validated_data)
        prompt_template_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template :: time after Prompt Template Service :: {format_indian_time(prompt_template_service_end_time)}\n")
        logger.info(
            f"\nTime profile :: Add Prompt Template :: Total time taken Prompt Template Service :: {(prompt_template_service_end_time - prompt_template_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Add Prompt Template API execution: {total_time:.4f} ms")

        # Send successful response
        logger.info("PromptTemplate added successfully.")
        return CustomResponse(SuccessMessages.ADD_PROMPT_TEMPLATE_SUCCESS)

    # Api to edit the prompt template for application of a customer
    @swagger_auto_schema(
        tags=constants.PROMPT_TEMPLATE_TAG,
        operation_description="Edit a Prompt Template",
        request_body=PromptTemplateSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_PROMPT_TEMPLATE_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['post'])
    def edit_prompt_template(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started editing a prompt template.")
        """
            Edit existing prompt template based on the provided data.

            :param request: The HTTP request object containing headers and other request data.
             Parameters:
                -customer_uuid (required):header
                -application_uuid (required):header
                -user_uuid (required):header
                -payload (request.data):request_body
            :return: Response object with success or error messages.
        """
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)

        # validate the request data
        logger.info("Validating request data with PromptTemplateSerializer.")
        serializer = PromptTemplateSerializer(data=request.data,status=constants.EDIT_KEY)
        if not serializer.is_valid():
            logger.error(f"Validation failed: {serializer.errors}")
            raise CustomException(serializer.errors)
        logger.info("Request data is valid.")
        self.prompt_template_service.update_prompt_template(customer_uuid, application_uuid, user_uuid, serializer.validated_data)
        logger.info("PromptTemplate updated successfully.")
        return CustomResponse(SuccessMessages.UPDATE_PROMPT_TEMPLATE_SUCCESS)


    # Api to get all prompt templates
    @swagger_auto_schema(
        tags=constants.PROMPT_TEMPLATE_TAG,
        operation_description="Get Prompt Templates",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: PromptTemplateModelSerializer
        }
    )
    @action(detail=False, methods=['get'])
    def get_prompt_templates(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started getting prompt templates.")
        """
            Retrieve all prompt templates of customer-application

            :param request: The HTTP request object containing headers and other request data.
             Parameters:
                -customer_uuid (required):header
                -application_uuid (required):header
                -user_uuid (required):header
            :return: Response object with prompt templates.
        """

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt Templates :: time before get_prompt_templates :: {format_indian_time(start_time)}\n")


        customer_uuid, application_uuid, _ = get_headers(request.headers)
        prompt_category_uuid = request.query_params.get('prompt_category_uuid')

        prompt_template_service_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt Templates :: time before Prompt Template Service :: {format_indian_time(prompt_template_service_start_time)}\n")
        # Returns the PromptTemplate
        response_data = self.prompt_template_service.get_prompt_templates(customer_uuid, application_uuid,prompt_category_uuid)
        prompt_template_service_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt Templates :: time after Prompt Template Service :: {format_indian_time(prompt_template_service_end_time)}\n")
        logger.info(f"\nTime profile :: Get Prompt Templates :: Total time taken Prompt Template Service :: {(prompt_template_service_end_time - prompt_template_service_start_time).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Prompt Templates API execution: {total_time:.4f} ms")

        return CustomResponse(response_data)

    # Api to get prompt template by ID
    @swagger_auto_schema(
        tags=constants.PROMPT_TEMPLATE_TAG,
        operation_description="Get Prompt Template by ID",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='prompt_template_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Prompt Template UUID')],
        responses={status.HTTP_200_OK: PromptTemplateModelSerializer}
    )
    @action(detail=False, methods=['get'])
    def get_prompt_template_by_id(self, request,mapping_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started getting prompt template by its id.")
        """ 
            Retrieve prompt template by mapping_uuid

            :param request: The HTTP request object containing headers and other request data.
            :param prompt_uuid: The unique identifier of the prompt to be fetched.
            :return: A response containing the filtered prompt template of application
        """
        # Returns the PromptTemplate
        response_data = self.prompt_template_service.get_prompt_template_by_id(mapping_uuid)

        return CustomResponse(response_data)

    # Api to delete prompt template by ID
    @swagger_auto_schema(
        tags=constants.PROMPT_TEMPLATE_TAG,
        operation_description="Delete Prompt Template",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='prompt_template_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Prompt Template UUID')],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_PROMPT_TEMPLATE_SUCCESS
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_prompt_template(self, request,mapping_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started deleting prompt template by its id.")
        """
            Delete prompt_template based on the provided UUID.

            :param request: The HTTP request object containing the request data.
            :param mapping_uuid: The unique identifier of the prompt_template_customer_application_mapping to be deleted.
            :return: A response indicating the success or failure of the delete operation.
        """
        _, _, user_uuid = get_headers(request.headers)
        self.prompt_template_service.delete_prompt_template(mapping_uuid,user_uuid)
        return CustomResponse(SuccessMessages.DELETE_PROMPT_TEMPLATE_SUCCESS)

    # Api to get prompt_category list
    @swagger_auto_schema(
        tags=constants.PROMPT_TEMPLATE_TAG,
        operation_description="Get all prompt categories",
        responses={
            status.HTTP_200_OK: PromptCategoryModelSerializer
        }
    )
    @action(detail=False, methods=['get'])
    def get_prompt_categories(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """ 
            This Method is used to get all prompt categories
        """
        # Returns the all prompt_categories
        prompt_category = self.prompt_template_service.get_prompt_categories()
        return CustomResponse(prompt_category)
