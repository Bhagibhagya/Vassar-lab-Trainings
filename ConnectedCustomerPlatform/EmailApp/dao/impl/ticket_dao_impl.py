from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException
from DatabaseApp.models import Ticket, UserTicketMapping
from EmailApp.constant.constants import EmailActionFlowStatus, EmailConversationParams, ChannelTypes
from django.db.models import Q,F, Func, Value ,CharField ,OuterRef, Subquery

from EmailApp.dao.interface.ticket_dao_interface import TicketDaoInterface
from EmailApp.utils import is_user_admin

import logging
logger = logging.getLogger(__name__)

class TicketDaoImpl(TicketDaoInterface):

    def query_email_tickets(self, customer_uuid, application_uuid,user_uuid, validated_data):
        if is_user_admin(user_uuid, customer_uuid, application_uuid):
            ticket_queryset = Ticket.objects.filter(
                channel=f'{ChannelTypes.EMAIL.value}',
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                inserted_ts__gte=validated_data['start_date'],
                inserted_ts__lte=validated_data['end_date'],
                is_deleted=False,
            ).order_by(f'-{EmailConversationParams.UPDATED_TS.value}')
        else:
            ticket_queryset = Ticket.objects.filter(
                userticketmapping__user_id=user_uuid,
                userticketmapping__is_active=True,
                channel=f'{ChannelTypes.EMAIL.value}',
                customer_uuid = customer_uuid,
                application_uuid = application_uuid,
                inserted_ts__gte=validated_data['start_date'],
                inserted_ts__lte=validated_data['end_date'],
                is_deleted=False,
            ).annotate(
                is_read = Subquery(
                            UserTicketMapping.objects.filter(
                                ticket_uuid=OuterRef('ticket_uuid'),
                                user_id=user_uuid,
                                is_active=True
                            ).values('is_read')[:1]  # Subquery to get 'is_read' for the specific mapping
                        )
            ).order_by(f'-{EmailConversationParams.UPDATED_TS.value}')

        # Check if customer_client_uuid is not null
        # Filter email conversations based on the customer_client_uuid conditions:
        # - If customer_client_uuid is NULL, include those records without further checks.
        # - If customer_client_uuid is NOT NULL, include only those where customer_client_uuid__is_deleted is False.
        ticket_queryset = ticket_queryset.filter(
            Q(customer_client_uuid__isnull=True) | Q(customer_client_uuid__is_deleted=False)
        )

        if validated_data['email_conversation_flow_status'] == EmailActionFlowStatus.AI_ASSISTED.value:
            ticket_queryset = ticket_queryset.filter(
                Q(status=EmailActionFlowStatus.AI_ASSISTED.value) |
                Q(status=EmailActionFlowStatus.NEED_ASSISTANCE.value)
            )
        elif validated_data['email_conversation_flow_status'] == EmailActionFlowStatus.MANUALLY_HANDLED.value:
            ticket_queryset = ticket_queryset.filter(
                Q(status=EmailActionFlowStatus.MANUALLY_HANDLED.value) |
                Q(status=EmailActionFlowStatus.NEED_ATTENTION.value)
            )
        elif validated_data['email_conversation_flow_status'] != EmailActionFlowStatus.TOTAL_EMAIL_RECEIVED.value:
            ticket_queryset = ticket_queryset.filter(status=validated_data['email_conversation_flow_status'])

        is_read_present = 'is_read' in ticket_queryset.query.annotations
 
        # Define the fields dynamically
        fields = [
            'ticket_uuid',
            'ticket_external_id',
            'client_name',
            'inserted_ts',
            'updated_ts',
        ]
 
        if is_read_present:
            fields.append('is_read')

        return ticket_queryset.values(*fields)

    
    def update_timestamp(self, ticket_obj, updated_ts):
        """
        Updates the `updated_ts` field of the given Ticket object.
        
        Args:
            ticket_obj (Ticket): The Ticket object to update.
            updated_ts (datetime): The timestamp to set in the `updated_ts` field.
        """
        ticket_obj.updated_ts = updated_ts
        ticket_obj.save(update_fields=['updated_ts'])  # Optimize query to update only the `updated_ts` field

    def update_ticket_status(self,ticket_uuid,status) -> None:
        """
        Updates status of the Ticket
        Args:
            ticket_uuid:
            status:

        Returns: True if successfully updated

        """
        logger.info("In TicketDaoImpl :: update_ticket_status")
        try:
            # Update the ticket status directly in the database
            updated_count = Ticket.objects.filter(ticket_uuid=ticket_uuid).update(status=status)

            if updated_count == 0:
                logger.error(f"Ticket with UUID {ticket_uuid} does not exist.")
                raise ResourceNotFoundException(f"Ticket with UUID {ticket_uuid} does not exist.")

        except Exception as e:
            logger.error(f"An error occurred while updating ticket status: {e}")
            raise CustomException(f"Error in updating ticket status with ticket uuid :: {ticket_uuid}")
