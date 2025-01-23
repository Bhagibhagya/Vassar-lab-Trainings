import json

from django.test import TestCase
from unittest.mock import patch, AsyncMock, MagicMock
from ChatBot.consumers import ChatConsumer


class BaseWebSocketTestCase(TestCase):
    def setUp(self):
        self.consumer = ChatConsumer()
        self.consumer.is_csr = "true"
        self.consumer.destination = "endUser"

        self.data = {
            'message': "{\"id\":\"msg_id\",\"csr_id\":null,\"source\":\"user\",\"message_marker\":\"LOGGED\",\"dimension_action_json\":{},\"message_text\":\"ooh\",\"media_url\":null,\"parent_message_uuid\":null,\"created_at\":1717659193133}"
        }
        self.delivery_marker = {
            'deliveryMarker': "{\"id\":\"3919631c-971f-41ae-8d71-fd125dad29d6\",\"marker_status\":\"READ\"}"
        }
        self.typing_indicator = {
            'typingIndicator': "{\"typing\":true,\"created_at\":\"Fri, 09 Aug 2024 09:01:58 GMT\"}"
        }

        self.mock_service = MagicMock()
        self.customer_uuid = "customer_uuid"
        self.application_uuid = "application_uuid"
        self.connection_uuid = "connection_uuid"
        self.channel_name = "channel_name"
        self.conversation_key = "conversation_key"



class TestCaseWebSocketReceive(BaseWebSocketTestCase):
    @patch('ChatBot.consumers.get_redis_connection')
    async def test_receive_json_user_info(self,mock_redis_connection):
        mock_redis_instance = mock_redis_connection.return_value
        # Setting up the mock data
        mock_data = {
            "user_info": {
                "name": "John Doe"
            }
        }
        mock_conversation_data = json.dumps({
            "user_details_json": {}
        })
        self.consumer.redis = mock_redis_instance
        mock_redis_instance.get.return_value = mock_conversation_data
        await self.consumer.receive_json(mock_data)
        mock_redis_instance.set.assert_called_once()


    #
    async def test_receive_json_is_csr_true(self):
        self.consumer.connection_uuid = "test_uuid"
        self.consumer.fetch_conversation_status = MagicMock(return_value="CSR_ONGOING")
        self.consumer.store_message_in_cache = AsyncMock()
        self.consumer.send_to_room = AsyncMock()

        await self.consumer.receive_json(self.data)

        self.consumer.fetch_conversation_status.assert_called_once()
        self.consumer.store_message_in_cache.assert_awaited_once()
        self.consumer.send_to_room.assert_awaited_once()


    @patch('ChatBot.consumers.get_redis_connection')
    async def test_receive_json_with_delivery_marker(self,mock_redis_connection):
        mock_redis_instance = mock_redis_connection.return_value
        self.consumer.redis = mock_redis_instance
        mock_redis_instance.get.return_value = None
        self.consumer.connection_uuid = "test_uuid"
        self.consumer.update_marker_status = MagicMock()

        await self.consumer.receive_json(self.delivery_marker)

        self.consumer.update_marker_status.assert_called_once()

    @patch('ChatBot.consumers.ChatConsumer.send_to_room')
    async def test_receive_json_with_typing_indicator_csr(self,mock_send_to_room):
        mock_send_to_room.return_value = None
        await self.consumer.receive_json(self.typing_indicator)


    @patch('ChatBot.consumers.get_redis_connection')
    @patch('ChatBot.consumers.ChatConsumer.send_to_room')
    async def test_receive_json_with_typing_indicator_no_csr(self, mock_send_to_room,mock_redis_connection):
        mock_redis_instance = mock_redis_connection.return_value
        self.consumer.redis = mock_redis_instance
        mock_data = {
            "conversation_status": "CSR_ONGOING"}

        mock_redis_instance.get.return_value = json.dumps(mock_data)
        mock_send_to_room.return_value = None
        self.consumer.is_csr = "false"
        await self.consumer.receive_json(self.typing_indicator)

