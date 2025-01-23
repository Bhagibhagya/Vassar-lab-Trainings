import inspect

from django.db.models import Q,F
from django.db import IntegrityError

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import PromptTemplateCustomerApplicationMapping
from Platform.constant.error_messages import ErrorMessages
from Platform.dao.interface.prompt_template_customer_application_mapping_dao_interface import IPromptTemplateCustomerApplicationMappingDao
import logging
logger = logging.getLogger(__name__)

class PromptTemplateCustomerApplicationMappingDaoImpl(IPromptTemplateCustomerApplicationMappingDao):
    """
        Dao for Prompt_template_customer_application_mapping, providing methods to add, edit,
        delete, and retrieve.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(PromptTemplateCustomerApplicationMappingDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of PromptTemplateCustomerApplicationMappingDaoImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the PromptDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside PromptTemplateCustomerApplicationMappingDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Save PromptTemplateCustomerApplicationMapping in the database.
    def save_mapping(self, mapping):
        """
            This method saves the prompt_template_customer_application_mapping in the database
            :param : Instance of prompt_template_customer_application_mapping
            :raises : Raises any exception while saving the data into database
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        try:
            mapping.save()
        except IntegrityError as e:
            # Log the entire exception for debugging
            logger.error(f"Integrity error occurred: {str(e)}")
            # Foreign key constraint violation check

            if 'prompt_template_customer_application_mapping_customer_uuid_fkey' in str(e):
                logger.error(f"Customer not found for: {mapping.customer_uuid}")
                raise CustomException(ErrorMessages.CUSTOMER_NOT_FOUND)

            elif 'prompt_template_customer_application_mapp_application_uuid_fkey' in str(e):
                logger.error(f"Application not found for: {mapping.application_uuid}")
                raise CustomException(ErrorMessages.APPLICATION_NOT_FOUND)

            # If the error doesn't match the above conditions, raise a generic exception
            else:
                raise e

    # Get all the prompt_templates under a customer and application
    def get_mappings(self, customer_uuid,application_uuid,prompt_category_uuid):
        """
            Fetches all the prompt_templates under specific customer and application from prompt_template_customer_application_mapping
            :param : customer_uuid : customer uuid of prompt_templates need to be fetched
            :param : application_uuid : application uuid of prompt_templates need to be fetched
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        filter_query = Q(customer_uuid=customer_uuid,application_uuid=application_uuid)
        # If prompt_uuid is not none then include it in filter_query
        if prompt_category_uuid is not None:
            filter_query &= Q(prompt_template_uuid__prompt_category_uuid=prompt_category_uuid)
        # Joining prompt_template_customer_application_mapping table ,prompt_template and prompt_category table using annotate and fetches required fields
        return (PromptTemplateCustomerApplicationMapping.objects.filter(filter_query)
                .annotate(
                    prompt_template_name=F('prompt_template_uuid__prompt_template_name'),
                    prompt_category_uuid=F('prompt_template_uuid__prompt_category_uuid'),
                    prompt_category_name=F('prompt_template_uuid__prompt_category_uuid__prompt_category_name'),
                    description=F('prompt_template_uuid__description'),
                    prompt_template_details_json = F('prompt_template_uuid__prompt_template_details_json'),
                    prompt_template_inserted_ts=F('prompt_template_uuid__inserted_ts')
                )
                .order_by('-prompt_template_inserted_ts')
                .values('mapping_uuid','prompt_template_uuid','prompt_category_uuid','prompt_template_details_json','description','prompt_template_name', 'prompt_category_name','inserted_ts'))

    # Get prompt_template by its mapping uuid
    def get_mapping_by_id(self, mapping_uuid):
        """
            Fetches the prompt_template under a customer using mapping_uuid from prompt_template_customer_application_mapping
            :param : mapping uuid which maps the prompt_template and customer_application
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Joining prompt_template_customer_application_mapping table ,prompt_template and prompt_category table using annotate and fetches required fields
        return (PromptTemplateCustomerApplicationMapping.objects.filter(mapping_uuid=mapping_uuid)
                .annotate(
                    prompt_template_name=F('prompt_template_uuid__prompt_template_name'),
                    prompt_category_uuid=F('prompt_template_uuid__prompt_category_uuid'),
                    prompt_category_name=F('prompt_template_uuid__prompt_category_uuid__prompt_category_name'),
                    description=F('prompt_template_uuid__description'),
                    prompt_template_details_json=F('prompt_template_uuid__prompt_template_details_json')
                )
                .order_by('-updated_ts')
                .values('mapping_uuid', 'prompt_template_uuid', 'prompt_category_uuid', 'prompt_template_details_json', 'description', 'prompt_template_name', 'prompt_category_name','inserted_ts')).first()

    # Delete the prompt_template_customer_application_mapping by mapping_uuid
    def delete_mapping_by_template_uuid(self, prompt_template_uuid):
        """
            Deletes the prompt_template_customer_application_mapping using prompt_template_uuid
            :param : prompt_template_uuid whose mappings need to be deleted
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return PromptTemplateCustomerApplicationMapping.objects.filter(prompt_template_uuid=prompt_template_uuid).delete()

    # Get the count of the prompt_template_customer_application_mappings with the provided prompt_template_name
    def get_mapping_by_template_name(self, prompt_template_name,customer_uuid,application_uuid,exclude_uuid):
        """
            Gets the count of prompt_template_customer_application_mappings with given name
            :param : prompt_template_name : prompt_template_name whose template mappings need to be fetched
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        if exclude_uuid is None:
            return PromptTemplateCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid, prompt_template_uuid__prompt_template_name__iexact=prompt_template_name).count()
        else:
            return PromptTemplateCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid, prompt_template_uuid__prompt_template_name__iexact=prompt_template_name).exclude(prompt_template_uuid=exclude_uuid).count()
