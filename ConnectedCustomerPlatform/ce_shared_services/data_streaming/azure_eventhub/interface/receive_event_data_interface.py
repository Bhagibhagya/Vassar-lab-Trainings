from abc import ABC, abstractmethod


class EventHubConsumerClient(ABC):

    @abstractmethod
    def start_consumer(self, callback_method):
        pass

    @abstractmethod
    def receive_event(self,callback_method):
        pass

    @abstractmethod
    def receive_event_batch(self, callback_method):
        pass
