from abc import ABC, abstractmethod


class EventHubClientCreationInterface(ABC):

    @abstractmethod
    def create_producer_client(self):
        pass

    @abstractmethod
    def create_consumer_client(self):
        pass
