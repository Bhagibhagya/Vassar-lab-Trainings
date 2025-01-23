from abc import ABC, abstractmethod


class StreamingService(ABC):
    @abstractmethod
    def create_producer(self, async_mode: bool = False):
        pass

    @abstractmethod
    def create_consumer(self, async_mode: bool = False):
        pass

    @abstractmethod
    def get_singleton_producer(self):
        pass
