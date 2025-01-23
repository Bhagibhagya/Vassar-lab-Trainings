from ..interface.event_hub_clients_interface import EventHubClientCreationInterface
from ..utils.eh_client_functions import create_async_producer_client, create_async_consumer_client


class AsyncClients(EventHubClientCreationInterface):

    def create_producer_client(self):
        """
        Creates an async producer client to send messages to the Event Hub.
        """
        return create_async_producer_client()

    def create_consumer_client(self):
        """
        Creates an async consumer client to receive messages from the Event Hub.
        """
        return create_async_consumer_client()
