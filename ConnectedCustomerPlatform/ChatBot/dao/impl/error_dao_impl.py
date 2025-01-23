from ChatBot.dao.interface.error_dao_interface import ErrorCorrectionDaoInterface

from ChatBot.constant.constants import ErrorConstants
from DatabaseApp.models import (
    Customers,
    Applications,
    CustomerApplicationMapping,
    KnowledgeSources,
    Errors,
    Media
)
from django.db.models import F, Value,IntegerField,Case, When
from django.db.models.functions import Cast

from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class ErrorCorrectionDaoImpl(ErrorCorrectionDaoInterface):
        
    def get_filedetails_by_fileuuid(self, file_uuid):
        
        """get the file details by file uuid
        
        Returns:
            knowledge source name, path, status, customer_uuid, appliation_uuid
        """
        logger.info("In error_dao.py :: ErrorCorrectionDaoImpl :: get_filedetails_by_fileuuid")
        
        file = KnowledgeSources.objects.filter(knowledge_source_uuid=file_uuid).values(
            'knowledge_source_name', 'knowledge_source_path', 'knowledge_source_status', 'customer_uuid__cust_uuid', 'application_uuid__application_uuid').first()
        if file is None:
            raise ResourceNotFoundException(f"No knowledge source with uuid :: {file_uuid}")
        
        return (
            file['knowledge_source_name'],
            file['knowledge_source_path'],
            file['knowledge_source_status'],
            file['customer_uuid__cust_uuid'],
            file['application_uuid__application_uuid']
        )
    
    def update_error_status(self, error_uuid, error_status):
        
        """update the error status of an error
        
        Returns:
            None
        """
        logger.info("In error_dao.py :: ErrorCorrectionDaoImpl :: update_error_status")
        
        updated_count =  Errors.objects.filter(error_uuid=error_uuid).update(error_status=error_status)
        
        if updated_count == 0:
            raise ResourceNotFoundException(f"No error with uuid :: {error_uuid}")
        
    def get_collections_by_customer_application(self, customer_uuid, application_uuid):
        
        """get the chroma collections by customer_uuid and application_uuid
        
        Returns:
            chunk collection name, cache collection name, custom collection name
        """
        logger.info("In error_dao.py :: ErrorCorrectionDaoImpl :: get_collections_by_customer_application")
        
        cam_id = CustomerApplicationMapping.objects.filter(customer__cust_uuid=customer_uuid, application__application_uuid=application_uuid).values_list('customer_application_id', flat=True).first()

        chunk_collection = f"cw_{str(cam_id)}"
        cache_collection = f"cw_cache_{str(cam_id)}"
        custom_collection = f"custom_{str(cam_id)}"
        
        return chunk_collection, cache_collection, custom_collection
    
    def update_knowledge_source_status(self, knowledge_source_uuid, status):
        
        """update the status of a knwoledge source
        
        Returns:
            None
        """
        logger.info("In error_dao.py :: ErrorCorrectionDaoImpl :: update_knowledge_source_status")
        
        updated_count = KnowledgeSources.objects.filter(knowledge_source_uuid=knowledge_source_uuid).update(knowledge_source_status=status)
        
        if updated_count == 0:
            raise ResourceNotFoundException(f"No knowledge source with uuid :: {knowledge_source_uuid}")
        
    def add_media(self, id, name, path, details, source_uuid, customer_uuid, application_uuid):
        
        """add a new image/video media
        
        Returns:
            None
        """
        logger.info("In error_dao.py :: ErrorCorrectionDaoImpl :: add_media")
        
        media = Media(
            media_uuid=id,
            media_name=name,
            media_path=path,
            media_details_json=details,
            knowledge_source_uuid=source_uuid,
            customer_uuid_id=customer_uuid,
            application_uuid_id=application_uuid
        )
        media.save()

    def delete_errors_of_knowledge_source(self,knowledge_source_uuid):
        """
        Deletes all errors associated with the specified knowledge source UUID.
        """
        Errors.objects.filter(knowledge_source_uuid=knowledge_source_uuid).delete()

    def knowledge_source_errors_count(self, knowledge_source_uuid: str) -> int:
        
        """
        returns knowledge source errors count
        """
        logger.info("In error_dao.py :: ErrorCorrectionDaoImpl :: knowledge_source_errors_count")
        return Errors.objects.filter(knowledge_source_uuid=knowledge_source_uuid,error_status=ErrorConstants.UNRESOLVED).count()
        
    def get_errors_with_knowledge_source_uuid(self,filters):
        """
        Retrieves knowledge source errors associated with a knowledge source uuid.
        """ 
        query = {
            'knowledge_source_uuid': str(filters.get('knowledge_source_uuid'))
        }

        # Add optional filters if they are provided
        if filters.get('error_type'):
            query['error_type__icontains'] = filters['error_type']

        # Base queryset to fetch common fields
        return Errors.objects.filter(**query).annotate(
            page_number=Case(
                When(
                    error_details_json__page=None,
                    then=Value(-1)  # Use -1 if the page is NULL
                ),
                default=Cast(F('error_details_json__page'), output_field=IntegerField()),  # Cast JSON to integer
                output_field=IntegerField()
            )
        ).order_by('page_number').values('error_uuid', 'error_type', 'error_status', 'error_details_json')                  
    def has_unresolved_errors(self, knowledge_source_uuid):
        has_errs = Errors.objects.filter(knowledge_source_uuid=knowledge_source_uuid,
                                         error_status=ErrorConstants.UNRESOLVED).exists()
        return has_errs

    def create_error_data(self,error_uuid, error_type, error_status, knowledge_source_uuid, application_uuid, customer_uuid):
        """
            create a error record based on params
            Args:
                error_uuid (str): unique identifier of error
                error_type (str): type of error
                error_status (str): error status whether it's resolved or in other state
                knowledge_source_uuid (str): unique identifier of knowledge_source
                application_uuid (str): unique identifier of application
                customer_uuid (str): unique identifier of customer
            Returns:
                created error record
        """
        logger.debug(f"creating error record for knowledgesource_uuid {knowledge_source_uuid}")
        error = Errors.objects.create(
                                error_uuid=error_uuid,
                                error_type=error_type,
                                error_status=error_status,
                                knowledge_source_uuid_id=knowledge_source_uuid,
                                application_uuid_id=application_uuid,
                                customer_uuid_id=customer_uuid,
                )
        return error