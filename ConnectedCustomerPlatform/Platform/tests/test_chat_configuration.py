import json
import uuid
from unittest.mock import patch, MagicMock
from urllib.parse import urlencode

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from Platform.tests.test_data import create_chat_configuration_test_data
from Platform.constant.success_messages import SuccessMessages
from Platform.constant.error_messages import ErrorMessages


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        (
            self.mapping,
            self.test_data1

        ) = create_chat_configuration_test_data()

        self.customer_uuid = self.mapping.customer_uuid
        self.application_uuid = self.mapping.application_uuid
        self.chat_configuration_type = "intent_page"
        self.chat_configuration_uuid = "7759a5b5-1952-4b90-8b28-7830d3406472"
        self.user_id = "user_id"
        self.wrong_uuid = "6559a5b3-1952-4b90-8b28-7830d3406472"
        self.headers = {
            'customer-uuid': self.mapping.customer_uuid.cust_uuid,
            'application-uuid': self.mapping.application_uuid.application_uuid,
            'user-uuid': self.user_id,
        }

class ChatConfigurationViewSetTestCase(BaseTestCase):

    ##
    # ========= Tests for "get all chat configuration" API ==========
    ##
    def test_get_all_chat_configurations_success(self):
        query_params = {
            'chat_configuration_type': self.chat_configuration_type
        }
        url = f"{reverse('Platform:chat_configuration')}?{urlencode(query_params)}"
        response = self.client.get(url, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result", response.data)

    def test_get_all_chat_configurations_status_default(self):
        query_params = {
            'chat_configuration_type':"landing_page"
        }
        url = f"{reverse('Platform:chat_configuration')}?{urlencode(query_params)}"
        response = self.client.get(url, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result", response.data)

    def test_get_all_chat_configurations_missing_application_uuid(self):
        headers = {
            'Customer-Uuid': self.customer_uuid,
            'User-Uuid': self.user_id
        }
        query_params = {
            'chat_configuration_type': self.chat_configuration_type
        }
        url = f"{reverse('Platform:chat_configuration')}?{urlencode(query_params)}"
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "application_uuid should not be NULL"

            })

    def test_get_all_chat_configurations_missing_customer_uuid(self):
        headers = {
            'Application-Uuid': self.application_uuid,
            'User-Uuid': self.user_id
        }
        query_params = {
            'chat_configuration_type': self.chat_configuration_type
        }
        url = f"{reverse('Platform:chat_configuration')}?{urlencode(query_params)}"
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "customer_uuid should not be NULL"

            })

    def test_get_all_chat_configurations_missing_chat_configuration_type(self):
        headers = {
            'Application-Uuid': self.application_uuid,
            'Customer-Uuid': self.customer_uuid,
            'User-Uuid': self.user_id
        }
        response = self.client.get(reverse("Platform:chat_configuration"), headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": ErrorMessages.CHAT_CONFIGURATION_TYPE_NOT_NULL
            })


    @patch('Platform.dao.impl.chat_configuration_dao_impl.ChatConfigurationDAOImpl.get_all_chat_configurations')
    def test_get_all_chat_configurations_no_data(self, mock_get_all_chat_configurations):
        mock_get_all_chat_configurations.return_value = []
        headers = {
            'Application-Uuid': self.application_uuid,
            'Customer-Uuid': self.customer_uuid,
            'User-Uuid': self.user_id
        }
        query_params = {
            'chat_configuration_type': self.chat_configuration_type
        }
        url = f"{reverse('Platform:chat_configuration')}?{urlencode(query_params)}"
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["result"]), 0)



    ###
    # ========= Tests for "get active configuration" API ==========
    ###
    def test_get_active_chat_configurations_success(self):
        query_params = {
            'application_uuid': uuid.UUID(self.application_uuid.application_uuid),
            'customer_uuid':uuid.UUID(self.customer_uuid.cust_uuid)
        }
        url = f"{reverse('Platform:chat_configuration_activation')}?{urlencode(query_params)}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result", response.data)


    def test_get_active_chat_configurations_no_configs_with_defaults(self):
        query_params = {
            'application_uuid': str('3359a5b5-1952-4b90-8b28-7830d3406472'),
            'customer_uuid': str('3359a5b5-1952-4b90-8b28-7830d3406472'),
        }
        url = f"{reverse('Platform:chat_configuration_activation')}?{urlencode(query_params)}"

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("chat_details_json", response.data["result"])




    def test_get_active_chat_configurations_missing_application_uuid(self):
        query_params = {
            'customer_uuid': str('3359a5b5-1952-4b90-8b28-7830d3406472'),
        }
        url = f"{reverse('Platform:chat_configuration_activation')}?{urlencode(query_params)}"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": {'application_uuid': ['This field is required.']}

            })

    def test_get_active_chat_configurations_missing_customer_uuid(self):
        query_params = {
            'application_uuid': str('3359a5b5-1952-4b90-8b28-7830d3406472')
        }
        url = f"{reverse('Platform:chat_configuration_activation')}?{urlencode(query_params)}"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": {'customer_uuid': ['This field is required.']}
            })


    ###
    # ========= Tests for "get chat configuration" API ==========


    def test_get_chat_configuration_with_uuid(self):
        response = self.client.get(reverse('Platform:chat_configuration_by_id', args=[self.chat_configuration_uuid]), headers=self.headers)
        assert response.status_code == status.HTTP_200_OK


    def test_get_chat_configuration_not_found_raises_exception(self):

        response = self.client.get(reverse('Platform:chat_configuration_by_id', args=["cff586b0-5dc1-49fb-acab-e5b6f05a95ea"]), headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual( json.loads(response.content),
        {
                "code": 404,
                "status": False,
                "result": ErrorMessages.CHAT_CONFIGURATION_NOT_FOUND

            })

    ###
    # ========= Tests for "create or update chat configuration" API ==========
    ###
    def test_create_chat_configuration_success_web(self):
        data = {
            "chat_configuration_name": "THEME LIGHT",
            "description": self.test_data1.description,
            "chat_details_json": self.test_data1.chat_details_json,
            "chat_configuration_type": self.test_data1.chat_configuration_type,
            "chat_configuration_provider": self.test_data1.chat_configuration_provider
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers= self.headers,
            data=data,
            format='json'
        )      # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 200,
                "status": True,
                "result": SuccessMessages.CHAT_CONFIGURATION_UPDATED_SUCCESSFULLY
            })

    def test_update_chat_configuration_success_web(self):
        data = {
            "chat_configuration_uuid":self.test_data1.chat_configuration_uuid,
            "chat_details_json": self.test_data1.chat_details_json,
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=self.headers,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 200,
                "status": True,
                "result": SuccessMessages.CHAT_CONFIGURATION_UPDATED_SUCCESSFULLY
            })

    def test_update_chat_configuration_name_duplicated(self):
        data = {
            "chat_configuration_name": self.test_data1.chat_configuration_name,
            "description": self.test_data1.description,
            "chat_details_json": self.test_data1.chat_details_json,
            "chat_configuration_type": self.test_data1.chat_configuration_type,
            "chat_configuration_provider": self.test_data1.chat_configuration_provider
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=self.headers,
            data=data,
            format='json'
        )  # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": ErrorMessages.CHAT_CONFIGURATION_NAME_NOT_DUPLICATED
            })


    @patch('Platform.dao.impl.chat_configuration_dao_impl.ChatConfigurationDAOImpl.get_configuration_templates_and_name_count')
    def test_update_chat_configuration_template_count_exceeded(self, mock_get_configuration_templates_and_name_count):
        mock_get_configuration_templates_and_name_count.return_value = (5, 0)
        data = {
            "chat_configuration_name": self.test_data1.chat_configuration_name,
            "chat_configuration_type": self.test_data1.chat_configuration_type,
            "chat_configuration_provider": self.test_data1.chat_configuration_provider
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=self.headers,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": ErrorMessages.MAXIMUM_TEMPLATE_LIMIT_REACHED
            })

    def test_update_chat_configuration_wrong_landing_data(self):
        data = {
            "chat_configuration_name":"RED THEME",
            "chat_configuration_type": "landing_page",
            "chat_configuration_provider": self.test_data1.chat_configuration_provider,
            "chat_details_json": {"landing_page_configuration":{"header":{}}}

        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=self.headers,
            data=data,
            format='json'
        )  # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "result": "Invalid bubble_configuration : Field required",
                "status": False,
                "code": 400
            })

    def test_update_chat_configuration_wrong_intent_data(self):
        data = {
            "chat_configuration_name": "RED THEME",
            "chat_configuration_type": "intent_page",
            "chat_configuration_provider": self.test_data1.chat_configuration_provider,
            "chat_details_json": {"intent_page_configuration": {"header": {}}}
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=self.headers,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "result": "Invalid chat_avatar : Field required",
                "status": False,
                "code": 400
            })

    def test_update_chat_configuration_invalid_chat_configuration_name(self):
        data = {
            "chat_configuration_name": "",
            "chat_configuration_type": self.chat_configuration_type,
            "chat_configuration_provider": self.test_data1.chat_configuration_provider
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=self.headers,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": {
                    "chat_configuration_name": [
                        "This field may not be blank."
                    ]
                }
            })

    def test_update_chat_configuration_invalid_chat_configuration_type(self):
        data = {
            "chat_configuration_name": self.test_data1.chat_configuration_name,
            "chat_configuration_provider": self.test_data1.chat_configuration_provider
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=self.headers,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                'result': {'chat_configuration_type': ['This field is required.']}
            })

    def test_update_chat_configuration_invalid_application_uuid(self):
        headers = {
            "Customer-Uuid": self.customer_uuid,
            "Application-Uuid": "",
            'User-Uuid': self.user_id
        }
        data = {
            "chat_configuration_name": self.test_data1.chat_configuration_name,
            "chat_configuration_type": self.chat_configuration_type,
            "chat_configuration_provider": self.test_data1.chat_configuration_provider
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=headers,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": "application_uuid should not be NULL"
            })

    def test_update_chat_configuration_missing_customer_uuid(self):
        headers = {
            "Application-Uuid": self.application_uuid,
            'User-Uuid': self.user_id
        }
        data = {
            "chat_configuration_name": self.test_data1.chat_configuration_name,
            "chat_configuration_type": self.chat_configuration_type,
            "chat_configuration_provider": self.test_data1.chat_configuration_provider
        }
        response = self.client.post(
            reverse("Platform:chat_configuration"),
            headers=headers,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                 "result": "customer_uuid should not be NULL"
            })

    ##
    # ========= Tests for "update activation status of configuration" API ==========
    ##

    def test_update_activation_status_create_mapping(self):
        data = {
            'chat_configuration_uuid': "9959a5b5-1952-4b90-8b28-7830d3406472",
            'chat_configuration_type': self.chat_configuration_type
        }
        response = self.client.post(reverse("Platform:chat_configuration_activation"), headers=self.headers, data =data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result'] == SuccessMessages.CHAT_CONFIGURATION_STATUS_UPDATED_SUCCESSFULLY


    def test_update_activation_status_no_configuration(self):
        data = {
            'chat_configuration_uuid': uuid.uuid4(),
            'chat_configuration_type': self.chat_configuration_type
        }
        response = self.client.post(reverse("Platform:chat_configuration_activation"), headers=self.headers, data =data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": ErrorMessages.SAVE_CONFIGURATION_BEFORE_PUBLISHING
            })

    @patch('Platform.dao.impl.chat_configuration_mapping_dao_impl.ChatConfigurationMappingDAOImpl.get_or_create_mapping_by_publishing')
    def test_update_activation_status_get_mapping(self,mock_get_or_create_mapping_by_publishing):
        mock_get_or_create_mapping_by_publishing.return_value = (self.mapping,False)

        data = {
            'chat_configuration_uuid':self.chat_configuration_uuid ,
            'chat_configuration_type': self.chat_configuration_type
        }
        response = self.client.post(reverse("Platform:chat_configuration_activation"), headers=self.headers, data =data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result'] == SuccessMessages.CHAT_CONFIGURATION_STATUS_UPDATED_SUCCESSFULLY


    def test_update_activation_status_no_configuration_uuid(self):
        data = {
            'chat_configuration_uuid': "",
            'chat_configuration_type': self.chat_configuration_type
        }
        response = self.client.post(reverse("Platform:chat_configuration_activation"), headers=self.headers, data =data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                'result': ErrorMessages.CHAT_CONFIGURATION_UUID_NOT_NULL,
            })

    def test_update_activation_status_configuration_uuid_not_found(self):
        data = {
            'chat_configuration_uuid': "8796bded-7cf4-4cbd-8a7e-7e5566ffe987",
            'chat_configuration_type': self.chat_configuration_type
        }
        response = self.client.post(reverse("Platform:chat_configuration_activation"), headers=self.headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                'result': ErrorMessages.SAVE_CONFIGURATION_BEFORE_PUBLISHING,
            })

    @patch('Platform.dao.impl.chat_configuration_mapping_dao_impl.ChatConfigurationMappingDAOImpl.get_or_create_mapping_by_publishing')
    def test_update_activation_status_excpetion_occuring(self,mock_mapping_dao):
        mock_mapping_dao.get_or_create_mapping_by_publishing.side_effect = Exception("Unexpected error")

        data = {
            'chat_configuration_uuid': "9959a5b5-1952-4b90-8b28-7830d3406472",
            'chat_configuration_type': self.chat_configuration_type
        }
        response = self.client.post(reverse("Platform:chat_configuration_activation"),
                                    headers=self.headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                'result': ErrorMessages.CANNOT_UPDATE_ACTIVATION_STATUS,
            })

    ###
    # ========= Tests for "delete chat configuration" API ==========
    ###

    @patch('Platform.dao.impl.chat_configuration_dao_impl.ChatConfigurationDAOImpl.delete_configuration_by_uuid')
    def test_delete_chat_configuration_precreated_template_not_possible(self, mock_delete_configuration):
        mock_delete_configuration.return_value = (0, 0)
        response = self.client.delete(
            reverse('Platform:chat_configuration_by_id', args=[self.test_data1.chat_configuration_uuid]),
            headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": ErrorMessages.UNABLE_TO_DELETE_TEMPLATE
            }
        )

    def test_delete_chat_configuration_success(self):
        response = self.client.delete(
            reverse('Platform:chat_configuration_by_id', args=[self.test_data1.chat_configuration_uuid]), headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"], SuccessMessages.CHAT_CONFIGURATION_DELETED_SUCCESSFULLY)

    def test_delete_chat_configuration_mapping_not_found(self):
        response = self.client.delete(
            reverse('Platform:chat_configuration_by_id', args=['0059a5b5-1952-4b90-8b28-7830d3406472']), headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "code": 400,
                "status": False,
                "result": ErrorMessages.CHAT_CONFIGURATION_MAPPING_NOT_FOUND
            }
        )



