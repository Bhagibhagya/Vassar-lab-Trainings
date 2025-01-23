import asyncio
import threading
from .receive_async import receive_async, receive_batch_async


#Usage :=
# consumer_runner = EventHubConsumerRunner()
#self.consumer_runner.start()
#self.consumer_runner.run_consumer("testhub","eventhubcheckpointstore",receive_chat_events)
#self.consumer_runner.run_consumer_batch("testhub","eventhubcheckpointstore",receive_chat_events, 10)
class EventHubConsumerRunner:
    def __init__(self):
        pass
        # self.loop = asyncio.new_event_loop()
        # self.thread = threading.Thread(target=self.start_loop, args=(self.loop,))

    # def start_loop(self, loop):
    #     asyncio.set_event_loop(loop)
    #     loop.run_forever()

    # def start(self):
    #     self.thread.start()

    # def stop(self):
    #     self.loop.call_soon_threadsafe(self.loop.stop)
    #     self.thread.join()

    def run_consumer(self, eventhub_name, blob_container_name, callback_method=None):
        asyncio.run(receive_async(eventhub_name, blob_container_name, callback_method))
    # def run_consumer_batch(self, eventhub_name, blob_container_name, callback_method=None, max_batch_size=None):
    #     asyncio.run_coroutine_threadsafe(receive_batch_async(eventhub_name, blob_container_name, callback_method, max_batch_size), self.loop)
