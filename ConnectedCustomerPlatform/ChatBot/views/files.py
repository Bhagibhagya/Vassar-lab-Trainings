import base64
import inspect
import json
import fitz

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from ChatBot.constant.constants import KnowledgeSourceConstants
from ChatBot.serializers import ErrorPagiNationSerializer, KnowledgeSourceNamesSerializer, KnowledgeSourceSerializer, \
    UploadFilesSerializer, ReUploadFilesSerializer, UploadImagesSerializer, DriveUploadSerializer, \
    UpdateKnowledgeSourceInternalJsonSerializer, EditableInternalJsonSerializer
from uuid import uuid4
from ChatBot.services.interface.knowledge_source_service_interface import IKnowledgeSource
from ConnectedCustomerPlatform.utils import Utils
from Platform.serializers import PagiNationSerializer
from DatabaseApp.models import Errors, KnowledgeSources
from Platform.constant import constants
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.success_messages import SuccessMessages
from DBServices.models import Files, Entities
from django.conf import settings
from ConnectedCustomerPlatform.responses import CustomResponse
from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException, \
    InvalidValueProvidedException
from ChatBot.utils import get_knowledge_source_type, get_collection_name
from AIServices.VectorStore.chromavectorstore import chroma_obj
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from Platform.utils import get_headers_and_validate
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager
from rest_framework.parsers import MultiPartParser, JSONParser
from EventHub.send_sync import EventHubProducerSync
import logging
import os
import requests

import io
from django.core.files.base import ContentFile
from ChatBot.services.services import get_service

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

azure_blob_manager = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)

file_processing_producer = EventHubProducerSync(settings.FILE_CONSUMER_EVENT_TOPIC)


