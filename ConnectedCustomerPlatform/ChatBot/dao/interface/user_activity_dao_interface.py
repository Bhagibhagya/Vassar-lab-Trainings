from abc import ABC, abstractmethod
from datetime import datetime


class UserActivityDaoInterface(ABC):
    
    @abstractmethod
    def add_feedback_activity(self, user_id: str, customer_uuid: str, application_uuid: str, question_uuid: str, answer_uuid: str, feedback: str) -> None:
        """
        Args:
            user_id (str): The unique identifier for the user providing feedback.
            customer_uuid (str): The unique identifier for the customer.
            application_uuid (str): The unique identifier for the application.
            question_uuid (str): The unique identifier for the question being answered.
            answer_uuid (str): The unique identifier for the answer given.
            feedback (str): The feedback provided by the user.
        
        Returns:
            None
        """
        pass
    
    @abstractmethod
    def get_leaderboard(self, customer_uuid: str) -> list[tuple[str, str, str, int]]:
        """
        Args:
            customer_uuid (str): The unique identifier for the customer.

        Returns:
            list[tuple[str, str, str, int]]: A list of tuples containing leaderboard entries.
        """
        pass
    
    @abstractmethod
    def get_timeseries(self, user_id: str, days: int) -> list[dict]:
        """
        Args:
            user_id (str): The unique identifier for the user.
            days (int): The number of days for which to retrieve time-series data.

        Returns:
            list[dict]: A list of dictionaries with time-series data.
        """
        pass
    
    @abstractmethod
    def get_query_activity_count(self, user_id: str) -> int:
        """
        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            int: The count of query activities for the user.
        """
        pass
    
    @abstractmethod
    def get_feedback_questions(self, user_id: str) -> list[tuple[str, str]]:
        """
        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            list[tuple[str, str]]: A list of tuples, each containing question details related to feedback.
        """
        pass
    
    @abstractmethod
    def get_query_activity_count_for_date_range(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        """
        Args:
            user_id (str): The unique identifier for the user.
            start_date (datetime): The start date for the date range.
            end_date (datetime): The end date for the date range.

        Returns:
            int: The count of query activities for the user within the specified date range.
        """
        pass