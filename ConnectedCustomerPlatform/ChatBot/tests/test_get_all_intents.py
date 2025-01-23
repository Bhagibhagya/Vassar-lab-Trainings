from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from DBServices.models import Dimensions, DimensionTypes
from ChatBot.constant.constants import Constants

class GetAllIntentsTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('ChatBot:get_all_intents')  # Update this with the correct URL name


    ###
    # ========= Tests for "get_all_intents" API ==========
    ###

    # 1. get all intents with success
    @patch('ChatBot.views.chat_bot.DimensionTypes.objects.filter')
    @patch('ChatBot.views.chat_bot.Dimensions.objects.filter')
    def test_get_all_intents_success(self, mock_dimensions_filter, mock_dimension_types_filter):
        # Arrange
        mock_dimension_type = MagicMock()
        mock_dimension_type.dimension_type_uuid = 'intent_uuid'
        mock_dimension_types_filter.return_value.first.return_value = mock_dimension_type

        mock_dimensions_filter.return_value = [
            MagicMock(dimension_name='intent1'),
            MagicMock(dimension_name='intent2'),
        ]

        headers = {
            'HTTP_APPLICATION-UUID': 'app_uuid',
            'HTTP_CUSTOMER-UUID': 'customer_uuid',
        }

        # Act
        response = self.client.get(self.url, **headers)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(Constants.INTENTS, response.data['result'])
        self.assertEqual(response.data['result'][Constants.INTENTS], ['intent1', 'intent2'])
        mock_dimensions_filter.assert_called_once_with(
            application_uuid='app_uuid',
            customer_uuid='customer_uuid',
            is_deleted=False,
            dimension_type_uuid='intent_uuid'
        )

    # 2. test with missing_application_uuid
    @patch('ChatBot.views.chat_bot.DimensionTypes.objects.filter')
    @patch('ChatBot.views.chat_bot.Dimensions.objects.filter')
    def test_get_all_intents_missing_application_uuid(self, mock_dimensions_filter, mock_dimension_types_filter):
        # Arrange
        mock_dimension_type = MagicMock()
        mock_dimension_type.dimension_type_uuid = 'intent_uuid'
        mock_dimension_types_filter.return_value.first.return_value = mock_dimension_type

        headers = {
            'HTTP_CUSTOMER-UUID': 'customer_uuid',
        }

        # Act
        response = self.client.get(self.url, **headers)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], Constants.NO_HEADERS)

    # 3. test with missing customer_uuid
    @patch('ChatBot.views.chat_bot.DimensionTypes.objects.filter')
    @patch('ChatBot.views.chat_bot.Dimensions.objects.filter')
    def test_get_all_intents_missing_customer_uuid(self, mock_dimensions_filter, mock_dimension_types_filter):
        # Arrange
        mock_dimension_type = MagicMock()
        mock_dimension_type.dimension_type_uuid = 'intent_uuid'
        mock_dimension_types_filter.return_value.first.return_value = mock_dimension_type

        headers = {
            'HTTP_APPLICATION-UUID': 'app_uuid',
        }

        # Act
        response = self.client.get(self.url, **headers)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], Constants.NO_HEADERS)


    # 4. test with no response getting no intents
    @patch('ChatBot.views.chat_bot.DimensionTypes.objects.filter')
    @patch('ChatBot.views.chat_bot.Dimensions.objects.filter')
    def test_get_all_intents_no_intents(self, mock_dimensions_filter, mock_dimension_types_filter):
        # Arrange
        mock_dimension_type = MagicMock()
        mock_dimension_type.dimension_type_uuid = 'intent_uuid'
        mock_dimension_types_filter.return_value.first.return_value = mock_dimension_type

        # Mocking empty results for dimensions
        mock_dimensions_filter.return_value = []

        headers = {
            'HTTP_APPLICATION-UUID': 'app_uuid',
            'HTTP_CUSTOMER-UUID': 'customer_uuid',
        }

        # Act
        response = self.client.get(self.url, **headers)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Access the result key and check if it contains the 'intents' key
        self.assertIn('result', response.data)
        self.assertIn('intents', response.data['result'])
        self.assertEqual(response.data['result']['intents'], [])

