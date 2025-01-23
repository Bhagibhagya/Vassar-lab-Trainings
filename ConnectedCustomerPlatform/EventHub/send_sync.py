import json
from datetime import datetime
import pytz
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData

from EventHub.client_creation import create_producer_client

# Usage :-
# producer = EventHubProducerSync("testhub")
# producer.send_event_data_batch(message_detail)
# producer.close()
ist = pytz.timezone('Asia/Kolkata')
class EventHubProducerSync:
    def __init__(self, eventhub):
        self.producer = create_producer_client(eventhub)
    # [START send_event_data_batch]
    def send_event_data_batch(self, event_data):

        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        print(f"\nTime profile :: main chatbot microservice :: time before batch creation   :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        event_data_batch = self.producer.create_batch()
        print(
            f"\nTime profile :: main chatbot microservice :: time after batch creation   :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        event_data_batch.add(EventData(event_data))
        self.producer.send_batch(event_data_batch=event_data_batch)
        #print("Produced batch data to Intent Classification Micro Service on event hub")
    # [END send_event_data_batch]

    def send_event_data_batch_with_limited_size(self, event_data_list):
        event_data_batch_with_limited_size = self.producer.create_batch(max_size_in_bytes=1000)
        for event_data in event_data_list:
            try:
                event_data_batch_with_limited_size.add(EventData(event_data))
            except ValueError:
                break
        self.producer.send_batch(event_data_batch_with_limited_size)

    def send_event_data_batch_with_partition_key(self, event_data, partition_key):
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        event_data_batch_with_partition_key = self.producer.create_batch(partition_key=partition_key)
        event_data_batch_with_partition_key.add(EventData(event_data))
        self.producer.send_batch(event_data_batch_with_partition_key)

    def send_event_data_batch_with_partition_id(self, event_data, partition_id):
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        event_data_batch_with_partition_id = self.producer.create_batch(partition_id=partition_id)
        event_data_batch_with_partition_id.add(EventData(event_data))
        self.producer.send_batch(event_data_batch_with_partition_id)

    def send_event_data_batch_with_properties(self, event_data, properties):
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")
        event_data_batch = self.producer.create_batch()
        event_data = EventData(event_data)
        event_data.properties = properties
        event_data_batch.add(event_data)
        self.producer.send_batch(event_data_batch)

    def send_event_data_list(self, event_data_list):
        event_data_list = [EventData(event) for event in event_data_list]
        try:
            self.producer.send_batch(event_data_list)
        except ValueError:
            print("Size of the event data list exceeds the size limit of a single send")
        except EventHubError as eh_err:
            print("Sending error: ", eh_err)

    def close(self):
        self.producer.close()