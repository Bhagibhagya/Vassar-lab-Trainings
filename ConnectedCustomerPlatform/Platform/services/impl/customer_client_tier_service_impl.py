import inspect
import logging
import uuid
from datetime import datetime
from django.db import IntegrityError
from DatabaseApp.models import CustomerClient
from DatabaseApp.models import CustomerClientTierMapping
from Platform.dao.impl.customer_client_tier_dao_impl import CustomerClientTierDaoImpl
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.services.interface.customer_client_tier_service_interface import ICustomerClientTierService
from Platform.constant.error_messages import ErrorMessages
from DatabaseApp.models import DimensionCustomerApplicationMapping
from rest_framework import status

logger = logging.getLogger(__name__)
class CustomerClientTierServiceImpl(ICustomerClientTierService):
    """
    ViewSet for managing Customer Client Tier Mapping, providing methods to add, edit,
    delete, and retrieve configurations.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerClientTierServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.customer_client_tier_dao = CustomerClientTierDaoImpl()
            print(f"Inside CustomerClientDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True


    def add_customer_client_tier_mapping(self, user_uuid, data):
        """
        Adds a new customer client tier mapping to the database.

        This method builds a customer client tier instance from the provided data
        and user information, then saves it using the DAO layer.

        Parameters:
            - user_uuid (str): The UUID of the user performing the operation.
            - data (dict): The validated data for creating the customer client tier instance.
        """

        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Build a new customer client tier instance using the provided data
        customer_client_tier_instance = self.__build_customer_client_tier_instance(user_uuid, data)

        # Save the customer client tier instance using the DAO layer
        try:
            # Attempt to save the customer client tier instance
            self.customer_client_tier_dao.save_customer_client_tier_mapping(customer_client_tier_instance)
        except IntegrityError as e:
            # Check if the error is due to the unique constraint on customer_client_uuid and tier_mapping_uuid
            if 'unique constraint' in str(e):
                logger.error(f"Duplicate found for: customer_client_uuid={data.get('customer_client_uuid')} and tier_mapping_uuid={data.get('tier_mapping_uuid')}")
                raise CustomException(ErrorMessages.CUSTOMER_CLIENT_TIER_MAPPING_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
            else:
                # Log and raise a generic integrity error
                logger.error("Database integrity error: %s", str(e))
                raise CustomException(ErrorMessages.ADD_CUSTOMER_CLIENT_TIER_FAILED)
        except Exception as e:
            # For all other unexpected errors, log and raise a generic failure message
            logger.error("Unexpected error occurred: %s", str(e))
            raise CustomException(ErrorMessages.ADD_CUSTOMER_CLIENT_TIER_FAILED)

        self.customer_client_tier_dao.save_customer_client_tier_mapping(customer_client_tier_instance)

    def edit_customer_client_tier_mapping(self, user_uuid, data):
        """
        Edits an existing CustomerClientTierMapping instance.

        Parameters:
            - user_uuid (str): The unique identifier of the user performing the operation.
            - data (dict): A dictionary containing the updated data for the customer client tier.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Editing customer client tier")

        # Retrieve the CustomerClientTierMapping instance using the mapping_uuid from the data
        customer_client_tier = self.customer_client_tier_dao.get_customer_client_instance_by_tier_mapping_uuid(data.get('mapping_uuid'))


        # Log the retrieved instance details for debugging
        logger.info(f"Retrieved customer client tier mapping for editing: {customer_client_tier}")

        # Update the instance fields with new data

        customer_client_tier.extractor_template_details_json = data.get('extractor_template_details_json')
        customer_client_tier.updated_by = user_uuid  # Set the user who made the update

        # Save the updated customer client tier instance

            # Attempt to save the customer client tier instance
        self.customer_client_tier_dao.save_customer_client_tier_mapping(customer_client_tier)

    def delete_customer_client_tier_mapping(self, mapping_uuid):
        """
        Deletes a customer client tier mapping.

        Parameters:
            - mapping_uuid (str): The unique identifier of the tier mapping to delete.
        """
        self.customer_client_tier_dao.delete_customer_client_tier_mapping(mapping_uuid)


    def get_customers_client_by_tier_mapping(self, tier_mapping_uuid):
        """
        Fetches a list of customer clients associated with a specified tier mapping.

        Parameters:
            - tier_mapping_uuid (str): The unique identifier for the tier mapping.

        Returns:
            list: A list of customer clients linked to the specified tier mapping.
        """
        customer_client_list = self.customer_client_tier_dao.get_customer_client_by_tier_mapping(tier_mapping_uuid)
        return customer_client_list

    def get_customer_client_dropdown_in_tier(self, application_uuid,customer_uuid):
        """
            Retrieves customer clients not already mapped to a tier under the given
            application and customer.

            :param application_uuid: The UUID of the application.
            :param customer_uuid: The UUID of the customer.
            :return: List of customer-client data excluding already mapped ones.
        """
        logger.info(f"Fetching customer clients for application_uuid: {application_uuid} and customer_uuid: {customer_uuid}")

        customer_clients = self.customer_client_tier_dao.get_customer_client_list_by_exclude_customer_client_list(application_uuid,customer_uuid)
        # Log successful completion of the process
        logger.info("Successfully fetched customer clients for dropdown.")
        return customer_clients

    def __build_customer_client_tier_instance(self, user_uuid, data):
        """
        Builds a CustomerClientTierMapping instance using the provided user UUID and data.

        Parameters:
            - user_uuid (str): The UUID of the user performing the operation.
            - data (dict): The validated data to create the customer client tier mapping instance.

        Returns:
            - CustomerClientTierMapping: The constructed customer client tier mapping instance.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        logger.info(f"Building instance for user_uuid: {user_uuid}, with data: {data}")

        # Build and return the CustomerClientTierMapping instance
        customer_client_tier_instance = CustomerClientTierMapping(
            mapping_uuid=uuid.uuid4(),
            customer_client_uuid=CustomerClient(data.get('customer_client_uuid')),
            tier_mapping_uuid=DimensionCustomerApplicationMapping(data.get('tier_mapping_uuid')),
            extractor_template_details_json=data.get('extractor_template_details_json'),
            created_by=user_uuid,
            updated_by=user_uuid
        )

        # Log successful instance creation
        logger.info(f"Successfully built CustomerClientTierMapping instance: {customer_client_tier_instance}")
        return customer_client_tier_instance
