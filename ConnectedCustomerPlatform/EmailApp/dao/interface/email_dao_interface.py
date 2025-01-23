from abc import ABC, abstractmethod

class EmailDaoInterface(ABC):

    @abstractmethod
    def get_parent_emails(self, email_conversation_uuids):
        pass

    @abstractmethod
    def get_email(self,email_uuid):
        pass

    @abstractmethod
    def delete_draft(self, email_uuid):
        pass

    @abstractmethod
    def save_email(self, email_uuid, email_conversation_uuid, email_flow_status, email_status,dimension_action_json, insert_ts, updated_ts, parent_uuid=None):
        pass
    
    @abstractmethod
    def update_email_conversation_flow_status(self, email_conversation, status):
        pass

    @abstractmethod
    def get_parent_emails_by_tickets(self, email_conversation_uuids):
        pass
    @abstractmethod
    def map_emails_to_primary_conversation(self,primary_conversation_uuid,secondary_conversation_uuid):
        pass

    @abstractmethod
    def get_latest_conversation_uuid(self,conversation_uuids):
        pass

    @abstractmethod
    def get_latest_conversation_time(self, conversation_uuid):
        pass

    @abstractmethod
    def get_emails(self, email_uuids):
        #Get the email objects by email uuids 
        pass
