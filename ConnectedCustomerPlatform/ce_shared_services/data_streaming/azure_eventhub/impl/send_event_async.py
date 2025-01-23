import asyncio
import json
import logging

from azure.eventhub import EventData
from azure.eventhub.exceptions import EventHubError

from ..interface.send_event_data_interface import EventHubProducerInterface
from ..utils.event_data_validator import validate_event_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncEventHubProducer(EventHubProducerInterface):

    def __init__(self, async_producer_client):
        self.producer = async_producer_client

    @validate_event_data
    async def send_event_data_batch(self, event_data):
        """Send a single event in a batch."""
        loop = asyncio.get_running_loop()
        conversation_uuid = json.loads(event_data).get("conversation_uuid")

        event_data_batch = await self.producer.create_batch()
        event_data_batch.add(EventData(event_data))

        send_batch_start_time = loop.time()
        await self.producer.send_batch(event_data_batch)
        send_batch_end_time = loop.time()

        logger.info(f"[{conversation_uuid}] send event data start time: {send_batch_start_time}")
        logger.info(f"[{conversation_uuid}] send event data end time: {send_batch_end_time}")
        send_event_elapsed_time = (send_batch_end_time - send_batch_start_time) * 1000
        logger.info(f"[{conversation_uuid}] send event data batch elapsed time: {send_event_elapsed_time} ms")

    async def send_event_data_batch_with_limited_size(self, event_data_list):
        """Send events with a batch size limit."""
        loop = asyncio.get_running_loop()
        event_data_batch_with_limited_size = await self.producer.create_batch(max_size_in_bytes=1000)

        for event_data in event_data_list:
            try:
                event_data_batch_with_limited_size.add(EventData(event_data))
            except ValueError:
                logger.warning("Event skipped due to size limit: %s", event_data)
                continue

        send_batch_start_time = loop.time()
        await self.producer.send_batch(event_data_batch_with_limited_size)
        send_batch_end_time = loop.time()

        logger.info(f"send event data (limited size) start time: {send_batch_start_time}")
        logger.info(f"send event data (limited size) end time: {send_batch_end_time}")
        logger.info(
            f"send event data (limited size) elapsed time: {(send_batch_end_time - send_batch_start_time) * 1000} ms")

    @validate_event_data
    async def send_event_data_batch_with_partition_key(self, event_data, partition_key):
        """Send an event batch with a partition key."""
        loop = asyncio.get_running_loop()
        event_data_batch_with_partition_key = await self.producer.create_batch(partition_key=partition_key)
        event_data_batch_with_partition_key.add(EventData(event_data))

        send_batch_start_time = loop.time()
        await self.producer.send_batch(event_data_batch_with_partition_key)
        send_batch_end_time = loop.time()

        logger.info(f"send event data (partition key: {partition_key}) start time: {send_batch_start_time}")
        logger.info(f"send event data (partition key: {partition_key}) end time: {send_batch_end_time}")
        logger.info(
            f"send event data (partition key: {partition_key}) elapsed time: {(send_batch_end_time - send_batch_start_time) * 1000} ms")

    @validate_event_data
    async def send_event_data_batch_with_partition_id(self, event_data, partition_id):
        """Send an event batch to a specific partition ID."""
        loop = asyncio.get_running_loop()
        event_data_batch_with_partition_id = await self.producer.create_batch(partition_id=partition_id)
        event_data_batch_with_partition_id.add(EventData(event_data))

        send_batch_start_time = loop.time()
        await self.producer.send_batch(event_data_batch_with_partition_id)
        send_batch_end_time = loop.time()

        logger.info(f"send event data (partition ID: {partition_id}) start time: {send_batch_start_time}")
        logger.info(f"send event data (partition ID: {partition_id}) end time: {send_batch_end_time}")
        logger.info(
            f"send event data (partition ID: {partition_id}) elapsed time: {(send_batch_end_time - send_batch_start_time) * 1000} ms")

    @validate_event_data
    async def send_event_data_batch_with_properties(self, event_data, properties):
        """Send an event batch with additional properties."""
        loop = asyncio.get_running_loop()
        event_data_batch = await self.producer.create_batch()
        event_data = EventData(event_data)
        event_data.properties = properties
        event_data_batch.add(event_data)

        send_batch_start_time = loop.time()
        await self.producer.send_batch(event_data_batch)
        send_batch_end_time = loop.time()

        logger.info(f"send event data (with properties) start time: {send_batch_start_time}")
        logger.info(f"send event data (with properties) end time: {send_batch_end_time}")
        logger.info(
            f"send event data (with properties) elapsed time: {(send_batch_end_time - send_batch_start_time) * 1000} ms")

    async def send_event_data_list(self, event_data_list):
        """Send a list of events."""
        loop = asyncio.get_running_loop()
        event_data_list = [EventData(event) for event in event_data_list]

        try:
            send_batch_start_time = loop.time()
            await self.producer.send_batch(event_data_list)
            send_batch_end_time = loop.time()

            logger.info(f"send event data list start time: {send_batch_start_time}")
            logger.info(f"send event data list end time: {send_batch_end_time}")
            logger.info(f"send event data list elapsed time: {(send_batch_end_time - send_batch_start_time) * 1000} ms")

        except ValueError as ve:
            logger.error("Validation error: %s", ve)
            raise
        except EventHubError as eh_err:
            logger.error("Sending error: %s", eh_err)
            raise

    async def close(self):
        """Close the producer client."""
        await self.producer.close()
        logger.info("azure_eventhub producer closed.")
