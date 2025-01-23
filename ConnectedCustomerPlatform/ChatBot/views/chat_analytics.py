import json
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import status
from DBServices.models import Conversations
import logging
from django.db.models import  Q,Count
from datetime import datetime, timedelta
from collections import Counter
from ChatBot.constant.constants import Constants
from ConnectedCustomerPlatform.responses import CustomResponse
from ChatBot.utils import get_redis_connection
from django.utils import timezone
from django.db.models.functions import TruncDate
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

# Create your views here.
class ChatAnalyticsViewSet(ViewSet):
    def __init__(self, *args, **kwargs):
        self.redis = get_redis_connection()

    def get_user_counts(self,customer_uuid,application_uuid):
        logger.info("In chat_analytics.py :: :: ::  ChatAnalyticsViewSet :: :: ::get_users_counts")
        """
            Retrieves counts of different types of users interacting with the chatbot.

        Returns:
            dict: A dictionary containing user count information.

            - TOTAL_USERS (int): Total number of users.
            - AUTHENTICATED_USERS (int): Number of authenticated users.
            - UNAUTHENTICATED_USERS (int): Number of unauthenticated users.
            - ACTIVE_USERS (int): Number of active users, including those currently interacting with the chatbot.
        """
        active_users = self.get_active_users(customer_uuid,application_uuid)
        return {
            Constants.TOTAL_USERS: Conversations.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid).values(Constants.USER_DETAIL_JSON_UID).distinct().count(),
            Constants.AUTHENTICATED_USERS: Conversations.objects.filter(user_details_json__userType='AUTHENTICATED',
                                                                        customer_uuid=customer_uuid,
                                                                        application_uuid=application_uuid).values(Constants.USER_DETAIL_JSON_UID).distinct().count(),
            Constants.UNAUTHENTICATED_USERS: Conversations.objects.filter(user_details_json__userType='NON_AUTHENTICATED',
                                                                          customer_uuid=customer_uuid,
                                                                          application_uuid=application_uuid).values(Constants.USER_DETAIL_JSON_UID).distinct().count(),
            Constants.ACTIVE_USERS: active_users
        }

    def calculate_fallback_rate(self,customer_uuid,application_uuid):

        logger.info("In chat_analytics.py :: :: ::  ChatAnalyticsViewSet :: :: ::calculate_fallback_rate")
        """
            Calculates the fallback rate of the chatbot.
            Fallback rate is the percentage of conversations or scenarios where the chatbot was unable to handle and a human agent had to take over.

            Formula:
                Fallback Rate = (Number of Fallback Conversations / Total Conversations) * 100
        """
        total_conversations = Conversations.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid
        ).count()

        fallback_conversations = Conversations.objects.filter(csr_hand_off=True,customer_uuid=customer_uuid,
                                                              application_uuid=application_uuid).count()
        fallback_rate = round((fallback_conversations / total_conversations) * 100) if total_conversations > 0 else 0
        return {
            Constants.TOTAL_CONVERSATIONS: total_conversations,
            Constants.FALLBACK_CONVERSATIONS: fallback_conversations,
            Constants.FALLBACK_RATE: fallback_rate
        }

    def calculate_session_duration(self,customer_uuid,application_uuid):
        logger.info("In chat_analytics.py :: :: ::  ChatAnalyticsViewSet :: :: ::calculate_session_duration")
        """ 
            - under_1_minute (int): Number of sessions with duration under 1 minute.
            - under_3_minute (int): Number of sessions with duration under 3 minutes.
            - under_5_minute (int): Number of sessions with duration under 5 minutes.
            - under_10_minute (int): Number of sessions with duration under 10 minutes.
            - above_10_minutes (int): Number of sessions with duration above 10 minutes.
            - intents (list): List of intents with usage statistics containing:
        """

        session_duration_count = {
            Constants.UNDER_1_MINUTE: 0,
            Constants.UNDER_3_MINUTE: 0,
            Constants.UNDER_5_MINUTE: 0,
            Constants.UNDER_10_MINUTE: 0,
            Constants.ABOVE_10_MINUTES: 0
        }

        sessions = Conversations.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid
        ).all()

        for session in sessions:
            conversation_stats_json = session.conversation_stats_json
            conversation_stats_list=[]
            # Ensure conversation_stats_json is a list
            if isinstance(conversation_stats_json, dict):
                conversation_stats_list = [conversation_stats_json]  # Convert single object to list
            elif isinstance(conversation_stats_json, list):
                conversation_stats_list = conversation_stats_json

            for stat in conversation_stats_list:
                start_time_str = stat.get('conversationStartTime')
                end_time_str = stat.get('conversationResolutionTime')
                if start_time_str and end_time_str:
                    start_time = datetime.fromisoformat(start_time_str)
                    end_time = datetime.fromisoformat(end_time_str)
                    duration = (end_time - start_time).seconds // 60  # Duration in minutes
                    if duration < 1:
                        session_duration_count[Constants.UNDER_1_MINUTE] += 1
                    elif duration < 3:
                        session_duration_count[Constants.UNDER_3_MINUTE] += 1
                    elif duration < 5:
                        session_duration_count[Constants.UNDER_5_MINUTE] += 1
                    elif duration < 10:
                        session_duration_count[Constants.UNDER_10_MINUTE] += 1
                    else:
                        session_duration_count[Constants.ABOVE_10_MINUTES] += 1
        return session_duration_count

    def extract_intents_from_message(self,message):
        intents = set()
        dimension_action_json = message.get('dimension_action_json', {})
        dimensions = dimension_action_json.get('dimensions', [])
        for dimension in dimensions:
            if dimension.get('dimension') == 'Intent' and 'value' in dimension:
                intents.add(dimension['value'])
        return intents

    def calculate_intent_usage(self,customer_uuid,application_uuid):
        logger.info("In chat_analytics.py :: :: ::  ChatAnalyticsViewSet :: :: ::calculate_intent_usage")
        """
            Calculates the usage of different intents in conversations.

            Returns:
                Counter: A Counter object containing the counts of different intents used in conversations.
        """

        intent_counter = Counter()
        conversations = Conversations.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid
        ).all()

        for conversation in conversations:
            unique_intents = set()
            if conversation.message_details_json:
                for message in conversation.message_details_json:
                    unique_intents.update(self.extract_intents_from_message(message))

            # Update the counter with unique intents from the conversation
            intent_counter.update(unique_intents)

        # Sort intents by usage in descending order
        sorted_intent_counter = dict(intent_counter.most_common())
        return sorted_intent_counter

    def get_containment_rate_dimensions(self,customer_uuid,application_uuid):
        intent_counter = Counter()
        conversations = Conversations.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid
        ).all()

        for conversation in conversations:
            unique_intents = set()
            if(conversation.conversation_status==Constants.CSR_RESOLVED):
                if conversation.message_details_json:
                    for message in conversation.message_details_json:
                        unique_intents.update(self.extract_intents_from_message(message))

                # Update the counter with unique intents from the conversation
                intent_counter.update(unique_intents)

        # Sort intents by usage in descending order
        sorted_intent_counter = dict(intent_counter.most_common())
        total_intents = sum(sorted_intent_counter.values())
        intents_with_percentages = [
            {
                "intent": intent,
                "transfers": count,
                "percentage": round((count / total_intents) * 100) if total_intents > 0 else 0
            }
            for intent, count in intent_counter.items()
        ]
        intents_with_percentages.sort(key=lambda x: x['transfers'], reverse=True)
        return intents_with_percentages

    def get_total_conversations_and_bounce_rate_data(self, start_date_str: str, end_date_str: str,customer_uuid,application_uuid):

        # total_conversation timeseries data
        total_conversation_daily = []
        total_conversation_weekly = []
        total_conversation_monthly = []

        # average
        total_conversation_avg_daily=0
        total_conversation_avg_weekly=0
        total_conversation_avg_monthly=0

        # conversation count
        successful_conversation=0
        unsuccessful_conversation=0

        # total_conversation_count count
        total_conversation_count = 0

        # Number of Interactions
        number_of_user_interactions=0

        # bounce rate
        bounce_rate=0

        # Parse start_date and end_date from string format "dd/mm/yyyy"
        start_date = datetime.strptime(start_date_str, '%d/%m/%Y').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        end_date = datetime.strptime(end_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
        
        # Validation to ensure end_date is greater than or equal to start_date
        if end_date < start_date:
            raise ValueError("end_date must be greater than or equal to start_date")

        # Calculate the number of days between the two dates
        delta = end_date - start_date
        number_of_days = delta.days + 1

        # Filter conversations for the target date range
        query = Conversations.objects.filter(customer_uuid=customer_uuid,
                                             application_uuid=application_uuid,insert_ts__range=(start_date, end_date))

        # Filter conversations within the date range and annotate the counts by day
        records = (query
                   .annotate(day=TruncDate('insert_ts'))
                   .values('day')
                   .annotate(count=Count('conversation_uuid'))  # Use a field that exists in your model for counting
                   .order_by('day'))

        # get successful_conversation and unsuccessful_conversation
        successful_conversation = query.filter(Q(conversation_status=Constants.BOT_RESOLVED) | Q(conversation_status=Constants.CSR_RESOLVED)).count()
        unsuccessful_conversation = query.filter(conversation_status=Constants.CLOSED).count()

        # get total_conversation_count & total_conversation_daily
        for record in records:
            date = record['day'].strftime('%d/%m/%Y')
            count = record['count']
            total_conversation_count+=count
            total_conversation_daily.append({Constants.DATE:date, Constants.COUNT:count})
        
        # get total_conversation_weekly
        start_week = start_date - timedelta(days=start_date.weekday()) # Find the first Monday after the start_date (if start_date is not Monday)

    
        week_ranges = []
        current_start = start_week
        while current_start <= end_date:
            current_end = current_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
            week_ranges.append((current_start, current_end))
            current_start += timedelta(days=7)

        for start, end in week_ranges:
            weekly_counts = Conversations.objects.filter(customer_uuid=customer_uuid,
                                                         application_uuid=application_uuid,insert_ts__range=(start, end)).count()
            total_conversation_weekly.append({Constants.DATE:start.strftime('%d/%m/%Y'), Constants.COUNT:weekly_counts})

        #get total_conversation_monthly
        current_start = start_date.replace(day=1)    # Generate the monthly ranges
        monthly_ranges = []
        while current_start <= end_date:
            next_month = current_start + relativedelta(months=1)
            current_end = next_month - timedelta(seconds=1)  # Last second of the current month
            monthly_ranges.append((current_start, current_end))
            current_start = next_month

        for start, end in monthly_ranges:
            monthly_counts = Conversations.objects.filter(customer_uuid=customer_uuid,
                                                          application_uuid=application_uuid,insert_ts__range=(start, end)).count()
            total_conversation_monthly.append({Constants.DATE:start.strftime('%d/%m/%Y'), Constants.COUNT:monthly_counts})

        #get avg_daily
        total_conversation_avg_daily= round(total_conversation_count/number_of_days) if number_of_days > 0 else 0

        #get avg_weekly
        total_weeks = round(number_of_days/7)
        total_conversation_avg_weekly = round(total_conversation_count/total_weeks) if total_weeks > 0 else 0

        #get avg_monthly
        total_months = round(number_of_days/30)
        total_conversation_avg_monthly = round(total_conversation_count/total_months) if total_months > 0 else 0

        # bounce rate
        records = query.values('conversation_uuid', 'message_details_json')
        for record in records:
            messages = record['message_details_json']
            for message in messages:
                if message['source'] == 'user':
                    number_of_user_interactions+=1
                    break

        bounce_rate = 100-((number_of_user_interactions/total_conversation_count)*100 if total_conversation_count > 0 else 0)

        # containment rate : query resolved by bot
        ai_resolved = query.filter(conversation_status=Constants.BOT_RESOLVED).count()
        containment_rate = round((ai_resolved/total_conversation_count)*100) if total_conversation_count > 0 else 0
        # return response
        return {
            Constants.TOTAL_CONVERSATIONS_AVERAGE:{
                Constants.AVG_DAILY:total_conversation_avg_daily,
                Constants.AVG_WEEKLY:total_conversation_avg_weekly,
                Constants.AVG_MONTHLY:total_conversation_avg_monthly
            },
            Constants.TOTAL_CONVERSATIONS_TIME_SERIES:{
                Constants.DAILY: total_conversation_daily,
                Constants.WEEKLY: total_conversation_weekly,
                Constants.MONTHLY: total_conversation_monthly
            },
            Constants.BOUNCE_RATE:{
                Constants.TOTAL_CONVERSATIONS: total_conversation_count,
                Constants.USERS_INTERACTED: number_of_user_interactions,
                Constants.BOUNCES: total_conversation_count-number_of_user_interactions,
                Constants.BOUNCE_RATE: round(bounce_rate),
                Constants.INTERACTION_RATE:100-round(bounce_rate)
            },
            Constants.SUCCESSFUL_CONVERSATION:successful_conversation,
            Constants.UNSUCCESSFUL_CONVERSATION:unsuccessful_conversation,
            Constants.CONTAINMENT_RATE:containment_rate,
        }

    @action(detail=False, methods=['post'])
    def chatbot_analytics(self,request):
        logger.info("In views :: :: :: chat_analytics.py:: :: :: ChatAnalyticsViewSet :: :: :: chatbot_analytics ")
        """
        This API endpoint retrieves various analytics data related to the chatbot's performance, including user counts,
        bounce rate, fallback rate, session duration, and intent usage.

        Returns:
            Response: Chatbot analytics data.

                - total_users (int): 
                - authenticated_users (int): 
                - unauthenticated_users (int): 
                - active_users (int): 
                - total_conversations (int): 
                - fallback_rate (dict): 
                    Formula: fallback_rate = (fallback_conversations / total_conversations) * 100 if total_conversations > 0 else 0
                - bounce_rate (dict):
                    Formula: bounce_rate = (bounces / total_visits) * 100 if total_visits > 0 else 0
                - session_duration (dict): Session duration distribution containing:
                - intents (list): List of intents with usage statistics containing:
        """

        customer_uuid = request.headers.get('Customer-Uuid')
        application_uuid = request.headers.get('Application-Uuid')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')

        if not start_date_str or not end_date_str:
            return CustomResponse('start_date and end_date are required.',status=False, code=status.HTTP_400_BAD_REQUEST)
        try:
            user_counts = self.get_user_counts(customer_uuid,application_uuid)
            fallback_rate = self.calculate_fallback_rate(customer_uuid,application_uuid)
            total_conversations_and_bounce_rate_data=self.get_total_conversations_and_bounce_rate_data(start_date_str, end_date_str,customer_uuid,application_uuid)

            session_duration_count = self.calculate_session_duration(customer_uuid,application_uuid)
            intent_counter = self.calculate_intent_usage(customer_uuid,application_uuid)
            containment_rate_dimensions  = self.get_containment_rate_dimensions(customer_uuid,application_uuid)

            total_intents = sum(intent_counter.values())
            intents_with_percentages = [
                {
                    "intent": intent,
                    "count": count,
                    "percentage": round((count / total_intents) * 100) if total_intents > 0 else 0
                }
                for intent, count in intent_counter.items()
            ]
            intents_with_percentages.sort(key=lambda x: x['count'], reverse=True)

            result = {
                Constants.TOTAL_USERS: user_counts[Constants.TOTAL_USERS],
                Constants.AUTHENTICATED_USERS: user_counts[Constants.AUTHENTICATED_USERS],
                Constants.UNAUTHENTICATED_USERS: user_counts[Constants.UNAUTHENTICATED_USERS],
                Constants.ACTIVE_USERS: user_counts[Constants.ACTIVE_USERS],
                Constants.TOTAL_CONVERSATIONS: fallback_rate[Constants.TOTAL_CONVERSATIONS],
                Constants.FALLBACK_RATE: fallback_rate,
                Constants.BOUNCE_RATE: total_conversations_and_bounce_rate_data[Constants.BOUNCE_RATE],
                Constants.SESSION_DURATION: session_duration_count,
                Constants.INTENTS: intents_with_percentages,
                Constants.TOTAL_CONVERSATIONS_AVERAGE:total_conversations_and_bounce_rate_data[Constants.TOTAL_CONVERSATIONS_AVERAGE],
                Constants.TOTAL_CONVERSATIONS_TIME_SERIES:total_conversations_and_bounce_rate_data[Constants.TOTAL_CONVERSATIONS_TIME_SERIES],
                Constants.SUCCESSFUL_CONVERSATION:total_conversations_and_bounce_rate_data[Constants.SUCCESSFUL_CONVERSATION],
                Constants.UNSUCCESSFUL_CONVERSATION:total_conversations_and_bounce_rate_data[Constants.UNSUCCESSFUL_CONVERSATION],
                Constants.CONTAINMENT_RATE:total_conversations_and_bounce_rate_data[Constants.CONTAINMENT_RATE],
                Constants.CONTAINMENT_RATE_DIMENSIONS:containment_rate_dimensions,
            }
            return CustomResponse(result)

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            return CustomResponse(str(e),status=False, code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_active_users(self,customer_uuid,application_uuid):

        active_users = 0
        # Fetch all keys from Redis that match the conversation status criteria
        conversation_keys = self.redis.keys("conversation:*")

        for key in conversation_keys:
            # Retrieve conversation data
            conversation_data = self.redis.get(key)
            if conversation_data:
                conversation_data = json.loads(conversation_data)
                # Check if conversation status is ongoing
                conversation_status = conversation_data.get("conversation_status", "")
                if (conversation_status in [Constants.BOT_ONGOING, Constants.CSR_ONGOING] and conversation_data.get("customer_uuid") == customer_uuid and
                        conversation_data.get("application_uuid") == application_uuid):
                    active_users += 1  # Increment active user count
        return active_users