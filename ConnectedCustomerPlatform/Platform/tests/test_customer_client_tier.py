import json
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import uuid

from Platform.tests.test_data import create_customer_client_tier_mapping_data


class CustomerClientAPITest(APITestCase):

    def setUp(self):
        # Create test data using the helper function from test_data.py
        self.user_uuid = uuid.uuid4()
        self.customer,self.application,self.test_customer_client_tier,self.dimension_mapping,self.test_customer_client1= create_customer_client_tier_mapping_data()


    ###
    # ========= Tests for "add_customer_tier_application_mapping" API ==========
    ###

    # 1. With all correct values
    def test_add_customer_tier_mapping_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_uuid":self.test_customer_client1.customer_client_uuid,
            "tier_mapping_uuid":self.dimension_mapping.mapping_uuid,
            "extractor_template_details_json":{}
        }
        response = self.client.post(
            reverse("Platform:customer_client_tier_mapping"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
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
                "result": "Customer added to tier successfully"
            })

    # 1. With all correct values
    def test_add_customer_tier_mapping_exist_customer_client(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client_uuid":self.test_customer_client_tier.customer_client_uuid.customer_client_uuid,
            "tier_mapping_uuid":self.dimension_mapping.mapping_uuid,
            "extractor_template_details_json":{}
        }
        response = self.client.post(
            reverse("Platform:customer_client_tier_mapping"), payload , format = 'json'
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
                "result": "Customer client tier mapping already exists"
            })

    # 3. With invalid payload
    def test_add_customer_tier_mapping_invalid_payload(self):
        # Simulate a POST request with valid parameters
        payload = {
            "customer_client":self.test_customer_client_tier.customer_client_uuid.customer_client_uuid,
            "tier_mapping_uuid":self.dimension_mapping.mapping_uuid,
            "extractor_template_details_json":{}
        }
        response = self.client.post(
            reverse("Platform:customer_client_tier_mapping"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
                "user_uuid": self.user_uuid
            }
        )


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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

    ###
    # ========= Tests for "edit_customer_tier_application_mapping" API ==========
    ###


    # 1. With all correct values
    def test_edit_customer_tier_mapping_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "mapping_uuid":self.test_customer_client_tier.mapping_uuid,
            "customer_client_uuid":self.test_customer_client_tier.customer_client_uuid.customer_client_uuid,
            "tier_mapping_uuid":self.dimension_mapping.mapping_uuid,
            "extractor_template_details_json":{}
        }
        response = self.client.put(
            reverse("Platform:customer_client_tier_mapping"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
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
                "result": "Customer updated to tier successfully"
            })

    # 2. With all correct values
    def test_edit_customer_tier_mapping_invalid_payload(self):
        # Simulate a POST request with valid parameters
        payload = {
            "mapping_uuid":self.test_customer_client_tier.mapping_uuid,
            "customer_client":self.test_customer_client_tier.customer_client_uuid.customer_client_uuid,
            "tier_mapping_uuid":self.dimension_mapping.mapping_uuid,
            "extractor_template_details_json": {}
        }
        response = self.client.put(
            reverse("Platform:customer_client_tier_mapping"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
                "user_uuid": self.user_uuid
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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


    ###
    # ========= Tests for "delete_customer_tier_application_mapping" API ==========
    ###

    # 1. With all correct values
    def test_delete_customer_tier_mapping_success(self):
        # Simulate a POST request with valid parameters

        response = self.client.delete(
            reverse("Platform:delete_customer_tier_mapping", args=[self.test_customer_client_tier.mapping_uuid]), format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
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
                "result": "Customer deleted from tier successfully"
            })

    ###
    # ========= Tests for "customer_dropdown_in_tier" API ==========
    ###

    # 1. With all correct values
    def test_customer_dropdown_in_tier_success(self):
        # Simulate a POST request with valid parameters

        url = f"{reverse('Platform:customer_client_dropdown_in_tier')}"
        response = self.client.get(
            url, format="json"
            , headers={
                "customer_uuid":self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    def test_get_get_customers_client_by_mapping_tier(self):

        response = self.client.get(
            reverse("Platform:customer_tier_mapping", args=[self.test_customer_client_tier.tier_mapping_uuid]), format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
                "user_uuid": self.user_uuid
            }
        )
        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    # 2. With all correct values but no matched data from db
    def test_get_get_customers_client_by_mapping_tier_empty(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:customer_tier_mapping", args=[self.test_customer_client_tier.mapping_uuid]), format="json"
            , headers={
                "customer_uuid":uuid.uuid4(),
                "application_uuid": self.application.application_uuid,
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