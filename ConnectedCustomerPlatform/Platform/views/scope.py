import inspect
import logging

from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from Platform.constant import constants
from Platform.constant import swagger_success_messages
from Platform.constant.success_messages import SuccessMessages
from Platform.utils import get_headers_and_validate, is_valid_uuid
from Platform.services.impl.scope_service_impl import ScopeServiceImpl

logger = logging.getLogger(__name__)


class ScopeViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScopeViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)

            print("Inside ScopeViewSet")
            self.scope_service = ScopeServiceImpl()
            print(f"Inside ScopeViewSet - Singleton Instance ID: {id(self)}")

            self.initialized = True

    @swagger_auto_schema(
        tags=constants.SCOPE_TAG,
        operation_description="API to retrieve all available scope categories.",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        responses={status.HTTP_200_OK: swagger_success_messages.SCOPE_CATEGORIES_RESPONSE_SUCCESS}
    )
    @action(detail=False, methods=['get'])
    def get_scope_categories(self, request):
        """
        API to retrieve all available scope categories.

        :param request: The HTTP request object.
        :return: A JSON response containing a list of scope categories.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        SuccessMessages.UM_SUCCESS_RESPONSE['response'] = ['NON_HIERARCHY']
        return JsonResponse(SuccessMessages.UM_SUCCESS_RESPONSE)

    @swagger_auto_schema(
        tags=constants.SCOPE_TAG,
        operation_description="API to retrieve scope category values based on the provided category.",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        responses={status.HTTP_200_OK: swagger_success_messages.SCOPE_CATEGORY_VALUES_SUCCESS}
    )
    @action(detail=False, methods=['get'])
    def get_scope_category_values(self, request, category):
        """
        API to retrieve scope category values based on the provided category.

        :param request: The HTTP request object.
        :param category: The category of scope (e.g., NON_HIERARCHY).
        :return: A JSON response containing a list of scope category values.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Static response for category values
        SuccessMessages.UM_SUCCESS_RESPONSE['response'] = ['INTENT', 'SENTIMENT', 'CUSTOMER_TIER', 'GEOGRAPHY', 'ENTITY']
        return JsonResponse(SuccessMessages.UM_SUCCESS_RESPONSE)

    @swagger_auto_schema(
        tags=constants.SCOPE_TAG,
        operation_description="Retrieves (CUSTOMER_TIER, INTENT, ENTITY, SENTIMENT or GEOGRAPHY) values",
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        responses={status.HTTP_200_OK: swagger_success_messages.SCOPE_TYPES_VALUES_RESPONSE_SUCCESS}
    )
    @action(detail=False, methods=['get'])
    def get_scope_types_values(self, request, category, scope_type):
        """
        Retrieve scope type values for a given customer and application based on the provided scope type.

        :param request: HTTP request object containing headers with customer and application details.
        :param category: The category to filter by (from URL).
        :param scope_type: The scope type to retrieve values for.
        :return: JsonResponse with success message and the retrieved scope type values.
        """
        logger.info(f"Entering {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")

        # Extract customer_uuid, application_uuid from request headers and validate
        customer_uuid, _, _ = get_headers_and_validate(request.headers)
        application_uuid = request.query_params.get(constants.APPLICATION_UUID)
        if not is_valid_uuid(application_uuid):
            raise CustomException("application_uuid : "+ErrorMessages.NOT_VALID_UUID)
        logger.debug(f"Headers extracted - Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")

        # Fetch scope type values from the service layer
        response_data = self.scope_service.get_scope_type_values(customer_uuid, application_uuid, scope_type)

        logger.info(f"Successfully fetched scope type values for scope type: {scope_type}, customer: {customer_uuid}")
        SuccessMessages.UM_SUCCESS_RESPONSE['response'] = response_data

        return JsonResponse(SuccessMessages.UM_SUCCESS_RESPONSE)