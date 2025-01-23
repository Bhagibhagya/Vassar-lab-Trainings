from abc import ABC, abstractmethod

from ChatBot.dataclasses.role_data import RoleData


class IRoleDao(ABC):
    """
        Interface for managing Roles.
        This interface provides abstract methods for creating, updating, deleting, retrieving roles
    """

    @abstractmethod
    def create_role(self, role_data: RoleData):
        """
            create a role record
            Args:
                role_data (RoleData): RoleData dataclass instance
            Returns:
                returns created role queryset
        """

    @abstractmethod
    def get_roles_by_customer_and_application(self, customer_uuid, application_uuid):
        """
            fetch roles by application and customer and excludes default customer admin role
            Args:
                customer_uuid (str): unique identifier of customer
                application_uuid (str): unique identifier of application
            Returns:
                returns roles queryset data matching application and customer
        """
