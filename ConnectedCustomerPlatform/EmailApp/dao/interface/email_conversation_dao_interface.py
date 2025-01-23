from abc import ABC, abstractmethod

class EmailConversationDaoInterface(ABC):

    @abstractmethod
    def get_email_conversation_by_email_uuid(self, email_uuid):
        pass

    @abstractmethod
    def save_email_conversation(self, email_conversation_uuid, customer_uuid, customer_client_uuid, email_conversation_flow_status, email_activity=None, inserted_ts=None, updated_ts=None, application_uuid=None):
        pass

    @abstractmethod
    def get_email_conversation(self, email_conversation_uuid):
        pass

    @abstractmethod
    def update_email_conversation(self, email_conversation_obj):
        pass
    
    @abstractmethod
    def get_email_conversation_obj(self, email_conversation_uuid):
        pass

    @abstractmethod
    def update_email_flow_status(self, parent_email_obj, status):
        pass

    @abstractmethod
    def update_email_activity_in_email_conversation(self, conversation_uuid,email_activity):
        pass

    @abstractmethod
    def get_email_conversation_by_ticket_uuid(self, ticket_uuid):
        pass
    def update_timeline(self, email_conversation_uuid: str, email_activity: dict, email_uuid: str, status: str, timestamp, user_uuid):
        """
        Update the timeline of an email conversation in the new dictionary format.

        This method updates the timeline for a specific email identified by
        the email_uuid within a conversation identified by email_conversation_uuid.

        Parameters:
        - email_conversation_uuid (str): EmailConversation uuid.
        - email_activity (dict): email_activity of email_conversation
        - email_uuid (str): The UUID of the email whose status is being updated.
        - status (str): The status to set for the email (e.g., 'sent', 'received').
        - timestamp: The timestamp to associate with the given status.
        - user (str, optional): The user performing the operation.

        Returns:
        - Updated email_activity (dict) or None if an error occurs.
        """
        pass
    
    @abstractmethod
    def update_timestamp(self, ticket_obj, updated_ts):
        """
        Updates the `updated_ts` field of the given Ticket object.
        
        Args:
            ticket_obj (Ticket): The Ticket object to update.
            updated_ts (datetime): The timestamp to set in the `updated_ts` field.
        """

    @abstractmethod
    def get_email_conversation_by_ticket_id(self, ticket_uuid):
        pass

    @abstractmethod
    def save_email_conversation_instance(self,email_conversation,user_uuid):
        pass
