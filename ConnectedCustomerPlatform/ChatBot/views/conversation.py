import logging

from drf_yasg.utils import swagger_auto_schema
from ChatBot.serializers import ConversationHistorySerializer, SummarySerializer
from ChatBot.utils import validate_input
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.constants import Constants, AgentDashboardConstants, SwaggerHeadersConstants, TagConstants
from ChatBot.utils import get_redis_connection
from ConnectedCustomerPlatform.responses import CustomResponse
from ChatBot.services.impl.conversation_service_impl import ConversationServiceImpl
logger = logging.getLogger(__name__)

class ConversationViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConversationViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        # Ensure __init__ is only called once
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            self.redis = get_redis_connection()
            self.conversation_service_impl = ConversationServiceImpl()
            self.initialized = True

    @action(detail=False, methods=[Constants.PUT])
    def update_conversation_status(self, request, conversation_uuid, csr_uid, csr_status):
        """
        Update the status of a CSR in a conversation.
        """
        logger.info("In AgentDashboardViewSet::update_conversation_status")

        # Validate input
        if not all([conversation_uuid, csr_uid, csr_status]):
            raise CustomException(ErrorMessages.INVALID_INPUT, status_code=status.HTTP_400_BAD_REQUEST)

        # Validate csr_status
        if csr_status not in AgentDashboardConstants.VALID_CSR_STATUS:
            raise CustomException(ErrorMessages.INVALID_CSR_STATUS, status_code=status.HTTP_400_BAD_REQUEST)

        # Delegate to service class to handle Redis and DB operations
        if self.conversation_service_impl.update_conversation_status(conversation_uuid, csr_uid, csr_status):
            return CustomResponse(SuccessMessages.CONVERSATION_STATUS_UPDATED)

        raise CustomException(ErrorMessages.CSR_ID_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=[Constants.GET])
    def ongoing_conversations_list(self, request, csr_uid):
        """
        Retrieve a list of ongoing conversations for a specific CSR.
        
        Args:
            request (Request): Contains the csr_uid as a query parameter.
        
        Returns:
            Response: A list of ongoing conversations.
        """
        logger.info("In AgentDashboardViewSet::ongoing_conversations_list")
        
        # Validate CSR UID
        if csr_uid is None:
            raise CustomException(ErrorMessages.CSR_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        ongoing_conversations = self.conversation_service_impl.get_ongoing_conversations(csr_uid)
        
        return CustomResponse(ongoing_conversations)


    @action(detail=False, methods=[Constants.GET])
    def conversation_history_details(self, request, conversation_uuid):
        """
        Retrieve the conversation history details.

        Args:
            request (Request): Contains the conversation UUID as a query parameter.

        Returns:
            Response: A list of message details with updated media URLs.
        """
        logger.info("In AgentDashboardViewSet::conversation_history_details")

        if not validate_input(conversation_uuid):
            raise CustomException(ErrorMessages.CONVERSATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        message_details = self.conversation_service_impl.get_conversation_history_details(conversation_uuid)
        
        return CustomResponse(message_details)


    @action(detail=False, methods=[Constants.GET])
    def total_conversation_information(self, request, conversation_uuid):
        """
        Retrieve total conversation information.

        Args:
            request (Request): The HTTP request containing the conversation UUID.

        Returns:
            Response: The conversation summary, intents, sentiment, and other data.
        """
        logger.info("In AgentDashboardViewSet::total_conversation_information")

        if not validate_input(conversation_uuid):
            raise CustomException(ErrorMessages.CONVERSATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        conversation_info = self.conversation_service_impl.get_total_conversation_information(conversation_uuid)
        return CustomResponse(conversation_info)

    @swagger_auto_schema(
        tags=TagConstants.HISTORY_TAG,
        operation_description="Retrieve the conversation history for a given ticket UUID.",
        responses={status.HTTP_200_OK:ConversationHistorySerializer,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.CHAT_CONVERSATION_NOT_FOUND}
    )
    @action(detail=False, methods=[Constants.GET])
    def conversation_history(self,request,ticket_uuid):
        """
        Retrieve the conversation history for a given ticket UUID.

        This API endpoint validates the provided ticket UUID and fetches the corresponding
        conversation history using the `conversation_service_impl` service.

        Args:
            request (HttpRequest): The incoming HTTP request object.
            ticket_uuid (str): The unique identifier for the ticket.

        Returns:
            Response: A custom response containing the message details of the conversation.
        """
        if not validate_input(ticket_uuid):
            raise CustomException(ErrorMessages.TICKET_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        message_details = self.conversation_service_impl.get_conversation_history_by_ticket_uuid(ticket_uuid)
        return CustomResponse(message_details)

    @swagger_auto_schema(
        tags=TagConstants.HISTORY_TAG,
        operation_description="Retrieve the total conversation information for a given ticket UUID.",
        responses={status.HTTP_200_OK:SummarySerializer,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.CHAT_CONVERSATION_NOT_FOUND}
    )
    @action(detail=False, methods=[Constants.GET])
    def total_conversation_information_by_ticket_uuid(self,request,ticket_uuid):
        """
        Retrieve the total conversation information for a given ticket UUID.
        Args:
            request (Request): The API request object.
            ticket_uuid (str): The unique identifier for the ticket.
        Returns:
            Response: A `CustomResponse` containing the total conversation information.
        """
        if not validate_input(ticket_uuid):
            raise CustomException(ErrorMessages.TICKET_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        conversation_info = self.conversation_service_impl.get_total_conversation_information_by_ticket_uuid(ticket_uuid=ticket_uuid)
        return CustomResponse(conversation_info)