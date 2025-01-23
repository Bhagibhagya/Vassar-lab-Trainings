from datetime import datetime
from urllib.parse import urlencode
from DatabaseApp.models import Email, EmailInfoDetail
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .test_data import create_test_data
from ..constant.error_messages import ErrorMessages
from ..constant.success_messages import SuccessMessages
from ..utils import get_timestamp_from_date, get_current_date_str
from unittest import TestCase as unitTestcase
from unittest.mock import patch, MagicMock
from EmailApp.services.impl.email_conversation_impl import EmailConversationServiceImpl

from django.db import connection


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        (
            self.dimension_type,
            self.dimension,
            self.customer_client,
            self.application,
            self.user,
            self.customer,
            self.email,
            self.email_conversation,
            self.email_info_detail,
            self.email_server,
            self.user_email_setting,
            self.ticket
        ) = create_test_data()

        cursor = connection.cursor()
        cursor.execute("""
                        CREATE OR REPLACE VIEW email_conversation_view AS
                        SELECT 
                            e.email_uuid,
                            e.email_conversation_uuid,
                            e.email_status,
                            e.dimension_action_json,
                            e.parent_uuid,
                            e.inserted_ts,
                            e.updated_ts,
                            eid.email_info_uuid,
                            eid.email_subject,
                            eid.email_body_url,
                            eid.html_body,
                            eid.attachments,
                            eid.sender,
                            eid.sender_name,
                            eid.recipient,
                            eid.recipients,
                            eid.cc_recipients,
                            eid.bcc_recipients,
                            eid.email_body_summary,
                            eid.email_meta_body,
                            eid.extracted_order_details,
                            eid.validated_details,
                            eid.verified,
                            e.email_flow_status,
                            ec.email_activity
                        FROM 
                            email e
                        JOIN 
                            email_info_detail eid ON e.email_uuid = eid.email_uuid
                        JOIN 
                            email_conversation ec ON e.email_conversation_uuid = ec.email_conversation_uuid
                        ORDER BY 
                            e.inserted_ts;"""
                       )
        cursor.close()
        self.customer_uuid = "af4bf2d8-fd3e-4b40-902a-1217952c0ff3"
        self.application_uuid = "e912de61-96c0-4582-89aa-64de807a4635"
        self.user_id = "user_uuid1"
        self.start_date = "01/01/2023"
        self.end_date = "01/01/2024"
        self.customer_client_uuid = self.customer_client.customer_client_uuid
        self.email_conversation_flow_status = "total_emails_received"
        self.email_uuid = self.email.email_uuid
        self.email_conversation_uuid = self.email_conversation.email_conversation_uuid
        self.invalid_uuid = "invalid_uuid"


####
# =========================== Tests for EmailConversationViewSet ===================================
####