class FilesViewSet(ViewSet):
    def __init__(self,knowledge_source_service=None, **kwargs):
        super().__init__(**kwargs)
        self.__knowledge_source_service: IKnowledgeSource = knowledge_source_service or  get_service("knowledge_source_service")
    parser_classes = (JSONParser, MultiPartParser)

    @action(detail=False, methods=['post'])
    def upload_knowledge_sources(self, request):
        logger.info("In files.py :: :: :: FilesViewSet :: :: :: upload_files")
        """
        Uploads files to the application.

        Parameters:
            - request: HTTP request object
        """
        customer_uuid, application_uuid,user_uuid=get_headers_and_validate(request.headers)
        serializer = UploadFilesSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        self.__knowledge_source_service.add_knowledge_sources_in_application(serializer.validated_data, user_uuid, customer_uuid, application_uuid)

        return CustomResponse(result=SuccessMessages.FILES_UPLOAD_SUCCESS, code=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def reupload_knowledge_source(self, request):
        logger.info("In files.py :: :: :: FilesViewSet :: :: :: reupload_file")
        """
        Reuploads a file to the application.

        Parameters:
            - request: HTTP request object
            - knowledge_source_uuid is the required
        """
        customer_uuid, application_uuid,user_uuid=get_headers_and_validate(request.headers)
        serializer = ReUploadFilesSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        self.__knowledge_source_service.reupload_knowledge_source(serializer.validated_data,user_uuid,customer_uuid,application_uuid)
        return CustomResponse(result=SuccessMessages.FILES_REUPLOAD_SUCCESS, code=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="knowledge_source_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_knowledge_source_by_uuid(self, request, knowledge_source_uuid):
        """
        Deletes a knowledge_source_uuid based on the application and customer uuid's.

        Parameters:
            - request: HTTP request object
            - knowledge_source_uuid: ID of the file to delete
        """
        logger.debug(
            f"In files.py :: :: :: FilesViewSet :: :: :: delete_file_by_id :: Deleting file with ID: {knowledge_source_uuid}")

        customer_uuid, application_uuid,_ = get_headers_and_validate(request.headers)
        self.__knowledge_source_service.delete_knowledge_source_by_uuid(knowledge_source_uuid,customer_uuid,application_uuid)

        return CustomResponse(result=SuccessMessages.FILE_DELETE_SUCCESS)


    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="knowledge_source_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=["get"])
    def get_knowledge_source_by_knowledge_source_uuid(self, request, knowledge_source_uuid):
        """
        Retrieves a file by its ID and provides a presigned URL.

        Parameters:
            - request: HTTP request object
            - knowledge_source_uuid: ID of the file to retrieve
        """
        logger.debug(
            f"In files.py :: :: :: FilesViewSet :: :: :: get_file_by_id :: Retrieving file with ID: {knowledge_source_uuid}")
        result = self.__knowledge_source_service.get_knowledge_source_by_knowledge_source_uuid(knowledge_source_uuid)
        return CustomResponse(result=result)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='page_number', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='page_number'),
            openapi.Parameter(name='total_entries_per_page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='total_entries_per_page'),
            openapi.Parameter(name='knowledge_source_name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='knowledge_source_name'),
            constants.application_uuid_header, constants.customer_uuid_header
        ],
        responses={status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=["get"])
    def get_knowledge_sources_list(self, request):
        logger.info("FilesViewSet: Fetching knowledge_sources based on the customer & application uuid's.")
        """
        Retrieves knowledge_sources based on the customer & application uuid's
        Parameters:
            - request: HTTP request object
        """
        customer_uuid, application_uuid, _ = get_headers_and_validate(request.headers)

        logger.debug(f"Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")

        serializer = KnowledgeSourceSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(f"Invalid query parameters: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        response = self.__knowledge_source_service.get_knowledge_sources_by_customer_and_application_ids(customer_uuid, application_uuid, serializer.validated_data)

        logger.info("Knowledge Sources fetched successfully.")
        return CustomResponse(result=response)
   
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='page_number', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='page_number'),
            openapi.Parameter(name='total_entries_per_page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='total_entries_per_page'),
            openapi.Parameter(name='knowledge_source_uuid', in_=openapi.IN_QUERY, type=openapi.FORMAT_UUID, description='knowledge_source_uuid'),
            constants.application_uuid_header, constants.customer_uuid_header
        ],
        responses={status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=["get"])
    def get_knowledge_sources_errors(self, request):
        logger.info("FilesViewSet: Fetching knowledge_sources errors for the application.")
        """
        Retrieves knowledge_sources errors associated with a specific application
        Parameters:
            - request: HTTP request object
        """
        serializer = ErrorPagiNationSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(f"Invalid query parameters: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        response = self.__knowledge_source_service.get_knowledge_sources_errors(serializer.validated_data)

        return CustomResponse(result=response)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="knowledge_source_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['put'])
    def resolve_knowledge_source(self, request, knowledge_source_uuid):
        """
        method to resolve file

        Parameters:
        - request: HTTP request object
        - knowledge_source_uuid: UUID of the file to assign the entity
        """

        logger.info("In files.py :: :: :: FilesViewSet :: :: :: resolve_knowledge_source")
        customer_uuid, application_uuid,_ = get_headers_and_validate(request.headers)

        self.__knowledge_source_service.resolve_knowledge_source(knowledge_source_uuid,customer_uuid,application_uuid)
        return CustomResponse(SuccessMessages.FILE_RESOLVE_SUCCESS)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="knowledge_source_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['get'])
    def get_internal_json(self, request, knowledge_source_uuid):
        logger.info("In files.py :: :: :: FilesViewSet :: :: :: get_internal_json")
        """
        method to get internal json

        Parameters:
        - request: HTTP request object
        - knowledge_source_uuid: UUID of the file to assign the entity
        """
        response = self.__knowledge_source_service.get_knowledge_source_internal_json(knowledge_source_uuid)
        return CustomResponse(response)

    @swagger_auto_schema(
        manual_parameters=[constants.customer_uuid_header,
                           constants.application_uuid_header],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=["get"])
    def get_videos_in_application(self, request):
        logger.info("In files.py :: :: :: FilesViewSet :: :: :: get_videos_in_application")
        """
        method to get get videos in application

        Parameters:
        - request: HTTP request object
        """
        customer_uuid,application_uuid,_=get_headers_and_validate(request.headers)
        response = self.__knowledge_source_service.get_video_type_knowledge_sources_in_application(customer_uuid, application_uuid)
        return CustomResponse(response)

    @swagger_auto_schema(
        manual_parameters=[constants.customer_uuid_header,
                           constants.application_uuid_header],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['get'])
    def get_files_for_questions_and_answers(self, request):
        logger.info("In files.py :: :: :: FilesViewSet :: :: :: get_files_for_questions_and_answers")
        """
        method to get get files for qa

        Parameters:
        - request: HTTP request object
        """
        customer_uuid, application_uuid,_ = get_headers_and_validate(request.headers)
        result_list = self.__knowledge_source_service.get_knowledge_sources_for_question_and_answer(customer_uuid,
                                                                                                    application_uuid)
        return CustomResponse(result=result_list)

    @action(detail=False, methods=['post'])
    def upload_image_to_azure(self, request):
        logger.info("In files.py :: FilesViewSet :: upload_image_to_azure")
        """
        Uploads images to Azure Blob Storage and returns presigned URLs.

        Parameters:
            - request: HTTP request object containing serialized image upload data
        """
        customer_uuid, application_uuid,_ = get_headers_and_validate(request.headers)
        serializer = UploadImagesSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        response = self.__knowledge_source_service.upload_image_to_azure(serializer.validated_data,customer_uuid,application_uuid)
        return CustomResponse(response)

    @swagger_auto_schema(
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        request_body=DriveUploadSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.FILES_UPLOAD_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    
    @action(detail=False, methods=['post'])
    def upload_files_via_drives(self, request):
        """
        uploads files to knowledge sources
        """
        customer_uuid, application_uuid,user_uuid=get_headers_and_validate(request.headers)
        serializer = DriveUploadSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        service_response=self.__knowledge_source_service.upload_files_via_drives(serializer.validated_data, user_uuid, customer_uuid, application_uuid)
        if service_response:
            return CustomResponse(service_response)
        return CustomResponse(result=SuccessMessages.FILES_UPLOAD_SUCCESS)

    @swagger_auto_schema(
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        request_body=KnowledgeSourceNamesSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.FILES_UPLOAD_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    
    @action(detail=False, methods=['post'])
    def check_knowledge_sources_exists(self, request):
        """
        Checks if the specified knowledge sources exist for the given customer and application.
        """
        customer_uuid, application_uuid,_=get_headers_and_validate(request.headers)
        serializer = KnowledgeSourceNamesSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        response=self.__knowledge_source_service.check_knowledge_sources_exists(serializer.validated_data, customer_uuid, application_uuid)
        return CustomResponse(result=response)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name="knowledge_source_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING),
            openapi.Parameter(
                name="page_number",
                in_=openapi.IN_PATH,
                description="Page number in the knowledge source (file)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['get'])
    def generate_formatted_internal_json(self, request, knowledge_source_uuid, page_number):
        """
            generate a formatted json from internal_json so that user can edit fields
            Args:
                knowledge_source_uuid (str): unique identifie of knowledge_source(file)
                page_number (str): page number in a knowledge_source(file)
            Returns:
                formatted json
        """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        validate_response = Utils.validate_input(knowledge_source_uuid)
        if not validate_response:
            raise CustomException(ErrorMessages.KNOWLEDGE_SOURCE_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        validate_response = Utils.validate_input(page_number)
        if not validate_response:
            raise CustomException(ErrorMessages.PAGE_NUMBER_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        response = self.__knowledge_source_service.generate_formatted_json_from_internal_json(knowledge_source_uuid, page_number)
        return CustomResponse(response)

    @swagger_auto_schema(
        request_body=UpdateKnowledgeSourceInternalJsonSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.INTERNAL_JSON_UPDATE_SUCCESS,
            status.HTTP_400_BAD_REQUEST: "Bad Request: Validation errors or missing required fields."
        },
        operation_summary="Update Internal JSON"
    )
    @action(detail=False, methods=['post'])
    def update_internal_json(self, request):
        """
            method to update internal_json

        """
        serializer = UpdateKnowledgeSourceInternalJsonSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Invalid data for updating internal_json")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        knowledge_source_uuid = data.get(KnowledgeSourceConstants.KNOWLEDGE_SOURCE_UUID)
        pages = data.get(KnowledgeSourceConstants.PAGES)
        self.__knowledge_source_service.update_knowledge_source_internal_json(knowledge_source_uuid, pages)
        return CustomResponse(SuccessMessages.INTERNAL_JSON_UPDATE_SUCCESS)

    @action(detail=False, methods=['post'])
    def editable_internal_json(self, request):
        """
            method to make internal_json as editable
        """
        serializer = EditableInternalJsonSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Invalid data for updating internal_json")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        knowledge_source_uuid = data.get(KnowledgeSourceConstants.KNOWLEDGE_SOURCE_UUID)
        blocks = data.get(KnowledgeSourceConstants.BLOCKS)
        self.__knowledge_source_service.editable_internal_json(knowledge_source_uuid, blocks)

        return CustomResponse(SuccessMessages.INTERNAL_JSON_UPDATE_SUCCESS)

def delete_file_chunks(file, collection_name):
    file_name = file.knowledge_source_name

    chroma_obj.delete_docs_from_collection(
        collection_name=collection_name,
        source_file=file_name
    )


def insert_file_chunks(file, collection_name):
    file.knowledge_source_status = KnowledgeSources.KnowledgeSourceStatus.CHUNKING
    event = {
        'event_type': 'chunking',
        'collection_name': collection_name,
        'file_uuid': str(file.knowledge_source_uuid),
        'file_name': file.knowledge_source_name,
        'file_type': file.knowledge_source_type,
    }
    file.save()

    file_processing_producer.send_event_data_batch(event)


def delete_knowledge_source_chunks(knowledge_source_name, chunk_collection: str):
    
    mvr_collection = 'mvr_' + chunk_collection.removeprefix('cw_')
    
    chroma_obj.delete_docs_from_collection(
        collection_name=mvr_collection,
        source_file=knowledge_source_name
    )
    
    chroma_obj.delete_docs_from_collection(
        collection_name=chunk_collection,
        source_file=knowledge_source_name
    )

def add_knowledge_source_chunks(knowledge_source_uuid, chunk_collection):
    
    file_details = KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).values('knowledge_source_name', 'knowledge_source_type').first()
    
    event = {
        'event_type': 'chunking',
        'collection_name': chunk_collection,
        'file_uuid': str(knowledge_source_uuid),
        'file_name': file_details['knowledge_source_name'],
        'file_type': file_details['knowledge_source_type'],
    }
    file_processing_producer.send_event_data_batch(event)