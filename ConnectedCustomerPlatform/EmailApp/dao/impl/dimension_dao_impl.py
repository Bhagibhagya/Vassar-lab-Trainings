from django.db.models import Q, F, Value, Func, TextField
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast

from DatabaseApp.models import DimensionCustomerApplicationMapping, Dimension,DimensionsView
import logging
from EmailApp.Exceptions.api_exception import InvalidValueProvidedException, ResourceNotFoundException
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.dao.interface.dimension_dao_interface import IDimensionDaoInterface
logger=logging.getLogger(__name__)
from EmailApp.constant.constants import DimensionTypeNames
from django.db import connection
from EmailApp.constant.queries import QUERY_FOR_FETCHING_INTENTS_SUBINTENTS
class DimensionDaoImpl(IDimensionDaoInterface):

    def get_dimensions_list_by_dimension_type_name(self, dimension_type_name,customer_uuid,application_uuid):
        """
        Gets dimensions names list for specific application and customer by dimension_type_name
        """
        logger.info("In DimensionDaoImpl::get_dimensions_list_by_dimension_type_name")
        #Fetch dimension names using Dimension type name by using DimCustAppMap, Dimension,DimensionType tables
        return (DimensionCustomerApplicationMapping.objects
            .filter(
                application_uuid=application_uuid,
                customer_uuid=customer_uuid,
                status=True,
                dimension_uuid__dimension_type_uuid__dimension_type_name=dimension_type_name,
                dimension_uuid__status=True,
                dimension_uuid__is_deleted=False
            )
            .values_list('dimension_uuid__dimension_name', flat=True))

    def get_intent_subintents_for_customer_application(self,customer_uuid,application_uuid):
        """
        dao for getting intents and sub_intents for the particular customer and application
        """
        logger.info("In DimensionDaoImpl::get_intent_subintents_for_customer_application")
        query = QUERY_FOR_FETCHING_INTENTS_SUBINTENTS    
        # Execute the raw query
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [DimensionTypeNames.INTENT,DimensionTypeNames.SUB_INTENT,customer_uuid, application_uuid,customer_uuid,application_uuid])
                intents_subintents = cursor.fetchall()
        finally:
            connection.close()
        return intents_subintents
    
    def get_dimension_uuid_dimension_name_description(self,customer_uuid,application_uuid,dimension_type_name):
        """
        Gets dimension_uuid,dimension_name, description details list for specific application and customer by dimension_type_name
        """
        logger.info("In DimensionDaoImpl::get_dimension_uuid_dimension_name_description")
        #Fetch dimension names, mapping_uuid, description using Dimension type name by using DimCustAppMap, Dimension,DimensionType tables
        return (DimensionCustomerApplicationMapping.objects
            .filter(
                application_uuid=application_uuid,
                customer_uuid=customer_uuid,
                status=True,
                dimension_uuid__dimension_type_uuid__dimension_type_name=dimension_type_name,
                dimension_uuid__status=True,
                dimension_uuid__is_deleted=False,
            )
            .values_list('dimension_uuid','dimension_uuid__dimension_name','description'))
    
    def get_mapping_dimension_uuid_dimension_name_list(self,dimension_type_name,customer_uuid,application_uuid):
        """
        Gets mapping_uuid, dimension_uuid, dimension_name details list for specific application and customer by dimension_type_name
        """
        logger.info("In DimensionDaoImpl::get_mapping_dimension_uuid_dimension_name_list")
        #Fetch dimension names, mapping_uuid, description using Dimension type name by using DimCustAppMap, Dimension,DimensionType tables
        return (DimensionCustomerApplicationMapping.objects
            .filter(
                application_uuid=application_uuid,
                customer_uuid=customer_uuid,
                status=True,
                dimension_uuid__dimension_type_uuid__dimension_type_name=dimension_type_name,
                dimension_uuid__status=True,
                dimension_uuid__is_deleted=False,
            )
            .values_list('mapping_uuid','dimension_uuid','dimension_uuid__dimension_name'))

    def update_description_of_dimension(self,mapping_uuid, new_description,updated_by):
        """Update the description for the given mapping_uuid"""

        # Perform the update and get the count of rows affected
        rows_affected = DimensionCustomerApplicationMapping.objects.filter(mapping_uuid=mapping_uuid).update(
            description=new_description,updated_by=updated_by)

        # Check if any row was updated
        if rows_affected == 0:
            logger.error(f"No record found with mapping_uuid '{mapping_uuid}' to update description.")
            raise InvalidValueProvidedException(f"No record found with mapping_uuid '{mapping_uuid}' to update description.")

    def fetch_dimension_parent_dimension_name_by_dimension_uuid(self,mapping_uuid,customer_uuid,application_uuid):
        """
            Fetches the names of a dimension and its parent dimension based on the given dimension UUID,
            customer UUID, and application UUID.

            Args:
                dimension_uuid (str): The unique identifier of the dimension.
                customer_uuid (str): The unique identifier of the customer.
                application_uuid (str): The unique identifier of the application.

            Returns:
                tuple: A tuple containing the names of the dimension and its parent dimension if found,
                       or None if no matching record is found.

            Raises:
                CustomException: If an exception occurs during the query execution.
            """
        logger.info("In DimensionDaoImpl :: fetch_dimension_parent_dimension_name_by_dimension_uuid")
        try:
            dimension_names= DimensionCustomerApplicationMapping.objects.filter(Q(parent_dimension_uuid__isnull=True) |
                Q(parent_dimension_uuid__isnull=False, parent_dimension_uuid__status=True,
                  parent_dimension_uuid__is_deleted=False),mapping_uuid=mapping_uuid,status=True,customer_uuid=customer_uuid,application_uuid=application_uuid,dimension_uuid__is_deleted=False,dimension_uuid__status=True).values_list('dimension_uuid__dimension_name','parent_dimension_uuid__dimension_name').first()
            if dimension_names is None:
                logger.error(f"Dimension not found with uuid :: {mapping_uuid}")
                raise ResourceNotFoundException(ErrorMessages.DIMENSION_NOT_FOUND)
            return dimension_names
        except Exception as e:
            logger.exception(f"Error in fetching  dimension :: {e}")
            raise

    def fetch_parent_and_child_dimension_details(self, customer_uuid, application_uuid, parent_dimension_type_name):
        logger.info("In DimensionDaoImpl :: fetch_parent_and_child_dimension_details")
        try:
            return DimensionsView.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid,
                                                 dimension_type_name=parent_dimension_type_name)

        except Exception as e:
            logger.exception(f"Error in fetching parent and child dimensions :: {e}")
            return None

    def reduce_training_phrase_count_for_dimensions(self, dimension_names,parent_dimension_name, customer_uuid, application_uuid):
        """
        Reduces the training_phrases_count by 1 for specified dimension names (case insensitive).

        Args:
            dimension_names (list): List of dimension names to update
            parent_dimension_name
            customer_uuid: UUID of the customer
            application_uuid: UUID of the application

        Returns:
            int: Number of records updated
        """

        logger.info(f"Reducing training phrase count for dimensions: {dimension_names}")
        try:
            # Create Q objects for case-insensitive name matching
            name_query = Q()
            for name in dimension_names:
                name_query |= Q(dimension_uuid__dimension_name__iexact=name)
            # Build base query filters
            base_filters = Q(
                customer_uuid=customer_uuid,
                application_uuid=application_uuid,
                status=True,
                dimension_details_json__has_key='training_phrases_count'
            )
            # Add parent dimension filter using Q objects
            if parent_dimension_name:
                parent_filter = Q(parent_dimension_uuid__dimension_name__iexact=parent_dimension_name)
            else:
                # Check for NULL or empty string for parent_dimension_uuid
                parent_filter = Q(parent_dimension_uuid__isnull=True) | Q(parent_dimension_uuid='')
            # Combine all filters using AND (&) operator
            final_filter = base_filters & name_query & parent_filter

            # Apply the update with case-insensitive filtering
            update_count = DimensionCustomerApplicationMapping.objects.filter(
                final_filter
            ).update(
            dimension_details_json=RawSQL(
                """
                jsonb_set(
                    dimension_details_json,
                    '{training_phrases_count}',
                    (GREATEST(
                        COALESCE((dimension_details_json->>'training_phrases_count')::int, 0) - 1,
                        0
                    )::text)::jsonb,
                    TRUE 
                    )
                """,
                ()
            )
            )
            logger.info(f"Successfully updated {update_count} dimension mappings")
            return update_count

        except Exception as e:
            logger.exception(f"Error reducing training phrase count: {e}")
            raise