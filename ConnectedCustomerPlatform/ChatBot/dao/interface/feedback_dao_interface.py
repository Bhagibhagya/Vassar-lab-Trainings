from abc import ABC, abstractmethod
from DatabaseApp.models import ChatConversation

class FeedbackDAOInterface(ABC):
    @abstractmethod
    def get_conversation_by_uuid(self, chat_conversation_uuid: str):
        """Fetch a conversation by its UUID."""


    @abstractmethod
    def save_chat_conversation(self, chat_conversation: ChatConversation, feedback_data: dict):
        """save the feedback data in conversation."""