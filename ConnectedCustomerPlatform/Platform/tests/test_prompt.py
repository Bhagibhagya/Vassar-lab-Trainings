import json
import uuid
from django.test import TestCase
from urllib.parse import urlencode

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from Platform.tests.test_data import create_prompt_test_data, create_prompt_template_test_data, create_customer_application_instances


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        (
            self.prompt,
            self.deleted_prompt,
            self.prompt_category,
            self.test_prompt
        ) = create_prompt_test_data()

        (
            self.prompt_template,
            self.deleted_prompt_template
        ) = create_prompt_template_test_data()

        self.application, self.customer=create_customer_application_instances()
        self.user_id = uuid.uuid4()


####
# =========================== Tests for PromptViewSet ===================================
####
class PromptViewSetTestCase(BaseTestCase):
    ###
    # ========= Tests for "get_prompts" API ==========
    ###

    # 1. With all correct values
    def test_get_prompts_success(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:prompt"),headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid":self.prompt.application_uuid.application_uuid,
                "user_uuid":self.user_id
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    # 2. With all correct values but no matched data from db
    def test_get_prompts_empty(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:prompt"), headers={
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

    ###
    # ========= Tests for "add_prompt" API ==========
    ###

    # 1. With all correct values
    def test_add_prompt_success(self):
        # Simulate a POST request with valid parameters
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_name": "Prompt-2",
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.post(
            reverse("Platform:prompt"),payload,format="json"
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
                "result": "Prompt created successfully"
            })

    # 2. With application_uuid null
    def test_add_prompt_application_uuid_null(self):
        # Simulate a POST request with application_uuid null
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_name": "Prompt-2",
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.post(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": self.customer.cust_uuid,
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

    # 3. With customer_uuid null
    def test_add_prompt_customer_uuid_null(self):
        # Simulate a POST request with customer_uuid null
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_name": "Prompt-2",
            "prompt_category_uuid": self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.post(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": None,
                "application_uuid": self.application.application_uuid,
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
    def test_add_dimension_type_invalid_payload(self):
        # Simulate a POST request with invalid payload
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "name": "Prompt-2", # key should be prompt_name
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.post(
            reverse("Platform:prompt"), payload, format="json"
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
                    "prompt_name": [
                        "This field is required."
                    ]
                }
            })

    # 5. With existing name
    def test_add_prompt_with_existing_name(self):
        # Simulate a POST request with valid parameters
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_name": self.prompt.prompt_name,
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.post(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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
                "result": "Prompt already exists"
            })

    # 6. With invalid prompt_category
    def test_add_prompt_with_invalid_prompt_category(self):
        # Simulate a POST request with valid parameters
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_name": "Prompt-2",
            "prompt_category_uuid": "kajshkjahskjhsiuay",
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.post(
            reverse("Platform:prompt"), payload, format="json"
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
    # ========= Tests for "edit_prompt" API ==========
    ###

    # 1. With all correct values
    def test_edit_prompt_success(self):
        # Simulate a POST request with valid parameters
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_uuid":str(self.prompt.prompt_uuid),
            "prompt_name": "Prompt-3",
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.put(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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
                "result": "Prompt updated successfully"
            })

    # 2. With  application_uuid null
    def test_edit_prompt_with_application_uuid_null(self):
        # Simulate a POST request with application_uuid null
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_uuid": str(self.prompt.prompt_uuid),
            "prompt_name": "Prompt-3",
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.put(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
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

    # 2. With  customer_uuid null
    def test_edit_prompt_with_customer_uuid_null(self):
        # Simulate a POST request with customer_uuid null
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_uuid": str(self.prompt.prompt_uuid),
            "prompt_name": "Prompt-3",
            "prompt_category_uuid": self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.put(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": None,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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

    # 3. With invalid payload
    def test_edit_dimension_with_invalid_payload(self):
        # Simulate a POST request with invalid payload
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_uuid": str(self.prompt.prompt_uuid),
            "name": "Prompt-3",
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.put(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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
                    "prompt_name": [
                        "This field is required."
                    ]
                }
            })

    # 4. With existing name
    def test_edit_prompt_with_existing_name(self):
        # Simulate a POST request with valid parameters
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_uuid": str(self.prompt.prompt_uuid),
            "prompt_name": self.test_prompt.prompt_name,
            "prompt_category_uuid" : self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.put(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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
                "result": "Prompt already exists"
            })

    # 1. With invalid prompt
    def test_edit_prompt_with_invalid_prompt(self):
        # Simulate a POST request with valid parameters
        prompt_template_uuid = str(self.prompt_template.prompt_template_uuid)
        payload = {
            "prompt_uuid": str(self.deleted_prompt.prompt_uuid),
            "prompt_name": "Prompt-3",
            "prompt_category_uuid": self.prompt_category.prompt_category_uuid,
            "prompt_details_json": {
                "prompt_template_uuid": prompt_template_uuid,
                "system_prompt": "system_prompt for template name 01",
                "context_prompt": "context_prompt for template name 01",
                "display_prompt": "display_prompt for template name 01",
                "remember_prompt": "remember_prompt for template name 01"
            }
        }
        response = self.client.put(
            reverse("Platform:prompt"), payload, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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
                "result": "Prompt not found"
            })

    ###
    # ========= Tests for "get_prompt_by_id" API ==========
    ###

    # 1. With all correct values
    def test_get_prompt_by_id_success(self):
        # Simulate a GET request with valid parameters
        url = f"{reverse('Platform:prompt')}/{self.prompt.prompt_uuid}"
        response = self.client.get(
            url,headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid":self.prompt.application_uuid.application_uuid,
                "user_uuid": self.user_id
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    # 2. With invalid prompt_uuid
    def test_get_prompt_by_id_with_invalid_id(self):
        # Simulate a GET request with invalid prompt_uuid(deleted)
        url = f"{reverse('Platform:prompt')}/{self.deleted_prompt.prompt_uuid}"
        response = self.client.get(
            url,headers={
                "customer_uuid": self.deleted_prompt.customer_uuid.cust_uuid,
                "application_uuid":self.deleted_prompt.application_uuid.application_uuid,
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
                "result": "Prompt not found"
            })

    ###
    # ========= Tests for "delete_prompt" API ==========
    ###

    # 1. With all correct values
    def test_delete_prompt_success(self):
        # Simulate a POST request with valid parameters
        url = f"{reverse('Platform:prompt')}/{self.prompt.prompt_uuid}"
        response = self.client.delete(
            url, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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
                "result": "Prompt deleted successfully"
            })

    # 2. With invalid prompt
    def test_delete_prompt_with_invalid_prompt(self):
        # Simulate a POST request with valid parameters
        url = f"{reverse('Platform:prompt')}/{self.deleted_prompt.prompt_uuid}"
        response = self.client.delete(
            url, format="json"
            , headers={
                "customer_uuid": self.prompt.customer_uuid.cust_uuid,
                "application_uuid": self.prompt.application_uuid.application_uuid,
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
                "result": "Prompt not found"
            })
