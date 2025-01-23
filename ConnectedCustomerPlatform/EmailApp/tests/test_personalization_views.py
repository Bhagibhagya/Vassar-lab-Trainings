import uuid
from datetime import datetime

from django.db import connection
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import os
from unittest.mock import Mock, patch,MagicMock
from EmailApp.dao.impl.dimension_dao_impl import DimensionDaoImpl
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch
import pandas as pd
from io import BytesIO


from ConnectedCustomerPlatform.responses import CustomResponse
import EmailApp.views.personalization_views
from AIServices.VectorStore.chromavectorstore import chroma_obj, ChromaVectorStore
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidCollectionException,InvalidValueProvidedException
from DatabaseApp.models import CustomerApplicationMapping, Applications, Customers, DimensionsView

from EmailApp.constant.constants import BULK_IMPORT_EXCEL_FILE, SPREAD_SHEET_CONTENT_TYPE, CsrChromaDbFields, \
    DimensionTypeNames, ChromaExcelSheetColumns

from EmailApp.constant.error_messages import ErrorMessages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from Platform.constant.error_messages import ErrorMessages as PlatformErrorMessages

from EmailApp.constant.success_messages import SuccessMessages
from EmailApp.constant.constants import DefaultResponsesTemplate, CsrChromaDbFields, EmailDashboardParams
from EmailApp.services.impl.personalization_service_impl import PersonalizationServiceImpl
from DatabaseApp.models import DimensionCustomerApplicationMapping,DimensionType,Dimension,Applications, Customers
from django.conf import settings

class DeleteEmailResponsesTest(APITestCase):
    def setUp(self):
        self.url = reverse('EmailApp:response_configurations')
        self.valid_params = {
            CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: "response-config-uuid"
        }

    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value=None)
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.delete_emails_by_metadata', return_value=["deleted_id_1", "deleted_id_2"])
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application', return_value="test_collection")
    def test_delete_emails_responses_success(self, mock_get_collection_name, mock_delete_emails, mock_validate_uuids):
        response = self.client.delete(
            self.url,
            **{'QUERY_STRING': f"{CsrChromaDbFields.RESPONSE_CONFIG_UUID.value}=response-config-uuid"},
            HTTP_CUSTOMER_UUID="customer_uuid",
            HTTP_USER_UUID="user_uuid",
            HTTP_ROLE_UUID="role_uuid",
            HTTP_APPLICATION_UUID="application_uuid"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Responses record successfully deleted", response.data['result'])

    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value=None)
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.delete_emails_by_metadata', return_value=None)
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application', return_value="test_collection")
    def test_delete_emails_responses_no_ids_deleted(self, mock_get_collection_name, mock_delete_emails, mock_validate_uuids):
        response = self.client.delete(
            self.url,
            **{'QUERY_STRING': f"{CsrChromaDbFields.RESPONSE_CONFIG_UUID.value}=response-config-uuid"},
            HTTP_CUSTOMER_UUID="customer_uuid",
            HTTP_USER_UUID="user_uuid",
            HTTP_ROLE_UUID="role_uuid",
            HTTP_APPLICATION_UUID="application_uuid"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('The specified response configuration is not present', response.data['result'])

class SaveResponseConfigurationsTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('EmailApp:response_configurations')
        self.valid_data = {
            CsrChromaDbFields.INTENT.value: "Intent",
            CsrChromaDbFields.SUB_INTENT.value: "SubIntent",
            CsrChromaDbFields.SENTIMENT.value: "Positive",
            CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: "response-config-uuid",
            CsrChromaDbFields.IS_DEFAULT.value: True,
            CsrChromaDbFields.TEXT_TO_SHOW.value: "Text to show"
        }
        self.headers = {
            "HTTP_CUSTOMER_UUID": "customer_uuid",
            "HTTP_USER_UUID": "user_uuid",
            "HTTP_APPLICATION_UUID": "application_uuid",
            "HTTP_ROLE_UUID": "role_uuid"
        }
        self.mock_excel_file = SimpleUploadedFile(
            "temp.xlsx", 
            b"Excel content", 
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    @patch('StorageServices.azure_services.AzureBlobManager.upload_attachments_to_azure_blob')
    @patch('EmailApp.services.impl.personalization_service_impl.parse_excel_to_list_of_examples')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.delete_emails_by_metadata')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.add_emails_and_metadata')
    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    def test_save_response_configurations_success(self,mock_validate_dict, mock_add_emails, mock_delete_emails, mock_get_collection, mock_parse_excel, mock_upload_azure):
        """
        Test saving response configurations successfully.
        """
        # Mock return values
        mock_validate_dict.return_value=None
        mock_parse_excel.return_value = [{"email": "test@example.com", "response": "Test response"}]
        mock_upload_azure.return_value = ["https://azure.blob.core.windows.net/responses.xlsx"]
        mock_get_collection.return_value = "chroma-collection"
        mock_delete_emails.return_value = ["doc1", "doc2"]
        mock_add_emails.return_value = ["id1", "id2"]

        # Create a temp file
        temp_file_path = 'temp.xlsx'
        
        try:
            # Write to the temp file
            with open(temp_file_path, 'wb') as f:
                f.write(b'Excel content')

            # Open the temp file for reading
            with open(temp_file_path, 'rb') as excel_file:
            # Make API request with mocked data
                response = self.client.post(
                            self.url,
                            data={**self.valid_data, CsrChromaDbFields.RESPONSES_FILE.value: excel_file},  # Use the constant for the file key
                            format='multipart',  # multipart format for file upload
                            **self.headers
                        )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["result"], "Successfully uploaded responses as examples")

            # Check if all mocks are called with correct arguments
            mock_parse_excel.assert_called_once_with(b'Excel content')
            mock_upload_azure.assert_called_once()
            mock_get_collection.assert_called_once_with(customer_uuid="customer_uuid", application_uuid="application_uuid")
            mock_delete_emails.assert_called()
            mock_add_emails.assert_called()
        finally:
            # Ensure the temporary file is removed after the test
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    @patch('StorageServices.azure_services.AzureBlobManager.upload_attachments_to_azure_blob')
    @patch('EmailApp.services.impl.personalization_service_impl.parse_excel_to_list_of_examples')
    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    def test_save_response_configurations_error_during_upload(self, mock_validate_dict,mock_parse_excel, mock_upload_azure):
        """
        Test error case where the file upload to Azure fails.
        """
        # Mock return values for the services
        mock_validate_dict.return_value=None
        mock_parse_excel.return_value = [{"email": "test@example.com", "response": "Test response"}]
        mock_upload_azure.return_value = None  # Simulate failure of Azure upload

        # Create a temp file
        temp_file_path = 'temp.xlsx'
        
        try:
            # Write to the temp file
            with open(temp_file_path, 'wb') as f:
                f.write(b'Excel content')

            # Open the temp file for reading
            with open(temp_file_path, 'rb') as excel_file:
                
                response = self.client.post(
                    self.url, 
                    data={**self.valid_data, CsrChromaDbFields.RESPONSES_FILE.value: excel_file}, 
                    format='multipart', 
                    **self.headers
                )
            # Check for the expected error response
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn("Error occured while uploading the file", response.data["result"])

            # Assert that the mock methods were called as expected
            mock_parse_excel.assert_called_once_with(b'Excel content')
            mock_upload_azure.assert_called_once()
        
        finally:
            # Ensure the temporary file is removed after the test
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    
    @patch('EmailApp.views.personalization_views.ResponseConfigurationRequestPayloadSerializer')
    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    def test_save_response_configurations_validation_error(self, mock_validator,mock_serializer):
        """
        Test the case where serializer validation fails.
        """
        # Create a mock instance of the serializer
        instance = MagicMock()
        instance.is_valid.return_value = False
        instance.errors = {"intent": ["This field is required."]}
        mock_serializer.return_value = instance
        mock_validator.return_value=None
        # Perform the POST request with invalid data
        response = self.client.post(
            self.url, 
            data={},  # Invalid data
            format='multipart', 
            **self.headers
        )

        # Assert the error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["result"], {"intent": ["This field is required."]})

        # Ensure that validation was called once
        instance.is_valid.assert_called_once()


    @patch('StorageServices.azure_services.AzureBlobManager.upload_attachments_to_azure_blob')
    @patch('EmailApp.services.impl.personalization_service_impl.parse_excel_to_list_of_examples')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.add_emails_and_metadata')
    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    def test_save_response_configurations_success2(self,mock_validate_dict, mock_add_emails, mock_get_collection, mock_parse_excel, mock_upload_azure):
        """
        Test saving response configurations successfully
        """
        valid_data2= {
            CsrChromaDbFields.INTENT.value: "Intent",
            CsrChromaDbFields.SUB_INTENT.value: "SubIntent",
            CsrChromaDbFields.SENTIMENT.value: "Positive",
            CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: "",
            CsrChromaDbFields.IS_DEFAULT.value: True,
            CsrChromaDbFields.TEXT_TO_SHOW.value: "Text to show"
        }
        # Mock return values
        mock_validate_dict.return_value=None
        mock_parse_excel.return_value = [{"email": "test@example.com", "response": "Test response"}]
        mock_upload_azure.return_value = ["https://azure.blob.core.windows.net/responses.xlsx"]
        mock_get_collection.return_value = "chroma-collection"
        mock_add_emails.return_value = ["id1", "id2"]

        # Create a temp file
        temp_file_path = 'temp.xlsx'
        
        try:
            # Write to the temp file
            with open(temp_file_path, 'wb') as f:
                f.write(b'Excel content')

            # Open the temp file for reading
            with open(temp_file_path, 'rb') as excel_file:
            # Make API request with mocked data
                response = self.client.post(
                            self.url,
                            data={**valid_data2, CsrChromaDbFields.RESPONSES_FILE.value: excel_file},  # Use the constant for the file key
                            format='multipart',  # multipart format for file upload
                            **self.headers
                        )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["result"], "Successfully uploaded responses as examples")

            # Check if all mocks are called with correct arguments
            mock_parse_excel.assert_called_once_with(b'Excel content')
            mock_upload_azure.assert_called_once()
            mock_get_collection.assert_called_once_with(customer_uuid="customer_uuid", application_uuid="application_uuid")
            mock_add_emails.assert_called()
        finally:
            # Ensure the temporary file is removed after the test
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)


