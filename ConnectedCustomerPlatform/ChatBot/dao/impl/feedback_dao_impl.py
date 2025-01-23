import inspect
import logging
from DatabaseApp.models import ChatConversation
from ChatBot.dao.interface.feedback_dao_interface import FeedbackDAOInterface


logger = logging.getLogger(__name__)
class FeedbackDAOImpl(FeedbackDAOInterface):
    def get_conversation_by_uuid(self, chat_conversation_uuid: str):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        """Fetch a chat_conversation by its UUID."""

        chat_conversation = ChatConversation.objects.filter(chat_conversation_uuid=chat_conversation_uuid).first()

        return chat_conversation


    def save_chat_conversation(self, chat_conversation: ChatConversation, feedback_data: dict):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        """Update the feedback data for a conversation."""
        chat_conversation.save()