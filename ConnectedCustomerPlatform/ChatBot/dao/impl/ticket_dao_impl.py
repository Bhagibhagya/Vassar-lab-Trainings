import inspect
import logging

from ChatBot.dao.interface.ticket_dao_interface import ITicketDao
from DatabaseApp.models import Ticket

logger = logging.getLogger(__name__)


class TicketDaoImpl(ITicketDao):
    """
    Data Access Object (DAO) for Ticket operations.
    Implements the Singleton pattern to ensure only one instance of this class is created.
    """
    _instance = None

    # To make sure only a single instance of this class is created
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TicketDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside TicketDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_ticket_external_uuid(self, ticket_uuid):
        """
        Retrieve the external ID of a ticket using its UUID.

        Args:
            ticket_uuid (str): The UUID of the ticket to fetch.

        Returns:
            str: The external ID of the ticket if found.
        """
        try:
            # Validate that ticket_uuid is provided
            if not ticket_uuid:
                raise ValueError("Ticket UUID must be provided.")

            # Fetch the ticket's external ID
            ticket_external_id = Ticket.objects.get(ticket_uuid=ticket_uuid).ticket_external_id
            return ticket_external_id
        except Ticket.DoesNotExist:
            logger.error(f"No ticket found with UUID: {ticket_uuid}")
            raise Ticket.DoesNotExist(f"No ticket found with UUID: {ticket_uuid}")
        except Exception as e:
            logger.error(f"An error occurred while fetching ticket external ID: {str(e)}")
            raise e
