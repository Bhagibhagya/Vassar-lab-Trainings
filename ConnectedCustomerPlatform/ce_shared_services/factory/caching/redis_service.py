import logging

from ce_shared_services.caching.redis.redis_service import RedisService, RedisConfig
from ce_shared_services.caching.interface.caching import ICaching

from ce_shared_services.factory.scope.singleton import Singleton

logger = logging.getLogger(__name__)

class CachingFactory(Singleton):
    CLASSNAME_CLASS_MAP = {
        RedisService.__name__: RedisService
    }

    @classmethod
    def instantiate(cls, class_name: str, redis_config: RedisConfig) -> ICaching:
        """
        Instantiate a caching service class.

        This method is responsible for instantiating and caching instances of the requested
        caching service class (e.g., RedisService). It ensures that only one instance of the
        requested class exists for a given `redis_config`. If no existing instance is found,
        a new one is created and stored.

        Parameters:
            class_name (str): The name of the caching service class to instantiate.
                             Must be a key in the `CLASSNAME_CLASS_MAP`.
            redis_config (RedisConfig): Configuration object for the caching service.

        Returns:
            ICaching: An instantiated object of the requested caching service class.

        Raises:
            ValueError: If `CLASSNAME_CLASS_MAP` is empty or the `class_name` is not defined
                        in the map.
            Exception: If the instantiation of the requested class fails for any reason.
        """

        if not cls.CLASSNAME_CLASS_MAP:
            logger.error("CLASSNAME_CLASS_MAP must be defined by sub-classes.")
            raise ValueError("CLASSNAME_CLASS_MAP must be defined by sub-classes.")

        if class_name not in cls.CLASSNAME_CLASS_MAP:
            logger.error(f"class_name :: {class_name} not available for instantiation.")
            raise ValueError(f"class_name :: {class_name} not available for instantiation.")


        if class_name not in cls._instances:
            cls._instances[class_name] = {}

        with cls._lock:

            if redis_config in cls._instances[class_name]:
                return cls._instances[class_name][redis_config]

            else:

                try:
                    instance = cls.CLASSNAME_CLASS_MAP[class_name](redis_config)
                    cls._instances[class_name][redis_config] = instance
                    return instance

                except Exception as exception:

                    logger.error(str(exception))
                    raise exception
