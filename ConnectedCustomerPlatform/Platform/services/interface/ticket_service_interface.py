from abc import ABC, abstractmethod

class TicketInterface(ABC):

    @abstractmethod
    def get_tickets(self, customer_uuid, application_uuid,user_uuid, validated_data):
        """
         Get Tickets inside a customer, application and assigned to particular user based on provided filters

         Parameters:
             customer_uuid : The UUID of the customer
            application_uuid : The UUID of the application
            user_uuid : The UUID of the user
            validated_data: filters from payload

        """

    @abstractmethod
    def get_filters(self, customer_uuid, application_uuid,user_uuid, validated_data):
        """

            Get the available filters to filter the tickets
            Parameters:
                customer_uuid : The UUID of the customer
                application_uuid : The UUID of the application
                user_uuid : The UUID of the user

        """

    @abstractmethod
    def update_is_read_status(self, ticket_uuid, is_read,user_uuid):
        """
        Marks an email conversation as read or unread in the database.

        Parameters:
            ticket_uuid (str): The UUID of the email ticket to update.
            is_read (bool): Boolean indicating whether the conversation is marked as read (True) or unread (False).
            user_uuid : UUID of the user
        Returns:
            bool: True if the update was successful (at least one row was updated), False otherwise.
        """

    @abstractmethod
    def merge_tickets(self, primary_ticket_uuid, secondary_ticket_uuid, customer_uuid, application_uuid, user_uuid):
        """
            Merging the provided two tickets
            Parameters:
                primary_ticket_uuid : The UUID of the primary ticket
                secondary_ticket_uuid : The UUID of the secondary ticket
                customer_uuid : The UUID of the customer
                application_uuid : The UUID of the application
                user_uuid : The UUID of the user
        """

    @abstractmethod
    def get_ticket_dropdown(self,customer_uuid,application_uuid,user_uuid):
        """
            Get the dropdown ticket list for merging
            Parameters:
                customer_uuid : The UUID of the customer
                application_uuid : The UUID of the application
                user_uuid : The UUID of the user
        """

    @abstractmethod
    def get_merged_conversation_by_ticket_uuid(self,ticket_uuid):
        """
            Get the conversations for merged ticket
            Parameters :
                ticket_uuid : The uuid of the merged ticket uuid
        """
