from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from drf_yasg import openapi

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException
from ConnectedCustomerPlatform.responses import CustomResponse
from EmailApp.constant.constants import EmailDashboardParams
from EmailApp.utils import validate_uuids_dict
from WiseFlow.serializers import IntentClassificationInputSerializer
from WiseFlow.services.impl.intent_classification_handler_service_impl import IntentClassificationHandlerServiceImpl
import logging
logger = logging.getLogger(__name__)
class IntentClassificationHandlerViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IntentClassificationHandlerViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print(f"Inside EntityViewSet - Singleton Instance ID: {id(self)}")
            self.intent_classification_service = IntentClassificationHandlerServiceImpl()
            self.initialized = True

    @swagger_auto_schema(
        method='post',
        operation_description="API to identify intent and return intent variable.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "selected_intents": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="List of selected intents for classification."
                ),
                "variables": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Variable name."),
                            "value": openapi.Schema(type=openapi.TYPE_STRING, description="Variable value.")
                        },
                    ),
                    description="List of variables to be used in classification."
                )
            },
            required=["selected_intents"],
            description="Payload for intent classification."
        ),
        manual_parameters=[
            openapi.Parameter(
                name=EmailDashboardParams.CUSTOMER_UUID.value,
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="Customer UUID header."
            ),
            openapi.Parameter(
                name=EmailDashboardParams.APPLICATION_UUID.value,
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="Application UUID header."
            )
        ],
        responses={
            200: openapi.Response(
                description="Intent variable identified successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "result": openapi.Schema(type=openapi.TYPE_OBJECT, description="Identified intent variable."),
                        "code": openapi.Schema(type=openapi.TYPE_INTEGER, description="Response status code.")
                    }
                )
            ),
            400: openapi.Response(
                description="Validation error.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error details.")
                    }
                )
            ),
            500: openapi.Response(
                description="Internal server error.",
                schema=openapi.Schema(type=openapi.TYPE_STRING, description="Error message.")
            )
        }
    )
    @action(detail=False, methods=['post'])
    def intent_classification_handler(self, request):
        """identifies intent and returns intent variable"""
        logger.info("In IntentClassificationHandlerViewSet :: intent_classification_handler")
        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value: customer_uuid,
                             EmailDashboardParams.APPLICATION_UUID.value: application_uuid})
        serializer = IntentClassificationInputSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            raise InvalidValueProvidedException(detail=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        intent_variable = self.intent_classification_service.identify_intent_sub_intent(customer_uuid, application_uuid,
                                                serializer.validated_data,request.data.get('selected_intents'),request.data.get('variables'))
        return CustomResponse(result=intent_variable,code=status.HTTP_200_OK)