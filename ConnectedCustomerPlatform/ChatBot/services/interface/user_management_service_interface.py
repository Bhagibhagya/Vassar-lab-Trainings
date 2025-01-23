from abc import ABC, abstractmethod

from ChatBot.dataclasses.make_request_data import MakeRequestData


class IUserManagementService(ABC):
    """
        Interface for calling user management api
        This interface provides abstract methods for calling user management apis
    """

    @abstractmethod
    def make_request(self, request_data: MakeRequestData):
        """
            calls user management api
            Args:
                 request_data (MakeRequestData): Dataclass containing request method, URL, headers, payload, and query parameters.
            Returns:
                returns response object
            Raises:
                CustomException : is any exception occured
        """
