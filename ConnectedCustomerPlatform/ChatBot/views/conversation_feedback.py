import inspect
import os
import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from ChatBot.serializers import ConversationFeedBackSerializer
from ConnectedCustomerPlatform.responses import CustomResponse
from ChatBot.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.services.impl.feedback_service_impl import FeedbackServiceImpl

# Set up a logger for this module
logger = logging.getLogger(__name__)

class ConversationFeedbackView(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConversationFeedbackView, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info("Inside ConversationFeedbackView - Singleton Instance ID: %s", id(self))
            # Initialize the feedback service implementation
            self.feedback_service = FeedbackServiceImpl()
            self.initialized = True

    @swagger_auto_schema(
        operation_description="Submits feedback for a specific chat conversation.",
        request_body=ConversationFeedBackSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.FEEDBACK_SUBMITTED_SUCCESSFULLY,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.INVALID_DATA,
            status.HTTP_404_NOT_FOUND: ErrorMessages.CHAT_CONVERSATION_NOT_FOUND
        }
    )
    @action(detail=False, methods=['post'])
    def chat_conversation_feedback(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} - Request received")
        """
        Handle POST request for submitting conversation feedback.
        :Parameters:
            - chat_conversation_uuid (str): UUID of the conversation for which feedback is submitted.
            - satisfaction_level (str): The level of satisfaction (e.g., "Great", "Average", "Poor").
            - additional_comments (str, optional): Any additional comments provided by the user.
        """
        # Deserialize the incoming request data
        serializer = ConversationFeedBackSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():

            # Process the feedback using the service layer
            self.feedback_service.handle_conversation_feedback(request.data)

            # Return a success response if feedback submission is successful
            logger.info(f"Feedback submitted successfully for chat_conversation UUID: {request.data.get('chat_conversation_uuid')}")
            return CustomResponse(SuccessMessages.FEEDBACK_SUBMITTED_SUCCESSFULLY)
        else:
            # Log validation errors and raise an exception
            logger.error(f"Feedback submission failed due to invalid data: {serializer.errors}")
            raise CustomException(ErrorMessages.INVALID_DATA)