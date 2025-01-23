INSERT INTO dimension_types (dimension_type_uuid, dimension_type_name, dimension_type_details_json, parent_dimension_type_uuid, status)
VALUES
    ('bc72228d-9362-4f86-a16a-21b0189575de', 'INTENT', '{}', NULL, false),
    ('d07dbc55-900e-418e-9c29-0b12857e0f3f', 'SUB_INTENT', '{}', 'bc72228d-9362-4f86-a16a-21b0189575de', false),
    ('17a33d7b-7b92-4102-92bc-d64d4070e7c7', 'SENTIMENT', '{}', NULL, false),
    ('313c631d-13bb-4f8c-a69a-7da116e4aefa', 'CUSTOMER_TIER', '{}', NULL, false),
    ('102376df-081e-40b4-9d46-0528de49ac72', 'GEOGRAPHY_COUNTRY', '{}', NULL, false),
    ('56c00be2-95ab-4ae5-890a-1765f0945d5c', 'GEOGRAPHY_STATE', '{}', '102376df-081e-40b4-9d46-0528de49ac72', false);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid)
VALUES
    ('78b341b1-015e-42fc-a3ea-adfe46208c4e', 'POSITIVE', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL),
    ('92eeab8c-4dfe-4c6e-9023-a589a6ed1dc8', 'NEUTRAL', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL),
    ('3d2b78f9-be76-4459-b702-2fd2dc10ad79', 'NEGATIVE', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES
    ('d1d778b3-d9d6-4ef3-be92-afcce4c68063', 'United States', 'b81f8ad5-0e6f-4e1e-9dae-1524a122ce23', '{}', NULL,
    '97ffeb19-8589-4c0a-9e9b-834cf3f95066','af4bf2d8-fd3e-4b40-902a-1217952c0ff3', true, NULL, NULL);


INSERT INTO prompt_category (prompt_category_uuid, prompt_category_name,created_by, updated_by)
VALUES
    ('bd821e3e-af57-4689-ad06-77791502ff35', 'Intent', NULL, NULL),
    ('bba9fd48-f71c-4776-b66e-a7e7533b36b2', 'Classification', NULL, NULL);


INSERT INTO prompt_category (prompt_category_uuid, prompt_category_name,created_by, updated_by)
VALUES
    ('3b6be12c-6165-41b2-9141-60453c29f5bb', 'INTENT_AND_SENTIMENT_CLASSIFICATION', NULL, NULL),
    ('2f3397f8-1afe-42c1-abe5-cd5b7cc520de', 'CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION', NULL, NULL),
    ('d929fed0-2897-4873-b4c6-459874dfcb00', 'DETAILS_EXTRACTION', NULL, NULL),
    ('da8870dc-6994-4ee4-a90d-a22b8c9e714b', 'SUMMARY_AND_RESPONSE_GENERATION', NULL, NULL);


INSERT INTO llm_provider_meta_data (llm_provider_uuid,llm_provider_name,llm_provider_details_json)
VALUES ('bc72bfcf-1649-41d6-a4d5-62bfe9beacd1','Azure Open AI',
    '{"model_names":["gpt-35-turbo","gpt-35-turbo-16k","gpt-35-turbo-instruct"],"api_types":["standard","azure"],"api_versions":["2024-02-01","2024-09-15-preview","2024-05-01-preview"]
    }');


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES
    ('e1ce93aa-33ea-47a4-aafb-d50d355cdba9', 'Texas', 'bfcacb62-0500-4acb-802c-844dae7cfc6d', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063',
     '97ffeb19-8589-4c0a-9e9b-834cf3f95066','af4bf2d8-fd3e-4b40-902a-1217952c0ff3', true, NULL, NULL),
    ('af4b435f-d08a-49f7-bb15-b28a46d028d7', 'New Jersey', 'bfcacb62-0500-4acb-802c-844dae7cfc6d', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063',
     '97ffeb19-8589-4c0a-9e9b-834cf3f95066','af4bf2d8-fd3e-4b40-902a-1217952c0ff3', true, NULL, NULL),
     ('af4b435f-d08a-49f7-bb15-b28a46d028d8', 'New York', 'bfcacb62-0500-4acb-802c-844dae7cfc6d', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063',
     '97ffeb19-8589-4c0a-9e9b-834cf3f95066','af4bf2d8-fd3e-4b40-902a-1217952c0ff3', true, NULL, NULL);


INSERT INTO email_server (email_server_uuid, server_type, server_url, email_provider_name, port, is_ssl_enabled, sync_time_interval, created_by, updated_by)
VALUES
    ('123e4567-e89b-12d3-a456-426614174000', 'IMAP', 'imap.gmail.com', 'Gmail', '993', true, 5, NULL, NULL),
    ('123e4567-e89b-12d3-a456-426614174001', 'SMTP', 'smtp.gmail.com', 'Gmail', '587', true, NULL, NULL, NULL),
    ('123e4567-e89b-12d3-a456-426614174002', 'IMAP', 'outlook.office365.com', 'Outlook', '993', true, 5, NULL, NULL),
    ('123e4567-e89b-12d3-a456-426614174003', 'SMTP', 'smtp.office365.com', 'Outlook', '587', true, NULL, NULL, NULL);


INSERT INTO public.chat_configuration (
    chat_configuration_uuid,
    chat_configuration_name,
    description,
    chat_details_json,
    code,
    application_uuid,
    customer_uuid,
    insert_ts,
    updated_ts,
    created_by,
    updated_by,
    chat_configuration_type,
    status,
    is_default,
    chat_configuration_provider
) VALUES
(
    'c0e9c769-3a20-470c-b6e9-f0030e979436',
    'Light theme',
    'Landing page Light theme',
    '{
        "landing_page_configuration": {
            "home_screen_configuration": {
                "background_fill_type": "Solid",
                "background_color": "#ffffff",
                "logo": "",
                "logo_width": "",
                "logo_height": ""
            },
            "bubble_configuration": {
                "bubble_type": "Icon",
                "bubble_animation_type": "SlideIn",
                "bubble_icon_type": 3,
                "custom_bubble_icon": "",
                "animation_duration": 300,
                "background_color": "#ffffff",
                "text_color": "#525252",
                "label_style": "Roboto"
            },
            "panel_configuration": {
                "width": 360,
                "height": 490,
                "has_box_shadow": true,
                "welcome_message": {
                    "message": "Hi there!\nWelcome to GenAI Chatbot...",
                    "font_family": "Open Sans",
                    "font_size": 28,
                    "color": "#525252"
                },
                "assistance_message": "How can I help you?",
                "default_intents": ["Order Status"],
                "input_box": "Tap to Speak/Type your message"
            }
        }
    }',
    NULL,
    NULL,
    NULL,
    '2024-08-05T05:57:59.824700Z',
    '2024-08-05T05:57:59.824798Z',
    'admin',
    'admin',
    'landing_page',
    FALSE,
    TRUE,
    'web'
),
(
    '510485d5-44f1-4dae-b3b0-fb98bb1ff27b',
    'Dark theme',
    'Landing page Dark theme',
    '{
        "landing_page_configuration": {
            "home_screen_configuration": {
                "background_fill_type": "Solid",
                "background_color": "#525252",
                "logo": "",
                "logo_width": "",
                "logo_height": ""
            },
            "bubble_configuration": {
                "bubble_type": "Icon",
                "bubble_animation_type": "SlideIn",
                "bubble_icon_type": 3,
                "custom_bubble_icon": "",
                "animation_duration": 300,
                "background_color": "#525252",
                "text_color": "#ffffff",
                "label_style": "Roboto"
            },
            "panel_configuration": {
                "width": 360,
                "height": 490,
                "has_box_shadow": true,
                "welcome_message": {
                    "message": "Hi there!\nWelcome to GenAI Chatbot...",
                    "font_family": "Open Sans",
                    "font_size": 28,
                    "color": "#ffffff"
                },
                "assistance_message": "How can I help you?",
                "default_intents": ["Order Status"],
                "input_box": "Tap to Speak/Type your message"
            }
        }
    }',
    NULL,
    NULL,
    NULL,
    '2024-08-05T06:04:38.552510Z',
    '2024-08-05T06:04:38.552524Z',
    'admin',
    'admin',
    'landing_page',
    FALSE,
    TRUE,
    'web'
),
(
    '5659a5b5-1952-4b90-8b28-7830d3406472',
    'Default theme',
    'Landing page Default theme',
    '{
        "landing_page_configuration": {
            "home_screen_configuration": {
                "background_fill_type": "Gradient",
                "background_color": "#65558F",
                "logo": "",
                "logo_width": "",
                "logo_height": ""
            },
            "bubble_configuration": {
                "bubble_type": "Icon",
                "bubble_animation_type": "SlideIn",
                "bubble_icon_type": 3,
                "custom_bubble_icon": "",
                "animation_duration": 300,
                "background_color": "#65558F",
                "text_color": "#ffffff",
                "label_style": "Roboto"
            },
            "panel_configuration": {
                "width": 360,
                "height": 490,
                "has_box_shadow": true,
                "welcome_message": {
                    "message": "Hi there!\nWelcome to GenAI Chatbot...",
                    "font_family": "Roboto",
                    "font_size": 28,
                    "color": "#ffffff"
                },
                "assistance_message": "How can I help you?",
                "default_intents": ["Order Status"],
                "input_box": "Tap to speak/Type your message"
            }
        }
    }',
    NULL,
    NULL,
    NULL,
    '2024-08-05T06:09:56.222133Z',
    '2024-08-05T06:09:56.222148Z',
    'admin',
    'admin',
    'landing_page',
    TRUE,
    TRUE,
    'web'
);

