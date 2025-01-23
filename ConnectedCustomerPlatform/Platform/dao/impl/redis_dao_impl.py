import logging
from redis.exceptions import RedisError
import redis

from ChatBot.utils import get_redis_connection
from Platform.dao.interface.redis_dao_interface import IRedisDao

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

    def get_data_by_key(self, key: str):
        """
            Method to fetch data by key
            Parameters:
                key (str): key to fetch data from redis.
            Returns:
                Json string: returns json string representation of data
        """
        logger.info("In redis_dao_impl :: get_data_by_key")
        logger.debug(f"fetching a specific data from redis with {key} key")
        try:

            redis_connection = get_redis_connection()

            return redis_connection.get(key)
        except RedisError as e:
            # Handle the case where the retries have failed and the Redis operation couldn't succeed
            logger.error(f"Failed to perform get Redis operation with {key} key: {str(e)}")
            raise e
        except Exception as e:
            print(e)

    def set_data_by_key(self, key: str, data:str)->bool:
        """
            Method to set data by key
            Parameters:
                key (str): key to set data.
                data (Any) : data to set with key in redis
            Returns:
                - True: if the operation is successful.
                - False: if the operation fails
        """
        logger.info("In redis_dao_impl :: set_data_by_key")
        try:
            redis_connection = get_redis_connection()
            return redis_connection.set(key, data)
        except RedisError as e:
            # Handle the case where the retries have failed and the Redis operation couldn't succeed
            logger.error(f"Failed to perform set Redis operation for {key} key: {str(e)}")
            raise e

    def set_data_by_key_with_expiry(self, key: str, data:str,expiry:int)->bool:
        """
            Method to set data by key
            Parameters:
                key (str): key to set data.
                expiry (int): expiration time in seconds
                data (Any) : data to set with key in redis
            Returns:
                - True: if the operation is successful.
                - False: if the operation fails
        """
        logger.info("In redis_dao_impl :: set_data_by_key_with_expiry")
        logger.info(f"storing data in redis with {key} key")
        try:
            redis_connection = get_redis_connection()
            return redis_connection.setex(key,expiry, data)
        except RedisError as e:
            # Handle the case where the retries have failed and the Redis operation couldn't succeed
            logger.error(f"Failed to perform set Redis operation for {key} key: {str(e)}")
            raise

    def delete_data_by_key(self, key: str):
        """
            Method to delete data by key
            Parameters:
                key (str): key to delete data.
        """
        logger.info("In redis_dao_impl :: delete_data_by_key")
        try:
            redis_connection = get_redis_connection()
            return redis_connection.delete(key)
        except RedisError as e:
            # Handle the case where the retries have failed and the Redis operation couldn't succeed
            logger.error(f"Failed to perform set Redis operation for {key} key: {str(e)}")
            raise e