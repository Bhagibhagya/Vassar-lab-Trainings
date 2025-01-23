from uuid import uuid4
import requests

from rest_framework import status
import unittest
from unittest import TestCase
    
    
class RelevantChunksTestCase(TestCase):
    
    def test_get_relevant_chunks_one(self):
        
        c = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
        a = '5d2b2a38-c3db-4033-9402-23dc3e901601'
        
        headers = {
            'customer-uuid' : c,
            'application-uuid' : a,
            'user-uuid' : str(uuid4())
        }
        
        n = 10
        json = {
            'top_n' : n,
            'query' : 'What is the leave policy?',
            'entity_filter' : {
                'default' : {
                }
            }
        }
        
        url = 'http://localhost:9000/api/chatbot/sme/chunks'
        
        response = requests.post(url, json=json, headers=headers)
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        chunks = json_response['result']
        self.assertEqual(len(chunks), n)
        
        for chunk in chunks:
            
            self.assertIsInstance(chunk, dict)
            self.assertListEqual(sorted(list(chunk.keys())), ['document', 'id', 'metadata'])

    def test_get_relevant_chunks_two(self):
        
        c = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
        a = '5d2b2a38-c3db-4033-9402-23dc3e901601'
        
        headers = {
            'customer-uuid' : c,
            'application-uuid' : a,
            'user-uuid' : str(uuid4())
        }
        
        n = 15
        json = {
            'top_n' : n,
            'query' : 'What is the leave policy?',
            'entity_filter' : {
                'default' : {
                    'default' : 'default'
                }
            }
        }
        
        url = 'http://localhost:9000/api/chatbot/sme/chunks'
        
        response = requests.post(url, json=json, headers=headers)
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        chunks = json_response['result']
        self.assertEqual(len(chunks), n)
        
        for chunk in chunks:
            
            self.assertIsInstance(chunk, dict)
            self.assertListEqual(sorted(list(chunk.keys())), ['document', 'id', 'metadata'])  
              
    def test_get_relevant_chunks_three(self):
        
        c = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
        a = '5d2b2a38-c3db-4033-9402-23dc3e901601'
        
        headers = {
            'customer-uuid' : c,
            'application-uuid' : a,
            'user-uuid' : str(uuid4())
        }
        
        n = 8
        json = {
            'top_n' : n,
            'query' : 'What is the leave policy?',
            'entity_filter' : None
        }
        
        url = 'http://localhost:9000/api/chatbot/sme/chunks'
        
        response = requests.post(url, json=json, headers=headers)
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        chunks = json_response['result']
        self.assertEqual(len(chunks), n)
        
        for chunk in chunks:
            
            self.assertIsInstance(chunk, dict)
            self.assertListEqual(sorted(list(chunk.keys())), ['document', 'id', 'metadata'])    
            
    def test_get_relevant_chunks_negative(self):
        
        c = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
        a = '5d2b2a38-c3db-4033-9402-23dc3e901601'
        
        headers = {
            'customer-uuid' : c,
            'application-uuid' : a,
            'user-uuid' : str(uuid4())
        }
        
        n = 10
        json = {
            'top_n' : n,
            'query' : 'What is the leave policy?',
        }
        
        url = 'http://localhost:9000/api/chatbot/sme/chunks'
        
        response = requests.post(url, json=json, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            

if __name__ == '__main__':
    
    unittest.main()