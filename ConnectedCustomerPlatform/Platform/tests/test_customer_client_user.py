import json
import uuid
from types import NoneType

from django.test import TestCase
from urllib.parse import urlencode

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from Platform.tests.test_data import create_customer_client_user_data, create_customer_application_instances
import uuid

class BaseTestCase(TestCase):

    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        self.geography, self.customer_client, self.customer_client_user1, self.customer_client_user2 = create_customer_client_user_data()

        self.valid_payload = {
            "first_name": "ayush",
            "last_name": "verma",
            "email_id": "ayushv@gmail.com",
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }

        self.invalid_payload = {
            "first": "ayush", # key should be first_name
            "last_name": "verma",
            "email_id": "ayushv@gmail.com",
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }

        self.application, self.customer=create_customer_application_instances()
        self.user_uuid = uuid.uuid4()

####
# =========================== Tests for CustomerUsersViewSet ===================================
####
class CustomerUsersViewSetTestCase(BaseTestCase):

    ###
    # ========= Tests for "add_customer_client_user" API ==========
    ###

    def test_add_customer_client_user_success(self):
        """
        Test case to add a customer client user successfully with valid data.
        """

        response = self.client.post(
            reverse("Platform:customer_user"), self.valid_payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 200,
                "status": True,
                "result": "Customer User created successfully"
            })

    # 2. With invalid payload
    def test_add_customer_client_user_invalid_payload(self):
        # Simulate a POST request with invalid payload

        response = self.client.post(
            reverse("Platform:customer_user"), self.invalid_payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Expecting a 400 Bad Request due to invalid payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": {
                    "first_name": [
                        "This field is required."
                    ]
                }
            })

    # 3. give the payload for existing name
    def test_add_customer_client_user_with_existing_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "first_name": self.customer_client_user1.first_name,
            "last_name": self.customer_client_user1.last_name,
            "email_id": "ayushv@gmail.com",
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }
        response = self.client.post(
            reverse("Platform:customer_user"), payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # 4. give the payload for existing email
    def test_add_customer_client_user_with_existing_email(self):
        # Simulate a POST request with valid parameters
        payload = {
            "first_name": "test",
            "last_name": "name",
            "email_id": self.customer_client_user1.email_id,
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }
        response = self.client.post(
            reverse("Platform:customer_user"), payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    ###
    # ========= Tests for "edit_customer_client" API ==========
    ###

    # 1. With all correct values
    def test_edit_customer_user_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "client_user_uuid":self.customer_client_user1.client_user_uuid,
            "first_name": self.customer_client_user1.first_name,
            "last_name": self.customer_client_user1.last_name,
            "email_id": "ayushv@gmail.com",
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }
        response = self.client.put(
            reverse("Platform:customer_user"), payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 200,
                "status": True,
                "result": "Customer User updated successfully"
            })
    # 2. With invalid payload
    def test_edit_customer_invalid_payload(self):
        # Simulate a POST request with invalid payload
        payload = {
            "client_user_uuid": self.customer_client_user1.client_user_uuid,
            "first": self.customer_client_user2.first_name,
            "last_name": self.customer_client_user2.last_name,
            "email_id": "ayushv@gmail.com",
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }
        response = self.client.put(
            reverse("Platform:customer_user"),payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Expecting a 400 Bad Request due to invalid payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": {
                    "first_name": [
                        "This field is required."
                    ]
                }
            })

    # 3. give the payload for existing name
    def test_edit_customer_with_existing_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "client_user_uuid": self.customer_client_user1.client_user_uuid,
            "first_name": self.customer_client_user2.first_name,
            "last_name": self.customer_client_user2.last_name,
            "email_id": "ayushv@gmail.com",
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }
        response = self.client.put(
            reverse("Platform:customer_user"), payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # 4. Editing the invalid user
    def test_edit_customer_with_invalid_id(self):
        # Simulate a POST request with valid parameters
        payload = {
            "client_user_uuid": uuid.uuid4(),
            "first_name": self.customer_client_user2.first_name,
            "last_name": self.customer_client_user2.last_name,
            "email_id": "ayushv@gmail.com",
            "geography_uuid": self.geography.dimension_uuid,
            "customer_client_uuid": self.customer_client.customer_client_uuid,
            "user_info_json": {
                "address": "sdbcuwygfw",
                "domain": "ayush@gmail.com"
            }
        }
        response = self.client.put(
            reverse("Platform:customer_user"), payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "Customer user not found"
            })

    ###
    # ========= Tests for "delete_customer_client_user" API ==========
    ###

    # 1. With all correct values
    def test_delete_customer_user_success(self):
        # Simulate a POST request with valid parameters

        url = f"{reverse('Platform:customer_user')}/{self.customer_client_user1.client_user_uuid}"
        response = self.client.delete(
            url, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 200,
                "status": True,
                "result": "Customer User deleted successfully"
            })

    def test_delete_customer_user_with_invalid_id(self):
        url = f"{reverse('Platform:customer_user')}/{uuid.uuid4()}"
        response = self.client.delete(
            url, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "Customer user not found"
            })

    ###
    # ========= Tests for "get_customers" API ==========
    ###

    # 1. With all correct values
    def test_get_customers_success(self):
        # Simulate a GET request with valid parameters

        url = f"{reverse('Platform:customer_user')}/client/{self.customer_client.customer_client_uuid}"
        response = self.client.get(
            url
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)