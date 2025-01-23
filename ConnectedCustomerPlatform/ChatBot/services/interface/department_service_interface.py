from abc import ABC, abstractmethod


class IDepartmentService(ABC):
    """
        Interface for managing departments.
        This interface provides abstract methods for retrieving the departments
    """

    @abstractmethod
    def get_all_departments(self, customer_uuid, application_uuid):
        """
            get all departments(roles from user management service) by customer_uuid and application_uuid

            :param customer_uuid: UUID of the customer.
            :param application_uuid: UUID of the application.

            :return : return list of DepartmentData(dataclass/pojo) objects
        """
