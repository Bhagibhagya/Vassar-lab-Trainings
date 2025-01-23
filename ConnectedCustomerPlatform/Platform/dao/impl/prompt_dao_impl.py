import inspect
from django.db import IntegrityError

from django.db.models import Q,F

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import PromptCategory, Prompt
from Platform.constant.error_messages import ErrorMessages
from Platform.dao.interface.prompt_dao_interface import IPromptDao
import logging
from django.db import transaction
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)

class PromptDaoImpl(IPromptDao):
    """
        Dao for managing Prompt, providing methods to add, edit,
        delete, and retrieve.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(PromptDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of PromptDaoImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the PromptDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside PromptDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Queries the database for a prompt using the specified UUID.
    def get_prompt_by_uuid(self, prompt_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        return (Prompt.objects.filter(prompt_uuid=prompt_uuid, is_deleted=False).select_related('prompt_category_uuid')
                .annotate(prompt_category=F('prompt_category_uuid__prompt_category_name'))
                .values('prompt_uuid', 'prompt_name', 'prompt_category_uuid', 'prompt_category', 'prompt_details_json', 'inserted_ts').first())

    # Saves the Prompt instance to database.
    def save_prompt(self, prompt):
        """
            Saves the prompt instance to database
            :param prompt: instance of prompt
            :raises :raises any unique constraints or foreign key constraints
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        try:
            prompt.save()
        except IntegrityError as e:
            # Log the entire exception for debugging
            logger.error(f"Integrity error occurred: {str(e)}")

            # Foreign key constraint violation check
            if 'prompt_prompt_category_uuid_fkey' in str(e):
                logger.error(f"Prompt category not found for: {prompt.prompt_category_uuid}")
                raise CustomException(ErrorMessages.PROMPT_CATEGORY_NOT_FOUND)

            elif 'prompt_customer_uuid_fkey' in str(e):
                logger.error(f"Customer not found for: {prompt.customer_uuid}")
                raise CustomException(ErrorMessages.CUSTOMER_NOT_FOUND)

            elif 'prompt_application_uuid_fkey' in str(e):
                logger.error(f"Application not found for: {prompt.application_uuid}")
                raise CustomException(ErrorMessages.APPLICATION_NOT_FOUND)

            # Check for unique constraint violation
            elif 'unique constraint' in str(e) and 'prompt_name' in str(e):
                logger.error(f"Duplicate of Prompt found for: {prompt.prompt_name}")
                raise CustomException(ErrorMessages.PROMPT_EXISTS)

            # If the error doesn't match the above conditions, raise the generic exception
            else:
                raise e

    # Removes the prompt record from the database.
    def delete_prompt(self, prompt_uuid,user_uuid):
        """
            Deleting the prompt by making is_deleted column true
            :param prompt_uuid : uuid of the prompt to be deleted
            :param user_uuid:uuid of the user who deleting the prompt
            :return : count of effected rows
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Perform the delete operation by marking the prompt as deleted
        updated_rows = Prompt.objects.filter(
            prompt_uuid=prompt_uuid,
            is_deleted=False
        ).update(
            is_deleted=True,
            updated_ts=timezone.now(),
            updated_by=user_uuid
        )
        # Return the number of rows updated
        return updated_rows

    # Fetches all the prompts for customer-application
    def get_prompts(self, customer_uuid, application_uuid):
        """
            Fetches all the prompt under a customer and application
            :param customer_uuid : uuid of customer
            :param application_uuid : uuid of application
            :return : List of prompts under specified customer and application
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        return (Prompt.objects.filter(customer_uuid=customer_uuid,application_uuid=application_uuid,is_deleted=False)
                .select_related('prompt_category_uuid').order_by('-inserted_ts').annotate(prompt_category=F('prompt_category_uuid__prompt_category_name'))
                .values('prompt_uuid','prompt_name','prompt_category_uuid','prompt_details_json','inserted_ts','prompt_category'))

    # Get the count of prompts mapped to particular prompt_template
    def get_prompt_count_mapped_to_prompt_template(self, prompt_template_uuid):
        """
            Method to get the count of prompts mapped to prompt_template
            :param prompt_template_uuid : uuid of prompt_template that has been deleted.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        return Prompt.objects.filter(prompt_details_json__contains={'prompt_template_uuid': prompt_template_uuid},is_deleted=False).count()

    # Update the prompt
    def update_prompt(self,prompt_uuid,prompt_name,prompt_category_uuid,prompt_details_json_dict,user_uuid,customer_uuid,application_uuid):
        """
            Updates the prompt with provided data using prompt_uuid
            :return : No of rows updated
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        try:
            updated_rows = Prompt.objects.filter(prompt_uuid=prompt_uuid,is_deleted=False).update(prompt_name=prompt_name,
                                                                                   prompt_category_uuid=PromptCategory(prompt_category_uuid),
                                                                                   prompt_details_json=prompt_details_json_dict,
                                                                                   updated_ts=timezone.now(), updated_by=user_uuid)
            return updated_rows
        except IntegrityError as e:
            # Log the entire exception for debugging
            logger.error(f"Integrity error occurred: {str(e)}")

            # Foreign key constraint violation check
            if 'prompt_prompt_category_uuid_fkey' in str(e):
                logger.error(f"Prompt category not found for: {prompt_category_uuid}")
                raise CustomException(ErrorMessages.PROMPT_CATEGORY_NOT_FOUND)

            elif 'prompt_customer_uuid_fkey' in str(e):
                logger.error(f"Customer not found for: {customer_uuid}")
                raise CustomException(ErrorMessages.CUSTOMER_NOT_FOUND)

            elif 'prompt_application_uuid_fkey' in str(e):
                logger.error(f"Application not found for: {application_uuid}")
                raise CustomException(ErrorMessages.APPLICATION_NOT_FOUND)

            # Check for unique constraint violation
            elif 'unique constraint' in str(e) and 'prompt_name' in str(e):
                logger.error(f"Duplicate of Prompt found for: {prompt_name}")
                raise CustomException(ErrorMessages.PROMPT_EXISTS)

            # If the error doesn't match the above conditions, raise the exception
            else:
                raise e
