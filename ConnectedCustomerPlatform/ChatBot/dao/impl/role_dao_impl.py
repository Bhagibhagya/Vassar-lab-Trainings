import inspect
import logging

from ChatBot.constant.constants import RoleConstants
from ChatBot.dao.interface.role_dao_interface import IRoleDao

from ChatBot.dataclasses.role_data import RoleData

from DatabaseApp.models import Roles, Customers, Applications

logger = logging.getLogger(__name__)


class RoleDaoImpl(IRoleDao):
    """
            Data Access Object (DAO) for Role operations.
            Implements the Singleton pattern to ensure only one instance of this class is created.
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(RoleDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
                Initialize the RoleDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside RoleDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def create_role(self, role_data: RoleData):
        """
            create a role record
            Args:
                role_data (RoleData): RoleData dataclass instance
            Returns:
                returns created role queryset
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"creating a role:: role_data :: {role_data.to_dict()}")
        # Use the RoleData fields to create a new Roles record
        role = Roles.objects.create(
            role_uuid=role_data.role_uuid,
            role_name=role_data.role_name,
            role_details_json=role_data.role_details_json,
            application_uuid=role_data.application_uuid,
            customer_uuid=role_data.customer_uuid,
            description=role_data.description,
            status=role_data.status,
            created_by=role_data.created_by,
            updated_by=role_data.updated_by
        )
        return role

    def get_roles_by_customer_and_application(self, customer_uuid, application_uuid):
        """
            fetch roles by application and customer and excludes default customer admin role
            Args:
                customer_uuid (str): unique identifier of customer
                application_uuid (str): unique identifier of application
            Returns:
                returns roles queryset data matching application and customer
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"fetching roles by customer:{customer_uuid}, application:{application_uuid}")
        customer_name = Customers.objects.filter(cust_uuid=customer_uuid).values_list('cust_name', flat=True).first()
        application_name = Applications.objects.filter(application_uuid=application_uuid).values_list(
            'application_name', flat=True).first()
        default_admin_role_name_to_exclude = customer_name + " " + application_name + " Admin"
        return Roles.objects.filter(application_uuid=application_uuid, customer_uuid=customer_uuid,
                                    status=True).exclude(
            role_name=default_admin_role_name_to_exclude
        ).values(RoleConstants.ROLE_UUID, RoleConstants.ROLE_NAME)
