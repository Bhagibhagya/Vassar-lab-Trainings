from django.urls import path, include

from ChatBot.views.chat_bot import ChatBotViewSet
from ChatBot.views.chat_analytics import ChatAnalyticsViewSet
from ChatBot.views.agent_dashboard import AgentDashboardViewSet
from ChatBot.views.conversation import ConversationViewSet
from ChatBot.connectors.msteams import ms_views
from ChatBot.views.captcha_image import CaptchaImageViewSet

from ChatBot.views.user_activity import UserActivityViewSet

from ChatBot.views.files import FilesViewSet
from ChatBot.views.entity import EntityViewSet

from ChatBot.views.sme import SMEViewSet
from ChatBot.views.attachments import AttachmentsViewSet
from ChatBot.views.header import HeaderCorrectionViewSet
from ChatBot.views.page import PageCorrectionViewSet
from ChatBot.views.video import VideoCorrectionViewSet
from ChatBot.views.table import TableCorrectionViewSet

from rest_framework.routers import SimpleRouter

from ChatBot.views.conversation_feedback import ConversationFeedbackView
from ChatBot.views.whatsapp_webhook import WhatsAppWebhookView

from ChatBot.views.department import DepartmentViewSet

from ChatBot.views.agent import AgentViewSet

from ChatBot.views.dimensions_intent import DimensionsIntentViewSet

app_name = 'ChatBot'

