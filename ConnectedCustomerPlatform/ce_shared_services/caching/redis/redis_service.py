import logging
import traceback
import redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    TimeoutError
)
from redis.client import Redis
from typing import Any
from ce_shared_services.caching.interface.caching import ICaching
from ce_shared_services.configuration_models.configuration_models import RedisConfig
from ce_shared_services.exceptions.exceptions import CachingException

logger = logging.getLogger(__name__)


class RedisService(ICaching):
    """
    Shared Redis service for managing connections and common Redis operations.
    """

    def __init__(self, config: RedisConfig):
        """
        Initialize the Redis connection.

        Args:
            config (RedisConfig): The Redis configuration model.
        """
        self._config = config
        self._retry_strategy = Retry(
            backoff=ExponentialBackoff(),
            retries=self._config.max_retries,
            supported_errors=(ConnectionError, TimeoutError, BusyLoadingError),
        )
        self._redis_client: Redis = self._initialize_client()

    def _initialize_client(self) -> Redis:
        """
        Initialize the Redis client using a connection pool.
        """
        pool = redis.ConnectionPool(
            host=self._config.host,
            port=self._config.port,
            db=self._config.db,
            password=self._config.password,
            decode_responses=self._config.decode_responses,
            max_connections=self._config.connection_pool_size,
            retry=self._retry_strategy,
        )

        return redis.Redis(connection_pool=pool)

    def get(self, key: str) -> Any:
        """
        Get the value of a key from Redis.
        """
        try:
            return self._redis_client.get(key)
        except Exception as e:
            logger.error(f"Error in 'get' method for key: {key}")
            logger.error(traceback.format_exc())
            raise CachingException(*e.args)

    def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        """
        Set a value in Redis.
        """
        try:
            return bool(self._redis_client.set(key, value, ex=expire))
        except Exception as e:
            logger.error(f"Error in 'set' method for key: {key}, expire: {expire}")
            logger.error(traceback.format_exc())
            raise CachingException(*e.args)

    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        """
        try:
            return bool(self._redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error in 'delete' method for key: {key}")
            logger.error(traceback.format_exc())
            raise CachingException(*e.args)

    # Additional Redis operations can be added here (e.g., incr, decr, hmset, etc.)
