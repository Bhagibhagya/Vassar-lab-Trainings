from enum import Enum
import os
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


class EmailActionFlowStatus(Enum):
    TOTAL_EMAIL_RECEIVED = "total_emails_received"
    AI_RESPONDED = "ai_resolved"
    AI_ASSISTED = "ai_assisted"
    MANUALLY_HANDLED = "manually_resolved"
    PROCESSING = "processing"
    NEED_ASSISTANCE = "need_assistance"
    NEED_ATTENTION = "need_attention"
    OPEN = "open"


class EmailType(Enum):
    NEW = "New"
    REPLY = "Reply"
    FORWARDED = "Forwarded"


class EmailTaskStatus(Enum):
    OPEN = "Open"
    IN_PROGRESS = "in_progress"
    DRAFT = "Draft"
    COMPLETED = "Completed"
    SENT = "Sent"
    UNIDENTIFIED = "Unidentified"
    NEED_REVIEW = "need_review"


# Email status codes
class Action(Enum):
    ai_resolved = "ai_resolved"
    ai_assisted = "ai_assisted"
    manually_resolved = "manually_resolved"
    need_assistance = "need_assistance"
    need_attention = "need_attention"


class PromptType(Enum):
    Prompt = "PROMPT"
    PromptChain = "PROMPT_CHAIN"


class PromptCategory(Enum):
    IntentSentimentClassification = "INTENT_AND_SENTIMENT_CLASSFICATION"
    CustomerGeographyIdentification = "CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION"
    DetailsExtraction = "DETAILS_EXTRACTION"
    SummaryResponseGeneration = "SUMMARY_AND_RESPONSE_GENERATION"


class DimensionTypeNames(Enum):
    GEOGRAPHY_STATE = "GEOGRAPHY_STATE"
    GEOGRAPHY_COUNTRY = "GEOGRAPHY_COUNTRY"
    INTENT = "INTENT"
    SUB_INTENT = "SUB_INTENT"
    SENTIMENT = "SENTIMENT"
    CUSTOMER_TIER = "CUSTOMER_TIER"


class TimelineTypes(Enum):
    EmailReceived = "Email_Received"
    IntentClassified = "Intent_Classified"
    DetailsExtracted = "Details_Extracted"
    ResponseGenerated = "Response_Generated"
    EmailSent = "Email_Sent"
    Validated_document = "Validated_Document"


class ServerType(Enum):
    SMTP = 'SMTP'
    IMAP = 'IMAP'
    MSAL = 'MSAL'


class MailBox(Enum):
    INBOX = 'inbox'


class TimeZones(Enum):
    IST = 'Asia/Kolkata'
    UTC = 'UTC'


class DateFormats(Enum):
    DAY_MONTHNAME_YEAR_FORMAT = "%d-%b-%Y"


class EmailMetaInfoHeaders(Enum):
    MESSAGE_ID = 'Message-ID'
    FROM = 'From'
    TO = 'To'
    SUBJECT = 'Subject'
    BCC = 'Bcc'
    CC = 'Cc'
    REFERENCES = 'References'
    IN_REPLY_TO = 'In-Reply-To'
    DATE = 'Date'


class ContentTypes(Enum):
    PLAIN_TEXT = 'text/plain'
    HTML_TEXT = 'text/html'
    MULTIPART = 'multipart'
    CONTENT_DISPOSITION = 'Content-Disposition'


