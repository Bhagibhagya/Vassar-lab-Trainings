import logging

from ChatBot.dao.interface.dimensions_intent_dao_interface import IDimensionsIntentDao

from DatabaseApp.models import DimensionCustomerApplicationMapping

logger = logging.getLogger(__name__)
class DimensionsIntentDaoImpl(IDimensionsIntentDao):
    """
    Data Access Object for Intent operations.
    This class handles database interactions for Intent-related data.
    """
    def get_all_dimensions_by_dimension_type_name(self, dimension_type_name,application_uuid,customer_uuid):
        """
            Fetch all dimensions associated with a specific dimension type name,
            ensuring the application and customer are properly mapped and the status is active.

            :param dimension_type_name: The name of the dimension type (e.g., 'INTENT').
            :param application_uuid: The unique identifier for the application.
            :param customer_uuid: The unique identifier for the customer.
            :return: A list of dimension names matching the given dimension type name, application, and customer.
        """
        logger.info(f"Fetching dimensions for dimension type: {dimension_type_name}")
        logger.debug(f"Application UUID: {application_uuid}, Customer UUID: {customer_uuid}")

        # Fetch dimensions that meet the criteria
        dimensions = (
            DimensionCustomerApplicationMapping.objects
            .select_related('dimension_uuid__dimension_type_uuid')  # Join with Dimension and DimensionType
            .filter(
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                dimension_uuid__dimension_type_uuid__dimension_type_name=dimension_type_name,  # Filter by dimension type name
                dimension_uuid__dimension_type_uuid__dimensiontypecustomerapplicationmapping__customer_uuid=customer_uuid,  # Ensure mapping for same customer
                dimension_uuid__dimension_type_uuid__dimensiontypecustomerapplicationmapping__application_uuid=application_uuid,  # Ensure mapping for same application
                dimension_uuid__dimension_type_uuid__dimensiontypecustomerapplicationmapping__status=True  # Ensure status is True
            )
            .values_list('dimension_uuid__dimension_name', flat=True)  # Get only the dimension names
        )

        # Return the fetched dimensions
        return dimensions