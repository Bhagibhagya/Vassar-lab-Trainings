from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore


class EventHubConstants:
    PRODUCER_EVENTHUB_NAME = None
    CONSUMER_EVENTHUB_NAME = None
    BLOB_CONTAINER_NAME = None
    CONNECTION_STRING = None
    STORAGE_CONNECTION_STRING = None
    CONSUMER_GROUP = None
    MAX_BATCH_SIZE = None
    RETRY_TOTAL = None
    TRANSPORT_TYPE = None
    LOGGING_ENABLE = None
    STARTING_POSITION = None
    CHECKPOINT_STORE = None
    NO_OF_PRODUCER_CLIENTS = None
    CONNECTION_RETRY_TIME = None

    @classmethod
    def update_constants(cls, producer_eventhub_name,
                         consumer_eventhub_name,
                         blob_container_name,
                         connection_string, storage_connection_string,
                         consumer_group, max_batch_size,
                         retry_total, transport_type,
                         logging_enable, starting_position, no_of_producer_clients,
                         connection_retry_time):
        cls.PRODUCER_EVENTHUB_NAME = producer_eventhub_name
        cls.CONSUMER_EVENTHUB_NAME = consumer_eventhub_name
        cls.BLOB_CONTAINER_NAME = blob_container_name
        cls.CONNECTION_STRING = connection_string
        cls.STORAGE_CONNECTION_STRING = storage_connection_string
        cls.CONSUMER_GROUP = consumer_group
        cls.MAX_BATCH_SIZE = max_batch_size
        cls.RETRY_TOTAL = retry_total
        cls.TRANSPORT_TYPE = transport_type
        cls.LOGGING_ENABLE = logging_enable
        cls.STARTING_POSITION = starting_position
        cls.CHECKPOINT_STORE = BlobCheckpointStore.from_connection_string(
            conn_str=cls.STORAGE_CONNECTION_STRING,
            container_name=cls.BLOB_CONTAINER_NAME
        )
        cls.NO_OF_PRODUCER_CLIENTS = no_of_producer_clients
        cls.CONNECTION_RETRY_TIME = connection_retry_time
