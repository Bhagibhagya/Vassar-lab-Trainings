from abc import ABC, abstractmethod

from ChatBot.dataclasses.user_data import UserData


class IUserDao(ABC):
    
    """
        Interface for managing Users.
        This interface provides abstract methods for creating, updating, deleting, retrieving users
    """
    
    @abstractmethod
    def create_user(self, user_data: UserData):
        """
                create a user record
                Args:
                    user_data (UserData) : UserData dataclass instance
                Returns:
                    returns created user queryset
        """
        pass
    
    @abstractmethod
    def get_user_info(self, user_id: str) -> tuple[str, str, str, str]:
        """
            Args:
                user_id (str): The unique identifier for the user.

            Returns:
                tuple[str, str, str, str]: A tuple containing user information.
        """
        pass