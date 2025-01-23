from typing import Optional
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from DatabaseApp.models import Ticket, UserTicketMapping, UserMgmtUsers
import logging
from datetime import datetime
from django.db.models import F, Func, Value

from EmailApp.dao.interface.user_ticket_mapping_dao_interface import IUserTicketMappingDao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserTicketMappingDaoImpl(IUserTicketMappingDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IUserTicketMappingDao, cls).__new__(cls)
        return cls._instance

    def create_user_ticket_mapping(self,ticket_uuid,user_id):
        """"
        Creates a new UserTicketMapping in the database.

        Args:
            ticket_uuid (str, optional): UUID for the ticket.
            user_id (str): UUID of the user.

        Returns:

        Raises:
            IntegrityError: If any required fields violate database integrity constraints.
            CustomException: If any other error occurs during the creation of the conversation.
        """
        logger.info("In UserTicketMappingDaoImpl :: create_user_ticket_mapping")

        mapping_uuid = str(uuid.uuid4())  # Generate a new UUID for new record

        try:
            # Create a new Ticket instance
            mapping = UserTicketMapping(
                mapping_uuid = mapping_uuid,
                ticket_uuid = Ticket(ticket_uuid),
                user_id = UserMgmtUsers(user_id)
            )

            # Save the new user_ticket_mapping record to the database
            mapping.save()

            logger.info(f"UserTicketMapping for {ticket_uuid} created successfully.")

        except IntegrityError as e:
            # Raised if there are violations of unique constraints or foreign key issues
            logger.error(f"IntegrityError occurred while creating UserTicketMapping: {e}")
            raise IntegrityError(f"Failed to create UserTicketMapping due to integrity violation: {e}")

        except Exception as e:
            # Catch-all for any other unexpected errors during the creation process
            logger.error(f"An error occurred while creating user_ticket_mapping: {ticket_uuid}")
            raise

    def update_status_and_action_details(self,ticket_uuid,user_id,is_active,action_details_json):
        """
            Updates the is_active status and action_details in UserTicketMapping table

             Args:
                ticket_uuid (str, optional): UUID for the ticket.
                user_id (str): UUID of the user.
                is_active(bool) : Status of that mapping
                action_details_json: action of csr on ticket

        """

        logger.info("In UserTicketMappingDaoImpl :: update_status_and_action_details")

        try :
            UserTicketMapping.objects.filter(ticket_uuid=ticket_uuid,user_id=user_id,is_active=True).update(is_active=is_active,action_details_json=action_details_json,updated_ts=datetime.now())

        except Exception as e:
            # Catch-all for any other unexpected errors during the creation process
            logger.error(f"An error occurred while updating user_ticket_mapping: {ticket_uuid}")
            raise

    def update_is_read_status(self, ticket_uuid: str, is_read: bool):
        """
        Updates the is_read field in an Ticket instance with the given Ticket UUID.

        Args:
            ticket_uuid (str): The UUID of the ticket to update.
            is_read (bool) : Boolean value

        """
        logger.info("In UserTicketMappingDaoImpl :: update_is_read_status")


        # Perform an atomic update without retrieving the object first
        rows_updated = UserTicketMapping.objects.filter(
            ticket_uuid=ticket_uuid,is_active=True
        ).update(is_read=is_read,updated_ts=datetime.now())

        if rows_updated > 0:
            logger.debug(f"Updated is_read to false for Ticket with UUID: {ticket_uuid}")
        else:
            logger.error(f"Ticket mappings with UUID {ticket_uuid} does not exist.")


    def get_csr_id_by_ticket_id(self, ticket_uuid: str) -> str:
        """
        Fetches the assigned_to by ticket uuid

        Args:
            ticket_uuid (str): The UUID of the ticket to fetch.

        Returns:
            assigned_to(csr uuid)
        """
        logger.info("In UserTicketMappingDaoImpl :: get_csr_id_by_ticket_id")
        try:
            user_uuid = UserTicketMapping.objects.filter(ticket_uuid=ticket_uuid, is_active=True).values_list('user_id', flat=True).get()
            logger.debug(f"Fetched user_uid of UUID: {ticket_uuid}")
            return user_uuid
        except ObjectDoesNotExist:
            logger.error(f"Ticket with UUID {ticket_uuid} does not exist.")
            return None