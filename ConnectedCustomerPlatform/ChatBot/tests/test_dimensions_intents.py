import json
import uuid
from uuid import uuid4

from rest_framework.test import APITestCase

from ChatBot.tests.test_data import create_dimensions_intents_data
from rest_framework import status
from django.urls import reverse

class DimensionsIntentViewSetTestCase(APITestCase):
    def setUp(self):
        # Create test data using the helper function from test_data.py
        self.user_uuid = "508825ca-5e1b-47ab-920c-63c7ca721562"
        self.dimension_type,self.application, self.customer =create_dimensions_intents_data()

    def test_get_all_dimensions_success(self):
        response = self.client.get(
            reverse("ChatBot:get_intent_dimensions"),format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)


    # 2. With all correct values but no matched data from db
    def test_get_all_dimensions_empty(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("ChatBot:get_intent_dimensions"),format="json"
            , headers={
                "customer_uuid": uuid.uuid4(),
                "application_uuid": self.application.application_uuid
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