from django.urls import path
from EmailApp.views.email_conversations import EmailConversationViewSet
from EmailApp.views.emails import EmailsViewSet
from EmailApp.views.personalization_views import PersonalizationViewset
from EmailApp.views.tickets import TicketViewSet

app_name = 'EmailApp'

#TODO add base URL email to all the APIs
urlpatterns = [
        
        path('healthCheck', EmailsViewSet.as_view({'get': 'healthCheck'}), name='healthCheck'),

        path('get_email_tickets', TicketViewSet.as_view({'post': 'get_email_tickets'}), name='get_email_tickets'),

        path('get_email_conversations',  EmailConversationViewSet.as_view({'post': 'get_email_conversations'}), name='get_email_conversations'),
        path('get_mail_conversation_by_ticket_uuid', EmailConversationViewSet.as_view({'get': 'get_mail_conversation_by_ticket_uuid'}), name='get_mail_conversation_by_ticket_uuid'),
        path('get_content_from_url',  EmailConversationViewSet.as_view({'get': 'get_content_from_url'}), name='get_content_from_url'),
        path('get_mail_conversation_count_by_ticket_uuid', EmailConversationViewSet.as_view({'get': 'get_mail_conversation_count_by_ticket_uuid'}), name='get_mail_conversation_count_by_ticket_uuid'),

        path('reply_to_mail', EmailConversationViewSet.as_view({'post': 'reply_to_mail'}), name='reply_to_mail'),
        
        path('draft_mail',
             EmailConversationViewSet.as_view({
                 'post': 'create_draft_mail',
                 'delete': 'delete_draft_mail'
              }),name='draft_mail'
          ),

        path('order_details_info',
             EmailConversationViewSet.as_view({
                 'post': 'post_order_details_info',
             }),name='order_details_info'
          ),

        path('get_downloadable_urls',  EmailConversationViewSet.as_view({'post': 'get_downloadable_urls'}), name='get_downloadable_urls'),

        path('get_mails_by_email_uuids',
             EmailConversationViewSet.as_view({
                 'post': 'get_mails_by_email_uuids',
             }),name='get_mails_by_email_uuids'
          ),

        path('process_attachment_by_blob_url',  EmailConversationViewSet.as_view({'post': 'process_attachment_by_blob_url'}), name='process_attachment_by_blob_url'),

        path('fetch_intents_subintents_sentiment', PersonalizationViewset.as_view({'get': 'fetch_intents_subintents_sentiment'}), name='fetch_intents_subintents_sentiment'),
        path('response_configurations', PersonalizationViewset.as_view({
        'get': 'fetch_response_configurations',
        'post': 'save_response_configurations',
        'delete':'delete_response_configurations'
          }), name='response_configurations'),
    path('download_responses_template', PersonalizationViewset.as_view({'get': 'download_template'}), name='download_template'),

        path('utterances',PersonalizationViewset.as_view({'delete': 'delete_utterance','post':'get_utterances_by_dimension'}),name='utterances_configuration'),
        path('generate_utterances',
             PersonalizationViewset.as_view({'post': 'generate_utterances'}),
             name='generate_utterances'),
        path('intents_with_training_phrases',PersonalizationViewset.as_view({'get':'download_intents_with_training_phrases',
                                                                             "post":"bulk_import_training_phrases"}),name='intents_with_training_phrases'),


]
