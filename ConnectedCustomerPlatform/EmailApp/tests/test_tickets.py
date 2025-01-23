from datetime import datetime
from urllib.parse import urlencode
from DatabaseApp.models import Email, EmailInfoDetail
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch

from .test_data import create_test_data
from ..constant.error_messages import ErrorMessages


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
# =========================== Tests for TicketViewSet ===================================
####

class TicketViewSetTestCase(BaseTestCase):

    ###
    # ========= Tests for "get_email_tickets" API =============
    ###
    # ==================================================

    @patch(
        'EmailApp.dao.impl.ticket_dao_impl.is_user_admin')
    def test_get_email_tickets_success(self,mock_is_user_admin):
        mock_is_user_admin.return_value=False
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
            reverse("EmailApp:get_email_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data['result'])

    def test_get_email_tickets_missing_start_date(self):
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
            reverse("EmailApp:get_email_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Asserting the serializer error
        self.assertIn("start_date", response.data["result"])
        self.assertEqual(response.data["result"]["start_date"][0], "This field is required.")

    def test_get_email_tickets_missing_end_date(self):
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
            reverse("EmailApp:get_email_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Asserting the serializer error
        self.assertIn("end_date", response.data["result"])
        self.assertEqual(response.data["result"]["end_date"][0], "This field is required.")

    def test_get_email_tickets_date_error(self):
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
            reverse("EmailApp:get_email_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['result'], ErrorMessages.START_DATE_GREATER_THAN_END_DATE)

    @patch(
        'EmailApp.dao.impl.ticket_dao_impl.is_user_admin')
    def test_get_email_tickets_invalid_page_number(self,mock_is_user_admin):
        mock_is_user_admin.return_value=False
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
            reverse("EmailApp:get_email_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["result"], ErrorMessages.PAGE_NUMBER_POSITIVE)

    @patch(
        'EmailApp.dao.impl.ticket_dao_impl.is_user_admin')
    def test_get_email_tickets_invalid_total_entry_per_page(self,mock_is_user_admin):
        mock_is_user_admin.return_value=False
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
            reverse("EmailApp:get_email_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["result"], ErrorMessages.TOTAL_ENTRY_PER_PAGE_POSITIVE)