import asyncio
import json
import logging
from datetime import datetime

import pytz
from azure.eventhub import EventData

from .async_clients import AsyncClients

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ist = pytz.timezone('Asia/Kolkata')


class EventHubProducerSingleton:
    _producer_clients = None
    _in_use = set()
    _current_index = 0
    _lock = asyncio.Lock()

    @classmethod
    async def initialize_clients(cls, no_of_producer_clients: int = 1) -> None:
        """Initialize producer clients for the specified Event Hub, if not already created."""
        async with cls._lock:
            if cls._producer_clients is None:
                if no_of_producer_clients < 1:
                    raise ValueError("Producer clients are not created")
                cls._producer_clients = [
                    AsyncClients().create_producer_client() for _ in
                    range(no_of_producer_clients)
                ]

    @classmethod
    async def get_all_producer_clients(cls):
        """Retrieve all initialized producer clients for the specified Event Hub."""
        return cls._producer_clients

    @classmethod
    async def release_client(cls, index: int):
        """Release a producer client, making it available for future use.

        This method marks a producer client as available by removing its index from the `_in_use` set.
        The `async with cls._lock` statement ensures that the release operation is thread-safe,
        avoiding conflicts with any other coroutines trying to access or modify `_in_use`.

        """
        # can remove a client index from `_in_use` at any given time.
        async with cls._lock:
            logger.info(f"Released client index: {index}")
            cls._in_use.discard(index)

    @classmethod
    async def get_producer_client(cls):
        """Get an available producer client or rotate clients if all are in use.
        This method retrieves an available producer client to publish messages to azure_eventhub. If all clients are in use,
        it rotates through the list of clients in a round-robin fashion to evenly distribute the load. The `async with cls._lock`
        statement ensures thread-safe access to shared data structures, avoiding race conditions.
        """
        # The lock prevents concurrent access to the list of clients and the `_in_use` set,
        # ensuring that only one coroutine can modify these structures at a time.
        async with cls._lock:
            for client_index, client in enumerate(cls._producer_clients):
                if client_index not in cls._in_use:
                    cls._in_use.add(client_index)
                    cls._current_index = client_index
                    return client, client_index

            # All clients are currently in use; use round-robin rotation to pick a client.
            cls._current_index = (cls._current_index + 1) % len(cls._producer_clients)
            return cls._producer_clients[cls._current_index], cls._current_index

    @classmethod
    async def send_event_data(cls, event_data):
        loop = asyncio.get_running_loop()
        producer_client, index = await cls.get_producer_client()
        conversation_uuid = event_data.get("conversation_uuid")
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)

        send_event_start_time = loop.time()
        _send_event_start_time = datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        await producer_client.send_event(EventData(event_data))
        send_event_end_time = loop.time()
        _send_event_end_time = datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        logger.info(f"[{conversation_uuid}] send event data start time: {_send_event_start_time}")
        logger.info(f"[{conversation_uuid}] send event data end time: {_send_event_end_time}")
        send_event_elapsed_time = (send_event_end_time - send_event_start_time)
        logger.info(
            f"[{conversation_uuid}] {index} {str(producer_client)} send event data elapsed time: {send_event_elapsed_time}")
        await cls.release_client(index)
            
    @classmethod
    async def send_event_data_with_partition_key(cls, event_data, partition_key):
        """Send an event batch with a partition key."""
        loop = asyncio.get_running_loop()
        producer_client, index = await cls.get_producer_client()
        conversation_uuid = event_data.get("conversation_uuid")
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)

        send_event_start_time = loop.time()
        _send_event_start_time = datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        await producer_client.send_event(EventData(event_data), partition_key=partition_key)
        send_event_end_time = loop.time()
        _send_event_end_time = datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        logger.info(f"[{conversation_uuid}] send event data (partition key: {partition_key}) start time: {_send_event_start_time}")
        logger.info(f"[{conversation_uuid}] send event data (partition key: {partition_key}) end time: {_send_event_end_time}")
        send_event_elapsed_time = (send_event_end_time - send_event_start_time)
        logger.info(
            f"[{conversation_uuid}] {index} {str(producer_client)} send event data (partition key: {partition_key}) elapsed time: {send_event_elapsed_time}")
        await cls.release_client(index)

    @classmethod
    async def close(cls):
        if cls._producer_clients:
            for producer_client in cls._producer_clients:
                await producer_client.close()
            cls._producer_clients = []
