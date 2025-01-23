import json

import channels
import pytest
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from ChatBot.consumers import ChatConsumer
from unittest.mock import patch, AsyncMock
from ChatBot.tests.test_data import create_conversation_test_data
from django.urls import path

from asgiref.sync import sync_to_async

from DBServices.models import Conversations

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path("ws/chatbot/", ChatConsumer.as_asgi(), name="chatbot"),
    ]),
})

class BaseWebSocketTestCase(TestCase):
    async def get_communicator(self, query_string):
        return WebsocketCommunicator(application, f"/ws/chatbot/?{query_string}")

    async def connect_communicator(self, communicator):
        connected, subprotocol = await communicator.connect()
        return connected


class TestWebSocketCaseConnect(BaseWebSocketTestCase):

# CSR Login
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_csr_connection_to_server(self, mock_redis_connection):
        mock_redis_instance = mock_redis_connection.return_value
        mock_redis_instance.get.return_value = None
        query_string = "is_csr=true&destination=server&csr_id=49fa8519-bce7-4e1a-98f2-713945c5b25c"
        communicator = await self.get_communicator(query_string)
        connected = await self.connect_communicator(communicator)
        assert connected


#CSR and Enduser
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_csr_connection_to_end_user(self, mock_redis_connection):
        mock_redis_instance = mock_redis_connection.return_value
        mock_redis_instance.get.return_value = None

        query_string = "is_csr=true&destination=endUser&conversation_uuid=537bc206-fe76-4d7b-92d7-68e0b0a9a40d"
        communicator = await self.get_communicator(query_string)
        connected = await self.connect_communicator(communicator)

        assert connected
        mock_redis_instance.reset_mock()

#Bot and existing User details in cache
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_existing_conversation_in_cache(self,mock_get_redis_connection):
        mock_redis_instance = mock_get_redis_connection.return_value
        print(mock_redis_instance)
        mock_data = {
            "conversation_uuid": "conversation_uuid_test",
            "name": "",
            "user_details_json": {"name": "Anonymous", "userType": "NON_AUTHENTICATED"},
            "csr_info_json": [],
            "csr_hand_off": False,
            "conversation_stats_json": {"conversationStartTime": "2024-07-11T07:41:45.161684"},
            "conversation_feedback_transaction_json": {},
            "task_details_json": {},
            "conversation_status": "CSR_ONGOING",
            "summary": "Conversation initiated",
            "application_uuid": "c83ca3fb-0ac7-4a0e-a03e-92be37d6c2b9",
            "customer_uuid": "2f2c9e13-943f-4cb2-b1fb-8b0c2ff3db24",
            "message_details_json": [{
                "id": "02df0843-e8cb-42b3-8b82-ee909ff98a54",
                "csr_id": None,
                "source": "bot",
                "message_marker": "LOGGED",
                "dimension_action_json": {},
                "message_text": "Hello, what can I help you with today?",
                "media_url": None,
                "parent_message_uuid": None,
                "created_at": "2024-07-11T07:41:45.162914+00:00"
            }],
            "insert_ts": "2024-07-11T07:41:45.161703+00:00"
        }

        # Convert mock_data to JSON string
        mock_data_json = json.dumps(mock_data)

        # Mocking Redis set and get methods

        mock_redis_instance.get.return_value = mock_data_json

        # Mock the query string and related method calls
        query_string = "is_csr=false&conversation_uuid=conversation_uuid_test"

        communicator = await self.get_communicator(query_string)
        connected = await self.connect_communicator(communicator)

        self.assertTrue(connected)

        mock_redis_instance.get.assert_called_once_with("conversation:conversation_uuid_test")
        mock_redis_instance.reset_mock()

#Ongoing CSR and User
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_csr_connection_data_in_db_status_csr_ongoing(self, mock_redis_connection):
        with  patch('ChatBot.consumers.ChatConsumer.get_conversation_from_db') as mock_get_conversation_from_db:
            mock_redis_instance = mock_redis_connection.return_value
            mock_redis_instance.get.return_value = None
            mock_redis_instance.set.return_value = None


            mock_get_conversation_from_db.return_value = await sync_to_async(create_conversation_test_data)()

            query_string = "is_csr=false&conversation_uuid=conversation_uuid"

            communicator = await self.get_communicator(query_string)
            connected = await self.connect_communicator(communicator)
            assert connected
            mock_redis_instance.reset_mock()


#Bot and User when status is Resolved
    @patch('ChatBot.consumers.ChatConsumer.send_reply')
    @patch('ChatBot.consumers.ChatConsumer.create_new_conversation')
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_csr_connection_data_in_db_status_resolved(self, mock_redis_connection ,mock_create_new_conversation ,mock_send_reply):
        with  patch('ChatBot.consumers.ChatConsumer.get_conversation_from_db') as mock_get_conversation_from_db:
            mock_redis_instance = mock_redis_connection.return_value
            mock_redis_instance.get.return_value = None
            mock_redis_instance.set.return_value = None

            conversation_data = None
            mock_get_conversation_from_db.return_value = conversation_data

            query_string = "is_csr=false&conversation_uuid=conversation_uuid"
            communicator = await self.get_communicator(query_string)
            connected = await self.connect_communicator(communicator)
            assert connected
            mock_create_new_conversation.assert_called_once()
            mock_send_reply.assert_called_once()
            mock_redis_instance.reset_mock()


#Conversation Dosenot exist but given in Params
    @patch('ChatBot.consumers.ChatConsumer.send_reply')
    @patch('ChatBot.consumers.ChatConsumer.create_new_conversation')
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_conversation_doesnot_exist(self, mock_redis_connection,mock_create_new_conversation,mock_send_reply):
        with  patch('ChatBot.consumers.ChatConsumer.get_conversation_from_db') as mock_get_conversation_from_db:
            mock_redis_instance = mock_redis_connection.return_value
            mock_redis_instance.get.return_value = None
            mock_redis_instance.set.return_value = None

            # mock_get_conversation_from_db.return_value = self.create_test_data()
            mock_get_conversation_from_db.side_effect = Conversations.DoesNotExist

            query_string = "is_csr=false&conversation_uuid=conversation_uuid"

            communicator = await self.get_communicator(query_string)
            connected = await self.connect_communicator(communicator)
            assert connected
            mock_create_new_conversation.assert_called_once()
            mock_send_reply.assert_called_once()
            mock_redis_instance.reset_mock()

# New conversation between User and Bot
    @patch('ChatBot.consumers.ChatConsumer.add_to_room')
    @patch('ChatBot.consumers.ChatConsumer.send_reply')
    @patch('ChatBot.consumers.ChatConsumer.create_new_conversation')
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_connection_with_no_params(self, mock_redis_connection, mock_create_new_conversation,
                                             mock_send_reply,mock_add_to_room):
        mock_redis_instance = mock_redis_connection.return_value
        mock_redis_instance.get.return_value = None
        mock_redis_instance.set.return_value = None
        mock_add_to_room.return_value = None
        query_string = ""

        communicator = await self.get_communicator(query_string)
        connected = await self.connect_communicator(communicator)
        assert connected
        mock_create_new_conversation.assert_called_once()
        mock_send_reply.assert_called_once()
        mock_redis_instance.reset_mock()















