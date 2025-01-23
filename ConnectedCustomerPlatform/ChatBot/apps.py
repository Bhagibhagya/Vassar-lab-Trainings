from django.apps import AppConfig

class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ChatBot'
    # consumer_runner = EventHubConsumerRunner()

    # def ready(self):
    #     send_reply_view_set = SendReplyViewSet()
    #     self.consumer_runner.start()
    #     self.consumer_runner.run_consumer("testhub", "eventhubcheckpointstore", send_reply_view_set.process_event)
    # consumer_runner.start()
    # consumer_runner.run_consumer("testhub","eventhubcheckpointstore",receive_chat_events)
