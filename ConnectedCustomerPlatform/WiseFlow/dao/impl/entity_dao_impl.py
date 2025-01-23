import logging
import uuid
import inspect
from django.db.models import F, Q

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException
from DatabaseApp.models import WiseflowEntity, Applications, Customers
from WiseFlow.constants.error_messages import EntityErrorMessages
from WiseFlow.dao.interface.entity_dao_interface import IEntityDaoInterface

logger=logging.getLogger(__name__)
class EntityDaoImpl(IEntityDaoInterface):

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(EntityDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of EntityDaoImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the EntityDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside EntityDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_entity_details(self,entity_uuid:str):
        """Returns of entity (system or custom)"""
        details=WiseflowEntity.objects.filter(entity_uuid=entity_uuid).values_list('entity_name','ownership','instructions','description','output_format').first()
        if details is None:
            logger.error(f"Entity with entity uuid {entity_uuid} does not exist")
            raise InvalidValueProvidedException(EntityErrorMessages.ENTITY_NOT_FOUND.format(entity_uuid=entity_uuid))
        return details

    def create_wiseflow_entity(self, entity_uuid, entity_name, description, parent_entity_uuid, output_format, instructions, ownership, application_uuid, customer_uuid, user_uuid):
        """
            create an entity in database
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        wiseflow_entity = WiseflowEntity.objects.create(
            entity_uuid=entity_uuid,
            entity_name=entity_name,
            description=description,
            parent_entity_uuid=WiseflowEntity(parent_entity_uuid),
            output_format=output_format,
            instructions=instructions,
            ownership=ownership,
            application_uuid=Applications(application_uuid),
            customer_uuid=Customers(customer_uuid),
            created_by=user_uuid
        )
        return wiseflow_entity

    def get_wiseflow_entities_by_customer_and_application(self, customer_uuid, application_uuid, ownership=None):
        """ get all entities under customer and application """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        filters = Q(customer_uuid=customer_uuid, application_uuid=application_uuid)
        if ownership:
            filters &= Q(ownership=ownership)

        return self.__helper_function_to_fetch_entities(filters=filters)

    def get_entity_by_entity_uuid(self, entity_uuid):
        """ fetch a particular entity """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        filters = Q(entity_uuid=entity_uuid)
        return self.__helper_function_to_fetch_entities(filters)

    def __helper_function_to_fetch_entities(self, filters: Q):
        """ helper function to fetch entities by filter """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        filtered_entities = WiseflowEntity.objects.filter(
            filters
        ).select_related('parent_entity_uuid'
        ).annotate(
            parent_entity_name=F('parent_entity_uuid__entity_name')
        ).order_by('-created_at'
        ).values(
            'entity_uuid',
            'entity_name',
            'description',
            'parent_entity_name',
            'parent_entity_uuid',
            'output_format',
            'instructions',
            'ownership',
            'application_uuid',
            'customer_uuid',
            'is_deleted',
            'status',
            'created_at',
        )

        return filtered_entities

    def delete_entity_by_customer_and_application(self,customer_uuid, application_uuid, entity_uuid):
        """ deletes an entity """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return WiseflowEntity.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            entity_uuid=entity_uuid,
        ).delete()

    def is_system_entity(self, entity_uuid):
        """check whether a entity is system entity or not"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Check if the record exists with SYSTEM ownership
        is_system_entity = WiseflowEntity.objects.filter(
            entity_uuid=entity_uuid,
            ownership=WiseflowEntity.OwnershipEnum.SYSTEM
        ).exists()

        return is_system_entity

    def get_entity_by_uuid(self, entity_uuid):
        """ get an entity by entity_uuid"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return WiseflowEntity.objects.filter(entity_uuid=entity_uuid).first()

    def save_entity(self, entity_instance):
        """update the entity"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"saving entity with entity_uuid:: {entity_instance.entity_uuid}")
        entity_instance.save()

    def fetch_parent_entities(self, ownership):
        """ fetch parent entities by ownership """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return WiseflowEntity.objects.filter(parent_entity_uuid=None, ownership=ownership).values('entity_uuid','entity_name','status')

    def is_valid_parent_entity(self, entity_uuid):
        """ check whether entity is parent entity or not """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # check whether the entity is parent entity or not. entity is parent entity if parent_entity_uuid is none and ownership = "CUSTOM"
        is_parent_entity = WiseflowEntity.objects.filter(
            entity_uuid=entity_uuid,
            parent_entity_uuid__isnull=True,
            ownership=WiseflowEntity.OwnershipEnum.CUSTOM
        ).exists()
        return is_parent_entity
