import uuid
import logging
from dataclasses import asdict
from typing import Set

from django.db.models import OuterRef, Q, Exists, F, Subquery
from django.db import connection

from DatabaseApp.models import DimensionCustomerApplicationMapping, Applications, Customers, CustomerApplicationMapping, \
    Entities, Dimension

from EmailApp.Exceptions.api_exception import ResourceNotFoundException
from Platform.dao.interface.dimension_cam_dao_interface import IDimensionCAMDao
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages

# Initialize logger
logger = logging.getLogger(__name__)


class DimensionCAMDaoImpl(IDimensionCAMDao):

    # Saves the given DimensionTypeCustomerApplicationMapping instance to the database.
    def save_dimension_mapping(self, dimension_mapping):
        logger.info(f"Saving dimension mapping instance - Mapping UUID: {dimension_mapping.mapping_uuid}")
        dimension_mapping.save()

    # Gets or creates a dimension mapping based on the provided uuid_data, validated data, dimension, and parent dimension.
    def get_or_create_dimension_mapping(self, uuid_data, validated_data, dimension, parent_dimension=None):
        customer_uuid, application_uuid, user_uuid = uuid_data

        logger.info(f"Attempting to get or create dimension mapping for Customer: {customer_uuid}, "
                    f"Application: {application_uuid}, Dimension: {dimension.dimension_uuid}")

        # Retrieve or create the dimension mapping
        dimension_details = validated_data.get('dimension_details_json')
        dimension_details_json = asdict(dimension_details) if dimension_details is not None else None
        dimension_mapping, created = DimensionCustomerApplicationMapping.objects.get_or_create(
            dimension_uuid=dimension,
            application_uuid=Applications(application_uuid),
            customer_uuid=Customers(customer_uuid),
            parent_dimension_uuid=parent_dimension,
            defaults={
                'mapping_uuid': str(uuid.uuid4()),
                'description': validated_data.get('description'),
                'dimension_details_json': dimension_details_json,
                'created_by': user_uuid,
                'updated_by': user_uuid,
            }
        )

        return dimension_mapping, created

    # Retrieves all dimensions that belong to the specified dimension type for the given customer and application.
    def get_dimensions_by_dimension_type(self, customer_uuid, application_uuid, dimension_type_uuid):
        logger.info(f"Fetching dimensions for Customer UUID: {customer_uuid}, "
                    f"Application UUID: {application_uuid}, Dimension Type UUID: {dimension_type_uuid}")

        # Query to fetch the dimension mappings
        dimensions = (DimensionCustomerApplicationMapping.objects
                      .select_related('dimension_uuid', 'parent_dimension_uuid')
                      .filter(
            Q(customer_uuid=customer_uuid,
              application_uuid=application_uuid,
              dimension_uuid__dimension_type_uuid=dimension_type_uuid) &
            (Q(dimension_uuid__dimension_type_uuid__dimension_type_name='GEOGRAPHY',
               parent_dimension_uuid__isnull=False) |
             ~Q(dimension_uuid__dimension_type_uuid__dimension_type_name='GEOGRAPHY'))
        ).annotate(
            dimension_name=F('dimension_uuid__dimension_name'), is_default=F('dimension_uuid__is_default'),
            parent_dimension_name=F('parent_dimension_uuid__dimension_name'),
            dimension_type_uuid=F('dimension_uuid__dimension_type_uuid')
        ).values(
            'mapping_uuid', 'dimension_uuid', 'dimension_type_uuid', 'parent_dimension_uuid', 'description',
            'dimension_details_json', 'dimension_name', 'is_default', 'parent_dimension_name',
            'customer_uuid', 'application_uuid', 'inserted_ts', 'updated_ts', 'status'
        ).order_by('-inserted_ts'))

        # Log the number of dimensions retrieved
        logger.info(f"Retrieved {dimensions.count()} dimensions for Customer UUID: {customer_uuid}, "
                    f"Application UUID: {application_uuid}, Dimension Type UUID: {dimension_type_uuid}")

        return dimensions

    # Retrieves a dimension type mapping based on the specified customer, application, mapping UUID, and checks if parent dimension.
    def get_dimension_mapping_by_id(self, customer_uuid, application_uuid, mapping_uuid, fetch_is_parent=False):
        logger.info(f"Fetching dimension mapping for Customer UUID: {customer_uuid}, "
                    f"Application UUID: {application_uuid}, Mapping UUID: {mapping_uuid}, Is Parent: {fetch_is_parent}")

        # Start building the base queryset
        query = (
            DimensionCustomerApplicationMapping.objects
            .select_related('dimension_uuid', 'parent_dimension_uuid')
            .filter(customer_uuid=customer_uuid, application_uuid=application_uuid, mapping_uuid=mapping_uuid)
        )

        # Conditionally add the Exists annotation if checking for parent status
        if fetch_is_parent:
            query = query.annotate(
                is_parent=Exists(
                    DimensionCustomerApplicationMapping.objects.filter(
                        parent_dimension_uuid=OuterRef('dimension_uuid'),
                        customer_uuid=customer_uuid,
                        application_uuid=application_uuid,
                    )
                )
            )

        # Retrieve the first matching record (or None if not found)
        return query.first()

    # Retrieves geography dimensions (e.g., countries, states) based on the specified parent dimension for the given customer and application.
    def get_geography_dimensions(self, customer_uuid, application_uuid, parent_dimension_uuid=None):
        logger.info(f"Retrieving geography dimensions for Customer UUID: {customer_uuid}, "
                    f"Application UUID: {application_uuid}, Parent Dimension UUID: {parent_dimension_uuid}")

        # Construct the filter query to fetch the geography dimensions
        filter_query = Q(
            customer_uuid=customer_uuid,
            parent_dimension_uuid=parent_dimension_uuid,
            status=True,
            dimension_uuid__dimension_type_uuid__dimension_type_name='GEOGRAPHY'
        )

        logger.debug(f"Filter Query: {filter_query}")

        # Fetch the dimension mappings ensuring customer-application mapping is present
        geography_dimensions = (
            DimensionCustomerApplicationMapping.objects
            .filter(
                filter_query,
                Exists(CustomerApplicationMapping.objects.filter(customer=OuterRef('customer_uuid'),
                                                                 application=OuterRef('application_uuid')))
            )
            .select_related('dimension_uuid')
            .distinct('dimension_uuid')
            .annotate(dimension_name=F('dimension_uuid__dimension_name'),
                      dimension_type_uuid=F('dimension_uuid__dimension_type_uuid'),
                      is_default=F('dimension_uuid__is_default'),
                      parent_dimension_name=F('parent_dimension_uuid__dimension_name'))
            .values('mapping_uuid', 'dimension_name', 'dimension_type_uuid', 'is_default', 'parent_dimension_name',
                    'description', 'dimension_details_json', 'dimension_uuid', 'parent_dimension_uuid',
                    'application_uuid', 'customer_uuid', 'updated_ts')
        )

        logger.info(
            f"Retrieved {geography_dimensions.count()} geography dimensions for Customer UUID: {customer_uuid}, " + f"Application UUID: {application_uuid}")

        return geography_dimensions

    # Function to get dimension values for scope
    def get_dimensions_for_scope_by_dimension_type_name(self, customer_uuid, application_uuid, dimension_type_name):
        # Fetch all geography dimensions for the specified customer and application
        logger.info(f"Fetching dimensions for scope: customer_uuid={customer_uuid}, application_uuid={application_uuid}, dimension_type_name={dimension_type_name}")
        # Base Query
        base_query = DimensionCustomerApplicationMapping.objects.filter(
            Q(customer_uuid=customer_uuid) &
            Q(application_uuid=application_uuid) &
            Q(status=True)
        ).annotate(
            dimension_name=F('dimension_uuid__dimension_name'),
            parent_dimension_name=F('parent_dimension_uuid__dimension_name'),
            label=F('dimension_uuid__dimension_name'), value=F('mapping_uuid'),
            has_children=Exists(
                DimensionCustomerApplicationMapping.objects.filter(
                    parent_dimension_uuid=OuterRef('dimension_uuid'),
                    customer_uuid=customer_uuid,
                    application_uuid=application_uuid,
                )
            )
        )

        # Adjust filter conditions based on `dimension_type_name`
        if dimension_type_name == 'INTENT':
            result = base_query.filter(
                Q(dimension_uuid__dimension_type_uuid__dimension_type_name__in=['INTENT', 'SUB_INTENT'])
            )
        else:
            result = base_query.filter(
                Q(dimension_uuid__dimension_type_uuid__dimension_type_name=dimension_type_name)
            )
        return result

    # Function to get Entity values for scope
    def get_entities_for_scope_by_application_uuid(self, customer_uuid, application_uuid):
        # Fetch all entities for the specified customer and application
        logger.info(f"Fetching entities from scope: customer_uuid={customer_uuid}, application_uuid={application_uuid}")
        return Entities.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid
        ).annotate(
            label=F('entity_name'),
            value=F('entity_uuid')
        )

    # Deletes the given DimensionTypeCustomerApplicationMapping instance from the database.
    def delete_dimension_mapping(self, dimension_mapping):
        logger.info(f"Attempting to delete dimension mapping: {dimension_mapping.mapping_uuid}")

        # Perform the deletion
        dimension_mapping.delete()

        logger.info(f"Successfully deleted dimension mapping: {dimension_mapping.mapping_uuid}")

    # Deleting the given dimension_uuid from user scope
    def delete_dimension_from_user_scope(self, mapping_uuid, application_uuid, customer_uuid):
        logger.info("Attempting to update the user scope in usermgmt")

        query = """
        UPDATE usermgmt.user_role_mapping
        SET user_role_details_json = jsonb_set(
            user_role_details_json,
            '{scope}',
            (
                SELECT jsonb_agg(
                    jsonb_set(
                        scope_elem,
                        '{scopeValue}',
                        (scope_elem->'scopeValue') - '%s'
                    )
                )
                FROM jsonb_array_elements(user_role_details_json->'scope') AS scope_elem
            )
        )
        WHERE user_role_details_json->'scope' @> '[{"scopeValue": ["%s"]}]' and role_id 
        in (select role_id from usermgmt.user_details_view where application_id='%s' 
        and customer_id='%s');

        """

        try:
            with connection.cursor() as cursor:
                native_query = query % (mapping_uuid, mapping_uuid, application_uuid, customer_uuid)
                logger.info("Executing query: %s", native_query)

                cursor.execute(native_query)
                logger.info("User scope updated successfully")
        except (Exception) as error:
            logger.error("Error while updating user scope: %s", error)
            raise CustomException(ErrorMessages.SCOPE_UPDATE_FAILED)


    def fetch_dimension_mappings_with_dimension_names(self, application_uuid : str, customer_uuid : str, dimension_names : Set[str]):
        """
        Fetch dimension mappings and organize them into a dictionary in a single ORM call.

        Args:
            application_uuid (str): The application UUID.
            customer_uuid (str): The customer UUID.
            dimension_names (set): Set of dimension names to filter.

        Returns:
            dict: A dictionary mapping (parent_dimension_name, child_dimension_name) to mapping objects.
        """
        logger.info("In DimensionCamDAOImpl :: fetch_dimension_mappings_with_dimension_names")
        # Validate inputs
        if not application_uuid or not customer_uuid or not dimension_names:
            raise ValueError("Invalid input: application_uuid, customer_uuid, and dimension_names are required.")
        try:
            # Subquery to fetch the parent dimension's name
            parent_name_subquery = Dimension.objects.filter(
                dimension_uuid=OuterRef('parent_dimension_uuid')
            ).values('dimension_name')[:1]
            query = Q()
            for name in dimension_names:
                query |= Q(dimension_uuid__dimension_name__iexact=name)
            # Query to fetch the required data
            mappings = DimensionCustomerApplicationMapping.objects.filter(
                query,
                application_uuid=application_uuid,
                customer_uuid=customer_uuid
            ).annotate(
                child_dimension_name=F('dimension_uuid__dimension_name'),  # Child dimension name
                parent_dimension_name=Subquery(parent_name_subquery)  # Parent dimension name
            )

            # Convert the query result into the desired dictionary
            mapping_dict = {}
            for mapping in mappings:
                parent_dimension_name = None
                if mapping.parent_dimension_name is not None:
                    parent_dimension_name = mapping.parent_dimension_name.upper()
                child_dimension_name = mapping.child_dimension_name.upper()
                mapping_dict[(parent_dimension_name, child_dimension_name)] = mapping

            return mapping_dict

        except Exception as e:
            logger.error(f"Error occurred in fetch_dimension_mappings_with_dimension_names: {e}")
            raise CustomException("Error occurred while fetch_dimension_mappings_with_dimension_names")

    def perform_bulk_update(self, dimension_updates : list):
        """
            Performs a bulk update on DimensionCustomerApplicationMapping objects.

            Updates the `dimension_details_json` and `updated_ts` fields for the given list of
            DimensionCustomerApplicationMapping objects in a single query.

            Args:
                dimension_updates (list): List of objects to be updated with new values.

            Returns:
                None
        """
        logger.info("In DimensionCamDAOImpl :: perform_bulk_update")

        try:
            # Perform bulk update
            DimensionCustomerApplicationMapping.objects.bulk_update(dimension_updates, ['dimension_details_json', 'updated_ts'])
        except Exception as e:
            logger.error(f"Error occurred in perform_bulk_update: {e}.")
            raise CustomException("Error occurred in perform_bulk_update.")

    def fetch_dimension_mapping_by_parent_child_names(self, customer_uuid, application_uuid, parent_dimension_name,
                                                      child_dimension_name):
        """
        Fetch dimension mapping based on customer, application, and dimension names.

        Args:
            customer_uuid: UUID of the customer
            application_uuid: UUID of the application
            parent_dimension_name: Name of the parent dimension (can be None)
            child_dimension_name: Name of the child dimension

        Returns:
            DimensionCustomerApplicationMapping object
        """
        logger.info("In DimensionCustomerApplicationMapping :: fetch_dimension_mapping_by_parent_child_names")
        try:
            # Start with base query filters
            query_filters = {
                'customer_uuid': customer_uuid,
                'application_uuid': application_uuid,
                'status': True,
                'dimension_uuid__is_deleted': False,
                'dimension_uuid__status':True,
                'dimension_uuid__dimension_name': child_dimension_name
            }

            # Add parent dimension filter if parent_dimension_name is provided
            if parent_dimension_name is not None:
                query_filters['parent_dimension_uuid__dimension_name'] = parent_dimension_name
                query_filters['parent_dimension_uuid__status'] = True
                query_filters['parent_dimension_uuid__is_deleted'] = False

            # Execute query and get the single record
            dimension_mapping = DimensionCustomerApplicationMapping.objects.get(**query_filters)

            return dimension_mapping

        except DimensionCustomerApplicationMapping.DoesNotExist:
            logger.error(f"No dimension mapping found for customer: {customer_uuid}, application: {application_uuid}, "
                         f"parent: {parent_dimension_name}, child: {child_dimension_name}")
            return None
        except Exception as e:
            # Handle any other exceptions
            logger.error(f"Error while getting the dimension mapping: {e}")
            return None

    def fetch_dimension_parent_dimension_name_by_dimension_uuid(self, mapping_uuid, customer_uuid, application_uuid):
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
            dimension_names = DimensionCustomerApplicationMapping.objects.filter(Q(parent_dimension_uuid__isnull=True) |
                                                                                 Q(parent_dimension_uuid__isnull=False,
                                                                                   parent_dimension_uuid__status=True,
                                                                                   parent_dimension_uuid__is_deleted=False),
                                                                                 mapping_uuid=mapping_uuid, status=True,
                                                                                 customer_uuid=customer_uuid,
                                                                                 application_uuid=application_uuid,
                                                                                 dimension_uuid__is_deleted=False,
                                                                                 dimension_uuid__status=True).values_list(
                'dimension_uuid__dimension_name', 'parent_dimension_uuid__dimension_name').first()
            if dimension_names is None:
                logger.error(f"Dimension not found with uuid :: {mapping_uuid}")
                raise ResourceNotFoundException(ErrorMessages.DIMENSION_NOT_FOUND)
            return dimension_names
        except Exception as e:
            logger.exception(f"Error in fetching  dimension :: {e}")
            raise

    def update_dimension_details_json_in_dimension_mapping(self, mapping_uuid, dimension_details_json):
        """
        updates email_activity in email_conversation
        Args:
            mapping_uuid:
            dimension_details_json:

        Returns:

        """
        logger.info("In EmailConversationDaoImpl :: update_email_activity_in_email_conversation")

        try:
            updated_count = DimensionCustomerApplicationMapping.objects.filter(mapping_uuid=mapping_uuid).update(
                dimension_details_json=dimension_details_json)

            if updated_count == 0:
                logger.error(f"DimensionCustomerMapping with UUID {mapping_uuid} does not exist.")
                raise ResourceNotFoundException(
                    f"DimensionCustomerApplicationMapping with UUID {mapping_uuid} does not exist.")
        except Exception as e:
            logger.error(f"An error occurred while updating dimension_details_json: {e}")
            raise CustomException(f"Error in updating dimension_details_json with mapping uuid :: {mapping_uuid}")

    def fetch_dimension_name_by_mapping_uuid(self, mapping_uuid):
        logger.info("In DimensionCAMDaoImpl :: fetch_dimension_name_by_mapping_uuid")

        try:
            return DimensionCustomerApplicationMapping.objects.filter(mapping_uuid=mapping_uuid).values_list(
                'dimension_uuid__dimension_name', flat=True).first()
        except Exception as e:
            logger.error(f"Error while fetching DimensionCustomerApplicationMapping :: {e}")
            raise
    
    def delete_dimension_mappings(self, parent_dimension_uuid, customer_uuid, application_uuid):
        """
        Deletes all records in DimensionCustomerApplicationMapping that match the given
        parent_dimension_uuid, customer_uuid, and application_uuid.

        Args:
            parent_dimension_uuid (str): The UUID of the parent dimension.
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            int: Number of records deleted.
        """
        try:
            # Filter and delete records
            deleted_count, _ = DimensionCustomerApplicationMapping.objects.filter(
                parent_dimension_uuid=parent_dimension_uuid,
                customer_uuid=customer_uuid,
                application_uuid=application_uuid
            ).delete()

            logger.info(f"Deleted {deleted_count} records for parent_dimension_uuid: {parent_dimension_uuid}, "
                        f"customer_uuid: {customer_uuid}, application_uuid: {application_uuid}")
            return deleted_count
        except Exception as e:
            logger.exception(f"Error deleting records: {e}")
            raise

    # Recursively deletes parent dimensions that do not have any child dimensions in the hierarchy.
    def delete_parent_dimension_mappings(self, parent_dimension_uuid, dimension_type_name, customer_uuid, application_uuid):
        # Only proceed if the dimension type is "GEOGRAPHY"
        if dimension_type_name != "GEOGRAPHY":
            logger.info(f"Dimension type '{dimension_type_name}' is not 'GEOGRAPHY'. No action taken.")
            return

        logger.info(
            f"Starting deletion of parent dimension mappings for parent_dimension_uuid: {parent_dimension_uuid}, "
            f"dimension_type: {dimension_type_name}, customer_uuid: {customer_uuid}, application_uuid: {application_uuid}")
        while parent_dimension_uuid is not None:
            logger.info(f"Fetching parent dimension with UUID: {parent_dimension_uuid}")
            # Fetch the parent dimension with metadata on whether it's a parent of another dimension
            parent_dimension = DimensionCustomerApplicationMapping.objects.filter(
                dimension_uuid=parent_dimension_uuid,
                customer_uuid=customer_uuid,
                application_uuid=application_uuid
            ).annotate(
                is_parent=Exists(
                    DimensionCustomerApplicationMapping.objects.filter(
                        parent_dimension_uuid=OuterRef('dimension_uuid'), customer_uuid=customer_uuid, application_uuid=application_uuid
            ))).first()

            if parent_dimension is None:
                logger.warning(f"No parent dimension found for UUID: {parent_dimension_uuid}. Stopping deletion process.")
                break

            # Update parent_dimension_uuid for the next iteration
            parent_dimension_uuid = parent_dimension.parent_dimension_uuid

            # Check if the current dimension is a parent of another dimension. If not delete the dimension
            if parent_dimension.is_parent:
                parent_dimension_uuid = None
            else:
                # Capture the mapping UUID before deletion
                mapping_uuid = parent_dimension.mapping_uuid
                parent_dimension.delete()
                # Remove the mapping from the user's scope
                self.delete_dimension_from_user_scope(mapping_uuid, application_uuid, customer_uuid)

    def update_parent_dimension_in_dimension_mapping(self, parent_dimension_uuid,updated_parent_dimension_uuid,customer_uuid,application_uuid):
        """
        updates parent_dimension
        Args:
            parent_dimension_uuid:
            customer_uuid:
            application_uuid:

        Returns:

        """
        logger.info("In EmailConversationDaoImpl :: update_parent_dimension_in_dimension_mapping")

        try:
            updated_count = DimensionCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,application_uuid=application_uuid,parent_dimension_uuid=parent_dimension_uuid).update(parent_dimension_uuid=updated_parent_dimension_uuid)

            if updated_count == 0:
                logger.error(f"DimensionCustomerMapping with  PARENT DIMENSION UUID {parent_dimension_uuid} does not exist.")
        except Exception as e:
            logger.error(f"An error occurred while updating dimension_details_json: {e}")
            raise CustomException(f"Error in updating parent dimension")
    def fetch_intent_with_sub_intents(self, customer_uuid, application_uuid):
        """
        Fetch all dimensions for a specific customer and application and organize them into a dictionary.

        The dictionary maps parent dimensions (Intents) to their corresponding child dimensions (Sub-Intents).
        If a dimension has no parent, it is considered a parent itself.

        Args:
            customer_uuid (str): The unique identifier of the customer.
            application_uuid (str): The unique identifier of the application.

        Returns:
            dict: A dictionary in the format:
                  {
                      "Parent Dimension 1": ["Child Dimension 1", "Child Dimension 2"],
                      "Parent Dimension 2": ["Child Dimension 3", "Child Dimension 4"],
                      ...
                  }
        """
        try:
            # Fetch mappings with related dimension and parent dimension using joins
            mappings = DimensionCustomerApplicationMapping.objects.select_related(
                'dimension_uuid', 'parent_dimension_uuid'
            ).filter(status=True, customer_uuid = customer_uuid, application_uuid = application_uuid)

            # Organize the data into a dictionary
            intent_sub_intent_mapping = dict()

            for mapping in mappings:

                parent_name = (
                    mapping.parent_dimension_uuid.dimension_name
                    if mapping.parent_dimension_uuid
                    else mapping.dimension_uuid.dimension_name  # Use self-name if no parent
                )
                child_name = mapping.dimension_uuid.dimension_name

                # Initialize the parent list if necessary and add the child
                intent_sub_intent_mapping.setdefault(parent_name.upper(), [])
                if parent_name != child_name:
                    intent_sub_intent_mapping.setdefault(parent_name.upper(),[]).append(child_name.upper())

            return intent_sub_intent_mapping

        except Exception as e:
            logger.error(f"Error fetching dimensions: {e}")
            raise CustomException("Error Fetching dimensions")
