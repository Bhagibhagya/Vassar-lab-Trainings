import uuid
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.tests.test_data import create_conversation_data


class ConversationTestCase(APITestCase):
    def setUp(self):
        # Create test data using the helper function from test_data.py

        self.customer,self.application,self.user,self.chat_conversation,self.ticket = create_conversation_data()


    def test_conversation_history_success(self):
        """
        Test the successful retrieval of conversation history for a valid ticket UUID.
        """
        # Call the conversation history API endpoint
        url = reverse('ChatBot:conversation_history', args=[self.ticket.ticket_uuid])
        response = self.client.get(url)
        print(response.data)
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the "result" key and that it is not empty
        self.assertIn('result', response.data)
        self.assertGreater(len(response.data['result']), 0)

    def test_conversation_history_invalid_ticket_uuid(self):
        """
        Test that the API returns an error when an invalid ticket UUID is provided.
        """
        invalid_ticket_uuid = "akm"  # A new invalid UUID
        url = reverse('ChatBot:conversation_history', args=[str(invalid_ticket_uuid)])

        response = self.client.get(url)
        print(response.data)

        # Assert that the status code is 400 (Bad Request) for invalid ticket UUID
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the error message is present in the 'result' field of the response
        self.assertEqual(response.data['result'], ErrorMessages.CHAT_CONVERSATION_NOT_FOUND)

        # Additional assertions to validate status and code
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['code'], 400)

    def test_conversation_history_invalid_or_missing_ticket_uuid(self):
        """
           Test that the API raises a CustomException when the ticket UUID is missing or invalid.
        """
        # Case 1: Missing ticket_uuid (empty string)
        url = reverse("ChatBot:conversation_history", args=["  "])  # Simulate missing UUID
        response = self.client.get(url)

        # Assert that the API returns a 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the error message matches the expected error message
        self.assertEqual(response.data['result'], ErrorMessages.TICKET_UUID_NOT_NULL)
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['code'], 400)

    def test_total_conversation_info_success(self):
        """
        Test the successful retrieval of conversation history for a valid ticket UUID.
        """
        # Call the conversation history API endpoint
        url = reverse('ChatBot:total_conversation_information_by_ticket_uuid', args=[self.ticket.ticket_uuid])

        response = self.client.get(url)
        print(response.data)
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the "result" key and that it is not empty
        self.assertIn('result', response.data)
        self.assertGreater(len(response.data['result']), 0)

    def test_total_conversation_information_invalid_ticket_uuid(self):
        """
        Test that the API returns an error when an invalid ticket UUID is provided.
        """
        invalid_ticket_uuid = "akm"  # A new invalid UUID
        url = reverse('ChatBot:total_conversation_information_by_ticket_uuid', args=[str(invalid_ticket_uuid)])

        response = self.client.get(url)
        print(response.data)

        # Assert that the status code is 400 (Bad Request) for invalid ticket UUID
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the error message is present in the 'result' field of the response
        self.assertEqual(response.data['result'], ErrorMessages.CHAT_CONVERSATION_NOT_FOUND)

        # Additional assertions to validate status and code
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['code'], 400)

    def test_total_conversation_info_invalid_or_missing_ticket_uuid(self):
        """
           Test that the API raises a CustomException when the ticket UUID is missing or invalid.
        """
        # Case 1: Missing ticket_uuid (empty string)
        url = reverse("ChatBot:total_conversation_information_by_ticket_uuid", args=["  "])  # Simulate missing UUID
        response = self.client.get(url)

        # Assert that the API returns a 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the error message matches the expected error message
        self.assertEqual(response.data['result'], ErrorMessages.TICKET_UUID_NOT_NULL)
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['code'], 400)

