from abc import ABC, abstractmethod


class UserActivityServiceInterface(ABC):
    
    @abstractmethod
    def get_user_chats(self, customer_uuid: str, user_id: str) -> list[dict[str, str]]:
        """
        Args:
            customer_uuid (str): The unique identifier for the customer.
            application_uuid (str): The unique identifier for the application.
            user_id (str): The unique identifier for the user.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing chat information for the user.
        """
        pass
    
    @abstractmethod
    def get_leaderboard(self, customer_uuid: str) -> list[dict]:
        """
        Args:
            customer_uuid (str): The unique identifier for the customer.

        Returns:
            list[dict]: A list of dictionaries containing leaderboard data.
        """
        pass
    
    @abstractmethod
    def get_timeseries(self, user_id: str) -> dict:
        """
        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            dict: A dictionary containing time-series data for the user.
        """
        pass
    
    @abstractmethod
    def get_feedback_details(self, user_id: str) -> dict:
        """
        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            dict: A dictionary containing detailed feedback information for the user.
        """
        pass
    
    @abstractmethod
    def get_query_activity_stats(self, user_id: str) -> list[dict]:
        """
        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            list[dict]: A list of dictionaries containing query activity statistics for the user.
        """
        pass
    
    @abstractmethod
    def get_user_info(self, user_id: str) -> dict:
        """
        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            dict: A dictionary containing user information.
        """
        pass
