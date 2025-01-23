from abc import ABC, abstractmethod

class EmailInfoDaoInterface(ABC):

    @abstractmethod
    def get_conversation_info(self, email_uuid):
        pass

    @abstractmethod
    def get_email_info(self, email_uuid):
        pass
        
    @abstractmethod
    def get_email_info_attachments(self, email_uuid):
        pass

    @abstractmethod
    def save_verified(self, email_uuid):
        pass
    
    @abstractmethod
    def save_email_info(self, email, email_info_json):
        pass