class EmailConversationViewSetTestCase(BaseTestCase):
    
    ###
    # ========= Tests for "get_mail_conversations_by_conversation_id" API =============
    ###

    # 1. With all correct values
    def test_get_mail_conversations_by_ticket_uuid_success(self):
        params = {
            "ticket_uuid": self.ticket.ticket_uuid
        }

        response = self.client.get(
            reverse("EmailApp:get_mail_conversation_by_ticket_uuid"),
            **{'QUERY_STRING': urlencode(params)}
        )

        response_data = response.content.decode('utf-8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("email_conversation_data", response_data)

    # 2. With missing parameters
    def test_get_mail_conversations_by_mail_id_missing_required_params(self):
        params = {
            "ticket_uuid": ""
        }

        response = self.client.get(
            reverse("EmailApp:get_mail_conversation_by_ticket_uuid"),
            **{'QUERY_STRING': urlencode(params)}
        )

        # Expecting a 400 Bad Request due to missing email_uuid or other fields
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data["result"], ErrorMessages.TICKET_UUID_NOT_NULL)

    # 3. With invalid email uuid
    def test_get_mail_conversations_by_mail_id_invalid_email_conversation_uuid(self):
        params = {
           "ticket_uuid": self.invalid_uuid
        }

        response = self.client.get(
            reverse("EmailApp:get_mail_conversation_by_ticket_uuid"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(response.data["result"], ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND)

    ###
    # ========= Tests for "delete_draft_mail" API =============
    ###

    # 1. With all correct values
    def test_delete_draft_mail_success(self):
        date = get_current_date_str()
        current_timestamp = get_timestamp_from_date(date)
        Email.objects.create(
            email_uuid="email_uuid2",
            email_conversation_uuid=self.email_conversation,
            email_status="Draft",
            inserted_ts=current_timestamp,
            updated_ts=current_timestamp
        )
        params = {
            "email_uuid": "email_uuid2"
        }
        response = self.client.delete(
            reverse("EmailApp:draft_mail"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn(SuccessMessages.DRAFT_MAIL_DELETED_SUCCESS, response.data['result'])

    # With missing conversation_uuid
    def test_delete_draft_mail_missing_mail_uuid(self):
        params = {}
        response = self.client.delete(
            reverse("EmailApp:draft_mail"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['result'], ErrorMessages.EMAIL_UUID_NULL_ERROR)

    def test_delete_draft_mail_invalid_email_uuid(self):
        params = {
            "email_uuid" : self.invalid_uuid
        }
        response = self.client.delete(
            reverse("EmailApp:draft_mail"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], ErrorMessages.DRAFT_MAIL_NOT_FOUND)

    ###
    # ========= Tests for "get_email_conversations" API =============
    ###
    # ==================================================

    def test_get_email_conversations_success(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user.user_id
        }
        data = {
            "start_date": "01/01/2023",
            "end_date": "10/10/2024",
            "email_conversation_flow_status": "total_emails_received",
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("EmailApp:get_email_conversations"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data['result'])

    def test_get_email_conversations_missing_start_date(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid":self.user.user_id
        }
        data = {
            "end_date": "10/10/2024",
            "email_conversation_flow_status": "total_emails_received",
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("EmailApp:get_email_conversations"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Asserting the serializer error
        self.assertIn("start_date", response.data["result"])
        self.assertEqual(response.data["result"]["start_date"][0], "This field is required.")

    def test_get_email_conversations_missing_end_date(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user.user_id
        }
        data = {
            "start_date": "01/01/2023",
            "email_conversation_flow_status": "total_emails_received",
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("EmailApp:get_email_conversations"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Asserting the serializer error
        self.assertIn("end_date", response.data["result"])
        self.assertEqual(response.data["result"]["end_date"][0], "This field is required.")

    def test_get_email_conversations_date_error(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user.user_id
        }
        data = {
            "start_date": "01/01/2024",
            "end_date": "10/10/2023",
            "email_conversation_flow_status": "total_emails_received",
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("EmailApp:get_email_conversations"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['result'], ErrorMessages.START_DATE_GREATER_THAN_END_DATE)

    def test_get_email_conversations_invalid_page_number(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user.user_id
        }
        data = {
            "start_date": "01/01/2023",
            "end_date": "10/10/2024",
            "email_conversation_flow_status": "total_emails_received",
            "page_number": 0,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("EmailApp:get_email_conversations"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["result"], ErrorMessages.PAGE_NUMBER_POSITIVE)

    def test_get_email_conversations_invalid_total_entry_per_page(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user.user_id
        }
        data = {
            "start_date": "01/01/2023",
            "end_date": "10/10/2024",
            "email_conversation_flow_status": "total_emails_received",
            "page_number": 1,
            "total_entry_per_page": 0
        }

        response = self.client.post(
            reverse("EmailApp:get_email_conversations"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["result"], ErrorMessages.TOTAL_ENTRY_PER_PAGE_POSITIVE)


    ###
    # ========= Tests for "get_content_from_url" API =============
    ###
    # ==================================================

    def test_get_content_from_url_success_for_text_content(self):
        email_body_url="https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-17/Email_body/3a3a2170-e554-429d-bf43-69cc46abae35.txt"
        
        params = {
            "file_url" : email_body_url
        }
        response = self.client.get(
            reverse("EmailApp:get_content_from_url"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_content_from_url_success_for_json_content(self):
        email_body_url="https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-06/Attachments/c584d23f-eb68-459f-bd56-e45c0e186a71.json"
        
        params = {
            "file_url" : email_body_url
        }
        response = self.client.get(
            reverse("EmailApp:get_content_from_url"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_content_from_url_failure(self):
        params = {}
        response = self.client.get(
            reverse("EmailApp:get_content_from_url"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.data["result"], ErrorMessages.FILE_URL_NULL_ERROR)

    
    ###
    # ========= Tests for "post_order_details_info" API =============
    ###
    # ==================================================

    # @patch('ConnectedCustomerPlatform.StorageServices.azure_services.AzureBlobManager.update_json_to_azure_blob')
    # def test_post_order_details_info_success(self):
    #     # Mock the return value of update_json_to_azure_blob
    #     mock_update_json_to_azure_blob.return_value = "https://fakeurl.com/updated_blob.json"

    #     # Create the service instance
    #     service = EmailConversationServiceImpl()

    #     # Sample input data
    #     email_uuid = "email_uuid1"
    #     details_extracted_json = {
    #         "purchaseorderinformation": {
    #             "purchaseOrderNumber": "73414",
    #             "orderDate": "4/11/2024",
    #             "eta": "4/12/2024",
    #             "currency": "USD"
    #         },
    #         "buyerinformation": {
    #             "buyerName": "Axel Reyes",
    #             "buyerAddress": "Spencer Technologies, Inc, 10 Trotter Drive, Medway, MA 02053, US",
    #             "buyerContact.phone": "",
    #             "buyerContact.email": "APinvoice@spencertech.com"
    #         }
    #     }

    #     # Simulated previous file URL
    #     file_url = "https://fakeurl.com/previous_blob.json"

    #     # Call the method being tested, which includes the update_json_to_azure_blob call
    #     response_url = service.azureblobmanager.update_json_to_azure_blob(
    #         json=json.dumps(details_extracted_json),
    #         previous_url=file_url
    #     )

    #     # Assertions
    #     self.assertEqual(response_url, "https://fakeurl.com/updated_blob.json")
    #     mock_update_json_to_azure_blob.assert_called_once_with(
    #         json=json.dumps(details_extracted_json),
    #         previous_url=file_url
    #     )

    def test_post_order_details_info_missing_email_uuid(self):
        headers = {
            "user-uuid": self.user.user_id
        }
        data = {
            "email_uuid" : None,
            "details_extracted_json" : {
                "purchaseorderinformation": {
                    "purchaseOrderNumber": "73414",
                    "orderDate": "4/11/2024",
                    "eta": "4/12/2024",
                    "currency": "USD"
                },
                "buyerinformation": {
                    "buyerName": "Axel Reyes",
                    "buyerAddress": "Spencer Technologies, Inc, 10 Trotter Drive, Medway, MA 02053, US",
                    "buyerContact.phone": "",
                    "buyerContact.email": "APinvoice@spencertech.com"
                }
            }
        }
        response = self.client.post(
            reverse("EmailApp:order_details_info"),
            headers = headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.data["result"], ErrorMessages.EMAIL_UUID_NULL_ERROR)

    def test_post_order_details_info_missing_details_extracted_json(self):
        headers = {
            "user-uuid": self.user.user_id
        }
        data = {
            "email_uuid" : "email_uuid1",
            "details_extracted_json" : {}
        }
        response = self.client.post(
            reverse("EmailApp:order_details_info"),
            headers = headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.data["result"], ErrorMessages.DETAILS_EXTRACTED_NULL_ERROR)


    ###
    # ========= Tests for "get_downloadable_urls" API =============
    ###
    # ==================================================


    def test_get_downloadable_urls_success(self):
        data = {
            "files_url_list" : "email_uuid1"
        }
        response = self.client.post(
            reverse("EmailApp:get_downloadable_urls"),
            data=data,
            format='json'
        )

        self.assertEqual(response.data["result"], ErrorMessages.FILES_URL_LIST_NULL_ERROR)

    def test_get_downloadable_urls_failure(self):
        data = {
            "files_url_list" : []
        }
        response = self.client.post(
            reverse("EmailApp:get_downloadable_urls"),
            data=data,
            format='json'
        )

        self.assertEqual(response.data["result"], ErrorMessages.FILES_URL_LIST_NULL_ERROR)
    

    ###
    # ========= Tests for "create_draft_mail" API =============
    ###
    # ==================================================

    # def test_create_draft_mail_success(self):
    #     data = {
    #         "files_url_list" : "email_uuid1"
    #     }
    #     headers = {
    #         "customer-uuid": self.customer_uuid,
    #         "application-uuid": self.application_uuid,
    #         "user_uuid": self.user_id
    #     }
    #     response = self.client.post(
    #         reverse("EmailApp:draft_mail"),
    #         headers=headers,
    #         data=data,
    #         format='json'
    #     )

    #     self.assertEqual(response.data["result"], ErrorMessages.DETAILS_EXTRACTED_NULL_ERROR)


    ###
    # ========= Tests for "get_mail_conversation_count_by_conversation_id" API ============
    ###

    # 1. With all correct values
    def test_get_mail_conversation_count_by_conversation_id_success(self):
        params = {
            "ticket_uuid": self.ticket.ticket_uuid
        }

        response = self.client.get(
            reverse("EmailApp:get_mail_conversation_count_by_ticket_uuid"),
            **{'QUERY_STRING': urlencode(params)}
        )

        response_data = response.content.decode('utf-8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate that the response contains the conversation count
        self.assertIn("email_conversation_count", response_data)

    # 2. With missing parameters
    def test_get_mail_conversation_count_by_mail_id_missing_required_params(self):
        params = {
            "ticket_uuid": ""
        }

        response = self.client.get(
            reverse("EmailApp:get_mail_conversation_count_by_ticket_uuid"),
            **{'QUERY_STRING': urlencode(params)}
        )

        # Expecting a 400 Bad Request due to missing email_conversation_uuid
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data["result"], ErrorMessages.TICKET_UUID_NOT_NULL)

    # 3. With invalid email UUID
    def test_get_mail_conversation_count_by_mail_id_invalid_email_conversation_uuid(self):
        params = {
        "ticket_uuid": self.invalid_uuid
        }

        response = self.client.get(
            reverse("EmailApp:get_mail_conversation_count_by_conversation_id"),
            **{'QUERY_STRING': urlencode(params)}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(response.data["result"], ErrorMessages.EMAIL_CONVERSATION_NOT_FOUND)


class TestSendOrReplyOutlook(unitTestcase):

    def setUp(self):
        """Set up the test case."""
        self.service = EmailConversationServiceImpl()

    @patch("builtins.open", create=True)
    @patch("base64.b64encode")
    @patch("EmailApp.services.impl.email_conversation_impl.hit_and_retry_with_new_token")
    @patch(
        "EmailApp.services.impl.email_conversation_impl.EmailServerCAMDaoImpl.get_outlook_server_details")
    def test_send_email_without_attachments(self, mock_get_details, mock_hit_and_retry, mock_b64encode, mock_open):
        """Test sending email without attachments."""
        # Mock dependencies
        mock_get_details.return_value = ("mapping_id", "client_id", "tenant_id")
        mock_hit_and_retry.return_value.ok = True

        email_info = MagicMock()
        email_info.email_subject = "Test Subject"
        email_info.attachments = []

        result = self.service._EmailConversationServiceImpl__send_or_reply_outlook(
            email_info=email_info,
            message_id=None,
            sender_email="sender@example.com",
            email_to=["recipient@example.com"],
            customer_uuid="customer_uuid",
            application_uuid="application_uuid",
            subject="Test Email",
            email_body="This is a test email body."
        )

        self.assertTrue(result)
        mock_hit_and_retry.assert_called_once()

    @patch("builtins.open", create=True)
    @patch("base64.b64encode")
    @patch("EmailApp.services.impl.email_conversation_impl.hit_and_retry_with_new_token")
    @patch(
        "EmailApp.services.impl.email_conversation_impl.EmailServerCAMDaoImpl.get_outlook_server_details")
    def test_reply_to_email(self, mock_get_details, mock_hit_and_retry, mock_b64encode, mock_open):
        """Test replying to an email."""
        # Mock dependencies
        mock_get_details.return_value = ("mapping_id", "client_id", "tenant_id")
        mock_hit_and_retry.return_value.ok = True

        email_info = MagicMock()
        email_info.email_subject = "Re: Original Email"
        email_info.attachments = []

        result = self.service._EmailConversationServiceImpl__send_or_reply_outlook(
            email_info=email_info,
            message_id="message_id",
            sender_email="sender@example.com",
            email_to=["recipient@example.com"],
            customer_uuid="customer_uuid",
            application_uuid="application_uuid",
            subject=None,
            email_body="This is a reply.",
            in_reply_to="message_id"
        )

        self.assertTrue(result)
        mock_hit_and_retry.assert_called_once()

    @patch("builtins.open", create=True)
    @patch("base64.b64encode")
    @patch("EmailApp.services.impl.email_conversation_impl.hit_and_retry_with_new_token")
    @patch(
        "EmailApp.services.impl.email_conversation_impl.EmailServerCAMDaoImpl.get_outlook_server_details")
    def test_email_with_attachments(self, mock_get_details, mock_hit_and_retry, mock_b64encode, mock_open):
        """Test sending email with attachments."""
        # Mock dependencies
        mock_get_details.return_value = ("mapping_id", "client_id", "tenant_id")
        mock_hit_and_retry.return_value.ok = True
        mock_b64encode.return_value.decode.return_value = "encoded_string"

        email_info = MagicMock()
        email_info.email_subject = "Test Subject"
        email_info.attachments = []
        mock_open.return_value.__enter__.return_value.read.return_value = b"file_content"

        result = self.service._EmailConversationServiceImpl__send_or_reply_outlook(
            email_info=email_info,
            message_id=None,
            sender_email="sender@example.com",
            email_to=["recipient@example.com"],
            customer_uuid="customer_uuid",
            application_uuid="application_uuid",
            subject="Test Email",
            email_body="This is a test email body.",
            attachments=["/path/to/file1.txt"]
        )

        self.assertTrue(result)
        mock_hit_and_retry.assert_called_once()

    @patch("EmailApp.services.impl.email_conversation_impl.hit_and_retry_with_new_token")
    @patch(
        "EmailApp.services.impl.email_conversation_impl.EmailServerCAMDaoImpl.get_outlook_server_details")
    def test_api_error_handling(self, mock_get_details, mock_hit_and_retry):
        """Test API error handling."""
        mock_get_details.return_value = ("mapping_id", "client_id", "tenant_id")
        mock_hit_and_retry.return_value.ok = False

        email_info = MagicMock()
        email_info.email_subject = "Test Subject"
        email_info.attachments = []

        result = self.service._EmailConversationServiceImpl__send_or_reply_outlook(
            email_info=email_info,
            message_id=None,
            sender_email="sender@example.com",
            email_to=["recipient@example.com"],
            customer_uuid="customer_uuid",
            application_uuid="application_uuid",
            subject="Test Email",
            email_body="This is a test email body."
        )

        self.assertFalse(result)
        mock_hit_and_retry.assert_called_once()
from rest_framework import status
import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
import json
from django.conf import settings


class TestProcessPDFByUrl(TestCase):
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

    @patch('EmailApp.services.impl.email_conversation_impl.EmailConversationServiceImpl.process_attachment_by_blob_url')
    def test_process_attachment_by_blob_url_success(self, mock_process_attachment_by_blob_url):
        # Mocking the service layer
        mock_process_attachment_by_blob_url.return_value = None

        # Request payload and headers
        payload = {
            "blob_url": ["https://example.com/sample.pdf"]
        }
        headers = {
            "application-uuid": "83b72bf6-ddda-4eb1-90de-590700597ab2",
            "customer-uuid": "e78349f1-3efe-4b52-b9f3-ddaf3e781a60",
        }

        # API call
        response = self.client.post(
            reverse("EmailApp:process_attachment_by_blob_url"),
            data=json.dumps(payload),
            content_type='application/json',
            headers = headers
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_process_attachment_by_blob_url.assert_called_once_with(
            "e78349f1-3efe-4b52-b9f3-ddaf3e781a60", "83b72bf6-ddda-4eb1-90de-590700597ab2", ["https://example.com/sample.pdf"]
        )
    
    def test_process_attachment_by_blob_url_failure(self):

        # Request payload and headers
        payload = {
            "blob_url": None
        }
        headers = {
            "application-uuid": "83b72bf6-ddda-4eb1-90de-590700597ab2",
            "customer-uuid": "e78349f1-3efe-4b52-b9f3-ddaf3e781a60",
        }

        # API call
        response = self.client.post(
            reverse("EmailApp:process_attachment_by_blob_url"),
            data=json.dumps(payload),
            content_type='application/json',
            headers = headers
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test with all correct values, including service code coverage
    @patch('EmailApp.services.impl.email_conversation_impl.QueuingServiceFactory.instantiate')
    def test_process_attachment_by_blob_url_service_success(self, mock_instantiate):
        # Mocking the Azure EventHub service and its methods
        mock_azure_eventhub_service = MagicMock()
        mock_event_hub_producer = MagicMock()
        
        # Mock the return values
        mock_instantiate.return_value = mock_azure_eventhub_service
        mock_azure_eventhub_service.create_producer.return_value = mock_event_hub_producer
        
        # Mock the send_event_data_batch method
        mock_event_hub_producer.send_event_data_batch.return_value = None

        # Request payload and headers
        payload = {
            "blob_url": ["https://example.com/sample.pdf"]
        }
        headers = {
            "application-uuid": "83b72bf6-ddda-4eb1-90de-590700597ab2",
            "customer-uuid": "e78349f1-3efe-4b52-b9f3-ddaf3e781a60",
        }

        # API call
        response = self.client.post(
            reverse("EmailApp:process_attachment_by_blob_url"),
            data=json.dumps(payload),
            content_type='application/json',
            headers=headers
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify service-level method calls
        mock_instantiate.assert_called_once_with(
            "AzureEventHubService",
            {
                "producer_eventhub_name": settings.EMAIL_PDF_PROCESSING_EVENTHUB_TOPIC,
                "consumer_eventhub_name": None,
                "connection_string": settings.EVENT_HUB_CONNECTION_STRING,
                "blob_container_name": settings.BLOB_CONTAINER_NAME,
                "storage_connection_string": settings.EVENT_HUB_STORAGE_CONNECTION_STRING,
            }
        )
        mock_azure_eventhub_service.create_producer.assert_called_once()
        mock_event_hub_producer.send_event_data_batch.assert_called_once_with({
            "customer_uuid": "e78349f1-3efe-4b52-b9f3-ddaf3e781a60",
            "application_uuid": "83b72bf6-ddda-4eb1-90de-590700597ab2",
            "blob_url": ["https://example.com/sample.pdf"]
        })

    @patch('EmailApp.services.impl.email_conversation_impl.QueuingServiceFactory.instantiate')
    def test_process_attachment_by_blob_url_service_exception(self, mock_instantiate):
        # Mocking the Azure EventHub service and its methods
        mock_azure_eventhub_service = MagicMock()
        mock_event_hub_producer = MagicMock()
        
        # Mock the return values
        mock_instantiate.return_value = mock_azure_eventhub_service
        mock_azure_eventhub_service.create_producer.return_value = mock_event_hub_producer
        
        # Simulate an exception during send_event_data_batch
        mock_event_hub_producer.send_event_data_batch.side_effect = Exception("EventHub error")

        # Request payload and headers
        payload = {
            "blob_url": ["https://example.com/sample.pdf"]
        }
        headers = {
            "application-uuid": "83b72bf6-ddda-4eb1-90de-590700597ab2",
            "customer-uuid": "e78349f1-3efe-4b52-b9f3-ddaf3e781a60",
        }

        # API call and exception handling
        with self.assertLogs('EmailApp.services.impl.email_conversation_impl', level='ERROR') as log:
            response = self.client.post(
                reverse("EmailApp:process_attachment_by_blob_url"),
                data=json.dumps(payload),
                content_type='application/json',
                headers=headers
            )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error while producing data into EventHub", log.output[0])
        self.assertIn("EventHub error", log.output[0])

        # Verify service-level method calls
        mock_instantiate.assert_called_once_with(
            "AzureEventHubService",
            {
                "producer_eventhub_name": settings.EMAIL_PDF_PROCESSING_EVENTHUB_TOPIC,
                "consumer_eventhub_name": None,
                "connection_string": settings.EVENT_HUB_CONNECTION_STRING,
                "blob_container_name": settings.BLOB_CONTAINER_NAME,
                "storage_connection_string": settings.EVENT_HUB_STORAGE_CONNECTION_STRING,
            }
        )
        mock_azure_eventhub_service.create_producer.assert_called_once()
        mock_event_hub_producer.send_event_data_batch.assert_called_once_with({
            "customer_uuid": "e78349f1-3efe-4b52-b9f3-ddaf3e781a60",
            "application_uuid": "83b72bf6-ddda-4eb1-90de-590700597ab2",
            "blob_url": ["https://example.com/sample.pdf"]
        })
