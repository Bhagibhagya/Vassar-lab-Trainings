from abc import ABC, abstractmethod

class FeedbackServiceInterface(ABC):


    @abstractmethod
    def handle_conversation_feedback(self, data):
        """Submit user rating for a conversation."""