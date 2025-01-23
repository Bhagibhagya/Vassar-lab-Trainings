import inspect
import logging

from ChatBot.dao.impl.role_dao_impl import RoleDaoImpl
from ChatBot.serializers import RoleSerializer
from ChatBot.services.interface.department_service_interface import IDepartmentService

logger = logging.getLogger(__name__)


class DepartmentServiceImpl(IDepartmentService):
    """
        Service layer for handling department logic such as retrieving departments.
        Interacts with the DAO layers
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DepartmentServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside DepartmentServiceImpl - Singleton Instance ID: {id(self)}")
            self.__role_dao = RoleDaoImpl()
            self.initialized = True

    def get_all_departments(self, customer_uuid, application_uuid):
        """
            get all departments(roles from user management service) by customer_uuid and application_uuid
            Args:
                customer_uuid (str): UUID of the customer.
                application_uuid (str): UUID of the application.
            Returns:
                return list of DepartmentData/Roles data
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"Retrieving all departments by customer: {customer_uuid} and application: {application_uuid}")
        # calling dao layer to fetch departments/roles by application and customer
        roles_data = self.__role_dao.get_roles_by_customer_and_application(customer_uuid=customer_uuid,
                                                                           application_uuid=application_uuid)
        logger.debug(
            f"successfully Retrieved all departments for customer:{customer_uuid}, application:{application_uuid}")
        # Serialize the objects without converting them manually
        return RoleSerializer(roles_data, many=True).data
