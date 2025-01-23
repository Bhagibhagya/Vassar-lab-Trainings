import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from Platform.tests.test_data import create_customer

class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()
        # Create test data
        self.customer = create_customer()
        
class CustomerViewSetTestCase(BaseTestCase):

    def test_get_customers_success(self):
        response = self.client.get(
            reverse("Platform:get_customers")
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)