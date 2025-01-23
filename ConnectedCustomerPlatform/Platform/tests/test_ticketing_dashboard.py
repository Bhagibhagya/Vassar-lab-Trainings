from unittest.mock import patch
from urllib.parse import urlencode

from django.db import connection
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from Platform.constant.constants import FALSE
from Platform.tests.test_data import activity_dashboard_data, merged_ticket_data


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        (
            self.dimension_type,
            self.dimension,
            self.customer, 
            self.customer_client, 
            self.application, 
            self.user,
            self.email_conversation, 
            self.email, 
            self.email_info_detail,
            self.ticket
        ) = activity_dashboard_data()
        self.email_ticket1,self.email_ticket2,self.email_ticket3,self.chat_ticket1,self.chat_ticket2,self.chat_ticket3\
        ,self.merge_application,self.merge_customer,self.merge_user,self.merged_ticket1,self.merged_ticket2,self.ticket_with_no_conversations=merged_ticket_data()
        self.customer_uuid = self.customer.cust_uuid
        self.application_uuid = self.application.application_uuid
        self.user_uuid=self.user.user_id

class TicketViewSetTestCase(BaseTestCase):

    ###
    # ========= Tests for "get_tickets" API =============
    ###
    @patch('Platform.dao.impl.ticket_dao_impl.is_user_admin', return_value=False)
    def test_get_tickets_success(self,mock_is_user_admin):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid":self.user_uuid
        }
        data = {
            "start_date": "01/01/2023",
            "end_date": "10/21/2024",
            "channels": ["email"],
            "client_names": ["Test Sender"],
            "email_ids": ["testsender@example.com"],
            "intents": ["dimension_name1"],
            "status": ["need_assistance"],
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("Platform:get_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data['result'])

    @patch('Platform.dao.impl.ticket_dao_impl.is_user_admin',return_value=True)
    def test_get_tickets_success2(self,mock_is_user_admin):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid":self.user_uuid
        }
        data = {
            "start_date": "01/01/2023",
            "end_date": "10/21/2024",
            "channels": ["email"],
            "client_names": ["Test Sender"],
            "email_ids": ["testsender@example.com"],
            "intents": ["dimension_name1"],
            "status": ["need_assistance"],
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("Platform:get_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data['result'])

    def test_get_tickets_failure(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid
        }
        data = {
            "end_date": "10/10/2024",
            "channels": ["email"],
            "client_names": ["Test Sender"],
            "email_ids": ["testsender@example.com"],
            "intents": ["dimension_name1"],
            "status": ["need_assistance"],
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.post(
            reverse("Platform:get_tickets"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ###
    # ========= Tests for "get_filters" API =============
    ###
    @patch('Platform.dao.impl.ticket_dao_impl.is_user_admin', return_value=False)
    def test_get_filters_success(self,mock_is_user_admin):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid":self.user_uuid
        }
        data = {
            "start_date": "01/01/2023",
            "end_date": "10/21/2024",
            "channels": ["email"],
            "client_names": ["Test Sender"],
            "email_ids": ["testsender@example.com"],
            "intents": ["dimension_name1"],
            "status": ["need_assistance"],
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.get(
            reverse("Platform:get_filters"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('Platform.dao.impl.ticket_dao_impl.is_user_admin', return_value=True)
    def test_get_filters_success2(self, mock_is_user_admin):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user_uuid
        }
        data = {
            "start_date": "01/01/2023",
            "end_date": "10/21/2024",
            "channels": ["email"],
            "client_names": ["Test Sender"],
            "email_ids": ["testsender@example.com"],
            "intents": ["dimension_name1"],
            "status": ["need_assistance"],
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.get(
            reverse("Platform:get_filters"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_filters_failure(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid":self.user_uuid
        }
        data = {
            "end_date": "10/10/2024",
            "channels": ["email"],
            "client_names": ["Test Sender"],
            "email_ids": ["testsender@example.com"],
            "intents": ["dimension_name1"],
            "status": ["need_assistance"],
            "page_number": 1,
            "total_entry_per_page": 10
        }

        response = self.client.get(
            reverse("Platform:get_filters"),
            headers=headers,
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mark_email_as_read(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user_uuid
        }
        query_params = {"ticket_uuid": self.ticket.ticket_uuid,"is_read":"True"}
        url = f"{reverse('Platform:mark_email_as_read')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_email_as_read_with_is_read_none(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user_uuid
        }
        query_params = {"ticket_uuid": self.ticket.ticket_uuid}
        url = f"{reverse('Platform:mark_email_as_read')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_email_as_read_with_ticket_uuid_none(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user_uuid
        }
        query_params = {"is_read":"true"}
        url = f"{reverse('Platform:mark_email_as_read')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_email_as_read_with_invalid_ticket_uuid(self):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user_uuid
        }
        query_params = {"ticket_uuid":"uaywgi738w27q3yw","is_read":"true"}
        url = f"{reverse('Platform:mark_email_as_read')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    @patch('Platform.dao.impl.ticket_dao_impl.is_user_admin', return_value=True)
    def test_get_ticket_dropdown_success_admin(self,mock_is_user_admin):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user_uuid
        }
        response = self.client.get(
            reverse("Platform:get_ticket_dropdown"),
            headers=headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('Platform.dao.impl.ticket_dao_impl.is_user_admin', return_value=False)
    def test_get_ticket_dropdown_success_csr(self, mock_is_user_admin):
        headers = {
            "customer-uuid": self.customer_uuid,
            "application-uuid": self.application_uuid,
            "user-uuid": self.user_uuid
        }
        response = self.client.get(
            reverse("Platform:get_ticket_dropdown"),
            headers=headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)



    def test_merge_ticket_success_email_chat(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {"primary_ticket_uuid":self.email_ticket1.ticket_uuid,"secondary_ticket_uuid":self.chat_ticket1.ticket_uuid}
        url = f"{reverse('Platform:merge_tickets')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_merge_ticket_success_chat_email(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {"primary_ticket_uuid":self.chat_ticket2.ticket_uuid,"secondary_ticket_uuid":self.email_ticket2.ticket_uuid}
        url = f"{reverse('Platform:merge_tickets')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_merge_ticket_success_merging_merged_tickets(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {"primary_ticket_uuid":self.merged_ticket1.ticket_uuid,"secondary_ticket_uuid":self.merged_ticket2.ticket_uuid}
        url = f"{reverse('Platform:merge_tickets')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_merge_ticket_with_invalid_ticket_uuids(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {"primary_ticket_uuid":"jahsgwu1ywi2178i21","secondary_ticket_uuid":self.merged_ticket2.ticket_uuid}
        url = f"{reverse('Platform:merge_tickets')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_merge_ticket_with_no_conversations(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {"primary_ticket_uuid":self.ticket_with_no_conversations.ticket_uuid,"secondary_ticket_uuid":self.ticket_with_no_conversations.ticket_uuid}
        url = f"{reverse('Platform:merge_tickets')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_merge_ticket_without_primary_ticket_uuid(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {}
        url = f"{reverse('Platform:merge_tickets')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_merge_ticket_without_secondary_ticket_uuid(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {"primary_ticket_uuid":self.ticket_with_no_conversations.ticket_uuid}
        url = f"{reverse('Platform:merge_tickets')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_merged_conversation_success(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {"ticket_uuid":self.merged_ticket1.ticket_uuid}
        url = f"{reverse('Platform:get_merged_conversation')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_merged_conversation_with_ticket_uuid_null(self):
        headers = {
            "customer-uuid": self.merge_customer.cust_uuid,
            "application-uuid": self.merge_application.application_uuid,
            "user-uuid": self.merge_user.user_id
        }
        query_params = {}
        url = f"{reverse('Platform:get_merged_conversation')}?{urlencode(query_params)}"
        response = self.client.get(
            url,
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


