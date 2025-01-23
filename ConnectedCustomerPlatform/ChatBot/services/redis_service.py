import json
import logging

from ChatBot.utils import get_redis_connection

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.redis = get_redis_connection()

    def check_if_redis_contains_data_by_conversation_key(self, conversation_key: str):
        """
            Method to check if conversation_data exist by conversation_key or not in redis
            Parameters:
                conversation_key (str): key to check conversation_data. format : "conversation:{conversation_uuid}"
            Returns:
                - 1 (True) : if conversation data exist
                - 0 (False) : if conversation data doesn't exist
        """
        logger.info("redis_service.py :: :: :: RedisService :: :: :: check_if_redis_contains_data_by_conversation_key")
        logger.info(f"conversation_key :: {conversation_key}")
        return self.redis.exists(conversation_key)

    def get_conversation_data_by_conversation_key(self, conversation_key: str):
        """
                    Method to fetch conversation data by conversation_key
                    Parameters:
                        conversation_key (str): key to fetch conversation_data. format : "conversation:{conversation_uuid}"
                    Returns:
                        Json_Dump: returns string representation of json/dict
                """
        # logger.info("redis_service.py :: :: :: RedisService :: :: :: get_conversation_data_by_conversation_key")
        # logger.info(f"conversation_key :: {conversation_key}")
        return self.redis.get(conversation_key)

    def set_conversation_data_in_redis(self, conversation_key: str, conversation_data):
        """
                            Method to set conversation data by conversation_key
                            Parameters:
                                conversation_key (str): key to set conversation_data. format : "conversation:{conversation_uuid}"
                                conversation_data : data to set with conversation_key in redis
                            Returns:
                                - True: if the operation is successful.
                                - False: if the operation fails
        """
        logger.info("redis_service.py :: :: :: RedisService :: :: :: set_conversation_data_in_redis")
        logger.info(f"conversation_key :: {conversation_key}\nconversation_data :: {conversation_data}")
        if isinstance(conversation_data, dict):
            conversation_data = json.dumps(conversation_data)
        set_status = self.redis.set(conversation_key, conversation_data)
        return set_status

    def get_all_redis_keys(self, pattern: str):
        """
                Method is used to retrieve all keys in the Redis database that match a given pattern.
                Parameters:
                    pattern (str): patter to fetch keys that matches
                Returns:
                    List of keys
        """
        logger.info("redis_service.py :: :: :: RedisService :: :: :: get_all_redis_conversation_keys")
        keys_list = self.redis.keys(pattern)
        return keys_list

    def get_all_conversation_data(self, conversation_keys: list):
        """
                        Method is used to retrieve all conversation_data using conversation_keys
                        Parameters:
                            conversation_keys (list): list of conversation keys in redis
                        Returns:
                            List of conversation_data objects
                """
        logger.info("redis_service.py :: :: :: RedisService :: :: :: get_all_conversation_data")
        conversation_data = self.redis.mget(conversation_keys)
        return conversation_data
