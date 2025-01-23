from abc import ABC, abstractmethod

class IEmailConversationService(ABC):
    
    @abstractmethod
    def get_email_conversations(self, customer_uuid, application_uuid,user_uuid, validated_data):
        pass
    
    @abstractmethod
    def get_mail_conversation_by_ticket_uuid(self,validated_data):
        pass
    
    @abstractmethod
    def post_order_details_info(self, email_uuid, details_extracted_json, file_path, attachment_id, user_uuid):
        pass

    @abstractmethod
    def get_downloadable_urls(self,validated_data):
        pass

    @abstractmethod
    def delete_draft_mail(self, validated_data):
        pass

    @abstractmethod
    def create_draft_mail(self, customer_uuid, applcation_uuid, user_uuid, validated_data):
        pass

    @abstractmethod
    def reply_to_mail(self, customer_uuid, application_uuid, validated_data):
        pass

    @abstractmethod   
    def get_content_from_url(self, email_body_url):
        pass
    
    @abstractmethod
    def get_mails_by_email_uuids(self,email_uuids_list):
        pass


    @abstractmethod
    def get_mail_conversation_count_by_ticket_uuid(self,ticket_uuid):
        pass
