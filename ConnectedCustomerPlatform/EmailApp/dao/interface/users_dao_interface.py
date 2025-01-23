from abc import ABC, abstractmethod


class UsersDaoInterface(ABC):

    @abstractmethod
    def get_user(self, user_uuid):
        pass

    @abstractmethod
    def get_users_name(self, user_uuids):
        # Raw SQL query to fetch user details based on user UUIDs
        pass