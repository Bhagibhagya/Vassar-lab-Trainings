import inspect
import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException, CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from ConnectedCustomerPlatform.utils import Utils
from EmailApp.constant.constants import EmailDashboardParams
from EmailApp.constant.swagger_constants import ChromaDBSwaggerParams, entity_uuid_param
from EmailApp.utils import validate_uuids_dict
from WiseFlow.constants.success_messages import EntitySuccessMessages
from WiseFlow.serializers import EntityExamplesRequestPayloadSerializer, WiseflowEntityRequestPayloadSerializer, \
    GetEntitiesRequestPayloadSerializer, TestEntityPromptRequestPayloadSerializer, EditEntityPayloadSerializer
from WiseFlow.services.impl.entity_service_impl import EntityServiceImpl

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
            print(f"Inside EntityViewSet - Singleton Instance ID: {id(self)}")
            self.entity_service = EntityServiceImpl()
            self.initialized = True

    @swagger_auto_schema(
        method='post',
        operation_description="API to add entity examples to chroma db.",
        request_body=EntityExamplesRequestPayloadSerializer,
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER],
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['post'])
    def add_entity_examples(self, request):
        """adds the examples to chroma vector db"""
        logger.info("In EntityViewSet :: add_entity_examples")
        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value: customer_uuid,
                             EmailDashboardParams.APPLICATION_UUID.value: application_uuid})
        serializer = EntityExamplesRequestPayloadSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            raise InvalidValueProvidedException(detail=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        self.entity_service.add_entity_examples(customer_uuid, application_uuid,
                                                                  serializer.validated_data)
        return CustomResponse(result=EntitySuccessMessages.EXAMPLES_ADDED_SUCCESS,
                              code=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        operation_description="API to test entity prompts",
        request_body=TestEntityPromptRequestPayloadSerializer,
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER],
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['post'])
    def test_entity_prompt(self,request):
        """API to test entity prompt"""
        logger.info("In EntityViewSet :: test_entity_prompt")
        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value: customer_uuid,
                             EmailDashboardParams.APPLICATION_UUID.value: application_uuid})
        serializer = TestEntityPromptRequestPayloadSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            raise InvalidValueProvidedException(detail=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        prompt_result=self.entity_service.test_entity_prompt(customer_uuid, application_uuid,
                                                serializer.validated_data)
        return CustomResponse(result=prompt_result,
                              code=status.HTTP_200_OK)


    @swagger_auto_schema(
        method='post',
        operation_description="API to create custom entity",
        request_body=WiseflowEntityRequestPayloadSerializer,
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER
        ],
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['POST'])
    def create_entity(self, request):
        """
            creates an entity in database and store examples in chromadb
            Args:
                request (django request): request object
            Returns:
                Dict: created entity_uuid, entity_name and success message
        """
        logger.info(f"Inside {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = Utils.get_headers(request.headers)
        # Validate dimension data
        serializer = WiseflowEntityRequestPayloadSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            raise InvalidValueProvidedException(detail=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        create_entity_result = self.entity_service.create_wiseflow_entity(customer_uuid=customer_uuid, application_uuid=application_uuid, user_uuid=user_uuid, data=serializer.validated_data)
        return CustomResponse(result=create_entity_result, code=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        operation_description="API to fetch all entities",
        request_body=GetEntitiesRequestPayloadSerializer,
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER
        ],
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['POST'])
    def get_entities(self, request):
        """
            Api to fetch all entities under customer and application
            Args:
                request (django request): request object
            Returns:
                List[dict]: entities data
        """
        logger.info(f"Inside {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = Utils.get_headers(request.headers)
        serializer = GetEntitiesRequestPayloadSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            raise InvalidValueProvidedException(detail=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        response_data = self.entity_service.get_wiseflow_entities(customer_uuid=customer_uuid, application_uuid=application_uuid, validated_data=serializer.validated_data)
        return CustomResponse(result=response_data, code=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        operation_description="API to fetch a particular entity",
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER,
            entity_uuid_param
        ],
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['GET'])
    def get_entity(self, request, entity_uuid):
        """
            Api to fetch a particular entity by entity_uuid
            Args:
                request (django request): request object
                entity_uuid (str): unique identifier of entity
            Returns:
                Dict: entity data
        """
        logger.info(f"Inside {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")
        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = Utils.get_headers(request.headers)
        response_data = self.entity_service.get_entity_by_entity_uuid(entity_uuid=entity_uuid, customer_uuid=customer_uuid, application_uuid=application_uuid)
        return CustomResponse(result=response_data, code=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='delete',
        operation_description="API to delete an entity",
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER,
            entity_uuid_param
        ],
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_entity(self, request, entity_uuid):
        """
            Api to delete a particular entity by entity_uuid
            Args:
                request (django request): request object
                entity_uuid (str): unique identifier of entity
            Returns:
                success message (str): Entity deleted successfully
        """
        logger.info(f"Inside {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")
        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = Utils.get_headers(request.headers)
        self.entity_service.delete_wiseflow_entity(customer_uuid=customer_uuid, application_uuid=application_uuid, entity_uuid=entity_uuid)
        # Return a success response.
        logger.info(f"entity deleted successfully for customer {customer_uuid} and application {application_uuid}")
        return CustomResponse(result=EntitySuccessMessages.ENTITY_DELETE_SUCCESS, code=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='put',
        operation_description="API to update entity",
        request_body=EditEntityPayloadSerializer,
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER
        ],
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['PUT'])
    def update_entity(self, request):
        """
            Api to update a particular entity by entity_uuid
            Args:
                request (django request): request object
            Returns:
                success message (str): entity updated successfully
        """
        logger.info(f"Inside {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")
        # Extract user information from headers
        customer_uuid, application_uuid, user_uuid = Utils.get_headers(request.headers)
        serializer = EditEntityPayloadSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            raise InvalidValueProvidedException(detail=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        self.entity_service.update_entity(customer_uuid=customer_uuid, application_uuid=application_uuid, validated_data=data)
        return CustomResponse(result=EntitySuccessMessages.ENTITY_UPDATED_SUCCESS, code=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        operation_description="API to fetch all parent entities",
        responses={
            200: openapi.Response(status.HTTP_200_OK, openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response(status.HTTP_400_BAD_REQUEST, openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(status.HTTP_500_INTERNAL_SERVER_ERROR, openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    @action(detail=False, methods=['GET'])
    def get_parent_entities(self, request):
        """
            Api to fetch parent entities
            Args:
                request (django request): request object
            Returns:
                list[dict]: parent entities data
        """
        logger.info(f"Inside {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")
        response_data = self.entity_service.get_parent_entities()
        return CustomResponse(result=response_data, code=status.HTTP_200_OK)