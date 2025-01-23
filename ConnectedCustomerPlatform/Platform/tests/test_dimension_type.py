import json
import uuid

from django.test import TestCase
from django.db import transaction, IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from Platform.tests.test_data import create_dimension_type_test_data
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages

class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        (
            self.default_dimension_type,
            self.dimension_type,
            self.dimension_type_mapping,
            self.dimension_type2
        ) = create_dimension_type_test_data()

        self.customer_uuid = self.dimension_type_mapping.customer_uuid_id
        self.application_uuid = self.dimension_type_mapping.application_uuid_id
        self.user_id = self.dimension_type_mapping.created_by


####
# =========================== Tests for DimensionTypeViewSet ===================================
####
class DimensionTypeViewSetTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mapping_uuid = self.dimension_type_mapping.mapping_uuid
        self.dimension_type_uuid = self.dimension_type_mapping.dimension_type_uuid_id
        self.description = self.dimension_type_mapping.description
        self.dimension_type_name = self.dimension_type.dimension_type_name

    ###
    # ========= Tests for "add_dimension_type" API ==========
    ###

    # 1. With all correct values
    def test_add_dimension_type_success(self):
        payload = {
            "dimension_type_name": "Dim1",
            "description": "Dim1 Description",
            "is_default": False
        }
        response = self.client.post(
            reverse("Platform:dimension_type"), payload,
            format="json",
            headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
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
                "result": SuccessMessages.ADD_DIMENSION_TYPE_SUCCESS
            })

    # 2. With invalid payload
    def test_add_dimension_type_invalid_payload(self):
        # Simulate a POST request with invalid payload
        payload = {
            "dimension_type_name": "",
            "description": "Description for dim 2",
            "is_default": False
        }
        response = self.client.post(
            reverse("Platform:dimension_type"), payload, format="json"
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            }
        )

        # Expecting a 400 Bad Request due to invalid payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertIn('This field may not be blank.', str(response.data.get('result')['dimension_type_name']))

    # 3. With existing name
    def test_add_dimension_type_with_existing_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "dimension_type_name": "Dimension Type 1",
            "description": "Random Desc",
            "is_default": False
        }
        response = self.client.post(
            reverse("Platform:dimension_type"), payload, format="json"
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
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
                "result": ErrorMessages.DIMENSION_TYPE_EXISTS
            })

    # 4. Add with default type name
    def test_add_dimension_type_with_default_name(self):
        # Simulate a POST request with valid parameters
        payload = {
            "dimension_type_name": "INTent",
            "description": "Random Desc",
            "is_default": False
        }
        response = self.client.post(
            reverse("Platform:dimension_type"), payload, format="json"
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
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
                "result": ErrorMessages.DIMENSION_TYPE_EXISTS
            })

    ###
    # # ========= Tests for "edit_dimension_type" API ==========
    # ###
    #
    # # 1. With Description Edit Success
    def test_edit_dimension_type_desc_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_type_uuid": self.dimension_type_uuid,
            "dimension_type_name": self.dimension_type_name,
            "description": "New Desc",
            "is_default": False,
            "status": True,
            "dimension_type_details_json": None
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertEqual(SuccessMessages.UPDATE_DIMENSION_TYPE_SUCCESS, response.data.get('result'))

    # 2. With Dimension Type Name Edit Success
    def test_edit_dimension_type_name_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_type_uuid": self.dimension_type_uuid,
            "dimension_type_name": "New Dim 1",
            "description": "New Desc",
            "is_default": False,
            "status": True,
            "dimension_type_details_json": None
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertEqual(SuccessMessages.UPDATE_DIMENSION_TYPE_SUCCESS, response.data.get('result'))

    # 3. With Default Dimension Type status update Success
    def test_edit_dimension_type_default_status_success(self):
        # Simulate a POST request with valid parameters
        payload = {
            "dimension_type_uuid": self.default_dimension_type.dimension_type_uuid,
            "dimension_type_name": "SENTIMENT",
            "status": True,
            "is_default": True,
            "dimension_type_details_json": None,
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertEqual(SuccessMessages.UPDATE_DIMENSION_TYPE_SUCCESS, response.data.get('result'))

    # 4. With Dimension Type already exists
    def test_edit_dimension_type_dimension_type_exists(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_type_uuid": self.dimension_type_uuid,
            "dimension_type_name": self.dimension_type2.dimension_type_name,
            "description": "New Desc",
            "is_default": False,
            "status": True,
            "dimension_type_details_json": None
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertEqual(ErrorMessages.DIMENSION_TYPE_EXISTS, response.data.get('result'))

    # 5. With Mapping uuid Null
    def test_edit_dimension_type_mapping_uuid_null(self):
        payload = {
            "dimension_type_uuid": self.dimension_type_uuid,
            "dimension_type_name": self.dimension_type_name,
            "description": "New Desc",
            "is_default": False,
            "status": True,
            "dimension_type_details_json": None
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertEqual(ErrorMessages.MAPPING_UUID_NOT_NULL, response.data.get('result'))

    # 7. Edit status for dimension types fail
    def test_edit_dimension_type_edit_status_fail(self):
        payload = {
            "mapping_uuid": uuid.uuid4(),
            "dimension_type_uuid": self.dimension_type_uuid,
            "dimension_type_name": self.dimension_type_name,
            "description": "New Desc",
            "is_default": False,
            "status": True,
            "dimension_type_details_json": None
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertEqual(ErrorMessages.DIMENSION_TYPE_NOT_FOUND, response.data.get('result'))

    # 8. With Default Dimension Type already exists
    def test_edit_dimension_type_default_name(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_type_uuid": self.dimension_type_uuid,
            "dimension_type_name": self.default_dimension_type.dimension_type_name,
            "description": "New Desc",
            "is_default": False,
            "status": True,
            "dimension_type_details_json": None
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertEqual(ErrorMessages.DIMENSION_TYPE_EXISTS, response.data.get('result'))

    # 9. Invalid Payload
    def test_edit_dimension_type_invalid_payload(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_type_uuid": self.dimension_type_uuid,
            "dimension_type_name": "",
            "description": "New Desc",
            "is_default": False,
            "status": True,
            "dimension_type_details_json": None
        }
        response = self.client.put(
            reverse('Platform:dimension_type'), payload
            , headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            },
            format="json"
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate the expected data in the response
        self.assertIn('This field may not be blank.', str(response.data.get('result')['dimension_type_name']))

    # ###
    # # ========= Tests for "get_dimension_types" API ==========
    # ###

    # 1. With all correct values
    def test_get_dimension_types_success(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse("Platform:dimension_type"), headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    # ###
    # # ========= Tests for "get_dimension_type_by_id" API ==========
    # ###

    # 1. With all correct values
    def test_get_dimension_type_by_id_success(self):
        # Simulate a GET request with valid parameters
        response = self.client.get(
            reverse('Platform:dimension_type_by_id', args=[self.mapping_uuid]), headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            }
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the expected data in the response
        self.assertIn("result", response.data)

    # # 2. With invalid dimension_type_uuid
    def test_get_dimension_type_by_id_with_invalid_id(self):
        response = self.client.get(
            reverse('Platform:dimension_type_by_id', args=[uuid.uuid4()]), headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
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
                "result": None
            })

    # ###
    # # ========= Tests for "delete_dimension_type" API ==========
    # ###

    # 1. With all correct values - default dimension type
    def test_delete_dimension_type_success(self):
        response = self.client.delete(
            reverse('Platform:dimension_type_by_id', args=[self.mapping_uuid]), headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SuccessMessages.DIMENSION_TYPE_DELETE_SUCCESS, response.data.get('result'))

    # 2. With non-existing dimension type
    def test_delete_dimension_type_dimension_type_not_exist(self):
        response = self.client.delete(
            reverse('Platform:dimension_type_by_id', args=[uuid.uuid4()]), headers={
                "customer_uuid": self.customer_uuid,
                "application_uuid": self.application_uuid,
                "user_uuid": self.user_id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ErrorMessages.DIMENSION_TYPE_NOT_FOUND, response.data.get('result'))