import logging
from django.core.management.base import BaseCommand, CommandError

from WiseFlow.apps import WiseFlowConfig
from WiseFlow.event_hub import start_eventhub_consumer


class Command(BaseCommand):
    help = 'Starts or stops the EventHub consumer runner'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, choices=['start', 'stop'], help='start or stop the consumer')

    def handle(self, *args, **options):
        action = options['action']
        logger = logging.getLogger('EventHub')

        if action == 'start':
            if WiseFlowConfig.consumer_runner is not None:
                logger.warning("Consumer is already running.")
                return

            logger.info("Starting the EventHub consumer via management command...")
            consumer_runner = start_eventhub_consumer()
            WiseFlowConfig.consumer_runner = consumer_runner

            try:
                while True:
                    # Keep the process running to maintain the consumer
                    pass
            except KeyboardInterrupt:
                logger.info("Stopping the EventHub consumer...")
                WiseFlowConfig.consumer_runner.stop()
                WiseFlowConfig.consumer_runner = None
                logger.info("EventHub consumer stopped.")

        elif action == 'stop':
            if WiseFlowConfig.consumer_runner is None:
                logger.warning("No consumer is running.")
                return

            logger.info("Stopping the EventHub consumer via management command...")
            WiseFlowConfig.consumer_runner.stop()
            WiseFlowConfig.consumer_runner = None
            logger.info("EventHub consumer stopped.")
        else:
            raise CommandError("Invalid action. Use 'start' or 'stop'.")
