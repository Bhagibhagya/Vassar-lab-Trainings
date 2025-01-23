from abc import ABC, abstractmethod

class EmailServerDaoInterface(ABC):

    @abstractmethod
    def get_email_server(self, smtp_filter):
        pass