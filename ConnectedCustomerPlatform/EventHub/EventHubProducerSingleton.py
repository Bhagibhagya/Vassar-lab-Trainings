import asyncio
import json
import traceback
from datetime import datetime
import pytz
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData, TransportType
from django.apps import AppConfig
from django.conf import settings

# EVENTHUB_CONNECTION_STR = "Endpoint=sb://ccprivatedev2.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=NuHOrnhbzCnxk7eWCtOQ8j1dckYaJzXCw+AEhDtUASY="
ist = pytz.timezone('Asia/Kolkata')
class EventHubProducerSingleton:
    _producer_client = None
    @staticmethod
    async def on_error_callback(event_batch, partition_id, exception):
        # Handle the error here
        print(f"An error occurred while processing an event batch on partition ::: {partition_id}.")
        print(f"Exception: {exception}")

        # Attempt to extract and print detailed traceback information
        if isinstance(exception, Exception):
            print("Exception details:")
            traceback_str = ''.join(traceback.format_exception(None, exception, exception.__traceback__))
            print(traceback_str)

        # Optionally, log the events in the batch that caused the error
        for event in event_batch:
            print(f"Failed event data: {event.body_as_str()}")
    @staticmethod
    async def on_success_callback(event_batch, partition_id):
        # Handle the sucess here
        print(f"Successfully published ::: {event_batch} and the partition_id is {partition_id}")
        print(
            f"\nTime profile :: main chatbot microservice :: time after event fully sent  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

    @classmethod
    def get_producer_client(cls, eventhub_name):
        print(f"PRODUCER CLIENT{cls._producer_client}")
        if cls._producer_client is None:
            print("PRODUCER CLIENT IS BEING INITIALIZED")
            cls._producer_client = EventHubProducerClient.from_connection_string(
                conn_str=settings.EVENTHUB_CONNECTION_STR,
                eventhub_name=eventhub_name,
                logging_enable=False,
                retry_total=3,
                transport_type=TransportType.Amqp,
                idle_timeout=600000,
                buffered_mode=False,
                #max_buffer_length=1500,
                #max_wait_time=0.1,
                on_error=cls.on_error_callback,
                on_success=cls.on_success_callback,
            )
        return cls._producer_client

    @classmethod
    async def send_event_data_batch(cls, event_data, eventhub_name):
        print(
            f"\nTime profile :: main chatbot microservice :: time before getting producer client  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')}\n")
        producer_client = cls.get_producer_client(eventhub_name)
        print(
            f"\nTime profile :: main chatbot microservice :: time after getting producer client  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')}\n")
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")

        # event_data_batch = await producer_client.create_batch()
        # event_data_batch.add(EventData(event_data))
        # event_data_obj = EventData(event_data)

        # Send event data to the buffer
        await producer_client.send_event(EventData(event_data))

        print(
            f"\nTime profile :: main chatbot microservice :: time after calling send_event  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')}\n")

        # event_data_batch = await producer_client.create_batch()
        # event_data_batch.add(EventData(event_data))
        # async with producer_client:
        #     await producer_client.send_batch(event_data_batch)

    @classmethod
    async def close(cls):
        if cls._producer_client:
            await cls._producer_client.close()
            cls._producer_client = None
