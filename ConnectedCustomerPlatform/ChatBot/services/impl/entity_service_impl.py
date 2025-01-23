from uuid import uuid4

from ChatBot.services.interface.entity_service_interface import IEntityService
from ChatBot.dao.impl.entity_dao_impl import EntityDaoImpl
from ChatBot.dao.impl.sme_dao_impl import SMEDaoImpl
from ChatBot.dao.impl.knowledge_sources_dao_impl import KnowledgeSourcesDaoImpl
from ChatBot.dataclasses.entity_data import Entity, AttributeDetailsJson

from rest_framework import status

from ChatBot.constant.constants import EntityConstants
from ChatBot.constant.error_messages import ErrorMessages
from django.db import transaction, IntegrityError

from ChatBot.utils import get_collection_names, get_default_entity_file_attributes
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException, \
    ResourceNotFoundException

from AIServices.VectorStore.chromavectorstore import chroma_obj
from Platform.utils import paginate_queryset

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class EntityServiceImpl(IEntityService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EntityServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        # Ensures initialization only occurs once (Singleton pattern)
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            self.__entity_dao = EntityDaoImpl()
            self.__knowledge_sources_dao = KnowledgeSourcesDaoImpl()
            self.__sme_dao = SMEDaoImpl()
            self.initialized = True
            logger.info("EntityService initialized.")

    @transaction.atomic
    def add_entity(self, entity, customer_uuid, application_uuid, user_uuid):
        """
        Adds a new entity to the database.

        Raises:
            CustomException: If an entity with the same name already exists or entity name is default.
        """
        logger.debug("Attempting to add entity: %s", entity.get('name'))

        # Check if the entity being added has default entity name
        if self.__check_is_default_entity(entity.get('name')):
            logger.error("Entity already exists: %s", entity.get('name'))
            raise CustomException(ErrorMessages.CANNOT_ADD_DEFAULT_ENTITY, status_code=status.HTTP_403_FORBIDDEN)

        # Create new entity dataclass object
        entity_data = Entity(
            entity_uuid=uuid4(),
            entity_name=entity.get('name'),
            description=entity.get('description'),
            attribute_details_json=AttributeDetailsJson(entity_name=entity.get('name'),
                                                        attributes=entity.get('attributes')),
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
        )

        # Persist the entity to the database
        try:
            _ = self.__entity_dao.create_entity(entity_data, user_uuid)
        except IntegrityError as e:
            self.__check_duplicate_entity_error(e, customer_uuid, application_uuid, entity_data.entity_name)
            raise e

        logger.debug("Entity added successfully: %s", entity.get('name'))

    @transaction.atomic
    def delete_entity(self, entity_uuid, customer_uuid, application_uuid, user_uuid):
        """
        Deletes an entity from the database.

        Raises:
            ResourceNotFoundException: If the entity is not found.
            InvalidValueProvidedException: If trying to delete a default entity.
        """
        logger.debug("Attempting to delete entity: %s", entity_uuid)

        entity_uuid = str(entity_uuid)

        # fetching default entity to assign it the knowledge source which having deleted entity
        default_entity = self.__entity_dao.get_or_create_default_entity(customer_uuid, application_uuid, user_uuid)

        default_entity_uuid = str(default_entity.entity_uuid)

        default_file_attribute_details_json = self.__get_default_entity_file_attributes()

        # update knowledge source having deleted entity with default entity
        ks_rows_updated = self.__knowledge_sources_dao.update_entity_attributes_by_entity_uuid(entity_uuid, default_entity_uuid, default_file_attribute_details_json, user_uuid)

        # Delete the entity from the database
        deleted_count = self.__entity_dao.delete_entity(entity_uuid)
        if deleted_count == 0:
            raise CustomException(ErrorMessages.UNABLE_TO_DELETE_ENTITY)

        # update entity_details_json in answers with deleted entity uuid to default entity uuid
        _ = self.__sme_dao.update_entity_uuid_in_answer(entity_uuid, default_entity_uuid, user_uuid)

        if ks_rows_updated != 0:
            collection_name, _ = get_collection_names(customer_uuid, application_uuid)
            # updating chunks metadata in chroma having deleted entity with default entity
            chroma_obj.update_entity_to_default(collection_name, entity_uuid, default_entity_uuid)

        logger.debug("Entity deleted successfully: %s", entity_uuid)

    @transaction.atomic
    def update_entity(self, entity, customer_uuid, application_uuid, user_uuid):
        """
        Updates an existing entity in the database.

        Raises:
            InvalidValueProvidedException: If trying to update a default entity.
            CustomException: if entity attribute or value is assigned to knowledge source
        """
        logger.debug("Attempting to update entity: %s", entity.get('entity_uuid'))

        entity_uuid = entity.get('entity_uuid')
        entity_name = entity.get('name')
        entity_attribute_details_json = AttributeDetailsJson(entity_name=entity_name,
                                                             attributes=entity.get('attributes'))

        # Check if the entity is a default entity, which cannot be updated
        if self.__check_is_default_entity(entity_name):
            logger.debug("Cannot update entity to default entity: %s", entity_name)
            raise InvalidValueProvidedException(ErrorMessages.ENTITY_NAME_CANNOT_BE_DEFAULT)

        # getting the all information of existing attributes and values assigned to knowledge sources
        knowledge_sources = self.__knowledge_sources_dao.get_knowledge_attribute_details_by_entity_uuid(entity_uuid)

        # checking if any attribute or its value assigned to a knowledge source is removed, if so raising exception
        for knowledge_source in knowledge_sources:
            for attribute in knowledge_source['attribute_details_json']['attributes']:
                if attribute not in entity_attribute_details_json.attributes:
                    raise CustomException(ErrorMessages.CANNOT_DELETE_ASSIGNED_ENTITY_ATTRIBUTES.format(attribute))
                value = knowledge_source['attribute_details_json']['attributes'][attribute]
                if value not in entity_attribute_details_json.attributes[attribute]['values']:
                    raise CustomException(ErrorMessages.CANNOT_DELETE_ASSIGNED_ENTITY_ATTRIBUTE_VALUES.format(attribute, value))
        ## todo next sprint update on exception handling

        # Create updated entity object
        entity_data = Entity(
            entity_uuid=entity_uuid,
            entity_name=entity_name,
            description=entity.get('description'),
            attribute_details_json=entity_attribute_details_json,
            customer_uuid=customer_uuid,
            application_uuid=application_uuid
        )

        # Persist the updated entity to the database
        try:
            updated_rows_cnt = self.__entity_dao.update_entity(entity_data, user_uuid)
        except IntegrityError as e:
            self.__check_duplicate_entity_error(e, customer_uuid, application_uuid, entity_name)
            raise e

        if updated_rows_cnt == 0:
            raise CustomException(ErrorMessages.UNABLE_TO_UPDATE_ENTITY)

        if len(knowledge_sources) > 0:
            collection_name, _ = get_collection_names(customer_uuid, application_uuid)

            # updating chunks metadata in chroma having old entity name to new entity name
            chroma_obj.update_entity_name_by_entity_uuid(collection_name, entity_uuid, entity_name)

        logger.debug("Entity updated successfully: %s", entity.get('entity_uuid'))

    def get_entity_details(self, entity_uuid):
        """
        Retrieves the entity based on entity UUID.
        """
        logger.debug("Retrieving entity: %s", entity_uuid)

        # Retrieve entity by entity_uuid
        entity = self.__entity_dao.get_entity(entity_uuid)

        if entity is None:
            raise ResourceNotFoundException(ErrorMessages.ENTITY_NOT_FOUND)

        logger.debug("Entities retrieved successfully.")
        return entity

    def get_entities_by_customer_and_application(self, customer_uuid, application_uuid, user_uuid, params):
        """
        Retrieves a list of entities based on customer and application UUIDs.
        """
        logger.debug("Retrieving entities for customer_uuid: %s, application_uuid: %s", customer_uuid, application_uuid)

        # Retrieve entities query set
        entities_queryset = self.__entity_dao.get_entities_by_customer_uuid_and_application_uuid(customer_uuid, application_uuid,params)

        page, paginator =  paginate_queryset(entities_queryset, params)

        total_entries = paginator.count

        data = page.object_list

        if total_entries == 0 and not(params.get('entity_name')):
            logger.debug(f"no entities are found creating default entity from customer: {customer_uuid}, application: {application_uuid}")
            # if no entities are present for given customer and application add default entity and return it

            default_entity = self.__entity_dao.create_default_entity(customer_uuid, application_uuid, user_uuid)

            # create the get entities response with only default entity
            data = [{'entity_uuid': default_entity.entity_uuid,
                     'entity_name': default_entity.entity_name,
                     'is_default': default_entity.is_default,
                     'attribute_keys': default_entity.attribute_details_json['attributes'].keys(),
                     'knowledge_source_count': 0
                     }]

            total_entries = 1

        response = {
            'total_entries': total_entries,
            'data': data
        }
        logger.info("Entities retrieved successfully.")
        return response

    @transaction.atomic
    def update_knowledge_source_entity_assignment(self, data, customer_uuid, application_uuid, user_uuid):
        """
        Assigns or unassigns an entity from a knowledge source based on the provided status. 
        It updates the entity attributes and manages dependencies with default entities as needed. 
        Handles input validation and raises exceptions for error scenarios.
        """
        knowledge_source_uuid = data.get('knowledge_source_uuid')
        entity_uuid=data.get('entity_uuid')
        entity_assignment_status=data.get('entity_assignment_status')
        attribute_details_json = data.get('attribute_details_json')
        prev_entity_uuid=str(data.get('prev_entity_uuid'))

        # Handles the unassign of an entity to a knowledge source.
        if entity_assignment_status == EntityConstants.ASSIGN_UNASSIGN_CHOICES[1]:  # when status is unassign
            default_entity = self.__entity_dao.get_or_create_default_entity(customer_uuid, application_uuid, user_uuid)
            updated_entity_uuid = str(default_entity.entity_uuid)
            prev_entity_uuid=str(entity_uuid)

            if updated_entity_uuid == entity_uuid:
                logger.error("Cannot unassign default entity: %s", updated_entity_uuid)
                raise CustomException(ErrorMessages.CANNOT_UNASSIGN_DEFAULT_ENTITY, status_code=status.HTTP_403_FORBIDDEN)
            updated_attribute_details_json = get_default_entity_file_attributes(default_entity.attribute_details_json)

        # Handles the assignment of an entity to a knowledge source. 
        else:
             # when status is assign
            updated_entity_uuid = str(entity_uuid)
            updated_attribute_details_json = (attribute_details_json)

        # Call the method to update entity assignments
        self.__update_entity_assignments(prev_entity_uuid, updated_entity_uuid, knowledge_source_uuid, updated_attribute_details_json, user_uuid, customer_uuid, application_uuid)
        
    def __update_entity_assignments(self, prev_entity_uuid, updated_entity_uuid, knowledge_source_uuid, updated_attribute_details_json, user_uuid, customer_uuid, application_uuid):
        """
        Updates entity UUID in answers and knowledge source attributes.
        Raises an exception if the update fails and updates metadata in Chroma.
        """
        # Update entity UUID in answers and knowledge source attributes
        updated_rows_cnt = self.__knowledge_sources_dao.update_entity_attributes(knowledge_source_uuid, prev_entity_uuid, updated_entity_uuid, updated_attribute_details_json, user_uuid)
        if updated_rows_cnt == 0:
            raise CustomException(ErrorMessages.KNOWLEDGE_SOURCE_ENTITY_UPDATING_FAILED)

        collection_name, _ = get_collection_names(customer_uuid, application_uuid)

        # update chunks metadata in chroma for the knowledge source
        chroma_obj.update_entity_of_knowledge_source(collection_name, knowledge_source_uuid, updated_entity_uuid, updated_attribute_details_json)

        logger.info("Entity assignment updated successfully for knowledge source UUID: %s", knowledge_source_uuid)

    def get_knowledge_sources_by_entity_uuid(self, entity_uuid, customer_uuid, application_uuid, params):
        """
        Retrieves a list of entities based on customer and application UUIDs.
        """
        logger.debug("Retrieving knowledge sources for customer_uuid: %s, application_uuid: %s, entity_uuid %s", customer_uuid, application_uuid, entity_uuid)

        # Retrieve entities query set
        entities_queryset = self.__knowledge_sources_dao.get_knowledge_sources_by_entity_uuid(entity_uuid, customer_uuid, application_uuid)

        page, paginator =  paginate_queryset(entities_queryset, params)

        response = {
            'total_entries': paginator.count,
            'data': page.object_list
        }
        logger.info("Entities retrieved successfully.")
        return response
    

    def __check_is_default_entity(self, entity_name):
        """
        Checks if the provided entity name matches the default entity.

        Returns:
            bool: True if the entity is the default entity, False otherwise.
        """
        return entity_name == EntityConstants.DEFAULT_ENTITY_NAME

    def __check_duplicate_entity_error(self, exception, customer_uuid, application_uuid, entity_name):
        error_message = str(exception)
        if "duplicate key value violates unique constraint" in error_message and f"({customer_uuid}, {application_uuid}, {entity_name}" in error_message:
            logger.debug(f"Product Type with name {entity_name} already exists : {exception}")
            raise CustomException(ErrorMessages.DUPLICATE_ENTITY, status_code=status.HTTP_409_CONFLICT)



    def __get_default_entity_file_attributes(self):
        return AttributeDetailsJson(
            entity_name=EntityConstants.DEFAULT_ENTITY_NAME,
            attributes={EntityConstants.DEFAULT_ATTRIBUTE_NAME: {'values':[EntityConstants.DEFAULT_ATTRIBUTE_VALUE],
                                                                 'description':EntityConstants.DEFAULT_ENTITY_DESC}}
                    ).__dict__