from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import status
import json

from ChatBot.constant.constants import Constants
from Platform.constant import constants
from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from ChatBot.services.impl.entity_service_impl import EntityServiceImpl
from ChatBot.serializers import AssignEntitySerializer, EntityPaginationSerializer, EntitySerializer
from Platform.serializers import PagiNationSerializer
from Platform.utils import get_headers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from Platform.utils import get_headers_and_validate


# Configure logger
logger = logging.getLogger(__name__)

class EntityViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EntityViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.__entity_service = EntityServiceImpl()
            self.initialized = True

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='page_number', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='page_number'),
            openapi.Parameter(name='total_entries_per_page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='total_entries_per_page'),
            constants.application_uuid_header, constants.customer_uuid_header
        ],
        responses={status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=["get"])
    def get_entities(self, request):
        logger.info("EntityViewSet: Fetching entities for the application.")
        """
        Retrieves entities associated with a specific application and their attributes,
        including mapped file count.

        Parameters:
            - request: HTTP request object
        """
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)

        logger.debug(f"Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        serializer = EntityPaginationSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(f"Invalid query parameters: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        response = self.__entity_service.get_entities_by_customer_and_application(customer_uuid, application_uuid, user_uuid, serializer.validated_data)

        logger.info("Entities fetched successfully.")
        return CustomResponse(result=response)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="entity_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_404_NOT_FOUND: ErrorMessages.ENTITY_NOT_FOUND
        }
    )
    @action(detail=False, methods=["get"])
    def get_entity(self, request, entity_uuid):
        logger.debug(f"EntityViewSet: Fetching entity details for the entity: {entity_uuid}")
        """
        Retrieves entity details of given entity_uuid 

        Parameters:
            - request: HTTP request object
            - entity_uuid: uuid of entity
        """

        response = self.__entity_service.get_entity_details(entity_uuid)

        logger.info("Entities fetched successfully.")
        return CustomResponse(result=response)

    @swagger_auto_schema(
        request_body=EntitySerializer,
        manual_parameters=[constants.application_uuid_header, constants.customer_uuid_header],
        responses={
            status.HTTP_201_CREATED: SuccessMessages.ENTITY_CREATED_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=["post"])
    def add_entity(self, request):
        logger.info("EntityViewSet: Adding a new entity.")
        """
        Adds a new entity to an application.

        Parameters:
            - request: HTTP request object containing JSON data for the new entity
        """
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)

        serializer = EntitySerializer(data=json.loads(request.body), status=Constants.ADD)
        if not serializer.is_valid(raise_exception=True):
            logger.error(f"Entity addition failed due to invalid data: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        entity = serializer.validated_data

        logger.debug(f"User UUID: {user_uuid}, Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        self.__entity_service.add_entity(entity, customer_uuid, application_uuid, user_uuid)

        logger.info("Entity added successfully.")
        return CustomResponse(result=SuccessMessages.ENTITY_CREATED_SUCCESS, code=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="entity_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_200_OK: SuccessMessages.ENTITY_DELETED_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=["delete"])
    def delete_entity(self, request, entity_uuid):
        logger.info(f"EntityViewSet: Deleting entity with UUID {entity_uuid}.")
        """
        Deletes an entity and unassigns associated files.

        Parameters:
            - request: HTTP request object containing the UUID of the entity to delete
        """
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)

        logger.debug(f"Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        self.__entity_service.delete_entity(entity_uuid, customer_uuid, application_uuid, user_uuid)

        logger.info("Entity deleted successfully.")
        return CustomResponse(result=SuccessMessages.ENTITY_DELETED_SUCCESS)

    @swagger_auto_schema(
        request_body=EntitySerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.ENTITY_UPDATED_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['put'])
    def update_entity(self, request):
        logger.info("EntityViewSet: Updating entity.")
        """
        Updates an entity's attributes and description.

        Parameters:
            - request: HTTP request object containing data for updating the entity
        """
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        serializer = EntitySerializer(data=request.data, status=Constants.EDIT)
        if not serializer.is_valid():
            logger.error(f"Entity update failed due to invalid data: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        entity = serializer.validated_data

        logger.debug(f"User UUID: {user_uuid}, Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        self.__entity_service.update_entity(entity, customer_uuid, application_uuid, user_uuid)

        logger.info("Entity updated successfully.")
        return CustomResponse(SuccessMessages.ENTITY_UPDATED_SUCCESS)

    @swagger_auto_schema(
        request_body=AssignEntitySerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.UPDATE_KNOWLEDGE_SOURCE_ENTITY_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=["put"])
    def update_knowledge_source_entity_assignment(self, request):
        logger.info("In entity.py :: :: :: EntityViewSet :: :: :: update_knowledge_source_entity_assignment")
        """
        Assigns and unassigns a entity (entity) to a knowledge_source.

        Parameters:
            - request: HTTP request object
            - knowledge_source_uuid: UUID of the file to assign the entity to
            - entity_uuid: UUID of the entity to be assigned
            - attributes: JSON object containing the attributes to be assigned
            - prev_entity_uuid: UUID of the entity to be unassigned
            - entity_assignment_status: choice field stating assign or unassign 
        """
        customer_uuid, application_uuid,user_uuid=get_headers_and_validate(request.headers)
        serializer = AssignEntitySerializer(data=json.loads(request.body))
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        self.__entity_service.update_knowledge_source_entity_assignment(data, customer_uuid, application_uuid, user_uuid)

        return CustomResponse(result=SuccessMessages.UPDATE_KNOWLEDGE_SOURCE_ENTITY_SUCCESS)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name="entity_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_number', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='page_number'),
            openapi.Parameter(name='total_entries_per_page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='total_entries_per_page')

        ],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=["get"])
    def get_knowledge_sources_by_entity(self, request, entity_uuid):
        logger.info(f"EntityViewSet: fetching file with entity UUID {entity_uuid}.")
        """
        gets list of file with given entity.

        Parameters:
            - request: HTTP request object
        """
        customer_uuid, application_uuid, _ = get_headers(request.headers)
        serializer = PagiNationSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(f"Entity update failed due to invalid data: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        response = self.__entity_service.get_knowledge_sources_by_entity_uuid(entity_uuid, customer_uuid, application_uuid, data)

        logger.info("fetched files successfully.")
        return CustomResponse(response)   
        
        
    



    


    