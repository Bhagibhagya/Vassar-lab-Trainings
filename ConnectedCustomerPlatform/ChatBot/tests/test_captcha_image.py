from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ChatBot.constant.error_messages import ErrorMessages

class CaptchaViewSetTestCase(APITestCase):
    def setUp(self):
        # Set up any necessary data for the tests
        self.url = reverse('ChatBot:generate_captcha_image')  # Replace 'captcha' with the actual route name


    def test_generate_captcha_success(self):
        """Test successful CAPTCHA generation."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])  # Check that status is true
        self.assertEqual(response.data['code'], 200)  # Ensure the code is 200
        self.assertIn('captcha_image', response.data['result'])  # Check for CAPTCHA image
        self.assertIn('encoded_text', response.data['result'])  # Check for encoded text


    def test_generate_captcha_invalid_method(self):
        """Test that GET requests are not allowed."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_generate_captcha_empty_request(self):
        """Test CAPTCHA generation with empty payload."""
        response = self.client.get(self.url, data={})  # Assuming empty data is allowed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])  # Check that status is true
        self.assertEqual(response.data['code'], 200)  # Ensure the code is 200
        self.assertIn('captcha_image', response.data['result'])  # Ensure the CAPTCHA is generated
        self.assertIn('encoded_text', response.data['result'])  # Check for encoded text


    @patch('ChatBot.services.impl.captcha_service_impl.CaptchaServiceImpl.generate_captcha_image')
    def test_generate_captcha_image_none_both(self, mock_generate):
        # Mock the generate_captcha_image to return (None, None)
        mock_generate.return_value = (None, None)
        # Make the request
        response = self.client.get(self.url)
        # Check for the CustomException in the response
        self.assertEqual(response.status_code, 400)  # Assuming 500 is returned for the exception
        self.assertIn(ErrorMessages.FAILED_T0_GENERATE_IMAGE, str(response.data))