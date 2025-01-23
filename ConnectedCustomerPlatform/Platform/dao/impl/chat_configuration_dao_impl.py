import inspect
import logging
import uuid

from django.db import connection
from django.db.models import Q

from DatabaseApp.models import ChatConfiguration, ChatConfigurationCustomerApplicationMapping, Applications, Customers
from Platform.constant import constants

from Platform.dao.interface.chat_configuration_dao_interface import IChatConfigurationDao

logger = logging.getLogger(__name__)

class ChatConfigurationDAOImpl(IChatConfigurationDao):
    """
          Dao for Chat Configuration template, providing methods to add, edit,
          delete, and retrieve.
      """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(ChatConfigurationDAOImpl, cls).__new__(cls)
            logger.info("Creating a new instance of ChatConfigurationDAOImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the PromptDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside ChatConfigurationDAOImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_all_chat_configurations(self, application_uuid, customer_uuid, chat_configuration_type):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
           Retrieves all chat configurations for a given application and customer.
           This includes pre-created configurations (not yet mapped) with a NULL status, and already mapped configurations with their respective status.
           """
        with connection.cursor() as cursor:
            pre_created_query = f"""
                SELECT 
                    cc.chat_configuration_uuid, 
                    cc.chat_configuration_name,
                    cc.chat_configuration_type, 
                    cc.chat_details_json,
                    cc.is_default,
                    cc.pre_created,
                    NULL as status 
                FROM 
                    chat_configuration cc
                WHERE 
                    cc.pre_created = TRUE
                    AND cc.chat_configuration_type = %s
                    AND cc.chat_configuration_provider = %s
                    AND NOT EXISTS (
                        SELECT 1 
                        FROM chat_configuration_customer_application_mapping cccam 
                        WHERE cc.chat_configuration_uuid = cccam.chat_configuration_uuid
                        AND cccam.application_uuid = %s
                        AND cccam.customer_uuid = %s
                    )
                UNION ALL
                SELECT 
                    cc.chat_configuration_uuid, 
                    cc.chat_configuration_name,
                    cc.chat_configuration_type, 
                    cc.chat_details_json,
                    cc.is_default,
                    cc.pre_created,
                    cccam.status
                FROM 
                    chat_configuration cc
                JOIN 
                    chat_configuration_customer_application_mapping cccam 
                    ON cc.chat_configuration_uuid = cccam.chat_configuration_uuid
                WHERE 
                    cccam.application_uuid = %s
                    AND cccam.customer_uuid = %s
                    AND cc.chat_configuration_type = %s
                    AND cc.chat_configuration_provider = %s;
                    
            """
            params = [chat_configuration_type,constants.WEB, application_uuid, customer_uuid,
                      application_uuid, customer_uuid, chat_configuration_type,constants.WEB]
            cursor.execute(pre_created_query, params)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

        # Combine column names and row data into a list of dictionaries
        results = [dict(zip(column_names, row)) for row in rows]

        return results

    def get_configuration_by_uuid(self,chat_configuration_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return ChatConfiguration.objects.filter(chat_configuration_uuid=chat_configuration_uuid).first()

    def get_active_configurations(self, application_uuid, customer_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        configurations = ChatConfiguration.objects.filter(
            chatconfigurationcustomerapplicationmapping__application_uuid=application_uuid,
            chatconfigurationcustomerapplicationmapping__customer_uuid=customer_uuid,
            chatconfigurationcustomerapplicationmapping__status=True,
            chat_configuration_provider=constants.WEB

        ).values(
            'chat_details_json',
            'chat_configuration_type'
        )
        return configurations

    def get_default_template_by_type(self,chat_configuration_type):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return ChatConfiguration.objects.filter(is_default=True , chat_configuration_type = chat_configuration_type).values('chat_details_json').first()

    def create_configuration(self,data,application_uuid, customer_uuid, user_id,chat_configuration_data):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """Create a ChatConfiguration instance and mapping instance."""
        chat_configuration = ChatConfiguration(
            chat_configuration_uuid=str(uuid.uuid4()),
            chat_configuration_type=data.get('chat_configuration_type'),
            chat_configuration_provider=data.get('chat_configuration_provider'),
            chat_configuration_name = data.get('chat_configuration_name'),
            created_by=user_id,
            chat_details_json = chat_configuration_data,
            updated_by = user_id,
            description = data.get('description'),
            pre_created = data.get('pre_created', False),
            code = data.get('code')
        )
        chat_configuration.save()
        mapping_instance = ChatConfigurationCustomerApplicationMapping(
            mapping_uuid=str(uuid.uuid4()),
            chat_configuration_uuid=chat_configuration,
            application_uuid=Applications(application_uuid),
            customer_uuid=Customers(customer_uuid),
            status=False,
            created_by=user_id,
            updated_by= user_id
        )
        mapping_instance.save()
        return chat_configuration

    def update_configuration(self,instance):
        """Save the ChatConfiguration instance."""
        instance.save()

    def get_default_templates(self):
        return ChatConfiguration.objects.filter(is_default=True).values('chat_details_json')


    def delete_configuration_by_uuid(self,chat_configuration_uuid):
        return ChatConfiguration.objects.filter(pre_created = constants.FALSE , chat_configuration_uuid=chat_configuration_uuid).delete()


    def get_configuration_templates_and_name_count(self, application_uuid, customer_uuid, chat_configuration_type,
                                                   chat_configuration_name, chat_configuration_provider):
        queryset = ChatConfiguration.objects.filter(
            Q(chatconfigurationcustomerapplicationmapping__customer_uuid=customer_uuid,
              chatconfigurationcustomerapplicationmapping__application_uuid=application_uuid) |
            Q(pre_created=constants.TRUE),
            chat_configuration_type=chat_configuration_type,
            chat_configuration_provider=chat_configuration_provider
        ).distinct()

        configuration_count = queryset.count()
        name_count = queryset.filter(
            chat_configuration_name__iexact=chat_configuration_name).count()
        return configuration_count, name_count

