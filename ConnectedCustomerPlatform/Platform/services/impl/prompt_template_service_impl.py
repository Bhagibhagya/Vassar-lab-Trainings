import inspect
import uuid
from dataclasses import asdict

from DatabaseApp.models import PromptTemplateCustomerApplicationMapping, PromptTemplate, PromptCategory, Customers, Applications
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from Platform.dao.impl.prompt_dao_impl import PromptDaoImpl
from Platform.dao.impl.prompt_template_customer_application_mapping_dao_impl import PromptTemplateCustomerApplicationMappingDaoImpl
from Platform.dao.impl.prompt_template_dao_impl import PromptTemplateDaoImpl
from Platform.services.interface.prompt_template_service_interface import IPromptTemplateService
from django.db import transaction
from Platform.dataclass import PromptTemplateDetailsJson
import logging
logger = logging.getLogger(__name__)

from datetime import datetime
import pytz

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
class PromptTemplateServiceImpl(IPromptTemplateService):
    """
        Prompt Template Service for managing Prompt, providing methods to add, edit,
        delete, and retrieve.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the PromptTemplateServiceImpl is created.
            Args:
                cls: The class reference.
                *args: Positional arguments for initialization.
                **kwargs: Keyword arguments for initialization.
            Returns:
                PromptTemplateServiceImpl: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(PromptTemplateServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
            Initialize the PromptTemplateServiceImpl.
            This method is called only once due to the singleton pattern. It initializes the
            PromptTemplateServiceImpl for handling business logic related to Prompts.
            Args:
                **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside PromptTemplateServiceImpl - Singleton Instance ID: {id(self)}")
            self.prompt_template_dao = PromptTemplateDaoImpl()
            self.prompt_dao = PromptDaoImpl()
            self.prompt_template_cust_app_mapping_dao = PromptTemplateCustomerApplicationMappingDaoImpl()
            self.initialized = True

    # create a new prompt_template instance.
    def create_prompt_template(self, customer_uuid, application_uuid, user_uuid, prompt_template):
        """
            Add a new Prompt Template to the database.
            :param customer_uuid: UUID of the customer to which the prompt template belongs.
            :param application_uuid: UUID of the application to which the prompt template belongs.
            :param user_uuid: UUID of the user adding the prompt.
            :param prompt_template: The prompt template data provided by the user.
            :raises CustomException: If Prompt Template already exists or any other database exceptions.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template Service :: time before add_prompt_template service :: {format_indian_time(start_time)}\n")

        # creating a tuple with all headers
        uuid_data = (customer_uuid, application_uuid, user_uuid)

        prompt_template_data_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template Service :: time before initializing data :: {format_indian_time(prompt_template_data_start_time)}\n")

        prompt_template_name = prompt_template.get('prompt_template_name')
        prompt_category_uuid = prompt_template.get('prompt_category_uuid')
        prompt_template_description = prompt_template.get('prompt_template_description')
        prompt_template_details_json = prompt_template.get('prompt_template_details_json')
        # Validate the prompt_template_details_json using dataclass
        prompt_template_details_dict = asdict(PromptTemplateDetailsJson(**prompt_template_details_json))
        prompt_template_data_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Template Service :: time after initializing data :: {format_indian_time(prompt_template_data_end_time)}\n")
        logger.info(f"\nTime profile :: Add Prompt Template :: Total time taken to initializing data :: {((prompt_template_data_end_time - prompt_template_data_start_time).total_seconds() * 1000):.4f}\n")


        try :
            with transaction.atomic():
                # Check prompt_template exists or not
                logger.info("Checking for existing prompt_template count")
                existing_prompt_template_mapping_count_start_time = datetime.now()
                logger.info(f"\nTime profile :: Add Prompt Template Service :: time before getting the existing_prompt_template_mapping_count  :: {format_indian_time(existing_prompt_template_mapping_count_start_time)}\n")

                existing_prompt_template_mapping_count = self.prompt_template_cust_app_mapping_dao.get_mapping_by_template_name(prompt_template_name,customer_uuid,application_uuid,None)
                existing_prompt_template_mapping_count_end_time = datetime.now()
                logger.info(f"\nTime profile :: Add Prompt Template Service :: time after getting the existing_prompt_template_mapping_count  :: {format_indian_time(existing_prompt_template_mapping_count_end_time)}\n")
                logger.info(f"\nTime profile :: Add Prompt Template :: Total time taken to get the existing_prompt_template_mapping_count :: {((existing_prompt_template_mapping_count_end_time - existing_prompt_template_mapping_count_start_time).total_seconds() * 1000):.4f}\n")

                if existing_prompt_template_mapping_count != 0:
                    logger.info("Existing prompt_template found")
                    raise CustomException(ErrorMessages.PROMPT_TEMPLATE_EXISTS)
                else:
                    logger.info("Prompt_template not found, creating the prompt_template and mapping")
                    # If prompt_template not exists , then create the prompt_template and map the customer to it
                    prompt_template_add_start_time = datetime.now()
                    logger.info(f"\nTime profile :: Add Prompt Template Service :: time before adding prompt_template into database  :: {format_indian_time(prompt_template_add_start_time)}\n")
                    prompt_template = self.__create_prompt_template(prompt_template_name,prompt_category_uuid,prompt_template_description,prompt_template_details_dict,user_uuid)
                    prompt_template_add_end_time = datetime.now()
                    logger.info(f"\nTime profile :: Add Prompt Template Service :: time after adding prompt_template into database  :: {format_indian_time(prompt_template_add_end_time)}\n")
                    logger.info(f"\nTime profile :: Add Prompt Template Service:: Total time taken to adding the prompt_template into database :: {((prompt_template_add_end_time - prompt_template_add_start_time).total_seconds() * 1000):.4f}\n")
                    prompt_template_mapping_add_start_time = datetime.now()
                    logger.info(f"\nTime profile :: Add Prompt Template Service :: time before adding prompt_template_customer_application_mapping into database  :: {format_indian_time(prompt_template_mapping_add_start_time)}\n")
                    self.__create_prompt_template_customer_application_mapping(prompt_template.prompt_template_uuid, uuid_data)
                    prompt_template_mapping_add_end_time = datetime.now()
                    logger.info(f"\nTime profile :: Add Prompt Template Service :: time after adding prompt_template_customer_application_mapping into database  :: {format_indian_time(prompt_template_mapping_add_end_time)}\n")
                    logger.info(f"\nTime profile :: Add Prompt Template Service:: Total time taken to adding prompt_template_customer_application_mapping into database :: {((prompt_template_mapping_add_end_time - prompt_template_mapping_add_start_time).total_seconds() * 1000):.4f}\n")

        except CustomException as e:
            # If it's already a CustomException, re-raise it
            raise e
        except Exception as e:
            logger.error("Failed to create prompt_template %s",str(e))
            # For any other exception, raise a CustomException with the appropriate message
            raise CustomException(ErrorMessages.FAILED_TO_CREATE_PROMPT_TEMPLATE)
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Add Prompt Template Service execution: {total_time:.4f} ms")

    # Update the existing prompt_template record in the database.
    def update_prompt_template(self, customer_uuid, application_uuid, user_uuid, prompt_template):
        """
            Update a Prompt Template in the database.
            :param customer_uuid: UUID of the customer to which the prompt template belongs.
            :param application_uuid: UUID of the application to which the prompt template belongs.
            :param user_uuid: UUID of the user adding the prompt template.
            :param prompt_template: The prompt template data provided by the user.
            :raises CustomException: If Prompt Template already exists or any other database errors.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        prompt_template_uuid = prompt_template.get('prompt_template_uuid')
        prompt_template_name = prompt_template.get('prompt_template_name')
        prompt_category_uuid = prompt_template.get('prompt_category_uuid')
        prompt_template_description = prompt_template.get('prompt_template_description')
        prompt_template_details_json = prompt_template.get('prompt_template_details_json')
        # Validate the prompt_template_details_json using dataclass
        prompt_template_details_dict = asdict(PromptTemplateDetailsJson(**prompt_template_details_json))
        existing_prompt_template_mapping_count = self.prompt_template_cust_app_mapping_dao.get_mapping_by_template_name(prompt_template_name, customer_uuid, application_uuid,prompt_template_uuid)
        if existing_prompt_template_mapping_count != 0:
            logger.info("Existing prompt_template found")
            raise CustomException(ErrorMessages.PROMPT_TEMPLATE_EXISTS)
        logger.info("Updating the prompt_template")
        updated_rows = self.prompt_template_dao.update_prompt_template(prompt_template_uuid,prompt_template_name,prompt_category_uuid,prompt_template_description,prompt_template_details_dict,user_uuid)

        if updated_rows == 0:
            raise CustomException(ErrorMessages.PROMPT_TEMPLATE_NOT_FOUND)

    # Removes the specified prompt_template_customer_application_mapping record from the database.
    def delete_prompt_template(self, prompt_template_uuid,user_uuid):
        """
            Delete the PromptTemplate in the database.
            :param prompt_template_uuid: UUID of the prompt_template.
            :raises CustomException: If PromptTemplate mapping not found.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        with transaction.atomic():
            # Check any prompts mapped to this prompt_template , if any prompts then we cannot allow to delete the prompt_template
            prompts_mapped_to_prompt_template = self.prompt_dao.get_prompt_count_mapped_to_prompt_template(prompt_template_uuid)
            if prompts_mapped_to_prompt_template !=0 :
                raise CustomException(ErrorMessages.PROMPT_TEMPLATE_CANNOT_BE_DELETED)
            # Delete prompt_template_customer_application_mapping
            self.prompt_template_cust_app_mapping_dao.delete_mapping_by_template_uuid(prompt_template_uuid)
            # Updating prompts under a specific prompt_template by removing the mapping to that prompt_template.
            deleted_rows = self.prompt_template_dao.delete_prompt_template(prompt_template_uuid,user_uuid)
            if deleted_rows == 0 :
                logger.error("Prompt_template not found")
                raise CustomException(ErrorMessages.PROMPT_TEMPLATE_NOT_FOUND)


    # Retrieves all the PromptTemplates for application
    def get_prompt_templates(self, customer_uuid, application_uuid,prompt_category_uuid):
        """
            Get the Prompt Templates from the database.
            :param customer_uuid: UUID of the customer to which the prompt_template belongs.
            :param application_uuid: UUID of the application to which the prompt_template belongs.
            :param prompt_category_uuid: UUID of the prompt_category to which the prompt_template belongs.
        """
        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt Templates Service :: time before get_prompt_templates :: {format_indian_time(start_time)}\n")

        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        prompt_template_get_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt Templates Service :: time before getting prompt_templates from database  :: {format_indian_time(prompt_template_get_start_time)}\n")
        templates =  self.prompt_template_cust_app_mapping_dao.get_mappings(customer_uuid,application_uuid,prompt_category_uuid)
        prompt_template_get_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt Templates Service :: time after getting prompt_templates from database  :: {format_indian_time(prompt_template_get_end_time)}\n")
        logger.info(f"\nTime profile :: Get Prompt Template Service:: Total time taken to get prompt_templates from database :: {((prompt_template_get_end_time - prompt_template_get_start_time).total_seconds() * 1000):.4f}\n")

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Prompt Templates Service execution: {total_time:.4f} ms")

        return templates

    # Retrieves the PromptTemplate by prompt_uuid
    def get_prompt_template_by_id(self, mapping_uuid):
        """
            Get the Prompt template by id from the database.
            :param mapping_uuid: UUID of the prompt template that need to be fetched.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        prompt_template = self.prompt_template_cust_app_mapping_dao.get_mapping_by_id(mapping_uuid)
        if prompt_template is None:
            raise CustomException(ErrorMessages.PROMPT_TEMPLATE_NOT_FOUND)
        return prompt_template

    # Retrieves all the PromptCategory
    def get_prompt_categories(self):
        """
            Get the Prompt categories from the database.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        return self.prompt_template_dao.get_prompt_categories()

    # Create prompt_template_customer_application_mapping in database
    def __create_prompt_template_customer_application_mapping(self, prompt_template_uuid,uuid_data):
        """This Method builds new PromptTemplateCustomerApplicationMapping and calls dao to create in the database."""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        customer_uuid, application_uuid, user_uuid = uuid_data

        # Build prompt_template_customer_application_mapping instance
        mapping = PromptTemplateCustomerApplicationMapping(
            mapping_uuid=str(uuid.uuid4()),
            prompt_template_uuid=PromptTemplate(prompt_template_uuid),
            customer_uuid=Customers(customer_uuid),
            application_uuid=Applications(application_uuid),
            created_by=user_uuid,
            updated_by=user_uuid,
        )

        # Call dao to add prompt_template_cust_app_mapping to db
        self.prompt_template_cust_app_mapping_dao.save_mapping(mapping)

    def __create_prompt_template(self, prompt_template_name,prompt_category_uuid,prompt_template_description,prompt_template_details_dict,user_uuid):
        """This Method builds new PromptTemplate and calls dao to create in the database."""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Build prompt_template instance
        prompt_template = PromptTemplate(
            prompt_template_uuid=str(uuid.uuid4()),
            prompt_template_name=prompt_template_name,
            description=prompt_template_description,
            prompt_template_details_json=prompt_template_details_dict,
            prompt_category_uuid=PromptCategory(prompt_category_uuid),
            is_default = False,
            created_by=user_uuid,
            updated_by=user_uuid,
        )

        # Call dao to add prompt_template_cust_app_mapping to db
        self.prompt_template_dao.save_prompt_template(prompt_template)
        return prompt_template
