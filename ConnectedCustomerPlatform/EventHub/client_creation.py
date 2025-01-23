from datetime import datetime

import pytz
from azure.eventhub import (
    EventHubProducerClient,
    EventHubConsumerClient,
    TransportType,
    EventHubSharedKeyCredential,
)
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from django.conf import settings


FULLY_QUALIFIED_NAMESPACE = settings.FULLY_QUALIFIED_NAMESPACE
SAS_POLICY = "RootManageSharedAccessKey"
SAS_KEY = settings.SAS_KEY
CONSUMER_GROUP = "$Default"
BLOB_CONTAINER_NAME = settings.BLOB_CONTAINER_NAME
STORAGE_CONNECTION_STR = settings.CHECKPOINT_STORAGE_CONNECTION_STR
checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, BLOB_CONTAINER_NAME)


async def on_error_callback(event_data, partition_id, error):
    print(f"Error occurred: {partition_id} {error}")


async def on_success_callback(event_data, partition_id):
    print(f"Message sent successfully: to : {partition_id} :: {event_data}")
    print(
        f"\nTime profile :: main chatbot microservice :: time after message completely sent   :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")


def create_producer_client(eventhub):
    print('Inside create_producer_client() method in EventHubStreaming')

    # Create producer client.

    producer_client = EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=eventhub,
        credential=EventHubSharedKeyCredential(
            policy=SAS_POLICY,
            key=SAS_KEY
        ),
        logging_enable=True,  # To enable network tracing log, set logging_enable to True.
        retry_total=3,  # Retry up to 3 times to re-do failed operations.
        transport_type=TransportType.Amqp,  # Use Amqp as the underlying transport protocol.
        on_error= on_error_callback,
        on_success=on_success_callback,
    )

    print("Calling producer client get eventhub properties:", producer_client.get_eventhub_properties())
    return producer_client


def create_consumer_client(eventhub):
    # Configure your connection details here

    # Create consumer client
    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=eventhub,
        consumer_group=CONSUMER_GROUP,
        checkpoint_store=checkpoint_store,  # For load-balancing and checkpoint. Leave None for no load-balancing.
        credential=EventHubSharedKeyCredential(
            policy=SAS_POLICY,
            key=SAS_KEY
        ),
        logging_enable=True,
        retry_total=3,
        transport_type=TransportType.Amqp
    )

    # Optional: Log event hub properties
    # print("Calling consumer client get eventhub properties:", await consumer_client.get_eventhub_properties())

    return consumer_client
