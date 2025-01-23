import inspect
import logging
from typing import Optional

from redis import RedisError
from rest_framework import status

from ChatBot.dao.interface.redis_dao_interface import IRedisDao
from ChatBot.utils import get_redis_connection
from ConnectedCustomerPlatform.exceptions import CustomException

logger = logging.getLogger(__name__)
class RedisDaoImpl(IRedisDao):
    """
        Service layer for handling redis logic such as fetching, storing etc.
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside {self.__class__.__name__} - Singleton Instance ID: {id(self)}")
            self.initialized = True


    def get_hash_field_value(self, key: str, field: str) -> Optional[str]:
        """Retrieves the value of a specified field for a given key."""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        if not key or not field:
            logger.error("Key and field must be provided. ")
            raise CustomException("Key and field must be provided ", status.HTTP_400_BAD_REQUEST)
        redis = get_redis_connection()
        value = redis.hget(key, field)
        if value is None:
            logger.warning(f"No value found for {field} under key {key}.")
        else:
            logger.info(f"Retrieved {field} for key {key}: {value}.")
        return value

    def get_data_by_key(self, key: str):
        """
            Method to fetch data by key
            Parameters:
                key (str): key to fetch data from redis.
            Returns:
                Json string: returns json string representation of data
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"fetching a specific data from redis with {key} key")
        try:
            redis_connection = get_redis_connection()
            return redis_connection.get(key)
        except RedisError as e:
            # Handle the case where the retries have failed and the Redis operation couldn't succeed
            logger.error(f"Failed to perform get Redis operation with {key} key: {str(e)}")
            raise e
