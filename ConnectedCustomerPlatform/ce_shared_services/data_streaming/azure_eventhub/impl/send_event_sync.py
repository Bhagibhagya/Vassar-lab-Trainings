import logging

from azure.eventhub import EventData
from azure.eventhub.exceptions import EventHubError

from ..interface.send_event_data_interface import EventHubProducerInterface
from ..utils.event_data_validator import validate_event_data

logger = logging.getLogger(__name__)


class SyncEventHubProducer(EventHubProducerInterface):

    def __init__(self, sync_producer_client):
        self.producer = sync_producer_client

    @validate_event_data
    def send_event_data_batch(self, event_data):
        """Send a single event in a batch."""
        event_data_batch = self.producer.create_batch()
        event_data_batch.add(EventData(event_data))
        self.producer.send_batch(event_data_batch)

    def send_event_data_batch_with_limited_size(self, event_data_list):
        """Send events with a batch size limit."""
        event_data_batch = self.producer.create_batch(max_size_in_bytes=1000)
        for event_data in event_data_list:
            try:
                event_data_batch.add(EventData(event_data))
            except ValueError:
                logger.warning("Event skipped due to size limit: %s", event_data)
                continue

        self.producer.send_batch(event_data_batch)

    @validate_event_data
    def send_event_data_batch_with_partition_key(self, event_data, partition_key):
        """Send an event batch with a partition key."""
        event_data_batch = self.producer.create_batch(partition_key=partition_key)
        event_data_batch.add(EventData(event_data))
        self.producer.send_batch(event_data_batch)

    @validate_event_data
    def send_event_data_batch_with_partition_id(self, event_data, partition_id):
        """Send an event batch to a specific partition ID."""
        event_data_batch = self.producer.create_batch(partition_id=partition_id)
        event_data_batch.add(EventData(event_data))
        self.producer.send_batch(event_data_batch)

    @validate_event_data
    def send_event_data_batch_with_properties(self, event_data, properties):
        """Send an event batch with additional properties."""
        event_data_batch = self.producer.create_batch()
        event = EventData(event_data)
        event.properties = properties
        event_data_batch.add(event)
        self.producer.send_batch(event_data_batch)

    def send_event_data_list(self, event_data_list):
        """Send a list of events."""
        event_data_batch = self.producer.create_batch()
        try:
            for event_data in event_data_list:
                event_data_batch.add(EventData(event_data))
            self.producer.send_batch(event_data_batch)
        except ValueError as ve:
            logger.error("Validation error: %s", ve)
            raise
        except EventHubError as eh_err:
            logger.error("Sending error: %s", eh_err)
            raise

    def close(self):
        """Close the producer client."""
        self.producer.close()
        logger.info("azure_eventhub producer closed.")