INSERT INTO public.chat_configuration (
    chat_configuration_uuid,
    chat_configuration_name,
    description,
    chat_details_json,
    code,
    application_uuid,
    customer_uuid,
    insert_ts,
    updated_ts,
    created_by,
    updated_by,
    chat_configuration_type,
    status,
    is_default,
    chat_configuration_provider
) VALUES
(
    '34b3c162-88a4-46d6-9b47-cdd593d53c4e',
    'Light theme',
    'Intent page Light theme',
    '{"intent_page_configuration": {"chat_avatar": {"avatar": "", "avatar_shape": "rounded", "avatar_type": "ProfilePic"}, "intent_page_panel_configuration": {"width": 360, "height": 490, "has_header": true, "has_box_shadow": true, "header": {"title": "Chat Assistance", "text_color": "#525252", "background_fill_type": "Solid", "background_color": "#ffffff"}, "bot_message": {"background_color": "#EBEBEB", "text_color": "#525252", "typing_indicator": "Typing...", "is_speech_enabled": false}, "user_message": {"background_color": "#F7F8F8", "text_color": "#525252"}, "footer": {"enable_attachments": true, "enable_text": true, "enable_speech": true, "enable_send": true}}}}',
    NULL,
    NULL,
    NULL,
    '2024-08-05T06:17:38.827668Z',
    '2024-08-05T06:17:38.827689Z',
    'admin',
    'admin',
    'intent_page',
    false,
    true,
    'web'
),
(
    'a49147c1-c5fc-44f3-aa18-3c29aa3c97d2',
    'Dark theme',
    'Intent page Dark theme',
    '{"intent_page_configuration": {"chat_avatar": {"avatar": "", "avatar_shape": "rounded", "avatar_type": "ProfilePic"}, "intent_page_panel_configuration": {"width": 360, "height": 490, "has_header": true, "has_box_shadow": true, "header": {"title": "Chat Assistance", "text_color": "#ffffff", "background_fill_type": "Solid", "background_color": "#363636"}, "bot_message": {"background_color": "#525252", "text_color": "#ffffff", "typing_indicator": "Typing...", "is_speech_enabled": false}, "user_message": {"background_color": "#404040", "text_color": "#ffffff"}, "footer": {"enable_attachments": true, "enable_text": true, "enable_speech": true, "enable_send": true}}}}',
    NULL,
    NULL,
    NULL,
    '2024-08-05T06:19:48.350677Z',
    '2024-08-05T06:19:48.350699Z',
    'admin',
    'admin',
    'intent_page',
    false,
    true,
    'web'
),
(
    '434ddea1-50d2-4e3a-8b52-b3581fd126d3',
    'Default theme',
    'Intent page Default theme',
    '{"intent_page_configuration": {"chat_avatar": {"avatar": "", "avatar_shape": "rounded", "avatar_type": "ProfilePic"}, "intent_page_panel_configuration": {"width": 360, "height": 490, "has_header": true, "has_box_shadow": true, "header": {"title": "Chat Assistance", "text_color": "#ffffff", "background_fill_type": "Gradient", "background_color": "#65558F"}, "bot_message": {"background_color": "#E0DDE9", "text_color": "#495057", "typing_indicator": "Typing...", "is_speech_enabled": false}, "user_message": {"background_color": "#f3f3f3", "text_color": "#495057"}, "footer": {"enable_attachments": true, "enable_text": true, "enable_speech": true, "enable_send": true}}}}',
    NULL,
    NULL,
    NULL,
    '2024-08-05T06:21:51.134775Z',
    '2024-08-05T06:21:51.134795Z',
    'admin',
    'admin',
    'intent_page',
    true,
    true,
    'web'
);