urlpatterns = [
    path("message/", ChatBotViewSet.as_view({'get': 'get_message'}), name='get_message'),
    path('chatbot_analytics/', ChatAnalyticsViewSet.as_view({'post': 'chatbot_analytics'}), name='chatbot_analytics'),
    path("upload_attachment", AttachmentsViewSet.as_view({'post': 'upload_attachment'}), name='upload_attachment'),
    path('whatsapp_webhook/', WhatsAppWebhookView.as_view(), name='whatsapp_webhook'),
    path("rateby_user/",ChatBotViewSet.as_view({'post': 'rateby_user'}), name='rateby_user'),
   
    path('conversations/<str:conversation_uuid>/update-status/<str:csr_uid>/<str:csr_status>', ConversationViewSet.as_view({'put': 'update_conversation_status'}),name='update_conversation_status'),
    path('conversations/<str:conversation_uuid>/history', ConversationViewSet.as_view({'get': 'conversation_history_details'}), name='conversation_history_details'),
    path('conversations/<str:ticket_uuid>/chat_history',ConversationViewSet.as_view({'get':'conversation_history'}),name='conversation_history'),
    path('conversations/<str:conversation_uuid>/summary', ConversationViewSet.as_view({'get': 'total_conversation_information'}), name='total_conversation_information'),
    path('conversations/<str:ticket_uuid>/chat_summary', ConversationViewSet.as_view({'get': 'total_conversation_information_by_ticket_uuid'}), name='total_conversation_information_by_ticket_uuid'),

    path('conversations/ongoing/<str:csr_uid>', ConversationViewSet.as_view({'get': 'ongoing_conversations_list'}), name='ongoing_conversations_list'),

    path("chat_conversation/feedback",ConversationFeedbackView.as_view({'post': 'chat_conversation_feedback'}), name='chat_conversation_feedback'),    path('update_conversation_status/', AgentDashboardViewSet.as_view({'post': 'update_conversation_status'}),
         name='update_conversation_status'),
    path('ms-teams/messages/', ms_views.MessagesView.as_view(), name='messages'),
    path('captcha/image',CaptchaImageViewSet.as_view({'get':'generate_captcha_image'}), name='generate_captcha_image'),
    path('dimension/intents',DimensionsIntentViewSet.as_view({'get': 'get_intent_dimensions'}), name='get_intent_dimensions'),

    path('agents/', AgentViewSet.as_view({'get': 'get_all_online_agents'}), name='get_all_online_agents'),
    path('departments/', DepartmentViewSet.as_view({'get': 'get_all_departments'}), name='get_all_departments'),

    path('useractivity/conversations', UserActivityViewSet.as_view({'get' : 'get_user_chats'}), name='get_user_chats'),
    path('useractivity/leaderboard', UserActivityViewSet.as_view({'get' : 'get_leaderboard'}), name='get_leaderboard'),
    path('useractivity/timeseries', UserActivityViewSet.as_view({'get' : 'get_timeseries'}), name='get_timeseries'),
    path('useractivity/feedback', UserActivityViewSet.as_view({'get' : 'get_feedback_details'}), name='get_feedback_details'),
    path('useractivity/averagestats', UserActivityViewSet.as_view({'get' : 'get_average_stats'}), name='get_average_stats'),
    path('useractivity/userinfo', UserActivityViewSet.as_view({'get' : 'get_user_info'}), name='get_user_info'),

    path('entity',
         EntityViewSet.as_view({'get': 'get_entities',
                                'put': 'update_entity',
                                'post': 'add_entity'
                                }), name='entity'),
    path('entity/<uuid:entity_uuid>', EntityViewSet.as_view({'get': 'get_entity',
                                                             'delete': 'delete_entity'}), name='get_or_delete_entity'),
    path('entities/knowledge-source',
         EntityViewSet.as_view({'put': 'update_knowledge_source_entity_assignment'}), name='update_knowledge_source_entity_assignment'),
    path('knowledgesources/<uuid:entity_uuid>', EntityViewSet.as_view({'get': 'get_knowledge_sources_by_entity'}), name='knwoledge_entities'),


     path('errors/headers/<uuid:file_uuid>/main', HeaderCorrectionViewSet.as_view({'get': 'get_h1_headings'}), name='get_h1_headings'),
     path('errors/headers/<uuid:file_uuid>/sub/<uuid:block_id>', HeaderCorrectionViewSet.as_view({'get' : 'get_child_blocks'}), name='get_child_blocks'),
     path('errors/headers', HeaderCorrectionViewSet.as_view({
          'post': 'insert_text_block',
          'put': 'update_headers',
          'delete': 'delete_block'
          }), name='errors_headers'),

     path('errors/tables/<uuid:file_uuid>/<uuid:table_id>', TableCorrectionViewSet.as_view({'get' : 'get_table'}), name='get_table'),
     path('errors/tables', TableCorrectionViewSet.as_view({
          'post' : 'get_table_from_csvfile',
          'put' : 'update_table'
          }), name='errors_tables'),

     path('errors/pages/<uuid:file_uuid>/<int:page>', PageCorrectionViewSet.as_view({'get' : 'get_page_blocks'}), name='get_page_blocks'),
     path('errors/pages', PageCorrectionViewSet.as_view({'post' : 'page_correction'}), name='page_correction'),

     path('errors/videos/<uuid:file_uuid>', VideoCorrectionViewSet.as_view({'get' : 'get_video_transcription'}), name='get_video_transcription'),
     path('errors/videos', VideoCorrectionViewSet.as_view({'post' : 'update_video_transcription'}), name='update_video_transcription'),
     
     path('knowledge-sources/errors', FilesViewSet.as_view({'get': 'get_knowledge_sources_errors'}), name='get_knowledge_sources_errors'),
     path('knowledge-sources/exists', FilesViewSet.as_view({'post': 'check_knowledge_sources_exists'}), name='check_knowledge_sources_exists'),
     path('knowledge-sources', FilesViewSet.as_view({'post': 'upload_knowledge_sources',
                                                     'get': 'get_knowledge_sources_list',
                                                    }), name='knowledge_sources'),
     path('knowledge-sources/<uuid:knowledge_source_uuid>', FilesViewSet.as_view({
                                                     'get':'get_knowledge_source_by_knowledge_source_uuid',
                                                     'delete':'delete_knowledge_source_by_uuid'}), name='knowledge_sources'),
     path('knowledge-sources/internal_json/<uuid:knowledge_source_uuid>', FilesViewSet.as_view({'get': 'get_internal_json'}),name='get_internal_json'),
     path('knowledge-sources/questions-answers', FilesViewSet.as_view({'get': 'get_files_for_questions_and_answers'}), name='get_files_for_questions_and_answers'),
     path('knowledge-sources/videos', FilesViewSet.as_view({'get': 'get_videos_in_application'}), name='get_videos_in_application'),
     path('knowledge-sources/<uuid:knowledge_source_uuid>/resolve', FilesViewSet.as_view({'put': 'resolve_knowledge_source'}), name='resolve_knowledge_source'),
     path('knowledge-sources/image-url', FilesViewSet.as_view({'post': 'upload_image_to_azure'}), name='upload_image_to_azure'),
     path('knowledge-sources/drives-files', FilesViewSet.as_view({'post': 'upload_files_via_drives'}), name='upload_files_via_drives'),
     path('knowledge-sources/reupload', FilesViewSet.as_view({'post': 'reupload_knowledge_source'}), name='reupload_knowledge_source'),
     path("knowledge-sources/internal_json/<str:knowledge_source_uuid>/<str:page_number>",FilesViewSet.as_view({'get': 'generate_formatted_internal_json'}), name='generate_formatted_internal_json'),
     path('knowledge-sources/internal_json', FilesViewSet.as_view({'post': 'update_internal_json'}), name='update_internal_json'),

     path('knowledge-sources/internal_json/edit', FilesViewSet.as_view({'post': 'editable_internal_json'}), name='editable_internal_json'),
    path('sme/question', SMEViewSet.as_view({'post': 'add_question',
                                             'get': 'get_questions',
                                             }), name='sme'),

    path('sme/question/<uuid:question_uuid>', SMEViewSet.as_view({'get': 'get_question_details'}), name='question'),

    path('sme/answer/<uuid:answer_uuid>', SMEViewSet.as_view({'delete': 'delete_answer'}), name='answer'),
    path('sme/answer', SMEViewSet.as_view({'put': 'update_answer'}), name='update_answer'),
    path('sme/verify', SMEViewSet.as_view({'put': 'verify_answer'}), name='verify_answer'),

    path('sme/generate_qa', SMEViewSet.as_view({'post': 'generate_qa'}), name='generate_qa'),

    path('sme/feedback', SMEViewSet.as_view({'post': 'update_feedback'}), name='update_feedback'),
    path('sme/chunks', SMEViewSet.as_view({'post': 'get_relevant_chunks'}), name='get_relevant_chunks'),
    path('sme/chunks/reference', SMEViewSet.as_view({'post': 'get_parent_chunks'}), name='get_parent_chunks'),
    path('sme/chunks/neighbour',SMEViewSet.as_view({'post':'get_neighbouring_chunks'}),name='get_neighbouring_chunks'),
]