class RegexTypes(Enum):
    FORWARDED_PATTERN = '([-]{10}\s+Forwarded\s+message\s+[-]{9})|([-]{5}\s+Forwarded\s+message\s+[-]{5})|([_]{32})'
    FORWARDED_EMAIL_REGEX = r'Fwd?:|Fw?:'
    REPLY_EMAIL_REGEX = r'Re:?:'
    CONTAINER_NAME_AND_BLOB_NAME = r'[^/]+/([^/]+)/(.+)' # Regex to extract the container name (first part after domain) and blob name (remaining path).
    FORWARDED_PATTERN_REGEX = r'(?s)(.*?)' + r'([-]{10}\s+Forwarded\s+message\s+[-]{9}|[-]{5}\s+Forwarded\s+message\s+[-]{5}|[_]{32})' + r'(.*)'
    FORWARDED_BODY_GMAIL = r'From:\s*(?P<from>.*\s*<.*>)\s*' + r'Date:\s*(?P<date>.*)\s*' + r'Subject:\s*(?P<subject>.*)\s*' + r'To:\s*(?P<to>.*\s*<.*>)\s*' + r'(?P<body>.*)'
    FORWARDED_BODY_OUTLOOK = r'From:\s*(?P<from>.*\s*)\s*' + r'Sent:\s*(?P<date>.*)\s*' + r'To:\s*(?P<to>.*\s*<.*>)\s*' + r'Subject:\s*(?P<subject>[^\n]*)\s*' + r'(?P<body>.*)'
    SIGNATURE_BODY_SEGREGATION = r'(?i)([-]+\s*\n|thanks\s*(?:&\s*regards)?|best\s*regards|sincerely|cheers|warm\s*regards|kind\s*regards|regards|best)(.*?)(?=--|thanks|best|sincerely|cheers|warm|kind|$)'
    FORWARDED_BODY_GMAIL_TO_CC = r'From:\s*(?P<from>.*\s*<.*>)\s*Date:\s*(?P<date>.*)\s*Subject:\s*(?P<subject>.*)\s*To:\s*(?P<to>.*\s*<.*>)\s*Cc:\s*(?P<cc>.*\s*<.*>)\s*(?P<body>.*)'
    FORWARDED_BODY_OUTLOOK_TO_CC = r'From:\s*(?P<from>.*\s*<.*>)\s*Sent:\s*(?P<date>.*)\s*To:\s*(?P<to>.*\s*<.*>)\s*(?i:Cc):\s*(?P<cc>.*\s*<.*>)\s*Subject:\s*(?P<subject>[^\n]*)\s*(?P<body>.*)'
    REPLY_PARENT_REMOVE_OUTLOOK = r"(?s)^_{32}.*$"
    REPLY_PARENT_SEGREGATION_GMAIL = r"(?s)On.*<.*>.*wrote:"
    REPLY_PARENT_REMOVE_GMAIL = r'^\s*>.*$'
    GOOGLE_GROUP_MAIL_FOOTER_PATTERN = r"--\s*\nYou received this message because you are subscribed to the Google Groups\s*\"[^\"]+\"\s*group\.\s*To unsubscribe from this group and stop receiving emails from it, send an email to\s*[^\s]+@googlegroups\.com\.\s*To view this discussion on the web visit https://groups\.google\.com/d/msgid/[^\s]+"
    VALIDATE_NAME_FOR_CHARS_WITHOUT_END_START_SPACE = r"^[a-zA-Z0-9][a-zA-Z0-9_\s-]*[a-zA-Z0-9]$"  # Check for allowed characters and no starting/ending space or hyphen or underscore
    CONSECUTIVE_SPACE_HYPHEN = r"[_\s-]{2}"  # Check for no consecutive spaces, hyphens, or space-hyphen combinations

UnitPrice = 'Unit Price'

FWD_SENDER_NAME_REGEX = '<strong\s*class="gmail_sendername"[^>]*>(.*?)</strong>'
FWD_MAILTO_REGEX = 'href="mailto:(.*?)"'

INVENTORY_FILEPATH = "https://docs.google.com/spreadsheets/d/1dYm2Ctm7we-B4haOmvMnbT-1S4yN63rxN6VJ_ASqYgs/export?format=csv&gid=0"
ORDER_STATUS_FILEPATH = "https://docs.google.com/spreadsheets/d/1dYm2Ctm7we-B4haOmvMnbT-1S4yN63rxN6VJ_ASqYgs/export?format=csv&gid=1334190115"
INVOICE_FILEPATH = "https://docs.google.com/spreadsheets/d/1s0GBOXVBCjE7vMZ69Wh3iYxxiAUFoOd0ehkNnZwQSB0/export?format=csv&id=1s0GBOXVBCjE7vMZ69Wh3iYxxiAUFoOd0ehkNnZwQSB0&gid=0"

