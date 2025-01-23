import json
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from Platform.tests.test_data import create_customer_client_data
import uuid

from Platform.constant.error_messages import ErrorMessages


class CustomerClientAPITest(APITestCase):

    def setUp(self):
        # Create test data using the helper function from test_data.py
        self.user_uuid = "508825ca-5e1b-47ab-920c-63c7ca721562"
        self.customer, self.application,self.dimension , self.customer_client , self.test_customer_client= create_customer_client_data()

        # Define a valid payload for testing
        self.valid_payload = {
            "customer_client_name": "Valid Client",
            "customer_client_domain_name": "validclient.com",
            "customer_client_emails": ["client@validclient.com"],
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }

        # Define an invalid payload for testing
        self.invalid_payload = {
            "customer_client_domain_name": "validclient.com",
            "customer_client_emails": ["client@validclient.com"],
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
    ###
    # ========= Tests for "add_customer_client" API ==========
    ###

    def test_add_customer_client_success(self):
        """
        Test case to add a customer client successfully with valid data.
        """

        response = self.client.post(
            reverse("Platform:customer_client"),self.valid_payload,format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
                "user_uuid":self.user_uuid
            }
        )

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 200,
                "status": True,
                "result": "Customer created successfully"
            })

    # 2. With invalid payload
    def test_add_customer_invalid_payload(self):
        # Simulate a POST request with invalid payload

        response = self.client.post(
            reverse("Platform:customer_client"), self.invalid_payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                    "customer_client_name": [
                        "This field is required."
                    ]
                }
            })

    # 3. give the payload for existing name
    def test_add_customer_with_existing_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_name": self.customer_client.customer_client_name,
            "customer_client_domain_name": "validclient.com",
            "customer_client_emails": ["client@validclient.com"],
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.post(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer name already exists"
            })

    # 4. give the payload for existing name
    def test_add_customer_with_existing_email(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_name": "testing",
            "customer_client_domain_name": "vassarlabs1.com",
            "customer_client_emails": list(self.customer_client.customer_client_emails),
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.post(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer email already exists"
            })

    # 5. With existing domain name
    def test_add_customer_with_existing_domain_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_name": "testing",
            "customer_client_domain_name": "vassarlabs1.com",
            "customer_client_emails": ["new_email@vassarlabs1.com"],
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.post(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
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
                "result": ErrorMessages.CUSTOMER_DOMAIN_NAME_EXISTS
            })

    ###
    # ========= Tests for "edit_customer_client" API ==========
    ###

    # 1. With all correct values
    def test_edit_customer_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_uuid":str(self.customer_client.customer_client_uuid),
            "customer_client_domain_name": "validclient.com",
            "customer_client_name": "customer1",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid),
            "customer_client_emails": ["client@validclient.com"],
            "customer_client_address": "456 New York",
        }
        response = self.client.put(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer updated successfully"
            })
    # 2. With invalid payload
    def test_edit_customer_invalid_payload(self):
        # Simulate a POST request with invalid payload
        invalid_payload = {
            "customer_client_name": "Valid Client",
            "customer_client_domain_name": "validclient.com",
            "customer_client_emails": ["client@validclient.com"],
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.put(
            reverse("Platform:customer_client"),invalid_payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
                "user_uuid": self.user_uuid
            }
        )

        # Expecting a 400 Bad Request due to invalid payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("response:::",response.data)
        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": {
                    "customer_client_uuid": [
                        "This field is required."
                    ]
                }
            })

    # 3. give the payload for existing name
    def test_edit_customer_with_existing_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_uuid":self.test_customer_client.customer_client_uuid,
            "customer_client_name": self.customer_client.customer_client_name,
            "customer_client_domain_name": "validclient.com",
            "customer_client_emails": ["client@validclient.com"],
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.put(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer name already exists"
            })

    # 4. give the payload for existing name
    def test_edit_customer_with_existing_email(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_uuid":self.test_customer_client.customer_client_uuid,
            "customer_client_name": "testing",
            "customer_client_domain_name": "vassarlabs1.com",
            "customer_client_emails": self.customer_client.customer_client_emails,
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.put(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer email already exists"
            })

    # 5. With existing domain name
    def test_edit_customer_with_existing_domain_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_uuid": self.test_customer_client.customer_client_uuid,
            "customer_client_name": "unique_name",
            "customer_client_domain_name": "vassarlabs1.com",
            "customer_client_emails": ["new_email@vassarlabs1.com"],
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.put(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
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
                "result": ErrorMessages.CUSTOMER_DOMAIN_NAME_EXISTS
            })
    # 6. With existing customer uuid
    def test_edit_customer_with_non_existing_customer_uuid(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_uuid":uuid.uuid4(),
            "customer_client_name": "testing",
            "customer_client_domain_name": "vassarlabs1.com",
            "customer_client_emails": self.customer_client.customer_client_emails,
            "customer_client_address": "456 New York",
            "customer_client_geography_uuid": str(self.dimension.dimension_uuid)
        }
        response = self.client.put(
            reverse("Platform:customer_client"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer not found"
            })

    ###
    # ========= Tests for "delete_customer_client" API ==========
    ###

    # 1. With all correct values
    def test_delete_customer_success(self):
        # Simulate a POST request with valid parameters

        url = f"{reverse('Platform:customer_client')}/{self.customer_client.customer_client_uuid}"
        response = self.client.delete(
            url, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer deleted successfully"
            })

    def test_delete_customer_not_provided_customer_client_uuid(self):
        url = f"{reverse('Platform:customer_client')}/{uuid.uuid4()}"
        response = self.client.delete(
            url, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
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
                "result": "Customer not found"
            })

    ###
    # ========= Tests for "get_customers" API ==========
    ###

    # 1. With all correct values
    def test_get_customers_success(self):
        # Simulate a GET request with valid parameters

        response = self.client.get(
            reverse("Platform:customer_client"), headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid":self.application.application_uuid,
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)


    # 2. With all correct values but no matched data from db
    def test_get_customers_empty(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:customer_client"), headers={
                "customer_uuid": str(uuid.uuid4()),
                "application_uuid":self.application.application_uuid,
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
                "result": []
            })