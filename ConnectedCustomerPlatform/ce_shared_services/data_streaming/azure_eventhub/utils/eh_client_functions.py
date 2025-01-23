import logging
import traceback
from datetime import datetime

import pytz
from azure.eventhub import EventHubProducerClient as SyncEventHubProducerClient, \
    EventHubConsumerClient as SyncEventHubConsumerClient
from azure.eventhub.aio import EventHubProducerClient as AsyncEventHubProducerClient, \
    EventHubConsumerClient as AsyncEventHubConsumerClient

from ..eventhub_constants import EventHubConstants

ist = pytz.timezone('Asia/Kolkata')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def on_error_callback(event_data_batch, partition_id, exception):
    """
    Callback function to handle errors that occur while processing an event batch.
    Logs the error details and the failed event data.
    """
    err_log_msg = "An error occurred while processing an event batch on partition"
    logger.info(f"{err_log_msg} {partition_id}.")
    logger.error(f"Exception: {exception}")
    if isinstance(exception, Exception):
        traceback_str = ''.join(traceback.format_exception(None, exception, exception.__traceback__))
        logger.info(traceback_str)
    for event in event_data_batch:
        logger.info(f"Failed event data: {event.body_as_str()}")


async def on_success_callback(event_data, partition_id):
    """
    Callback function to handle successful publishing of an event.
    Logs the event data along with the partition ID and timestamp.
    """
    timestamp = datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    logger.info(f"on_success_callback method invoked at {timestamp}")
    logger.info(f"Successfully published event. Event data: {event_data}, Partition ID: {partition_id}, Timestamp: {timestamp}")


def create_async_producer_client():
    """
    Creates and returns an asynchronous Event Hub producer client.
    """
    producer_client = AsyncEventHubProducerClient.from_connection_string(
        conn_str=EventHubConstants.CONNECTION_STRING,
        eventhub_name=EventHubConstants.PRODUCER_EVENTHUB_NAME,
        logging_enable=EventHubConstants.LOGGING_ENABLE,
        retry_total=EventHubConstants.RETRY_TOTAL,
        transport_type=EventHubConstants.TRANSPORT_TYPE,
        on_error=on_error_callback,
        on_success=on_success_callback,
    )
    return producer_client


def create_sync_producer_client():
    """
    Creates and returns a synchronous Event Hub producer client.
    """
    producer_client = SyncEventHubProducerClient.from_connection_string(
        conn_str=EventHubConstants.CONNECTION_STRING,
        eventhub_name=EventHubConstants.PRODUCER_EVENTHUB_NAME,
        logging_enable=EventHubConstants.LOGGING_ENABLE,
        retry_total=EventHubConstants.RETRY_TOTAL,
        transport_type=EventHubConstants.TRANSPORT_TYPE,
        on_error=on_error_callback,
        on_success=on_success_callback,
    )
    return producer_client


def create_async_consumer_client():
    """
    Creates and returns an asynchronous Event Hub consumer client.
    """
    consumer_client = AsyncEventHubConsumerClient.from_connection_string(
        conn_str=EventHubConstants.CONNECTION_STRING,
        consumer_group=EventHubConstants.CONSUMER_GROUP,
        eventhub_name=EventHubConstants.CONSUMER_EVENTHUB_NAME,
        logging_enable=EventHubConstants.LOGGING_ENABLE,
        retry_total=EventHubConstants.RETRY_TOTAL,
        transport_type=EventHubConstants.TRANSPORT_TYPE,
        checkpoint_store=EventHubConstants.CHECKPOINT_STORE,
    )
    return consumer_client


def create_sync_consumer_client():
    """
    Creates and returns  synchronous Event Hub consumer client.
    """
    consumer_client = SyncEventHubConsumerClient.from_connection_string(
        conn_str=EventHubConstants.CONNECTION_STRING,
        consumer_group=EventHubConstants.CONSUMER_GROUP,
        eventhub_name=EventHubConstants.CONSUMER_EVENTHUB_NAME,
        logging_enable=EventHubConstants.LOGGING_ENABLE,
        retry_total=EventHubConstants.RETRY_TOTAL,
        transport_type=EventHubConstants.TRANSPORT_TYPE,
        checkpoint_store=EventHubConstants.CHECKPOINT_STORE,
    )
    return consumer_client
