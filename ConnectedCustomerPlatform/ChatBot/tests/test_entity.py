from django.core.management import call_command
from django.test import TestCase

from ChatBot.constant.constants import EntityConstants, TestEntityConstants
from ChatBot.constant.error_messages import ErrorMessages
from django.urls import reverse
from ChatBot.tests.test_data import create_headers_data, create_entity_test_data, create_knowledge_source_test_data
from Platform.constant import constants
from ChatBot.constant.success_messages import SuccessMessages
from rest_framework import status
from rest_framework.test import APIClient

# Base test class with setup methods for common functionality
class BaseTestCase(TestCase):

    maxDiff = None

    # Setup class-level configuration, including running migrations for test setup
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Run migrations to ensure database is ready for testing
        call_command('makemigrations')
        call_command('migrate')

    @classmethod
    def setUpTestData(cls):
        # Create test headers data (user_uuid, customer_uuid, application_uuid)
        (
            cls.user_uuid,
            cls.customer_uuid,
            cls.application_uuid,
        ) = create_headers_data()

        # Define headers for API requests
        cls.headers = {
            constants.CUSTOMER_UUID: cls.customer_uuid,
            constants.APPLICATION_UUID: cls.application_uuid,
            constants.USER_ID: cls.user_uuid
        }

    # Setup individual test data for each test case
    def setUp(self):

        # Create entity test data for the application
        self.entity = create_entity_test_data(self.customer_uuid, self.application_uuid)

        # Create knowledge source test data for the entity
        self.knowledge_source = create_knowledge_source_test_data(self.entity.entity_uuid, self.customer_uuid, self.application_uuid, self.user_uuid)

        # Initialize APIClient with the headers
        self.client = APIClient(headers=self.headers)


#### =========================== Tests for EntityViewSet ===================================
####

