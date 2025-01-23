import inspect
import uuid
from dataclasses import asdict

import pandas as pd

from django.forms.models import model_to_dict
from DatabaseApp.models import Prompt, Customers, Applications, PromptCategory
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from Platform.dao.impl.prompt_dao_impl import PromptDaoImpl
from Platform.dao.impl.prompt_template_dao_impl import PromptTemplateDaoImpl
from Platform.services.interface.prompt_service_interface import IPromptService
from Platform.utils import get_customer_application_instances
from Platform.dataclass import PromptDetailsJson
from django.db import IntegrityError
from rest_framework import status

import logging
logger = logging.getLogger(__name__)

from datetime import datetime
import pytz

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class PromptServiceImpl(IPromptService):
    """
        Prompt Service for managing Prompt, providing methods to add, edit,
        delete, and retrieve.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the PromptServiceImpl is created.
            Args:
                cls: The class reference.
                *args: Positional arguments for initialization.
                **kwargs: Keyword arguments for initialization.
            Returns:
                PromptServiceImpl: The singleton instance of the Service.
        """
        if cls._instance is None:
            cls._instance = super(PromptServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
            Initialize the PromptServiceImpl.
            This method is called only once due to the singleton pattern. It initializes the
            PromptServiceImpl for handling business logic related to Prompts.
            Args:
                **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside PromptServiceImpl - Singleton Instance ID: {id(self)}")
            self.prompt_dao = PromptDaoImpl()
            self.prompt_template_dao = PromptTemplateDaoImpl()
            self.initialized = True

    # Inserts a new prompt record in the database.
    def create_prompt(self, customer_uuid, application_uuid, user_uuid, prompt):
        """
            Add a new Prompt to the database.
            :param customer_uuid: UUID of the customer to which the prompt belongs.
            :param application_uuid: UUID of the application to which the prompt belongs.
            :param user_uuid: UUID of the user adding the prompt.
            :param prompt: The prompt data provided by the user.
            :raises CustomException: If Prompt already exists or customer not found.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Service :: time before add_prompt service :: {format_indian_time(start_time)}\n")

        uuid_data = (customer_uuid, application_uuid, user_uuid)

        prompt_data_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Service :: time before initializing data :: {format_indian_time(prompt_data_start_time)}\n")

        prompt_name = prompt.get('prompt_name')
        prompt_category_uuid = prompt.get('prompt_category_uuid')
        prompt_details_json = prompt.get('prompt_details_json')
        # Validate the prompt_details_json using dataclass
        prompt_json_dict = asdict(PromptDetailsJson(**prompt_details_json))
        prompt_json_dict['SYSTEM'] = prompt_json_dict.pop('system_prompt')
        prompt_json_dict['CONTEXT'] = prompt_json_dict.pop('context_prompt')
        prompt_json_dict['DISPLAY'] = prompt_json_dict.pop('display_prompt')
        prompt_json_dict['REMEMBER'] = prompt_json_dict.pop('remember_prompt')

        prompt_data_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Service :: time after initializing data :: {format_indian_time(prompt_data_end_time)}\n")
        logger.info(
            f"\nTime profile :: Add Prompt :: Total time taken to initializing data :: {((prompt_data_end_time - prompt_data_start_time).total_seconds() * 1000):.4f}\n")

        prompt_instance_create_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Service :: time before creating prompt instance :: {format_indian_time(prompt_instance_create_start_time)}\n")

        # Create Prompt Instance
        prompt_instance = self.__create_prompt_instance(prompt_name,prompt_category_uuid,prompt_json_dict,uuid_data)

        prompt_instance_create_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Service :: time after creating prompt instance :: {format_indian_time(prompt_instance_create_end_time)}\n")
        logger.info(f"\nTime profile :: Add Prompt Template :: Total time taken to create prompt instance :: {((prompt_instance_create_end_time - prompt_instance_create_start_time).total_seconds() * 1000):.4f}\n")

        logger.info("Prompt instance created saving to database")
        prompt_save_dao_start_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Service :: time before saving prompt instance :: {format_indian_time(prompt_save_dao_start_time)}\n")
        # Call dao to add prompt to db
        self.prompt_dao.save_prompt(prompt_instance)
        prompt_save_dao_end_time = datetime.now()
        logger.info(f"\nTime profile :: Add Prompt Service :: time after saving prompt instance :: {format_indian_time(prompt_save_dao_end_time)}\n")
        logger.info(
            f"\nTime profile :: Add Prompt Template :: Total time taken to save prompt instance :: {((prompt_save_dao_end_time - prompt_save_dao_start_time).total_seconds() * 1000):.4f}\n")

        logger.info("Prompt saved to database successfully")
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Add Prompt Service execution: {total_time:.4f} ms")

    # Update the existing prompt record in the database.
    def update_prompt(self, customer_uuid, application_uuid, user_uuid, prompt):
        """
            Update a Prompt in the database.
            :param customer_uuid: UUID of the customer to which the prompt belongs.
            :param application_uuid: UUID of the application to which the prompt belongs.
            :param user_uuid: UUID of the user adding the prompt.
            :param prompt: The prompt data provided by the user.
            :raises CustomException: If Prompt already exists or customer not found.
        """
        start_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt Service :: time before update_prompt service :: {format_indian_time(start_time)}\n")

        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        prompt_data_start_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt Service :: time before initializing data :: {format_indian_time(prompt_data_start_time)}\n")

        prompt_uuid = prompt.get('prompt_uuid')
        prompt_name = prompt.get('prompt_name')
        prompt_category_uuid = prompt.get('prompt_category_uuid')
        prompt_details_json = prompt.get('prompt_details_json')
        # Validate the prompt_details_json using dataclass
        prompt_details_json_dict = asdict(PromptDetailsJson(**prompt_details_json))
        prompt_details_json_dict['SYSTEM'] = prompt_details_json_dict.pop('system_prompt')
        prompt_details_json_dict['CONTEXT'] = prompt_details_json_dict.pop('context_prompt')
        prompt_details_json_dict['DISPLAY'] = prompt_details_json_dict.pop('display_prompt')
        prompt_details_json_dict['REMEMBER'] = prompt_details_json_dict.pop('remember_prompt')
        logger.debug("Prompt json dict::", prompt_details_json_dict)

        prompt_data_end_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt Service :: time after initializing data :: {format_indian_time(prompt_data_end_time)}\n")
        logger.info(
            f"\nTime profile :: Update Prompt :: Total time taken to initializing data :: {((prompt_data_end_time - prompt_data_start_time).total_seconds() * 1000):.4f}\n")

        # update the prompt
        logger.info("Calling dao to update the prompt")
        prompt_save_dao_start_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt Service :: time before updating prompt in dao :: {format_indian_time(prompt_save_dao_start_time)}\n")

        updated_rows = self.prompt_dao.update_prompt(prompt_uuid, prompt_name, prompt_category_uuid,
                                                     prompt_details_json_dict, user_uuid, customer_uuid,
                                                     application_uuid)

        prompt_save_dao_end_time = datetime.now()
        logger.info(f"\nTime profile :: Update Prompt Service :: time after updating prompt in dao :: {format_indian_time(prompt_save_dao_end_time)}\n")
        logger.info(
            f"\nTime profile :: Update Prompt Template :: Total time taken to update prompt in dao :: {((prompt_save_dao_end_time - prompt_save_dao_start_time).total_seconds() * 1000):.4f}\n")

        if updated_rows == 0:
            logger.info("Prompt not found with uuid :: %s", prompt_uuid)
            raise CustomException(ErrorMessages.PROMPT_NOT_FOUND)

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Update Prompt Service execution: {total_time:.4f} ms")

    # Removes the specified prompt record from the database.
    def delete_prompt(self, prompt_uuid, user_uuid):
        """
            Delete the Prompt in the database.
            :param prompt_uuid: UUID of the prompt.
            :param user_uuid: UUID of the user.
            :raises CustomException: If Prompt not found.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        updated_rows = self.prompt_dao.delete_prompt(prompt_uuid, user_uuid)
        logger.info(f"delete_prompt :: Rows updated after delete operation: {updated_rows}")
        # Check if any rows were updated, otherwise raise exception
        if updated_rows == 0:
            logger.error(f"delete_prompt :: Prompt not found: {prompt_uuid}")
            raise CustomException(ErrorMessages.PROMPT_NOT_FOUND)

    # Retrieves all the Prompts for application
    def get_prompts(self, customer_uuid, application_uuid):
        """
            Get the Prompts from the database.
            :param customer_uuid: UUID of the customer to which the prompt belongs.
            :param application_uuid: UUID of the application to which the prompt belongs.
        """
        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts Service :: time before get_prompts service :: {format_indian_time(start_time)}\n")

        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        get_prompts_dao_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts Service :: time before getting prompts from dao :: {format_indian_time(get_prompts_dao_start_time)}\n")

        # Get the Prompts from database
        prompts = self.prompt_dao.get_prompts(customer_uuid, application_uuid)

        get_prompts_dao_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts Service :: time after getting prompts from dao :: {format_indian_time(get_prompts_dao_end_time)}\n")
        logger.info(
            f"\nTime profile :: Get Prompts Service :: Total time taken to get prompts from dao :: {((get_prompts_dao_end_time - get_prompts_dao_start_time).total_seconds() * 1000):.4f}\n")

        if not prompts.exists():
            return []
        result = []
        prompt_templates_dict = {}
        get_prompt_template_dao_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts Service :: time before getting prompt templates from dao :: {format_indian_time(get_prompt_template_dao_start_time)}\n")

        prompt_templates = self.prompt_template_dao.get_prompt_templates()

        get_prompt_template_dao_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts Service :: time after getting prompts from dao :: {format_indian_time(get_prompt_template_dao_end_time)}\n")
        logger.info(
            f"\nTime profile :: Get Prompts :: Total time taken to get prompts from dao :: {((get_prompt_template_dao_end_time - get_prompt_template_dao_start_time).total_seconds() * 1000):.4f}\n")

        if prompt_templates.exists():
            prompt_template_dataframe_start_time = datetime.now()
            logger.info(f"\nTime profile :: Get Prompts Service :: time before converting prompt templates to dataframe :: {format_indian_time(prompt_template_dataframe_start_time)}\n")
            prompt_templates_dict = pd.DataFrame(prompt_templates).set_index('prompt_template_uuid').to_dict('index')
            prompt_template_dataframe_end_time = datetime.now()
            logger.info(f"\nTime profile :: Get Prompts Service :: time after converting prompt templates to dataframe :: {format_indian_time(prompt_template_dataframe_end_time)}\n")
            logger.info(f"\nTime profile :: Get Prompts :: Total time taken to converting prompt templates to dataframe :: {((prompt_template_dataframe_end_time - prompt_template_dataframe_start_time).total_seconds() * 1000):.4f}\n")

        prompts_process_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts Service :: time before processing prompts :: {format_indian_time(prompts_process_start_time)}\n")

        # Include the necessary fields to prompt objects
        for prompt in prompts:
            prompt_dict = self.__get_necessary_fields(prompt, prompt_templates_dict)
            result.append(prompt_dict)
        prompts_process_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompts Service :: time after processing prompts :: {format_indian_time(prompts_process_end_time)}\n")
        logger.info(f"\nTime profile :: Get Prompts :: Total time taken to process prompt :: {((prompts_process_end_time - prompts_process_start_time).total_seconds() * 1000):.4f}\n")

        logger.info("Returning prompts :: no of prompts :: %d", len(result))
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Prompts Service execution: {total_time:.4f} ms")

        return result

    # Retrieves the Prompt by prompt_uuid
    def get_prompt_by_id(self, prompt_uuid):
        """
            Get the Prompt by id from the database.
            :param prompt_uuid: UUID of the prompt that need to be fetched.
        """

        start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt By Id Service :: time before get_prompt_by_id service :: {format_indian_time(start_time)}\n")

        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        get_prompt_dao_start_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt By Id Service :: time before getting prompt from dao :: {format_indian_time(get_prompt_dao_start_time)}\n")

        # Get the Prompt from database by uuid
        prompt = self.prompt_dao.get_prompt_by_uuid(prompt_uuid)

        get_prompt_dao_end_time = datetime.now()
        logger.info(f"\nTime profile :: Get Prompt By Id Service :: time after getting prompt from dao :: {format_indian_time(get_prompt_dao_end_time)}\n")
        logger.info(f"\nTime profile :: Get Prompt BY Id Service :: Total time taken to get prompts from dao :: {((get_prompt_dao_end_time - get_prompt_dao_start_time).total_seconds() * 1000):.4f}\n")

        if prompt is None:
            raise CustomException(ErrorMessages.PROMPT_NOT_FOUND)
        prompt_templates_dict = {}
        prompt_templates = self.prompt_template_dao.get_prompt_templates()
        if prompt_templates.exists():
            prompt_templates_dict = pd.DataFrame(prompt_templates).set_index('prompt_template_uuid').to_dict('index')

        prompt_dict = self.__get_necessary_fields(prompt, prompt_templates_dict)
        logger.info("Returning the prompt")
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Prompt By Id Service execution: {total_time:.4f} ms")

        return prompt_dict

    # Method to create the Prompt instance
    def __create_prompt_instance(self, prompt_name, prompt_category_uuid, prompt_json_dict, uuid_data):
        """This Method builds new prompt instance."""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        customer_uuid, application_uuid, user_uuid = uuid_data
        # Build Prompt instance
        prompt = Prompt(
            prompt_uuid=str(uuid.uuid4()),
            prompt_name=prompt_name,
            prompt_category_uuid=PromptCategory(prompt_category_uuid),
            prompt_details_json=prompt_json_dict,
            customer_uuid=Customers(customer_uuid),
            application_uuid=Applications(application_uuid),
            created_by=user_uuid,
            updated_by=user_uuid,
        )
        return prompt


    # Method to add necessary fields to prompt object
    def __get_necessary_fields(self, prompt, prompt_templates_dict):
        """This Method adds the necessary fields to prompt object"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        prompt_dict = {key: value for key, value in prompt.items()}
        prompt_details_dict = prompt_dict['prompt_details_json']
        if prompt_details_dict is not None:
            prompt_details_dict['system_prompt'] = prompt_details_dict.pop('SYSTEM',None)
            prompt_details_dict['context_prompt'] = prompt_details_dict.pop('CONTEXT',None)
            prompt_details_dict['display_prompt'] = prompt_details_dict.pop('DISPLAY',None)
            prompt_details_dict['remember_prompt'] = prompt_details_dict.pop('REMEMBER',None)
            prompt_template_uuid = prompt_details_dict.get('prompt_template_uuid')
            if prompt_template_uuid is not None:
                prompt_template = prompt_templates_dict.get(prompt_template_uuid)
                if prompt_template is not None:
                    prompt_dict['prompt_template_name'] = prompt_template.get('prompt_template_name')
        return prompt_dict