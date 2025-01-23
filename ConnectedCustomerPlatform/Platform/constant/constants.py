from enum import Enum

from drf_yasg import openapi
import os
from pathlib import Path

TRUE_RESPONSE = {'code': 200, 'status': True, 'result': ''}
BUILT_IN = "built-in"
FALSE_RESPONSE = {'code': 400, 'status': False, 'result': ''}
CUSTOMER_UUID = 'customer-uuid'
APPLICATION_UUID = 'application-uuid'
USER_ID = 'user-uuid'
LLM_CONFIGURATION_UUID="llm_configuration_uuid"
ACTIVITY_UUID = "activity_uuid"
IS_READ = "is_read"
SPREAD_SHEET_MACRO_ENABLED = "application/vnd.ms-excel.sheet.macroenabled.12"
EXPECTED_COLUMNS = ['ID', 'Training Phrases', 'Intent 1', 'Sub Intent 1', 'Intent 2', 'Sub Intent 2', 'Intent 3', 'Sub Intent 3', 'Intent 4', 'Sub Intent 4', 'Intent 5', 'Sub Intent 5']

BLOB_URL = "blob_url"
AZURE_STORAGE_MANAGER = "AzureStorageManager"

ADD_KEY = 'Add'
EDIT_KEY = 'Edit'
TICKET_UUID = "ticket_uuid"
PRIMARY_TICKET_UUID = "primary_ticket_uuid"
SECONDARY_TICKET_UUID = "secondary_ticket_uuid"
EMAIL_CHANNEL = 'Email'
CHAT_CHANNEL = 'Chat'
LLM_STATUS = 'llm_status'
DIMENSION_TYPE_INTENT = 'INTENT'


# Common Request Headers for Swagger
customer_uuid_header = openapi.Parameter(
    name=CUSTOMER_UUID, in_=openapi.IN_HEADER, description="Customer UUID", type=openapi.TYPE_STRING)
application_uuid_header = openapi.Parameter(
    name=APPLICATION_UUID, in_=openapi.IN_HEADER, description="Application UUID", type=openapi.TYPE_STRING)
user_id_header = openapi.Parameter(
    name=USER_ID, in_=openapi.IN_HEADER, description="User ID", type=openapi.TYPE_STRING)

chat_configuration_properties = {
    'chat_configuration_uuid': openapi.Schema(type=openapi.TYPE_STRING),
    'chat_configuration_name': openapi.Schema(type=openapi.TYPE_STRING),
    'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'read_only': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    'background_fill_type': openapi.Schema(type=openapi.TYPE_STRING),
    'background_color': openapi.Schema(type=openapi.TYPE_STRING),
}

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
    "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso",
    "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic",
    "Chad", "Chile", "China", "Colombia", "Comoros", "Congo, Democratic Republic of the",
    "Congo, Republic of the", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
    "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland",
    "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala",
    "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India",
    "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan",
    "Kazakhstan", "Kenya", "Kiribati", "Korea, North", "Korea, South", "Kosovo", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
    "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta",
    "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco",
    "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal",
    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway",
    "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru",
    "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis",
    "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
    "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia",
    "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka",
    "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand",
    "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
    "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "USA",
    "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]

# Email Server - IMAP and SMTP
SERVER_URLS = {
    'Gmail': {
        'IMAP': 'imap.gmail.com',
        'SMTP': 'smtp.gmail.com'
    },
    'Outlook': {
        'IMAP': 'outlook.office365.com',
        'SMTP': 'smtp.office365.com'
    },
    'default': {
        'IMAP': 'imap.gmail.com',
        'SMTP': 'smtp.gmail.com'
    }
}

# Swagger Tags

# Email Settings
EMAIL_SETTINGS_TAG = ["Platform - Email Server"]
USER_EMAIL_SETTINGS_TAG = ["Platform - User Email Settings"]
DIMENSION_TYPES_TAG = ["Platform - Dimension Types"]
DIMENSIONS_TAG = ["Platform - Dimensions"]
PROMPT_TEMPLATE_TAG = ["Platform - Prompt Template"]
PROMPT_TAG = ["Platform - Prompts"]
CUSTOMER_CLIENTS_TAG = ["Platform - Customer-Clients"]
CUSTOMER_CLIENTS_USERS_TAG = ["Platform - Customer-Client-Users"]
TOOLS_TAG = ["Platform - Tools"]
AGENTS_TAG = ["Platform - Agents"]
SCOPE_TAG = ["Scope"]
CHAT_CONFIGURATION_TEMPLATE_TAG = ["Platform - Chat Configuration Template"]
LLM_CONFIGURATION_TAG = ["Platform - LLM Configuration"]

# Email types
EMAIL_TYPE_GROUP = "group"
EMAIL_TYPE_INDIVIDUAL = "individual"

