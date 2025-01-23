import uuid

from DatabaseApp.models import DimensionType, Dimension, DimensionCustomerApplicationMapping
from Platform.dao.interface.dimension_type_dao_interface import IDimensionTypeDao


class DimensionTypeDaoImpl(IDimensionTypeDao):
    # Retrieves all default dimension types from the database.
    def get_default_dimension_types(self):
        return DimensionType.objects.filter(is_default=True, is_deleted=False).values()

    # Retrieves all default dimensions associated with the specified dimension type UUID.
    def get_default_dimensions(self, dimension_type_uuid):
        return Dimension.objects.filter(is_default=True, is_deleted=False, dimension_type_uuid=dimension_type_uuid)

    # Saves the given DimensionType instance to the database.
    def save_dimension_type(self, dimension_type):
        dimension_type.save()

    # Bulk creates a list of dimension mappings to the database.
    def bulk_create_dimensions(self, dimension_mappings):
        DimensionCustomerApplicationMapping.objects.bulk_create(dimension_mappings)

    # Retrieve or create a DimensionType based on the name and user information.
    def get_or_create_dimension_type(self, dimension_type_name, user_id):
        return DimensionType.objects.get_or_create(
            dimension_type_name__iexact=dimension_type_name,
            defaults={
                'dimension_type_name': dimension_type_name,
                'dimension_type_uuid': str(uuid.uuid4()),
                'created_by': user_id,
                'updated_by': user_id,
            }
        )
