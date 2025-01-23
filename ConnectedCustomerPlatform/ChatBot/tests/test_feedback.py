import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from ChatBot.tests.test_data import create_conversation_data
from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.error_messages import ErrorMessages
from django.urls import reverse
from rest_framework import status
from ChatBot.constant.constants import Constants
from ChatBot.constant.constants import FeedbackConstants


class BaseTestCase(TestCase):
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()
        # Import test data from test_data module
        self.customer,self.application,self.user,self.chat_conversation,self.ticket = create_conversation_data()

class FeedbackAPITests(BaseTestCase):
    # Call the base setup

    # 1. With all correct values
    def test_rateby_user_success(self):
        data = {
            FeedbackConstants.CHAT_CONVERSATION_UUID: str(self.chat_conversation.chat_conversation_uuid),
            FeedbackConstants.SATISFACTION_LEVEL: Constants.SATISFACTION_CHOICES[0],  # Use one of the valid choices
            FeedbackConstants.ADDITIONAL_COMMENTS: "Great service!"
        }

        response = self.client.post(
            reverse('ChatBot:chat_conversation_feedback'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SuccessMessages.FEEDBACK_SUBMITTED_SUCCESSFULLY, response.data.get('result'))

    # 2. With invalid conversation_uuid
    def test_rateby_user_invalid_conversation_uuid(self):
        data = {
            FeedbackConstants.CHAT_CONVERSATION_UUID: "invalid_uuid",
            FeedbackConstants.SATISFACTION_LEVEL: Constants.SATISFACTION_CHOICES[0],  # Use one of the valid choices
            FeedbackConstants.ADDITIONAL_COMMENTS: "Great service!"
        }

        response = self.client.post(
            reverse('ChatBot:chat_conversation_feedback'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(ErrorMessages.CHAT_CONVERSATION_NOT_FOUND, response.data.get('result'))

    # 3. With missing required fields
    def test_rateby_user_missing_fields(self):
        data = {
            FeedbackConstants.CHAT_CONVERSATION_UUID: str(self.chat_conversation.chat_conversation_uuid),
            FeedbackConstants.SATISFACTION_LEVEL: "",  # Missing satisfaction level
            FeedbackConstants.ADDITIONAL_COMMENTS: "Great service!"
        }

        response = self.client.post(
            reverse('ChatBot:chat_conversation_feedback'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.INVALID_DATA, response.data.get('result'))

    # 4. With invalid satisfaction level
    def test_rateby_user_invalid_satisfaction_level(self):
        data = {
            FeedbackConstants.CHAT_CONVERSATION_UUID: str(self.chat_conversation.chat_conversation_uuid),
            FeedbackConstants.SATISFACTION_LEVEL: "Not a valid choice",  # Invalid satisfaction level
            FeedbackConstants.ADDITIONAL_COMMENTS: "Great service!"
        }

        response = self.client.post(
            reverse('ChatBot:chat_conversation_feedback'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ErrorMessages.INVALID_DATA, response.data.get('result'))

    # 5. Non-existent conversation
    def test_rateby_user_non_existent_conversation(self):
        # Assuming we can create a valid conversation_uuid but then delete the conversation
        non_existent_uuid = str(uuid.uuid4())  # Generate a UUID that doesn't exist

        data = {
            FeedbackConstants.CHAT_CONVERSATION_UUID: non_existent_uuid,
            FeedbackConstants.SATISFACTION_LEVEL: Constants.SATISFACTION_CHOICES[0],
            FeedbackConstants.ADDITIONAL_COMMENTS: "Great service!"
        }

        response = self.client.post(
            reverse('ChatBot:chat_conversation_feedback'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(ErrorMessages.CHAT_CONVERSATION_NOT_FOUND, response.data.get('result'))