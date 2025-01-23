import logging
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from Platform.constant import constants
from Platform.serializers import AssignOrganizationSerializer
from Platform.services.impl.assign_organization_service_impl import AssignOrganizationServiceImpl
from Platform .utils import validate_input
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.responses import CustomResponse
from rest_framework import status
from ConnectedCustomerPlatform.exceptions import CustomException

logger = logging.getLogger(__name__)


class AssignOrganizationViewSet(ViewSet):
    """
    ViewSet for managing Assigning of organizations.

    This ViewSet provides methods to add, delete, and retrieve Assigned organizations
    It ensures that only a single instance is created using the Singleton pattern.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the AssignOrganizationViewSet is created.

        Args:
            cls: The class reference.
            *args: Positional arguments for initialization.
            **kwargs: Keyword arguments for initialization.

        Returns:
            AssignOrganizationViewSet: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(AssignOrganizationViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the AssignOrganizationViewSet.

        This method is called only once due to the singleton pattern. It initializes the
        AssignOrganizationService for handling business logic related to Assigning of organizations.

        Args:
            **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.__assign_org_service = AssignOrganizationServiceImpl()  # Instantiate the service to handle business logic
            logger.info(f"Inside AssignOrganizationViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    @action(detail=False, methods=['post'])
    def add_organizations(self, request):
        """
        Handle adding the new organizations for the llm configuration.

        :param request: DRF request object containing the data to add new organizations for the llm configuration.
             Parameters:
                -customer_uuid (required):header
                -user_uuid (required):header
                -payload (request.data):request_body
        :return: Response object with success or error messages.
        """

        logger.info("In assign_organization.py :: :: ::  AssignOrganizationViewSet :: :: :: add_organizations ")

        # Extract customer and user UUID from request headers
        user_uuid = request.headers.get(constants.USER_ID)

        logger.info(f"Attempting to add organizations by user {user_uuid}")

        #  Validate user UUID
        if not validate_input(user_uuid):
            raise CustomException(ErrorMessages.USER_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        # Validate incoming request data using serializer
        serializer = AssignOrganizationSerializer(data=request.data)
        if serializer.is_valid():
            self.__assign_org_service.add_organizations(user_uuid, serializer.validated_data)
            return CustomResponse(SuccessMessages.ADD_ORGANIZATIONS_TO_LLM_CONFIGURATION)
        else:
            logger.error(f"Invalid data for add Organizations: {serializer.errors}")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def get_organizations(self, request):
        """
        Retrieve all organizations for a given LLM configuration.

        :param request: DRF request object containing the customer UUID.
             Parameters:
                -llm_configuration_uuid (required):params
        :return: Response object with a list of configurations.
        """

        logger.info("In assign_organization.py :: :: :: AssignOrganizationViewSet :: :: :: get_organizations ")

        llm_configuration_uuid = request.query_params.get('llm_configuration_uuid')
        # Retrieve LLM configurations using the service layer
        organizations = self.__assign_org_service.get_organizations(llm_configuration_uuid)
        logger.info("Successfully retrieved organizations for the llm configuration")
        return CustomResponse(organizations)
    
    @action(detail=False, methods=['delete'])
    def delete_organization(self, request):
        """
        Remove the organization for a given LLM configuration.

        :param request: DRF request object containing the customer UUID.
             Parameters:
                -llm_configuration_uuid (required):params
        :return: Response object with a list of configurations.
        """

        logger.info("In assign_organization.py :: :: :: AssignOrganizationViewSet :: :: :: delete_organization ")

        llm_configuration_uuid = request.query_params.get('llm_configuration_uuid')
        customer_uuid = request.query_params.get('customer_uuid')
        # Delete the organization for the llm_configuration using the service layer
        self.__assign_org_service.delete_organization(llm_configuration_uuid, customer_uuid)
        logger.info(f"Successfully deleted organization {customer_uuid}")
        return CustomResponse(SuccessMessages.DELETE_ORGANIZATION_SUCCESS)
    
    @action(detail=False, methods=['get'])
    def get_organization_by_id(self, request, customer_uuid):
        """
        Retrieve details of an organization based on the customer UUID.

        This endpoint allows clients to fetch organization details associated with a specific
        customer UUID. Optionally, it can filter results based on a specified communication channel.

        :param request: DRF request object containing query parameters.
                        Expected query parameters:
                        - channel (optional): The communication channel to filter the organization details.
                        - customer_uuid: The UUID of the customer organization for which to retrieve details.
        :param customer_uuid: The UUID of the organization whose details are being requested.
        :return: Response object containing the organization details.
                If a channel is provided, returns filtered organization details; otherwise, returns all details.
        """
        channel = request.query_params.get('channel')
        organization_details = self.__assign_org_service.get_organization_by_id(customer_uuid,channel)
        logger.info("Successfully retrieved organization details")
        return CustomResponse(organization_details)