from abc import ABC, abstractmethod

class IConversationsDao(ABC):
    """
    Interface for Conversations Data Access Object.
    """

    @abstractmethod
    def get_conversation_by_uuid(self, conversation_uuid):
        """
        Fetches a conversation from the database by its UUID.

        Args:
            conversation_uuid (str): The UUID of the conversation.

        Returns:
            Conversation object if found, otherwise None.
        """
        pass

    @abstractmethod
    def update_csr_info(self, conversation, csr_info):
        """
        Updates the csr_info_json field of the conversation in the database.

        Args:
            conversation (ChatConversation): The conversation object.
            csr_info (list): The updated CSR info data.
        """
        pass

    @abstractmethod
    def save_conversation(self, conversation_data):
        """
        Save the conversation data to the database.

        - Fetch foreign key instances from the database.
        - Prepare and save the conversation instance.
        - Handle exceptions for missing foreign key instances and any other errors.
        """
        pass
    
    @abstractmethod
    def get_user_chats(self, customer_uuid: str, user_id: str) -> list[dict]:
        pass

    @abstractmethod
    def save_chat_conversation_instance(self,chat_conversation):
        pass

    @abstractmethod
    def get_latest_conversation_uuid(self,primary_conversation_uuid,secondary_conversation_uuid):
        pass

    @abstractmethod
    def get_latest_message_time(self,conversation_uuid):
        pass

