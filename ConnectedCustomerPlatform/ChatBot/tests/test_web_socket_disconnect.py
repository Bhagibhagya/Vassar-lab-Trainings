import json

from django.test import TestCase
from unittest.mock import patch, AsyncMock, MagicMock
from ChatBot.consumers import ChatConsumer


class BaseWebSocketTestCase(TestCase):
    def setUp(self):
        self.consumer = ChatConsumer()


class TestCaseWebSocketDisconnect(BaseWebSocketTestCase):
    @patch('ChatBot.views.user_info.UserInfoViewSet')
    async def test_disconnect_csr_true_server(self, mock_user_info_view_set):
        self.consumer.connection_uuid = "test_uuid"
        self.consumer.is_csr = "true"
        self.consumer.destination = "server"
        self.consumer.csr_id = "csr_id"
        mock_user_info_view_set.return_value.update_user = MagicMock()
        self.consumer.close = AsyncMock()
        self.consumer.discard_from_room = AsyncMock()
        await self.consumer.disconnect(close_code=None)
        mock_user_info_view_set.return_value.update_user.assert_called_once()
        self.consumer.close.assert_awaited_once()
        self.consumer.discard_from_room.assert_awaited_once()


    @patch('ChatBot.consumers.get_redis_connection')
    async def test_disconnect_csr_true_end_user(self,mock_redis_connection):
        mock_redis_instance = mock_redis_connection.return_value
        mock_redis_instance.get.return_value = json.dumps({
            "csr_info_json": [{"csr_uid": "csr_id", "status": "Active"}],
            "conversation_stats_json": [
                {
                    "startTime": "2024-08-02T12:00:00Z",
                    "endTime": "2024-08-02T12:05:00Z"
                }]
        })
        self.consumer.redis = mock_redis_instance
        self.consumer.connection_uuid = "test_uuid"
        self.consumer.is_csr = "true"
        self.consumer.destination = "endUser"
        self.consumer.csr_id = "csr_id"
        self.consumer.conversation_key = "conversation_key"
        self.consumer.close = AsyncMock()
        self.consumer.discard_from_room = AsyncMock()
        self.consumer.save_conversation_to_db = MagicMock()
        await self.consumer.disconnect(close_code=None)
        self.consumer.save_conversation_to_db.assert_called_once()
        self.consumer.close.assert_awaited_once()
        self.consumer.discard_from_room.assert_awaited_once()


    @patch('ChatBot.consumers.get_redis_connection')
    async def test_disconnect_csr_false(self, mock_redis_connection):
        # Mock Redis instance
        mock_redis_instance = mock_redis_connection.return_value
        mock_redis_instance.get.return_value = json.dumps({
            "conversation_stats_json": [
                {
                    "startTime": "2024-08-02T12:00:00Z",
                    "endTime": "2024-08-02T12:05:00Z"
                }]
        })
        self.consumer.redis = mock_redis_instance
        self.consumer.close = AsyncMock()
        self.consumer.discard_from_room = AsyncMock()
        self.consumer.connection_uuid = "test_uuid"
        self.consumer.is_csr = "false"
        self.consumer.conversation_key = "conversation_key"
        self.consumer.save_conversation_to_db = MagicMock()

        await self.consumer.disconnect(close_code=None)

        self.consumer.close.assert_awaited_once()
        self.consumer.discard_from_room.assert_awaited_once()