	--Insert Script
-- Generate UUIDv4 function
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO channel_types (channel_type_uuid, channel_type_name, application_uuid, channel_type_details_json, status, created_by, updated_by)
VALUES
    ('75e4025e-2c64-422a-8355-19313aca6d48', 'Email', 'a26a2650-19f8-49de-a6e5-7aa73841acb0', '{}', true, NULL, NULL),
    ('154355d4-8b3f-4242-8d91-f8430837f244', 'Chat', 'a26a2650-19f8-49de-a6e5-7aa73841acb0', '{}', true, NULL, NULL);

INSERT INTO dimension_types (dimension_type_uuid, dimension_type_name, dimension_type_details_json, parent_dimension_type_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('bc72228d-9362-4f86-a16a-21b0189575de', 'INTENT', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0',NULL, true, NULL, NULL),
    ('d07dbc55-900e-418e-9c29-0b12857e0f3f', 'SUB_INTENT', '{}', 'bc72228d-9362-4f86-a16a-21b0189575de','75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0',NULL, true, NULL, NULL),
     ('17a33d7b-7b92-4102-92bc-d64d4070e7c7', 'SENTIMENT', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0',NULL, true, NULL, NULL),
    ('313c631d-13bb-4f8c-a69a-7da116e4aefa', 'CUSTOMER_TIER', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0',NULL, true, NULL, NULL),
     ('102376df-081e-40b4-9d46-0528de49ac72', 'GEOGRAPHY_COUNTRY', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0',NULL, true, NULL, NULL),
     ('56c00be2-95ab-4ae5-890a-1765f0945d5c', 'GEOGRAPHY_STATE', '{}', '102376df-081e-40b4-9d46-0528de49ac72', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0',NULL, true, NULL, NULL)
    ;
    
INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('90d7fdc4-6fda-4eea-ae17-acbbb0255d92', 'Tier 1', '313c631d-13bb-4f8c-a69a-7da116e4aefa', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('77d9d961-dbd4-4263-b735-930e58745a1c', 'Tier 2', '313c631d-13bb-4f8c-a69a-7da116e4aefa', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('05d5408c-c83f-4775-a4ac-117ed5b2cc31', 'Tier 3', '313c631d-13bb-4f8c-a69a-7da116e4aefa', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES
    ('d1d778b3-d9d6-4ef3-be92-afcce4c68063', 'UNITED STATES', '102376df-081e-40b4-9d46-0528de49ac72', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('2d4be7bb-aa65-4720-a585-187e4bab4d6f', 'INDIA', '102376df-081e-40b4-9d46-0528de49ac72', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('450e4fef-359a-456a-8218-3f8ca617e1f5', 'SERVICE_REQUEST', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d', 'PURCHASE_ORDER', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('84525baa-30d1-43fe-8d7e-00eafdc93bef', 'WARRANTY', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('2e03e50c-d691-4a66-8733-ff639855dfcb', 'SHIPMENT_STATUS', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('f0171b23-bb80-4029-b360-b012cb7b5d87', 'INVOICE', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('4fe863f9-85ea-47d2-af00-81a7e192b5fd', 'TROUBLESHOOTING', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('1403f488-4458-4a82-8860-6fcd55a059b1', 'ROUTINE_MAINTENANCE', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('5ef670aa-53f2-44c1-82c2-0158995640b8', 'RESOLVED', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('1a3fd73d-998a-4205-a079-fc738fa799e8', 'INSTALLATION', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('9e563c2c-a961-456f-9326-202a1f2c0cce', 'NEW_PO', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('170ac23e-705d-4028-b75a-6ddc1d3364c1', 'CHECK_PO_STATUS', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('c55c4f57-3f6f-4f62-91a2-0ef7740a84f7', 'INITIATE_WARRANTY_CLAIM', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','84525baa-30d1-43fe-8d7e-00eafdc93bef', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('cc69b53f-d8c7-4517-84de-f9b204d4a689', 'CHECK_SHIPMENT_STATUS', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','2e03e50c-d691-4a66-8733-ff639855dfcb', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('6640ae2e-36c7-4a37-905d-ac516fee56fb', 'INVOICE_VERIFICATION', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','f0171b23-bb80-4029-b360-b012cb7b5d87', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);

INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid)
VALUES
    ('78b341b1-015e-42fc-a3ea-adfe46208c4e', 'POSITIVE', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL),
    ('92eeab8c-4dfe-4c6e-9023-a589a6ed1dc8', 'NEUTRAL', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL),
    ('3d2b78f9-be76-4459-b702-2fd2dc10ad79', 'NEGATIVE', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL);

INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES
    ('e1ce93aa-33ea-47a4-aafb-d50d355cdba9', 'TEXAS', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('af4b435f-d08a-49f7-bb15-b28a46d028d7', 'NEW JERSEY', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     'a26a2650-19f8-49de-a6e5-7aa73841acb0','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);
    
INSERT INTO action_flows (action_flow_uuid, action_flow_name, channel_type_uuid, application_uuid, dimension_details_json, customer_uuid,
status, created_by, updated_by)
VALUES 
    ('c6dc5273-4103-4568-b3c7-0766c1028a3b', 'ai_responded', '75e4025e-2c64-422a-8355-19313aca6d48', 'a26a2650-19f8-49de-a6e5-7aa73841acb0', '[{"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "0fb8ade8-89bd-44a5-8bca-7366db429bf2"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "4fe863f9-85ea-47d2-af00-81a7e192b5fd"}]}], "sentiment": "*"}, {"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "1403f488-4458-4a82-8860-6fcd55a059b1"}]}], "sentiment": [{"uuid":"78b341b1-015e-42fc-a3ea-adfe46208c4e"},{"uuid":"92eeab8c-4dfe-4c6e-9023-a589a6ed1dc8"},{"uuid":"b7e12851-fed2-49a1-bf4d-220423dae620"},{"uuid":"cd29986b-887c-4e37-880e-ac28cfd64989"}]}, {"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "1403f488-4458-4a82-8860-6fcd55a059b1"}]}], "sentiment": [{"uuid":"3d2b78f9-be76-4459-b702-2fd2dc10ad79"},{"uuid":"9abdd3f4-f380-407d-bc46-5f7c172574e7"}]}]','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     true, NULL, NULL),
    ('632179f6-a10b-4a50-861b-64a890d9cf95', 'ai_assisted', '75e4025e-2c64-422a-8355-19313aca6d48', 'a26a2650-19f8-49de-a6e5-7aa73841acb0', '[{"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "4fe863f9-85ea-47d2-af00-81a7e192b5fd"}]}], "sentiment": "*"}, {"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "0fb8ade8-89bd-44a5-8bca-7366db429bf2"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "1403f488-4458-4a82-8860-6fcd55a059b1"}]}], "sentiment": "*"},{"intent": [{"uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": [{"uuid": "170ac23e-705d-4028-b75a-6ddc1d3364c1"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]},{"intent": [{"uuid": "2e03e50c-d691-4a66-8733-ff639855dfcb", "sub_intent": [{"uuid": "cc69b53f-d8c7-4517-84de-f9b204d4a689"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]},{"intent": [{"uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": [{"uuid": "9e563c2c-a961-456f-9326-202a1f2c0cce"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "e1ce93aa-33ea-47a4-aafb-d50d355cdba9"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]},{"intent": [{"uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": [{"uuid": "9e563c2c-a961-456f-9326-202a1f2c0cce"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]}]','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     true, NULL, NULL),
    ('fc96493d-0e50-42de-b8a0-9dd95d2bc0c2', 'manually_handled', '75e4025e-2c64-422a-8355-19313aca6d48', 'a26a2650-19f8-49de-a6e5-7aa73841acb0', '{}','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     true, NULL, NULL);
    

-- change this details 

INSERT INTO email_server (email_server_uuid, server_type, server_url, email_provider_name, port, is_ssl_enabled, sync_time_interval, customer_uuid, application_uuid, created_by, updated_by)
VALUES
    ('123e4567-e89b-12d3-a456-426614174000', 'IMAP', 'imap.gmail.com', 'Gmail', '993', true, 5, NULL, 'a26a2650-19f8-49de-a6e5-7aa73841acb0', NULL, NULL),
    ('123e4567-e89b-12d3-a456-426614174001', 'SMTP', 'smtp.gmail.com', 'Gmail', '587', true, NULL, NULL, 'a26a2650-19f8-49de-a6e5-7aa73841acb0', NULL, NULL),
    ('123e4567-e89b-12d3-a456-426614174002', 'IMAP', 'outlook.office365.com', 'Outlook', '993', true, 5, NULL, 'a26a2650-19f8-49de-a6e5-7aa73841acb0', NULL, NULL),
    ('123e4567-e89b-12d3-a456-426614174003', 'SMTP', 'smtp.office365.com', 'Outlook', '587', true, NULL, NULL, 'a26a2650-19f8-49de-a6e5-7aa73841acb0', NULL, NULL);


    
-- Inserting 5 entries with different data but the same customer_uuid
INSERT INTO customer_clients (customer_client_uuid, customer_client_geography_uuid, customer_client_domain_name, customer_client_name, customer_client_tier_uuid, customer_uuid,
 customer_client_details_json, created_by, updated_by)
VALUES 
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'walmartservicechannel@gmail.com', 'Walmart', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'lululemonservicechannel@gmail.com', 'Lululemon', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'spencertechservicechannel@gmail.com', 'Spencertech', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL);

  
 -- Insert data into client_users table
INSERT INTO client_users (client_user_uuid, first_name, last_name, email_id, dimension_uuid, customer_client_uuid,
created_by, updated_by)
VALUES
    ('1af2ee1b-be0b-497f-bc62-20cd36136ec5', 'Spencertech', 'Service Channel', 'spencertechservicechannel@gmail.com', 'e1ce93aa-33ea-47a4-aafb-d50d355cdba9', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22',
     NULL, NULL),
    ('305391c8-2ea7-40a2-abaa-19fda01945a4', 'Lululemon', 'Service Channel', 'lululemonservicechannel@gmail.com', 'af4b435f-d08a-49f7-bb15-b28a46d028d7', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 
     NULL, NULL),
    ('3bd091d5-bf5c-4c3e-b9e0-40a3e88eb68d', 'Walmart', 'Service Channel', 'walmartservicechannel@gmail.com', 'af4b435f-d08a-49f7-bb15-b28a46d028d7', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24', 
     NULL, NULL);


-- Insert data into user_email_settings table
INSERT INTO user_email_settings (user_email_uuid, user_name, password_hash, email_type, customer_uuid, application_uuid, 
status, created_by, updated_by)
VALUES
    ('123e4567-e89b-12d3-a456-426634174000', 'sensormaticservicechannel@gmail.com', 'jexv xerf zihb kepf', 'Gmail', '5e4e09eb-9200-41c8-95d0-d50655bca07c', 'a26a2650-19f8-49de-a6e5-7aa73841acb0', true, NULL, NULL);



INSERT INTO emails (email_uuid, customer_uuid, customer_client_uuid, email_task_status, email_action_flow_status, email_activity, dimension_uuid, assigned_to, role_uuid)
VALUES
    ('bbf238d2-441c-47a4-b0c0-dbafd808240e', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22', 'Draft', 'ai_assisted', NULL, '4fe863f9-85ea-47d2-af00-81a7e192b5fd', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('c7758706-f247-4170-8aff-e9bc6a1f4e8c', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 'Completed', 'ai_responded', NULL, '1403f488-4458-4a82-8860-6fcd55a059b1', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('43e951cf-1d03-4013-a317-f296b02aa57e', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24', 'Sent', 'ai_assisted', NULL, '5ef670aa-53f2-44c1-82c2-0158995640b8', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('ead998b9-639b-49ec-9a6e-9d38a9d75245', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c25', 'In-Progress', 'ai_responded', NULL, '4fe863f9-85ea-47d2-af00-81a7e192b5fd', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('1675c906-3e13-4910-b1be-7978cd26e89c', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c26', 'Open', 'manually_handled', NULL, '1403f488-4458-4a82-8860-6fcd55a059b1', NULL, 'e78b736d-7654-4850-852e-19607324ddf8');
    
    
INSERT INTO email_conversations (conversation_uuid, email_uuid, email_subject, email_flow_status, email_status, email_info_json, dimension_action_json)
VALUES
    ('aa102b14-a86b-4b21-95a6-c4a0453beb16', 'bbf238d2-441c-47a4-b0c0-dbafd808240e', 'Conversation 1 for Email 1', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/9b37686d-2e90-495d-a71a-1887be182fab", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/c5b6a9a0-ee3c-442a-a058-d3f46dda53e4_PO2024006.pdf"], "sender": "customer1@vassarlabs.com", "sender_name": "John Doe", "recipients": ["recipient1@example.com", "recipient2@example.com"], "cc_recipients": ["cc1@example.com", "cc2@example.com"], "bcc_recipients": ["bcc1@example.com", "bcc2@example.com"], "email_body_summary": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac arcu at libero efficitur lobortis. Integer lobortis diam at nisi vestibulum, vel blandit ipsum luctus."}', NULL),
    ('4693aafc-7b31-4f86-bd9a-8474833f4f3d', 'bbf238d2-441c-47a4-b0c0-dbafd808240e', 'Conversation 2 for Email 1', 'manually_handled', 'Completed', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/3e2936b6-3f91-4d26-9a36-0875ab9d44fb", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/41c3f221-cc6f-42e7-9e76-47e7cf47eb80_Invoice.docx"], "sender": "customer2@vassarlabs.com", "sender_name": "Jane Smith", "recipients": ["recipient5@example.com", "recipient6@example.com"], "cc_recipients": ["cc5@example.com", "cc6@example.com"], "bcc_recipients": ["bcc5@example.com", "bcc6@example.com"], "email_body_summary": "Proin efficitur quam eget nulla vulputate, nec feugiat mi aliquet. Cras commodo urna vitae felis fringilla, vel sodales nisi ultricies. Aliquam erat volutpat."}', NULL),
    ('db61a85a-6486-4880-bebb-b8df361d8c41', 'bbf238d2-441c-47a4-b0c0-dbafd808240e', 'Conversation 3 for Email 1', 'ai_assisted', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/6d9b1e5b-d670-4953-ba39-8c90b4c5cf94", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/9bf2e534-f836-4f2d-afaf-7d982893aa81_Contract.pdf"], "sender": "customer3@vassarlabs.com", "sender_name": "Alice Johnson", "recipients": ["recipient7@example.com", "recipient8@example.com"], "cc_recipients": ["cc7@example.com", "cc8@example.com"], "bcc_recipients": ["bcc7@example.com", "bcc8@example.com"], "email_body_summary": "Fusce maximus risus id tempus bibendum. Integer varius felis et sapien malesuada, vel dapibus odio ultricies. In fringilla libero vitae quam vestibulum, sed egestas justo fermentum."}', NULL),
    ('5fc82b4b-6bb2-4b19-83c3-4e76df85d9aa', 'c7758706-f247-4170-8aff-e9bc6a1f4e8c', 'Conversation 1 for Email 2', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/7f4b5a36-03b1-44bc-bd62-303c02aeac65", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/8c97f9de-29b4-4b80-a8c4-3ff0dc7d5a57_Presentation.pptx"], "sender": "customer4@vassarlabs.com", "sender_name": "Bob Johnson", "recipients": ["recipient9@example.com", "recipient10@example.com"], "cc_recipients": ["cc9@example.com", "cc10@example.com"], "bcc_recipients": ["bcc9@example.com", "bcc10@example.com"], "email_body_summary": "Aenean consectetur lectus in nulla gravida, nec rhoncus nunc cursus. In lobortis feugiat purus vitae viverra. Vivamus vel enim id velit dignissim scelerisque."}', NULL),
    ('437b2a1a-eab7-4790-ba10-05ab3b3c70ec', '43e951cf-1d03-4013-a317-f296b02aa57e', 'Conversation 1 for Email 3', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/7f4b5a36-03b1-44bc-bd62-303c02aeac65", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/8c97f9de-29b4-4b80-a8c4-3ff0dc7d5a57_Presentation.pptx"], "sender": "customer9@example1.com", "sender_name": "Charlie Brown", "recipients": ["recipient9@example.com", "recipient10@example.com"], "cc_recipients": ["cc9@example.com", "cc10@example.com"], "bcc_recipients": ["bcc9@example.com", "bcc10@example.com"], "email_body_summary": "Aenean consectetur lectus in nulla gravida, nec rhoncus nunc cursus. In lobortis feugiat purus vitae viverra. Vivamus vel enim id velit dignissim scelerisque."}', NULL);

UPDATE action_flows
SET dimension_details_json = dimension_details_json::jsonb || '[{"intent": [{"uuid": "f0171b23-bb80-4029-b360-b012cb7b5d87", "sub_intent": [{"uuid": "6640ae2e-36c7-4a37-905d-ac516fee56fb"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]}]'::jsonb
WHERE action_flow_uuid = '632179f6-a10b-4a50-861b-64a890d9cf95';


