import json
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from ChatBot.views.scheduler import ConversationScheduler, run_conversation_scheduler
from django.test import TestCase

class BaseWebSocketTestCase(TestCase):
    def setUp(self):
        self.scheduler = ConversationScheduler()


class TestConversationScheduler(BaseWebSocketTestCase):

    @patch('ChatBot.consumers.get_redis_connection')
    @patch('ChatBot.consumers.ChatConsumer')
    def test_save_conversation_if_threshold_exceeded_no_conversation_keys(self, mock_chat_consumer,mock_redis_client):
        mock_redis_instance = mock_redis_client.return_value

        self.scheduler.redis = mock_redis_instance
        mock_redis_instance.keys.return_value = []
        self.scheduler.save_conversation_if_threshold_exceeded()

        mock_redis_instance.keys.assert_called_once_with("conversation:*")
        mock_chat_consumer.assert_not_called()



    @patch('ChatBot.consumers.get_redis_connection')
    @patch('ChatBot.consumers.ChatConsumer')
    @patch('ChatBot.views.scheduler.datetime')
    def test_save_conversation_if_threshold_exceeded_within_threshold(self, mock_datetime, mock_chat_consumer, mock_redis_client):
        mock_redis_instance = mock_redis_client.return_value
        self.scheduler.redis = mock_redis_instance
        mock_redis_instance.keys.return_value = ["conversation:123"]
        mock_redis_instance.get.return_value = json.dumps({
            "message_details_json": [{"created_at": "2024-08-25T10:00:00Z"}]
        })

        mock_datetime.now.return_value = datetime(2024, 8, 25, 10, 5, tzinfo=timezone.utc)
        mock_datetime.timezone = timezone
        mock_datetime.timedelta = timedelta


        self.scheduler.save_conversation_if_threshold_exceeded()

        mock_redis_instance.keys.assert_called_once_with("conversation:*")
        mock_redis_instance.get.assert_called_once_with("conversation:123")
        mock_chat_consumer.assert_not_called()




    @patch('ChatBot.consumers.get_redis_connection')
    @patch('ChatBot.consumers.ChatConsumer.save_conversation_to_db')
    @patch('ChatBot.views.scheduler.datetime')
    def test_save_conversation_if_threshold_exceeded_exceeds_threshold(self, mock_datetime, mock_chat_consumer_save_to_db, mock_redis_client):
        mock_redis_instance = mock_redis_client.return_value
        self.scheduler.redis = mock_redis_instance

        mock_redis_instance.keys.return_value = ["conversation:123"]
        mock_redis_instance.get.return_value = json.dumps({
            "message_details_json": [{"created_at": "2024-08-25T10:00:00Z"}]
        })

        mock_datetime.now.return_value = datetime(2024, 8, 25, 10, 31, tzinfo=timezone.utc)
        mock_datetime.timezone = timezone
        mock_datetime.timedelta = timedelta
        mock_chat_consumer_save_to_db.return_value = None

        self.scheduler.save_conversation_if_threshold_exceeded()

        mock_redis_instance.keys.assert_called_once_with("conversation:*")
        mock_redis_instance.get.assert_called_once_with("conversation:123")
        mock_chat_consumer_save_to_db.assert_called_once_with("conversation:123")


    @patch('ChatBot.consumers.get_redis_connection')
    @patch('ChatBot.consumers.ChatConsumer')
    def test_save_conversation_if_threshold_exceeded_no_message_details(self, mock_chat_consumer,mock_redis_client):
        mock_redis_instance = mock_redis_client.return_value

        self.scheduler.redis = mock_redis_instance
        mock_redis_instance.keys.return_value = ["conversation:123"]
        mock_redis_instance.get.return_value = json.dumps({
            "message_details_json": []
        })
        self.scheduler.save_conversation_if_threshold_exceeded()

        mock_redis_instance.keys.assert_called_once_with("conversation:*")
        mock_redis_instance.get.assert_called_once_with("conversation:123")
        mock_chat_consumer.assert_not_called()



    #

    @patch('ChatBot.consumers.get_redis_connection')
    @patch('ChatBot.consumers.ChatConsumer')
    def test_save_conversation_if_threshold_exceeded_no_conversation_data(self, mock_chat_consumer, mock_redis_client):
        mock_redis_instance = mock_redis_client.return_value
        self.scheduler.redis = mock_redis_instance
        mock_redis_instance.keys.return_value = ["conversation:123"]
        mock_redis_instance.get.return_value = None

        self.scheduler.save_conversation_if_threshold_exceeded()

        mock_redis_instance.keys.assert_called_once_with("conversation:*")
        mock_redis_instance.get.assert_called_once_with("conversation:123")
        mock_chat_consumer.assert_not_called()


    @patch('ChatBot.consumers.get_redis_connection')
    @patch('ChatBot.consumers.ChatConsumer')
    def test_save_conversation_if_threshold_exceeded_redis_keys_exception(self, mock_chat_consumer_class, mock_redis_client):
        mock_redis_instance = mock_redis_client.return_value
        self.scheduler.redis = mock_redis_instance

        mock_redis_instance.keys.side_effect = Exception("Redis connection error")

        self.scheduler.save_conversation_if_threshold_exceeded()


        mock_chat_consumer_instance = mock_chat_consumer_class.return_value
        mock_chat_consumer_instance.save_conversation_to_db.assert_not_called()
