import inspect
import logging
import os
from ChatBot.constant.constants import Constants
from ChatBot.services.interface.feedback_service_interface import FeedbackServiceInterface
from ChatBot.dao.impl.feedback_dao_impl import FeedbackDAOImpl
from ChatBot.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException

logger = logging.getLogger(__name__)

class FeedbackServiceImpl(FeedbackServiceInterface):
    _instance = None  # Class variable to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FeedbackServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.feedback_dao = FeedbackDAOImpl()
            logger.info("Inside FeedbackServiceImpl - Singleton Instance ID: %s", id(self))
            self.initialized = True

    def handle_conversation_feedback(self, data):
        # Log the start of the feedback handling process
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Check if the conversation exists using DAO
        chat_conversation = self.feedback_dao.get_conversation_by_uuid(data.get("chat_conversation_uuid"))
        if chat_conversation is None:
            raise ResourceNotFoundException(ErrorMessages.CHAT_CONVERSATION_NOT_FOUND)

        # Prepare the feedback data
        feedback_data = {
            Constants.SATISFACTION_LEVEL: data.get("satisfaction_level"),
            Constants.ADDITIONAL_COMMENTS: data.get("additional_comments"),
        }

        logger.info(f"Feedback data prepared: {feedback_data}")

        # Update the conversation feedback using DAO
        chat_conversation.conversation_feedback_transaction_json = feedback_data
        self.feedback_dao.save_chat_conversation(chat_conversation, feedback_data)