from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
import logging
from rest_framework.decorators import action
from ConnectedCustomerPlatform.responses import CustomResponse
from ChatBot.services.impl.dimensions_intents_service_impl import DimensionsIntentServiceImpl
from ConnectedCustomerPlatform.utils import Utils
from ChatBot.constant.constants import TagConstants, SwaggerHeadersConstants
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.serializers import DimensionResultSerializer

logger = logging.getLogger(__name__)

class DimensionsIntentViewSet(ViewSet):
    """
    ViewSet for handling intent operations.
    Implements the Singleton pattern to ensure a single instance.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of DimensionsIntentViewSet exists.
        """
        if cls._instance is None:
            cls._instance = super(DimensionsIntentViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the service only once for the singleton instance.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info("Initializing DimensionsIntentViewSet Singleton Instance")
            self.dimensions_intent_service = DimensionsIntentServiceImpl() # Example service instance
            logger.info(f"DimensionsIntentViewSet Singleton Instance ID: {id(self)}")
            self.initialized = True

    @swagger_auto_schema(
        tags=TagConstants.DEPARTMENT_TAG,
        operation_description="Get all departments by application and customer UUID",
        manual_parameters=[SwaggerHeadersConstants.CUSTOMER_UUID_HEADER,
                           SwaggerHeadersConstants.APPLICATION_UUID_HEADER],
        responses={status.HTTP_200_OK:DimensionResultSerializer,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA}
    )
    @action(detail=False, methods=['GET'])
    def get_intent_dimensions(self, request):
        """
        Fetch dimension mapping for the given application_uuid, customer_uuid, and dimension type 'INTENT'
        """
        # Extract and validate headers
        logger.info("Extracting and validating request headers.")
        customer_uuid, application_uuid, _ = Utils.get_headers(request.headers)
        logger.debug(f"Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")

        # Define the dimension type name
        dimension_type_name = "INTENT"
        logger.info(f"Fetching dimensions for dimension type: {dimension_type_name}")

        # Fetch dimensions using the service
        dimensions = self.dimensions_intent_service.get_all_dimensions_by_dimension_type_name(
            dimension_type_name,
            application_uuid,
            customer_uuid
        )
        logger.debug(f"Fetched dimensions: {dimensions}")

        # Step 4: Return dimensions in a custom response format
        return CustomResponse(dimensions)


