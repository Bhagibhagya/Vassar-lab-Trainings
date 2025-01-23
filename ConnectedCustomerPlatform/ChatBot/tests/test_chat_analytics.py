import json
import unittest
from django.test import TestCase
import logging

from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from collections import Counter
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count


from rest_framework import status
from django.urls import reverse
from datetime import datetime, timedelta
from ..views.chat_analytics import ChatAnalyticsViewSet


from .test_data_ana import create_rateby_user_data
from ..constant.constants import Constants
# from ..constant.constants import RatingConstants
from ..constant.success_messages import SuccessMessages
from ..constant.error_messages import ErrorMessages

logger = logging.getLogger(__name__)

class BaseTestCase(TestCase):
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()
        self.viewset = ChatAnalyticsViewSet()

        # Import test data from test_data module
        self.conversation = create_rateby_user_data()
        self.cnt=0
        

class ChatAnalyticsTestCase(BaseTestCase):
    # 1. With all correct values
    def test_chat_bot_analytics_success(self):
        
        logger.info("testing will correct start Date and End Date")
        
        payload = {
            "start_date": "25/05/2024",
            "end_date": "25/05/2024"
        }

        response = self.client.post(
            reverse('ChatBot:chatbot_analytics'), payload, format='json'
        )


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    # 2. Missing start Date
    def test_chat_bot_analytics_invalid_request(self):

        logger.info("Testing with Missing Start Date")
        payload = {
            "start_date": "",
            "end_date": "25/05/2024"
        }

        response = self.client.post(
            reverse('ChatBot:chatbot_analytics'), payload, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
       
        # 3. Incorrect values
    def test_chat_bot_analytics_incorrect_request(self):
        logger.info("Testing With Incorrect Input value")
        payload = {
            "start_date": "25/05",
            "end_date": "25/05/2024"
        }

        response = self.client.post(
            reverse('ChatBot:chatbot_analytics'), payload, format='json'
        )
        self.assertEqual(response.status_code, 500)

    # 4.Start date after end date
    def test_chat_bot_analytics_SDAED(self):
        logger.info("Testing when start Date after End Date")
        payload = {
            "start_date": "26/05/2024",
            "end_date": "25/05/2024"
        }
        response = self.client.post(
            reverse('ChatBot:chatbot_analytics'), payload, format='json'
        )
        self.assertEqual(response.status_code, 500)


    #5. Testing get_user_counts method
    @patch('DBServices.models.Conversations.objects')
    def test_get_user_counts(self, mock_conversations_objects):
        logger.info("Testing User Count Function")
        # Initialize the viewset instance
        self.viewset = ChatAnalyticsViewSet()

        customer_uuid = 'test-customer-uuid'
        application_uuid = 'test-application-uuid'

        # Create a mock queryset
        mock_query_set = MagicMock()
        
        # Set up mock return values for each queryset call
        mock_conversations_objects.filter.return_value = mock_query_set
        mock_query_set.values.return_value = mock_query_set
        mock_query_set.distinct.return_value = mock_query_set
        
        # Mock counts for different user types
        mock_query_set.count.side_effect = [1, 1, 0]  # Total users, authenticated users, unauthenticated users
        
        # Mock the get_active_users method
        self.viewset.get_active_users = MagicMock(return_value=1)

        # Call the method under test
        user_counts = self.viewset.get_user_counts(customer_uuid, application_uuid)

        # Define the expected result
        expected_counts = {
            Constants.TOTAL_USERS: 1,
            Constants.AUTHENTICATED_USERS: 1,
            Constants.UNAUTHENTICATED_USERS: 0,
            Constants.ACTIVE_USERS: 1
        }

        # Assert that the results match the expected values
        self.assertEqual(user_counts, expected_counts)
    #6. 
    @patch('DBServices.models.Conversations.objects')
    def test_calculate_fallback_rate(self, mock_conversations_objects):
        logger.info("Testing Falback rate")
        instance = ChatAnalyticsViewSet()

        # Mock the filter queries
        # Mock total conversations count
        mock_conversations_objects.filter.return_value.count.side_effect = [
            200,  # Total conversations
            50    # Fallback conversations
        ]

        # Define customer_uuid and application_uuid for testing
        customer_uuid = 'test-customer-uuid'
        application_uuid = 'test-application-uuid'

        # Call the method with the mock data
        result = instance.calculate_fallback_rate(customer_uuid, application_uuid)

        # Define the expected result based on the mocked data
        expected_result = {
            Constants.TOTAL_CONVERSATIONS: 200,
            Constants.FALLBACK_CONVERSATIONS: 50,
            Constants.FALLBACK_RATE: 25
        }

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)


    #8
    @patch('DBServices.models.Conversations.objects')
    @patch.object(ChatAnalyticsViewSet, 'extract_intents_from_message')
    def test_calculate_intent_usage(self, mock_extract_intents_from_message, mock_conversations_objects):
        logger.info("Testing Calculate Intent usage")
        instance = ChatAnalyticsViewSet()

        # Define customer_uuid and application_uuid for testing
        customer_uuid = 'test-customer-uuid'
        application_uuid = 'test-application-uuid'

        # Mock the filter query
        mock_conversations_objects.filter.return_value.all.return_value = [
            MagicMock(message_details_json=[
                {'dimension_action_json': [{'dimensions': [{'dimension': 'Intent', 'value': 'Greeting'}]}]}
            ]),
            MagicMock(message_details_json=[
                {'dimension_action_json': [{'dimensions': [{'dimension': 'Intent', 'value': 'Inquiry'}]}]}
            ]),
            MagicMock(message_details_json=[
                {'dimension_action_json': [{'dimensions': [{'dimension': 'Intent', 'value': 'Support'}]}]}
            ]),
            MagicMock(message_details_json=[
                {'dimension_action_json': [{'dimensions': [{'dimension': 'Intent', 'value': 'Greeting'}]}]}
            ]),
            MagicMock(message_details_json=[
                {'dimension_action_json': [{'dimensions': [{'dimension': 'Intent', 'value': 'Support'}]}]}
            ])
        ]

        # Mock the extract_intents_from_message method
        mock_extract_intents_from_message.side_effect = [
            {'Greeting'},
            {'Inquiry'},
            {'Support'},
            {'Greeting'},
            {'Support'}
        ]

        # Call the method with the mock data
        result = instance.calculate_intent_usage(customer_uuid, application_uuid)

        # Define the expected result based on the mocked data
        expected_result = {
            'Greeting': 2,
            'Inquiry': 1,
            'Support': 2
        }

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    # 9-> 
    @patch('DBServices.models.Conversations.objects')
    def test_calculate_session_duration(self, mock_conversations_objects):
        logger.info("Testing Calculate Session Duration")
        instance = ChatAnalyticsViewSet()

        # Define customer_uuid and application_uuid for testing
        customer_uuid = 'test-customer-uuid'
        application_uuid = 'test-application-uuid'

        # Mock the filter query
        mock_conversations_objects.filter.return_value.all.return_value = [
            MagicMock(conversation_stats_json={'conversationStartTime': '2024-07-11T10:00:00', 'conversationResolutionTime': '2024-07-11T10:01:00'}),
            MagicMock(conversation_stats_json={'conversationStartTime': '2024-07-11T11:00:00', 'conversationResolutionTime': '2024-07-11T11:03:00'}),
            MagicMock(conversation_stats_json={'conversationStartTime': '2024-07-11T12:00:00', 'conversationResolutionTime': '2024-07-11T12:05:00'}),
            MagicMock(conversation_stats_json={'conversationStartTime': '2024-07-11T13:00:00', 'conversationResolutionTime': '2024-07-11T13:08:00'}),
            MagicMock(conversation_stats_json={'conversationStartTime': '2024-07-11T14:00:00', 'conversationResolutionTime': '2024-07-11T14:15:00'}),
            MagicMock(conversation_stats_json={'conversationStartTime': '2024-07-11T15:00:00', 'conversationResolutionTime': '2024-07-11T15:30:00'}),
        ]

        # Call the method with the mock data
        result = instance.calculate_session_duration(customer_uuid, application_uuid)

        # Define the expected result based on the mocked data
        expected_result = {
            Constants.UNDER_1_MINUTE: 0,   # Zero session in less than 1 minute
            Constants.UNDER_3_MINUTE: 1,   # One session in less than 3 minutes
            Constants.UNDER_5_MINUTE: 1,   # One session in less than 5 minutes
            Constants.UNDER_10_MINUTE: 2,  # Two sessions in less than 10 minutes
            Constants.ABOVE_10_MINUTES: 2  # Two sessions above 10 minutes
        }

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)
    # 10
    @patch('DBServices.models.Conversations.objects')
    def test_get_containment_rate_dimensions(self, mock_conversations_objects):
        logger.info("Testing Containment Rate Dimensions")
        instance = ChatAnalyticsViewSet()

        # Define customer_uuid and application_uuid for testing
        customer_uuid = 'test-customer-uuid'
        application_uuid = 'test-application-uuid'

        # Mock conversation objects with conversation_status and message_details_json
        mock_conversations_objects.filter.return_value.all.return_value = [
            # CSR Resolved Conversation
            MagicMock(conversation_status=Constants.CSR_RESOLVED, message_details_json=[
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Inquiry'}]}},
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Support'}]}},
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Inquiry'}]}},
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Feedback'}]}}
            ]),
            # CSR Resolved Conversation
            MagicMock(conversation_status=Constants.CSR_RESOLVED, message_details_json=[
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Inquiry'}]}},
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Feedback'}]}}
            ]),
            # CSR Resolved Conversation
            MagicMock(conversation_status=Constants.CSR_RESOLVED, message_details_json=[
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Inquiry'}]}}
            ]),
            # Bot Resolved Conversation
            MagicMock(conversation_status=Constants.CLOSED, message_details_json=[
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Inquiry'}]}},
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Support'}]}},
                {'dimension_action_json': {'dimensions': [{'dimension': 'Intent', 'value': 'Feedback'}]}}
            ])
        ]

        # Call the method with the mock data
        result = instance.get_containment_rate_dimensions(customer_uuid, application_uuid)

        # Define the expected result based on the mocked data
        expected_result = [
            {'intent': 'Inquiry', 'transfers': 3, 'percentage': 50},
            {'intent': 'Feedback', 'transfers': 2, 'percentage': 33},
            {'intent': 'Support', 'transfers': 1, 'percentage': 17}
        ]

        # Assert that the result matches the expected result
        # print(f'Actual results -----> {result}')
        # print(f'Expected Result---> {expected_result}')

        self.assertEqual(result, expected_result)


    #--> 11 
    @patch('DBServices.models.Conversations.objects')
    def test_get_total_conversations_and_bounce_rate_data(self, mock_conversations_objects):
        logger.info("Testing Total Conversation and Bounce Rate")
        instance = ChatAnalyticsViewSet()

        customer_uuid = 'test-customer-uuid'
        application_uuid = 'test-application-uuid'


        # Mock data for test
        start_date_str = '01/01/2023'
        end_date_str = '31/01/2023'

        # Mock query set
        mock_query_set = MagicMock()
        mock_conversations_objects.filter.return_value = mock_query_set

        # Mock daily counts
        mock_query_set.annotate.return_value.values.return_value.annotate.return_value.order_by.return_value = [
            {'day': datetime(2023, 1, 1, tzinfo=timezone.utc), 'count': 10},
            {'day': datetime(2023, 1, 2, tzinfo=timezone.utc), 'count': 20},
            {'day': datetime(2023, 1, 3, tzinfo=timezone.utc), 'count': 20}
        ]

        # Mock successful and unsuccessful conversations counts
        successful_query_set = MagicMock()
        unsuccessful_query_set = MagicMock()
        bot_resolve_set=MagicMock()

        # Mock the return values for the successful and unsuccessful filters
        successful_query_set.count.return_value = 30
        unsuccessful_query_set.count.return_value = 20
        bot_resolve_set.count.return_value=15
           

        # Configure the mock to return the correct queryset for each filter call
        def side_effect_filter(*args, **kwargs):
            # print(f'Argments---> {args}')
            if self.cnt==0:
                self.cnt=self.cnt+1
                return successful_query_set
            elif self.cnt==1:
                self.cnt+=1
                return unsuccessful_query_set
            else:
                return bot_resolve_set  

        mock_query_set.filter.side_effect = side_effect_filter

        mock_query_set.values.return_value = [
            {'conversation_uuid': '1', 'message_details_json': [{'source': 'user'}, {'source': 'bot'}]},
            {'conversation_uuid': '2', 'message_details_json': [{'source': 'user'}]},
            {'conversation_uuid': '3', 'message_details_json': [{'source': 'bot'}]}
        ]

        # Call the method under test
        result = instance.get_total_conversations_and_bounce_rate_data(start_date_str, end_date_str,customer_uuid,application_uuid)

        # Define expected result based on mocked data
        total_conversation_count = 50
        number_of_days = 31
        total_conversation_avg_daily = round(total_conversation_count / number_of_days)
        total_weeks = round(number_of_days / 7)
        total_conversation_avg_weekly = round(total_conversation_count / total_weeks)
        total_months = round(number_of_days / 30)
        total_conversation_avg_monthly = round(total_conversation_count / total_months)
        number_of_user_interactions = 2  # Only one conversation out of three is not bounced

        bounce_rate = 100 - ((number_of_user_interactions / total_conversation_count) * 100 if total_conversation_count > 0 else 0)
        containment_rate = round((15 / total_conversation_count) * 100) if total_conversation_count > 0 else 0

        expected_result = {
            Constants.TOTAL_CONVERSATIONS_AVERAGE: {
                Constants.AVG_DAILY: total_conversation_avg_daily,
                Constants.AVG_WEEKLY: total_conversation_avg_weekly,
                Constants.AVG_MONTHLY: total_conversation_avg_monthly
            },
            Constants.BOUNCE_RATE: {
                Constants.TOTAL_CONVERSATIONS: total_conversation_count,
                Constants.USERS_INTERACTED: number_of_user_interactions,
                Constants.BOUNCES: total_conversation_count - number_of_user_interactions,
                Constants.BOUNCE_RATE: round(bounce_rate),
                Constants.INTERACTION_RATE: 100 - round(bounce_rate)
            },
            Constants.SUCCESSFUL_CONVERSATION: 30,
            Constants.UNSUCCESSFUL_CONVERSATION: 20,
            Constants.CONTAINMENT_RATE: containment_rate,
        }

        self.assertEqual(result[Constants.TOTAL_CONVERSATIONS_AVERAGE], expected_result[Constants.TOTAL_CONVERSATIONS_AVERAGE])
        self.assertEqual(result[Constants.BOUNCE_RATE], expected_result[Constants.BOUNCE_RATE])
        self.assertEqual(result[Constants.SUCCESSFUL_CONVERSATION], expected_result[Constants.SUCCESSFUL_CONVERSATION])
        self.assertEqual(result[Constants.UNSUCCESSFUL_CONVERSATION], expected_result[Constants.UNSUCCESSFUL_CONVERSATION])
        self.assertEqual(result[Constants.CONTAINMENT_RATE], expected_result[Constants.CONTAINMENT_RATE])

        