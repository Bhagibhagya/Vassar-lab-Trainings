import json
import logging
import time
from dataclasses import asdict
from Platform.dao.impl.configuration_details_dao_impl import ConfigurationDetailsDAOImpl
from Platform.services.interface.llm_configuration_service_interface import ILLMConfigurationService
from Platform.dao.impl.llm_configuration_dao_impl import LLMConfigurationDaoImpl
from DatabaseApp.models import  LLMProviderMetaData,Customers
from azure.core.exceptions import AzureError
from ConnectedCustomerPlatform.utils import create_new_uuid_4
from Platform.dataclass import CustomerClientDetailsJson, LLMConfigurationDetailsJson
from Platform.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.exceptions import CustomException
from rest_framework import status
from django.db import transaction
from django.conf import settings
from ce_shared_services import Container,exceptions
from ce_shared_services.key_vault.azure.azure_key_vault_service import AzureKeyVaultService

from ce_shared_services.factory.caching.redis_service import CachingFactory
from ce_shared_services.configuration_models.configuration_models import RedisConfig

from ce_shared_services.factory.key_vault.keyvault_factory import KeyVaultFactory
from ce_shared_services.configuration_models.configuration_models import AzureKeyVaultConfig

logger = logging.getLogger(__name__)


class LLMConfigurationServiceImpl(ILLMConfigurationService):
    """
    Service layer for handling LLM configuration logic such as adding, editing, deleting,
    and retrieving LLM configurations. Interacts with the DAO layer and manages
    integration with Azure Key Vault for securely storing API keys.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LLMConfigurationServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside LLMConfigurationService - Singleton Instance ID: {id(self)}")
            self.__config_details_dao = ConfigurationDetailsDAOImpl()
            self.__llm_config_dao = LLMConfigurationDaoImpl()
            config = {
                "vault_url": settings.AZURE_KEY_VAULT_URL,
                "client_id": settings.IDENTITY_CLIENT_ID
            }
            self.azure_secret = KeyVaultFactory.instantiate("AzureKeyVaultService", AzureKeyVaultConfig(**config))
            self.redis_config = RedisConfig(port=settings.REDIS_PORT, host=settings.REDIS_HOST, db=settings.REDIS_DB)
            self.redis_client = CachingFactory.instantiate("RedisService", self.redis_config)
            self.initialized = True
    
    @transaction.atomic
    def add_llm_configuration(self, customer_uuid: str | None, user_uuid: str, data: dict):
        """
        Add a new LLM configuration to the database and store its API key in Azure Key Vault.

        :param customer_uuid: UUID of the customer to which the configuration belongs.
        :param user_uuid: UUID of the user adding the configuration.
        :param data: The configuration data provided by the user.
        :raises CustomException: If LLM configuration already exists or customer not found.
        """
        logger.info("In llm_configuration_service_impl.py :: LLMConfigurationService :: add_llm_configuration")

        start_time = time.time()

        llm_configuration_name = data.get('llm_configuration_name')
        llm_configuration_details_json = data.get('llm_configuration_details_json', {})
        llm_provider_uuid = data.get('llm_provider_uuid')

        # Validate the llm_configuration_details_json using dataclass
        try:
            llm_configuration_details_json_dict = asdict(LLMConfigurationDetailsJson(**llm_configuration_details_json))
        except Exception as e:
            logger.error(f"Error validating LLM configuration details: {e}")
            raise CustomException(ErrorMessages.INVALID_LLM_CONFIGURATION_DETAILS)
        
        llm_configuration_details_json_dict = asdict(LLMConfigurationDetailsJson(**llm_configuration_details_json))

        logger.info(f"\nTime profile :: Add LLM Configuration :: time before validation: {time.time() - start_time}\n")

        logger.info(f"Adding LLM configuration '{llm_configuration_name}' for customer {customer_uuid}")

        # Time profiling for checking LLM configuration existence
        check_start_time = time.time()

        # Check for the existence of the LLM configuration
        existing_config = self.__llm_config_dao.check_llm_configuration_exists(llm_configuration_name, customer_uuid)
        if existing_config:
            raise CustomException(ErrorMessages.LLM_CONFIGURATION_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)

        logger.info(f"\nTime profile :: Check for LLM Configuration existence: {time.time() - check_start_time}\n")

        # Time profiling for retrieving customer name
        customer_name_start_time = time.time()

        logger.info(f"\nTime profile :: Fetch customer name: {time.time() - customer_name_start_time}\n")

        # Time profiling for managing Azure secret
        azure_secret_start_time = time.time()

        # Creating new uuid for llm configuration
        llm_configuration_uuid = create_new_uuid_4()

        #Storing in redis
        if customer_uuid is None:
            self.redis_client.set(f'{llm_configuration_uuid}-llm', json.dumps(llm_configuration_details_json_dict))

        secret_name = f"{llm_configuration_uuid}-llm-api-key"
        # We can pass another parameter expires_on if needed
        self.azure_secret.set_secret(secret_name,llm_configuration_details_json_dict['api_key'])
        llm_configuration_details_json_dict['api_key'] = secret_name
        logger.info(f"\nTime profile :: Manage Azure secret: {time.time() - azure_secret_start_time}\n")

        # Time profiling for UUID creation
        uuid_start_time = time.time()

        logger.info(f"\nTime profile :: UUID generation: {time.time() - uuid_start_time}\n")

        # Time profiling for saving to database
        db_start_time = time.time()
        llm_provider_instance = LLMProviderMetaData(llm_provider_uuid)
        # Save LLM configuration to the database
        if customer_uuid is None:
            self.__llm_config_dao.create_llm_configuration({
                'llm_configuration_uuid': llm_configuration_uuid,
                'llm_configuration_name': llm_configuration_name,
                'llm_configuration_details_json': llm_configuration_details_json_dict,
                'llm_provider_uuid': llm_provider_instance,
                'is_default': True,
                'created_by': user_uuid,
                'updated_by': user_uuid
            })
        else:
            llm_configuration_instance = self.__llm_config_dao.create_llm_configuration({
                'llm_configuration_uuid': llm_configuration_uuid,
                'llm_configuration_name': llm_configuration_name,
                'llm_configuration_details_json': llm_configuration_details_json_dict,
                'llm_provider_uuid': llm_provider_instance,
                'is_default': False,
                'created_by': user_uuid,
                'updated_by': user_uuid
            })
            # Creating new uuid for mapping llm configuration and customer
            mapping_uuid = create_new_uuid_4()
            customer_instance = Customers(customer_uuid)
            self.__llm_config_dao.create_llm_configuration_customer_mapping({
                'mapping_uuid': mapping_uuid,
                'llm_configuration_uuid': llm_configuration_instance,
                'customer_uuid': customer_instance,
                'created_by': user_uuid,
                'updated_by': user_uuid
            })

        logger.info(f"\nTime profile :: Save to database: {time.time() - db_start_time}\n")

        logger.info(f"LLM configuration '{llm_configuration_name}' created successfully")

        # Final time profile for the entire process
        logger.info(f"\nTime profile :: Total time taken: {time.time() - start_time}\n")

        return llm_configuration_uuid

    def edit_llm_configuration(self, customer_uuid: str | None, user_uuid: str, data: dict):
        logger.info(
            "In llm_configuration_service_impl.py :: :: :: LLMConfigurationService :: :: :: edit_llm_configuration")
        """
        Edit an existing LLM configuration and update its API key in Azure Key Vault if necessary.

        :param customer_uuid: UUID of the customer to which the configuration belongs.
        :param user_uuid: UUID of the user editing the configuration.
        :param data: The updated configuration data provided by the user.
        :raises CustomException: If LLM configuration is not found, exists with another name, or an error occurs with Azure Key Vault.
        """
        llm_configuration_uuid = data.get('llm_configuration_uuid')
        llm_configuration_name = data.get('llm_configuration_name')
        llm_configuration_details_json = data.get('llm_configuration_details_json', {})
        llm_provider_uuid=data.get('llm_provider_uuid')

        # Validate the llm_configuration_details_json using dataclass
        try:
            llm_configuration_details_json_dict = asdict(LLMConfigurationDetailsJson(**llm_configuration_details_json))
        except Exception as e:
            logger.error(f"Error validating LLM configuration details: {e}")
            raise CustomException(ErrorMessages.INVALID_LLM_CONFIGURATION_DETAILS)

        logger.info(f"Editing LLM configuration '{llm_configuration_name}' for customer {customer_uuid}")

        # Fetch LLM configuration and related customer name in a single query
        llm_configuration = self.__llm_config_dao.get_llm_configuration_by_uuid(llm_configuration_uuid, customer_uuid)
        if llm_configuration is None:
            raise CustomException(ErrorMessages.LLM_CONFIGURATION_NOT_FOUND)

        if customer_uuid is not None:
            llm_configuration = llm_configuration.llm_configuration_uuid
        # Check if another configuration with the same name exists for the customer
        if self.__llm_config_dao.check_llm_configuration_exists_excluding_current(llm_configuration_name,
                                                                                  customer_uuid,
                                                                                  llm_configuration_uuid):
            logger.error(f"LLM configuration '{llm_configuration_name}' already exists for customer {customer_uuid}")
            raise CustomException(ErrorMessages.LLM_CONFIGURATION_EXISTS,status_code=status.HTTP_400_BAD_REQUEST)

        

        #Update api key in the redis as well
        if customer_uuid is None:
            llm_config_details = self.redis_client.get(f"{llm_configuration_uuid}-llm") #get the llm configuration details
            llm_config_details = json.loads(llm_config_details) #convert the llm configuration details to dict
            llm_config_details['api_key'] = llm_configuration_details_json_dict['api_key'] #Update the llm api key
            self.redis_client.set(f'{llm_configuration_uuid}-llm', json.dumps(llm_config_details)) #Update the llm configuration details

        # Update API key in Key Vault if necessary
        secret_name = f"{llm_configuration_uuid}-llm-api-key"
        # We can pass another parameter expires_on if needed
        self.azure_secret.set_secret(secret_name,llm_configuration_details_json_dict['api_key'])
        llm_configuration_details_json_dict['api_key'] = secret_name

        # Prepare data for the update
        llm_provider_instance = LLMProviderMetaData(llm_provider_uuid)
        update_data = {
            'llm_configuration_name': llm_configuration_name,
            'llm_configuration_details_json': llm_configuration_details_json_dict,
            'updated_by': user_uuid,
            'llm_provider_uuid':llm_provider_instance,
        }
        # Update the LLM configuration in the DAO
        self.__llm_config_dao.update_llm_configuration(llm_configuration_uuid, update_data, customer_uuid)
        logger.info(f"LLM configuration '{llm_configuration_name}' updated successfully")

    @transaction.atomic
    def delete_llm_configuration(self, llm_configuration_uuid: str, user_uuid: str):
        logger.info(
            "In llm_configuration_service_impl.py :: :: :: LLMConfigurationService :: :: :: delete_llm_configuration")
        """
        Mark an LLM configuration as deleted in the database.

        :param llm_configuration_uuid: UUID of the LLM configuration to delete.
        :param user_uuid: UUID of the user performing the delete operation.
        :raises CustomException: If LLM configuration is not found or cannot be marked as deleted.
        """
        logger.info(f"Attempting to delete LLM configuration '{llm_configuration_uuid}'")
        # Delete llm_configuration_customer_mapping
        self.__llm_config_dao.delete_mapping_by_llm_configuration_uuid(llm_configuration_uuid)

        #Delete the llm configuration details from the redis
        self.redis_client.delete(f"{llm_configuration_uuid}-llm")

        # Mark the LLM configuration as deleted in the database
        self.__llm_config_dao.mark_llm_configuration_as_deleted(llm_configuration_uuid, user_uuid)
        logger.info(f"LLM configuration '{llm_configuration_uuid}' marked as deleted by user '{user_uuid}'")

    def get_llm_configurations(self, customer_uuid: str | None):
        logger.info(
            "In llm_configuration_service_impl.py :: :: :: LLMConfigurationService :: :: :: get_llm_configurations")
        """
        Retrieve all LLM configurations for a given customer.

        :param customer_uuid: UUID of the customer whose configurations are to be retrieved.
        :return: A list of sanitized LLM configurations.
        :raises CustomException: If the customer is not found or there is a database error.
        """
        logger.info(f"Retrieving LLM configurations for customer {customer_uuid}")
    
        results =  self.__llm_config_dao.get_llm_configurations_by_customer_uuid(customer_uuid)
        normalized_results = [
            {
                'llm_configuration_name': result.get('llm_configuration_uuid__llm_configuration_name') or result.get('llm_configuration_name'),
                'llm_configuration_uuid': result.get('llm_configuration_uuid__llm_configuration_uuid') or result.get('llm_configuration_uuid'),
                'llm_configuration_details_json': result.get('llm_configuration_uuid__llm_configuration_details_json') or result.get('llm_configuration_details_json'),
                'llm_provider_uuid': result.get('llm_configuration_uuid__llm_provider_uuid') or result.get('llm_provider_uuid'),
            }
            for result in results
        ]
        return normalized_results

    def get_llm_configuration_by_id(self, customer_uuid: str | None, llm_configuration_uuid: str):
        logger.info(
            "In llm_configuration_service_impl.py :: :: :: LLMConfigurationService :: :: :: get_llm_configuration_by_id")
        """
        Retrieve a specific LLM configuration by its UUID, excluding the API key.

        :param llm_configuration_uuid: UUID of the LLM configuration to retrieve.
        :return: A sanitized LLM configuration, excluding the API key.
        :raises CustomException: If the configuration is not found or if a database error occurs.
        """
        logger.info(f"Retrieving LLM configuration '{llm_configuration_uuid}' by ID")

        return self.__llm_config_dao.get_llm_configuration_by_id(customer_uuid, llm_configuration_uuid)

    def get_llm_provider_meta_data(self):
        logger.info(
            "In llm_configuration_service_impl.py :: :: :: LLMConfigurationService :: :: :: get_llm_provider_meta_data ")
        """
        Retrieve metadata for all LLM providers from the DAO layer.

        Returns:
            list: A list of dictionaries where each dictionary contains metadata for an LLM provider.
        :raises CustomException: If a database error occurs during the retrieval of metadata.
        """
        logger.info("Fetching LLM provider metadata.")

        # Retrieve the provider metadata from the DAO layer
        metadata = self.__llm_config_dao.get_llm_provider_meta_data()
        logger.debug(f"LLM provider metadata retrieved: {metadata}")
        return metadata

    def verify_llm_configuration(self, data: dict):
        """
        Verify the LLM configuration details provided in the request data.

        This method takes a dictionary containing LLM configuration details,
        validates the details using a data class, and attempts to instantiate
        and interact with the LLM to confirm the configuration is correct.

        :param data: A dictionary containing the LLM configuration details.
                    Expected key:
                    - llm_configuration_details_json: A JSON object with required fields
                    for LLM instantiation.
        :raises CustomException: If validation of the LLM configuration details fails
                                or if the LLM verification process encounters an error.
        """

        # Extract and validate the LLM configuration details from the provided data
        llm_configuration_details_json = data.get('llm_configuration_details_json', {})
        
        # Validate the llm_configuration_details_json using dataclass
        try:
            llm_configuration_details_json_dict = asdict(LLMConfigurationDetailsJson(**llm_configuration_details_json))
        except Exception as e:
            logger.error(f"Error validating LLM configuration details: {e}")
            raise CustomException(ErrorMessages.INVALID_LLM_CONFIGURATION_DETAILS)

        # Prepare the configuration for the LLM
        llm_class_name = 'AzureOpenAILLM'
        llm_config = {
            'deployment_name' : llm_configuration_details_json_dict.get('deployment_name'),
            'model_name' : llm_configuration_details_json_dict.get('model_name'),
            'endpoint' : llm_configuration_details_json_dict.get('api_base'),
            'api_type' : llm_configuration_details_json_dict.get('api_type'),
            'api_key' : llm_configuration_details_json_dict.get('api_key'),
            'api_version' : llm_configuration_details_json_dict.get('api_version'),
        }

        # Instantiate the LLM using the provided configuration
        try:
            llm = Container.llm.instantiate(llm_class_name, llm_config)
            llm.run_sync('Hi')
        except Exception as e:
            error_message = "LLM verification failed"
            raise CustomException(error_message)
        
    def update_llm_status_by_id(self, customer_uuid: str | None, status: bool):
        logger.info(
            "In llm_configuration_service_impl.py :: :: :: LLMConfigurationService :: :: :: update_llm_status_by_id")
        """
        :param customer_uuid: UUID of the customer to which the configurations status values has to be updated.
        :param status: Boolean value to update the status of the configurations.
        """
        self.__llm_config_dao.update_llm_status_by_id(customer_uuid, status)
        self.__config_details_dao.update_llm_status(customer_uuid, status)
        
    
    def get_llm_status_by_id(self, customer_uuid: str | None):
        logger.info(
            "In llm_configuration_service_impl.py :: :: :: LLMConfigurationService :: :: :: get_llm_status_by_id")
        """
        :param customer_uuid: UUID of the customer to which the configurations status values has to be updated.
        """
        return self.__config_details_dao.get_llm_status_by_id(customer_uuid)