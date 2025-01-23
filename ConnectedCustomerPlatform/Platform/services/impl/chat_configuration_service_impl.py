import inspect
import json
import logging

from datetime import datetime

import pytz
from django.db import transaction
from pydantic import ValidationError

from rest_framework import status

from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException, \
    InvalidValueProvidedException

from Platform.constant.error_messages import ErrorMessages
from Platform.constant.success_messages import SuccessMessages
from Platform.dao.impl.chat_configuration_dao_impl import ChatConfigurationDAOImpl
from Platform.dao.impl.chat_configuration_mapping_dao_impl import ChatConfigurationMappingDAOImpl

from Platform.dataclass import IntentPageData, LandingPageData
from Platform.serializers import  ValidateChatConfigurationSerializer
from Platform.constant import constants
from Platform.constant.constants import ChatConfiguration

from Platform.services.interface.chat_configuration_service_interface import IChatConfigurationService
from Platform.utils import  get_current_timestamp


logger = logging.getLogger(__name__)

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class ChatConfigurationServiceImpl(IChatConfigurationService):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatConfigurationServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside ChatConfigurationServiceImpl")
            self.chat_configuration_dao = ChatConfigurationDAOImpl()
            self.chat_configuration_mapping_dao = ChatConfigurationMappingDAOImpl()
            print(f"Inside ChatConfigurationServiceImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True


    def get_all_chat_configurations(self,application_uuid, customer_uuid, chat_configuration_type):
        """
        Retrieves and processes chat configurations based on application and customer UUIDs.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        fetch_start_time = datetime.now()
        logger.info(
            f"\nTime profile :: Get All Chat Configurations :: time before chat_configuration_dao call :: {format_indian_time(fetch_start_time)}\n")
        # Step 1: Fetch chat configurations
        chat_configurations = self.chat_configuration_dao.get_all_chat_configurations(application_uuid, customer_uuid,chat_configuration_type)
        fetch_end_time = datetime.now()
        logger.info(
            f"\nTime profile :: Get All Chat Configurations :: time after chat_configuration_dao call :: {format_indian_time(fetch_end_time)}\n")
        logger.info(
            f"\nTime profile :: Get All Chat Configurations :: Total time taken for fetching configurations :: {((fetch_end_time - fetch_start_time).total_seconds() * 1000):.4f} ms\n")

        logger.info(
            f"Retrieved {len(chat_configurations)} chat configurations for application_uuid {application_uuid} and customer_uuid {customer_uuid}")
        pre_created_theme = []
        other_themes = []
        all_statuses_false = True
        default_theme = None
        # Step 2: Process configurations
        process_start_time = datetime.now()
        logger.info(
            f"\nTime profile :: Get All Chat Configurations :: time before processing configurations :: {format_indian_time(process_start_time)}\n")
        for data in chat_configurations:
            pre_created = data.get('pre_created',False)
            mapping_status = data.get('status') or False
            all_statuses_false &= not mapping_status  # Track if all mapping statuses are False
            item = {
                "chat_configuration_uuid": data.get("chat_configuration_uuid",""),
                "chat_configuration_name": data.get("chat_configuration_name",""),
                "status": mapping_status,
                "read_only": pre_created
            }
            chat_details_json = data.get("chat_details_json", {})
            chat_details_json = json.loads(chat_details_json)
            # Extract the appropriate configuration based on the type (landing page or intent page)
            configuration = (chat_details_json.get("landing_page_configuration", {})
                             .get("home_screen_configuration", {})
                             if chat_configuration_type == "landing_page"
                             else chat_details_json.get("intent_page_configuration", {})
                             .get("intent_page_panel_configuration", {}).get("header", {}))

            item["background_fill_type"] = configuration.get("background_fill_type","")
            item["background_color"] = configuration.get("background_color","")
            # Append the item to the appropriate list (pre-created or other themes)
            if pre_created:
                pre_created_theme.append(item)
                if data.get('is_default', False):
                    default_theme = item
            else:
                other_themes.append(item)
        process_end_time = datetime.now()
        logger.info(
            f"\nTime profile :: Get All Chat Configurations :: time after processing configurations :: {format_indian_time(process_end_time)}\n")
        logger.info(
            f"\nTime profile :: Get All Chat Configurations :: Total time taken for processing configurations :: {((process_end_time - process_start_time).total_seconds() * 1000):.4f} ms\n")

        if all_statuses_false and default_theme:
            logger.debug(f"Set default theme {default_theme['chat_configuration_uuid']} as active (status=True)")
            default_theme["status"] = True
        #join both default and manually created themes
        template_data = pre_created_theme + other_themes
        end_time = datetime.now()
        total_time = (end_time - fetch_start_time).total_seconds() * 1000
        logger.info(
            f"After Execution::Total time taken for Get All Chat Configurations API execution: {total_time:.4f} ms")
        return template_data


    def delete_chat_configuration(self,chat_configuration_uuid,customer_uuid, application_uuid):
        """
            Deletes chat configurations based on configuration UUID for a particular customer and application.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Check if a mapping exists between the chat configuration UUID, customer UUID, and application UUID.
        if not self.chat_configuration_mapping_dao.check_mapping_exists(chat_configuration_uuid, customer_uuid, application_uuid):
            raise InvalidValueProvidedException(ErrorMessages.CHAT_CONFIGURATION_MAPPING_NOT_FOUND)
        logger.info(f"Deleting chat configuration for customer {customer_uuid}, application {application_uuid}, and chat_configuration_uuid {chat_configuration_uuid}")
        deleted, _ = self.chat_configuration_dao.delete_configuration_by_uuid(chat_configuration_uuid)
        if deleted == 0:
            logger.error("Unable to delete chat configuration.")
            raise CustomException(ErrorMessages.UNABLE_TO_DELETE_TEMPLATE)
        logger.info("Chat configuration deleted successfully.")

    def get_active_chat_configurations(self, application_uuid, customer_uuid):
        """
           Function to get active chat configurations specific to application and customer.
           It retrieves active configurations from the database and includes default templates
            when there are no active configurations
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        configurations = self.chat_configuration_dao.get_active_configurations(application_uuid, customer_uuid)
        active_configurations = {}
        if len(configurations)>0:
            logger.info(f"length of retrieved configurations from mapping table: {len(configurations)}")
            for configuration in configurations:
                active_configurations.update(configuration["chat_details_json"])

            # If there is only one active configuration, attempt to fetch the opposite configuration type
            if len(configurations) == 1:
                config_type = configurations[0].get("chat_configuration_type")
                logger.info(f"custom active configuration:{config_type}")
                opposite_type = ChatConfiguration.CONFIG_TYPE_MAPPING.get(config_type, "")
                default_template = self.chat_configuration_dao.get_default_template_by_type(opposite_type)
                if default_template:
                    logger.debug(f"Adding single default template of {opposite_type}")
                    active_configurations.update(default_template.get("chat_details_json"))
        else:
            # If no configurations were retrieved, get default templates from the database
            default_templates = self.chat_configuration_dao.get_default_templates()
            logger.debug("Adding both default templates")
            for template in default_templates:
                active_configurations.update(template.get("chat_details_json"))

        result = {"chat_details_json": active_configurations}
        return result

    @transaction.atomic
    def update_activation_status(self,chat_configuration_uuid,application_uuid, customer_uuid ,user_id):
        """
            Function to make a configuration active.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        try:
            # Retrieve the chat configuration using the provided UUID
            configuration = self.chat_configuration_dao.get_configuration_by_uuid(chat_configuration_uuid)
            if configuration:
                # Get or create the mapping for a specific application and customer
                mapping, created = self.chat_configuration_mapping_dao.get_or_create_mapping_by_publishing(configuration,application_uuid,customer_uuid,user_id)
                if not created:
                    self.chat_configuration_mapping_dao.update_mapping_status(mapping, True , user_id)
                self.chat_configuration_mapping_dao.deactivate_other_configurations(application_uuid, customer_uuid, configuration.chat_configuration_type,
                                                                     chat_configuration_uuid,user_id)
                logger.info(SuccessMessages.CHAT_CONFIGURATION_STATUS_UPDATED_SUCCESSFULLY,
                            f"for uuid :{chat_configuration_uuid}")
                return SuccessMessages.CHAT_CONFIGURATION_STATUS_UPDATED_SUCCESSFULLY

            else:
                raise CustomException(ErrorMessages.SAVE_CONFIGURATION_BEFORE_PUBLISHING,
                                      status_code=status.HTTP_400_BAD_REQUEST)

        except CustomException as ce:
            logger.error("Custom exception occurred: %s", str(ce))
            raise ce

        except Exception as e:
            logger.error("Error updating activation status: %s", str(e))
            raise CustomException(ErrorMessages.CANNOT_UPDATE_ACTIVATION_STATUS)

    def get_chat_configuration(self, chat_configuration_uuid, customer_uuid, application_uuid):
        """
            Get configuration based on configuration uuid.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        start_time = datetime.now()
        logger.info(
            f"Time profile :: Get Chat Configuration :: time before get_configuration_by_uuid call :: {format_indian_time(start_time)}\n")

        # Step 1: Fetch chat configuration by UUID
        fetch_start_time = datetime.now()
        configuration = self.chat_configuration_dao.get_configuration_by_uuid(chat_configuration_uuid)
        fetch_end_time = datetime.now()
        logger.info(
            f"Time profile :: Get Chat Configuration :: time after get_configuration_by_uuid call :: {format_indian_time(fetch_end_time)}\n")
        logger.info(
            f"Time profile :: Get Chat Configuration :: Total time taken for get_configuration_by_uuid :: {((fetch_end_time - fetch_start_time).total_seconds() * 1000):.4f} ms\n")

        if not configuration:
            raise ResourceNotFoundException(ErrorMessages.CHAT_CONFIGURATION_NOT_FOUND)
        json_extract_start_time = datetime.now()
        chat_configuration_json = configuration.chat_details_json
        json_extract_end_time = datetime.now()
        logger.info(
            f"Time profile :: Get Chat Configuration :: time after extracting chat_details_json :: {format_indian_time(json_extract_end_time)}\n")
        logger.info(
            f"Time profile :: Get Chat Configuration :: Total time taken for extracting chat_details_json :: {((json_extract_end_time - json_extract_start_time).total_seconds() * 1000):.4f} ms\n")

        build_start_time = datetime.now()
        configuration_data = self.__build_configuration_object(configuration, chat_configuration_json)
        build_end_time = datetime.now()
        logger.info(
            f"Time profile :: Get Chat Configuration :: time after building configuration object :: {format_indian_time(build_end_time)}\n")
        logger.info(
            f"Time profile :: Get Chat Configuration :: Total time taken for building configuration object :: {((build_end_time - build_start_time).total_seconds() * 1000):.4f} ms\n")
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"After Execution::Total time taken for Get Chat Configuration API execution: {total_time:.4f} ms")

        return configuration_data


    def __build_configuration_object(self, configuration, chat_configuration_json):
        """Helper function to build the response object"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        return {
            'chat_configuration_uuid': getattr(configuration, 'chat_configuration_uuid', None),
            'chat_configuration_name': getattr(configuration, 'chat_configuration_name', None),
            'description': getattr(configuration, 'description', None),
            'chat_details_json': chat_configuration_json if chat_configuration_json else None,
            'chat_configuration_provider': getattr(configuration, 'chat_configuration_provider', None),
            'code': getattr(configuration, 'code', None),
            'insert_ts': getattr(configuration, 'inserted_ts', None),
            'updated_ts': getattr(configuration, 'updated_ts', None),
            'created_by': getattr(configuration, 'created_by', None),
            'updated_by': getattr(configuration, 'updated_by', None),
            'chat_configuration_type': getattr(configuration, 'chat_configuration_type', None),
            'is_default': getattr(configuration, 'is_default', False),
            'pre_created': getattr(configuration, 'pre_created', False),
        }


    def create_or_update_chat_configuration(self,data, application_uuid, customer_uuid, user_id):
        """Main method to update the chat configuration."""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        start_time = datetime.now()
        logger.info(f"Time profile :: Start :: {format_indian_time(start_time)}")
        chat_configuration_uuid = data.get('chat_configuration_uuid')
        logger.info(f"Time profile :: Before get configuration :: {format_indian_time(datetime.now())}")
        instance = self.chat_configuration_dao.get_configuration_by_uuid(chat_configuration_uuid) if chat_configuration_uuid else None
        logger.info(f"Time profile :: After get configuration :: {format_indian_time(datetime.now())}")
        # If the instance does not exist,create a new configuration
        if instance is None:
            serializer = ValidateChatConfigurationSerializer(data=data)
            if not serializer.is_valid():
                raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
            logger.info(f"Time profile :: Before template and name count :: {format_indian_time(datetime.now())}")

            template_count, name_count = self.chat_configuration_dao.get_configuration_templates_and_name_count(
                application_uuid, customer_uuid,
                data.get("chat_configuration_type"), data.get("chat_configuration_name"),data.get("chat_configuration_provider")
            )
            logger.info(f"Time profile :: After template and name count :: {format_indian_time(datetime.now())}")
            if template_count >= 5:
                raise CustomException(
                    ErrorMessages.MAXIMUM_TEMPLATE_LIMIT_REACHED,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if name_count != 0:
                raise CustomException(ErrorMessages.CHAT_CONFIGURATION_NAME_NOT_DUPLICATED)
            logger.info(f"Time profile :: Before processing configuration :: {format_indian_time(datetime.now())}")
            chat_configuration_data = self.process_web_configuration(data)
            logger.info(f"Time profile :: Before creating new configuration :: {format_indian_time(datetime.now())}")
            #creating new configuration and mapping
            instance = self.chat_configuration_dao.create_configuration(data,application_uuid, customer_uuid, user_id,chat_configuration_data)
            logger.debug(f"creating new configuration:{instance.chat_configuration_uuid} and mapping")
        else:
            # Update the instance with new data
            logger.debug(f"updating the existing configuration:{instance.chat_configuration_uuid}")
            logger.info(
                f"Time profile :: Before processing update configuration :: {format_indian_time(datetime.now())}")
            chat_configuration_data = self.process_web_configuration(data)
            instance.chat_details_json = chat_configuration_data
            instance.updated_ts = get_current_timestamp()
            instance.updated_by = user_id
            instance.description = data.get('description', instance.description)
            instance.pre_created = data.get('pre_created',False)
            instance.code = data.get('code', instance.code)
            logger.info(f"Time profile :: Before updating configuration in DB :: {format_indian_time(datetime.now())}")
            self.chat_configuration_dao.update_configuration(instance)
            logger.info(f"Time profile :: End :: {format_indian_time(datetime.now())}")
            logger.info(
                f"Time profile :: before get :: message receiving time:: {format_indian_time(datetime.now())}\n")

        logger.info(f"chat configuration: {instance.chat_configuration_uuid} updated successfully ")
        return SuccessMessages.CHAT_CONFIGURATION_UPDATED_SUCCESSFULLY


    def process_web_configuration(self, data):
        """
            Function to process the configuration specific to web.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        chat_configuration_type = data.get('chat_configuration_type')
        chat_configuration_json = data.get('chat_details_json')
        if chat_configuration_json:
            if chat_configuration_type == ChatConfiguration.LANDING_PAGE:
                try:
                    validated_data = LandingPageData(**chat_configuration_json)
                    return validated_data.model_dump()
                except ValidationError as e:
                    first_error = e.errors()[0]
                    error_message = f"Invalid {first_error['loc'][-1]} : {first_error['msg']}"
                    logger.error(f"Landing page data is invalid ::{str(e)}")
                    raise CustomException(error_message, status_code=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    validated_data = IntentPageData(**chat_configuration_json)
                    return validated_data.model_dump()
                except ValidationError as e:
                    first_error = e.errors()[0]
                    error_message = f"Invalid {first_error['loc'][-1]} : {first_error['msg']}"
                    logger.error(f"Intent page data is invalid ::{str(e)}")
                    raise  CustomException(error_message, status_code=status.HTTP_400_BAD_REQUEST)