TRUE_RESPONSE = {'code': 200, 'status': True, 'result': ''}
FALSE_RESPONSE = {'code': 400, 'status': False, 'result': ''}

SMTP_HOST_DATA = 'smtp.gmail.com'
SMTP_PORT_DATA = 587

CSR_ID = "86511840-9b7f-4c6e-b378-26d017a422df"

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = 'us-west-2'
AWS_STORAGE_BUCKET_NAME = 'connected-customer'

ATTACHMENTS_FOLDER_PATH = os.path.join(settings.BASE_DIR, "attachments/")


class DateFormats(Enum):
    MM_DD_YYYY = '%m/%d/%Y'


class EmailDashboardParams(Enum):
    CUSTOMER_UUID = "customer-uuid"
    START_DATE = "start_date"
    END_DATE = "end_date"
    CUSTOMER_CLIENT_UUID = "customer_client_uuid"
    SENDER_NAME = "sender_name"
    EMAIL_ID = "email_id"
    INTENT = "intent"
    STATUS = "status"
    CUSTOMER_NAME = "customer_name"
    GEOGRAPHY = "geography"
    CUSTOMER_TIER = "customer_tier"
    EMAIL_ACTION_FLOW_STATUS = "email_action_flow_status"
    PAGE_NUMBER = "page_number"
    TOTAL_ENTRY_PER_PAGE = "total_entry_per_page"
    USER_UUID = "user-uuid"
    ROLE_UUID = "role_uuid"
    APPLICATION_UUID = "application-uuid"
    CHANNEL_TYPE_UUID = "channel_type_uuid"


class EmailConversationParams(Enum):
    EMAIL_UUID = "email_uuid"
    EMAIL_CONVERSATION_UUID = "email_conversation_uuid"
    FROM_EMAIL_ID = "from_email_id"
    TO = "to"
    BCC = "bcc"
    CC = "cc"
    IN_REPLY_TO = "in_reply_to"
    SUBJECT = "subject"
    BODY = "body"
    ATTACHMENTS = "attachments"
    DETAILS_EXTRACTED_JSON = "details_extracted_json"
    INSERT_TS = "insert_ts"
    UPDATED_TS = "updated_ts"
    SEND = "send"
    REMOVE_ATTACHMENTS = "attachments_to_remove"
    INSERTED_TS = "inserted_ts"
    FILE_URL = "file_url"
    FILES_URL_LIST = "files_url_list"
    EMAIL_UUIDS_LIST = "email_uuids_list"

class EmailDraftParams(Enum):
    DRAFT = "draft"
    EMAIL_INFO_JSON = "email_info_json"
    DIMENSION_ACTION_JSON = "dimension_action_json"
    CONVERSATION_UUID = "conversation_uuid"
    EMAIL_SUBJECT = "email_subject"
    EMAIL_FLOW_STATUS = "email_flow_status"
    EMAIL_STATUS = "email_status"
    PARENT_UUID = "parent_uuid"


class EmailReplyParams(Enum):
    SMTP = "SMTP"
    GMAIL = "Gmail"
    EXTRACTED_ORDER_DETAILS = "extracted_order_details"
    VERIFIED = "verified"
    SENDER = "sender"
    CUSTOMER_CLIENT_NAME = "customer_client_name"


class ChannelTypes(Enum):
    EMAIL = "email"


class ChannelTypesUUID(Enum):
    EMAIL = "ee17c351-1331-4d8b-a183-27e0243bdba2"


