from abc import ABC, abstractmethod

from ChatBot.dataclasses.application_data import ApplicationData


class IApplicationDao(ABC):
    """
        Interface for managing Application.
        This interface provides abstract methods for creating, updating, deleting, retrieving application
    """
    @abstractmethod
    def create_application(self, application_data: ApplicationData):
        """
            create a application record
            Args:
                application_data (ApplicationData): ApplicationData dataclass instance
            Returns:
                returns created application queryset
        """
