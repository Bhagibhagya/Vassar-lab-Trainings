import inspect
import logging
from datetime import datetime
import pytz

from django.db.transaction import atomic
from rest_framework import status
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from ConnectedCustomerPlatform.responses import CustomResponse
from EmailApp.constant.constants import ChromadbMetaDataParams, EmailDashboardParams,  FileExtensions, BULK_IMPORT_EXCEL_FILE
from EmailApp.serializers import PaginationParamsSerializer
from EmailApp.utils import validate_uuids_dict
from Platform.constant import constants

from Platform.constant.constants import DUPLICATES, SPREAD_SHEET_MACRO_ENABLED, CUSTOMER_UUID, APPLICATION_UUID, ChromaExcelSheet

from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.serializers import DimensionSerializer, CustomResponseSerializer, DimensionCAMModelSerializer
from Platform.utils import get_headers_and_validate
from Platform.services.impl.dimension_service_impl import DimensionServiceImpl

logger = logging.getLogger(__name__)

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
# ViewSet for Dimension apis
class DimensionViewSet(ViewSet):
    """API View for managing dimension operations"""

    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DimensionViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside DimensionViewSet")
            self.dimension_service = DimensionServiceImpl()
            print(f"Inside DimensionViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True


    # Api to add the dimension under a dimension_type for a application of a customer
    @swagger_auto_schema(
        tags=constants.DIMENSIONS_TAG,
        operation_description="Add a dimension",
        request_body=DimensionSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.ADD_DIMENSION_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['POST'])
    @atomic
    def add_dimension(self, request):
        """
        Adds a new dimension and its mapping for a customer and application.

        :param request: The HTTP request object.

        :return: A success response with a message on success or an error response with appropriate details.
        """

        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Validate dimension data
        serializer = DimensionSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors)

        # Call service method to add dimension and its mappings
        duplicates = self.dimension_service.add_dimension_and_mapping(customer_uuid, application_uuid, user_uuid, serializer.validated_data)
        if duplicates:
            return CustomResponse(SuccessMessages.ADD_DIMENSION_SUCCESS, {"Duplicates found":duplicates})
        return CustomResponse(SuccessMessages.ADD_DIMENSION_SUCCESS)

    @action(detail=False, methods=['POST'])
    def add_training_phrases(self, request):
        """
        Adds a new dimension and its mapping for a customer and application.

        :param request: The HTTP request object.

        :return: A success response with a message on success or an error response with appropriate details.
        """

        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)
        utterances = request.data.get('utterances')
        dimension_name = request.data.get(ChromadbMetaDataParams.DIMENSION_NAME.value)
        parent_dimension_name = request.data.get(ChromadbMetaDataParams.PARENT_DIMENSION_NAME.value, None)

        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value: customer_uuid,
                             EmailDashboardParams.APPLICATION_UUID.value: application_uuid,
                             EmailDashboardParams.USER_UUID.value: user_uuid})
        duplicates = self.dimension_service.add_training_phrases(utterances=utterances,parent_dimension_name=parent_dimension_name,dimension_name=dimension_name,customer_uuid=customer_uuid,application_uuid=application_uuid)
        if duplicates:
            raise CustomException({
                    DUPLICATES.DUPLICATES_FOUND: duplicates,
                    DUPLICATES.MESSAGE: SuccessMessages.SIMILAR_TRAINING_PHRASES_ADDED
                })
        return CustomResponse(SuccessMessages.TRAINING_PHRASES_SUCCESSFULLY_ADDED)

    # Api to edit the dimension under a dimension_type for a application of a customer
    @swagger_auto_schema(
        tags=constants.DIMENSIONS_TAG,
        operation_description="Edit a dimension",
        request_body=DimensionSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header, constants.user_id_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_DIMENSION_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
        }
    )
    @action(detail=False, methods=['PUT'])
    @atomic
    def edit_dimension(self, request):
        """
        Edits a dimension mapping

        :param request: The HTTP request object.

        :return: A success response with a message on success or an error response with appropriate details.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Validate dimension data
        serializer = DimensionSerializer(data=request.data, is_edit=True)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        # Call service method to edit dimension and its mappings
        duplicates =self.dimension_service.edit_dimension(customer_uuid, application_uuid, user_uuid, serializer.validated_data)
        if duplicates:
            return CustomResponse(SuccessMessages.UPDATE_DIMENSION_SUCCESS, {"Duplicates found":duplicates})
        return CustomResponse(SuccessMessages.UPDATE_DIMENSION_SUCCESS)

    @action(detail=False, methods=['POST'])
    def edit_training_phrase(self, request):
        """
        Edits a dimension mapping

        :param request: The HTTP request object.

        :return: A success response with a message on success or an error response with appropriate details.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)
        utterance=request.data.get('utterance')
        dimension_names = request.data.get(ChromadbMetaDataParams.DIMENSION_NAMES.value)
        parent_dimension_name = request.data.get(ChromadbMetaDataParams.PARENT_DIMENSION_NAME.value, None)

        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid,EmailDashboardParams.USER_UUID.value:user_uuid})

        duplicates=self.dimension_service.edit_training_phrase(utterance=utterance,parent_dimension_name=parent_dimension_name,child_dimensions=dimension_names,customer_uuid=customer_uuid,application_uuid=application_uuid)
        if duplicates:
            return CustomResponse(SuccessMessages.TRAINING_PHRASE_SUCCESSFULLY_UPDATED, {"Duplicates found": duplicates})
        return CustomResponse(SuccessMessages.TRAINING_PHRASE_SUCCESSFULLY_UPDATED)

    # Api to delete dimension by mapping uuid
    @swagger_auto_schema(
        tags=constants.DIMENSIONS_TAG,
        operation_description="Delete Dimension",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='dimension_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='UUID of the Dimension')],
        responses={
            status.HTTP_200_OK: SuccessMessages.DELETE_DIMENSION_SUCCESS
        }
    )
    @action(detail=False, methods=['DELETE'])
    @atomic
    def delete_dimension(self, request, mapping_uuid):
        """
        Deletes a dimension mapping

        :param request: The HTTP request object.
        :param mapping_uuid: The UUID of the dimension mapping.

        :return: A success response with a message on success or an error response with appropriate details.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # Call service method to delete dimension mapping
        self.dimension_service.delete_dimension_mapping(customer_uuid, application_uuid, user_uuid, mapping_uuid)

        return CustomResponse(SuccessMessages.DELETE_DIMENSION_SUCCESS)


    # API to get dimension by mapping uuid
    @swagger_auto_schema(
        tags=constants.DIMENSIONS_TAG,
        operation_description="Get Dimension by ID",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='dimension_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Dimension UUID')],
        responses={status.HTTP_200_OK: DimensionCAMModelSerializer()}
    )
    @action(detail=False, methods=['GET'])
    def get_dimension_by_id(self, request, mapping_uuid):
        """
        Retrieves a dimension by its mapping UUID.

        :param request: The HTTP request object.
        :param mapping_uuid: The UUID of the dimension mapping.

        :return: A success response with the dimension data or None
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)

        # Call service method to get dimension mapping by uuid
        response_data = self.dimension_service.get_dimension_mapping_by_id(customer_uuid, application_uuid, mapping_uuid)

        return CustomResponse(response_data)


    # Api to get all dimensions under a dimension_type
    @swagger_auto_schema(
        tags=constants.DIMENSIONS_TAG,
        operation_description="Get Dimensions by type",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='dimension_type_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Dimension Type UUID')],
        responses={status.HTTP_200_OK: DimensionCAMModelSerializer()}
    )
    @action(detail=False, methods=['POST'])
    def get_dimensions_by_type(self, request, dimension_type_uuid):
        """
        Retrieves dimensions by their dimension type UUID.

        :param request: The HTTP request object.
        :param dimension_type_uuid: The UUID of the dimension type.

        :return: A success response with the list of dimensions or empty list
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Dimension by DimensionType :: time before get_dimension_by_type :: {format_indian_time(start_time)}\n")

        # Extract user information from headers
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)
        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid})

        # Validate request body using the serializer
        pagination_serializer = PaginationParamsSerializer(data=request.data.get(ChromadbMetaDataParams.PARAMS.value))

        if not pagination_serializer.is_valid():
            raise CustomException(pagination_serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        # Call service method to get dimension mapping by uuid
        get_dimensions_by_type_service_st = datetime.now()
        logger.info(f"\nTime profile :: Get Dimension by DimensionType :: time before Calling Get dimension by dimension type service :: {format_indian_time(get_dimensions_by_type_service_st)}\n")
        response_data = self.dimension_service.get_dimensions_by_dimension_type(customer_uuid, application_uuid, dimension_type_uuid,pagination_serializer.validated_data)
        get_dimensions_by_type_service_et = datetime.now()
        logger.info(f"\nTime profile :: Get Dimension by DimensionType :: time after Calling Get dimension by dimension type service:: {format_indian_time(get_dimensions_by_type_service_et)}\n")
        logger.info(f"\nTime profile :: Get Dimension by DimensionType :: Total time taken Calling Get dimension by dimension type service :: {(get_dimensions_by_type_service_et - get_dimensions_by_type_service_st).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Dimension by DimensionType:: {total_time:.4f} ms")

        return CustomResponse(response_data)


    # Api to get all country and state dimensions for a customer-application
    @swagger_auto_schema(
        tags=constants.DIMENSIONS_TAG,
        operation_description="Get Dimensions for dropdown in add_customer",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header,
                           openapi.Parameter(name='parent_uuid', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Parent Dimension UUID')],
        responses={status.HTTP_200_OK: DimensionCAMModelSerializer()}
    )
    @action(detail=False, methods=['GET'])
    def get_geography_dimensions(self, request, parent_dimension_uuid=None):
        """
        Retrieves dimensions as a dropdown list.

        :param request: The HTTP request object.
        :param parent_dimension_uuid: The UUID of the parent dimension (optional).

        :return: A success response with the list of dimensions or an error response with appropriate details.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Geography Dimensions :: time before get_geography_dimensions :: {format_indian_time(start_time)}\n")

        # Extract user information from headers
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)

        # Call service method to get countries or states for a customer-application
        get_geography_dimensions_service_st = datetime.now()
        logger.info(f"\nTime profile :: Get Geography Dimensions :: time before Calling geography dimensions Service :: {format_indian_time(get_geography_dimensions_service_st)}\n")
        response_data = self.dimension_service.get_geography_dimensions(customer_uuid, application_uuid, parent_dimension_uuid)
        get_geography_dimensions_service_et = datetime.now()
        logger.info(f"\nTime profile :: Get Geography Dimensions :: time after  Calling geography dimensions Service :: {format_indian_time(get_geography_dimensions_service_et)}\n")
        logger.info(f"\nTime profile :: Get Geography Dimensions :: Total time taken  Calling geography dimensions Service :: {(get_geography_dimensions_service_et - get_geography_dimensions_service_st).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Geography Dimensions :: {total_time:.4f} ms")

        return CustomResponse(response_data)


    # Api to get country,states for dropdown
    @swagger_auto_schema(
        tags=constants.DIMENSIONS_TAG,
        operation_description="Get all countries and states for dropdown",
        responses={status.HTTP_200_OK: CustomResponseSerializer()}
    )
    @action(detail=False, methods=['GET'])
    def get_country_state_dropdown(self, request, country_name=None):
        """
        Retrieves list of countries or states

        :param country_name: The name of the country (optional)
        :param request: The HTTP request object.

        :return: A success response with the list of countries or states or an error response with appropriate details.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Country State DropDown :: time before get_country_state_dropdown :: {format_indian_time(start_time)}\n")

        # Call service method to get list of all countries or states under a country
        get_country_state_dd_st = datetime.now()
        logger.info(f"\nTime profile :: Get Country State DropDown :: time before calling get countries state Service :: {format_indian_time(get_country_state_dd_st)}\n")
        response_data = self.dimension_service.get_countries_or_states(country_name)
        get_country_state_dd_et = datetime.now()
        logger.info(f"\nTime profile :: Get Country State DropDown :: time after calling get countries state Service :: {format_indian_time(get_country_state_dd_et)}\n")
        logger.info(f"\nTime profile :: Get Country State DropDown :: Total time taken get countries state Service :: {(get_country_state_dd_et - get_country_state_dd_st).total_seconds() * 1000:.4f} ms\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Country State DropDown :: {total_time:.4f} ms")

        return CustomResponse(response_data)

    @action(detail=False, methods=['post'])
    def upload_examples_to_chromadb(self, request):
        """
                API to upload an Excel file and save the training phrases in ChromaDB directly from memory.

                :param request: HTTP request with the Excel file in multipart/form-data format.
                :param customer_uuid: UUID of the customer for whom the intents and phrases are being uploaded.
                :param application_uuid: UUID of the application.
                :param user_uuid: UUID of the user uploading the file.
                :return: Response indicating success or failure.
        """

        if BULK_IMPORT_EXCEL_FILE not in request.FILES:
            raise InvalidValueProvidedException(f"Cannot find excel file with name {BULK_IMPORT_EXCEL_FILE}",
                                                status_code=status.HTTP_400_BAD_REQUEST)

        excel_file = request.FILES.get(BULK_IMPORT_EXCEL_FILE)

        # check whether the file type is macro enabled and with .xlsm or not
        if not (excel_file.content_type == SPREAD_SHEET_MACRO_ENABLED and excel_file.name.endswith(
                FileExtensions.XLSM.value)):
            logger.error(ErrorMessages.NOT_MACRO_ENABLED_EXCEL)
            raise InvalidValueProvidedException(ErrorMessages.NOT_MACRO_ENABLED_EXCEL)

        # Get uuids from headers
        customer_uuid = request.headers.get(CUSTOMER_UUID)
        application_uuid = request.headers.get(APPLICATION_UUID)

        # Validate UUIDs
        validate_uuids_dict({
            CUSTOMER_UUID: customer_uuid,
            APPLICATION_UUID: application_uuid
        })

        return self.dimension_service.upload_examples_to_chromadb(excel_file_obj=excel_file,
                                                                        customer_uuid=customer_uuid,
                                                                        application_uuid=application_uuid)


    @action(detail=False, methods=['get'])
    def download_training_phrases(self, request):

        # Get uuids from headers
        customer_uuid = request.headers.get(CUSTOMER_UUID)
        application_uuid = request.headers.get(APPLICATION_UUID)

        # Validate UUIDs
        validate_uuids_dict({
            CUSTOMER_UUID: customer_uuid,
            APPLICATION_UUID: application_uuid
        })

        return self.dimension_service.download_training_phrases(application_uuid=application_uuid,
                                                             customer_uuid=customer_uuid)

    @action(detail=False, methods=['post'])
    def resolve_duplicates(self, request):

        # Get uuids from headers
        customer_uuid = request.headers.get(CUSTOMER_UUID)
        application_uuid = request.headers.get(APPLICATION_UUID)

        # Validate UUIDs
        validate_uuids_dict({
            CUSTOMER_UUID: customer_uuid,
            APPLICATION_UUID: application_uuid
        })

        training_phrases = request.data.get(ChromaExcelSheet.UTTERANCES.value)

        if not training_phrases:
            raise InvalidValueProvidedException(detail= "No utterances found", status_code= status.HTTP_400_BAD_REQUEST)

        return self.dimension_service.resolve_duplicates(application_uuid=application_uuid,
                                                         customer_uuid=customer_uuid, utterances= training_phrases)

    @swagger_auto_schema(
        operation_summary="Download default template",
        operation_description="Downloads the default Excel template stored in Azure.",
        responses={
            200: openapi.Response(
                description="Base64 encoded file content",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "content": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format="byte",
                            description="Base64 encoded content of the template"
                        ),
                        "content_type": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="MIME type of the file"
                        ),
                    },
                ),
            ),
            400: "Bad Request - Invalid UUIDs",
            500: "Internal Server Error",
        },
    )
    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """
        Downloads the default template which is stored in azure and the url is stored in settings
        """
        # Get uuids from headers
        customer_uuid = request.headers.get(CUSTOMER_UUID)
        application_uuid = request.headers.get(APPLICATION_UUID)

        # Validate UUIDs
        validate_uuids_dict({
            CUSTOMER_UUID: customer_uuid,
            APPLICATION_UUID: application_uuid
        })

        return self.dimension_service.download_template()



