import logging

from Platform.services.interface.scope_service_interface import IScopeService
from Platform.dao.impl.dimension_cam_dao_impl import DimensionCAMDaoImpl

logger = logging.getLogger(__name__)

class ScopeServiceImpl(IScopeService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScopeServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside ScopeServiceImpl")
            self.dimension_cam_dao = DimensionCAMDaoImpl()
            print(f"Inside ScopeServiceImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Retrieve scope type values based on the given scope type for the provided customer and application.
    def get_scope_type_values(self, customer_uuid, application_uuid, scope_type):
        if scope_type in ['GEOGRAPHY', 'INTENT']:
            logger.info(f"Fetching {scope_type} dimensions for customer_uuid: {customer_uuid}, application_uuid: {application_uuid}")

            # Retrieve all dimensions for the customer and application
            dimensions = list(
                self.dimension_cam_dao.get_dimensions_for_scope_by_dimension_type_name(customer_uuid, application_uuid, scope_type)
                .values('dimension_uuid', 'parent_dimension_uuid', 'dimension_name', 'has_children', 'mapping_uuid')
            )
            if not dimensions:
                logger.warning("No dimensions found.")
                return []

            # Build adjacency list and metadata
            adjacency_list, node_data, roots = self.__build_adjacency_list(dimensions)

            # Build scope_dimension_data using the adjacency list
            scope_dimension_data = self.__build_hierarchy(roots, adjacency_list, node_data)

            logger.debug(f"scope_dimension_data successfully built with {len(scope_dimension_data)} root nodes.")
            return scope_dimension_data
        elif scope_type == 'ENTITY':
            return list(self.dimension_cam_dao.get_entities_for_scope_by_application_uuid(customer_uuid, application_uuid).values('label', 'value'))
        # If scope_type is not 'GEOGRAPHY' or 'ENTITY', fetch dimensions for other scope types (INTENT, SENTIMENT, CUSTOMER_TIER)
        logger.info(f"Fetching dimensions for scope type: {scope_type}")
        return list(self.dimension_cam_dao.get_dimensions_for_scope_by_dimension_type_name(customer_uuid, application_uuid, scope_type).values('label', 'value'))

    def __build_adjacency_list(self, dimensions):
        """
        Builds an adjacency list from the dimensions and identifies root nodes.
        Returns:
            adjacency_list (dict): Maps parent_dimension_uuid to a list of child dimension_uuids.
            node_data (dict): Maps dimension_uuid to its full metadata.
            roots (list): List of root dimension_uuids (no parent).
        """
        adjacency_list = {}
        node_data = {}
        roots = []

        for dimension in dimensions:
            dimension_uuid = dimension['dimension_uuid']
            parent_uuid = dimension['parent_dimension_uuid']

            # Store dimension metadata for easy access
            node_data[dimension_uuid] = dimension

            # Populate adjacency list
            if parent_uuid not in adjacency_list:
                adjacency_list[parent_uuid] = []
            adjacency_list[parent_uuid].append(dimension_uuid)

            # Identify root nodes
            if parent_uuid is None:
                roots.append(dimension_uuid)

        return adjacency_list, node_data, roots

    def __build_hierarchy(self, roots, adjacency_list, node_data):
        """
        Recursively builds the hierarchy tree using the adjacency list and metadata.
        Args:
            roots (list): List of root dimension_uuids.
            adjacency_list (dict): Adjacency list mapping parent_uuid to child_uuids.
            node_data (dict): Metadata for each dimension.
        Returns:
            list: Hierarchy tree starting from the roots.
        """

        # Recursively builds a hierarchy tree starting from the given node.
        def _build_tree(node_uuid):
            node = node_data[node_uuid]

            # Recursively build the tree for each child.
            children = [
                _build_tree(child_uuid)
                for child_uuid in adjacency_list.get(node_uuid, [])
            ]
            return {
                'value': node['mapping_uuid'],
                'label': node['dimension_name'],
                'isLeaf': not node['has_children'],
                'disabled': False,
                'children': children
            }

        return [_build_tree(root_uuid) for root_uuid in roots]


