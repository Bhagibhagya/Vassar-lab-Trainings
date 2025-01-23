from abc import ABC, abstractmethod

class ITicketDao(ABC):
    """
    Interface for Ticket DAO operations.
    This defines the contract that any Ticket DAO implementation should follow.
    """

    @abstractmethod
    def get_ticket_external_uuid(self, ticket_uuid):
        """
        Retrieve the external ID of a ticket using its UUID.

        Args:
            ticket_uuid (str): The UUID of the ticket to fetch.

        Returns:
            str: The external ID of the ticket if found.
        """