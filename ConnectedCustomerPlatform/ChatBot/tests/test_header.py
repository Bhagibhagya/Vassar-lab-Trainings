from django.test import TestCase
from ChatBot.constant.success_messages import SuccessMessages
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from .test_error_data import create_data_header
from django.core.management import call_command
import uuid


class BaseTestCase(TestCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        
        super().setUpClass()
        call_command('makemigrations')
        call_command('migrate')


class HeaderCorrectionTestCase(BaseTestCase):
    
        
    def setUp(self):
        
        self.client = APIClient()
        file, error = create_data_header()
        
        self.file = file
        self.error = error
    
    def test_get_h1_headings(self):
        
        file_uuid = self.file.knowledge_source_uuid
        response = self.client.get(reverse('ChatBot:get_h1_headings', kwargs={'file_uuid': file_uuid}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_json = response.json()
        blocks = response_json['result']['blocks']
        self.assertEqual(len(blocks), 18)
        
        app_id = response_json['result']['application_uuid']
        self.assertEqual(app_id, self.file.application_uuid.application_uuid)
    
    def test_get_h1_headings_negative(self):
        
        file_uuid = str(uuid.uuid4())
        response = self.client.get(reverse('ChatBot:get_h1_headings', kwargs={'file_uuid': file_uuid}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_child_blocks(self):
        
        file_uuid = self.file.knowledge_source_uuid
        block_id = '29e5f3b7-b09a-4189-a0f3-08ae9bc4988f'

        response = self.client.get(reverse('ChatBot:get_child_blocks', kwargs={'file_uuid': file_uuid, 'block_id' : block_id}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_json = response.json()
        blocks = response_json['result']['blocks']
        
        print(blocks)
        self.assertEqual(len(blocks), 10)
        
        fuuid = response_json['result']['file_uuid']
    
        self.assertEqual(fuuid, self.file.knowledge_source_uuid)
        
    def test_get_child_blocks_negative(self):
        
        file_uuid = str(uuid.uuid4())
        block_id = '29e5f3b7-b09a-4189-a0f3-08ae9bc4988f'

        response = self.client.get(reverse('ChatBot:get_child_blocks', kwargs={'file_uuid': file_uuid, 'block_id' : block_id}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_insert_text_block(self):
        
        prev_id = 'f4885fdb-1d6c-48ba-81c3-7da7cd55fcf6'
        file_uuid = self.file.knowledge_source_uuid
        
        response = self.client.post(
            reverse('ChatBot:errors_headers'),
            data={
                'previous_block_id' : prev_id,
                'file_uuid' : file_uuid,
                'block' : {
                    'text_type' : 'Body',
                    'content' : 'This text has been added'
                },
            },
            format="json"
        )
        
        json_response = response.json()
        message = json_response['result']
        
        self.assertEqual(message, SuccessMessages.BLOCK_INSERTED_SUCCESS)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_insert_text_block_prev_id_none(self):
        
        prev_id = None
        file_uuid = self.file.knowledge_source_uuid
        
        response = self.client.post(
            reverse('ChatBot:errors_headers'),
            data={
                'previous_block_id' : prev_id,
                'file_uuid' : file_uuid,
                'block' : {
                    'text_type' : 'Body',
                    'content' : 'This text has been added at beginning of json'
                },
            },
            format="json"
        )
        
        json_response = response.json()
        message = json_response['result']
        
        self.assertEqual(message, SuccessMessages.BLOCK_INSERTED_SUCCESS)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_insert_text_block_negative(self):
        
        prev_id = str(uuid.uuid4())
        file_uuid = str(uuid.uuid4())
        
        response = self.client.post(
            reverse('ChatBot:errors_headers'),
            data={
                'previous_block_id' : prev_id,
                'file_uuid' : file_uuid,
                'block' : {
                    'text_type' : 'Body',
                    'content' : 'This text has been added at beginning of json'
                },
            },
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_block(self):
        
        file_uuid = self.file.knowledge_source_uuid
        
        repsonse = self.client.delete(
            reverse('ChatBot:errors_headers'),
            data = {
                'file_uuid' : file_uuid,
                'block_id' : '3288c448-0549-4065-94a4-4d12fe89b733'
            }
        )
        
        json_response = repsonse.json()
        self.assertEqual(json_response['result'], SuccessMessages.BLOCK_DELETED_SUCCESS)
    
    def test_delete_block_not_text(self):
        
        file_uuid = self.file.knowledge_source_uuid
        
        repsonse = self.client.delete(
            reverse('ChatBot:errors_headers'),
            data = {
                'file_uuid' : file_uuid,
                'block_id' : '1659959d-c277-4800-9570-e2fd2fc6940b'
            }
        )

        self.assertEqual(repsonse.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_delete_block_neagtive(self):
        
        file_uuid = self.file.knowledge_source_uuid
        
        repsonse = self.client.delete(
            reverse('ChatBot:errors_headers'),
            data = {
                'file_uuid' : file_uuid,
                'block_id' : str(uuid.uuid4())
            }
        )

        self.assertEqual(repsonse.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_headers(self):
        
        erro_uuid = self.error.error_uuid
        file_uuid = self.file.knowledge_source_uuid
        
        response = self.client.put(
            reverse('ChatBot:errors_headers'),
            data={
                'error_uuid' : erro_uuid,
                'file_uuid' : file_uuid,
                'blocks' : [
                    {
                        "block_type": "text",
                        "text_type":  "Body",
                        "content": "Clean with a metallic brush",
                        "block_id": "a4189b10-9d9e-4490-a43e-fdfc58513ce8",
                    },
                    {
                        "block_type": "text",
                        "text_type":  "H1",
                        "content": "Hit with a golden ball",
                        "block_id": "636c3c95-5700-4b1d-ac3b-ef4075d0c65c",
                    },
                    {
                        "block_type": "text",
                        "text_type":  "H3",
                        "content": "Fight with a brass rod",
                        "block_id": "6c055002-fa1c-4b7f-b9c3-0f0fe4d27bac",
                    }
                ]
            },
            format="json"
        )
        
        json_response= response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result'], SuccessMessages.HEADERS_UPDATED_SUCCESS)
    
    def test_update_headers_negative(self):
        
        erro_uuid = self.error.error_uuid
        file_uuid = str(uuid.uuid4())
        
        response = self.client.put(
            reverse('ChatBot:errors_headers'),
            data={
                'error_uuid' : erro_uuid,
                'file_uuid' : file_uuid,
                'blocks' : [
                    {
                        "block_type": "text",
                        "text_type":  "Body",
                        "content": "Clean with a metallic brush",
                        "block_id": "a4189b10-9d9e-4490-a43e-fdfc58513ce8",
                    },
                    {
                        "block_type": "text",
                        "text_type":  "H1",
                        "content": "Hit with a golden ball",
                        "block_id": "636c3c95-5700-4b1d-ac3b-ef4075d0c65c",
                    },
                    {
                        "block_type": "text",
                        "text_type":  "H3",
                        "content": "Fight with a brass rod",
                        "block_id": "6c055002-fa1c-4b7f-b9c3-0f0fe4d27bac",
                    }
                ]
            },
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)