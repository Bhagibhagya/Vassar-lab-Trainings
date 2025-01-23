from abc import ABC, abstractmethod

class ITicketService(ABC):
    
    @abstractmethod
    def get_email_tickets(self, customer_uuid, application_uuid,user_uuid, validated_data):
        pass
