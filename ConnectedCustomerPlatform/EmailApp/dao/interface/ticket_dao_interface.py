from abc import ABC, abstractmethod

class TicketDaoInterface(ABC):

    @abstractmethod
    def query_email_tickets(self, customer_uuid, application_uuid,user_uuid, validated_data):
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
    def update_ticket_status(self,ticket_uuid,status) -> None:
        """
        Updates status of the Ticket
        Args:
            ticket_uuid:
            status:

        Returns: True if successfully updated

        """
        pass
