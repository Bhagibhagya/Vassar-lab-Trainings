from urllib.parse import urlencode

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from Platform.constant.error_messages import ErrorMessages
from Platform.tests.test_data import create_scope_test_data


class BaseTestCase(TestCase):

    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        self.dimension_mapping = create_scope_test_data()

        # Common headers
        self.headers = {
            'customer-uuid': self.dimension_mapping.customer_uuid_id,
            'application-uuid': self.dimension_mapping.application_uuid_id,
            'user-uuid': self.dimension_mapping.created_by,
        }


class ScopeTestCase(BaseTestCase):
    # utility function to check assertions
    def assert_response(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        if len(response_data.get('response')) > 0:
            expected_keys = {'label', 'value'}
            self.assertTrue(expected_keys.issubset(response_data.get('response')[0].keys()))

    ###
    # ========= Tests for "get_scope_categories" API ==========
    ###

    # 1. Success
    def test_get_scope_categories_success(self):
        response = self.client.get(
            reverse('Platform:get_scope_categories'),
            headers=self.headers,
        )

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(['NON_HIERARCHY'], response_data.get('response'))

    # ###
    # # ========= Tests for "get_scope_category_values" API ==========
    # ###

    # 1. Success - category - NON_HIERARCHY
    def test_get_scope_category_values_non_hierarchy(self):
        category = 'NON_HIERARCHY'
        response = self.client.get(
            reverse('Platform:get_scope_category_values', kwargs={'category': category}),
            headers=self.headers,
        )

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(['INTENT', 'SENTIMENT', 'CUSTOMER_TIER', 'GEOGRAPHY', 'ENTITY'], response_data.get('response'))


    ###
    # ========= Tests for "get_scope_types_values" API ==========
    ###

    # 1. category = NON_HIERARCHY, scope_type = INTENT
    def test_get_scope_types_values_intent(self):
        category = 'NON_HIERARCHY'
        scope_type = 'INTENT'
        application_uuid = self.headers.get('application-uuid')

        # Build the URL with query parameters
        base_url = reverse('Platform:get_scope_types_values', kwargs={'category': category, 'scope_type': scope_type})
        query_params = urlencode({'application-uuid': application_uuid})
        full_url = f"{base_url}?{query_params}"

        # Make the GET request with the full URL and headers
        response = self.client.get(
            full_url,
            headers=self.headers,
        )
        self.assert_response(response)

    # 2. category = NON_HIERARCHY, scope_type = GEOGRAPHY
    def test_get_scope_types_values_geography(self):
        category = 'NON_HIERARCHY'
        scope_type = 'GEOGRAPHY'
        application_uuid = self.headers.get('application-uuid')
        # Build the URL with query parameters
        base_url = reverse('Platform:get_scope_types_values', kwargs={'category': category, 'scope_type': scope_type})
        query_params = urlencode({'application-uuid': application_uuid})
        full_url = f"{base_url}?{query_params}"

        response = self.client.get(
            full_url,
            headers=self.headers,
        )

        self.assert_response(response)

    # 3. Missing Headers
    def test_get_scope_types_values_missing_headers(self):
        category = 'NON_HIERARCHY'
        scope_type = 'GEOGRAPHY'

        response = self.client.get(
            reverse('Platform:get_scope_types_values', kwargs={'category': category, 'scope_type': scope_type}),
        )

        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ErrorMessages.CUSTOMER_UUID_NOT_NULL, response_data.get('result'))
        
    # 4. category = NON_HIERARCHY, scope_type = ENTITY
    def test_get_scope_types_values_entity(self):
        category = 'NON_HIERARCHY'
        scope_type = 'ENTITY'
        application_uuid = self.headers.get('application-uuid')
        # Build the URL with query parameters
        base_url = reverse('Platform:get_scope_types_values', kwargs={'category': category, 'scope_type': scope_type})
        query_params = urlencode({'application-uuid': application_uuid})
        full_url = f"{base_url}?{query_params}"

        response = self.client.get(
            full_url,
            headers=self.headers,
        )

        self.assert_response(response)

    # 5. category = NON_HIERARCHY, scope_type = SENTIMENT
    def test_get_scope_types_values_sentiment(self):
        category = 'NON_HIERARCHY'
        scope_type = 'SENTIMENT'
        application_uuid = self.headers.get('application-uuid')
        # Build the URL with query parameters
        base_url = reverse('Platform:get_scope_types_values', kwargs={'category': category, 'scope_type': scope_type})
        query_params = urlencode({'application-uuid': application_uuid})
        full_url = f"{base_url}?{query_params}"

        response = self.client.get(
            full_url,
            headers=self.headers,
        )

        self.assert_response(response)
