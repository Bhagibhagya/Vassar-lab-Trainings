import json
import time
import asyncio
import os

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
# from azure.eventhub import EventData.sendsync

from EventHub.client_creation_async import create_producer_client


class EventHubProducer:
    def __init__(self,eventhub):
        self.producer = create_producer_client(eventhub)

    async def send_event_data_batch(self, event_data):
        print("After sending")
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        event_data_batch = await self.producer.create_batch()
        event_data_batch.add(EventData(event_data))
        await self.producer.send_batch(event_data_batch)

    async def send_event_data_batch_with_limited_size(self, event_data_list):
        event_data_batch_with_limited_size = await self.producer.create_batch(max_size_in_bytes=1000)
        for event_data in event_data_list:
            try:
                event_data_batch_with_limited_size.add(EventData(event_data))
            except ValueError:
                break
        await self.producer.send_batch(event_data_batch_with_limited_size)

    async def send_event_data_batch_with_partition_key(self, event_data, partition_key):
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        event_data_batch_with_partition_key = await self.producer.create_batch(partition_key=partition_key)
        event_data_batch_with_partition_key.add(EventData(event_data))
        await self.producer.send_batch(event_data_batch_with_partition_key)

    async def send_event_data_batch_with_partition_id(self, event_data, partition_id):
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        event_data_batch_with_partition_id = await self.producer.create_batch(partition_id=partition_id)
        event_data_batch_with_partition_id.add(EventData(event_data))
        await self.producer.send_batch(event_data_batch_with_partition_id)

    async def send_event_data_batch_with_properties(self, event_data, properties):
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        event_data_batch = await self.producer.create_batch()
        event_data = EventData(event_data)
        event_data.properties = properties
        event_data_batch.add(event_data)
        await self.producer.send_batch(event_data_batch)

    async def send_event_data_list(self, event_data_list):
        event_data_list = [EventData(event) for event in event_data_list]
        try:
            await self.producer.send_batch(event_data_list)
        except ValueError:
            print("Size of the event data list exceeds the size limit of a single send")
        except EventHubError as eh_err:
            print("Sending error: ", eh_err)

    async def close(self):
        self.producer.close()

