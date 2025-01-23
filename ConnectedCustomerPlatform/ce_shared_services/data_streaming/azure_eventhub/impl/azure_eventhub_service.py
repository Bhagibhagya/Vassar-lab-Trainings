from azure.eventhub import TransportType

from ..eventhub_constants import EventHubConstants
from ..impl.async_clients import AsyncClients
from ..impl.event_hub_producer_singleton import EventHubProducerSingleton
from ..impl.receive_event_async import AsyncEventHubConsumer
from ..impl.receive_event_sync import SyncEventHubConsumer
from ..impl.send_event_async import AsyncEventHubProducer
from ..impl.send_event_sync import SyncEventHubProducer
from ..impl.sync_client import SyncClients
from ....data_streaming.interface.streaming_service import StreamingService


class AzureEventHubService(StreamingService):

    def __init__(
            self,
            producer_eventhub_name,
            consumer_eventhub_name,
            blob_container_name,
            connection_string,
            storage_connection_string,
            consumer_group="$Default",
            max_batch_size=100,
            retry_total=3,
            transport_type=TransportType.Amqp,
            logging_enable=False,
            starting_position="-1",
            no_of_producer_clients=0,
            connection_retry_time=230
    ):

        EventHubConstants.update_constants(
            producer_eventhub_name=producer_eventhub_name,
            consumer_eventhub_name=consumer_eventhub_name,
            blob_container_name=blob_container_name,
            connection_string=connection_string,
            storage_connection_string=storage_connection_string,
            consumer_group=consumer_group,
            max_batch_size=max_batch_size,
            retry_total=retry_total,
            transport_type=transport_type,
            logging_enable=logging_enable,
            starting_position=starting_position,
            no_of_producer_clients=no_of_producer_clients,
            connection_retry_time=connection_retry_time
        )

    def create_producer(self, async_mode: bool = False):
        if async_mode:
            async_producer = AsyncClients().create_producer_client()
            return AsyncEventHubProducer(async_producer)
        sync_producer = SyncClients().create_producer_client()
        return SyncEventHubProducer(sync_producer)

    def create_consumer(self, async_mode: bool = False):
        if async_mode:
            async_consumer = AsyncClients().create_consumer_client()
            return AsyncEventHubConsumer(async_consumer)
        sync_consumer = SyncClients().create_consumer_client()
        return SyncEventHubConsumer(sync_consumer)

    def get_singleton_producer(self):
        return EventHubProducerSingleton
