from urllib.parse import urlencode
import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from DatabaseApp.models import Customers, LLMConfiguration, LLMConfigurationCustomerMapping
from Platform.tests.test_data import create_assign_organization_test_data


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()
        # Create test data
        self.llm_configuration, self.customer_uuid, self.llm_provider_uuid = create_assign_organization_test_data()
        # Ensure you have the correct UUIDs for your tests
        self.user_uuid = uuid.uuid4()
        
class AssignOrganizationViewSetTestCase(BaseTestCase):

    ###
    # ========= Tests for "add_llm_configuration" API ==========
    ###

    # 1. With all correct values
    def test_add_organizations_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "organizations": [self.customer_uuid.cust_uuid],  
        }
        response = self.client.post(
            reverse("Platform:assign_organization"),
            payload,
            format="json",
            headers={
                "user_uuid":self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 2. With all correct values
    def test_add_organizations_user_uuid_null(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "organizations": [self.customer_uuid.cust_uuid],  
        }
        response = self.client.post(
            reverse("Platform:assign_organization"),
            payload,
            format="json",
            headers={
                "user_uuid":None
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # 3. With all Incorrect values
    def test_add_organizations_invalid(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "organizations": self.customer_uuid.cust_uuid,  
        }
        response = self.client.post(
            reverse("Platform:assign_organization"),
            payload,
            format="json",
            headers={
                "user_uuid":self.user_uuid
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ###
    # ========= Tests for "get_llm_configuration_by_id" API ==========
    ###

    def test_get_organizations_success(self):

        params = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid
        }

        response = self.client.get(
            reverse("Platform:assign_organization"),
            **{'QUERY_STRING': urlencode(params)}
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    ###
    # ========= Tests for "delete_organization" API ==========
    ###

    def test_delete_organization_success(self):
        mapping_uuid = uuid.uuid4()
        llm_configuration_instance = LLMConfiguration(self.llm_configuration.llm_configuration_uuid)
        # Retrieve a customer instance by UUID
        customer_instance = Customers(self.customer_uuid.cust_uuid)
        new_mapping_data = {
            'mapping_uuid': mapping_uuid,
            'llm_configuration_uuid': llm_configuration_instance,
            'customer_uuid': customer_instance,
            'created_by': self.user_uuid,
            'updated_by': self.user_uuid
        }
        LLMConfigurationCustomerMapping.objects.create(**new_mapping_data)
        params = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "customer_uuid": self.customer_uuid.cust_uuid
        }

        response = self.client.delete(
            reverse("Platform:assign_organization"),
            **{'QUERY_STRING': urlencode(params)}
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_organization_failure(self):
        params = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "customer_uuid": self.customer_uuid.cust_uuid
        }

        response = self.client.delete(
            reverse("Platform:assign_organization"),
            **{'QUERY_STRING': urlencode(params)}
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ###
    # ========= Tests for "get_organization_by_id" API ==========
    ###

    def test_get_organization_by_id_success(self):
        url = f"{reverse('Platform:assign_organization')}/{self.customer_uuid.cust_uuid}"
        params = {
            "channel": "Email"
        }

        response = self.client.get(
            url,
            **{'QUERY_STRING': urlencode(params)}
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)