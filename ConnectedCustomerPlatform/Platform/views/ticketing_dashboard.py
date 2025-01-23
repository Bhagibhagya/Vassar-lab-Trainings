from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from Platform.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException
from EmailApp.utils import validate_uuids_dict
from Platform.serializers import TicketParamsSerializer
from Platform.services.impl.ticket_service_impl import TicketServiceImpl
from Platform.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.constant import constants
from rest_framework import status as http_status
from rest_framework import status


import logging

from Platform.utils import validate_input, get_headers_and_validate

logger = logging.getLogger(__name__)


class TicketViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TicketViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.ticket_service = TicketServiceImpl()
            self.initialized = True

    @action(detail=False, methods=['post'])
    def get_tickets(self, request):
        """
        API endpoint to retrieve tickets for a specific customer and application and assigned to specific user.

        This method processes a POST request to fetch ticket information based on the 
        provided customer UUID and application UUID. It validates the UUIDs extracted 
        from the request headers, deserializes the request data, and invokes the 
        unified activity service to fetch the relevant tickets.

        """
        # Log the entry into the get_tickets API method
        logger.info(" In TicketViewSet inside get_tickets api")

        # Extract customer UUID, application UUID, and user UUID from request headers
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)
        application_uuid = request.headers.get(constants.APPLICATION_UUID)
        user_uuid = request.headers.get(constants.USER_ID)

        # Validate the extracted UUIDs to ensure they are in the correct format
        validate_uuids_dict({
            constants.APPLICATION_UUID:application_uuid,
            constants.CUSTOMER_UUID:customer_uuid,
            constants.USER_ID : user_uuid
        })

        # Deserialize the request data using UnifiedActivityParamsSerializer
        serializer = TicketParamsSerializer(data=request.data)
        
        # Check if the serializer is valid; if not, raise a custom exception with error details
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=http_status.HTTP_400_BAD_REQUEST)
        
        # Call the service layer to get tickets based on validated data
        response_data = self.ticket_service.get_tickets(customer_uuid, application_uuid,user_uuid, serializer.validated_data)

        # Return a custom response with the result data
        return CustomResponse(result=response_data)
    
    @action(detail=False, methods=['get'])
    def get_filters(self, request):
        """
        API endpoint to retrieve filter options for unified activity data.

        This endpoint allows clients to fetch distinct filter values such as status, client names,
        email IDs, intents, and channels based on the provided customer and application UUIDs.
        
        """
        logger.info(" In TicketViewSet inside get_filters api")
        # Retrieve UUIDs from the request headers
        customer_uuid = request.headers.get(constants.CUSTOMER_UUID)
        application_uuid = request.headers.get(constants.APPLICATION_UUID)
        user_uuid = request.headers.get(constants.USER_ID)

        # Validate the provided UUIDs for the application and customer
        validate_uuids_dict({
            constants.APPLICATION_UUID:application_uuid,
            constants.CUSTOMER_UUID:customer_uuid,
            constants.USER_ID : user_uuid
        })
        
        # Deserialize and validate query parameters using the serializer
        serializer = TicketParamsSerializer(data=request.query_params)

        if not serializer.is_valid():
            # Raise an exception if the serializer is not valid, returning the errors
            raise CustomException(serializer.errors, status_code=http_status.HTTP_400_BAD_REQUEST)
        
        # Call the service layer to get the filter values based on validated data
        response_data = self.ticket_service.get_filters(customer_uuid, application_uuid,user_uuid, serializer.validated_data)

        # Return a custom response containing the result data
        return CustomResponse(result=response_data)

    @action(detail=False, methods=['get'])
    def mark_email_as_read(self, request):
        logger.info(" In TicketViewSet inside mark_email_as_read api")
        # Call the service layer to get the filter values based on validated data
        ticket_uuid = request.query_params.get(constants.TICKET_UUID)
        is_read = request.query_params.get(constants.IS_READ)
        user_uuid = request.headers.get(constants.USER_ID)


        # Validate is_read
        if is_read is None or is_read.lower() not in ['true', 'false']:
            raise ResourceNotFoundException(ErrorMessages.INVALID_IS_READ_VALUE)  # Replace with your custom exception if needed
        
        # Convert is_read to boolean
        is_read = is_read.lower() == 'true'
        if ticket_uuid is None:
            raise ResourceNotFoundException(ErrorMessages.TICKET_UUID_NULL_ERROR)
        
        self.ticket_service.update_is_read_status(ticket_uuid,is_read,user_uuid)

        # Return a custom response containing the result data
        logger.info("Successfully marked email as read")
        return CustomResponse(SuccessMessages.MARK_EMAIL_AS_READ)

    @action(detail=False, methods=['get'])
    def merge_tickets(self,request):
        """
            API to merge the two different tickets based on channel
        """
        logger.info("In ticketing_dashboard.py :: :: :: TicketViewSet :: :: :: merge_tickets ")

        # Get ticket uuids from query params
        primary_ticket_uuid = request.query_params.get(constants.PRIMARY_TICKET_UUID)
        secondary_ticket_uuid = request.query_params.get(constants.SECONDARY_TICKET_UUID)
        if not validate_input(primary_ticket_uuid):
            logger.error("Primary ticket found null")
            raise CustomException(ErrorMessages.PRIMARY_TICKET_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        if not validate_input(secondary_ticket_uuid):
            logger.error("Secondary ticket found null")
            raise CustomException(ErrorMessages.SECONDARY_TICKET_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # calling service for merge tickets
        self.ticket_service.merge_tickets(primary_ticket_uuid,secondary_ticket_uuid,customer_uuid,application_uuid,user_uuid)

        # Return a custom response containing the result data
        logger.info("Successfully merged the tickets")
        return CustomResponse(SuccessMessages.MERGED_SUCCESSFULLY)

    @action(detail=False, methods=['get'])
    def get_ticket_dropdown(self,request):
        """
            API to get tickets for dropdown while merging
        """
        logger.info("In ticketing_dashboard.py :: :: :: TicketViewSet :: :: :: get_ticket_dropdown ")

        # Get headers
        customer_uuid, application_uuid, user_uuid = get_headers_and_validate(request.headers)

        # call the Service to get the tickets
        result = self.ticket_service.get_ticket_dropdown(customer_uuid,application_uuid,user_uuid)

        # Return a custom response containing the result data
        return CustomResponse(result=result)


    def get_merged_conversation(self,request):
        """
            API to get the Merged conversation by ticket_uuid
        """
        logger.info("In ticketing_dashboard.py :: :: ::  TicketViewSet :: :: :: get_merged_conversation")

        ticket_uuid = request.query_params.get(constants.TICKET_UUID)

        if ticket_uuid is None:
            raise CustomException(ErrorMessages.TICKET_UUID_NULL_ERROR)

        response_data = self.ticket_service.get_merged_conversation_by_ticket_uuid(ticket_uuid)

        return CustomResponse(result=response_data, code=status.HTTP_200_OK)