class ExcelColumns(Enum):
    UNIT_PRICE = "Unit Price"
    QUANTITY = "Quantity"

class CategoriesForPersonalization(Enum):
    CLASSIFICATION_CATEGORY = "dimension_classification"
    RESPONSE_GENERATION_CATEGORY = "response_generation_category"
    INTENT_CLASSIFICATION_CATEGORY = "intent_classification"


class CsrChromaDbFields(Enum):
    IS_DEFAULT = "is_default"
    USER_UUID = "user_uuid"
    RESPONSE_CONFIG_UUID = "response_config_uuid"
    DEFAULT_TEMPLATE = "default_template"
    CSR_UUID = "csr_uuid"
    INTENT = "intent"
    SUB_INTENT = "sub_intent"
    SENTIMENT = "sentiment"
    RESPONSES_FILE = "response_file"
    FILE_URL = "file_url"
    TIME_STAMP = "time_stamp"
    CATEGORY = "category"
    TEXT_TO_SHOW="textToShow"
    BULK_ADDITION="bulk_addition"

class DefaultResponsesTemplate(Enum):
    HEADER_1 = "Response I"
    HEADER_2 = "Response II"
    HEADER_3 = "Response III"
    TEMPLATE_URL="https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-19/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx"
    SHEET_NAME_OF_RESPONSES="Knowledge"

PROFANE_WORDS_LIST = ["towelhead", "shyt", "nigga", "spaz", "cripple", "gimp", "midget", "blasphemer"]


class ChromadbMetaDataParams(Enum):
    USER_UUID = "user_uuid"
    DIMENSION_UUID = "dimension_uuid"
    CATEGORY = "category"
    PARAMS = "params"
    CREATED_TIMESTAMP = "created_at"
    UPDATED_TIME_STAMP = "updated_at"
    DIMENSION_NAME = "dimension_name"
    DIMENSION_NAMES = "dimension_names"
    TYPE_OF_ADDITION="type_of_addition"
    INTENT = "INTENT"
    SUB_INTENT = "SUBINTENT"
    SEPARATOR = ","
    SUB_INTENT_FILTER = "is_subintent"
    INTENT_UUID = "intent_uuid"
    MAPPING_UUID = "mapping_uuid"
    PARENT_DIMENSION_NAME = "parent_dimension_name"
    LENGTH_FOR_INTENT = 2
    LENGTH_FOR_SUB_INTENT = 3

class ChromaParams(Enum):
    METADATAS= 'metadatas'
    DOCUMENTS = 'documents'
    EMBEDDINGS = 'embeddings'



class UtterancesGeneratorParams(Enum):
    INTENT = "intent"
    DESCRIPTION = "description"
    ID = "id"
    UTTERANCE = "utterance"
    CONTENT = "content"

class PaginationParams(Enum):
    PAGE_NUM = "page_number"
    TOTAL_ENTRY_PER_PAGE = "total_entry_per_page"
    TOTAL_ENTRIES = "total_entries"
    TOTAL_PAGES = "total_pages"


class ChromaDBParams(Enum):
    IDS="ids"
    DOCUMENTS = "documents"
    METADATA = "metadatas"

class DefaultPaginationValues(Enum):
    PAGE_NUM = 1
    TOTAL_ENTRIES = 0
    TOTAL_PAGES = 1


PREFIX_FOR_EMAIL_CHROMA_COLLECTION_NAME="email_"

BOOLEAN_TRUE_STRING="true"

class BlobConstants:
    BLOB_SEPARATOR = '/'
    FILENAME_PART_SEPARATOR = '_'
    BLOB_URL_LIST = "blob_url_list"
class CategeriesForPersonalization(Enum):
    INTENT_CLASSIFICATION_CATEGORY = "intent_classification"
    RESPONSE_GENERATION_CATEGORY = "response_generation_category"

