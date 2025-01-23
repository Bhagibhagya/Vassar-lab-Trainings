from abc import ABC, abstractmethod


class IUsersDetailsViewDaoInterface(ABC):

    @abstractmethod
    def get_role_name_of_user(self, user_uuid,customer_uuid,application_uuid):
        """Returns role_name, application_name, customer_name for the user and application"""
        pass