# Test cases for the EntityViewSet API
class EntityViewSetTestCase(BaseTestCase):

    ###
    # ========= Tests for "add_entity" API ==========
    ###

    # 1. Test adding a valid entity with correct parameters
    def test_add_entity_success(self):
        # Define payload for a valid entity creation request
        payload = {
            "description": "entity1244 Description",
            "name": "Test12 entity",
            "attributes": {"a1p1": ["a1v1p1"]},
        }

        # Send POST request to create an entity
        response = self.client.post(reverse("ChatBot:entity"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the response contains expected success message and status
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_201_CREATED,
                "status": True,
                "result": SuccessMessages.ENTITY_CREATED_SUCCESS
            }
        )

    # 2. Test adding an entity with the same name to trigger duplicate error
    def test_add_entity_with_same_name(self):
        # Define payload for creating an entity with a duplicate name
        payload = {
            "description": "entity1244 Description",
            "name": "same_entity",
            "application_uuid": self.application_uuid,
            "attributes": {"a1p1": ["a1v1p1"]},
        }

        # First entity creation (should succeed)
        _ = self.client.post(reverse("ChatBot:entity"), payload, format="json")
        # Second entity creation with the same name (should fail)
        response = self.client.post(reverse("ChatBot:entity"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Verify the response contains expected error message for duplicate entity
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_409_CONFLICT,
                "status": False,
                "result": ErrorMessages.DUPLICATE_ENTITY
            }
        )

    ###
    # ========= Tests for "get_application_entities" API ==========
    ###

    # Test fetching entities for a given application
    def test_get_entities_success(self):

        # Send GET request to retrieve entities for an application, it will create a default entity
        url = reverse('ChatBot:entity')
        response = self.client.get(url, {'total_entry_per_page': 5, 'page_number': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {'total_entries': 1,
                         'data': [{'entity_uuid': str(self.entity.entity_uuid),
                                   'entity_name': self.entity.entity_name,
                                   'attribute_keys': list(self.entity.attribute_details_json['attributes'].keys()),
                                   'is_default': False,
                                   'knowledge_source_count': 1
                                   }]
                         }

        response_data = response.json()

        self.assertDictEqual(
            response_data,
            {
                "code": 200,
                "status": True,
                "result": expected_data
            }
        )

    def test_get_entities_with_default_only_success(self):
        #  DELETE existing entity object from db
        self.knowledge_source.delete()
        self.entity.delete()

        # Send GET request to retrieve entities for an application, it will create a default entity
        url = reverse('ChatBot:entity')
        response = self.client.get(url, {'total_entry_per_page':5, 'page_number': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        test_entity_uuid = 'ENTITY_UUID'

        # testing only having default entity
        expected_data= {'total_entries': 1,
                        'data': [
                                  {'entity_uuid': test_entity_uuid,
                                   'entity_name': EntityConstants.DEFAULT_ENTITY_NAME,
                                   'attribute_keys': [EntityConstants.DEFAULT_ATTRIBUTE_NAME],
                                   'is_default': True,
                                   'knowledge_source_count': 0
                                   }]
                        }

        response_data = response.json()
        response_data['result']['data'][0]['entity_uuid'] = test_entity_uuid

        self.assertDictEqual(
            response_data,
            {
                "code": 200,
                "status": True,
                "result": expected_data
            }
        )


    ###
    # ========= Tests for "delete_entity" API ==========
    ###

    # 1. Test successful deletion of an entity
    def test_delete_entity_success(self):
        # Send DELETE request to delete an existing entity
        response = self.client.delete(reverse("ChatBot:get_or_delete_entity", kwargs={"entity_uuid": self.entity.entity_uuid}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response contains expected success message for entity deletion
        self.assertDictEqual(
            response.json(),
            {
                "code": 200,
                "status": True,
                "result": ErrorMessages.ENTITY_DELETED
            }
        )

    # 2. Test deleting a non-existent entity
    def test_delete_entity_invalid_entity(self):
        # Send DELETE request to delete a non-existent entity
        response = self.client.delete(reverse("ChatBot:get_or_delete_entity", kwargs={"entity_uuid": 'c7f43048-c45b-454a-ac37-cdfe052449fa'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the response contains expected error message for non-existent entity
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "status": False,
                "result": ErrorMessages.UNABLE_TO_DELETE_ENTITY
            }
        )

    # 3. Test deleting a non-existent entity
    def test_delete_default_entity(self):
        # Send DELETE request to delete an existing entity
        response = self.client.delete(reverse("ChatBot:get_or_delete_entity", kwargs={"entity_uuid": self.entity.entity_uuid}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('ChatBot:entity')
        response = self.client.get(url, {'total_entry_per_page':5, 'page_number': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        # get default entity_uuid
        default_entity_uuid = None
        for entity in response_data['result']['data']:
            if entity['is_default']:
                default_entity_uuid = entity['entity_uuid']

        # Send DELETE request to delete a non-existent entity
        response = self.client.delete(
            reverse("ChatBot:get_or_delete_entity", kwargs={"entity_uuid": default_entity_uuid}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the response contains expected error message for non-existent entity
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "status": False,
                "result": ErrorMessages.UNABLE_TO_DELETE_ENTITY
            }
        )

    ###
    # ========= Tests for "update_entity" API ==========
    ###

    # 1. Test successful update of an entity
    def test_update_entity_success(self):
        # Define payload for updating an entity
        payload = {
            "description": "entity1244 Description",
            "name": "Test12345678 entity",
            "entity_uuid": self.entity.entity_uuid,
            "attributes": TestEntityConstants.ENTITY_ATTRIBUTE_DETAILS_JSON.attributes,
        }

        # Send PUT request to update an entity
        response = self.client.put(reverse("ChatBot:entity"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response contains expected success message for entity update
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.ENTITY_UPDATED_SUCCESS
            }
        )

    # 2. Test updating an entity with invalid data (missing attributes)
    def test_update_entity_invalid_data(self):
        # Define payload for updating an entity with invalid data (missing 'attributes' field)
        payload = {
            "description": "entity1244 Description",
            "name": "Test12345678 entity",
            "entity_uuid": self.entity.entity_uuid,
            "attributes": {"a1p1": ["a1v1p1"]},  # Incorrect field name
        }

        # Send PUT request with invalid data
        response = self.client.put(reverse("ChatBot:entity"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the response contains expected error message for invalid update
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "status": False,
                "result": ErrorMessages.CANNOT_DELETE_ASSIGNED_ENTITY_ATTRIBUTES.format(TestEntityConstants.ATTRIBUTE_NAME1)
            }
        )

    # Test unassigning an entity from knowledge source
    def test_unassign_entity_success(self):
        # Send PUT request to unassign an entity from knowledge source
        response = self.client.put(reverse("ChatBot:unassign_file_entity", kwargs={'knowledge_source_uuid': self.knowledge_source.knowledge_source_uuid,
                                                                           'entity_uuid': str(self.entity.entity_uuid)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response contains expected success message for unassignment
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.ENTITY_UNASSIGNED_SUCCESS
            }
        )

    # Test unassigning an entity from knowledge source
    def test_unassign_entity_invalid(self):
        # Send PUT request to unassign an entity from knowledge source
        response = self.client.put(reverse("ChatBot:unassign_file_entity", kwargs={
            'knowledge_source_uuid': self.knowledge_source.knowledge_source_uuid,
            'entity_uuid': '00000000-c45b-454a-ac37-cdfe052449fa'}))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the response contains expected error message for unassignment
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "status": False,
                "result": ErrorMessages.UNABLE_TO_UNASSIGN_ENTITY
            }
        )

    # Test unassigning an entity from knowledge source
    def test_unassign_entity_default(self):
        # Send PUT request to unassign an entity from knowledge source
        response = self.client.put(reverse("ChatBot:unassign_file_entity", kwargs={
            'knowledge_source_uuid': self.knowledge_source.knowledge_source_uuid,
            'entity_uuid': str(self.entity.entity_uuid)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('ChatBot:entity'), {'total_entry_per_page':5, 'page_number': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        # get default entity_uuid
        default_entity_uuid = None
        for entity in response_data['result']['data']:
            if entity['is_default']:
                default_entity_uuid = entity['entity_uuid']

        # Send PUT request to unassign an default entity from knowledge source
        response = self.client.put(reverse("ChatBot:unassign_file_entity", kwargs={
            'knowledge_source_uuid': self.knowledge_source.knowledge_source_uuid,
            'entity_uuid': default_entity_uuid}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the response contains expected error message for unassignment
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_403_FORBIDDEN,
                "status": False,
                "result": ErrorMessages.CANNOT_UNASSIGN_DEFAULT_ENTITY
            }
        )

    def test_get_entity_success(self):
        # Send GET request to retrieve entities for an application, it will create a default entity
        url = reverse('ChatBot:get_or_delete_entity', kwargs={'entity_uuid': str(self.entity.entity_uuid)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertDictEqual(
            response_data,
            {
                "code": 200,
                "status": True,
                "result": {
                    'entity_uuid': str(self.entity.entity_uuid),
                    'entity_name': self.entity.entity_name,
                    'entity_description': self.entity.entity_description,
                    'attributes': self.entity.attribute_details_json['attributes']
                }
            }
        )

    # Test fetching entities for a given application
    def test_get_knowledge_sources_by_entities(self):
        # Send GET request to retrieve knowledge sources by entity for an application, it will create a default entity
        url = reverse('ChatBot:knwoledge_entities', kwargs={'entity_uuid': str(self.entity.entity_uuid)})
        response = self.client.get(url, {'total_entry_per_page': 5, 'page_number': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {'total_entries': 1,
                         'data': [{'knowledge_source_uuid': str(self.knowledge_source.knowledge_source_uuid),
                                   'knowledge_source_name': self.knowledge_source.knowledge_source_name
                                   }]
                         }

        response_data = response.json()

        self.assertDictEqual(
            response_data,
            {
                "code": 200,
                "status": True,
                "result": expected_data
            }
        )



    def test_update_knowledge_source_entity_unassignment_success(self):
        payload = {
            "knowledge_source_uuid": str(self.knowledge_source.knowledge_source_uuid),  
            "entity_uuid": str(self.entity.entity_uuid),
            "unassign": True
        }

        # Send PUT request to update an entity
        response = self.client.put(reverse("ChatBot:update_knowledge_source_entity_assignment"), payload, format="json")

        # Debugging output for response
        print("Response Status Code:", response.status_code)  # Print actual status code
        print("Response JSON:", response.json())              # Print the full response for debugging

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response contains expected success message for entity update
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.UPDATE_KNOWLEDGE_SOURCE_ENTITY_SUCCESS
            }
        )

    def test_update_knowledge_source_entity_assignment_success(self):

        response = self.client.put(reverse("ChatBot:unassign_file_entity", kwargs={
            'knowledge_source_uuid': self.knowledge_source.knowledge_source_uuid,
            'entity_uuid': str(self.entity.entity_uuid)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('ChatBot:entity'), {'total_entry_per_page':5, 'page_number': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        # get default entity_uuid
        default_entity_uuid = None
        for entity in response_data['result']['data']:
            if entity['is_default']:
                default_entity_uuid = entity['entity_uuid']
        payload = {
            "knowledge_source_uuid": str(self.knowledge_source.knowledge_source_uuid),  
            "prev_entity_uuid": str(self.knowledge_source.entity_uuid),
            "entity_uuid": str(self.entity.entity_uuid),
            "unassign": False,
            "attribute_details_json": {
                "attributes": {
                    "aslkdjf": ["asdfjn"]  # Ensure attributes are correctly formatted
                },
                "entity_name": "p1"
            }
        }

        # Send PUT request to update an entity
        response = self.client.put(reverse("ChatBot:update_knowledge_source_entity_assignment"), payload, format="json")

        # Debugging output for response
        print("Response Status Code:", response.status_code)  # Print actual status code
        print("Response JSON:", response.json())              # Print the full response for debugging

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response contains expected success message for entity update
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.UPDATE_KNOWLEDGE_SOURCE_ENTITY_SUCCESS
            }
        )
