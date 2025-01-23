import inspect
from django.db import IntegrityError
from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import PromptTemplate, PromptCategory
from Platform.constant.error_messages import ErrorMessages
from Platform.dao.interface.prompt_template_dao_interface import IPromptTemplateDao
import logging
from django.utils import timezone
logger = logging.getLogger(__name__)

class PromptTemplateDaoImpl(IPromptTemplateDao):
    """
        Dao for Prompt template, providing methods to add, edit,
        delete, and retrieve.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(PromptTemplateDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of PromptDaoImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the PromptDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside PromptTemplateDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Save prompt_template.
    def save_prompt_template(self, prompt_template):
        """
            This method creates new row in the database with provided prompt_template instance
            :param prompt_template: prompt_template instance
            :raises: raises any exception while inserting into database
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        try:
            prompt_template.save()
        except IntegrityError as e:
            if 'prompt_template_prompt_category_uuid_fkey' in str(e):
                logger.error(f"Prompt category not found for: {prompt_template.prompt_category_uuid}")
                raise CustomException(ErrorMessages.PROMPT_CATEGORY_NOT_FOUND)
            # If the error doesn't match the above conditions, raise the exception
            raise e

    # Update the prompt_template
    def update_prompt_template(self, prompt_template_uuid, prompt_template_name, prompt_category_uuid, prompt_template_description, prompt_template_details_dict, user_uuid):
        """
            This method updates the existing record of prompt_template using prompt_template_uuid
            :return : Updated rows count
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        try :
            updated_rows = (PromptTemplate.objects.filter(prompt_template_uuid=prompt_template_uuid, is_deleted=False)
                        .update(prompt_template_name=prompt_template_name, description=prompt_template_description,
                                prompt_template_details_json=prompt_template_details_dict, prompt_category_uuid=PromptCategory(prompt_category_uuid),
                                updated_ts=timezone.now(), updated_by=user_uuid))
        except IntegrityError as e:
            if 'prompt_template_prompt_category_uuid_fkey' in str(e):
                logger.error(f"Prompt category not found for: {prompt_category_uuid}")
                raise CustomException(ErrorMessages.PROMPT_CATEGORY_NOT_FOUND)
            # If the error doesn't match the above conditions, raise exception
            raise e
        logger.info("Number of rows updated %d",updated_rows)
        return updated_rows


    # Fetches all the prompt_templates
    def get_prompt_templates(self):
        """
            Fetches all the prompt_templates
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        return PromptTemplate.objects.filter(is_deleted=False).values('prompt_template_uuid','prompt_template_name')

    # Delete the prompt_template
    def delete_prompt_template(self,prompt_template_uuid,user_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        updated_rows = PromptTemplate.objects.filter(prompt_template_uuid=prompt_template_uuid,is_deleted=False).update(is_deleted=True,updated_ts=timezone.now(), updated_by=user_uuid)
        return updated_rows

    # Fetches all the prompt_categories
    def get_prompt_categories(self):
        """
            Fetches all the prompt_category meta data
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        return PromptCategory.objects.filter().order_by('prompt_category_name').values('prompt_category_uuid', 'prompt_category_name')
