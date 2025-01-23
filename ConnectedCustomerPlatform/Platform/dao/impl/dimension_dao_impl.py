import uuid
import logging

from django.db.models import Q
from django.db.models.functions import Upper

from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.dao.interface.dimension_dao_interface import IDimensionDao
from DatabaseApp.models import Dimension, DimensionType, States, Countries, DimensionsView

# Initialize logger
logger = logging.getLogger(__name__)

class DimensionDaoImpl(IDimensionDao):
    # Gets or creates a dimension based on the provided name, dimension type UUID, and user UUID.
    def get_or_create_dimension(self, dimension_name, dimension_type_uuid, user_uuid):
        logger.info(f"Attempting to get or create dimension: {dimension_name}, "
                    f"Type UUID: {dimension_type_uuid}")

        # Retrieve or create the dimension
        dimension, created = Dimension.objects.get_or_create(
            dimension_name__iexact=dimension_name,
            dimension_type_uuid= DimensionType(dimension_type_uuid),
            defaults={
                'dimension_name': dimension_name,
                'dimension_uuid': str(uuid.uuid4()),
                'created_by': user_uuid,
                'updated_by': user_uuid
            }
        )

        return dimension, created

    # Retrieves countries or states (depending on the parent dimension) from the database.
    def get_countries_or_states(self, country_name):
        logger.info(f"Retrieving countries or states for Country Name: {country_name}")

        if country_name is None:
            # Fetch all countries, convert the name to uppercase, and return uppercase 'country_name'
            logger.debug("Fetching all countries as parent_dimension_uuid is None.")
            countries = Countries.objects.annotate(
                country_name=Upper('name')
            ).values_list('country_name', flat=True).order_by('country_name')

            logger.info(f"Retrieved {countries.count()} countries.")
            return countries


        logger.debug(f"Fetched states under the country - {country_name}")

        # Filter states by country name, convert state name to uppercase, and return and uppercase 'name'
        states = States.objects.filter(
            country__name__iexact=country_name
        ).annotate(
            state_name=Upper('name')
        ).values_list('state_name', flat=True).order_by('state_name')

        logger.info(f"Retrieved {states.count()} states for Country: {country_name}.")
        return states

    def fetch_parent_and_child_dimension_details(self, customer_uuid, application_uuid, parent_dimension_type_uuid):
        logger.info("In DimensionDaoImpl :: fetch_parent_and_child_dimension_details")
        try:
            return DimensionsView.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid,
                                                 dimension_type_uuid=parent_dimension_type_uuid).order_by('-updated_ts').values()

        except Exception as e:
            logger.exception(f"Error in fetching parent and child dimensions :: {e}")
            return None
    def fetch_parent_and_child_dimension_details_by_parent_dimension_name(self, customer_uuid, application_uuid, parent_dimension_type_name):
        logger.info("In DimensionDaoImpl :: fetch_parent_and_child_dimension_details")
        try:

            return DimensionsView.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid,
                                                 dimension_type_name=parent_dimension_type_name)

        except Exception as e:
            logger.exception(f"Error in fetching parent and child dimensions :: {e}")
            raise CustomException("Error in fetching parent and child dimensions")



