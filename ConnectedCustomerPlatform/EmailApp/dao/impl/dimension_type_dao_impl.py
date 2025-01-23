from DatabaseApp.models import DimensionTypeCustomerApplicationMapping
from EmailApp.dao.interface.dimension_type_dao_interface import IDimensionTypeDao


class DimensionTypeDaoImpl(IDimensionTypeDao):
    def get_dimension_type_uuid_by_name(self,dimension_type_name : str,customer_uuid : str,application_uuid : str)->str:
        """
        returns dimension_type_uuid by dimension_type_name for given customer_uuid and application_uuid
        """
        return (DimensionTypeCustomerApplicationMapping.objects
            .filter(
                application_uuid=application_uuid,
                customer_uuid=customer_uuid,
                status=True,
                dimension_type_uuid__dimension_type_name=dimension_type_name,
                dimension_type_uuid__status=True,
                dimension_type_uuid__is_deleted=False,
            )
            .values_list('dimension_type_uuid',flat=True)).first()