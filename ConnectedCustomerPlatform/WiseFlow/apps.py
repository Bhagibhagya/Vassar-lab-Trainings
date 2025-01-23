# WiseFlow/apps.py
from django.apps import AppConfig

class WiseFlowConfig(AppConfig):
    name = 'WiseFlow'
    _consumer_started = False
    consumer_runner = None

    def ready(self):
        pass

    @staticmethod
    def stop_consumer(**kwargs):
        if WiseFlowConfig.consumer_runner:
            WiseFlowConfig.consumer_runner.stop()