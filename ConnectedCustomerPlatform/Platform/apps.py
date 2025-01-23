import logging
from django.apps import AppConfig

# Configure logger for the app
logger = logging.getLogger(__name__)

class PlatformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Platform'


class ClassInitializationConfig(AppConfig):
    """
    Configuration class for the Platform application.

    This class initializes singleton instances of key components in the application
    (ViewSet, Service, and DAO) when the application is ready, ensuring that only
    one instance of each is created for efficient resource management.
    """
    name = 'Platform'
    instance_store = {}
    initialized = False

    def ready(self):
        """
        Initializes instances of key components when the application is ready.

        This method is called when the application registry is fully populated.
        It creates one instance each of LLMConfigurationViewSet, LLMConfigurationService,
        and LLMConfigurationDAO, storing them in the instance_store dictionary.
        """
        if not self.initialized:
            # Import required classes only when the app is ready
            from Platform.views.llm_configuration import LLMConfigurationViewSet

            # Store one instance of each class
            self.instance_store = {
                'LLMConfigurationViewSet': LLMConfigurationViewSet()
            }

            # Log instance IDs for debugging
            logger.debug("Initialized instances in ClassInitializationConfig:")
            for class_name, instance in self.instance_store.items():
                logger.debug(f"{class_name} Instance ID: {id(instance)}")

            # Mark as initialized to prevent further instance creation
            self.initialized = True
            logger.info("ClassInitializationConfig instances created successfully.")
