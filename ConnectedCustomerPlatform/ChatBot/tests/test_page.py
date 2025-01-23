from django.test import TestCase
from ChatBot.constant.success_messages import SuccessMessages
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from .test_error_data import create_data_page
from django.core.management import call_command
import uuid
import base64


class BaseTestCase(TestCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        
        super().setUpClass()
        call_command('makemigrations')
        call_command('migrate')


class PageCorrectionTestCase(BaseTestCase):
    
    def setUp(self):
        
        self.client = APIClient()
        file, error = create_data_page()
        
        self.file = file
        self.error = error
    
    def test_get_page_blocks(self):
        
        file_uuid = self.file.knowledge_source_uuid
        page = 6
        
        response = self.client.get(
            reverse('ChatBot:get_page_blocks', kwargs={'file_uuid' : file_uuid, 'page' : page})
        )
        
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result']['no_of_blocks'], 7)
    
    def test_get_page_blocks_no_page(self):
        
        file_uuid = self.file.knowledge_source_uuid
        page = 36
        
        response = self.client.get(
            reverse('ChatBot:get_page_blocks', kwargs={'file_uuid' : file_uuid, 'page' : page})
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_page_blocks_negative(self):
        
        file_uuid = str(uuid.uuid4())
        page = 6
        
        response = self.client.get(
            reverse('ChatBot:get_page_blocks', kwargs={'file_uuid' : file_uuid, 'page' : page})
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_page_correction(self):
        
        file_uuid = self.file.knowledge_source_uuid
        error_uuid = self.error.error_uuid
        
        image_stream = base64.b64encode(open('/home/vassar/Files/12.png', 'rb').read())
        
        page = 3
        blocks = [
            {
                'block_type' : 'text',
                'text_type' : 'Body',
                'content' : 'Sample body text'
            },
            {
                'block_type' : 'image',
                'name' : ['Figure-10'],
                'stream' : image_stream,
                'extension' : 'png',
                'content' : 'tesseract text'
            },
            {
                'block_type' : 'table',
                'name' : ['Table 8'],
                'columns' : ['a', 'b'],
                'matrix' : [['0', '1'], ['2', '3']],
                'stream' : image_stream,
                'extension' : 'png'
            }
        ]
        
        response = self.client.post(
            reverse('ChatBot:page_correction'),
            data={
                'file_uuid' : file_uuid,
                'error_uuid' : error_uuid,
                'page' : page,
                'blocks' : blocks
            },
            format="json"
        )
        
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result'], SuccessMessages.PAGE_CORRECTION_SUCCESS)
    
    def test_page_correction_negative(self):
        
        file_uuid = str(uuid.uuid4())
        error_uuid = self.error.error_uuid
        
        image_stream = base64.b64encode(open('/home/vassar/Files/12.png', 'rb').read())
        
        page = 3
        blocks = [
            {
                'block_type' : 'text',
                'text_type' : 'Body',
                'content' : 'Sample body text'
            },
            {
                'block_type' : 'image',
                'name' : ['Figure-10'],
                'stream' : image_stream,
                'extension' : 'png',
                'content' : 'tesseract text'
            },
            {
                'block_type' : 'table',
                'name' : ['Table 8'],
                'columns' : ['a', 'b'],
                'matrix' : [['0', '1'], ['2', '3']],
                'stream' : image_stream,
                'extension' : 'png'
            }
        ]
        
        response = self.client.post(
            reverse('ChatBot:page_correction'),
            data={
                'file_uuid' : file_uuid,
                'error_uuid' : error_uuid,
                'page' : page,
                'blocks' : blocks
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)