from abc import ABC, abstractmethod

class TicketDaoInterface(ABC):

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
    def update_is_read_status(self,ticket_uuid,is_read,user_uuid):
        """
        Marks an email activity as read or unread based on the given parameters.

        Parameters:
            ticket_uuid (str): The UUID of the email ticket to update.
            is_read (bool): Boolean indicating whether the email is marked as read (True) or unread (False).
            user_uuid: UUID of the user
        
        Raises:
            InvalidValueProvidedException: If the activity_uuid is not found in the database.

        Returns:
            None
        """

    @abstractmethod
    def get_ticket_by_id(self,ticket_uuid):
        """
            Get the Ticket by ticket_uuid
        """

    @abstractmethod
    def assign_merged_ticket_to_csr(self,primary_ticket_uuid,secondary_ticket_uuid,latest_ticket_uuid):
        """
            Assign the merged ticket to CSR
        """

    @abstractmethod
    def save_ticket_instance(self,ticket):
        """
            Save the ticket instance into DB
        """

    @abstractmethod
    def get_ticket_dropdown(self, customer_uuid, application_uuid,user_uuid):
        """
            Get the tickets dropdown for merging
        """