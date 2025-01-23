import json
import uuid
from django.test import TestCase
from urllib.parse import urlencode

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from Platform.tests.test_data import create_prompt_template_mapping, create_customer_application_instances


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        (
            self.prompt_template,
            self.prompt_template_1,
            self.prompt_template_2,
            self.mapping
        ) = create_prompt_template_mapping()

        self.application, self.customer = create_customer_application_instances()
        self.user_id = uuid.uuid4()


####
# =========================== Tests for PromptTemplateViewSet ===================================
####
class PromptTemplateViewSetTestCase(BaseTestCase):
    ###
    # ========= Tests for "get_prompt_templates" API ==========
    ###

    # 1. With all correct values
    def test_get_prompt_templates_success(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:prompt_template"), headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    # 2. With all correct values but no matched data from db
    def test_prompt_templates_empty(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:prompt_template"), headers={
                "customer_uuid": uuid.uuid4(),
                "application_uuid": uuid.uuid4(),
                "user_uuid": self.user_id
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

    # 3. With all correct values under a prompt_category
    def test_get_prompt_templates_under_category_success(self):
        # Simulate a GET request with valid parameters
        query_params = {"prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid}
        url = f"{reverse('Platform:prompt_template')}?{urlencode(query_params)}"
        response = self.client.get(
            url, headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)


    ###
    # ========= Tests for "add_prompt_template" API ==========
    ###

    # 1. With all correct values
    def test_add_prompt_template_with_invalid_customer(self):
        # Simulate a POST request with valid parameters
        payload = {
            "prompt_template_name": "PromptTemplate",
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.post(
            reverse("Platform:prompt_template"), payload, format="json"
            , headers={
                "customer_uuid": uuid.uuid4(),
                "application_uuid": self.application.application_uuid,
                "user_uuid": self.user_id
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

    # 1. With all correct values
    def test_add_prompt_template_with_invalid_application(self):
        # Simulate a POST request with valid parameters
        payload = {
            "prompt_template_name": "PromptTemplate",
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.post(
            reverse("Platform:prompt_template"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": uuid.uuid4(),
                "user_uuid": self.user_id
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
                "result": "Application not found"
            })

    # 1. With all correct values
    def test_add_prompt_template_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "prompt_template_name": "PromptTemplate",
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description":"description"
        }
        response = self.client.post(
            reverse("Platform:prompt_template"),payload,format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
                "user_uuid":self.user_id
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
                "result": "Prompt Template created successfully"
            })

    # 2. With application_uuid null
    def test_add_prompt_template_application_uuid_null(self):
        # Simulate a POST request with application_uuid null
        payload = {}
        response = self.client.post(
            reverse("Platform:prompt_template"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": None,
                "user_uuid":self.user_id
            }
        )

        # Expecting a 400 Bad Request due to application_uuid null
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "application_uuid should not be NULL"
            })

    # 3. With customer_uuid null
    def test_add_prompt_template_customer_uuid_null(self):
        # Simulate a POST request with customer_uuid null
        payload = {}
        response = self.client.post(
            reverse("Platform:prompt_template"), payload, format="json"
            , headers={
                "customer_uuid": None,
                "application_uuid": self.application.application_uuid,
                "user_uuid":self.user_id
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
                "result": "customer_uuid should not be NULL"
            })

    # 4. With invalid payload
    def test_add_prompt_template_invalid_payload(self):
        # Simulate a POST request with invalid payload
        payload = {
            "template_name": "Template Name 01", # key should be prompt_template_name
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.post(
            reverse("Platform:prompt_template"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
                "user_uuid": self.user_id
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
                    "prompt_template_name": [
                        "This field is required."
                    ]
                }
            })

    # 5. With existing name
    def test_add_prompt_template_with_existing_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "prompt_template_name": self.mapping.prompt_template_uuid.prompt_template_name,
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.post(
            reverse("Platform:prompt_template"), payload, format="json"
            , headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt template already exists"
            })

    # 7. With invalid prompt_category
    def test_add_prompt_template_with_invalid_prompt_category(self):
        # Simulate a POST request with valid parameters
        payload = {
            "prompt_template_name": self.prompt_template.prompt_template_name,
            "prompt_category_uuid": uuid.uuid4(),
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.post(
            reverse("Platform:prompt_template"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
                "application_uuid": self.application.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt category not found"
            })


    ###
    # ========= Tests for "edit_prompt_template" API ==========
    ###

    # 1. With all correct values
    def test_edit_prompt_template_success(self):
        # Simulate a POST request with valid parameters
        print("*********",self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid)
        payload = {
            "mapping_uuid":self.mapping.mapping_uuid,
            "prompt_template_uuid":self.mapping.prompt_template_uuid.prompt_template_uuid,
            "prompt_template_name": "prompt_template",
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.put(
            reverse('Platform:prompt_template'), payload, format="json"
            , headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt Template updated successfully"
            })

    # 2. With all application_uuid null
    def test_edit_prompt_template_with_application_uuid(self):
        # Simulate a POST request with application_uuid null
        payload = {}
        response = self.client.put(
            reverse('Platform:prompt_template'), payload, format="json"
            , headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": None,
                "user_uuid": self.user_id
            }
        )

        # Expecting a 400 Bad Request due to application_uuid null
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "application_uuid should not be NULL"
            })

    # 3. With all customer_uuid null
    def test_edit_prompt_template_with_customer_uuid(self):
        # Simulate a POST request with customer_uuid null
        payload = {}
        response = self.client.post(
            reverse('Platform:prompt_template'), payload, format="json"
            , headers={
                "customer_uuid": None,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "customer_uuid should not be NULL"
            })

    # 4. With invalid payload
    def test_edit_prompt_template_with_invalid_payload(self):
        # Simulate a POST request with invalid payload
        payload = {
            "mapping_uuid":self.mapping.mapping_uuid,
            "prompt_template_uuid": self.mapping.prompt_template_uuid.prompt_template_uuid,
            "template_name": "Template Name 01",  # key should be prompt_template_name
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.put(
            reverse('Platform:prompt_template'), payload, format="json"
            , headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                    "prompt_template_name": [
                        "This field is required."
                    ]
                }
            })

    # 7. With existing name
    def test_edit_prompt_template_with_existing_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "mapping_uuid": self.mapping.mapping_uuid,
            "prompt_template_uuid": self.mapping.prompt_template_uuid.prompt_template_uuid,
            "prompt_template_name": self.prompt_template_2.prompt_template_name,
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.put(
            reverse('Platform:prompt_template'), payload, format="json"
            , headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt template already exists"
            })

    # 8. With invalid prompt_category
    def test_edit_prompt_template_with_invalid_prompt_category(self):
        # Simulate a POST request with valid parameters
        payload = {
            "mapping_uuid": self.mapping.mapping_uuid,
            "prompt_template_uuid": self.mapping.prompt_template_uuid.prompt_template_uuid,
            "prompt_template_name": "New Prompt",
            "prompt_category_uuid": uuid.uuid4(),
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.put(
            reverse('Platform:prompt_template'), payload, format="json"
            , headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt category not found"
            })

    # 9. With invalid mapping_uuid
    def test_edit_prompt_template_with_invalid_prompt_template_uuid(self):
        # Simulate a POST request with valid parameters
        payload = {
            "mapping_uuid": self.mapping.mapping_uuid,
            "prompt_template_uuid": uuid.uuid4(),
            "prompt_template_name": "Prompt_Template",
            "prompt_category_uuid": self.mapping.prompt_template_uuid.prompt_category_uuid.prompt_category_uuid,
            "prompt_template_details_json": {
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            },
            "prompt_template_description": "description"
        }
        response = self.client.put(
            reverse('Platform:prompt_template'), payload, format="json"
            , headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt template not found"
            })


    ###
    # ========= Tests for "get_prompt_template_by_id" API ==========
    ###

    # 1. With all correct values
    def test_get_prompt_template_by_id_success(self):
        # Simulate a GET request with valid parameters
        url = f"{reverse('Platform:prompt_template')}/{self.mapping.mapping_uuid}"
        response = self.client.get(
            url, headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    # 2. With invalid prompt_template_uuid
    def test_get_prompt_template_by_id_with_invalid_id(self):
        # Simulate a GET request with invalid prompt_template_uuid
        url = f"{reverse('Platform:prompt_template')}/{uuid.uuid4()}"
        response = self.client.get(
            url, headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt template not found"
            })

    ###
    # ========= Tests for "delete prompt template" API ==========
    ###

    # 1. With all correct values
    def test_delete_prompt_template_status_success(self):
        # Simulate a POST request with valid parameters
        url = f"{reverse('Platform:prompt_template')}/{self.mapping.prompt_template_uuid.prompt_template_uuid}"
        response = self.client.delete(
            url, headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt Template deleted successfully"
            })

    # 2. With invalid id
    def test_delete_prompt_template_with_invalid_id(self):
        # Simulate a POST request with valid parameters
        url = f"{reverse('Platform:prompt_template')}/{uuid.uuid4()}"
        response = self.client.delete(
            url, headers={
                "customer_uuid": self.mapping.customer_uuid,
                "application_uuid": self.mapping.application_uuid,
                "user_uuid": self.user_id
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
                "result": "Prompt template not found"
            })

    ###
    # ========= Tests for "get prompt categories" API ==========
    ###

    # 1. With all correct values
    def test_get_prompt_category_success(self):
        # Simulate a POST request with valid parameters
        url = f"{reverse('Platform:prompt_category')}"
        response = self.client.get(
            url
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)