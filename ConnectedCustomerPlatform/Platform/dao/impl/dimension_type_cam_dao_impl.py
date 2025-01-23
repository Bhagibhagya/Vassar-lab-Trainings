from django.db.models import F

from DatabaseApp.models import DimensionTypeCustomerApplicationMapping
from Platform.dao.interface.dimension_type_cam_dao_interface import IDimensionTypeCAMDao


class DimensionTypeCAMDaoImpl(IDimensionTypeCAMDao):

    # Retrieves a dimension type mapping by mapping UUID with joined data, or all mappings of customer-application
    def get_mapped_dimension_type_by_id_or_all(self, customer_uuid, application_uuid, mapping_uuid=None):
        base_query = (DimensionTypeCustomerApplicationMapping.objects.select_related('dimension_type_uuid')
                      .defer('dimension_type_uuid__status', 'dimension_type_uuid__created_by',
                             'dimension_type_uuid__is_deleted',
                             'dimension_type_uuid__updated_by', 'dimension_type_uuid__inserted_ts',
                             'dimension_type_uuid__updated_ts', )
                      ).annotate(dimension_type_name=F('dimension_type_uuid__dimension_type_name'),
                              is_default=F('dimension_type_uuid__is_default'))

        # Retrieve all dimension type mappings of customer-application
        if mapping_uuid is None:
            return (base_query.filter(customer_uuid=customer_uuid, application_uuid=application_uuid).order_by("-inserted_ts")
                    .values('mapping_uuid', 'dimension_type_uuid', 'description', 'dimension_type_details_json',
                            'application_uuid', 'customer_uuid', 'status', 'inserted_ts', 'updated_ts', 'dimension_type_name', 'is_default')
                    )

        # Retrieve single dimension type mapping by mapping UUID
        return base_query.filter(mapping_uuid=mapping_uuid, customer_uuid=customer_uuid, application_uuid=application_uuid).first()

    # Saves the given DimensionTypeCustomerApplicationMapping instance to the database.
    def save_dimension_type_mapping(self, dimension_type_mapping):
        dimension_type_mapping.save()

    # Deletes the given DimensionTypeCustomerApplicationMapping instance from the database.
    def delete_dimension_type_mapping(self, customer_uuid, application_uuid, mapping_uuid):
        return DimensionTypeCustomerApplicationMapping.objects.filter(customer_uuid=customer_uuid,
                                                                      application_uuid=application_uuid,
                                                                      mapping_uuid=mapping_uuid).delete()