class PromptCategory(Enum):
    IntentClassification = "INTENT_CLASSIFICATION_PROMPT"
    CustomerGeographyIdentification = "CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION"
    DetailsExtraction = "DETAILS_EXTRACTION"
    SummaryResponseGeneration = "SUMMARY_AND_RESPONSE_GENERATION"
    SentimentClassification = "SENTIMENT_CLASSIFICATION"
    SummaryGeneration = "SUMMARY_GENERATION"
    email_summary_generation="EMAIL_SUMMARY_GENERATION"
    SubIntentClassification="SUB_INTENT_CLASSIFICATION_PROMPT"


EMAIL_ADDRESS_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

class BulkImportExcelHeaders:
    TRAINING_PHRASES_HEADER="Training Phrases"
    DESCRIPTION_HEADER="Intent Description"

BULK_IMPORT_EXCEL_FILE="bulk_import_excel_file"
INTENT_TRAINING_PHRASES_INSTRUCTIONS_TEMPLATE_FILE_NAME='intents_training_phrases_instructions_template.xlsx'
SPREAD_SHEET_CONTENT_TYPE='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
EXCEL_CONTENT_TYPE='application/vnd.ms-excel'
INSTUCTIONS_SHEET_NAME_OF_EXCEL='Instructions'
SPREAD_SHEET_MACRO_ENABLED = "application/vnd.ms-excel.sheet.macroenabled.12"
EXPECTED_COLUMNS = ['ID', 'Training Phrases', 'Intent 1', 'Sub Intent 1', 'Intent 2', 'Sub Intent 2', 'Intent 3', 'Sub Intent 3', 'Intent 4', 'Sub Intent 4', 'Intent 5', 'Sub Intent 5']

PDF_PROCESSING_STEP_NAME = "PDF PROCESSING"
class FileExtensions(Enum):
    XLSX='.xlsx'
    XLS='.xls'
    XLSM = '.xlsm'

class Role_names(Enum):
    ADMIN="admin"

class Configure(Enum):
    BODY_LENGTH=50



class TicketParams(Enum):
    TICKET_UUID = "ticket_uuid"

class EmailProvider(Enum):
    GMAIL = "Gmail"
    OUTLOOK = "Outlook"


SECRET_NAME_FORMAT_PREFIX = "microsoft-secret-"


class MicrosoftSecretDetailsKeys(Enum):
    ACCESS_TOKEN = 'access_token'
    CLIENT_SECRET = 'client_secret'
    SECRET_EXPIRY = 'secret_expiry'
    SECRET_CREATED_TS = 'secret_created_ts'

class OutlookUrlsEndPoints(Enum):
    DEFAULT_SCOPE="https://graph.microsoft.com/.default"
    AUTHORITY_URL="https://login.microsoftonline.com/{microsoft_tenant_id}"
    # Microsoft Graph API URL to fetch user profile(test connection)
    USER_PROFILE_URL = "https://graph.microsoft.com/v1.0/users/{EMAIL_ID}"
    BASE_URL = "https://graph.microsoft.com/v1.0"
    GET_PERMISSIONS="https://graph.microsoft.com/v1.0/me/appRoleAssignments"

class MicrosoftGraphPermissions(Enum):
    # MAIL_READ_BASIC_ALL="Mail.ReadBasic.All"
    MAIL_SEND="Mail.Send"
    MAIL_READ_ALL="Mail.Read.All"
    USER_READ_BASIC_ALL="User.ReadBasic.All"
    MAIL_READ_WRITE="Mail.ReadWrite"

CODE_FOR_AUTHENTICATION_ERROR_GRAPH_API="InvalidAuthenticationToken"


class FileUploadNames(Enum):
    EMAIL_BODY_FILE_NAME = "{email_uuid}/body.{content_type}"
    ATTACHMENTS_FILE_NAME = "{email_uuid}/attachments/{attachment_name}"


class FileContentTypes(Enum):
    HTML = "html"
    TEXT = "txt"
    JSON = "json"

class ReturnTypes(Enum):
    URL = "url"



