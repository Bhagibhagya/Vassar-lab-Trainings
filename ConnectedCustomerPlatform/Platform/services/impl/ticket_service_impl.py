from datetime import datetime

from ChatBot.constant.constants import Constants
from ChatBot.dao.impl.conversations_dao_impl import ConversationsDaoImpl
from ChatBot.services.impl.conversation_service_impl import ConversationServiceImpl
from DatabaseApp.models import Ticket, CustomerClient
from EmailApp.dao.impl.email_conversation_dao_impl import EmailConversationDaoImpl
from EmailApp.dao.impl.email_dao_impl import EmailDaoImpl
from EmailApp.services.impl.email_conversation_impl import EmailConversationServiceImpl
from Platform.constant import constants
from Platform.dao.impl.ticket_dao_impl import TicketDaoImpl
from Platform.serializers import TicketSerializer
from Platform.services.interface.ticket_service_interface import TicketInterface
from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException, CustomException
from Platform.constant.error_messages import ErrorMessages
from heapq import merge

from datetime import datetime,timezone
from django.db import transaction

import logging

from Platform.utils import paginate_queryset
logger = logging.getLogger(__name__)

class TicketServiceImpl(TicketInterface):

    def __init__(self):
        self.ticket_dao = TicketDaoImpl()
        self.conversation_service = ConversationServiceImpl()
        self.email_conversation_dao = EmailConversationDaoImpl()
        self.email_dao = EmailDaoImpl()
        self.chat_conversations_dao = ConversationsDaoImpl()
        self.conversation_service_impl = ConversationServiceImpl()
        self.email_conversation_service = EmailConversationServiceImpl()

    def get_tickets(self, customer_uuid, application_uuid,user_uuid, validated_data):
        # Log the validated input data for debugging purposes
        logger.debug(f"Validated Data : {validated_data}")

        # Extract channels from the validated data
        channels = validated_data.get('channels')

        # Retrieve activity data and status counts using the DAO method
        ticket_data, status_counts = self.ticket_dao.get_tickets(customer_uuid, application_uuid,user_uuid, validated_data)

        # Initialize a summary dictionary for tracking ticket statuses
        status_summary = {
            'total': 0,
            'ai_resolved': 0,
            'ai_assisted': 0,
            'need_assistance': 0,
            'manually_resolved': 0,
            'need_attention': 0
        }

        # Update the status summary with counts from status_counts
        for status_count in status_counts:
            status_summary[status_count['status']] = status_count['count']

        # Combine AI-assisted and manually resolved counts into the summary
        status_summary['ai_assisted'] += status_summary['need_assistance']
        status_summary['manually_resolved'] += status_summary['need_attention']

        # Calculate the total count of tickets based on the statuses
        status_summary['total'] = status_summary['ai_resolved'] + status_summary['ai_assisted'] + status_summary['manually_resolved'] + status_summary.get("processing", 0) or 0 + status_summary.get("CLOSED", 0) or 0

        # Initialize a list for unified activity data retrieved from conversations
        # unified_activity_data_list_queryset = []
        # start_date = validated_data.get('start_date')
        # end_date = validated_data.get('end_date')
        # If channels contain "chat", fetch active conversations
        # if 'chat' in map(str.lower, channels):
        #     active_list = [Constants.CSR_ONGOING]
        #     unified_activity_data_list_queryset = self.conversation_service.get_active_conversation(application_uuid, customer_uuid, active_list,user_uuid, start_date, end_date)

        # combined_data = unified_activity_data_list_queryset + list(ticket_data)
        # Paginate the combined queryset
        paginated_data, paginator = paginate_queryset(ticket_data, validated_data)

        # Serialize the paginated data to prepare for the response
        # serializer = TicketSerializer(paginated_data, many=True)

        # Return the response containing pagination details, serialized data, and status statistics
        return {
            'page_number': paginated_data.number,
            'total_pages': paginator.num_pages,
            'total_entries': paginator.count,
            'data': list(paginated_data),
            'statistics': status_summary
        }
    
    def get_filters(self, customer_uuid, application_uuid,user_uuid, validated_data):
        # Call the DAO layer to retrieve distinct filter values for statuses, client names, email IDs, intents, and channels
        response_dict = self.ticket_dao.get_filters(customer_uuid, application_uuid,user_uuid, validated_data)
        
        # Format the response into a dictionary with keys corresponding to each filter type
        filters = {
            'status': response_dict['status_values'],  # Include the distinct status values
            'client_names': response_dict['client_names'],  # Include the distinct client names
            'email_ids': response_dict['email_ids'],  # Include the distinct email IDs
            'intents': response_dict['intents'],  # Include the distinct intents
            'channels': response_dict['channels']  # Include the distinct channels
        }

        return filters # Return the formatted filter data

    def update_is_read_status(self, ticket_uuid, is_read,user_uuid):
        """
        Marks an email activity as read or unread based on the given parameters.

        Parameters:
            ticket_uuid (str): The UUID of the ticket to update.
            is_read (bool): Boolean indicating whether the email is marked as read (True) or unread (False).
            user_uuid : UUID of the user
        Raises:
            InvalidValueProvidedException: If the activity_uuid is not found in the database.

        Returns:
            None
        """
        # Call the DAO layer to update the read status of the email activity.
        # The DAO function returns False if the activity_uuid is not found.
        status = self.ticket_dao.update_is_read_status(ticket_uuid, is_read,user_uuid)
        
        # If the DAO returns False, raise an exception indicating the UUID is not found.
        if status is False:
            raise InvalidValueProvidedException(ErrorMessages.TICKET_UUID_NOT_FOUND)

    def __get_latest_time(self,time1, time2):
        """
        Returns the latest time between two datetime values.
        Handles None by treating it as the earliest possible time.
        """
        time1 = time1 if time1 is not None else datetime.min.replace(tzinfo=timezone.utc)
        time2 = time2 if time2 is not None else datetime.min.replace(tzinfo=timezone.utc)
        return max(time1, time2)

    def __convert_to_datetime(self,value):
        """
        Converts a string, timestamp, datetime object, or integer (milliseconds) to a datetime object.
        """
        if isinstance(value, datetime):
            # Already a datetime object
            return value
        elif isinstance(value, str):
            # Convert string to datetime (handles ISO format and other formats)
            try:
                return datetime.fromisoformat(value)  # Try ISO 8601 format first
            except ValueError:
                # Handle other formats or fallback to custom format (adjust as needed)
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")  # Example fallback format
        elif isinstance(value, (int, float)):
            # Convert timestamp (seconds since epoch)
            # Ensure it works both for naive and aware datetimes
            return datetime.fromtimestamp(value, tz=timezone.utc)  # Convert to UTC timezone-aware datetime
        else:
            # If unsupported type, raise an error
            raise TypeError(f"Unsupported type: {type(value)}")


    def merge_tickets(self, primary_ticket_uuid, secondary_ticket_uuid, customer_uuid, application_uuid, user_uuid):
        """
            Merging the both primary and secondary tickets
        """

        # Fetch the primary , secondary ticket instances
        primary_ticket = self.ticket_dao.get_ticket_by_id(primary_ticket_uuid)
        secondary_ticket = self.ticket_dao.get_ticket_by_id(secondary_ticket_uuid)
        try :
            with transaction.atomic():
                # Fetch all conversations for both tickets
                primary_email_conversation = self.email_conversation_dao.get_email_conversation_by_ticket_id(primary_ticket.ticket_uuid)
                secondary_email_conversation = self.email_conversation_dao.get_email_conversation_by_ticket_id(secondary_ticket.ticket_uuid)
                primary_chat_conversation = self.chat_conversations_dao.get_conversation_by_ticket_uuid(primary_ticket.ticket_uuid)
                secondary_chat_conversation = self.chat_conversations_dao.get_conversation_by_ticket_uuid(secondary_ticket.ticket_uuid)
                if not ((primary_email_conversation or primary_chat_conversation) and (secondary_email_conversation or secondary_chat_conversation)):
                    logger.exception(f"No conversations found for primary or secondary tickets :: {primary_ticket_uuid, secondary_ticket_uuid}")
                    raise CustomException(ErrorMessages.FAILED_TO_MERGE_TICKETS)

                # Get the latest message time for primary ticket and secondary ticket
                primary_email_conversation_time = None
                secondary_email_conversation_time = None
                secondary_chat_conversation_time = None
                primary_chat_conversation_time = None
                if primary_email_conversation:
                    primary_email_conversation_time = self.__convert_to_datetime(self.email_dao.get_latest_conversation_time(primary_email_conversation.email_conversation_uuid).replace(tzinfo=timezone.utc))
                if primary_chat_conversation:
                    primary_chat_conversation_time = self.__convert_to_datetime(self.chat_conversations_dao.get_latest_message_time(primary_chat_conversation.chat_conversation_uuid))
                primary_time = self.__get_latest_time(primary_email_conversation_time,primary_chat_conversation_time)
                if secondary_email_conversation:
                    secondary_email_conversation_time = self.__convert_to_datetime(self.email_dao.get_latest_conversation_time(secondary_email_conversation.email_conversation_uuid).replace(tzinfo=timezone.utc))
                if secondary_chat_conversation:
                    secondary_chat_conversation_time = self.__convert_to_datetime(self.chat_conversations_dao.get_latest_message_time(secondary_chat_conversation.chat_conversation_uuid))
                secondary_time = self.__get_latest_time(secondary_email_conversation_time,secondary_chat_conversation_time)

                # Based on latest messages timestamp get the latest ticket
                latest_ticket = primary_ticket if primary_time > secondary_time else secondary_ticket

                # If primary and secondary tickets have email_conversations then merge them
                if primary_email_conversation and secondary_email_conversation:
                    # Get the latest conversation between primary and secondary
                    latest_conversation = self.__get_latest_email_conversation(primary_email_conversation, secondary_email_conversation)
                    self.__merge_email_conversations(primary_email_conversation, secondary_email_conversation, user_uuid, latest_conversation)
                # If primary and secondary tickets have chat_conversations then merge them
                if primary_chat_conversation and secondary_chat_conversation:
                    # Get the latest conversation between primary and secondary
                    latest_conversation = self.__get_latest_chat_conversation(primary_chat_conversation, secondary_chat_conversation)
                    self.__merge_chat_conversations(primary_chat_conversation, secondary_chat_conversation, user_uuid, latest_conversation,latest_ticket)
                # If both tickets have different channel conversations then map the second conversation to primary ticket
                # If secondary conversation is email
                if secondary_email_conversation and secondary_email_conversation.is_deleted==False:
                    secondary_email_conversation.ticket_uuid = Ticket(primary_ticket.ticket_uuid)
                    self.email_conversation_dao.save_email_conversation_instance(secondary_email_conversation, user_uuid)
                # If secondary conversation is chat
                if secondary_chat_conversation and secondary_chat_conversation.is_deleted==False:
                    secondary_chat_conversation.ticket_uuid = Ticket(primary_ticket.ticket_uuid)
                    secondary_chat_conversation.updated_by = user_uuid
                    self.chat_conversations_dao.save_chat_conversation_instance(secondary_chat_conversation)

                # Merge the two tickets
                self.__merge_two_tickets(primary_ticket, secondary_ticket, user_uuid, latest_ticket)

        except Exception as e:
            # Log the error with detailed information
            logger.exception(f"Error while merging tickets :: {primary_ticket_uuid,secondary_ticket_uuid}: {e}")
            raise CustomException(ErrorMessages.FAILED_TO_MERGE_TICKETS)



    def __merge_two_tickets(self,primary_ticket,secondary_ticket,user_uuid,latest_ticket):
        logger.info("TicketServiceImpl :: __merge_two_tickets")
        # update the primary ticket and save
        primary_ticket.is_merged = True
        primary_ticket.ticket_details_json = self.__update_ticket_details_json(primary_ticket.ticket_details_json, secondary_ticket.ticket_details_json,secondary_ticket.channel)
        primary_ticket.dimension_details_json = latest_ticket.dimension_details_json
        primary_ticket.client_name = latest_ticket.client_name
        primary_ticket.email_id = latest_ticket.email_id
        primary_ticket.status = latest_ticket.status
        if latest_ticket.customer_client_uuid is not None:
            primary_ticket.customer_client_uuid = CustomerClient(latest_ticket.customer_client_uuid)
        else:
            primary_ticket.customer_client_uuid = None
        # update the csr-assignment for the updated primary merged ticket
        self.ticket_dao.assign_merged_ticket_to_csr(primary_ticket.ticket_uuid, secondary_ticket.ticket_uuid,latest_ticket.ticket_uuid)
        primary_ticket.updated_by = user_uuid
        self.ticket_dao.save_ticket_instance(primary_ticket)
        # soft delete the secondary ticket
        secondary_ticket.is_deleted = True
        secondary_ticket.updated_by = user_uuid
        self.ticket_dao.save_ticket_instance(secondary_ticket)


    def __merge_email_conversations(self,primary_conversation,secondary_conversation,user_uuid,latest_conversation):
        logger.info("TicketServiceImpl :: __merge_email_conversations")
        # Map all emails of secondary conversations to primary conversation
        self.email_dao.map_emails_to_primary_conversation(primary_conversation.email_conversation_uuid, secondary_conversation.email_conversation_uuid)
        # merge the email_activity data
        primary_conversation.email_activity = self.__merge_email_activity(primary_conversation.email_activity, secondary_conversation.email_activity,latest_conversation.email_activity)
        # save the conversation
        self.email_conversation_dao.save_email_conversation_instance(primary_conversation, user_uuid)
        # soft delete the secondary conversation
        secondary_conversation.is_deleted = True
        self.email_conversation_dao.save_email_conversation_instance(secondary_conversation, user_uuid)



    def __merge_chat_conversations(self,primary_conversation,secondary_conversation,user_uuid,latest_conversation,primary_ticket):
        logger.info("TicketServiceImpl :: __merge_chat_conversations")
        # merge the both chat messages
        primary_conversation.message_details_json = self.__merge_chat_messages(primary_conversation.message_details_json, secondary_conversation.message_details_json)
        # merge the both chat stats
        primary_conversation.conversation_stats_json = self.__merge_conversation_stats(primary_conversation.conversation_stats_json, secondary_conversation.conversation_stats_json)
        # update the CSR information
        primary_conversation.csr_info_json = latest_conversation.csr_info_json
        # update the user_info_json
        primary_conversation.user_details_json = latest_conversation.user_details_json
        # update client_name in ticket
        primary_ticket.client_name = latest_conversation.user_details_json.get('user_name')
        self.ticket_dao.save_ticket_instance(primary_ticket)
        # update the summary
        primary_conversation.summary = latest_conversation.summary
        primary_conversation.updated_by = user_uuid
        self.chat_conversations_dao.save_chat_conversation_instance(primary_conversation)
        # soft delete the secondary conversation
        secondary_conversation.updated_by = user_uuid
        secondary_conversation.is_deleted = True
        self.chat_conversations_dao.save_chat_conversation_instance(secondary_conversation)

    def __merge_email_activity(self,primary_email_activity,secondary_activity,latest_activity):
        logger.info("TicketServiceImpl :: __merge_email_activity")
        # Merge both timelines
        for key, value in secondary_activity.get("timeline", {}).items():
            if "timeline" not in primary_email_activity:
                primary_email_activity["timeline"] = {}  # Initialize timeline if it doesn't exist
            if key in primary_email_activity["timeline"]:
                primary_email_activity["timeline"][key].extend(value)  # Append the timeline entries
            else:
                primary_email_activity["timeline"][key] = value

        if "email_summary" in latest_activity:
            primary_email_activity["email_summary"] = latest_activity["email_summary"]
        # TODO update summary in primary_email_activity with merged_summary
        return primary_email_activity

    def __merge_conversation_stats(self,primary_stats,secondary_stats):
        logger.info("TicketServiceImpl :: __merge_conversation_stats")
        if primary_stats:
            if secondary_stats:
                primary_stats.extend(secondary_stats)
            return primary_stats
        else:
            return secondary_stats


    def __merge_chat_messages(self,primary_messages,secondary_messages):
        logger.info("TicketServiceImpl :: __merge_chat_messages")
        merged_messages = list(
            merge(primary_messages, secondary_messages, key=lambda obj: obj["created_at"])
        )
        return merged_messages

    def __update_ticket_details_json(self, primary_ticket_details_json, secondary_ticket_details_json, channel):
        logger.info("TicketServiceImpl :: __update_ticket_details_json")

        # Initialize the result JSON with the primary ticket details
        ticket_details_json = primary_ticket_details_json or {}

        # Merge the merged_tickets_count
        primary_count = ticket_details_json.get('merged_tickets_count', 0)
        secondary_count = secondary_ticket_details_json.get('merged_tickets_count', 0) if secondary_ticket_details_json else 0
        ticket_details_json['merged_tickets_count'] = primary_count + secondary_count + 1

        # Merge the merged_channels
        primary_channels = ticket_details_json.get('merged_channels', {}) or {}
        secondary_channels = secondary_ticket_details_json.get('merged_channels', {}) if secondary_ticket_details_json else {}

        # Combine channel counts from both primary and secondary
        for sec_channel, sec_count in secondary_channels.items():
            primary_channels[sec_channel] = primary_channels.get(sec_channel, 0) + sec_count

        # Update the count for the current channel
        primary_channels[channel] = primary_channels.get(channel, 0) + 1
        ticket_details_json['merged_channels'] = primary_channels

        return ticket_details_json

    def __get_latest_email_conversation(self,primary_conversation,secondary_conversation):
        logger.info("TicketServiceImpl :: __get_latest_email_conversation")
        latest_conversation_uuid = self.email_dao.get_latest_conversation_uuid([primary_conversation.email_conversation_uuid,secondary_conversation.email_conversation_uuid])
        # Determine the conversation with the latest timestamp
        return primary_conversation if latest_conversation_uuid == primary_conversation.email_conversation_uuid else secondary_conversation

    def __get_latest_chat_conversation(self,primary_conversation,secondary_conversation):
        logger.info("TicketServiceImpl :: __get_latest_chat_conversation")
        latest_conversation_uuid = self.chat_conversations_dao.get_latest_conversation_uuid(primary_conversation.chat_conversation_uuid,secondary_conversation.chat_conversation_uuid)
        return primary_conversation if latest_conversation_uuid == primary_conversation.chat_conversation_uuid else secondary_conversation

    def get_ticket_dropdown(self,customer_uuid,application_uuid,user_uuid,):
        """
            Get the dropdown ticket list for merging
            Parameters:
                customer_uuid : The UUID of the customer
                application_uuid : The UUID of the application
                user_uuid : The UUID of the user
        """
        logger.info("In ticket_service_impl.py :: :: :: TicketServiceImpl :: :: :: get_ticket_dropdown ")

        return self.ticket_dao.get_ticket_dropdown(customer_uuid, application_uuid, user_uuid)


    def get_merged_conversation_by_ticket_uuid(self,ticket_uuid):
        """
            Get the conversations for merged ticket
            Parameters :
                ticket_uuid : The uuid of the merged ticket uuid
        """
        ticket = self.ticket_dao.get_ticket_by_id(ticket_uuid)
        chat_conversation = self.chat_conversations_dao.get_conversation_by_ticket_uuid(ticket_uuid)
        email_conversation = self.email_conversation_dao.get_email_conversation_by_ticket_id(ticket_uuid)
        response = {}
        messages = []
        email_response = {}
        chat_response = {}
        if email_conversation is not None:
            email_activity = email_conversation.email_activity
            emails_data = self.email_conversation_dao.get_email_conversation_by_ticket_uuid(ticket_uuid)
            emails = self.email_conversation_service.build_email_conversation_data(emails_data)
            emails = sorted(emails, key=lambda email: email.get('inserted_ts', 0))
            for email in emails:
                email.update({
                    'channel': 'Email',
                    'created_at': self.milliseconds_to_iso(email.get('inserted_ts', 0)),
                    'message_text': email.get('email_info_json', {}).get('email_meta_body'),
                    'intent': email.get('dimension_action_json', {}).get('intent', {}).get('name'),
                })
                messages.append(email)

            email_response = {
                'timeline': email_activity.get('timeline', {}),
                'summary': email_activity.get('email_summary'),
                'csr_assignment_reason': emails[-1].get('dimension_action_json', {}).get('reason'),
                'comment': emails[-1].get('dimension_action_json', {}).get('comment'),
                'sender_name': emails[-1].get('email_info_json', {}).get('sender_name'),
                'sender_email': emails[-1].get('email_info_json', {}).get('sender'),
            }
        if chat_conversation is not None:
            conversation_info = self.conversation_service_impl.get_total_conversation_information(chat_conversation.chat_conversation_uuid)
            message_details = self.conversation_service_impl.get_conversation_history_details(chat_conversation.chat_conversation_uuid)
            for message in message_details:
                message.update({
                    'channel': 'Chat',
                    'sender_name': message.get('sender_name') or message.get('source'),
                    'intent': next((item['value'] for item in message.get('dimension_action_json', {}).get('dimensions', []) if item.get('dimension') == 'intent'), None)
                })
                messages.append(message)

            chat_response = {
                    'summary': chat_conversation.summary,
                    'csr_assignment_reason': conversation_info.get('csr_transfer_reason'),
                    'sender_name': conversation_info.get('user_details', {}).get('user_name'),
                    'sender_email': None,
                    'comment' : None
                }

        sorted_data = sorted(messages, key=lambda x: x['created_at'])
        latest_channel = sorted_data[-1].get('channel')
        if latest_channel.lower() == 'email':
            response.update(email_response)
        else:
            response.update(chat_response)
        response['Dimensions'] = ticket.dimension_details_json
        response['messages'] = sorted_data
        return response

    def milliseconds_to_iso(self,timestamp_ms):
        # Convert the timestamp to seconds and create a datetime object
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

        # Format the datetime object to ISO 8601 string
        iso_format = dt.isoformat()
        return iso_format

