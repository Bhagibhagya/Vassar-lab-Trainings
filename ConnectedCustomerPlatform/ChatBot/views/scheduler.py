import json
from datetime import timezone
from datetime import datetime, timedelta
from ChatBot.constant.constants import Constants
from ChatBot.consumers import ChatConsumer
from ChatBot.services.impl.conversation_service_impl import ConversationServiceImpl
import redis
from dateutil import parser
from django.conf import settings

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)

class ConversationScheduler:
    def __init__(self):
        self.redis = redis_client

    def save_conversation_if_threshold_exceeded(self):
        print("ConversationScheduler :: save_conversation_if_threshold_exceeded() 1")
        try:
            print("Entering save_conversation_if_threshold_exceeded")
            conversation_keys = self.redis.keys("conversation:*")
            if not conversation_keys:
                print("No conversation data to process")
                return


            now = datetime.now(timezone.utc)
            for conversation_key in conversation_keys:
                # Retrieve conversation data from Redis
                print(f"Processing conversation key: {conversation_key}")
                conversation_data = self.redis.get(conversation_key)
                if conversation_data:
                    conversation_data = json.loads(conversation_data)
                    message_details = conversation_data.get("message_details_json", [])

                    if message_details:
                        latest_message = message_details[-1]
                        created_at_str = latest_message['created_at']
                        created_at = parser.isoparse(created_at_str)
                    else:
                        created_at = None
                else:
                    continue


                threshold = timedelta(minutes=Constants.CACHE_THRESHOLD)
                if created_at and now - created_at > threshold:
                    print(f"Saving conversation key: {conversation_key} to DB")
                    consumer_instance = ChatConsumer()
                    print(consumer_instance)
                    consumer_instance.save_conversation_to_db(conversation_key)

        except Exception as e:
            print(f"An error occurred while checking or saving conversations: {e}")


def run_conversation_scheduler():
    conversation_service_impl = ConversationServiceImpl()
    conversation_service_impl.process_conversations()