class DownloadUploadedTemplateViewTest(APITestCase):

    def setUp(self):
    
        self.url = reverse('EmailApp:download_template')
    
    @patch('EmailApp.services.impl.personalization_service_impl.get_metadata_and_presigned_url')
    def test_download_template_success(self, mock_get_metadata_and_presigned_url):
        mock_url =settings.RESPONSE_CONFIGS_TEMPLATE_URL
        mock_template_data = {
            "template_name": "sample_template.xlsx",
            "content": "<base64_encoded_data>"
        }
        mock_get_metadata_and_presigned_url.return_value = mock_template_data
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], mock_template_data)
        mock_get_metadata_and_presigned_url.assert_called_once_with(mock_url)

    @patch('EmailApp.services.impl.personalization_service_impl.get_metadata_and_presigned_url')
    def test_download_template_service_failure(self, mock_get_metadata_and_presigned_url):
        mock_get_metadata_and_presigned_url.side_effect = Exception("Azure error")

        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['result'], "An error occurred while downloading template: Azure error")
        mock_get_metadata_and_presigned_url.assert_called_once()

class GenerateUtterancesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('EmailApp:generate_utterances')

    def test_generate_utterances_success(self):
        # Mock the LLM response

        # Define payload for the request
        payload = {
            'intent': 'Order Status',
            'description': 'Help customers with order status inquiries'
        }

        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name for the view
            payload,
            format='json'
        )

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_exception_in_utterances_not_provided_generate_utterances_success(self):
        # Define payload for the request
        payload = {
            'intent': None,
            'description': 'Help customers with order status inquiries'
        }

        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name for the view
            payload,
            format='json'
        )

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exception_in_LLM_generate_utterances_success(self):
        # Define payload for the request
        payload = {
            'intent': 'Order Status',
            'description': 'Help customers with order status inquiries'
        }
        with patch.object(EmailApp.views.personalization_views.LLMChain,'query',side_effect=Exception("Exception in LLM")):
            # Make POST request
            response = self.client.post(
                self.url,  # Replace with the correct URL name for the view
                payload,
                format='json'
            )

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_Json_decode_exception_in_LLM__generate_utterances_success(self):
        # Define payload for the request
        payload = {
            'intent': 'Order Status',
            'description': 'Help customers with order status inquiries'
        }
        with patch.object(EmailApp.views.personalization_views.LLMChain,'query',return_value="utterance"):
            # Make POST request
            response = self.client.post(
                self.url,  # Replace with the correct URL name for the view
                payload,
                format='json'
            )

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetUtterancesByIntentTests(APITestCase):

    def setUp(self):

        self.client = APIClient()
        self.url = reverse('EmailApp:utterances_configuration')
        self.headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3",
            "HTTP_USER_UUID":"af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }
        self.applications = Applications.objects.create(application_uuid="e912de61-96c0-4582-89aa-64de807a4635")
        self.customers = Customers.objects.create(cust_uuid="af4bf2d8-fd3e-4b40-902a-1217952c0ff3")
        self.customer_application_mapping = CustomerApplicationMapping.objects.create(
            customer_application_id = "mapping_uuid",
            customer = self.customers,
            application = self.applications
        )

    @patch('EmailApp.services.impl.personalization_service_impl.ChromaVectorStore.get_records_by_metadata_with_specific_fields')
    def test_get_utterances_by_intent_sub_intent_success(self,mock_get_emails):
        # Mock the responses
        mock_get_emails.return_value = {
            'ids': ['1e9b02b7-f981-4528-baa1-0cfdc9cfc2bd', 'bc6a6803-4ed3-438f-b14c-fc8fa4ff5f8a',
                    'e7e28ed7-1061-4c06-9fc0-d21d35d811d3'], 'embeddings': None, 'metadatas': [
                {'category': 'intent_classification',"INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True, 'created_at': '2024-09-16 06:59:02.576503',
                 'updated_at': '2024-09-17 06:38:56.600860'},
                {'category': 'intent_classification',"INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True, 'created_at': '2024-09-16 06:59:00.007896',
                 'updated_at': '2024-09-16 06:59:00.007896'},
                {'category': 'intent_classification',"INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True, 'created_at': '2024-09-16 06:59:02.079360',
                 'updated_at': '2024-09-17 06:38:56.984155'}],
            'documents': ['"I want to know if my order has been packed. edited"', '"Has my order been packed?"',
                          '"Can you confirm if my order has been packed? wait a min"'], 'data': None, 'uris': None}

        # Define the payload and headers
        payload = {
            'parent_dimension_name':"intent",
            'dimension_names': ['subIntent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **self.headers
        )
        # Assert the mock methods were called with the correct arguments
        mock_get_emails.assert_called_once()

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response data structure
        self.assertIn('result', response.json())
        self.assertIn('data', response.json()['result'])

    @patch('EmailApp.services.impl.personalization_service_impl.ChromaVectorStore.get_records_by_metadata')
    def test_get_utterances_by_sub_intent_success(self, mock_get_emails):
        # Mock the responses
        mock_get_emails.return_value = {
            'ids': ['1e9b02b7-f981-4528-baa1-0cfdc9cfc2bd', 'bc6a6803-4ed3-438f-b14c-fc8fa4ff5f8a',
                    'e7e28ed7-1061-4c06-9fc0-d21d35d811d3'], 'embeddings': None, 'metadatas': [
                {'category': 'intent_classification', "INTENT,intent": True, "SUBINTENT,intent,subintent": True,
                 "is_subintent": True, 'created_at': '2024-09-16 06:59:02.576503',
                 'updated_at': '2024-09-17 06:38:56.600860'},
                {'category': 'intent_classification', "INTENT,intent": True, "SUBINTENT,intent,subintent": True,
                 "is_subintent": True, 'created_at': '2024-09-16 06:59:00.007896',
                 'updated_at': '2024-09-16 06:59:00.007896'},
                {'category': 'intent_classification', "INTENT,intent": True, "SUBINTENT,intent,subintent": True,
                 "is_subintent": True, 'created_at': '2024-09-16 06:59:02.079360',
                 'updated_at': '2024-09-17 06:38:56.984155'}],
            'documents': ['"I want to know if my order has been packed. edited"', '"Has my order been packed?"',
                          '"Can you confirm if my order has been packed? wait a min"'], 'data': None, 'uris': None}

        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **self.headers
        )
        # Assert the mock methods were called with the correct arguments
        mock_get_emails.assert_called_once()

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response data structure
        self.assertIn('result', response.json())
        self.assertIn('data', response.json()['result'])

    @patch('EmailApp.services.impl.personalization_service_impl.ChromaVectorStore.get_records_by_metadata')
    def test_get_utterances_by_dimension_empty_list(self, mock_get_emails):
        # Mock the responses
        mock_get_emails.side_effect = InvalidCollectionException("Collection does not exists")

        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **self.headers
        )

        # Assert the mock methods were called with the correct arguments
        mock_get_emails.assert_called_once()

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response data structure
        self.assertIn('result', response.json())
        self.assertIn('data', response.json()['result'])

    @patch('EmailApp.services.impl.personalization_service_impl.ChromaVectorStore.get_records_by_metadata')
    @patch('EmailApp.services.impl.personalization_service_impl.ChromaVectorStore.get_chroma_collection_name_by_customer_application')
    def test_get_utterances_by_dimension_exception(self,mock_collection, mock_get_emails):
        # Mock the responses
        mock_collection.return_value="collection_name"
        mock_get_emails.side_effect = Exception('Collection collection_name does not exist')

        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **self.headers
        )

        # Assert the mock methods were called with the correct arguments
        mock_collection.assert_called_once()
        mock_get_emails.assert_called_once()

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response data structure
        self.assertIn('result', response.json())
        self.assertIn('data', response.json()['result'])

    @patch('EmailApp.services.impl.personalization_service_impl.ChromaVectorStore.get_records_by_metadata')
    @patch(
        'EmailApp.services.impl.personalization_service_impl.ChromaVectorStore.get_chroma_collection_name_by_customer_application')
    def test_get_utterances_by_dimension_unknown_exception(self, mock_collection, mock_get_emails):
        # Mock the responses
        mock_collection.return_value = "collection_name"
        mock_get_emails.side_effect = Exception('Unknown')

        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **self.headers
        )

        # Assert the mock methods were called with the correct arguments
        mock_collection.assert_called_once()
        mock_get_emails.assert_called_once()

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the response data structure
        self.assertIn('result', response.json())

    def test_get_utterances_by_dimension_incorrect_payload(self):
        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry': 5, 'page_number': 1}
        }
        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **self.headers
        )

        # Assert the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_get_utterances_by_dimension_incorrect_customer_uuid(self):
        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        headers = self.headers
        headers['HTTP_CUSTOMER_UUID']="customer_uuid"

        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **headers
        )

        # Assert the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['customer-uuid should be valid uuid'],response.data['result'])

    def test_get_utterances_by_intent_incorrect_application_uuid(self):
        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        headers=self.headers
        headers['HTTP_APPLICATION_UUID']="application_uuid"

        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **headers
        )

        # Assert the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['application-uuid should be valid uuid'],response.data['result'])


    def test_get_utterances_by_user_uuid_incorrect_user_uuid(self):
        # Define the payload and headers
        payload = {
            'dimension_names': ['intent'],
            'params': {'total_entry_per_page': 5, 'page_number': 1}
        }
        headers=self.headers
        headers['HTTP_USER_UUID']="user_uuid"

        # Make POST request
        response = self.client.post(
            self.url,  # Replace with the correct URL name
            payload,
            format='json',
            **headers
        )

        # Assert the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['user-uuid should be valid uuid'],response.data['result'])


class DeleteInChromaServerAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('EmailApp:utterances_configuration')
        self.applications = Applications.objects.create(application_uuid="e912de61-96c0-4582-89aa-64de807a4635")
        self.customers = Customers.objects.create(cust_uuid="af4bf2d8-fd3e-4b40-902a-1217952c0ff3")
        self.customer_application_mapping = CustomerApplicationMapping.objects.create(
            customer_application_id="mapping_uuid",
            customer=self.customers,
            application=self.applications
        )
        # Define the payload and headers
        self.payload = {
            'dimension_names': ['subintent'],
            "parent_dimension_name":"intent"
        }


    def test_delete_success(self):
        """
        Test successful deletion when all parameters are valid.
        """

        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }

        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b79b2"
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}

        with patch.object(EmailApp.services.impl.personalization_service_impl.ChromaVectorStore,'get_record_by_id',return_value=training_phrase) as mock_delete:
            with patch.object(EmailApp.services.impl.personalization_service_impl.DimensionDaoImpl,'reduce_training_phrase_count_for_dimensions') as mock_dimension:
                # Make the delete request
                response = self.client.delete(url_with_params,self.payload,format='json', **headers)

        # Assert the response status is 200 OK and the success message
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['result'], SuccessMessages.UTTERANCE_SUCCESSFULLY_DELETED)

        # Assert that the delete method was called with the correct parameters
        mock_delete.assert_called()

    def test_delete_success_with_mapping_uuid(self):
        """
        Test successful deletion when all parameters are valid.
        """

        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }

        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b79b2"
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}
        with patch.object(EmailApp.services.impl.personalization_service_impl.ChromaVectorStore,'get_record_by_id',return_value=training_phrase) as mock_delete:
            with patch.object(EmailApp.services.impl.personalization_service_impl.DimensionDaoImpl,'reduce_training_phrase_count_for_dimensions') as mock_dimension:
                with patch.object(EmailApp.services.impl.personalization_service_impl.DimensionDaoImpl,
                                  'fetch_dimension_parent_dimension_name_by_dimension_uuid',return_value=('subintent','intent')) as mock_get_dimension:

                    # Make the delete request
                    response = self.client.delete(url_with_params,{"mapping_uuid":str(uuid.uuid4())},format='json', **headers)

        # Assert the response status is 200 OK and the success message
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['result'], SuccessMessages.UTTERANCE_SUCCESSFULLY_DELETED)

        # Assert that the delete method was called with the correct parameters
        mock_delete.assert_called()
        mock_dimension.assert_called()
        mock_get_dimension.assert_called()

    def test_delete_success_intent(self):
        """
        Test successful deletion when all parameters are valid.
        """

        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }
        payload = {
            'dimension_name': ['intent']
        }

        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b79b2"
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,otherintent":True,"SUBINTENT,intent,test_delete_success":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}

        with patch.object(EmailApp.services.impl.personalization_service_impl.ChromaVectorStore,'get_record_by_id',return_value=training_phrase) as mock_delete:
            with patch.object(EmailApp.services.impl.personalization_service_impl.ChromaVectorStore, 'update_metadata_by_id',
                              return_value=training_phrase) as mock_update:

                with patch.object(EmailApp.services.impl.personalization_service_impl.DimensionDaoImpl,'reduce_training_phrase_count_for_dimensions') as mock_dimension:
                    # Make the delete request
                    response = self.client.delete(url_with_params,payload,format='json', **headers)

        # Assert the response status is 200 OK and the success message
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['result'], SuccessMessages.UTTERANCE_SUCCESSFULLY_DELETED)

        # Assert that the delete method was called with the correct parameters
        mock_delete.assert_called()

    def test_delete_success_intent_raise_exception(self):
        """
        Test successful deletion when all parameters are valid.
        """

        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }
        payload = {
            'dimension_name': 'intent'
        }

        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b79b2"
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,otherintent":True,"SUBINTENT,intent,test_delete_success":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}

        with patch.object(EmailApp.services.impl.personalization_service_impl.ChromaVectorStore,'get_record_by_id',return_value=training_phrase) as mock_delete:
            with patch.object(EmailApp.services.impl.personalization_service_impl.ChromaVectorStore, 'update_metadata_by_id',
                              return_value=training_phrase) as mock_update:

                with patch.object(EmailApp.services.impl.personalization_service_impl.DimensionDaoImpl,'reduce_training_phrase_count_for_dimensions') as mock_dimension:
                    # Make the delete request
                    response = self.client.delete(url_with_params,payload,format='json', **headers)

        # Assert the response status is 200 OK and the success message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data['result'], "Invalid Dimension names")


    def test_incorrect_utterance_id(self):
        """
        Test that an error is raised when the utterance_id is incorrect.
        """
        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }
        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b7"

        # Make the delete request without utterance_id
        response = self.client.delete(url_with_params, self.payload, format='json', **headers)

        # Assert the response status is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['id should be valid uuid'],response.data['result'])

    def test_incorrect_customer_uuid(self):
        """
        Test that an error is raised when customer_uuid is incorrect.
        """
        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0"
        }

        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b79b2"
        # Make the delete request without customer_uuid
        response = self.client.delete(url_with_params, self.payload, format='json', **headers)

        # Assert the response status is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['customer-uuid should be valid uuid'], response.data['result'])

    def test_incorrect_application_uuid(self):
        """
        Test that an error is raised when application_uuid is incorrect.
        """
        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a463",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }

        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b79b2"

        # Make the delete request without application_uuid
        response = self.client.delete(url_with_params, self.payload, format='json', **headers)

        # Assert the response status is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['application-uuid should be valid uuid'], response.data['result'])

    def test_delete_raises_exception(self):
        """
        Test that an error is returned when an exception is raised during deletion.
        """
        headers = {
            'HTTP_APPLICATION_UUID': "e912de61-96c0-4582-89aa-64de807a4635",
            'HTTP_CUSTOMER_UUID': "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        }

        url_with_params = f"{self.url}?id=c325a7e5-98a2-47d8-9dda-7b625d8b79b2"
        # Make the delete request
        response = self.client.delete(url_with_params, self.payload, format='json', **headers)

        # Assert the response status is 400 BAD REQUEST and the exception message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid dimension combination", response.data['result'])




class FetchResponseConfigurationsTestCase(APITestCase):
    
    def setUp(self):
        self.url = reverse('EmailApp:response_configurations')  
        self.headers = {
            EmailDashboardParams.CUSTOMER_UUID.value: 'test-customer-uuid',
            EmailDashboardParams.USER_UUID.value: 'test-user-uuid',
            EmailDashboardParams.APPLICATION_UUID.value: 'test-application-uuid'
        }
        self.query_params = {
            CsrChromaDbFields.IS_DEFAULT.value: 'True'
        }
        
    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch('EmailApp.services.impl.personalization_service_impl.get_metadata_and_presigned_url', return_value='http://example.com/file')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_records_by_metadata', return_value={'metadatas': [
        {CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: 'config-uuid-1', CsrChromaDbFields.FILE_URL.value: 'http://example.com/file1'},
        {CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: 'config-uuid-2', CsrChromaDbFields.FILE_URL.value: 'http://example.com/file2'}
    ]})
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application', return_value='test-collection')
    def test_fetch_response_configurations_success_default_user(self, mock_collection_name, mock_get_emails, mock_get_presigned_url, mock_validate_uuids):
        """
        Test successful fetching of response configurations for the default user (CSR admin)
        """
        response = self.client.get(self.url, headers=self.headers, data=self.query_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()['result']
        
        # Assertions for the response data
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['response_config_uuid'], 'config-uuid-1')
        self.assertEqual(response_data[1]['response_config_uuid'], 'config-uuid-2')
        self.assertIn('downloadable_url', response_data[0])

        # Asserting mocked method calls
        mock_validate_uuids.assert_called_once_with({
            EmailDashboardParams.USER_UUID.value: self.headers[EmailDashboardParams.USER_UUID.value],
            EmailDashboardParams.APPLICATION_UUID.value: self.headers[EmailDashboardParams.APPLICATION_UUID.value],
            EmailDashboardParams.CUSTOMER_UUID: self.headers[EmailDashboardParams.CUSTOMER_UUID.value]
        })
        mock_collection_name.assert_called_once_with('test-customer-uuid', 'test-application-uuid')
        mock_get_emails.assert_called_once()

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    def test_fetch_response_configurations_missing_is_default(self, mock_validate_uuids):
        """
        Test failure when `is_default` query parameter is missing
        """
        response = self.client.get(self.url, headers=self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('result', response.json())
        self.assertEqual(response.json()['result'], ErrorMessages.IS_DEFAULT_IS_NONE)
        
    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch('EmailApp.services.impl.personalization_service_impl.get_metadata_and_presigned_url', return_value='http://example.com/file')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_records_by_metadata', return_value={'metadatas': [
        {CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: 'config-uuid-1', CsrChromaDbFields.FILE_URL.value: 'http://example.com/file1'},
        {CsrChromaDbFields.RESPONSE_CONFIG_UUID.value: 'config-uuid-1', CsrChromaDbFields.FILE_URL.value: 'http://example.com/file1'}  # Duplicate
    ]})
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application', return_value='test-collection')
    def test_fetch_response_configurations_duplicate_configs(self, mock_collection_name, mock_get_emails, mock_get_presigned_url, mock_validate_uuids):
        """
        Test fetching response configurations where duplicate metadata is returned, but only unique ones are included
        """
        response = self.client.get(self.url, headers=self.headers, data=self.query_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()['result']
        
        # Assertions for the response data, should only have 1 unique response
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['response_config_uuid'], 'config-uuid-1')

        mock_collection_name.assert_called_once_with('test-customer-uuid', 'test-application-uuid')
        mock_get_emails.assert_called_once()

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch('EmailApp.services.impl.personalization_service_impl.get_metadata_and_presigned_url', return_value='http://example.com/file')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_records_by_metadata', return_value={'metadatas': []})
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application', return_value='test-collection')
    def test_fetch_response_configurations_no_results(self, mock_collection_name, mock_get_emails, mock_get_presigned_url, mock_validate_uuids):
        """
        Test when no response configurations are found
        """
        response = self.client.get(self.url, headers=self.headers, data=self.query_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()['result']
        
        # Assertions for the response data, should be empty
        self.assertEqual(len(response_data), 0)

        mock_collection_name.assert_called_once_with('test-customer-uuid', 'test-application-uuid')
        mock_get_emails.assert_called_once()


class FetchIntentsSubintentsSentimentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = f"{reverse('EmailApp:fetch_intents_subintents_sentiment')}?include_sentiments=true"
        self.headers = {
            EmailDashboardParams.CUSTOMER_UUID.value: "customer_uuid_1",
            EmailDashboardParams.USER_UUID.value: "user_uuid_1",
            EmailDashboardParams.APPLICATION_UUID.value: "app_uuid_1"
        }
        EmailApp.dao.impl.dimension_dao_impl

    @patch('EmailApp.views.personalization_views.validate_uuids_dict',return_value=None)
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.fetch_parent_and_child_dimension_details')
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_dimensions_list_by_dimension_type_name')
    def test_fetch_intents_subintents_sentiment_success(self, mock_filter, mock_get_intents_subintents,mock_validate):
        """
        Test successful response of fetch_intents_subintents_sentiment API.
        This patches the DAO layer filters and raw cursor execution.
        """
        # Mocking filter for sentiment fetching
        mock_filter.return_value = ['Positive', 'Negative']

        # Mocking the DAO method to return intents and sub-intents
        mock_get_intents_subintents.return_value = [DimensionsView(
                mapping_uuid="3c732c14-9a8f-4e6f-a19e-3a61e2464d53",
                dimension_uuid="a23d4fbb-0c32-4e69-9b6c-f89e79c3db9e",
                dimension_name="SHIPMENT_STATUS",
                dimension_description="Checking the status of a shipment.",
                customer_uuid="af4bf2d8-fd3e-4b40-902a-1217952c0ff3",
                application_uuid="e912de61-96c0-4582-89aa-64de807a4635",
                dimension_type_name="INTENT",
                dimension_type_uuid="d1e1c2b8-89b5-4c6e-a3c6-1a6f1f6d1e2e",
                is_default=False,
                dimension_details_json={"details": "Shipment tracking information"},
                inserted_ts=datetime.strptime("2025-01-05 12:23:07.059175", "%Y-%m-%d %H:%M:%S.%f"),
                updated_ts=datetime.strptime("2025-01-05 12:23:07.059175", "%Y-%m-%d %H:%M:%S.%f"),
                child_dimensions=[
                    {
                        "is_default": False,
                        "updated_ts": "2025-01-05T12:23:07.059175",
                        "inserted_ts": "2025-01-05T12:23:07.059175",
                        "child_dimension_name": "CHECK_SHIPMENT_STATUS",
                        "child_dimension_uuid": "f2b1c0a2-3a9c-4c3e-a2a8-b9e4c7e92769",
                        "child_dimension_description": "Checking the status of a shipment.",
                        "child_dimension_details_json": {"details": "Check shipment status request"},
                        "child_dimension_mapping_uuid": "df7a8e0e-bfae-4b52-95e2-144c128b03c3",
                    }
                ]
            )]



        # Making the API request
        response = self.client.get(self.url, **{'HTTP_' + k: v for k, v in self.headers.items()})
        print("asd12",response.data['result'])
        # Expected response format
        expected_data = {
            'intent_subintent': {
                'SHIPMENT_STATUS': ['CHECK_SHIPMENT_STATUS']
            },
            'sentiment': ['Positive', 'Negative']
        }

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], expected_data)
        mock_filter.assert_called_once(
        )
        mock_get_intents_subintents.assert_called_once()

    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_intent_subintents_for_customer_application')
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionCustomerApplicationMapping.objects.filter')
    def test_fetch_intents_subintents_sentiment_missing_headers(self, mock_filter, mock_get_intents_subintents):
        """
        Test response when the required headers are missing.
        """
        # Sending request without required headers
        response = self.client.get(self.url)
        # Assertions for bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user-uuid should be valid uuid', response.data['result'])
        self.assertIn('application-uuid should be valid uuid', response.data['result'])
        self.assertIn('customer-uuid should be valid uuid', response.data['result'])



    @patch('EmailApp.views.personalization_views.validate_uuids_dict',return_value=None)
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.fetch_parent_and_child_dimension_details')
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_dimensions_list_by_dimension_type_name')
    def test_fetch_intents_subintents_sentiment_empty_response(self, mock_filter, mock_get_intents_subintents,mock_validate):
        """
        Test when there are no intents, subintents, or sentiments returned.
        """
        # Mocking empty response for both intents and sentiments
        mock_filter.return_value = []
        mock_get_intents_subintents.return_value = []

        # Making the API request
        response = self.client.get(self.url, **{'HTTP_' + k: v for k, v in self.headers.items()})

        # Expected response format
        expected_data = {
            'intent_subintent': {},
            'sentiment': []
        }

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], expected_data)



class BulkImportTrainingPhrasesTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('EmailApp:intents_with_training_phrases')  
        self.headers = {
            EmailDashboardParams.CUSTOMER_UUID.value: 'test-customer-uuid',
            EmailDashboardParams.USER_UUID.value: 'test-user-uuid',
            EmailDashboardParams.APPLICATION_UUID.value: 'test-application-uuid'
        }


    def __create_excel_file(self, data,sheet_name):
        # Create a DataFrame using the provided data
        df = pd.DataFrame(data)

        # Create an in-memory Excel file directly using `to_excel`
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False, sheet_name=sheet_name,
                    header=False)  # `header=False` for custom row content

        # Reset pointer to the beginning of the in-memory file
        excel_file.seek(0)

        return excel_file
    
    def __create_excel_with_content_type(self,data,sheet_name):
        # Create the in-memory Excel file with the correct content type and file extension
        excel_file = self.__create_excel_file(data=data,sheet_name=sheet_name)
        mock_file_obj = Mock()
        mock_file_obj.content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Example for .xlsx
        mock_file_obj.name = 'test_file.xlsx'
        mock_file_obj.read.return_value = excel_file.getvalue()
        return mock_file_obj


    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch(
        'EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list')
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value='dimension-type-uuid')
    def test_bulk_import_training_phrases_invalid_headers_of_excel(self, mock_get_dimension_type_uuid,
                                                                   mock_get_existing_intents,
                                                                   mock_validate_uuids):
        # Mock the return value for existing intents
        mock_get_existing_intents.return_value = [('mapping-uuid', 'intent-uuid', 'Intent1')]

        # Data with incorrect headers
        excel_data = {
            'Intent Description': [
                'Desc1',  # Incorrect header in row 1
                '',  # Empty row
                '',
                'Training'  # Incorrect placement in row 3
            ]
        }
        
        response = self.client.post(self.url, headers=self.headers, data={
            BULK_IMPORT_EXCEL_FILE: self.__create_excel_with_content_type(excel_data,'Intent1')
        })

        # Validate that the response contains the expected error message
        self.assertIn("Sheet 'Intent1' has incorrect headers.", response.json()['result'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the mock methods were called as expected
        mock_validate_uuids.assert_called_once_with({
            EmailDashboardParams.CUSTOMER_UUID.value: 'test-customer-uuid',
            EmailDashboardParams.APPLICATION_UUID.value: 'test-application-uuid',
            EmailDashboardParams.USER_UUID.value: 'test-user-uuid'
        })
        mock_get_existing_intents.assert_called_once()
        mock_get_dimension_type_uuid.assert_called_once()

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch(
        'EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list')
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value='dimension-type-uuid')
    def test_bulk_import_training_phrases_less_no_of_training_phrases(self, mock_get_dimension_type_uuid,
                                                                   mock_get_existing_intents,
                                                                   mock_validate_uuids):
        # Mock the return value for existing intents
        mock_get_existing_intents.return_value = [('mapping-uuid', 'intent-uuid', 'Intent1')]

        response = self.client.post(self.url, headers=self.headers,
                                    data={BULK_IMPORT_EXCEL_FILE: self.__create_excel_with_content_type(data={
                                        'Intent Description': [
                                            'Intent Description',  # empty row
                                            'Desc1',  # empty row
                                            '',
                                            'Training Phrases',  # sheet_data.iloc[3, 0]
                                            'Tp1'
                                        ]
                                    },sheet_name='Intent1')})


        self.assertIn(response.json()['result'], "Sheet 'Intent1' has less than 2 training phrases.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch(
        'EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list')
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value='dimension-type-uuid')
    def test_bulk_import_training_phrases_greater_than_250_chars(self, mock_get_dimension_type_uuid,
                                                                   mock_get_existing_intents,
                                                                   mock_validate_uuids):
        # Mock the return value for existing intents
        mock_get_existing_intents.return_value = [('mapping-uuid', 'intent-uuid', 'Intent1')]

        response = self.client.post(self.url, headers=self.headers,
                                    data={BULK_IMPORT_EXCEL_FILE: self.__create_excel_with_content_type(data={

                                        'Intent Description': [
                                            'Intent Description',  # empty row
                                            'Desc1',  # empty row
                                            '',
                                            'Training Phrases',  # sheet_data.iloc[3, 0]
                                            'Tp111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111',
                                            'Tp2'
                                        ]
                                    },sheet_name='Intent1')})


        self.assertIn(response.json()['result'], "Some training phrases in sheet 'Intent1' exceed 250 characters.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_bulk_import_training_phrases_exception_while_extract_training_phrases(self):


        # Mock the sheet_data to raise an exception on iloc access
        mock_sheet_data = MagicMock()
        mock_sheet_data.iloc.__getitem__.side_effect = Exception("Test Exception")

        # Create an instance of the class containing the method
        instance = PersonalizationServiceImpl()  
        
        # Run the test
        with self.assertRaises(CustomException) as context:
            instance._PersonalizationServiceImpl__extract_validate_training_phrases(mock_sheet_data, "Sheet1")
        
        # Check that the exception message is as expected
        self.assertEqual(str(context.exception), "Exception occurred while fetching Training phases")
    @patch("EmailApp.services.impl.personalization_service_impl.pd.read_excel") 
    def test_bulk_import_training_phrases_exception_read_excel(self,mock_read_excel):


        # Configure the mock to raise an exception
        mock_read_excel.side_effect = Exception("Test Excel Read Error")

        # Create an instance of the class containing the method
        instance = PersonalizationServiceImpl()  

        # Call the method with a mock Excel file object
        mock_excel_file_obj = MagicMock()
        response = instance._PersonalizationServiceImpl__read_excel(mock_excel_file_obj)

        # Assert that CustomResponse is returned with the expected error code and message
        self.assertIsInstance(response, CustomResponse)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch(
        'EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list')
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value='dimension-type-uuid')
    def test_bulk_import_training_phrases_file_not_found(self,mock_get_dimension_type_uuid,mock_get_existing_dimensions ,mock_validate_uuids):
        """
        Test failure when no file is provided.
        """
        mock_get_existing_dimensions.return_value = [('mapping-uuid', 'intent-uuid', 'Intent_new')]
        mock_get_dimension_type_uuid.return_value='dim_type_uuid'
        response = self.client.post(self.url, headers=self.headers, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot find file with key", response.json()['result'])

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    def test_bulk_import_invalid_file_type(self, mock_validate_uuids):
        mock_file_obj = Mock()
        mock_file_obj.content_type = 'application/pdf'
        mock_file_obj.name = 'test_file.pdf'
        mock_file_obj.read.return_value = b"Random PDF content"

        response = self.client.post(
            self.url,
            headers=self.headers,
            data={BULK_IMPORT_EXCEL_FILE: mock_file_obj}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Provided file is not an excel file.", response.json()['result'])

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch(
        'EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list')
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value='dimension-type-uuid')

    def test_bulk_import_no_description_for_new_intent(self,mock_get_dimension_type_uuid,mock_get_existing_dimensions ,mock_validate_uuids):
        mock_get_existing_dimensions.return_value = []
        mock_get_dimension_type_uuid.return_value='dim_type_uuid'
        excel_data = {
            'Intent Description': [
                'Intent Description',
                '',  # Empty description for new intent
                '',
                'Training Phrases',
                'Phrase1',
                'Phrase2'
            ]
        }

        response = self.client.post(
            self.url,
            headers=self.headers,
            data={BULK_IMPORT_EXCEL_FILE: self.__create_excel_with_content_type(excel_data,sheet_name='Intent1')}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Sheet 'Intent1' is newly added intent and requires a description.", response.json()['result'])
    
    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value={"Intent1": "intent-uuid"})
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list',
           return_value=[("mapping-uuid", "intent-uuid", "Intent1"),("mapping-uuid2", "intent-uuid2", "Intent2")])
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value="dimension-type-uuid")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.delete_emails_by_metadata',return_value=['id1'])
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application',return_value='temp_collection')
    @patch('Platform.services.impl.dimension_service_impl.DimensionServiceImpl.upload_intent_utterances_to_chroma_server',return_value=None)
    @patch('Platform.services.impl.dimension_service_impl.DimensionServiceImpl.delete_dimension_mapping',return_value=None)
    def test_bulk_import_training_phrases_success(self,mock_delete_dimension,mock_upload_intents,mock_get_collection, mock_delete_emails,mock_get_dimension_type_uuid,
                                                  mock_get_existing_intents, mock_validate_uuids):
        """
        Test successful import of training phrases with valid data.
        """
        
        # Mocking valid Excel data structure
        excel_data = {
            'Intent Description': [
                'Intent Description',  # Header row
                'Desc1',               # Description for intent
                '',
                'Training Phrases',     # Header for training phrases
                'tp1',
                'tp2'
            ]
        }

        excel_file = self.__create_excel_with_content_type(data=excel_data,sheet_name='Intent1')
        
        response = self.client.post(self.url, headers=self.headers, data={BULK_IMPORT_EXCEL_FILE: excel_file})

        # Assertions to confirm success
        self.assertIn("Training phrases successfully saved.", response.json()['result'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
        # Confirming that the mocks were called with expected values
        mock_get_existing_intents.assert_called_once()
        mock_get_dimension_type_uuid.assert_called_once()
        mock_delete_dimension.assert_called_once()

    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value={"Intent1": "intent-uuid"})
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list',
           return_value=[])
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value="dimension-type-uuid")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.delete_emails_by_metadata',return_value=['id1'])
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application',return_value='temp_collection')
    @patch('Platform.services.impl.dimension_service_impl.DimensionServiceImpl.add_dimension_and_mapping',return_value=None)
    @patch('Platform.services.impl.dimension_service_impl.DimensionServiceImpl.delete_dimension_mapping',return_value=None)
    def test_bulk_import_training_phrases_success2(self,mock_delete_dimension,mock_upload_intents,mock_get_collection, mock_delete_emails,mock_get_dimension_type_uuid,
                                                  mock_get_existing_intents, mock_validate_uuids):
        """
        Test successful import of training phrases with valid data.
        """
        
        # Mocking valid Excel data structure
        excel_data = {
            'Intent Description': [
                'Intent Description',  # Header row
                'Desc1',               # Description for intent
                '',
                'Training Phrases',     # Header for training phrases
                'tp1',
                'tp2'
            ]
        }

        excel_file = self.__create_excel_with_content_type(data=excel_data,sheet_name='Intent1')
        
        response = self.client.post(self.url, headers=self.headers, data={BULK_IMPORT_EXCEL_FILE: excel_file})

        # Assertions to confirm success
        self.assertIn("Training phrases successfully saved.", response.json()['result'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
        # Confirming that the mocks were called with expected values
        mock_get_existing_intents.assert_called_once()
        mock_get_dimension_type_uuid.assert_called_once()

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    @patch(
        'EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list')
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value='')
    def test_bulk_import_training_phrases_no_dimenstion_type_found(self, mock_get_dimension_type_uuid,

                                                                   mock_get_existing_intents,
                                                                   mock_validate_uuids):
        # Mock the return value for existing intents
        mock_get_existing_intents.return_value = [('mapping-uuid', 'intent-uuid', 'Intent1')]
        excel_data = {
            'Intent Description': [
                'Desc1'
            ]
        }
        
        response = self.client.post(self.url, headers=self.headers, data={
            BULK_IMPORT_EXCEL_FILE: self.__create_excel_with_content_type(excel_data,'Intent1')
        })
        self.assertIsInstance(response, CustomResponse)
        self.assertEqual(response.json()['result'], f"Dimension type not found for {DimensionTypeNames.INTENT.value}.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
 
        mock_get_existing_intents.assert_called_once()
        mock_get_dimension_type_uuid.assert_called_once()

    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value={"Intent1": "intent-uuid"})
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_mapping_dimension_uuid_dimension_name_list',
           return_value=[])
    @patch('EmailApp.dao.impl.dimension_type_dao_impl.DimensionTypeDaoImpl.get_dimension_type_uuid_by_name',
           return_value="dimension-type-uuid")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.delete_emails_by_metadata',return_value=['id1'])
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application',return_value='temp_collection')
    @patch('Platform.services.impl.dimension_service_impl.DimensionServiceImpl.add_dimension_and_mapping',return_value=None)
    @patch('Platform.services.impl.dimension_service_impl.DimensionServiceImpl.delete_dimension_mapping',return_value=None)
    def test_bulk_import_training_phrases_success2(self,mock_delete_dimension,mock_upload_intents,mock_get_collection, mock_delete_emails,mock_get_dimension_type_uuid,
                                                  mock_get_existing_intents, mock_validate_uuids):
        """
        Test successful import of training phrases with valid data.
        """
        
        # Mocking valid Excel data structure
        excel_data = {
            'Intent Description': [
                'Intent Description',  # Header row
                'Desc1',               # Description for intent
                '',
                'Training Phrases',     # Header for training phrases
                'tp1',
                'tp2'
            ]
        }

        excel_file = self.__create_excel_with_content_type(data=excel_data,sheet_name='Intent1')
        
        response = self.client.post(self.url, headers=self.headers, data={BULK_IMPORT_EXCEL_FILE: excel_file})

        # Assertions to confirm success
        self.assertIn("Training phrases successfully saved.", response.json()['result'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
        # Confirming that the mocks were called with expected values
        mock_get_existing_intents.assert_called_once()
        mock_get_dimension_type_uuid.assert_called_once()

    @patch('EmailApp.views.personalization_views.validate_uuids_dict')
    def test_bulk_import_training_phrases_invalid_sheet_name(self,mock_validate_uuids):
                                                                   
        # Data with incorrect headers
        excel_data = {
            'Intent Description': [
                'Desc1',  # Incorrect header in row 1
                '',  # Empty row
                '',
                'Training'  # Incorrect placement in row 3
            ]
        }
        
        response = self.client.post(self.url, headers=self.headers, data={
            BULK_IMPORT_EXCEL_FILE: self.__create_excel_with_content_type(excel_data,'-Intent1')
        })

        # Validate that the response contains the expected error message
        self.assertIn("Name of sheet -Intent1 is Invalid.\n Only alphanumeric characters and hyphens are allowed. The value must be 2-64 characters long and cannot start or end with a hyphen.", response.json()['result'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the mock methods were called as expected
        mock_validate_uuids.assert_called_once_with({
            EmailDashboardParams.CUSTOMER_UUID.value: 'test-customer-uuid',
            EmailDashboardParams.APPLICATION_UUID.value: 'test-application-uuid',
            EmailDashboardParams.USER_UUID.value: 'test-user-uuid'
        })











class DownloadIntentsWithTrainingPhrasesViewTestCase(APITestCase):
    
    def setUp(self):
        self.url = reverse('EmailApp:intents_with_training_phrases')  
        self.headers = {
            EmailDashboardParams.CUSTOMER_UUID.value: "valid-customer-uuid",
            EmailDashboardParams.APPLICATION_UUID.value: "valid-application-uuid",
            EmailDashboardParams.USER_UUID.value: "valid-user-uuid"
        }
    
    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value=None)
    @patch('EmailApp.dao.impl.dimension_dao_impl.DimensionDaoImpl.get_dimension_uuid_dimension_name_description', 
           return_value=[("dimension-uuid-1", "Intent1", "Sample Description")])
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application', 
           return_value='temp_collection')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_records_by_metadata', 
           return_value={"documents":['"phrase1"', '"phrase2"'],"metadata":["metadata1","metadata2"],"ids":["id1","id2"]})
    def test_download_intents_with_training_phrases_success(self, mock_get_records, mock_get_collection, mock_get_dimension_details, mock_validate_uuids):
        """
        Test successful download of intents with training phrases with all valid inputs.
        """
        response = self.client.get(self.url, **{"HTTP_" + key.upper().replace("-", "_"): value for key, value in self.headers.items()})
        # Check that the response contains the correct Excel file
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], SPREAD_SHEET_CONTENT_TYPE)
        self.assertIn("attachment; filename=valid-customer-uuid_intents_training_phrases.xlsx", response['Content-Disposition'])
        
        # Verify mocks were called
        mock_get_dimension_details.assert_called_once()
        mock_get_collection.assert_called_once()
        mock_get_records.assert_called_once()


    @patch('EmailApp.services.impl.personalization_service_impl.logger')
    def test_generic_exception_collection_not_exist(self, mock_logger):
        # Create a MagicMock for the chroma_vector_store
        mock_chroma_vector_store = MagicMock()

        # Set the return value for the collection name method
        mock_chroma_vector_store.get_chroma_collection_name_by_customer_application.return_value = 'testcollection'

        # Set the side effect for get_records_by_metadata to simulate the exception
        mock_chroma_vector_store.get_records_by_metadata.side_effect = Exception("Collection testcollection does not exist")

        # Instantiate the service and assign the mock
        instance = PersonalizationServiceImpl()
        instance.chroma_vector_store = mock_chroma_vector_store

        # Call the function under test
        result = instance._PersonalizationServiceImpl__fetch_dimension_utterances_for_customer_application(
            "test_customer", "test_application", "test_dimension", "test_user"
        )

        # Assertions
        self.assertEqual(result, [])  # Expecting an empty list in case of exception
        mock_logger.error.assert_called_once_with("Exception in fetching utterances :: Collection testcollection does not exist")

    
    def test_invalid_collection_exception(self):
        # Setup: Mock the chroma_vector_store to raise InvalidCollectionException
        mock_chroma_vector_store = MagicMock()
        mock_chroma_vector_store.get_chroma_collection_name_by_customer_application.return_value = 'testcollection'
        mock_chroma_vector_store.get_records_by_metadata.side_effect = InvalidCollectionException("Invalid collection")

        instance = PersonalizationServiceImpl()  
        instance.chroma_vector_store = mock_chroma_vector_store

        result = instance._PersonalizationServiceImpl__fetch_dimension_utterances_for_customer_application("test_customer","test_application","test_dimension","test_user")  

        self.assertEqual(result, [])  

    @patch('EmailApp.services.impl.personalization_service_impl.logger')
    def test_generic_exception_other_error(self, mock_logger):
        # Setup: Mock the chroma_vector_store to raise a generic exception with a different message
        mock_chroma_vector_store = MagicMock()
        mock_chroma_vector_store.get_chroma_collection_name_by_customer_application.return_value = 'testcollection'

        mock_chroma_vector_store.get_records_by_metadata.side_effect = Exception("Some other error")

        instance = PersonalizationServiceImpl()
        instance.chroma_vector_store = mock_chroma_vector_store

        # Use assertRaises to expect that the exception is re-raised
        with self.assertRaises(Exception) as context:
            instance._PersonalizationServiceImpl__fetch_dimension_utterances_for_customer_application("test_customer", "test_application", "test_dimension", "test_user")

        # Assertions for the exception
        self.assertEqual(str(context.exception), "Some other error")
        mock_logger.error.assert_called_once_with("Exception in fetching utterances :: Some other error")

    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value=True)
    @patch('EmailApp.services.impl.personalization_service_impl.PersonalizationServiceImpl.download_intents_with_training_phrases', return_value=None)
    def test_download_intents_with_training_phrases_none_response(self, mock_download_intents, mock_validate_uuids):
        """
        Test case for when download_intents_with_training_phrases service returns None.
        """
        response = self.client.get(self.url, **{"HTTP_" + key.upper().replace("-", "_"): value for key, value in self.headers.items()})
        # Check for 500 Internal Server Error response when service returns None
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()['result'], "Failed to generate the Excel file")
        
        # Verify that mocks were called
        mock_validate_uuids.assert_called_once()
        mock_download_intents.assert_called_once_with(
            customer_uuid="valid-customer-uuid",
            application_uuid="valid-application-uuid",
            user_uuid="valid-user-uuid",
            Dimension_type_name=DimensionTypeNames.INTENT.value
        )

    @patch('EmailApp.views.personalization_views.validate_uuids_dict', return_value=True)
    @patch('EmailApp.services.impl.personalization_service_impl.PersonalizationServiceImpl.download_intents_with_training_phrases', side_effect=Exception("Unexpected error"))
    def test_download_intents_with_training_phrases_exception(self, mock_download_intents, mock_validate_uuids):
        """
        Test case for when download_intents_with_training_phrases service raises an Exception.
        """
        response = self.client.get(self.url, **{"HTTP_" + key.upper().replace("-", "_"): value for key, value in self.headers.items()})
        
        # Check for 500 Internal Server Error response when an exception is raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()['result'], "Error while downloading intents with training phrases: Unexpected error")
        
        # Verify that mocks were called
        mock_validate_uuids.assert_called_once()
        mock_download_intents.assert_called_once_with(
            customer_uuid="valid-customer-uuid",
            application_uuid="valid-application-uuid",
            user_uuid="valid-user-uuid",
            Dimension_type_name=DimensionTypeNames.INTENT.value
        )
    @patch('openpyxl.load_workbook')
    def test_general_exception_handling(self, mock_load_workbook):
        """
        Test case to ensure the service method handles a general exception properly
        and returns None if an error occurs in any part of the process.
        """
        # Simulate an exception during load_workbook
        mock_load_workbook.side_effect = Exception("Error loading workbook")

        # Call the service method
        response = PersonalizationServiceImpl().download_intents_with_training_phrases(
            "customer_uuid", "application_uuid", "user_uuid", "dimension_type_name"
        )

        # Assert that the response is None, indicating the exception was handled
        self.assertIsNone(response)
