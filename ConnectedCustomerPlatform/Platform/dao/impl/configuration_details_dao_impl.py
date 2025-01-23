
from datetime import datetime
import logging

from ConnectedCustomerPlatform.utils import create_new_uuid_4
from DatabaseApp.models import ConfigurationDetails
from Platform.dao.interface.configuration_details_dao_interface import IConfigurationDetailsDAO
from DatabaseApp.models import Customers
logger = logging.getLogger(__name__)

class ConfigurationDetailsDAOImpl(IConfigurationDetailsDAO):

    def update_llm_status(self, customer_uuid: str | None, status: bool):
        """
        Create or update a record in ConfigurationDetails based on customer_uuid.

        Args:
            customer_uuid (str|None): The UUID of the customer. Can be None.
            status (bool): The value to update for `is_llm_enabled` in configuration_details_json.

        Returns:
            ConfigurationDetails: The created or updated record.
        """

        # Define the JSON update data
        configuration_json = {"is_llm_enabled": status}

        try:
            if customer_uuid is None:
                # Handle the special case where customer_uuid is None
                record = ConfigurationDetails.objects.get(customer_uuid=None)
                # Update only the required fields
                record.configuration_details_json = configuration_json
                record.updated_ts = datetime.now()
                record.save()
                return record, False  # False indicates no new record was created
            else:
                # If customer_uuid is provided, try to get the record
                record = ConfigurationDetails.objects.get(customer_uuid=customer_uuid)
                # Update only the required fields
                record.configuration_details_json = configuration_json
                record.updated_ts = datetime.now()
                record.save()
                return record, False  # False indicates no new record was created

        except ConfigurationDetails.DoesNotExist:
            customer_instance = None if customer_uuid is None else Customers(customer_uuid)
            record = ConfigurationDetails.objects.create(
                configuration_details_uuid=create_new_uuid_4(),
                customer_uuid=customer_instance,  # Can be None or a specific UUID
                configuration_details_json=configuration_json,
                inserted_ts=datetime.now(),
                updated_ts=datetime.now(),
            )
            return record, True  # True indicates a new record was created

    def get_llm_status_by_id(self, customer_uuid: str | None):
        """
        Retrieve the LLM status for a specific customer.

        Args:
            customer_uuid (str|None): The UUID of the customer. Can be None.

        Returns:
            bool: The LLM status for the customer.
        """

        try:
            # Use values() to fetch only the required field
            record = ConfigurationDetails.objects.filter(customer_uuid=customer_uuid).values("configuration_details_json").first()

            if not record:
                # If no record is found, return False
                return False

            # Safely extract the is_llm_enabled field
            return bool(record.get("configuration_details_json", {}).get("is_llm_enabled", False))
        except Exception as e:
            logger.error(f"Error fetching LLM status for customer_uuid={customer_uuid}: {e}")
            return False
        
