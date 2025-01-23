import logging


from ce_shared_services.factory.scope.singleton import Singleton

from ce_shared_services.event_handlers.impl.intent_classification_event_handler import \
    IntentClassificationEventHandler

from ce_shared_services.event_handlers.interface.event_handler import IEventHandler

from ce_shared_services.configuration_models.configuration_models import IntentClassificationConfig

logger = logging.getLogger(__name__)


class IntentClassificationEventHandlerFactory(Singleton):
    CLASSNAME_CLASS_MAP = {
        IntentClassificationEventHandler.__name__: IntentClassificationEventHandler
    }
    @classmethod
    def instantiate(cls, class_name: str, intent_classification_config: IntentClassificationConfig) -> IEventHandler:
        """
    Instantiate or retrieve a singleton instance of an Intent Classification Event Handler class.

    This method ensures that only one instance of a given class is created per unique configuration.
    It checks if an instance with the specified class name and configuration already exists. If not,
    it creates a new instance using the `CLASSNAME_CLASS_MAP`, which maps class names to their respective
    class implementations.

    Args:
        class_name (str): The name of the class to instantiate.
        intent_classification_config (IntentClassificationConfig): The configuration object containing
            the necessary settings for intent classification.


    Returns:
        IEventHandler: A singleton instance of the specified class.

    Raises:
        ValueError: If the specified class name is not found in `CLASSNAME_CLASS_MAP`.
        ValueError: If `CLASSNAME_CLASS_MAP` is not defined by the subclass.
        Exception: If instantiation of the class fails for any other reason.
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

            if intent_classification_config in cls._instances[class_name]:
                return cls._instances[class_name][intent_classification_config]

            else:

                try:
                    instance = cls.CLASSNAME_CLASS_MAP[class_name](intent_classification_config)
                    cls._instances[class_name][intent_classification_config] = instance
                    return instance

                except Exception as exception:

                    logger.error(str(exception))
                    raise exception