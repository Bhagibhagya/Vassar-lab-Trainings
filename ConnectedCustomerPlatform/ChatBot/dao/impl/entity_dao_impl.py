import logging

from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.dao.interface.entity_dao_interface import IEntityDao
from ChatBot.dataclasses.entity_data import Entity, AttributeDetailsJson
from DatabaseApp.models import Entities, KnowledgeSources
from ChatBot.constant.constants import EntityConstants
from uuid import uuid4
from ChatBot.constant.constants import TestEntityConstants
from django.db.models.expressions import RawSQL
from django.db import models
from rest_framework import status
from django.db.models import F, Count, Prefetch

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EntityDaoImpl(IEntityDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EntityDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.initialized = True

    def create_entity(self, entity: Entity, user_uuid):
        """Create a new entity in the database."""
        logger.debug(f"Creating entity: {entity.entity_name} for user: {user_uuid}")

        if Entities.objects.filter(
            application_uuid = entity.application_uuid,
            customer_uuid = entity.customer_uuid,
            entity_name__iexact=entity.entity_name
        ).exists():
            
            logger.error(f"Entity with name '{entity.entity_name}' already exists.")
            
            raise CustomException(
                f"Product Type with name '{entity.entity_name}' already exists.",
                status.HTTP_409_CONFLICT
            )
        
        _ = Entities.objects.create(
            entity_uuid=entity.entity_uuid,
            entity_name=entity.entity_name,
            entity_description=entity.description,
            application_uuid_id=entity.application_uuid,
            customer_uuid_id=entity.customer_uuid,
            attribute_details_json=entity.attribute_details_json.__dict__,
            created_by=user_uuid,
            updated_by=user_uuid
        )

        logger.debug(f"Entity {entity.entity_name} created successfully.")

    def create_default_entity(self, customer_uuid, application_uuid, user_uuid):
        """Create a new entity in the database."""
        logger.debug(f"Creating default entity for customer: {customer_uuid}, application: {application_uuid}")

        attribute_details_json = AttributeDetailsJson(
            entity_name=EntityConstants.DEFAULT_ENTITY_NAME,
            attributes={EntityConstants.DEFAULT_ATTRIBUTE_NAME: [EntityConstants.DEFAULT_ATTRIBUTE_VALUE]}
        )

        default_entity = Entities.objects.create(
            entity_uuid=uuid4(),
            entity_name=EntityConstants.DEFAULT_ENTITY_NAME,
            application_uuid_id=application_uuid,
            customer_uuid_id=customer_uuid,
            is_default=True,
            entity_description=EntityConstants.DEFAULT_ENTITY_DESC,
            attribute_details_json=attribute_details_json.__dict__,
            created_by=user_uuid,
            updated_by=user_uuid
        )

        logger.debug(f"Default entity created entity_uuid: {default_entity.entity_uuid}")
        return default_entity

    def delete_entity(self, entity_uuid):
        """Delete an entity and its related data."""
        logger.debug(
            f"Deleting entity with UUID: {entity_uuid}")
        cnt, _ = Entities.objects.filter(entity_uuid=entity_uuid, is_default=False).delete()
        logger.debug(f"Entity with UUID: {entity_uuid} deleted successfully count: {cnt}.")

        return cnt

    def get_entity(self, entity_uuid):
        """Retrieve an entity by its UUID."""
        entity = Entities.objects.filter(entity_uuid=entity_uuid).annotate(attributes = F('attribute_details_json__attributes')).values('entity_uuid', 'entity_name', 'attributes', 'entity_description').first()
        logger.debug(f"Retrieved entity: {entity} for UUID: {entity_uuid}")
        return entity

    def update_entity(self, entity: Entity, user_uuid):
        
        """Update an existing entity."""
        
        logger.debug(f"Updating entity: {entity.entity_uuid} by user: {user_uuid}")
        
        if Entities.objects.exclude(entity_uuid=entity.entity_uuid).filter(
            application_uuid = entity.application_uuid,
            customer_uuid = entity.customer_uuid,
            entity_name__iexact=entity.entity_name
        ).exists():
            
            logger.error(f"Entity with name '{entity.entity_name}' already exists.")
            
            raise CustomException(
                f"Entity with name '{entity.entity_name}' already exists.",
                status.HTTP_409_CONFLICT
            )
        
        rows_cnt = Entities.objects.filter(entity_uuid=entity.entity_uuid, is_default=False).update(
            entity_name=entity.entity_name,
            entity_description=entity.description,
            attribute_details_json=entity.attribute_details_json.__dict__,
            updated_by=user_uuid
        )

        logger.debug(f"Entity {entity.entity_uuid} updated successfully.")
        return rows_cnt


    def get_or_create_default_entity(self, customer_uuid, application_uuid, user_uuid):
        """Retrieve or create the default entity for a customer and application."""
        logger.debug(
            f"Retrieving or creating default entity for customer: {customer_uuid}, application: {application_uuid}")

        attribute_details_json = AttributeDetailsJson(
            entity_name=EntityConstants.DEFAULT_ENTITY_NAME,
            attributes={EntityConstants.DEFAULT_ATTRIBUTE_NAME: {'values':[EntityConstants.DEFAULT_ATTRIBUTE_VALUE],
                                                                 'description':EntityConstants.DEFAULT_ENTITY_DESC}}
                    )

        entity, created = Entities.objects.get_or_create(
            entity_name=EntityConstants.DEFAULT_ENTITY_NAME,
            application_uuid_id=application_uuid,
            customer_uuid_id=customer_uuid,
            is_default=True,
            defaults={"entity_description": EntityConstants.DEFAULT_ENTITY_DESC,
            "attribute_details_json": attribute_details_json.__dict__,
                      'entity_uuid': uuid4(),
                      'created_by': user_uuid,
                      'updated_by': user_uuid}
        )

        logger.info(f"Default entity created: {created}, entity_uuid: {entity.entity_uuid}")
        return entity

    def get_entities_by_customer_uuid_and_application_uuid(self, customer_uuid, application_uuid, params):
        """Retrieve entities based on customer and application UUIDs with selective attributes."""
        logger.debug(f"Creating entities queryset for customer: {customer_uuid}, application: {application_uuid}")
        query = {
        'customer_uuid': customer_uuid,
        'application_uuid': application_uuid
        }

        # Add optional filters if provided
        if params and params.get('entity_name'):
            query['entity_name__icontains'] = params.get('entity_name')

        # Base queryset to fetch common fields
        entities_queryset = Entities.objects.filter(**query).order_by('-updated_ts')
        
        if params.get('only_attribute_keys'):
               # Prefetch knowledge sources and count them
            knowledge_sources_prefetch = Prefetch(
                'knowledge_sources',  # Adjust if you have a related name specified
                queryset=KnowledgeSources.objects.annotate(
                    knowledge_source_count=Count('knowledge_source_uuid')
                )
            )
            entities_queryset = entities_queryset.annotate(
            attribute_keys=RawSQL(
                "SELECT jsonb_agg(attribute_key) FROM jsonb_object_keys(entities.attribute_details_json->'attributes') AS attribute_key",
                [],
                output_field=models.JSONField()
            ),
            knowledge_source_count=Count('knowledgesources')  # Counting related KnowledgeSources
        ).prefetch_related(knowledge_sources_prefetch).values(
            'entity_uuid', 'entity_name', 'attribute_keys', 'is_default', 'knowledge_source_count'
        )
        else:
            entities_queryset = entities_queryset.values('entity_uuid', 'entity_name', 'is_default', 'attribute_details_json')
            if(params.get('entity_uuid')):
                entities_queryset = entities_queryset.exclude(entity_uuid=params.get('entity_uuid'))
        return entities_queryset

    def create_test_entity(self, customer_uuid, application_uuid):
        """Create a test entity for a specific customer and application."""
        logger.info(f"Creating test entity for customer: {customer_uuid}, application: {application_uuid}")
        entity = Entities.objects.create(
            entity_uuid=uuid4(),
            entity_name=TestEntityConstants.ENTITY_NAME,
            application_uuid_id=application_uuid,
            customer_uuid_id=customer_uuid,
            attribute_details_json=TestEntityConstants.ENTITY_ATTRIBUTE_DETAILS_JSON.__dict__
        )
        logger.info(f"Test entity created: {entity.entity_name}")
        return entity
