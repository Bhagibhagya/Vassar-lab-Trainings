from django.db.models import Func, F, Value,Q
from django.db import models
from functools import reduce
from django.db.models.functions import Lower

from ChatBot.dao.interface.knowledge_sources_dao_interface import IKnowledgeSourcesDao
from ChatBot.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException
from DatabaseApp.models import KnowledgeSources
from ChatBot.constant.constants import TestKnowledgeSourceConstants, SMEConstants, KnowledgeSourceTypes

from uuid import uuid4
import logging

# Configure logger
logger = logging.getLogger(__name__)

class KnowledgeSourcesDaoImpl(IKnowledgeSourcesDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KnowledgeSourcesDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        # Ensures initialization only occurs once (Singleton pattern)
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            self.initialized = True


    def update_entity_attributes_by_entity_uuid(self, prev_entity_uuid, entity_uuid, attribute_details_json, user_uuid):
        logger.debug(f"updating to knowledge sources entity details having entity: {prev_entity_uuid} to entity: {entity_uuid}, attributes: {attribute_details_json}")

        rows_updated = KnowledgeSources.objects.filter(entity_uuid_id=prev_entity_uuid).update(
            entity_uuid_id=entity_uuid,
            attribute_details_json=attribute_details_json,
            updated_by=user_uuid
        )

        logger.debug(f"updated to knowledge sources entity details having entity: {prev_entity_uuid} to entity: {entity_uuid}, attributes: {attribute_details_json}")

        return rows_updated

    def update_entity_attributes(self, knowledge_source_uuid, prev_entity_uuid, entity_uuid, attribute_details_json, user_uuid):
        logger.debug(f"updating to knowledge sources entity details having entity: {prev_entity_uuid}, ks uuid: {knowledge_source_uuid} to entity: {entity_uuid}, attributes: {attribute_details_json}")
        rows_updated = KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid, entity_uuid_id=prev_entity_uuid).update(
            entity_uuid_id=entity_uuid,
            attribute_details_json=attribute_details_json,
            updated_by=user_uuid
        )
        logger.debug(f"updated to knowledge sources entity details having entity: {prev_entity_uuid}, ks uuid: {knowledge_source_uuid} to entity: {entity_uuid}, attributes: {attribute_details_json}")

        return rows_updated

    def create_test_knowledge_source(self, entity_uuid, customer_uuid, application_uuid, user_uuid):
        knowledge_source = KnowledgeSources.objects.create(knowledge_source_uuid = uuid4(),
                                                            knowledge_source_name = TestKnowledgeSourceConstants.KNOWLEDGE_SOURCE_NAME,
                                                            knowledge_source_path = TestKnowledgeSourceConstants.KNOWLEDGE_SOURCE_PATH,
                                                            knowledge_source_type = TestKnowledgeSourceConstants.KNOWLEDGE_SOURCE_TYPE,
                                                            knowledge_source_status = KnowledgeSources.KnowledgeSourceStatus.UNDER_REVIEW,
                                                            knowledge_source_metadata = TestKnowledgeSourceConstants.KNOWLEDGE_SOURCE_METADATA,
                                                            application_uuid_id= application_uuid,
                                                            customer_uuid_id = customer_uuid,
                                                            entity_uuid_id = entity_uuid,
                                                            attribute_details_json = TestKnowledgeSourceConstants.KNOWLEDGE_SOURCE_ATTRIBUTE_DETAILS_JSON.__dict__,
                                                            created_by = user_uuid,
                                                            updated_by = user_uuid
                                                    )
        return knowledge_source

    def get_knowledge_attribute_details_by_entity_uuid(self, entity_uuid):
        knowledge_sources =  KnowledgeSources.objects.filter(entity_uuid=entity_uuid).values('attribute_details_json').all()
        return knowledge_sources

    def update_qa_generation_status(self, knowledge_source_uuids, user_uuid, entity_uuids_list):
        queryset = KnowledgeSources.objects.filter(
            knowledge_source_uuid__in=knowledge_source_uuids,
            qa_status=False
        )

        # Apply entity_uuid filter only if entity_uuids_list is not empty
        if entity_uuids_list:
            queryset = queryset.filter(entity_uuid__in=entity_uuids_list)

        rows_matched = queryset.update(
            knowledge_source_status=KnowledgeSources.KnowledgeSourceStatus.QA_GENERATING,
            qa_status=True,
            updated_by=user_uuid
        )
        return rows_matched


    def get_knowledge_sources_by_entity_uuid(self, entity_uuid, customer_uuid, application_uuid):
        """Retrieve knowledge source by  entities based on customer and application UUIDs, with pagination."""
        logger.debug(
            f"Creating knowledge sources queryset for customer: {customer_uuid}, application: {application_uuid}, entity: {entity_uuid}")

        return KnowledgeSources.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid, entity_uuid=entity_uuid).exclude(knowledge_source_status__in=[KnowledgeSources.KnowledgeSourceStatus.PROCESSING, KnowledgeSources.KnowledgeSourceStatus.FAILED]).values('knowledge_source_uuid', 'knowledge_source_name', 'knowledge_source_status').order_by('-updated_ts')

    

    def get_reviewed_knowledge_sources_by_customer_and_application(self, customer_uuid, application_uuid):
        
        knowledge_sources = KnowledgeSources.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            knowledge_source_status=KnowledgeSources.KnowledgeSourceStatus.REVIEWED,
            qa_status=False
        ).values("knowledge_source_uuid", "knowledge_source_name", "knowledge_source_metadata")
        
        return list(knowledge_sources)

    def get_qa_generated_knowledge_sources_with_json_edited(self, customer_uuid: str, application_uuid: str) -> list[dict]:
                
        """ 
        Fetch the knwoledge sources which are qa generated but not json has been edited.
        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            knwoledge source uuids and names which are qa generated, but json has been edited.
        """
        
        logger.info('Fetching knowledge sources with qa generated True and json edited.')
        
        sources = list(KnowledgeSources.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            knowledge_source_status=KnowledgeSources.KnowledgeSourceStatus.QA_GENERATED
        ).values(
            "knowledge_source_uuid", "knowledge_source_name", "knowledge_source_metadata"
        ))
        
        edited_sources = []
        
        for source in sources:

            meta:dict = source['knowledge_source_metadata']
            if meta.get('edited', False) == True:
                
                edited_sources.append({
                    'knowledge_source_uuid' : source['knowledge_source_uuid'],
                    'knowledge_source_name' : source['knowledge_source_name'],
                    'json_edited' : True
                })

        return edited_sources  

    def get_video_type_knowledge_sources_by_customer_and_application(self, customer_uuid, application_uuid):
        knowledge_sources = KnowledgeSources.objects.filter(application_uuid=application_uuid,
                                                            customer_uuid=customer_uuid,
                                                            knowledge_source_type=KnowledgeSourceTypes.VIDEO.value,
                                                            knowledge_source_status__in=[
                                                                KnowledgeSources.KnowledgeSourceStatus.REVIEWED,
                                                                KnowledgeSources.KnowledgeSourceStatus.QA_GENERATING]).values(
            "knowledge_source_name", "knowledge_source_uuid", "knowledge_source_metadata", "knowledge_source_path")
        return knowledge_sources
    
    def create_knowledge_source(self,knowledge_source_uuid, knowledge_source_name, application_uuid, 
                                knowledge_source_type, status, user_uuid, customer_uuid, 
                                entity_uuid, attribute_details_json,reason_for_failure,is_i3s_enabled
):
        """
        Implementation of the abstract method to create a KnowledgeSource record.
        """
        KnowledgeSources.objects.create(
            knowledge_source_uuid=knowledge_source_uuid,
            knowledge_source_name=knowledge_source_name,
            application_uuid_id=application_uuid,  # use _id when passing the raw UUID
            knowledge_source_type=knowledge_source_type,
            knowledge_source_status=status ,
            updated_by=user_uuid,
            customer_uuid_id=customer_uuid,  # use _id for ForeignKey raw UUIDs
            entity_uuid_id=entity_uuid,  # use _id for ForeignKey raw UUIDs
            attribute_details_json=attribute_details_json,
            knowledge_source_metadata={'fail_cause':reason_for_failure,'is_i3s_enabled':is_i3s_enabled}
        )
        return {
            "knowledge_source_uuid": knowledge_source_uuid,
    }
        
    def update_knowledge_source_details(self,knowledge_source_uuid,knowledge_source_name,knowledge_source_type,status,metadata,user_uuid,customer_uuid,application_uuid):
       """
        Implementation of the abstract method to update a KnowledgeSource record.
        """
       KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).update(
            knowledge_source_name=knowledge_source_name,
            application_uuid_id=application_uuid,
            knowledge_source_type=knowledge_source_type,
            knowledge_source_status=status,
            updated_by=user_uuid,
            customer_uuid_id=customer_uuid,
            is_reuploaded=True,
            knowledge_source_metadata = metadata
        )
    
    def get_knowledge_source_with_uuid(self, knowledge_source_uuid) -> dict:
        """
        Retrieves specific fields of a KnowledgeSource by UUID.
        Logs an error and raises an exception if the KnowledgeSource is not found.
        """
        # Attempt to retrieve the knowledge source by filtering with the provided UUID
        knowledge_source = KnowledgeSources.objects.filter(
            knowledge_source_uuid=knowledge_source_uuid).values(
            'knowledge_source_name', 
            'knowledge_source_type', 
            'knowledge_source_status',
            'knowledge_source_path',
            'knowledge_source_metadata'
        ).first()

        # Check if knowledge source exists; if not, log an error and raise exception
        if not knowledge_source:
            logger.error(f"Knowledge source with UUID {knowledge_source_uuid} not found.")
            raise ResourceNotFoundException(ErrorMessages.KNOWLEDGE_SOURCE_NOT_FOUND)

        return knowledge_source
    

    def update_knowledge_source_path(self,knowledge_source_uuid,knowledge_source_path):
       """
        Implementation of the abstract method to update a KnowledgeSource Path.
        """
       KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).update(
            knowledge_source_path=knowledge_source_path,
        )

    def get_knowledge_sources_by_customer_and_application_ids(self, customer_uuid, application_uuid,filters) :
        """Retrieve knowledge_sources based on customer and application UUIDs."""
        logger.debug(f"Creating knowledge_sources queryset for customer: {customer_uuid}, application: {application_uuid}")
        query = {
            'customer_uuid': customer_uuid,
            'application_uuid': application_uuid
        }

        # Add optional filters if they are provided
        if filters.get('knowledge_source_name'):
            query['knowledge_source_name__icontains'] = filters['knowledge_source_name']

        # Base queryset to fetch common fields
        return KnowledgeSources.objects.filter(**query).order_by('-updated_ts')


    def check_knowledge_sources_exists(self,knowledge_source_names,knowledge_source_uuid, customer_uuid, application_uuid):
        """
        Checks if specified knowledge source files exist in the database for a given user, 
        customer, and application UUID, returning a list of matching file names or IDs.
        """
        # Convert names to lowercase for comparison
        lower_names = [name.lower() for name in knowledge_source_names]

        filters = Q(customer_uuid=customer_uuid, application_uuid=application_uuid)

        # Exclude specific `knowledge_source_uuid` if provided
        if knowledge_source_uuid:
            filters &= ~Q(knowledge_source_uuid=knowledge_source_uuid)

        # Filter by case-insensitive matching
        return set(
            KnowledgeSources.objects.annotate(lower_name=Lower('knowledge_source_name'))
            .filter(filters, lower_name__in=lower_names)
            .values_list('knowledge_source_name', flat=True)
        )
    

    def delete_knowledge_source_by_uuid(self, knowledge_source_uuid):
        """
        deleted knowledge source by knowledge_source_uuid
        """
        KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).delete()

    def get_metadata(self, knowledge_source_uuid: str) -> dict:
        
        """
        Fetch the metadata of the knowledge source.

        Args:
            knowledge_source_uuid (_type_): UUID of knowledge source

        Returns:
            metadata of the knowledge source: dict

        Raises:
            ResourceNotFoundException: When there is no knowledge source with given uuid.
        """
        
        logger.info(f'Fetching metadata of the knowledge source with id :: {knowledge_source_uuid}')
        metadata = KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).values_list(
            'knowledge_source_metadata', flat=True
        ).first()
        
        if metadata is None:
            logger.error(f'No knowledge source with uuid :: {knowledge_source_uuid}')
            raise ResourceNotFoundException(f'No knowledge source with uuid :: {knowledge_source_uuid}')

        return metadata
    
    def update_metadata(self, knowledge_source_uuid, metadata):
        
        """
        Update the metadata of the knowledge source.

        Args:
            knowledge_source_uuid (_type_): UUID of knowledge source
            metadata (_type_): metadata dict

        Raises:
            ResourceNotFoundException: When there is no knowledge source with given uuid.
        """
        
        logger.info(f'Updating metadata of the knowledge source with id :: {knowledge_source_uuid}')
        rows_updated = KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).update(
            knowledge_source_metadata=metadata
        )
        
        if rows_updated == 0:
            logger.error(f'No knowledge source with uuid :: {knowledge_source_uuid}')
            raise ResourceNotFoundException(f'No knowledge source with uuid :: {knowledge_source_uuid}')
    
    def update_qa_status(self, knowledge_source_uuid: str, qa_status: bool) -> None:
        
        """
        Update the knowledge source qa status

        Args:
            knowledge_source_uuid (str): UUID of the knowledge source
            qa_status (bool): the boolean values the field has to be updated to
        """
        
        logger.info(f'Updating the qa status of the knowledge source with uuid :: {knowledge_source_uuid}')
        rows_updated = KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).update(qa_status=qa_status)
        
        if rows_updated == 0:
            
            logger.error(f'No knowledge source with uuid :: {knowledge_source_uuid}')
            raise ResourceNotFoundException(f'No knowledge source with uuid :: {knowledge_source_uuid}')