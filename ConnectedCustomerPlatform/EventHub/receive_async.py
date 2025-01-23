import asyncio
import json
import os
from typing import Dict
from EventHub.client_creation_async import create_consumer_client
import traceback

# partition_recv_cnt_since_last_checkpoint: Dict[str, int] = {}
# checkpoint_event_cnt = 20

def execute_on_event(callback_method):
    async def on_event(partition_context, events):
        print("Entered on_event method :: receiving events ::")
        print(events)
        if not isinstance(events, list):
            events = [events]

        print("Received {} events from partition: {}.".format(len(events), partition_context.partition_id))

        deserialized_events = []
        for event in events:
            deserialized_event = json.loads(event.body_as_str())
            deserialized_events.append(deserialized_event)

            # p_id = partition_context.partition_id
            # if p_id not in partition_recv_cnt_since_last_checkpoint:
            #     partition_recv_cnt_since_last_checkpoint[p_id] = 0
            # partition_recv_cnt_since_last_checkpoint[p_id] += 1
            #
            # # If the checkpoint count threshold is reached, update the checkpoint for this event
            # if partition_recv_cnt_since_last_checkpoint[p_id] >= checkpoint_event_cnt:
            #     await partition_context.update_checkpoint(event)
            #     partition_recv_cnt_since_last_checkpoint[p_id] = 0

        # Call the custom callback with the deserialized batch of events
        await callback_method(partition_context, deserialized_events)

        await partition_context.update_checkpoint(events[-1])

        # # Update the checkpoint for the last event in the batch if not already done
        # if partition_recv_cnt_since_last_checkpoint[partition_context.partition_id] > 0:
        #     await partition_context.update_checkpoint(events[-1])
        #     partition_recv_cnt_since_last_checkpoint[partition_context.partition_id] = 0

    return on_event

async def on_partition_initialize(partition_context):
    # Put your code here.
    print("Partition: {} has been initialized.".format(partition_context.partition_id))


async def on_partition_close(partition_context, reason):
    # Put your code here.
    print("Partition: {} has been closed, reason for closing: {}.".format(
        partition_context.partition_id,
        reason
    ))


async def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))
    print(traceback.format_exc())


async def receive_async(eventhub_name, blob_container_name, callback_method):
    client = await create_consumer_client(eventhub_name, blob_container_name)
    async with client:
        await client.receive(
            on_event=execute_on_event(callback_method),
            on_error=on_error,
            on_partition_close=on_partition_close,
            on_partition_initialize=on_partition_initialize,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )

async def receive_batch_async(eventhub_name, blob_container_name, callback_method, max_batch_size):
    client = await create_consumer_client(eventhub_name, blob_container_name)
    async with client:
        await client.receive_batch(
            on_event_batch=execute_on_event(callback_method),
            on_error=on_error,
            on_partition_close=on_partition_close,
            on_partition_initialize=on_partition_initialize,
            max_batch_size = max_batch_size,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )

