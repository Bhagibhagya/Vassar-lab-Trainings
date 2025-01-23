import inspect
import os
import logging
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action


from ConnectedCustomerPlatform.responses import CustomResponse

from ChatBot.constant.error_messages import ErrorMessages

from ChatBot.constant.constants import TagConstants, SwaggerHeadersConstants
from ChatBot.services.impl.department_service_impl import DepartmentServiceImpl

from ChatBot.serializers import RoleSerializer

from drf_yasg.utils import swagger_auto_schema

from ConnectedCustomerPlatform.utils import Utils

logger = logging.getLogger(__name__)


class DepartmentViewSet(ViewSet):
    """
        ViewSet for managing departments/roles of user management provide get methods
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        """
                Ensure that only one instance of the DepartmentViewSet is created.
                Args:
                    cls: The class reference.
                    *args: Positional arguments for initialization.
                    **kwargs: Keyword arguments for initialization.
                Returns:
                    DepartmentViewSet: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(DepartmentViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
                Initialize the AgentViewSet.
                This method is called only once due to the singleton pattern. It initializes the
                AgentService for handling business logic related to Agents.
                Args:
                    **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.__department_service = DepartmentServiceImpl()
            logger.info(f"Inside DepartmentViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    @swagger_auto_schema(
        tags=TagConstants.DEPARTMENT_TAG,
        operation_description="Get all departments by application and customer UUID",
        manual_parameters=[SwaggerHeadersConstants.CUSTOMER_UUID_HEADER,
                           SwaggerHeadersConstants.APPLICATION_UUID_HEADER],
        responses={status.HTTP_200_OK: RoleSerializer(many=True),
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA}
    )
    @action(detail=False, methods=['get'])
    def get_all_departments(self, request):
        """
                    Method to get all departments(roles from user-management) by application and customer UUID.
                    Parameters:
                        - application-uuid (required): request header
                        - customer_uuid (required): request header
                        - user_uuid (required): request header
                    Returns:
                        CustomResponse: List of department
                    """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        customer_uuid, application_uuid, user_uuid = Utils.get_headers(request.headers)
        logger.debug(f"User UUID: {user_uuid}, Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        # call department service method to fetch departments/roles by customer_uuid, application_uuid
        departments = self.__department_service.get_all_departments(customer_uuid=customer_uuid,
                                                                    application_uuid=application_uuid)

        return CustomResponse(departments)
