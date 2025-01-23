#from EventHub.eventhub_consumer_runner import EventHubConsumerRunner
from ChatBot.views.send_reply import SendReplyViewSet
from EventHub.eventhub_consumer_runner import EventHubConsumerRunner
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def start_eventhub_consumer():
    send_reply_view_set = SendReplyViewSet()
    logger.info(f"Starting EventHubConsumerRunner...::{settings.CONSUMER_EVENT_HUB_NAME}")
    consumer_runner = EventHubConsumerRunner()
    # consumer_runner.start()
    consumer_runner.run_consumer(settings.CONSUMER_EVENT_HUB_NAME, "eventhubcheckpointstore", send_reply_view_set.process_event)
    # logger.info("EventHubConsumerRunner started.")
    return consumer_runner