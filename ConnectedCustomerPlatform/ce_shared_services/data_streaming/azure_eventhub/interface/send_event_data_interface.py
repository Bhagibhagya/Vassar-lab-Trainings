from abc import ABC, abstractmethod

class EventHubProducerInterface(ABC):
    @abstractmethod
    def send_event_data_batch(self, event_data):
        pass

    @abstractmethod
    def send_event_data_batch_with_limited_size(self, event_data_list):
        pass

    @abstractmethod
    def send_event_data_batch_with_partition_key(self, event_data, partition_key):
        pass

    @abstractmethod
    def send_event_data_batch_with_partition_id(self, event_data, partition_id):
        pass

    @abstractmethod
    def send_event_data_batch_with_properties(self, event_data, properties):
        pass

    @abstractmethod
    def send_event_data_list(self, event_data_list):
        pass

    @abstractmethod
    def close(self):
        pass