#Chat Configuration
CONFIG_TYPE_MAPPING = {
    "landing_page": "intent_page",
    "intent_page": "landing_page",
}
TRUE = True
FALSE = False
LANDING_PAGE_CONFIGURATION = 'landing page configuration'
PANEL_CONFIGURATION = 'panel configuration'
INTENT_PAGE_CONFIGURATION = 'intent page configuration'
#whatsapp configuration
WHATSAPP = 'whatsapp'
WEB = "web"
WHATSAPP_PROFILE_IMAGE = "Whatsapp_Profile_Image"
PENDING = "PENDING"
APPROVED = "APPROVED"
CHANNEL_UUID = "channel_uuid"
API_KEY = "API_KEY"
CHAT_CHANNEL = "Chat"
TEMPLATE_CREATION_URL = "https://graph.facebook.com/v20.0/{business_key}/message_templates"
TEMPLATE_EDITING_URL = "https://graph.facebook.com/v20.0/{template_uuid}"
BUSINESS_DETAILS_URL = "https://graph.facebook.com/v20.0/{business_id}"
START_UPLOAD_URL = "https://graph.facebook.com/v20.0/{app_id}/uploads"
UPLOAD_SESSION_URL = "https://graph.facebook.com/v20.0/upload:{upload_session_id}"
PROFILE_UPDATION_URL = "https://graph.facebook.com/v20.0/{phone_number_id}/whatsapp_business_profile"
DELETE_TEMPLATE_URL = 'https://graph.facebook.com/v16.0/{whatsapp_business_account_id}/message_templates?hsm_id={template_id}&name={template_name}'
TEMPLATE_CREATION = "template creation"
BUSINESS_INFO_FETCHING = "Fetching business Information"

TEMPLATE_PAYLOAD = {
    "name": "{template_name}",
    "language": "en_US",
    "category": "MARKETING",
    "components": [
        {
            "type": "HEADER",
            "format": "TEXT",
            "text": "{header_text}"
        },
        {
            "type": "BODY",
            "text": "{body_text}"
        }
    ]
}
BUTTON_TYPE = "QUICK_REPLY"
BUTTONS_COMPONENT = {
    "type": "BUTTONS",
    "buttons": [
        {
            "type": "{button_type}",
            "text": "{button_text}"
        }
    ]
}

VALID_FILE_TYPE = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
PROJECT_NAME = "connected-enterprise"
DOWNLOAD_INTENT_EXCEL_NAME = "download_intents.xlsx"

class ChatConfiguration:
    CONFIG_TYPE_MAPPING = {
        "landing_page": "intent_page",
        "intent_page": "landing_page",
    }
    LANDING_PAGE = "landing_page"
    INTENT_PAGE = "intent_page"
    CHAT_CONFIGURATION_UUID = "chat_configuration_uuid"
    CHAT_CONFIGURATION_NAME = "chat_configuration_name"
    DESCRIPTION = "description"
    CHAT_DETAILS_JSON = "chat_details_json"
    CHAT_CONFIGURATION_PROVIDER = "chat_configuration_provider"

class ChromaExcelSheet(Enum):
    DROP_DOWN_TABLE_SHEET = "DropDownTBL"
    USAGE = "How to use it"
    TRAINING_PHRASES = "Training Phrases"
    ROW_NUMBER = "row_number"
    TRAINING_PHRASE = "training_phrase"
    ERROR_REASON = "reason"
    ROW_INDEX = "row_index"
    TRAINING_PHRASE_ID = "training_phrase_id"
    ID_COLUMN = "ID"
    INTENT_SUBINTENT_MAP = "intent_subintent_map"
    UTTERANCES = "utterances"
    DOC_ID = "doc_id"
    INTENT_COLUMN = "Intent"

class ReasonForFailure(Enum):

    INVALID_INTENT_SUBINTENT_PAIR = "Intent is empty for the given sub-intent."
    NO_INTENT_SUBINTENT = "Training Phrase is not mapping to any intent."
    DUPLICATE_ROW = "Duplicate entries found in the sheet."
    DUPLICATE_ENTRY = "Duplicate entry - record exists in ChromaDB."

class ChromaUtils(Enum):
    FILTERED_QUERIES = "filtered_queries"
    FILTERED_EMBEDDINGS = "filtered_embeddings"
    DOC_IDS_LIST = "doc_ids_list"
    METADATA_LIST = "metadata_list"
    DIMENSION_WISE_COUNT = "dimension_wise_count"
    UPDATED_DOC_IDS = "updated_doc_ids"
    UPDATED_METADATA_LIST = "updated_metadata_list"
    ERROR_ROWS = "error_rows"

class DUPLICATES:
    MESSAGE="message"
    DUPLICATES_FOUND="duplicates_found"

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
AES_KEY_PATH = os.path.join(parent_dir, "secret/AES_key.pem")
