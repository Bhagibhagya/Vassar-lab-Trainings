import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deserialize_events(events):
    """
    Deserializes a list of events by converting their body from JSON string to Python dictionary.
    """
    deserialized_events = []
    for event in events:
        deserialized_event = json.loads(event.body_as_str())
        deserialized_events.append(deserialized_event)
    return deserialized_events


async def on_partition_initialize(partition_context):
    """
     Logs a message when a partition has been initialized.
    """
    logger.info(f"Partition: {partition_context.partition_id} has been initialized.")


async def on_partition_close(partition_context, reason):
    """
    Logs a message when a partition is closed, including the reason for closing.
    """
    logger.info(f"Partition: {partition_context.partition_id} has been closed. Reason: {reason}")


async def on_error(partition_context, error):
    """
    Logs an error message when an exception occurs either in the partition or during load balancing.
    """
    if partition_context:
        logger.error(f"Exception: {error} occurred during receiving from Partition: {partition_context.partition_id}.")
    else:
        logger.error(f"Exception: {error} occurred during the load balance process.")
