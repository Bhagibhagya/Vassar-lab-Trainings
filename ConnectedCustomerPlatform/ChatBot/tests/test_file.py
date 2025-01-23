from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
import uuid

from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.tests.test_data import create_test_knowledge_source_data, get_mocked_knowledge_source_data, \
    fetch_internal_json, create_test_error_data


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

class FileViewSetTestCase(BaseTestCase):
    ###
    # ========= Tests for "generate_formatted_internal_json" API ==========
    ###
    def setUp(self):
        super().setUp()  # Call the base setup
        (
            self.knowledge_source,
            self.application_uuid,
            self.customer_uuid
        ) = create_test_knowledge_source_data()


    # 1 with success-full fetching
    @patch('ChatBot.services.impl.knowledge_source_service_impl.KnowledgeSourceServiceImpl.fetch_internal_json')
    # @patch('ChatBot.services.impl.knowledge_source_service_impl.KnowledgeSourceServiceImpl._KnowledgeSourceServiceImpl__fetch_internal_json')
    def test_generate_formatted_internal_json(self, mock_fetch_internal_json):

        knowledge_source_uuid = self.knowledge_source.knowledge_source_uuid

        mock_fetch_internal_json.return_value = (get_mocked_knowledge_source_data(knowledge_source=self.knowledge_source), fetch_internal_json())

        page_number = "1"
        response = self.client.get(
            reverse('ChatBot:generate_formatted_internal_json', kwargs={'knowledge_source_uuid': knowledge_source_uuid, 'page_number': page_number})
        )
        print("response1 :: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("review_json", response.data['result'])

    # 2 without knowledge_source_uuid i.e None
    def test_generate_formatted_internal_json_missing_knowledge_source_uuid(self):
        page_number = "1"
        response = self.client.get(
            reverse(
                'ChatBot:generate_formatted_internal_json',
                kwargs={
                    'knowledge_source_uuid': " ",
                    'page_number': page_number
                }
            )
        )
        print("response2 :: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ErrorMessages.KNOWLEDGE_SOURCE_UUID_NOT_NULL, response.data['result'])

    # 3 without page_number i.e None
    def test_generate_formatted_internal_json_missing_page_number(self):
        knowledge_source_uuid = self.knowledge_source.knowledge_source_uuid
        response = self.client.get(
            reverse(
                'ChatBot:generate_formatted_internal_json',
                kwargs={
                    'knowledge_source_uuid': knowledge_source_uuid,
                    'page_number': " "
                }
            )
        )

        print("response3 :: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ErrorMessages.PAGE_NUMBER_NOT_NULL, response.data['result'])

    # 4 enable_review is True
    @patch('ChatBot.services.impl.knowledge_source_service_impl.KnowledgeSourceServiceImpl.fetch_internal_json')
    def test_generate_formatted_internal_json_enable_review_true(self, mock_fetch_internal_json):

        mock_fetch_internal_json.return_value = (get_mocked_knowledge_source_data(knowledge_source=self.knowledge_source), fetch_internal_json())
        knowledge_source_uuid = self.knowledge_source.knowledge_source_uuid
        page_number = "1"
        response = self.client.get(
            reverse('ChatBot:generate_formatted_internal_json',
                    kwargs={'knowledge_source_uuid': knowledge_source_uuid, 'page_number': page_number})
        )
        print("response4 :: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(True, response.data['result'].get("enable_review"))

    # 5 enable_review is False
    @patch('ChatBot.services.impl.knowledge_source_service_impl.KnowledgeSourceServiceImpl.fetch_internal_json')
    def test_generate_formatted_internal_json_enable_review_false(self, mock_fetch_internal_json):
        knowledge_source_uuid = self.knowledge_source.knowledge_source_uuid
        error = create_test_error_data(self.knowledge_source.knowledge_source_uuid, self.application_uuid, self.customer_uuid)
        mock_fetch_internal_json.return_value = (get_mocked_knowledge_source_data(knowledge_source=self.knowledge_source), fetch_internal_json())
        page_number = "1"
        response = self.client.get(
            reverse('ChatBot:generate_formatted_internal_json',
                    kwargs={'knowledge_source_uuid': knowledge_source_uuid, 'page_number': page_number})
        )
        print("response5 :: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(False, response.data['result'].get("enable_review"))
