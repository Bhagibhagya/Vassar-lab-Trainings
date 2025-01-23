from abc import ABC, abstractmethod

class EmailConversationDaoInterface(ABC):

    @abstractmethod
    def query_email_conversation(self, customer_uuid, application_uuid, validated_data):
        pass

    @abstractmethod
    def get_parent_emails(self,email_conversation_uuids):
        pass

    @abstractmethod
    def get_conversation_info(self, email_uuid):
        pass

    @abstractmethod
    def get_dimension(self,dimension_uuid):
        pass
    
    @abstractmethod
    def get_emails_by_conversation_uuid(self, email_conversation_uuid):
        pass

    @abstractmethod
    def get_email_conversation_create_draft_mail(self, email_conversation_uuid):
        pass

    @abstractmethod
    def get_email_info_order_details(self, email_uuid):
        pass
    
    @abstractmethod
    def get_email_info_attachments(self, email_uuid):
        pass
    
    @abstractmethod
    def get_email(self,email_uuid):
        pass
    
    @abstractmethod
    def get_step_details(self, step_uuid):
        pass
    
    @abstractmethod
    def save_verified(self, email_uuid):
        pass
    
    @abstractmethod
    def get_email_conversation_queryset(self,email_conversation_queryset):
        pass

    @abstractmethod
    def delete_draft(self, email_uuid):
        pass

    @abstractmethod
    def get_user_email_setting(self, customer_uuid, from_email_id, application_uuid):
        pass

    @abstractmethod
    def get_primary_email_setting(self, customer_uuid, application_uuid):
        pass

    @abstractmethod
    def get_customer_name(self, customer_uuid):
        pass

    @abstractmethod
    def get_user(self, user_uuid):
        pass

    @abstractmethod
    def get_email_conversation_uuid_from_email_uuid(self, in_reply_to):
        pass

    @abstractmethod
    def get_parent_email_create_draft_mail(self, in_reply_to):
        pass

    @abstractmethod
    def save_email_conversation_to_db(self, email_conversation_uuid, customer_uuid, customer_client_uuid, email_conversation_flow_status,email_activity, inserted_ts, updated_ts,application_uuid):
        pass

    @abstractmethod  
    def save_email_data(self, email_conversation_uuid, email_uuid, email_subject, email_flow_status, email_status,email_info_json, dimension_action_json, insert_ts, updated_ts, parent_uuid):
        pass
    
    @abstractmethod  
    def save_email_info(self, email, email_info_json):
        pass
    
    @abstractmethod
    def update_email_conversation_data(self, email_conversation_obj):
        pass
    
    @abstractmethod
    def get_email_conversation(self, email_conversation_uuid):
        pass