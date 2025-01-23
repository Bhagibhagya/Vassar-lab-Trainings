from EmailApp.DataClasses.response.pagination_data import PaginationResponse
from EmailApp.dao.impl.email_conversation_dao_impl import EmailConversationDaoImpl
from EmailApp.dao.impl.email_dao_impl import EmailDaoImpl
from EmailApp.dao.impl.email_info_dao_impl import EmailInfoDaoImpl
from EmailApp.dao.impl.ticket_dao_impl import TicketDaoImpl
from EmailApp.services.interface.ticket_service_interface import ITicketService
from Platform.utils import paginate_queryset
from EmailApp.utils import datetime_to_milliseconds

import logging
logger = logging.getLogger(__name__)

class TicketServiceImpl(ITicketService):
    
    def __init__(self):
        self.ticket_dao = TicketDaoImpl()
        self.email_conversation_dao = EmailConversationDaoImpl()
        self.email_dao = EmailDaoImpl()
        self.email_info_dao = EmailInfoDaoImpl()

    def get_email_tickets(self, customer_uuid, application_uuid,user_uuid, validated_data):
        """
        Fetches paginated email tickets for a specific customer and application.

        Args:
            customer_uuid (str): Unique identifier for the customer.
            application_uuid (str): Unique identifier for the application.
            user_uuid (str): Unique identifier for the user.
            validated_data (dict): Data used for filtering and pagination.
        
        Returns:
            dict: A response containing paginated email tickets and metadata.
        """
        logger.info("Fetching email conversations for customer: %s, application: %s", customer_uuid, application_uuid)

        # Fetch email tickets from database with optimized pagination
        email_ticket_queryset = self.ticket_dao.query_email_tickets(customer_uuid, application_uuid,user_uuid, validated_data)

        # Paginate the queryset and fetch the email conversations for the requested page
        page, paginator = paginate_queryset(email_ticket_queryset, validated_data)

        paginated_email_tickets = self.build_email_tickets_list(page.object_list)

        # Build and return the response
        return self.build_response(paginated_email_tickets, paginator.count, paginator.num_pages, validated_data)


    def build_email_tickets_list(self, email_ticket_obj):
        """
        Builds a list of email tickets with necessary details.

        Args:
            email_ticket_queryset (QuerySet): QuerySet of email tickets.

        Returns:
            list: A list of dictionaries containing email ticket details.
        """

        # Extract ticket UUIDs
        ticket_uuids = [ticket['ticket_uuid'] for ticket in email_ticket_obj]

        # Fetch email_conversation_uuids of a ticket
        parent_emails = self.email_dao.get_parent_emails_by_tickets(ticket_uuids)

        tickets_list = []
        if parent_emails is not None and len(parent_emails)!=0:

            # Build a dictionary for quick lookup of parent emails
            emails_dict = {email['ticket_uuid']: email for email in parent_emails}

            # Build the list of email tickets
            tickets_list = [
                self.build_parent_email_dict(email_ticket, emails_dict.get(email_ticket['ticket_uuid']))
                for email_ticket in email_ticket_obj
            ]

        return tickets_list

    def build_parent_email_dict(self, email_ticket, email):
        """
        Builds a dictionary with details of a parent email.

        Args:
            email_conversation (dict): Email conversation details.
            email (dict): Parent email details.

        Returns:
            dict: Dictionary containing email conversation details.
        """

        # Retrieve sender name and sender email from email info by email_uuid
        sender_name, subject = self.email_info_dao.get_conversation_info(email['email_uuid'])


        # Build and return the dictionary
        return {
            'ticket_uuid': email_ticket['ticket_uuid'],
            'sender_name': sender_name,
            'subject': subject,
            'is_read': email_ticket.get('is_read'),
            'inserted_ts': datetime_to_milliseconds(email_ticket['inserted_ts']),
            'updated_ts': datetime_to_milliseconds(email_ticket['updated_ts']),
        }


    def build_response(self, paginated_emails, total_mails, total_pages, validated_data):
        """
        Builds the response containing paginated email conversations and metadata.

        Args:
            paginated_emails (list): List of paginated email conversations.
            total_mails (int): Total number of email conversations.
            validated_data (dict): Data containing pagination info.

        Returns:
            dict: Response with email conversations and pagination metadata.
        """
        return PaginationResponse(
            page_num=validated_data['page_number'],
            total_entry_per_page=validated_data['total_entry_per_page'],
            total_entries=total_mails,
            total_pages=total_pages,
            data=paginated_emails
        ).model_dump()