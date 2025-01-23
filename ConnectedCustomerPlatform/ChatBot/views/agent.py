import inspect
import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action


from ConnectedCustomerPlatform.responses import CustomResponse


from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.constants import TagConstants, SwaggerHeadersConstants


from ChatBot.services.impl.agent_service_impl import AgentServiceImpl

from ChatBot.serializers import UserDetailsSerializer
from ConnectedCustomerPlatform.utils import Utils

logger = logging.getLogger(__name__)


class AgentViewSet(ViewSet):
    """
        ViewSet for managing agents/users of user management provide get methods
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        """
                Ensure that only one instance of the AgentViewSet is created.
                Args:
                    cls: The class reference.
                    *args: Positional arguments for initialization.
                    **kwargs: Keyword arguments for initialization.
                Returns:
                    AgentViewSet: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(AgentViewSet, cls).__new__(cls)
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
            logger.info(f"Inside AgentViewSet - Singleton Instance ID: {id(self)}")
            self.__agent_service = AgentServiceImpl()  # Instantiate the service to handle business logic
            self.initialized = True

    @swagger_auto_schema(
        tags=TagConstants.AGENT_TAG,
        operation_description="Get all agents by application and customer UUID",
        manual_parameters=[SwaggerHeadersConstants.CUSTOMER_UUID_HEADER,
                           SwaggerHeadersConstants.APPLICATION_UUID_HEADER,
                           SwaggerHeadersConstants.USER_UUID_HEADER],
        responses={status.HTTP_200_OK: UserDetailsSerializer(many=True),
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA
                   }
    )
    @action(detail=False, methods=['get'])
    def get_all_online_agents(self, request):
        """
                Method to get all online agents(users from user-management)  by application and customer UUID.
                Parameters:
                    - application-uuid (required): request header
                    - customer_uuid (required): request header
                    - user_uuid (required): request header
                Returns:
                    CustomResponse: List of online agent/user
            """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        customer_uuid, application_uuid, user_uuid = Utils.get_headers(request.headers)
        logger.debug(f"User UUID: {user_uuid}, Customer UUID: {customer_uuid}, Application UUID: {application_uuid}")
        # call agent service method to fetch online users by customer_uuid, application_uuid and to exclude current agent/user by user_uuid
        agent_data = self.__agent_service.get_all_agents_except_current_agent(customer_uuid=customer_uuid,
                                                                              application_uuid=application_uuid,
                                                                              user_uuid=user_uuid)
        logger.debug(f"Successfully retrieved online agents by customer :: {customer_uuid} and application :: {application_uuid}")
        return CustomResponse(agent_data)
