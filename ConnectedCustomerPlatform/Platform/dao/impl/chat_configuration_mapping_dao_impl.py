import inspect
import logging
import uuid

from django.db.models import Q

from DatabaseApp.models import ChatConfigurationCustomerApplicationMapping, Applications, Customers
from Platform.dao.interface.chat_configuration_mapping_dao_interface import IChatConfigurationMappingDAO

logger = logging.getLogger(__name__)

class ChatConfigurationMappingDAOImpl(IChatConfigurationMappingDAO):
    """
            Dao for Chat ConfigurationMapping template, providing methods to add, edit,
            delete, and retrieve.
        """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(ChatConfigurationMappingDAOImpl, cls).__new__(cls)
            logger.info("Creating a new instance of ChatConfigurationMappingDAOImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the PromptDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside ChatConfigurationMappingDAOImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_or_create_mapping_by_publishing(self, chat_configuration_instance, application_uuid, customer_uuid, user_id):
        """Get or create a ChatConfigurationCustomerApplicationMapping"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return ChatConfigurationCustomerApplicationMapping.objects.get_or_create(
            chat_configuration_uuid=chat_configuration_instance,
            application_uuid=Applications(application_uuid),
            customer_uuid=Customers(customer_uuid),
            defaults={
                'mapping_uuid': str(uuid.uuid4()),
                'status': True,
                'created_by': user_id,
                'updated_by': user_id
            }
        )

    def update_mapping_status(self,mapping, status, user_id):
        """Update the status of a specific mapping"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        mapping.status = status
        mapping.updated_by = user_id
        mapping.save()

    def deactivate_other_configurations(self,application_uuid, customer_uuid, chat_configuration_type,exclude_uuid,user_id):
        """Deactivate all configurations in ChatConfigurationCustomerApplicationMapping
         except the one published"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        ChatConfigurationCustomerApplicationMapping.objects.filter(
            Q(application_uuid=application_uuid) &
            Q(customer_uuid=customer_uuid) &
            Q(chat_configuration_uuid__chat_configuration_type=chat_configuration_type) &
            ~Q(chat_configuration_uuid=exclude_uuid)
        ).update(status=False,updated_by = user_id)

    def check_mapping_exists(self,chat_configuration_uuid, customer_uuid, application_uuid):
        """
        Check if a mapping exists between the given chat_configuration_uuid, customer_uuid, and application_uuid.
        """
        return ChatConfigurationCustomerApplicationMapping.objects.filter(
            chat_configuration_uuid=chat_configuration_uuid,
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
        ).exists()