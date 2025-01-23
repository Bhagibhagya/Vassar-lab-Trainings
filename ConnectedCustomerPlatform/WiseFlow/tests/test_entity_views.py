import uuid
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException
from EmailApp.constant.constants import EmailDashboardParams
from WiseFlow.constants.success_messages import EntitySuccessMessages


class AddEntityExamplesTestCase(APITestCase):
    """Test case for add_entity_examples API"""

    def setUp(self):
        """Set up test data and mocks"""
        super().setUp()
        self.customer_uuid = str(uuid.uuid4())
        self.application_uuid = str(uuid.uuid4())
        self.entity_uuid = str(uuid.uuid4())
        self.entity_name = "Test Entity"
        self.examples = [
            {"input": {"key": "value1"}, "output": "output1"},
            {"input": {"key": "value2"}, "output": "output2"}
        ]
        self.payload = {
            "entity_uuid": self.entity_uuid,
            "entity_name": self.entity_name,
            "examples": self.examples,
            "is_default": True
        }
        self.headers = {
            "HTTP_CUSTOMER_UUID": self.customer_uuid,
            "HTTP_APPLICATION_UUID": self.application_uuid
        }

    @patch("WiseFlow.services.impl.entity_service_impl.VectorDBFactory.instantiate")
    @patch("WiseFlow.views.entity_views.EntityExamplesRequestPayloadSerializer")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_add_entity_examples_success(self, mock_validate_uuids, mock_serializer, mock_vector_db_factory):
        """Test successful addition of entity examples"""
        # Mock serializer
        mock_serializer.return_value.is_valid.return_value = True
        mock_serializer.return_value.validated_data = self.payload
        mock_validate_uuids.return_value=None
        # Mock the VectorDB service
        mock_vector_db_service = MagicMock()
        mock_vector_db_factory.return_value = mock_vector_db_service

        url = reverse("add_entity_examples")
        response = self.client.post(url, data=self.payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"], EntitySuccessMessages.EXAMPLES_ADDED_SUCCESS)
        mock_serializer.assert_called_once_with(data=self.payload)
        mock_vector_db_service.add_chunks_sync.assert_called()

    @patch("WiseFlow.views.entity_views.EntityExamplesRequestPayloadSerializer")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_add_entity_examples_serializer_validation_error(self, mock_validate_uuids, mock_serializer):
        """Test serializer validation error during entity examples addition"""
        # Mock serializer
        mock_serializer.return_value.is_valid.return_value = False
        mock_serializer.return_value.errors = {"examples": ["This field is required."]}
        mock_validate_uuids.return_value = None

        url = reverse("add_entity_examples")
        response = self.client.post(url, data=self.payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("examples", response.data["detail"])
        mock_serializer.assert_called_once_with(data=self.payload)

    @patch("WiseFlow.views.entity_views.EntityExamplesRequestPayloadSerializer")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_add_entity_examples_invalid_uuid(self, mock_validate_uuids, mock_serializer):
        """Test invalid UUIDs in request headers"""
        mock_validate_uuids.side_effect = InvalidValueProvidedException(
            detail={"customer-uuid": "Invalid UUID format"}, status_code=status.HTTP_400_BAD_REQUEST
        )

        url = reverse("add_entity_examples")
        response = self.client.post(url, data=self.payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer-uuid", response.data['result'])
        mock_validate_uuids.assert_called_once()

    @patch("WiseFlow.services.impl.entity_service_impl.VectorDBFactory.instantiate")
    @patch("WiseFlow.views.entity_views.EntityExamplesRequestPayloadSerializer")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_add_entity_examples_json_decode_error(self, mock_validate_uuids, mock_serializer, mock_vector_db_factory):
        """Test JSON decoding error during entity examples addition"""
        # Mock serializer
        mock_serializer.return_value.is_valid.return_value = True
        invalid_payload = {
            "entity_uuid": "valid-uuid",
            "entity_name": "Test Entity",
            "examples": [
                {
                    "input": {"key": set([1, 2, 3])},  # Non-serializable set
                    "output": "Sample Output"
                }
            ],
            "is_default": True
        }
        mock_serializer.return_value.validated_data = invalid_payload
        mock_validate_uuids.return_value = None

        url = reverse("add_entity_examples")
        response = self.client.post(url, data=invalid_payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Failed to decode example text as JSON", response.data["result"])

    @patch("WiseFlow.services.impl.entity_service_impl.VectorDBFactory.instantiate")
    @patch("WiseFlow.views.entity_views.EntityExamplesRequestPayloadSerializer")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_add_entity_examples_vectordb_failure(self, mock_validate_uuids, mock_serializer, mock_vector_db_factory):
        """Test VectorDB failure during entity examples addition"""
        # Mock serializer
        mock_serializer.return_value.is_valid.return_value = True
        mock_serializer.return_value.validated_data = self.payload
        mock_validate_uuids.return_value = None

        # Mock VectorDB failure
        mock_vector_db_service = MagicMock()
        mock_vector_db_service.add_chunks_sync.side_effect = Exception("Database error")
        mock_vector_db_factory.return_value = mock_vector_db_service

        url = reverse("add_entity_examples")
        response = self.client.post(url, data=self.payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Cannot add entity examples to chroma", response.data["result"])

    @patch("WiseFlow.views.entity_views.EntityExamplesRequestPayloadSerializer")
    def test_add_entity_examples_missing_headers(self, mock_serializer):
        """Test missing headers during entity examples addition"""

        # Remove headers
        headers = {"HTTP_CUSTOMER_UUID": None, "HTTP_APPLICATION_UUID": None}

        url = reverse("add_entity_examples")
        response = self.client.post(url, data=self.payload, headers=headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer-uuid should be valid uuid", response.data["result"])
        self.assertIn("application-uuid should be valid uuid", response.data["result"])

from unittest.mock import patch, MagicMock
from rest_framework.reverse import reverse
from rest_framework import status
from WiseFlow.constants.success_messages import EntitySuccessMessages
from WiseFlow.constants.error_messages import EntityErrorMessages
import uuid
import json

class TestEntityPromptViewSet(APITestCase):
    def setUp(self):
        """Set up test data and mocks"""
        super().setUp()
        self.customer_uuid = str(uuid.uuid4())
        self.application_uuid = str(uuid.uuid4())
        self.entity_uuid = str(uuid.uuid4())
        self.chat_history = [
            {"source": "user", "message": "What is the price?"},
            {"source": "ai", "message": "The price is $20."}
        ]
        self.payload = {
            "entity_uuid": self.entity_uuid,
            "chat_history": self.chat_history,
            "previous_value_of_entity": "Value before",
            "user_query": "What's the updated value?"
        }
        self.headers = {
            "HTTP_CUSTOMER_UUID": self.customer_uuid,
            "HTTP_APPLICATION_UUID": self.application_uuid
        }

    @patch("WiseFlow.services.impl.entity_service_impl.EntityDaoImpl.get_entity_details")
    @patch("WiseFlow.services.impl.entity_service_impl.LLM.run_sync")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_test_entity_prompt_success(self,mock_validate_uuid, mock_llm_run, mock_get_entity_details):
        """Test successful entity prompt response"""
        mock_validate_uuid.return_value=None

        # Mock `get_entity_details`
        mock_get_entity_details.return_value = (
            "TestEntity",
            "system",
            "Provide details for {today_date}",
            "Test Description",
            {"format": "json"}
        )
        # Mock LLM response
        mock_llm_run.return_value = '{"response": "Updated value is 30"}'

        url = reverse("test_entity_prompt")
        response = self.client.post(url, data=self.payload, headers=self.headers, format="json")

        # Assertions
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("prompt_response", response.data["result"])
        self.assertIn("prompt", response.data["result"])
        mock_get_entity_details.assert_called_once_with(self.entity_uuid)

    @patch("WiseFlow.services.impl.entity_service_impl.EntityDaoImpl.get_entity_details")
    @patch("WiseFlow.services.impl.entity_service_impl.LLM.run_sync")
    def test_test_entity_prompt_validation_error(self, mock_llm_run, mock_get_entity_details):
        """Test validation error during entity prompt"""
        invalid_payload = {"invalid_field": "value"}
        url = reverse("test_entity_prompt")
        response = self.client.post(url, data=invalid_payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer-uuid should be valid uuid", response.data["result"])
        self.assertIn("application-uuid should be valid uuid", response.data["result"])
        mock_llm_run.assert_not_called()
        mock_get_entity_details.assert_not_called()

    @patch("WiseFlow.services.impl.entity_service_impl.EntityDaoImpl.get_entity_details")
    @patch("WiseFlow.services.impl.entity_service_impl.LLM.run_sync")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_test_entity_prompt_llm_json_error(self,mock_validate_uuids, mock_llm_run, mock_get_entity_details):
        """Test JSON decode error from LLM response"""
        # Mock `get_entity_details`
        mock_get_entity_details.return_value = (
            "TestEntity",
            "system",
            "Provide details for {today_date}",
            "Test Description",
            {"format": "json"}
        )
        # Mock invalid LLM response
        mock_llm_run.return_value = {"key": {1, 2, 3}}

        url = reverse("test_entity_prompt")
        response = self.client.post(url, data=self.payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("prompt_response", response.data["result"])
        mock_get_entity_details.assert_called_once_with(self.entity_uuid)

    @patch("WiseFlow.services.impl.entity_service_impl.EntityDaoImpl.get_entity_details")
    @patch("WiseFlow.views.entity_views.validate_uuids_dict")
    def test_test_entity_prompt_invalid_ownership(self, mock_validate_uuids,mock_get_entity_details):
        """Test JSON decode error from LLM response"""
        # Mock `get_entity_details`
        mock_get_entity_details.return_value = (
            "TestEntity",
            "invalid",
            "Provide details for {today_date}",
            "Test Description",
            {"format": "json"}
        )
        # Mock invalid LLM response

        url = reverse("test_entity_prompt")
        response = self.client.post(url, data=self.payload, headers=self.headers, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid ownership found', response.data["result"])
        mock_get_entity_details.assert_called_once_with(self.entity_uuid)

