from abc import ABC, abstractmethod


class IUserTicketMappingDao(ABC):

    @abstractmethod
    def create_user_ticket_mapping(self,ticket_uuid: str, user_id: str):
        """
        Creates a new UserTicketMapping in the database.

        Args:
            ticket_uuid (str, optional): UUID for the ticket.
            user_id (str): UUID of the user.

        Returns:

        Raises:
            IntegrityError: If any required fields violate database integrity constraints.
            CustomException: If any other error occurs during the creation of the mapping.
        """

        pass

    @abstractmethod
    def update_status_and_action_details(self,ticket_uuid,user_id,is_active,action):
        """
        Updates the is_active status and action_details in UserTicketMapping table

         Args:
            ticket_uuid (str, optional): UUID for the ticket.
            user_id (str): UUID of the user.
            is_active(bool) : Status of that mapping
            action: action of csr on ticket

        """
        pass

    @abstractmethod
    def update_is_read_status(self, ticket_uuid: str, is_read: bool):
        """
        Updates the is_read field in an Ticket instance with the given Ticket UUID.

        Args:
            ticket_uuid (str): The UUID of the ticket to update.
            is_read (bool) : boolean value

        """
        pass

    @abstractmethod
    def get_csr_id_by_ticket_id(self, ticket_uuid: str) -> str:
        """
        Fetches the assigned_to by ticket uuid

        Args:
            ticket_uuid (str): The UUID of the ticket to fetch.

        Returns:
            assigned_to(csr uuid)
        """
        pass