import uuid

from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status


class KnowLedgeSourceViewTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mock_knowledge_source_service = MagicMock()

    @patch("ChatBot.views.files.get_service")
    def test_get_files_for_qa(self, mock_get_service):
        mock_get_service.return_value = self.mock_knowledge_source_service
        mock_data = [
            {'knowledge_source_uuid': '123', 'knowledge_source_name': 'test_file_1'},
            {'knowledge_source_uuid': '456', 'knowledge_source_name': 'test_file_2'}
        ]
        self.mock_knowledge_source_service.get_knowledge_sources_for_question_and_answer.return_value = mock_data
        headers = {
            'Customer-UUID': 'customer-uuid-123',
            'Application-UUID': 'application-uuid-456'
        }
        response = self.client.get(reverse('ChatBot:get_files_for_questions_and_answers'), headers=headers)
        self.assertIsNotNone(response)
        result_data = list(response.data['result'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result_data, [
            {'knowledge_source_uuid': '123', 'knowledge_source_name': 'test_file_1'},
            {'knowledge_source_uuid': '456', 'knowledge_source_name': 'test_file_2'},
        ])

    @patch("ChatBot.views.files.get_service")
    def test_get_videos_in_applications(self, mock_get_service):
        mock_get_service.return_value = self.mock_knowledge_source_service
        mock_data = {
            'videos': [
                {
                    'knowledge_source_name': 'test_file_1',
                    'knowledge_source_uuid': '123',
                    'knowledge_source_url': 'https://mockurl.com/presigned-url',
                    'duration': None
                }
            ],
            'message': 'videos fetched successfully'
        }
        self.mock_knowledge_source_service.get_video_type_knowledge_sources_in_application.return_value = mock_data
        headers = {
            'Customer-UUID': 'customer-uuid-123',
            'Application-UUID': 'application-uuid-456'
        }
        response = self.client.get(reverse('ChatBot:get_videos_in_application'), headers=headers)
        self.assertIsNotNone(response)
        result_data = response.data['result']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'videos': [
                {
                    'knowledge_source_name': 'test_file_1',
                    'knowledge_source_uuid': '123',
                    'knowledge_source_url': 'https://mockurl.com/presigned-url',
                    'duration': None
                }
            ],
            'message': 'videos fetched successfully'
        }
        self.assertEqual(result_data, expected_data)

    @patch("ChatBot.views.files.get_service")
    def test_get_internal_json(self, mock_get_service):
        mock_get_service.return_value = self.mock_knowledge_source_service
        mock_data = {
            "message": "internal json fetched successfully",
            "review_json": {
                "metadata": {
                    "source": "door_manual.pdf",
                    "title": "Installation Manual",
                    "page_count": 51,
                    "language": "en-US"
                },
                "pages": {
                    1: [
                        {
                            "page": 1,
                            "content_type": "text",
                            "text": {
                                "type": "Body",
                                "content": "ProCare™ 8500"
                            },
                            "block_id": "eadf90bb-485b-4b12-89bc-6021c1cf0351",
                            "level": 1
                        },
                        {
                            "page": 1,
                            "content_type": "text",
                            "text": {
                                "type": "H1",
                                "content": "MANUAL AND AUTOMATIC TELESCOPIC ICU DOOR SYSTEM INSTALLATION AND OPERATION MANUAL"
                            },
                            "block_id": "96b4dc2c-7c4b-4e41-88d3-9c8c5ed01763",
                            "level": 1
                        }
                    ]
                }
            },
            "file_status": "Processing",
            "enable_review": True
        }

        self.mock_knowledge_source_service.get_knowledge_source_internal_json.return_value = mock_data
        expected_response = {
            "message": "internal json fetched successfully",
            "review_json": {
                "metadata": {
                    "source": "door_manual.pdf",
                    "title": "Installation Manual",
                    "page_count": 51,
                    "language": "en-US"
                },
                "pages": {
                    1: [
                        {
                            "page": 1,
                            "content_type": "text",
                            "text": {
                                "type": "Body",
                                "content": "ProCare™ 8500"
                            },
                            "block_id": "eadf90bb-485b-4b12-89bc-6021c1cf0351",
                            "level": 1
                        },
                        {
                            "page": 1,
                            "content_type": "text",
                            "text": {
                                "type": "H1",
                                "content": "MANUAL AND AUTOMATIC TELESCOPIC ICU DOOR SYSTEM INSTALLATION AND OPERATION MANUAL"
                            },
                            "block_id": "96b4dc2c-7c4b-4e41-88d3-9c8c5ed01763",
                            "level": 1
                        }
                    ]
                }
            },
            "file_status": "Processing",
            "enable_review": True
        }
        url = reverse('ChatBot:get_internal_json', kwargs={'file_uuid': uuid.uuid4()})
        response = self.client.get(url, headers=None)
        self.assertIsNotNone(response)
        result_data = response.data['result']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result_data, expected_response)

    @patch("ChatBot.views.files.get_service")
    def check_knowledge_sources_exists(self, mock_get_service):
        mock_get_service.return_value = self.mock_knowledge_source_service
        mock_data = {
        "knowledge_sources": [
            {
                "knowledge_source_name": "test_file_1",
                "exists": True
            }
        ]
    }
        self.mock_knowledge_source_service.check_knowledge_sources_exists.return_value = mock_data
        headers = {
            'Customer-UUID': 'customer-uuid-123',
            'Application-UUID': 'application-uuid-456'
        }
        response = self.client.get(reverse('ChatBot:get_files_for_questions_and_answers'), headers=headers)
        self.assertIsNotNone(response)
        result_data = (response.data['result'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result_data, mock_data)

    @patch("ChatBot.views.files.get_service")
    def test_check_knowledge_sources_exists(self, mock_get_service):
            mock_get_service.return_value = self.mock_knowledge_source_service
            # Mock data returned by the service
            mock_data = {
                "knowledge_sources": [
                    {
                        "knowledge_source_name": "test_file_1",
                        "exists": True
                    }
                ]
            }
            
            # Mock the service method's return value
            self.mock_knowledge_source_service.return_value.check_knowledge_sources_exists.return_value = mock_data

            # Define request data
            request_data = {
                "knowledge_source_names": ["test_file_1"]
            }
            
            # Send a POST request
            response = self.client.post(
                reverse('ChatBot:get_files_for_questions_and_answers'),
                data=request_data,
                content_type="application/json",
                **{
                    'HTTP_Customer-UUID': 'customer-uuid-123',
                    'HTTP_Application-UUID': 'application-uuid-456'
                }
            )
            
            # Assertions
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result_data = response.data['result']
            self.assertEqual(result_data, mock_data)
