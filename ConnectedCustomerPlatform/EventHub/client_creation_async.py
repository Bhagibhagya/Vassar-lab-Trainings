from azure.eventhub import TransportType
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient, EventHubSharedKeyCredential
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from django.conf import settings

CONSUMER_GROUP = "$Default"


async def create_producer_client(eventhub_name):
    print('create producer client.')

    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=settings.EVENTHUB_CONNECTION_STR,
        eventhub_name=eventhub_name,
        logging_enable=False,  # To enable network tracing log, set logging_enable to True.
        retry_total=3,  # Retry up to 3 times to re-do failed operations.
        transport_type=TransportType.Amqp  # Use Amqp as the underlying transport protocol.
    )

    return producer_client
    # async with producer_client:
    #     print("Calling producer client get eventhub properties:", await producer_client.get_eventhub_properties())


async def create_consumer_client(eventhub_name, blob_container_name):
    print('create consumer client.')

    checkpoint_store = BlobCheckpointStore.from_connection_string(settings.CHECKPOINT_STORAGE_CONNECTION_STR, blob_container_name)

    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=settings.EVENTHUB_CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=eventhub_name,
        logging_enable=False,  # To enable network tracing log, set logging_enable to True.
        retry_total=3,  # Retry up to 3 times to re-do failed operations.
        transport_type=TransportType.Amqp,  # Use Amqp as the underlying transport protocol.
        checkpoint_store = checkpoint_store,  # For load-balancing and checkpoint. Leave None for no load-balancing.
    )

    return consumer_client
    # async with consumer_client:
    #     print("Calling consumer client get eventhub properties:", await consumer_client.get_eventhub_properties())
