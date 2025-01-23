import asyncio
import logging

from ..eventhub_constants import EventHubConstants
from ..interface.receive_event_data_interface import EventHubConsumerClient
from ..utils.eventhub_consumer_functions import deserialize_events, on_error, on_partition_close, \
    on_partition_initialize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncEventHubConsumer(EventHubConsumerClient):

    def __init__(self, consumer):
        self.consumer_client = consumer

    @staticmethod
    def execute_on_event(callback_method):
        """
         Creates an event handler that deserializes events and invokes the callback method.
        """

        async def on_event(partition_context, events):
            logger.info("Entered on_event method :: receiving events ::")
            if not isinstance(events, list):
                events = [events]
            logger.info("Received {} events from partition: {}.".format(len(events), partition_context.partition_id))
            deserialized_events = deserialize_events(events)
            # Call the custom callback with the deserialized batch of events
            await callback_method(partition_context, deserialized_events)
            await partition_context.update_checkpoint(events[-1])

        return on_event

    async def receive_event(self, callback_method):
        """
            Asynchronously receives events from Event Hub and processes them via the provided callback method.
        """
        async with self.consumer_client:
            await self.consumer_client.receive(
                on_event=self.execute_on_event(callback_method),
                on_error=on_error,
                on_partition_close=on_partition_close,
                on_partition_initialize=on_partition_initialize,
                starting_position=EventHubConstants.STARTING_POSITION,
            )

    async def receive_event_batch(self, callback_method):
        """
            Asynchronously receives a batch of events from Event Hub and processes them via the provided callback method.
        """
        async with self.consumer_client:
            await self.consumer_client.receive_batch(
                on_event_batch=self.execute_on_event(callback_method),
                on_error=on_error,
                on_partition_close=on_partition_close,
                on_partition_initialize=on_partition_initialize,
                max_batch_size=EventHubConstants.MAX_BATCH_SIZE,
                starting_position=EventHubConstants.STARTING_POSITION,
            )

    async def start_consumer(self, callback_method=None):
        """
            Starts the event hub consumer by awaiting the receive_event method.
        """
        await self.receive_event(callback_method)

    def start_consumer_with_asyncio(self, callback_method):
        """
            Starts the event hub consumer by running the receive_event method in an asyncio event loop.
        """
        asyncio.run(self.receive_event(callback_method))
