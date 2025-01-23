from ..interface.event_hub_clients_interface import EventHubClientCreationInterface
from ..utils.eh_client_functions import create_sync_consumer_client, create_sync_producer_client


class SyncClients(EventHubClientCreationInterface):

    def create_producer_client(self):
        """
        Creates a sync producer client to send messages to the Event Hub.
        """
        return create_sync_producer_client()

    def create_consumer_client(self):
        """
        Creates a sync consumer client to receive messages from the Event Hub.
        """
        return create_sync_consumer_client()
