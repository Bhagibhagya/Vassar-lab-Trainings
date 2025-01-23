
from azure.eventhub import EventHubConsumerClient
from EventHub.client_creation import create_consumer_client
from EventHub.receive_async import create_consumer_client

# CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
# EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

def on_event(partition_context, event):
    # Add your code here.
    # If the operation is i/o intensive, multi-thread will have better performance.
    print("Received event from partition: {}.".format(partition_context.partition_id))
    partition_context.update_checkpoint(event)

def on_partition_initialize(partition_context):
    # Put your code here.
    print("Partition: {} has been initialized.".format(partition_context.partition_id))

def on_partition_close(partition_context, reason):
    # Put your code here.
    print("Partition: {} has been closed, reason for closing: {}.".format(
        partition_context.partition_id,
        reason
    ))

def on_error(partition_context, error):
    # Add your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))

def start_event_hub_consumer():
    consumer_client = create_consumer_client()
    print(consumer_client)
    # with consumer_client:
    #     consumer_client.receive(
    #         on_event=on_event,
    #         starting_position="-1",  # "-1" is from the beginning of the partition.
    #     )
    #
    # # worker.start()
    # time.sleep(10)  # Keep receiving for 10s then close.
    # # Close down the consumer handler explicitly.
    # consumer_client.close()

