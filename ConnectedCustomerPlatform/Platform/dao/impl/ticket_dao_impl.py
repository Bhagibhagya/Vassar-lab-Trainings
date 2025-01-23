import datetime

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import Ticket, UserTicketMapping
from EmailApp.dao.impl.user_ticket_mapping_dao_impl import UserTicketMappingDaoImpl
from Platform.constant.error_messages import ErrorMessages
from Platform.dao.interface.ticket_dao_interface import TicketDaoInterface
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.postgres.aggregates import ArrayAgg
from EmailApp.utils import is_user_admin
import logging
from django.db.models import F, Func, Value ,CharField ,OuterRef, Subquery


logger = logging.getLogger(__name__)
class TicketDaoImpl(TicketDaoInterface):

    def __init__(self):
        self.user_ticket_mapping_dao = UserTicketMappingDaoImpl()

    def get_tickets(self, customer_uuid, application_uuid,user_uuid, validated_data):
        # Retrieve activity data from UnifiedActivity model based on the provided UUIDs and date range
        #If the user is admin show all the tickets without any user_id filters
        if is_user_admin(user_uuid,customer_uuid,application_uuid):
            ticket_data = (Ticket.objects.filter(
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                updated_ts__gte=validated_data['start_date'],
                updated_ts__lte=validated_data['end_date'],
                is_deleted = False,
            ).annotate(
                intent=Func(
                    F('dimension_details_json'),  # JSONB column name
                    Value('intent'),  # Outer key in the JSON object
                    Value('name'),  # Nested key path in the JSON object
                    function='jsonb_extract_path_text',
                    output_field=CharField()  # Specify output type as CharField
                )
            ).exclude(status='BOT_ONGOING').values(
                *[field.name for field in Ticket._meta.fields],'intent',
            ))
        else:
            ticket_data = Ticket.objects.filter(
                userticketmapping__user_id=user_uuid,
                userticketmapping__is_active=True,
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                updated_ts__gte=validated_data['start_date'],
                updated_ts__lte=validated_data['end_date'],
                is_deleted=False,
            ).annotate(
                is_read = Subquery(
                            UserTicketMapping.objects.filter(
                                ticket_uuid=OuterRef('ticket_uuid'),
                                user_id=user_uuid,
                                is_active=True
                            ).values('is_read')[:1]  # Subquery to get 'is_read' for the specific mapping
                        ),
                intent=Func(
                    F('dimension_details_json'),  # JSONB column name
                    Value('intent'),  # Outer key in the JSON object
                    Value('name'),  # Nested key path in the JSON object
                    function='jsonb_extract_path_text',
                    output_field=CharField()  # Specify output type as CharField
                )
            ).exclude(status='BOT_ONGOING').values(
                *[field.name for field in Ticket._meta.fields],'is_read','intent'
            )

        # Extract various filtering criteria from the validated data
        status_list = validated_data.get('status')
        channels = validated_data.get('channels')
        client_names = validated_data.get('client_names')
        email_ids = validated_data.get('email_ids')
        intents = validated_data.get('intents')

        ticket_data = ticket_data.filter(
            Q(customer_client_uuid__isnull=True) | Q(customer_client_uuid__is_deleted=False)
        )

        # If channels are provided, filter the activity data for the specified channels
        if channels:
            query = Q()
            for channel in channels:
                query |= Q(channel__iexact=channel)
            ticket_data = ticket_data.filter(query)

        # If client names are provided, filter the activity data for the specified client names
        if client_names:
            ticket_data = ticket_data.filter(client_name__in=client_names)
        
        # If email IDs are provided, filter the activity data for the specified email IDs
        if email_ids:
            ticket_data = ticket_data.filter(email_id__in=email_ids)

        # If intents are provided, filter the activity data for the specified intents
        if intents:
            ticket_data = ticket_data.filter(intent__in=intents)

        # Count occurrences of each status in the filtered activity data and order by status
        status_counts = ticket_data.values('status').annotate(count=Count('status')).order_by('status')

        # If a status list is provided and it does not include 'total', filter activity data based on the status list
        if status_list and 'total' not in status_list:
            ticket_data = ticket_data.filter(status__in=status_list)

        ticket_data = ticket_data.order_by('-updated_ts')

        # Return the filtered activity data and the status counts
        return ticket_data, status_counts
    

    def get_filters(self, customer_uuid, application_uuid,user_uuid, validated_data):
        # Extract start and end dates from validated data
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        status_list = validated_data.get('status')  # Get the list of statuses from validated data
        channels = validated_data.get('channels')  # Get the list of channels from validated data

        # Filter UnifiedActivity objects by customer UUID, application UUID, and date range
        if is_user_admin(user_uuid, customer_uuid, application_uuid):
            ticket_data = Ticket.objects.filter(
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                updated_ts__gte=start_date,
                updated_ts__lte=end_date,
                is_deleted=False
            ).annotate(
                intent=Func(
                    F('dimension_details_json'),  # JSONB column name
                    Value('intent'),  # Outer key in the JSON object
                    Value('name'),  # Nested key path in the JSON object
                    function='jsonb_extract_path_text',
                    output_field=CharField()  # Specify output type as CharField
                )
            )
        else:
            ticket_data = Ticket.objects.filter(
                userticketmapping__user_id=user_uuid,
                userticketmapping__is_active=True,
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                updated_ts__gte=start_date,
                updated_ts__lte=end_date,
                is_deleted=False
            ).annotate(
                intent=Func(
                    F('dimension_details_json'),  # JSONB column name
                    Value('intent'),  # Outer key in the JSON object
                    Value('name'),  # Nested key path in the JSON object
                    function='jsonb_extract_path_text',
                    output_field=CharField()  # Specify output type as CharField
                )
            )

        # Further filter by status if provided
        if status_list and 'total' not in status_list:
            ticket_data = ticket_data.filter(status__in=status_list)

        # Filter by channels if provided, converting to lowercase
        if channels:
            channels = [channel.lower() for channel in channels]
            ticket_data = ticket_data.filter(channel__in=channels)
        
        # Use ARRAY_AGG to collect distinct values for each filter category
        #ARRAY_AGG() in PostgreSQL is an aggregate function that collects a set of values into an array and returns that array as a result.
        #ARRAY_AGG() effectively handles NULL values in aggregated columns, ensuring comprehensive data aggregation across rows.
        # Aggregating all distinct values in a single query
        result = ticket_data.aggregate(
            status_values=ArrayAgg('status', distinct=True, filter=~Q(status__isnull=True) & ~Q(status='')),
            client_names=ArrayAgg('client_name', distinct=True, filter=~Q(client_name__isnull=True) & ~Q(client_name='')),
            email_ids=ArrayAgg('email_id', distinct=True, filter=~Q(email_id__isnull=True) & ~Q(email_id='')),
            intents=ArrayAgg('intent', distinct=True, filter=~Q(intent__isnull=True) & ~Q(intent='')),
            channels=ArrayAgg('channel', distinct=True, filter=~Q(channel__isnull=True) & ~Q(channel='')),
        )

        # Extract the results and ensure they default to empty lists if no results found
        status_values = result['status_values'] or []
        client_names = result['client_names'] or []
        email_ids = result['email_ids'] or []
        intents = result['intents'] or []
        channels = result['channels'] or []

        reponse_dict = {
            "status_values": status_values,
            "client_names":client_names,
            "email_ids":email_ids,
            "intents":intents,
            "channels":channels
        }

        return reponse_dict # Return aggregated filter values as a dict

    def update_is_read_status(self, ticket_uuid, is_read,user_uuid):
        """
        Marks an email conversation as read or unread in the database.

        Parameters:
            ticket_uuid (str): The UUID of the ticket to update.
            is_read (bool): Boolean indicating whether the conversation is marked as read (True) or unread (False).
            user_uuid : UUID of the user
        Returns:
            bool: True if the update was successful (at least one row was updated), False otherwise.
        """
        # Attempt to update the is_read field for the specified email_conversation_uuid.
        # `update` returns the number of rows updated in the database.
        rows_updated = UserTicketMapping.objects.filter(
            ticket_uuid=ticket_uuid,user_id=user_uuid,is_active=True
        ).update(is_read=is_read)
        
        # If no rows were updated, log a warning and return False to indicate failure.
        if rows_updated == 0:
            print(f"No activity found with ticket_uuid: {ticket_uuid}")
            logger.warning(f"No activity found with ticket_uuid: {ticket_uuid}")
            return False  # No matching record was found, so no updates were made.
        
        # If rows were successfully updated, return True.
        return True

    def get_ticket_by_id(self,ticket_uuid):
        """
            Get the ticket by uuid
            Args:
                ticket_uuid : uuid of the ticket to retrieve
        """

        ticket = Ticket.objects.filter(ticket_uuid=ticket_uuid).first()
        if not ticket:
            raise CustomException(ErrorMessages.TICKET_NOT_FOUND)
        return ticket

    def assign_merged_ticket_to_csr(self,primary_ticket_uuid,secondary_ticket_uuid,latest_ticket_uuid):
        """
            Assign the merged to csr
        """
        if latest_ticket_uuid != primary_ticket_uuid:
            latest_csr = self.user_ticket_mapping_dao.get_csr_id_by_ticket_id(latest_ticket_uuid)
            primary_csr = self.user_ticket_mapping_dao.get_csr_id_by_ticket_id(primary_ticket_uuid)
            if latest_csr is not None and primary_csr!=latest_csr:
                self.user_ticket_mapping_dao.create_user_ticket_mapping(primary_ticket_uuid, latest_csr)
        else:
            primary_csr = self.user_ticket_mapping_dao.get_csr_id_by_ticket_id(primary_ticket_uuid)
            if primary_csr is None:
                secondary_csr = self.user_ticket_mapping_dao.get_csr_id_by_ticket_id(secondary_ticket_uuid)
                if secondary_csr is not None and primary_csr!=secondary_csr:
                    self.user_ticket_mapping_dao.create_user_ticket_mapping(primary_ticket_uuid, secondary_csr)

    def save_ticket_instance(self,ticket):
        ticket.save()

    def get_ticket_dropdown(self, customer_uuid, application_uuid,user_uuid):
        logger.info("In ticket_dao_impl.py :: :: :: TicketDaoImpl :: :: :: get_ticket_dropdown ")
        if is_user_admin(user_uuid, customer_uuid, application_uuid):
            ticket_data = Ticket.objects.filter(
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                is_deleted=False,
            ).annotate(
                intent=Func(
                    F('dimension_details_json'),  # JSONB column name
                    Value('intent'),  # Outer key in the JSON object
                    Value('name'),  # Nested key path in the JSON object
                    function='jsonb_extract_path_text',
                    output_field=CharField()  # Specify output type as CharField
                )
            ).exclude(status__in=['BOT_ONGOING','CSR_ONGOING']).values(
                'ticket_uuid','ticket_external_id', 'intent','channel'
            )
        else:
            ticket_data = Ticket.objects.filter(
                userticketmapping__user_id=user_uuid,
                userticketmapping__is_active=True,
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                is_deleted=False,
            ).annotate(
                intent=Func(
                    F('dimension_details_json'),  # JSONB column name
                    Value('intent'),  # Outer key in the JSON object
                    Value('name'),  # Nested key path in the JSON object
                    function='jsonb_extract_path_text',
                    output_field=CharField()  # Specify output type as CharField
                )
            ).exclude(status__in=['BOT_ONGOING','CSR_ONGOING']).values(
                'ticket_uuid', 'ticket_external_id', 'intent','channel'
            )
        return ticket_data
