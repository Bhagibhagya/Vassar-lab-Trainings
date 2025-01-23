import inspect
import logging
from django.db.models import F, Value, Subquery
from DatabaseApp.models import CustomerClientTierMapping,CustomerClient
from Platform.dao.interface.customer_client_tier_dao_interface import ICustomerClientTierDao

logger = logging.getLogger(__name__)
class CustomerClientTierDaoImpl(ICustomerClientTierDao):


    def save_customer_client_tier_mapping(self, customer_client_tier):
        """
        Saves a CustomerClientTierMapping instance to the database.

        Parameters:
            - customer_client_tier (CustomerClientTierMapping): The instance to be saved.
        """
        # Log the beginning of the save operation
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Saving customer client tier instance")
        customer_client_tier.save()

        # Log success after saving the instance
        logger.info(f"Customer client tier instance saved successfully: {customer_client_tier}")


    def delete_customer_client_tier_mapping(self, mapping_uuid):
        """
        Deletes a customer client tier mapping by its unique identifier.

        Parameters:
            - mapping_uuid (str): The unique identifier of the tier mapping to delete.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        CustomerClientTierMapping.objects.filter(mapping_uuid=mapping_uuid).delete()


    def get_customer_client_by_tier_mapping(self, tier_mapping_uuid):
        """
        Retrieves customer client details associated with a specific tier mapping.
        Parameters:
            - tier_mapping_uuid (str): The unique identifier for the tier mapping.
        Returns:
            QuerySet: A queryset containing details of customer clients linked to the tier mapping,
            including their names, emails, addresses, and metadata.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        data = CustomerClientTierMapping.objects.filter(tier_mapping_uuid=tier_mapping_uuid) \
            .select_related('customer_client_uuid') \
            .values(
            'mapping_uuid',
            'customer_client_uuid_id',
            'tier_mapping_uuid_id',
            'extractor_template_details_json',
            'inserted_ts',
            'updated_ts',
            'created_by',
            'updated_by',
            customer_client_name=F('customer_client_uuid__customer_client_name'),
            customer_client_emails=F('customer_client_uuid__customer_client_emails'),
            customer_client_address=F('customer_client_uuid__customer_client_address'),
            customer_client_domain=F('customer_client_uuid__customer_client_domain_name'),
        ).order_by('-inserted_ts')
        return data


    def get_customer_client_instance_by_tier_mapping_uuid(self,mapping_uuid):
        """
            Fetches a CustomerClientTierMapping instance based on the provided mapping_uuid.

            :param mapping_uuid: The UUID of the mapping to retrieve.
            :return: A CustomerClientTierMapping instance if found, None otherwise.
        """
        return CustomerClientTierMapping.objects.filter(mapping_uuid=mapping_uuid).first()

    def get_customer_client_list_by_exclude_customer_client_list(self,application_uuid,customer_uuid):
        """
            Retrieve a list of customer clients by excluding those mapped in CustomerClientTierMapping
            for a specific application UUID.
            Args:
                application_uuid (str): The UUID of the application to filter tier mappings.
                customer_uuid (str): The UUID of the customer to filter customer clients.

            Returns: A list of dictionaries containing customer client details, excluding those
                present in the tier mapping.
        """
        excluded_customer_client_uuids = CustomerClientTierMapping.objects.filter(
            tier_mapping_uuid__application_uuid=application_uuid
        ).values('customer_client_uuid')

        # Now, filter CustomerClient and exclude customer_client_uuids using the subquery
        customer_clients = CustomerClient.objects.filter(
            customer_uuid=customer_uuid,
            is_deleted=False
        ).exclude(
            customer_client_uuid__in=Subquery(excluded_customer_client_uuids)
        ).values(
            'customer_client_uuid', 'customer_client_name', 'customer_client_emails',
            'customer_client_address', 'customer_client_domain_name'
        )
        return customer_clients
