
import json
import uuid

from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from DatabaseApp.models import LLMConfiguration, LLMConfigurationCustomerMapping
from Platform.tests.test_data import create_customer, create_llm_test_data


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Create test data
        self.llm_configuration, self.customer_uuid, self.llm_provider_uuid = create_llm_test_data()
        # Ensure you have the correct UUIDs for your tests
        self.user_uuid = uuid.uuid4()


####
# =========================== Tests for LLMConfigurationViewSet ===================================
####
class LLMConfigurationViewSetTestCase(BaseTestCase):

    ###
    # ========= Tests for "add_llm_configuration" API ==========
    ###

    # 1. With all correct values
    def test_add_llm_configuration_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_name": "Azure Open AI 3",
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid,  # Use the correct UUID here
            "llm_configuration_details_json": {
                "llm_provider": "Azure Open AI",
                "api_key": "51df12767",
                "deployment_name": "AYG",
                "model_name": "gpt-35-turbo",
                "api_base": "https://americanyacht.com",
                "api_type": "Azure",
                "api_version": "2023-09-15-preview"
            }
        }
        response = self.client.post(
            reverse("Platform:llm_configuration"),
            payload,
            format="json",
            headers={
                "customer_uuid":self.customer_uuid.cust_uuid,
                "user_uuid":self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    # 2. With customer_uuid null
    def test_add_llm_configuration_customer_uuid_null(self):
        # Simulate a POST request with customer_uuid null
        payload = {
            "llm_configuration_name": "Azure Open AI 3",
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid,
            "llm_configuration_details_json": {
                "llm_provider":"Azure Open AI",
                "api_key":"51df12767",
                "deployment_name":"AYG",
                "model_name":"gpt-35-turbo",
                "api_base":"https://americanyacht.com",
                "api_type":"Azure",
                "api_version":"2023-09-15-preview"
            }
        }
        response = self.client.post(
            reverse("Platform:llm_configuration"),payload,format="json"
            , headers={
                "customer_uuid": None,
                "user_uuid":self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 3. With user_uuid null
    def test_add_llm_configuration_user_uuid_null(self):
        # Simulate a POST request with customer_uuid null
        payload = {
            "llm_configuration_name": "Azure Open AI 3",
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid
            ,
            "llm_configuration_details_json": {
                "llm_provider": "Azure Open AI",
                "api_key": "51df12767",
                "deployment_name": "AYG",
                "model_name": "gpt-35-turbo",
                "api_base": "https://americanyacht.com",
                "api_type": "Azure",
                "api_version": "2023-09-15-preview"
            }
        }
        response = self.client.post(
            reverse("Platform:llm_configuration"), payload, format="json"
            , headers={
                "customer_uuid": self.customer_uuid,
                "user_uuid": None
            }
        )

        # Expecting a 400 Bad Request due to customer_uuid null
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 4. With invalid payload
    def test_add_llm_configuration_invalid_payload(self):
        # Simulate a POST request with invalid payload
        payload = {
            "llm_configuration": "Azure Open AI 3", # key should be llm_configuration_name
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid,
            "llm_configuration_details_json": {
                "llm_provider":"Azure Open AI",
                "api_key":"51df12767",
                "deployment_name":"AYG",
                "model_name":"gpt-35-turbo",
                "api_base":"https://americanyacht.com",
                "api_type":"Azure",
                "api_version":"2023-09-15-preview"
            }
        }
        response = self.client.post(
            reverse("Platform:llm_configuration"),payload,format="json"
            , headers={
                "customer_uuid": self.customer_uuid,
                "user_uuid":self.user_uuid
            }
        )

        # Expecting a 400 Bad Request due to invalid payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_add_llm_configuration_invalid_payload2(self):
        # Simulate a POST request with invalid payload
        payload = {
            "llm_configuration_name": "Azure Open AI 3", # key should be llm_configuration_name
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid,
            "llm_configuration_details_json": {
                "llm_provider":"Azure Open AI",
                "api_key":"51df12767",
                "deployment_name":"AYG",
                "api_base":"https://americanyacht.com",
                "api_type":"Azure",
                "api_version":"2023-09-15-preview"
            }
        }
        response = self.client.post(
            reverse("Platform:llm_configuration"),payload,format="json"
            , headers={
                "customer_uuid": self.customer_uuid,
                "user_uuid":self.user_uuid
            }
        )

        # Expecting a 400 Bad Request due to invalid payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    ###
    # ========= Tests for "edit_llm_configuration" API ==========
    ###

    # 1. With all correct values
    def test_edit_llm_configuration_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_uuid":self.llm_configuration.llm_configuration_uuid,
            "llm_configuration_name": "LLM Configuration 2",
            "llm_configuration_details_json": self.llm_configuration.llm_configuration_details_json,
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid
        }
        response = self.client.put(
            reverse("Platform:llm_configuration"),payload,format="json"
            , headers={
                "user_uuid":self.user_uuid
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
                "result": "LLM Configuration updated successfully"
            })

    def test_edit_llm_configuration_json_invalid(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "llm_configuration_name": "LLM Configuration 2",
            "llm_configuration_details_json": {
                "llm_provider": "Azure Open AI",
                "api_key": "51df12767",
                "delopment_name": "AYG",
                "model_name": "gpt-35-turbo",
                "api_base": "https://americanyacht.com",
                "api_type": "Azure",
                "api_version": "2023-09-15-preview"
            },
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid

        }
        response = self.client.put(
            reverse("Platform:llm_configuration"), payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # 2. With customer_uuid 
    def test_edit_llm_configuration_customer_uuid(self):
        llm_configuration_details_json = {
            "llm_provider": "Azure Open AI",
            "api_key": "95058a9e99794e4689d179dd726e7eec",
            "deployment_name": "vassar-turbo35-16k",
            "model_name": "gpt-35-turbo-instruct",
            "api_base": "https://vassar-openai.openai.azure.com/",
            "api_type": "azure",
            "api_version": "2023-07-01-preview"
        }
        user_uuid = uuid.uuid4()
        llm = LLMConfiguration.objects.create(llm_configuration_uuid=uuid.uuid4(), llm_configuration_name='llm_configuration_name', llm_provider_uuid=self.llm_provider_uuid, llm_configuration_details_json=llm_configuration_details_json,
                                        is_default = False, created_by=user_uuid, updated_by=user_uuid)
        
        # Creating new uuid for mapping llm configuration and customer
        mapping_uuid = uuid.uuid4()
        customer_uuid=create_customer()
        LLMConfigurationCustomerMapping.objects.create(
            mapping_uuid= mapping_uuid,
            llm_configuration_uuid = llm,
            customer_uuid = customer_uuid,
            created_by = user_uuid,
            updated_by = user_uuid
        )

        # Simulate a POST request with customer_uuid null
        payload = {
            "llm_configuration_uuid": llm.llm_configuration_uuid,
            "llm_configuration_name": "LLM Configuration 2",
            "llm_configuration_details_json": llm.llm_configuration_details_json,
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid

        }
        response = self.client.put(
            reverse("Platform:llm_configuration"), payload, format="json"
            , headers={
                "customer_uuid": customer_uuid,
                "user_uuid": llm.created_by
            }
        )

        # Expecting a 400 Bad Request due to customer_uuid null
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 2. With user_uuid null
    def test_edit_llm_configuration_user_uuid_null(self):
        # Simulate a POST request with customer_uuid null
        payload = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "llm_configuration_name": "LLM Configuration 2",
            "llm_configuration_details_json": self.llm_configuration.llm_configuration_details_json,
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid

        }
        response = self.client.put(
            reverse("Platform:llm_configuration"), payload, format="json"
            , headers={
                "customer_uuid": self.customer_uuid,
                "user_uuid":None
            }
        )

        # Expecting a 400 Bad Request due to customer_uuid null
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "user_uuid should not be NULL"
            })

    # 4. With invalid payload
    def test_edit_llm_configuration_invalid_payload(self):
        # Simulate a POST request with invalid payload
        payload = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "llm_configuration": "LLM Configuration 2",
            "llm_configuration_details_json": self.llm_configuration.llm_configuration_details_json,
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid

        }
        response = self.client.put(
            reverse("Platform:llm_configuration"), payload, format="json"
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
                    "llm_configuration_name": [
                        "This field is required."
                    ]
                }
            })

    # 5. With existing name
    def test_edit_llm_configuration_existing_name(self):
        # Simulate a POST request with existing name
        payload = {
            "llm_configuration_uuid": self.llm_configuration.llm_configuration_uuid,
            "llm_configuration_name": "default_llm",
            "llm_configuration_details_json": self.llm_configuration.llm_configuration_details_json,
            "llm_provider_uuid": self.llm_provider_uuid.llm_provider_uuid
        }
        response = self.client.put(
            reverse("Platform:llm_configuration"), payload, format="json"
            , headers={
                "user_uuid": self.user_uuid
            }
        )

        # Expecting a 400 Bad Request due with existing name
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "LLM Configuration already exists"
            })


    #configuration is not found
    def test_edit_llm_configuration_not_found(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_uuid": self.user_uuid,
            "llm_configuration_name": "LLM Configuration 2",
            "llm_configuration_details_json": self.llm_configuration.llm_configuration_details_json,
            "llm_provider_uuid":self.llm_provider_uuid.llm_provider_uuid
        }
        response = self.client.put(
            reverse("Platform:llm_configuration"), payload, format="json"
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
                "result": "LLM Configuration not found"
            })

    ###
    # ========= Tests for "get_llm_configuration_by_id" API ==========
    ###

    # 1. With all correct values
    def test_get_llm_configuration_by_id_failure1(self):
        # Simulate a GET request with valid parameters
        url = f"{reverse('Platform:llm_configuration')}/{self.llm_configuration.llm_configuration_uuid}"
        response = self.client.get(
            url
        )

        # Check if the response is Failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # 2. With Incorrect values
    def test_get_llm_configuration_by_id_failure2(self):
        # Simulate a GET request with valid parameters
        url = f"{reverse('Platform:llm_configuration')}/{self.llm_configuration.llm_configuration_uuid}"
        response = self.client.get(
            url,
            headers={
                "customer_uuid": self.customer_uuid,
            }
        )

        # Check if the response is Failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ###
    # ========= Tests for "get_llm_configurations" API ==========
    ###

    # 1. With all correct values
    def test_get_llm_configurations_success(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:llm_configuration"), headers={
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)


    ###
    # ========= Tests for "delete_llm_configuration" API ==========
    ###

    # 1. With all correct values
    def test_delete_llm_configuration_success(self):
        # Simulate a POST request with valid parameters
        url = f"{reverse('Platform:llm_configuration')}/{self.llm_configuration.llm_configuration_uuid}"
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
                "result": "LLM Configuration deleted successfully"
            })

    # 2.user_uuid not provided
    def test_delete_llm_configuration_user_id_null(self):
        # Simulate a POST request with valid parameters
        url = f"{reverse('Platform:llm_configuration')}/{self.llm_configuration.llm_configuration_uuid}"
        response = self.client.delete(
            url, format="json"
            , headers={
                "user_uuid": None
            }
        )

        # Check if the response is Failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "result": "user_uuid should not be NULL",
                "status": False,
                "code": 400
            })

    ###
    # ========= Tests for "get_llm_provider_meta_data" API ==========
    ###

    # 1. With all correct values
    def test_get_llm_provider_meta_data_success(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:get_llm_provider_meta_data")
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)
    

    ###
    # ========= Tests for "verify_llm_configuration" API ==========
    ###

    # 1. With all correct values
    def test_verify_llm_configuration_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_details_json": {
                "llm_provider": "Azure Open AI",
                "api_key": "95058a9e99794e4689d179dd726e7eec",
                "deployment_name": "vassar-turbo35-16k",
                "model_name": "gpt-35-turbo-16k",
                "api_base": "https://vassar-openai.openai.azure.com/",
                "api_type": "azure",
                "api_version": "2024-02-01"
            }
        }
        response = self.client.post(
            reverse("Platform:verify_llm_configuration"),
            payload,
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 2. With Incorrect values
    def test_verify_llm_configuration_failure(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_details_json": None
        }
        response = self.client.post(
            reverse("Platform:verify_llm_configuration"),
            payload,
            format="json"
        )

        # Check if the response is Failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 3. With Incorrect values
    def test_verify_llm_configuration_failure2(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_details_json": {
                "llm_provider": "Azure Open AI",
                "api_key": "95058a9e99794e4689d179dd726e7eec",
                "deployment_name": "vassar-turbo35-16k",
                "api_base": "https://vassar-openai.openai.azure.com/",
                "api_type": "azure",
                "api_version": "2024-02-01"
            }
        }
        response = self.client.post(
            reverse("Platform:verify_llm_configuration"),
            payload,
            format="json"
        )

        # Check if the response is Failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 4. With Incorrect values
    def test_verify_llm_configuration_failure3(self):
        # Simulate a POST request with valid parameters
        payload = {
            "llm_configuration_details_json": {
                "llm_provider": "Azure Open AI",
                "api_key": "95058a9e99794e4689d179dd726e7eec",
                "deployment_name": "vassar-tur",
                "model_name": "gpt-35-turbo-16k",
                "api_base": "https://vassar-openai.openai.azure.com/",
                "api_type": "azure",
                "api_version": "2024-02-01"
            }
        }
        response = self.client.post(
            reverse("Platform:verify_llm_configuration"),
            payload,
            format="json"
        )

        # Check if the response is Failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)