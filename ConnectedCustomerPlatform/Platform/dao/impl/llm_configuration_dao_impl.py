from datetime import datetime
import json
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.dao.interface.llm_configuration_dao_interface import ILLMConfigurationDAO
from DatabaseApp.models import LLMConfiguration, LLMConfigurationCustomerMapping, LLMProviderMetaData, Customers
from django.db import DatabaseError
from ce_shared_services.key_vault.azure.azure_key_vault_service import AzureKeyVaultService
from django.conf import settings
import logging

from Platform.utils import aes_encryption
from ce_shared_services.factory.key_vault.keyvault_factory import KeyVaultFactory
from ce_shared_services.configuration_models.configuration_models import AzureKeyVaultConfig


logger = logging.getLogger(__name__)

class LLMConfigurationDaoImpl(ILLMConfigurationDAO):
    """
    Data Access Object (DAO) for LLM Configuration operations.
    Implements the Singleton pattern to ensure only one instance of this class is created.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(LLMConfigurationDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of LLMConfigurationDAO")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the LLMConfigurationDAO instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            config = {
                "vault_url": settings.AZURE_KEY_VAULT_URL,
                "client_id": settings.IDENTITY_CLIENT_ID
            }
            self.azure_secret = KeyVaultFactory.instantiate("AzureKeyVaultService", AzureKeyVaultConfig(**config))
            logger.info(f"Inside LLMConfigurationDAO - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def create_llm_configuration(self, llm_configuration_data):
        """
        Create a new LLM configuration record in the database.

        :param llm_configuration_data: Dictionary containing configuration data.
        :return: The newly created LLM configuration instance.
        """
        logger.info("Creating new LLM configuration")
        return LLMConfiguration.objects.create(**llm_configuration_data)

    def create_llm_configuration_customer_mapping(self, mapping_data):
        """
        Create a new LLM configuration,customer mapping record in the database.

        :param mapping_data: Dictionary containing mapping data.
        """
        logger.info("Creating new LLM configuration customer mapping")
        LLMConfigurationCustomerMapping.objects.create(**mapping_data)

    def check_llm_configuration_exists(self, llm_configuration_name: str, customer_uuid: str | None) -> bool:
        """
        Check if an LLM configuration with the given name exists for the customer.

        :param llm_configuration_name: The name of the LLM configuration.
        :param customer_uuid: The UUID of the customer.
        :return: True if configuration exists, False otherwise.
        """
        logger.debug(f"Checking if LLM configuration '{llm_configuration_name}' exists for customer '{customer_uuid}'")
        #Case for vassar/super admin
        if customer_uuid is None:
            return LLMConfiguration.objects.filter(
                llm_configuration_name__iexact=llm_configuration_name,
                is_deleted = False,
                is_default = True
            ).exists()
        #Case for org/customer admin
        return LLMConfigurationCustomerMapping.objects.filter(
            llm_configuration_uuid__llm_configuration_name__iexact=llm_configuration_name,
            customer_uuid=customer_uuid,
            llm_configuration_uuid__is_deleted=False,
        ).exists()

    def get_customer_name(self, customer_uuid: str):
        """
        Retrieve the name of the customer based on the UUID.

        :param customer_uuid: The UUID of the customer.
        :return: The customer name if found, None otherwise.
        """
        logger.debug(f"Fetching customer name for UUID: {customer_uuid}")
        return Customers.objects.filter(cust_uuid=customer_uuid).values_list('cust_name', flat=True).first()

    def update_llm_configuration(self, llm_configuration_uuid: str, updated_data: dict, customer_uuid: str | None):
        """
        Update an existing LLM configuration in the database.

        :param customer_uuid: Unique identifier for the customer.
        :param llm_configuration_uuid: UUID of the LLM configuration to update.
        :param updated_data: Dictionary containing the updated configuration data.
        """
        llm_configuration = self.get_llm_configuration_by_uuid(llm_configuration_uuid,customer_uuid)
        if customer_uuid is not None:
            llm_configuration = llm_configuration.llm_configuration_uuid
        llm_configuration.llm_configuration_name = updated_data['llm_configuration_name']
        llm_configuration.llm_configuration_details_json = updated_data['llm_configuration_details_json']
        llm_configuration.llm_provider_uuid=updated_data['llm_provider_uuid']
        llm_configuration.updated_ts = datetime.now()
        llm_configuration.updated_by = updated_data['updated_by']

        llm_configuration.save()

    def get_llm_configuration_by_uuid(self, llm_configuration_uuid: str, customer_uuid: str | None):
        """
        Retrieve an LLM configuration by its UUID.

        :param customer_uuid: The UUID of the customer.
        :param llm_configuration_uuid: The UUID of the LLM configuration.
        :return: LLMConfiguration object if found, None otherwise.
        """
        logger.debug(f"Fetching LLM configuration for UUID: {llm_configuration_uuid}")
        if customer_uuid is None:
            return LLMConfiguration.objects.filter(
                llm_configuration_uuid=llm_configuration_uuid,
                is_deleted = False,
                is_default = True
            ).first()
        return LLMConfigurationCustomerMapping.objects.select_related('llm_configuration_uuid').filter(
            llm_configuration_uuid=llm_configuration_uuid, 
            customer_uuid=customer_uuid,
            llm_configuration_uuid__is_deleted = False
        ).first()

    def check_llm_configuration_exists_excluding_current(self, llm_configuration_name: str, customer_uuid: str | None, llm_configuration_uuid: str):
        """
        Check if an LLM configuration with the given name exists, excluding the current configuration by UUID.

        :param llm_configuration_name: The name of the LLM configuration.
        :param customer_uuid: The UUID of the customer.
        :param llm_configuration_uuid: The UUID of the LLM configuration to exclude.
        :return: True if configuration exists, False otherwise.
        """
        logger.debug(f"Checking if LLM configuration '{llm_configuration_name}' exists for customer '{customer_uuid}', excluding UUID '{llm_configuration_uuid}'")
        if customer_uuid is None:
            return LLMConfiguration.objects.filter(
                llm_configuration_name__iexact=llm_configuration_name,
                is_deleted=False,
                is_default=True
            ).exclude(llm_configuration_uuid=llm_configuration_uuid).exists()
        
        return LLMConfigurationCustomerMapping.objects.filter(
            llm_configuration_uuid__llm_configuration_name__iexact=llm_configuration_name,
            customer_uuid=customer_uuid,
            llm_configuration_uuid__is_deleted=False,
            llm_configuration_uuid__is_default=False
        ).exclude(llm_configuration_uuid=llm_configuration_uuid).exists()


    def mark_llm_configuration_as_deleted(self, llm_configuration_uuid: str, user_uuid: str):
        """
        Mark an LLM configuration as deleted by setting the `is_deleted` flag.

        :param llm_configuration_uuid: The UUID of the LLM configuration.
        :param user_uuid: The UUID of the user performing the action.
        :return: Number of rows updated.
        """
        logger.info(f"Marking LLM configuration '{llm_configuration_uuid}' as deleted")
        return LLMConfiguration.objects.filter(llm_configuration_uuid=llm_configuration_uuid, is_deleted=False).update(
            is_deleted=True,
            updated_by=user_uuid
        )

    def delete_mapping_by_llm_configuration_uuid(self, llm_configuration_uuid: str):
        """
            Deletes the llm_configuration_customer_mapping using llm_configuration_uuid
            :param : llm_configuration_uuid whose mappings need to be deleted
        """
        logger.info("In delete_mapping_by_llm_configuration_uuid DAO")
        return LLMConfigurationCustomerMapping.objects.filter(llm_configuration_uuid=llm_configuration_uuid).delete()

    def get_llm_configurations_by_customer_uuid(self, customer_uuid: str | None):
        """
        Retrieve all LLM configurations for a given customer.

        :param customer_uuid: The UUID of the customer.
        :return: A list of LLM configuration records.
        """
        logger.debug(f"Fetching LLM configurations for customer UUID: {customer_uuid}")
        
        #Case for vassar/super admin
        if customer_uuid is None:
            return LLMConfiguration.objects.filter(
                is_deleted=False,
                is_default = True
            ).values(
                'llm_configuration_name',
                'llm_configuration_uuid',
                'llm_configuration_details_json',
                'llm_provider_uuid'
            ).order_by('-updated_ts')  # Ordering by 'inserted_ts' to get most recent first
        #Case for org/customer admin
        return LLMConfigurationCustomerMapping.objects.filter(
            llm_configuration_uuid__is_deleted=False,
            customer_uuid=customer_uuid,
            llm_configuration_uuid__is_default=False,
        ).values(
            'llm_configuration_uuid__llm_configuration_name',  # Use double underscores for related fields
            'llm_configuration_uuid__llm_configuration_uuid',
            'llm_configuration_uuid__llm_configuration_details_json',
            'llm_configuration_uuid__llm_provider_uuid'
        ).order_by('-llm_configuration_uuid__updated_ts')  # Ordering by 'inserted_ts' of related LLM configuration

    def get_llm_configuration_by_id(self, customer_uuid: str | None, llm_configuration_uuid: str):
        """
        Retrieve a specific LLM configuration by its UUID.

        :param llm_configuration_uuid: The UUID of the LLM configuration.
        :return: LLM configuration record with the api_key replaced with a custom secret_name.
        """
        logger.debug(f"Fetching LLM configuration by UUID: {llm_configuration_uuid}")

        # Fetch LLM configuration details from the database
        llm_config = LLMConfiguration.objects.filter(
            is_deleted=False,
            llm_configuration_uuid=llm_configuration_uuid
        ).values(
            'llm_configuration_uuid',
            'llm_configuration_name',
            'llm_configuration_details_json',
            'llm_provider_uuid'
        ).first()  # We use first() to get only one result

        if not llm_config:
            logger.error(f"LLM configuration not found for UUID: {llm_configuration_uuid}")
            return None  # or raise a CustomException if required

        # Parse the JSON field to modify the api_key
        try:
            llm_configuration_details = llm_config['llm_configuration_details_json']
            api_key =  self.azure_secret.get_secret(f"{llm_configuration_uuid}-llm-api-key")
            encrypted_api_key = aes_encryption(api_key)
            llm_configuration_details['api_key'] = encrypted_api_key
        except Exception as e:
            logger.error(f"Error parsing LLM configuration details: {e}")
            raise CustomException("Error processing LLM configuration details")
                
        return llm_config

    def get_llm_provider_meta_data(self):
        """
        Retrieve metadata for all LLM providers.

        :return: A list of LLM provider metadata records.
        """
        logger.info("Fetching all LLM provider metadata")
        return list(LLMProviderMetaData.objects.all().values())
    
    
    def update_llm_status_by_id(self, customer_uuid, status):
        """
        Updates the status field in LLMConfiguration based on the given customer_uuid.
        If customer_uuid is None, updates status for configurations where is_default=True.
        Otherwise, updates status for configurations mapped to the given customer_uuid.
        Handles database exceptions gracefully.
        """
        try:
            # Case for vassar admin (no customer_uuid provided)
            if customer_uuid is None:
                updated_count = LLMConfiguration.objects.filter(
                    is_deleted=False,
                    is_default=True
                ).update(
                    status=status
                )
                logger.info(f"Updated {updated_count} configurations where is_default=True.")
            # Case for org/customer admin (customer_uuid provided)
            updated_count = LLMConfiguration.objects.filter(
                llmconfigurationcustomermapping__customer_uuid=customer_uuid,
                is_deleted=False,
                is_default=False
            ).update(
                status=status
            )
            logger.info(f"Updated {updated_count} configurations for customer_uuid={customer_uuid}.")

        except DatabaseError as e:
            # Log the exception and re-raise it
            logger.error(f"Database error occurred while updating LLM configurations: {e}")
            raise CustomException("Database error occurred while updating LLM configurations")
        except Exception as e:
            # Handle any other unexpected exceptions
            logger.error(f"An unexpected error occurred: {e}")
            raise CustomException("Error processing LLM configuration details")
    