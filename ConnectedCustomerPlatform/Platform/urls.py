# from Platform.views.chat_configuration import ChatConfigurationViewSet
from Platform.views.assign_organization import AssignOrganizationViewSet
from Platform.views.chat_configuration_base import ChatConfigurationBaseViewSet
from Platform.views.customer_users import CustomerUsersViewSet
from Platform.views.customers import CustomersViewSet
from Platform.views.dimension import DimensionViewSet
from Platform.views.dimension_type import DimensionTypeViewSet
from Platform.views.email_server import EmailServerSettingsViewSet
from Platform.views.email_settings import UserEmailSettingsViewSet
from Platform.views.llm_configuration import LLMConfigurationViewSet
from Platform.views.prompt import PromptViewSet
from Platform.views.prompt_template import PromptTemplateViewSet
from Platform.views.scope import ScopeViewSet
from Platform.views.ticketing_dashboard import TicketViewSet
from django.urls import path
# from Platform.views.whatsapp_configuration import WhatsappConfigurationViewSet
from Platform.views.customer_client import CustomerClientViewSet
from Platform.views.customer_client_tier import CustomerClientTierViewSet
app_name = 'Platform'
from Platform.views.stream_file import StreamFileViewSet

urlpatterns = [
    # DimensionType urls
    # DimensionType urls
    path('dimension_type', DimensionTypeViewSet.as_view({
        'post': 'add_dimension_type',
        'get': 'get_dimension_types',
        'put': 'edit_dimension_type',
    }), name='dimension_type'),

    path('dimension_type/<str:mapping_uuid>', DimensionTypeViewSet.as_view({
        'get': 'get_dimension_type_by_id',
        'delete': 'delete_dimension_type',
    }), name='dimension_type_by_id'),

    # Dimension URLs
    # Add, Edit APIs
    path('dimension',
         DimensionViewSet.as_view({
             'post': 'add_dimension',
             'put': 'edit_dimension'
         }), name='dimension'),

    # Get or delete by mapping uuid APIs
    path('dimension/<uuid:mapping_uuid>',
         DimensionViewSet.as_view({
             'get': 'get_dimension_by_id',
             'delete': 'delete_dimension'
         }), name='dimension_by_id'),

    # edit training phrase
    path('edit_training_phrase',
         DimensionViewSet.as_view({
             'post': 'edit_training_phrase',
         }), name='edit_training_phrase'),

    # add training phrases
    path('add_training_phrases',
     DimensionViewSet.as_view({
         'post': 'add_training_phrases',
     }), name='add_training_phrase'),

    # Get dimensions by a specific type
    path('dimension/type/<uuid:dimension_type_uuid>', DimensionViewSet.as_view({'post': 'get_dimensions_by_type'}), name='dimensions_by_type'),

    # Handle geography-related dimensions, with optional parent dimension UUID
    path('dimension/geography', DimensionViewSet.as_view({'get': 'get_geography_dimensions'}), name='geography_dimensions'),
    path('dimension/geography/<uuid:parent_dimension_uuid>',
         DimensionViewSet.as_view({'get': 'get_geography_dimensions'}),
         name='geography_dimensions_by_id'),

    # Get a dropdown of countries and states
    path('dimension/countries', DimensionViewSet.as_view({'get': 'get_country_state_dropdown'}), name='country_state_dropdown'),
    path('dimension/states/<str:country_name>', DimensionViewSet.as_view({'get': 'get_country_state_dropdown'}),
         name='country_state_dropdown_by_id'),

    # Prompt_Template urls
    path('prompt_template', PromptTemplateViewSet.as_view({
        'post': 'add_prompt_template',
        'get': 'get_prompt_templates',
        'put': 'edit_prompt_template',
    }), name='prompt_template'),
    path('prompt_template/<str:mapping_uuid>', PromptTemplateViewSet.as_view({
        'delete': 'delete_prompt_template',
        'get':'get_prompt_template_by_id'
    }), name='prompt_template_dynamic_path'),
    path('prompt_category', PromptTemplateViewSet.as_view({
        'get':'get_prompt_categories'
    }), name='prompt_category'),

    # Prompts urls
    path('prompt', PromptViewSet.as_view({
        'post': 'add_prompt',
        'get': 'get_prompts',
        'put': 'edit_prompt'
    }), name='prompt'),
    path('prompt/<str:prompt_uuid>', PromptViewSet.as_view({
        'delete': 'delete_prompt',
        'get':'get_prompt_by_id'
    }), name='prompt_dynamic_path'),

    # Customer Client urls
    path('customer_client', CustomerClientViewSet.as_view({
        'post': 'add_customer_client',
        'put': 'edit_customer_client',
        'get':'get_customer_client'
    }), name='customer_client'),
    path('customer_client/<str:customer_client_uuid>', CustomerClientViewSet.as_view({'delete': 'delete_customer_client'}), name='delete_customer_client'),

    path('customer_client_tier_mapping', CustomerClientTierViewSet.as_view({
        'post': 'add_customer_client_tier_mapping',
        'put': 'edit_customer_client_tier_mapping',
    }), name='customer_client_tier_mapping'),
    path('customer_client_tier_mapping/<str:mapping_uuid>',CustomerClientTierViewSet.as_view({
        'delete': "delete_customer_client_tier_mapping",
    }), name='delete_customer_tier_mapping'),
    path('customer_tier_mapping/<str:tier_mapping_uuid>',CustomerClientTierViewSet.as_view({
        'get': 'get_customers_client_by_tier_mapping',
    }), name='customer_tier_mapping'),
    path('customer_client_tier_dropdown', CustomerClientTierViewSet.as_view({
        'get': 'get_customer_client_dropdown_in_tier',
    }), name='customer_client_dropdown_in_tier'),

    # Email Server urls
    path('email_server', EmailServerSettingsViewSet.as_view({
        'post': 'add_email_server',
        'get': 'get_email_server',
        'put': 'edit_email_server',
        'delete': 'delete_email_server',
    }), name='email_server'),

    path('server_provider', EmailServerSettingsViewSet.as_view({
        'get': 'get_server_provider_name'}), name='server_provider'),

    path('outlook_server', EmailServerSettingsViewSet.as_view({
        'get': 'get_outlook_server',
        'post': 'save_outlook_server',
    }), name='outlook_server'),

    # Email Settings urls
    path('email_settings', UserEmailSettingsViewSet.as_view({
        'post': 'add_user_email_settings',
        'get': 'get_user_email_settings',
        'put': 'edit_user_email_settings'
    }), name='user_email_settings'),

    path('email_settings/test_connection/gmail', UserEmailSettingsViewSet.as_view({
        'post': 'test_connection_gmail'
    }), name='test_connection_gmail'),

    path('email_settings/test_connection/outlook', UserEmailSettingsViewSet.as_view({
        'post': 'test_connection_outlook'
    }), name='test_connection_outlook'),

    path('email_settings/<str:user_email_uuid>', UserEmailSettingsViewSet.as_view({
        'delete': 'delete_user_email_settings'
    }), name='user_email_settings_by_id'),

    # User Management Scope Urls
    path('scope/categories', ScopeViewSet.as_view({'get': 'get_scope_categories'}), name='get_scope_categories'),

    path('scope/<str:category>/values', ScopeViewSet.as_view({'get': 'get_scope_category_values'}),
         name='get_scope_category_values'),

    path('scope/<str:category>/names/<str:scope_type>/values',
         ScopeViewSet.as_view({'get': 'get_scope_types_values'}), name='get_scope_types_values'),

    # Chat Configuration Activation Urls
    path('chat_configuration/activate', ChatConfigurationBaseViewSet.as_view({
        'post': 'update_activation_status',
        'get': 'get_active_chat_configurations'
    }), name='chat_configuration_activation'),

    # Chat Configuration Template Urls
    path('chat_configuration', ChatConfigurationBaseViewSet.as_view({
        'post': 'create_or_update_chat_configuration',
        'get': 'get_all_chat_configurations'
    }), name='chat_configuration'),

    #Chat Configuration By Id Urls
    path('chat_configuration/<uuid:chat_configuration_uuid>',
         ChatConfigurationBaseViewSet.as_view({
             'get': 'get_chat_configuration',
             'delete': 'delete_chat_configuration'
         }), name='chat_configuration_by_id'),

    # path('whatsapp_configuration_template/get_business_information',
    #      WhatsappConfigurationViewSet.as_view({'get': 'get_business_info'}),name='whatsapp_configuration_template'),
    # path('whatsapp_configuration_template/get_whatsapp_business_profile',
    #      WhatsappConfigurationViewSet.as_view({'get': 'get_whatsapp_business_profile'}),name='whatsapp_configuration_template'),
    # path('whatsapp_configuration_template/delete_template',
    #      WhatsappConfigurationViewSet.as_view({'delete': 'delete_whatsapp_template'}), name='delete_whatsapp_template'),

    # LLM Configuration Urls
    path('llm_configuration/get_llm_provider_meta_data', LLMConfigurationViewSet.as_view({'get': 'get_llm_provider_meta_data'}),
         name='get_llm_provider_meta_data'),
    path('llm_configuration', LLMConfigurationViewSet.as_view({
            'post': 'add_llm_configuration',
            'get': 'get_llm_configurations',
            'put': 'edit_llm_configuration'
        }), name='llm_configuration'),
    path('llm_configuration/<str:llm_configuration_uuid>', LLMConfigurationViewSet.as_view({
        'get': 'get_llm_configuration_by_id',
        'delete': 'delete_llm_configuration'
    }), name='llm_configuration'),

    path('assign_organization',AssignOrganizationViewSet.as_view({
        'post':'add_organizations',
        'get': 'get_organizations',
        'delete': 'delete_organization'
    }), name='assign_organization'),

    path('assign_organization/<str:customer_uuid>',AssignOrganizationViewSet.as_view({
        'get': 'get_organization_by_id',
    }), name='assign_organization'),

    path('verify_llm_configuration', LLMConfigurationViewSet.as_view({
            'post': 'verify_llm_configuration'
        }), name='verify_llm_configuration'),

    path('update_llm_status', LLMConfigurationViewSet.as_view({
            'get': 'update_llm_status'
        }), name='update_llm_status'),

    path('get_llm_status', LLMConfigurationViewSet.as_view({
            'get': 'get_llm_status'
        }), name='get_llm_status'),

    path('get_customers',CustomersViewSet.as_view({
            'get': 'get_customers'
        }), name='get_customers'),
        
    # Customer user urls
    path('customer_user', CustomerUsersViewSet.as_view({
        'post': 'add_customer_user',
        'put': 'edit_customer_user'
    }), name='customer_user'),
    path('customer_user/<str:client_user_uuid>', CustomerUsersViewSet.as_view({'delete': 'delete_customer_user'}), name='delete_customer_user'),
    path('customer_user/client/<str:customer_client_uuid>',CustomerUsersViewSet.as_view({'get': 'get_customer_users'}), name='get_customer_users'),

     # Unified Activity Dashboard URL's
     path('ticketing_dashboard/get_tickets', TicketViewSet.as_view({'post':'get_tickets'}), name ='get_tickets'),
     path('ticketing_dashboard/get_filters', TicketViewSet.as_view({'get':'get_filters'}), name ='get_filters'),
    path('ticketing_dashboard/mark_email_as_read', TicketViewSet.as_view({'get':'mark_email_as_read'}), name ='mark_email_as_read'),
    path('ticketing_dashboard/merge_tickets', TicketViewSet.as_view({'get': 'merge_tickets'}), name='merge_tickets'),
    path('ticketing_dashboard/get_ticket_dropdown', TicketViewSet.as_view({'get': 'get_ticket_dropdown'}), name='get_ticket_dropdown'),
    path('ticketing_dashboard/get_merged_conversation', TicketViewSet.as_view({'get': 'get_merged_conversation'}), name='get_merged_conversation'),
     
    path('upload_examples_to_chromadb', DimensionViewSet.as_view({
        'post': 'upload_examples_to_chromadb'
    }), name='upload_examples_to_chromadb'),
 
    path('download_training_phrases', DimensionViewSet.as_view({
            'get': 'download_training_phrases'
        }), name='download_training_phrases'),

    path('resolve_duplicates', DimensionViewSet.as_view({
                'post': 'resolve_duplicates'
            }), name='resolve_duplicates'),
    path('download_template', DimensionViewSet.as_view({
        'get': 'download_template'
    }), name='download_template'),
     path('stream_file', StreamFileViewSet.as_view({'post': 'stream_file_data'}), name='stream_file_data'),
]
