	--Insert Script
-- Generate UUIDv4 function
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO channel_types (channel_type_uuid, channel_type_name, application_uuid, channel_type_details_json, status, created_by, updated_by)
VALUES
    ('75e4025e-2c64-422a-8355-19313aca6d48', 'Email', '25c046fe-1766-437d-adc0-9eb1a935099e', '{}', true, NULL, NULL),
    ('154355d4-8b3f-4242-8d91-f8430837f244', 'Chat', '25c046fe-1766-437d-adc0-9eb1a935099e', '{}', true, NULL, NULL);

INSERT INTO dimension_types (dimension_type_uuid, dimension_type_name, dimension_type_details_json, parent_dimension_type_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('102376df-081e-40b4-9d46-0528de49ac72', 'GEOGRAPHY_COUNTRY', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('bc72228d-9362-4f86-a16a-21b0189575de', 'INTENT', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('d07dbc55-900e-418e-9c29-0b12857e0f3f', 'SUB_INTENT', '{}', 'bc72228d-9362-4f86-a16a-21b0189575de','75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('313c631d-13bb-4f8c-a69a-7da116e4aefa', 'CUSTOMER_TIER', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('17a33d7b-7b92-4102-92bc-d64d4070e7c7', 'SENTIMENT', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('56c00be2-95ab-4ae5-890a-1765f0945d5c', 'GEOGRAPHY_STATE', '{}', '102376df-081e-40b4-9d46-0528de49ac72', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);

    
INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('90d7fdc4-6fda-4eea-ae17-acbbb0255d92', 'Tier 1', '313c631d-13bb-4f8c-a69a-7da116e4aefa', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('77d9d961-dbd4-4263-b735-930e58745a1c', 'Tier 2', '313c631d-13bb-4f8c-a69a-7da116e4aefa', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('05d5408c-c83f-4775-a4ac-117ed5b2cc31', 'Tier 3', '313c631d-13bb-4f8c-a69a-7da116e4aefa', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('d1d778b3-d9d6-4ef3-be92-afcce4c68063', 'USA', '102376df-081e-40b4-9d46-0528de49ac72', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('b560dc0f-aa5f-4f5c-b231-4176826452c4', 'CANADA', '102376df-081e-40b4-9d46-0528de49ac72', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('2d4be7bb-aa65-4720-a585-187e4bab4d6f', 'INDIA', '102376df-081e-40b4-9d46-0528de49ac72', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('bf09bacb-0748-4334-9c0d-6f5a53440e8e', 'SPAIN', '102376df-081e-40b4-9d46-0528de49ac72', '{}', NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);
    
INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('f2d528ea-0822-4ca7-ba41-bb15f4ccc82a', 'ALABAMA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('1d008d03-7f09-4369-b13c-3eb242f08bf2', 'ALASKA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('a0e32aae-e3ec-459a-89a6-fc8af38e4608', 'ARIZONA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('5e7795f3-4e5f-48c5-a3c4-6a242aebfbaf', 'ARKANSAS', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('9eeb9825-caf9-4cc5-9615-969b0bdb49ba', 'CALIFORNIA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('d59b1e26-3287-459e-a430-73fbf54711ba', 'COLORADO', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('57479e40-63b1-44bd-8765-aca2ac11e5f4', 'CONNECTICUT', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('505ab825-69c2-4f47-8fe4-5393b6222050', 'DELAWARE', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('f6afafc5-3690-4a6d-9da8-0f68d1cad694', 'FLORIDA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('1f91efd7-4f2a-40c7-a468-aaf91bae9dc2', 'GEORGIA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('84120300-2a54-44ed-b902-c3d047e356d6', 'HAWAII', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('90517169-3e6e-4b50-9ce2-2c4c98731039', 'IDAHO', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('3b77ae0a-51f8-45ef-a5b7-76501e52f3b2', 'ILLINOIS', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('a45c20f1-5a59-48fc-ad26-d66236f47aae', 'INDIANA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('57b4ce86-ddb3-4a1f-b865-e0587ab96a14', 'IOWA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('9e8d2eaa-1bd6-4d4f-b625-cc901eeaeecd', 'KANSAS', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('d471890f-6363-4168-9f9c-80a229cbe875', 'KENTUCKY', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('79e7f9d4-88fe-4729-ab9a-3b302b2727ad', 'LOUISIANA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('14459c50-49dd-436d-8126-a19e8f4578b3', 'MAINE', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('11d834ab-11e4-4fa2-8d05-65831b520e85', 'MARYLAND', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('92b73f43-9a90-427a-bd0e-cb2ebd0d0e48', 'MASSACHUSETTS', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('cc2d443a-b85a-4c40-b992-7416c5aefa92', 'MICHIGAN', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('feb924aa-c3e4-4855-8e7d-e40d5560fca9', 'MINNESOTA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('f19b55fc-79b8-4d0b-9bdd-884102e889f4', 'MISSISSIPPI', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('0b87433d-c8b9-439c-9a0f-aa6f7bd01793', 'MISSOURI', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('2881739c-6a53-4f47-a7e3-7bdff168cd61', 'MONTANA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('c6b0583f-7388-430f-937e-4b9ad36ea10e', 'NEBRASKA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('3a3c8e6d-db96-4d10-a722-6e41b7a7e4e0', 'NEVADA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('ed96de1d-873d-4712-a658-c2aa813f70a6', 'NEW HAMPSHIRE', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('af4b435f-d08a-49f7-bb15-b28a46d028d7', 'NEW JERSEY', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('98ac6fce-238a-4698-aefb-866273e9a0e7', 'NEW MEXICO', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('0fb8ade8-89bd-44a5-8bca-7366db429bf2', 'NEW YORK', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('674a53db-48d8-4a15-9dd0-94dcea8709ee', 'NORTH CAROLINA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('8b3b2564-5db2-4125-b06f-e3e3e646d8d0', 'NORTH DAKOTA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('509fa86e-f9b7-4b54-80fb-2ecccd1e2098', 'OHIO', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('dad4656e-418d-4453-b401-853fbefcad22', 'OKLAHOMA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('f837c330-df00-471b-9fdf-b3ea7efa6703', 'OREGON', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('a93f9c3f-5219-4ef5-a9bf-ac31059ae0b8', 'PENNSYLVANIA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('8a8be122-0022-4363-af9e-b77d02535408', 'RHODE ISLAND', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('741ba430-92b4-422d-82c6-09b6561e08b1', 'SOUTH CAROLINA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('376d4eb1-aedd-42af-936c-411d7d5eefe7', 'SOUTH DAKOTA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('5dac06cc-6a78-4dc1-afde-eedb14dd43a4', 'TENNESSEE', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('e1ce93aa-33ea-47a4-aafb-d50d355cdba9', 'TEXAS', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('fe408032-cccf-464d-9d30-e1f5c90b4cdd', 'UTAH', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('c1b8c94b-1250-4459-8a77-24a34d5ae539', 'VERMONT', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('cfe1ccab-b9f0-49f0-8d4d-49da914e1dfe', 'VIRGINIA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('aafd9c63-ad4a-4269-b647-305e23f5c4cf', 'WASHINGTON', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('8cfa0423-6437-47eb-b7b5-e50893b5da48', 'WEST VIRGINIA', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('bef170a5-3a1f-4275-b8e1-4e89dd8a3313', 'WISCONSIN', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('0ba16314-2ead-48c1-bbc8-5bdafc5f5a0e', 'WYOMING', '56c00be2-95ab-4ae5-890a-1765f0945d5c', '{}','d1d778b3-d9d6-4ef3-be92-afcce4c68063', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('450e4fef-359a-456a-8218-3f8ca617e1f5', 'SERVICE_REQUEST', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d', 'PURCHASE_ORDER', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('84525baa-30d1-43fe-8d7e-00eafdc93bef', 'WARRANTY', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('2e03e50c-d691-4a66-8733-ff639855dfcb', 'SHIPMENT_STATUS', 'bc72228d-9362-4f86-a16a-21b0189575de', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
    '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('4fe863f9-85ea-47d2-af00-81a7e192b5fd', 'TROUBLESHOOTING', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('1403f488-4458-4a82-8860-6fcd55a059b1', 'ROUTINE_MAINTENANCE', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('5ef670aa-53f2-44c1-82c2-0158995640b8', 'RESOLVED', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('1a3fd73d-998a-4205-a079-fc738fa799e8', 'INSTALLAION', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','450e4fef-359a-456a-8218-3f8ca617e1f5', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('9e563c2c-a961-456f-9326-202a1f2c0cce', 'NEW_PO', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('170ac23e-705d-4028-b75a-6ddc1d3364c1', 'CHECK_PO_STATUS', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('c55c4f57-3f6f-4f62-91a2-0ef7740a84f7', 'INITIATE_WARRANTY_CLAIM', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','84525baa-30d1-43fe-8d7e-00eafdc93bef', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('cc69b53f-d8c7-4517-84de-f9b204d4a689', 'CHECK_SHIPMENT_STATUS', 'd07dbc55-900e-418e-9c29-0b12857e0f3f', '{}','2e03e50c-d691-4a66-8733-ff639855dfcb', '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);


INSERT INTO dimensions (dimension_uuid, dimension_name, dimension_type_uuid, dimension_details_json, parent_dimension_uuid, channel_type_uuid,
application_uuid, customer_uuid, status, created_by, updated_by)
VALUES 
    ('78b341b1-015e-42fc-a3ea-adfe46208c4e', 'HAPPY', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('92eeab8c-4dfe-4c6e-9023-a589a6ed1dc8', 'NEUTRAL', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('3d2b78f9-be76-4459-b702-2fd2dc10ad79', 'ANGRY', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('b7e12851-fed2-49a1-bf4d-220423dae620', 'EXPEDITE', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('cd29986b-887c-4e37-880e-ac28cfd64989', 'SATISFIED', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL),
    ('9abdd3f4-f380-407d-bc46-5f7c172574e7', 'ANXIOUS', '17a33d7b-7b92-4102-92bc-d64d4070e7c7', '{}',NULL, '75e4025e-2c64-422a-8355-19313aca6d48',
     '25c046fe-1766-437d-adc0-9eb1a935099e','5e4e09eb-9200-41c8-95d0-d50655bca07c', true, NULL, NULL);
    
    
INSERT INTO action_flows (action_flow_uuid, action_flow_name, channel_type_uuid, application_uuid, dimension_details_json, customer_uuid,
status, created_by, updated_by)
VALUES 
    ('c6dc5273-4103-4568-b3c7-0766c1028a3b', 'ai_responded', '75e4025e-2c64-422a-8355-19313aca6d48', '25c046fe-1766-437d-adc0-9eb1a935099e', '[{"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "0fb8ade8-89bd-44a5-8bca-7366db429bf2"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "4fe863f9-85ea-47d2-af00-81a7e192b5fd"}]}], "sentiment": "*"}, {"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "1403f488-4458-4a82-8860-6fcd55a059b1"}]}], "sentiment": [{"uuid":"78b341b1-015e-42fc-a3ea-adfe46208c4e"},{"uuid":"92eeab8c-4dfe-4c6e-9023-a589a6ed1dc8"},{"uuid":"b7e12851-fed2-49a1-bf4d-220423dae620"},{"uuid":"cd29986b-887c-4e37-880e-ac28cfd64989"}]}, {"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "1403f488-4458-4a82-8860-6fcd55a059b1"}]}], "sentiment": [{"uuid":"3d2b78f9-be76-4459-b702-2fd2dc10ad79"},{"uuid":"9abdd3f4-f380-407d-bc46-5f7c172574e7"}]}]','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     true, NULL, NULL),
    ('632179f6-a10b-4a50-861b-64a890d9cf95', 'ai_assisted', '75e4025e-2c64-422a-8355-19313aca6d48', '25c046fe-1766-437d-adc0-9eb1a935099e', '[{"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "4fe863f9-85ea-47d2-af00-81a7e192b5fd"}]}], "sentiment": "*"}, {"customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "0fb8ade8-89bd-44a5-8bca-7366db429bf2"}]}]}, "intent": [{"uuid": "450e4fef-359a-456a-8218-3f8ca617e1f5", "sub_intent": [{"uuid": "1403f488-4458-4a82-8860-6fcd55a059b1"}]}], "sentiment": "*"},{"intent": [{"uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": [{"uuid": "170ac23e-705d-4028-b75a-6ddc1d3364c1"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]},{"intent": [{"uuid": "2e03e50c-d691-4a66-8733-ff639855dfcb", "sub_intent": [{"uuid": "cc69b53f-d8c7-4517-84de-f9b204d4a689"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "af4b435f-d08a-49f7-bb15-b28a46d028d7"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]},{"intent": [{"uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": [{"uuid": "9e563c2c-a961-456f-9326-202a1f2c0cce"}]}], "geography": {"country": [{"uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": [{"uuid": "e1ce93aa-33ea-47a4-aafb-d50d355cdba9"}]}]}, "sentiment": "*", "customer_tier": [{"uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}]}]','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     true, NULL, NULL),
    ('fc96493d-0e50-42de-b8a0-9dd95d2bc0c2', 'manually_handled', '75e4025e-2c64-422a-8355-19313aca6d48', '25c046fe-1766-437d-adc0-9eb1a935099e', '{}','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     true, NULL, NULL);
    
    
-- change this details 
        
INSERT INTO email_server (email_server_uuid, server_type, server_url, email_provider_name, port, is_ssl_enabled, sync_time_interval, customer_uuid, 
application_uuid, created_by, updated_by)
VALUES
    ('123e4567-e89b-12d3-a456-426614174000', 'IMAP', 'imap.gmail.com', 'Gmail', '993', true, 30, '5e4e09eb-9200-41c8-95d0-d50655bca07c', 
     '25c046fe-1766-437d-adc0-9eb1a935099e', NULL, NULL),
    ('123e4567-e89b-12d3-a456-426614174001', 'SMTP', 'smtp.gmail.com', 'Gmail', 587, true, 30, '5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '25c046fe-1766-437d-adc0-9eb1a935099e', NULL, NULL);

    
-- Inserting 15 entries with different data but the same customer_uuid
INSERT INTO customer_clients (customer_client_uuid, customer_client_geography_uuid, customer_client_domain_name, customer_client_name, customer_client_tier_uuid, customer_uuid,
 customer_client_details_json, created_by, updated_by)
VALUES 
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'blazemart100@gmail.com', 'Blazemart', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'bingeflicks100@gmail.com', 'Bingeflicks', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'spendity100@gmail.com', 'Spendity', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c25', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', 'example3.com', 'Example Company 3', '05d5408c-c83f-4775-a4ac-117ed5b2cc31','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c26', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'example4.com', 'Example Company 4', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c27', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', 'example5.com', 'Example Company 5', '77d9d961-dbd4-4263-b735-930e58745a1c','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c28', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', 'example6.com', 'Example Company 6', '05d5408c-c83f-4775-a4ac-117ed5b2cc31','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c29', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'example7.com', 'Example Company 7', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c30', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', 'example8.com', 'Example Company 8', '77d9d961-dbd4-4263-b735-930e58745a1c','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c31', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', 'example9.com', 'Example Company 9', '05d5408c-c83f-4775-a4ac-117ed5b2cc31','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c32', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'example10.com', 'Example Company 10', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c33', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', 'example11.com', 'Example Company 11', '77d9d961-dbd4-4263-b735-930e58745a1c','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c34', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', 'example12.com', 'Example Company 12', '05d5408c-c83f-4775-a4ac-117ed5b2cc31','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL),
    ('2b965e4e-f3a5-4e9b-8fb7-f6706fc06c35', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', 'example13.com', 'Example Company 13', '90d7fdc4-6fda-4eea-ae17-acbbb0255d92','5e4e09eb-9200-41c8-95d0-d50655bca07c',
     '{"cc": [], "bcc": []}', NULL, NULL);

  
 -- Insert data into client_users table
INSERT INTO client_users (client_user_uuid, first_name, last_name, email_id, dimension_uuid, customer_client_uuid,
created_by, updated_by)
VALUES
    ('1af2ee1b-be0b-497f-bc62-20cd36136ec5', 'Spendity', 'Online', 'spendity100@gmail.com', 'e1ce93aa-33ea-47a4-aafb-d50d355cdba9', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22',
     NULL, NULL),
    ('305391c8-2ea7-40a2-abaa-19fda01945a4', 'Bingeflicks', 'Online', 'bingeflicks100@gmail.com', 'af4b435f-d08a-49f7-bb15-b28a46d028d7', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 
     NULL, NULL),
    ('3bd091d5-bf5c-4c3e-b9e0-40a3e88eb68d', 'Blazemart', 'Online', 'blazemart100@gmail.com', 'af4b435f-d08a-49f7-bb15-b28a46d028d7', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24', 
     NULL, NULL),
    ('8c1baf2b-44c3-4f3a-947a-143536a1fb68', 'Customer4', '4', 'customer4@vassarlabs.com', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22', 
     NULL, NULL),
    ('db7ab3e5-2a8e-4d4f-8edc-02f16934317b', 'Customer5', '5', 'customer5@vassarlabs.com', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22', 
     NULL, NULL),
    ('7ba2f1b2-1235-4e0d-b2e0-b8b9a09ef4f1', 'Customer6', '6', 'customer6@example1.com', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 
     NULL, NULL),
    ('ca0641ed-91e2-4e51-8774-f9649b7c6837', 'Customer7', '7', 'customer7@example1.com', 'bf09bacb-0748-4334-9c0d-6f5a53440e8e', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 
     NULL, NULL),
    ('27aa4969-14b2-40d6-a68e-34f15dc9d125', 'Customer8', '8', 'customer8@example1.com', 'bf09bacb-0748-4334-9c0d-6f5a53440e8e', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 
     NULL, NULL),
    ('fdb0c0ef-2f4e-4b2c-80d2-260efdb27a15', 'Customer9', '9', 'customer9@example1.com', 'bf09bacb-0748-4334-9c0d-6f5a53440e8e', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 
     NULL, NULL),
    ('7f9de814-6bae-44b7-9e53-586ba6460242', 'Customer10', '10', 'customer10@example1.com', 'bf09bacb-0748-4334-9c0d-6f5a53440e8e', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 
     NULL, NULL),
    ('afb273a3-341d-4d26-bc1d-106914989fc9', 'Customer11', '11', 'customer11@example2.com', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24', 
     NULL, NULL),
    ('728e484a-8c66-4e9c-bef3-04a7d8023923', 'Customer12', '12', 'customer12@example2.com', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24',
     NULL, NULL),
    ('2bec0ad4-4a52-41bd-84f3-a206cc4243ff', 'Customer13', '13', 'customer13@example2.com', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24',
     NULL, NULL),
    ('40a68f49-4420-4610-a2d2-0336c213a500', 'Customer14', '14', 'customer14@example3.com', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c25',
     NULL, NULL),
    ('1c608863-854b-4d10-b38a-349256a1d3af', 'Customer15', '15', 'customer15@example3.com', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c25',
     NULL, NULL),
    ('3f90b57d-f843-49c2-8433-4d6a83f99f21', 'Customer16', '16', 'customer16@example3.com', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c25',
     NULL, NULL),
    ('1049ed43-b884-4dff-a61e-789dc1aaaea7', 'Customer17', '17', 'customer17@example4.com', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c26',
     NULL, NULL),
    ('dc7dee5d-e633-4c43-a662-4b7007289a8f', 'Customer18', '18', 'customer18@example4.com', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c26',
     NULL, NULL),
    ('e6ad5dc7-beaf-4da7-9f87-18cbd32cf1ba', 'Customer19', '19', 'customer19@example4.com', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c26',
     NULL, NULL),
    ('c8c82129-a608-4898-9679-91e22f85a727', 'Customer20', '20', 'customer20@example5.com', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c27',
     NULL, NULL),
    ('6775ff5d-2b76-4cfd-8aba-a4d65868cf00', 'Customer21', '21', 'customer21@example5.com', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c27',
     NULL, NULL),
    ('ad3ed741-910e-49c4-997f-e71c4f76fb60', 'Customer22', '22', 'customer22@example5.com', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c27',
     NULL, NULL),
    ('cd95a569-66aa-413a-9e2b-dc812a8ca8a5', 'Customer23', '23', 'customer23@example6.com', 'd1d778b3-d9d6-4ef3-be92-afcce4c68063', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c28',
     NULL, NULL),
    ('7f9b1830-09c2-482f-8dbb-29364ea8696c', 'Customer24', '24', 'customer24@example6.com', 'b560dc0f-aa5f-4f5c-b231-4176826452c4', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c28',
     NULL, NULL),
    ('47d9a5e9-4708-4ce6-8450-58ccbd8b784d', 'Customer25z', '25', 'customer25@example6.com', '2d4be7bb-aa65-4720-a585-187e4bab4d6f', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c28',
     NULL, NULL);

-- Insert data into user_email_settings table

INSERT INTO user_email_settings (user_email_uuid, user_name, password_hash, email_type, customer_uuid, application_uuid, 
status, created_by, updated_by)
VALUES
    ('123e4567-e89b-12d3-a456-426634174000', 'ccsupport@vassarlabs.com', 'fcns srom chaq cmub', 'Gmail', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '25c046fe-1766-437d-adc0-9eb1a935099e', 
     true, NULL, NULL);



INSERT INTO emails (email_uuid, customer_uuid, customer_client_uuid, email_task_status, email_action_flow_status, email_activity, dimension_uuid, assigned_to, role_uuid)
VALUES
    ('bbf238d2-441c-47a4-b0c0-dbafd808240e', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22', 'Draft', 'ai_assisted', NULL, '4fe863f9-85ea-47d2-af00-81a7e192b5fd', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('c7758706-f247-4170-8aff-e9bc6a1f4e8c', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c23', 'Completed', 'ai_responded', NULL, '1403f488-4458-4a82-8860-6fcd55a059b1', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('43e951cf-1d03-4013-a317-f296b02aa57e', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c24', 'Sent', 'ai_assisted', NULL, '5ef670aa-53f2-44c1-82c2-0158995640b8', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('ead998b9-639b-49ec-9a6e-9d38a9d75245', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c25', 'In-Progress', 'ai_responded', NULL, '4fe863f9-85ea-47d2-af00-81a7e192b5fd', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
    ('1675c906-3e13-4910-b1be-7978cd26e89c', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c26', 'Open', 'manually_handled', NULL, '1403f488-4458-4a82-8860-6fcd55a059b1', NULL, 'e78b736d-7654-4850-852e-19607324ddf8'),
   ('bf2b3a06-df57-4658-87ba-65c9f884b62e', '5e4e09eb-9200-41c8-95d0-d50655bca07c', '2b965e4e-f3a5-4e9b-8fb7-f6706fc06c27', 'Draft', 'ai_assisted', NULL, '4fe863f9-85ea-47d2-af00-81a7e192b5fd', NULL, 'e78b736d-7654-4850-852e-19607324ddf8');
    
    
INSERT INTO email_conversations (conversation_uuid, email_uuid, email_subject, email_flow_status, email_status, email_info_json, dimension_action_json)
VALUES
    ('aa102b14-a86b-4b21-95a6-c4a0453beb16', 'bbf238d2-441c-47a4-b0c0-dbafd808240e', 'Conversation 1 for Email 1', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/9b37686d-2e90-495d-a71a-1887be182fab", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/c5b6a9a0-ee3c-442a-a058-d3f46dda53e4_PO2024006.pdf"], "sender": "customer1@vassarlabs.com", "sender_name": "John Doe", "recipients": ["recipient1@example.com", "recipient2@example.com"], "cc_recipients": ["cc1@example.com", "cc2@example.com"], "bcc_recipients": ["bcc1@example.com", "bcc2@example.com"], "email_body_summary": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac arcu at libero efficitur lobortis. Integer lobortis diam at nisi vestibulum, vel blandit ipsum luctus."}', NULL),
    ('4693aafc-7b31-4f86-bd9a-8474833f4f3d', 'bbf238d2-441c-47a4-b0c0-dbafd808240e', 'Conversation 2 for Email 1', 'manually_handled', 'Completed', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/3e2936b6-3f91-4d26-9a36-0875ab9d44fb", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/41c3f221-cc6f-42e7-9e76-47e7cf47eb80_Invoice.docx"], "sender": "customer2@vassarlabs.com", "sender_name": "Jane Smith", "recipients": ["recipient5@example.com", "recipient6@example.com"], "cc_recipients": ["cc5@example.com", "cc6@example.com"], "bcc_recipients": ["bcc5@example.com", "bcc6@example.com"], "email_body_summary": "Proin efficitur quam eget nulla vulputate, nec feugiat mi aliquet. Cras commodo urna vitae felis fringilla, vel sodales nisi ultricies. Aliquam erat volutpat."}', NULL),
    ('db61a85a-6486-4880-bebb-b8df361d8c41', 'bbf238d2-441c-47a4-b0c0-dbafd808240e', 'Conversation 3 for Email 1', 'ai_assisted', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/6d9b1e5b-d670-4953-ba39-8c90b4c5cf94", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/9bf2e534-f836-4f2d-afaf-7d982893aa81_Contract.pdf"], "sender": "customer3@vassarlabs.com", "sender_name": "Alice Johnson", "recipients": ["recipient7@example.com", "recipient8@example.com"], "cc_recipients": ["cc7@example.com", "cc8@example.com"], "bcc_recipients": ["bcc7@example.com", "bcc8@example.com"], "email_body_summary": "Fusce maximus risus id tempus bibendum. Integer varius felis et sapien malesuada, vel dapibus odio ultricies. In fringilla libero vitae quam vestibulum, sed egestas justo fermentum."}', NULL),
    ('5fc82b4b-6bb2-4b19-83c3-4e76df85d9aa', 'c7758706-f247-4170-8aff-e9bc6a1f4e8c', 'Conversation 1 for Email 2', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/7f4b5a36-03b1-44bc-bd62-303c02aeac65", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/8c97f9de-29b4-4b80-a8c4-3ff0dc7d5a57_Presentation.pptx"], "sender": "customer4@vassarlabs.com", "sender_name": "Bob Johnson", "recipients": ["recipient9@example.com", "recipient10@example.com"], "cc_recipients": ["cc9@example.com", "cc10@example.com"], "bcc_recipients": ["bcc9@example.com", "bcc10@example.com"], "email_body_summary": "Aenean consectetur lectus in nulla gravida, nec rhoncus nunc cursus. In lobortis feugiat purus vitae viverra. Vivamus vel enim id velit dignissim scelerisque."}', NULL),
    ('437b2a1a-eab7-4790-ba10-05ab3b3c70ec', '43e951cf-1d03-4013-a317-f296b02aa57e', 'Conversation 1 for Email 3', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/7f4b5a36-03b1-44bc-bd62-303c02aeac65", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/8c97f9de-29b4-4b80-a8c4-3ff0dc7d5a57_Presentation.pptx"], "sender": "customer9@example1.com", "sender_name": "Charlie Brown", "recipients": ["recipient9@example.com", "recipient10@example.com"], "cc_recipients": ["cc9@example.com", "cc10@example.com"], "bcc_recipients": ["bcc9@example.com", "bcc10@example.com"], "email_body_summary": "Aenean consectetur lectus in nulla gravida, nec rhoncus nunc cursus. In lobortis feugiat purus vitae viverra. Vivamus vel enim id velit dignissim scelerisque."}', NULL),
    ('79d2f8e1-f023-496d-90b1-32df780387ee', '43e951cf-1d03-4013-a317-f296b02aa57e', 'Conversation 2 for Email 3', 'manually_handled', 'Completed', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/bd1f84b8-026d-4a8b-bfa7-f42b8a814d29", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/32fca8e3-84df-4419-88f3-21f5a1cc44e3_Resume.doc"], "sender": "customer10@example1.com", "sender_name": "David Smith", "recipients": ["recipient11@example.com", "recipient12@example.com"], "cc_recipients": ["cc11@example.com", "cc12@example.com"], "bcc_recipients": ["bcc11@example.com", "bcc12@example.com"], "email_body_summary": "Duis malesuada diam nec efficitur luctus. Quisque in velit vitae tellus lacinia egestas eu in elit. Sed lobortis semper libero vel faucibus."}', NULL),
    ('39962a4f-7bad-4090-95d3-38f86cb6e52a', '43e951cf-1d03-4013-a317-f296b02aa57e', 'Conversation 3 for Email 3', 'ai_assisted', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/5f22f4a0-b93a-4d82-94b1-3dbd9dfccf38", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/6db1094d-af8c-4f27-94f1-5d2de95b2a1b_Report.pdf"], "sender": "customer10@example1.com", "sender_name": "Emma Johnson", "recipients": ["recipient13@example.com", "recipient14@example.com"], "cc_recipients": ["cc13@example.com", "cc14@example.com"], "bcc_recipients": ["bcc13@example.com", "bcc14@example.com"], "email_body_summary": "Vivamus scelerisque nisl auctor, bibendum tortor non, euismod tortor. Nulla facilisi. Aenean eget felis vel purus ullamcorper maximus."}', NULL),
    ('535cec33-b8f8-42e8-8dda-c1d331d51f76', 'ead998b9-639b-49ec-9a6e-9d38a9d75245', 'Conversation 1 for Email 4', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/4db6c18c-95aa-49ad-8f8f-481abbb0197f", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/61b16b41-61dc-4b92-bbc9-d3e47fb1480b_Statement.xlsx"], "sender": "customer11@example2.com", "sender_name": "Frank Smith", "recipients": ["recipient15@example.com", "recipient16@example.com"], "cc_recipients": ["cc15@example.com", "cc16@example.com"], "bcc_recipients": ["bcc15@example.com", "bcc16@example.com"], "email_body_summary": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Curabitur ac nisi a justo tristique tristique. Donec varius augue ut sapien tempus tempus."}', NULL),
    ('20fa4194-f649-4eae-950c-76c87301c490', 'ead998b9-639b-49ec-9a6e-9d38a9d75245', 'Conversation 2 for Email 4', 'manually_handled', 'Completed', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/bd1f84b8-026d-4a8b-bfa7-f42b8a814d29", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/32fca8e3-84df-4419-88f3-21f5a1cc44e3_Resume.doc"], "sender": "customer12@example2.com", "sender_name": "Grace Johnson", "recipients": ["recipient17@example.com", "recipient18@example.com"], "cc_recipients": ["cc17@example.com", "cc18@example.com"], "bcc_recipients": ["bcc17@example.com", "bcc18@example.com"], "email_body_summary": "Duis malesuada diam nec efficitur luctus. Quisque in velit vitae tellus lacinia egestas eu in elit. Sed lobortis semper libero vel faucibus."}', NULL),
    ('ca2bb7fc-4e34-4db8-9ad3-2cf365d0fbb9', 'ead998b9-639b-49ec-9a6e-9d38a9d75245', 'Conversation 3 for Email 4', 'ai_assisted', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/5f22f4a0-b93a-4d82-94b1-3dbd9dfccf38", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/6db1094d-af8c-4f27-94f1-5d2de95b2a1b_Report.pdf"], "sender": "customer13@example2.com", "sender_name": "Harry Smith", "recipients": ["recipient19@example.com", "recipient20@example.com"], "cc_recipients": ["cc19@example.com", "cc20@example.com"], "bcc_recipients": ["bcc19@example.com", "bcc20@example.com"], "email_body_summary": "Vivamus scelerisque nisl auctor, bibendum tortor non, euismod tortor. Nulla facilisi. Aenean eget felis vel purus ullamcorper maximus."}', NULL),
    ('ec7b4b2d-fc84-48a5-842d-295820daaa4c', '1675c906-3e13-4910-b1be-7978cd26e89c', 'Conversation 1 for Email 5', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/a6352c3d-1f5b-4f5e-b5fd-b5f3b93ed96a", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/6b8d0f85-c27a-4dd4-bddf-71163e0a2d32_Contract.pdf"], "sender": "customer14@example3.com", "sender_name": "Olivia Johnson", "recipients": ["recipient21@example.com", "recipient22@example.com"], "cc_recipients": ["cc21@example.com", "cc22@example.com"], "bcc_recipients": ["bcc21@example.com", "bcc22@example.com"], "email_body_summary": "Phasellus interdum tortor sed est gravida, ut gravida nunc varius. Vestibulum ut nunc eget ante volutpat pellentesque. Integer rhoncus magna a elit congue, non fringilla nisi bibendum."}', NULL),
    ('b8944372-89e1-4b80-9713-ba7a15b8bf3e', '1675c906-3e13-4910-b1be-7978cd26e89c', 'Conversation 2 for Email 5', 'manually_handled', 'Completed', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/13296de9-467f-45e6-91b2-c1f2c2292f82", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/5e78e7c4-7ec5-4038-9dbf-291de5a121b0_Presentation.pptx"], "sender": "customer15@example3.com", "sender_name": "Sophia Smith", "recipients": ["recipient23@example.com", "recipient24@example.com"], "cc_recipients": ["cc23@example.com", "cc24@example.com"], "bcc_recipients": ["bcc23@example.com", "bcc24@example.com"], "email_body_summary": "Nulla at metus at nibh ultrices sollicitudin. Cras fermentum, turpis quis egestas dapibus, turpis massa tincidunt risus, eu eleifend ipsum dolor ac ligula."}', NULL),
    ('d9e0e902-c057-45e5-9e12-1a26c2e0370b', '1675c906-3e13-4910-b1be-7978cd26e89c', 'Conversation 3 for Email 5', 'ai_assisted', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/9c54f6cf-d513-4596-8f5d-dbc29b4a2c42", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/2d00bc62-9372-4e5d-944f-15ef34f13114_Contract.docx"], "sender": "customer16@example3.com", "sender_name": "James Johnson", "recipients": ["recipient25@example.com", "recipient26@example.com"], "cc_recipients": ["cc25@example.com", "cc26@example.com"], "bcc_recipients": ["bcc25@example.com", "bcc26@example.com"], "email_body_summary": "Fusce eget turpis ut augue sagittis mollis in a velit. Praesent sed mauris fermentum, placerat justo sed, fermentum risus."}', NULL),
    ('7af3359b-4cb5-4904-8b15-16c8569fb82b', 'bf2b3a06-df57-4658-87ba-65c9f884b62e', 'Conversation 1 for Email 6', 'ai_responded', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/2251c8aa-f76d-4030-ba48-b2b57b76e4ab", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/f0cbdfad-1200-4eb2-a30d-fc4bf11e979b_Report.pdf"], "sender": "customer17@example4.com", "sender_name": "Charlotte Smith", "recipients": ["recipient27@example.com", "recipient28@example.com"], "cc_recipients": ["cc27@example.com", "cc28@example.com"], "bcc_recipients": ["bcc27@example.com", "bcc28@example.com"], "email_body_summary": "Nam condimentum, felis in consectetur ultricies, justo eros vehicula nulla, a fermentum dolor nisl sed lectus."}', NULL),
    ('b53534de-0fc5-4b52-af1d-8a4d5e41d12b', 'bf2b3a06-df57-4658-87ba-65c9f884b62e', 'Conversation 2 for Email 6', 'manually_handled', 'Completed', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/c6efde92-1abf-4b62-a2bc-2e6f1a34d2a7", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/8ad9d33e-08b2-4f81-ba86-141502184f0a_Presentation.pdf"], "sender": "customer18@example4.com", "sender_name": "William Johnson", "recipients": ["recipient29@example.com", "recipient30@example.com"], "cc_recipients": ["cc29@example.com", "cc30@example.com"], "bcc_recipients": ["bcc29@example.com", "bcc30@example.com"], "email_body_summary": "Integer facilisis convallis risus a ultrices. In hac habitasse platea dictumst. Integer vitae quam libero."}', NULL),
    ('d899b4e9-477f-4539-b2c5-1d2875dc2b08', 'bf2b3a06-df57-4658-87ba-65c9f884b62e', 'Conversation 3 for Email 6', 'ai_assisted', 'Open', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/8dd87f9b-d47d-4316-97e2-fc34937c6fe6", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/7e1d2f7a-1a45-42e6-8d08-68a1b2b49cfb_Report.docx"], "sender": "customer19@example4.com", "sender_name": "Alexander Smith", "recipients": ["recipient31@example.com", "recipient32@example.com"], "cc_recipients": ["cc31@example.com", "cc32@example.com"], "bcc_recipients": ["bcc31@example.com", "bcc32@example.com"], "email_body_summary": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum non risus condimentum, porta ante sit amet, ullamcorper ligula."}', NULL),
    ('d899b4e9-477f-4539-b2c5-1d2875dc2b09', 'bf2b3a06-df57-4658-87ba-65c9f884b62e', 'Conversation 4 for Email 6', 'ai_assisted', 'Draft', '{"email_body_url": "https://connected-customer.s3.amazonaws.com/Documents/8dd87f9b-d47d-4316-97e2-fc34937c6fe6", "attachments": ["https://connected-customer.s3.amazonaws.com/Documents/7e1d2f7a-1a45-42e6-8d08-68a1b2b49cfb_Report.docx"], "sender": "", "sender_name": "", "recipients": ["recipient31@example.com", "recipient32@example.com"], "cc_recipients": ["cc31@example.com", "cc32@example.com"], "bcc_recipients": ["bcc31@example.com", "bcc32@example.com"], "email_body_summary": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum non risus condimentum, porta ante sit amet, ullamcorper ligula."}', NULL);
    
        



