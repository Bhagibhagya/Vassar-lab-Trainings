from abc import ABC, abstractmethod

class UserEmailSettingDaoInterface(ABC):

    @abstractmethod
    def is_user_email_setting_exists(self, customer_uuid, from_email_id, application_uuid):
        pass
    
    @abstractmethod
    def get_primary_email_setting(self, customer_uuid, application_uuid):
        pass

    @abstractmethod
    def get_mail_and_password(self, application_uuid, user_email_filter):
        pass