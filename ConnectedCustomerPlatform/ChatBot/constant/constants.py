import uuid
from enum import Enum
from drf_yasg import openapi

from ChatBot.dataclasses.entity_data import AttributeDetailsJson
from ChatBot.dataclasses.knowledge_sources_data import FileAttributeDetailsJson
from ChatBot.dataclasses.sme_data import ImageAttachment, VideoAttachment

class Constants:
    TOTAL_USERS = "total_users"
    TOTAL_CONVERSATIONS_TIME_SERIES = "total_conversations_time_series"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AVG_DAILY = "avg_daily"
    AVG_WEEKLY = "avg_weekly"
    AVG_MONTHLY = "avg_monthly"
    COUNT = "count"
    DATE = "date"
    TOTAL_CONVERSATIONS_AVERAGE = "total_conversations_average"
    SUCCESSFUL_CONVERSATION = "successful_conversation"
    UNSUCCESSFUL_CONVERSATION = "unsuccessful_conversation"
    AUTHENTICATED_USERS = "authenticated_users"
    UNAUTHENTICATED_USERS = "unauthenticated_users"
    ACTIVE_USERS = "active_users"
    TOTAL_CONVERSATIONS = "total_conversations"
    FALLBACK_RATE = "fallback_rate"
    BOUNCE_RATE = "bounce_rate"
    INTERACTION_RATE = "interaction_rate"
    CONTAINMENT_RATE = "containment_rate"
    CONTAINMENT_RATE_DIMENSIONS = "containment_rate_dimensions"
    SESSION_DURATION = "session_duration"
    INTENTS = "intents"
    INTENT = "intent"
    SENTIMENT = "sentiment"
    TRANSFERS = "transfers"
    FALLBACK_CONVERSATIONS = "fallback_conversations"
    TOTAL_VISITS = "total_visits"
    USERS_INTERACTED = "users_interacted"
    BOUNCES = "bounces"
    USER_DETAIL_JSON_UID = "user_details_json__uid"
    UNDER_1_MINUTE = "under_1_minute"
    UNDER_3_MINUTE = "under_3_minute"
    UNDER_5_MINUTE = "under_5_minute"
    UNDER_10_MINUTE = "under_10_minute"
    ABOVE_10_MINUTES = "10+ min"
    USER_TYPE = "NON_AUTHENTICATED"
    VALID_MARKER_STATUS = {"READ", "DELIVERED", "LOGGED"}
    READ = "READ"
    DELIVERED = "DELIVERED"
    DELIVERY_MARKER = "deliveryMarker"
    CACHE_THRESHOLD = 20
    CSR_UID = "csr_uid"
    NAME = "name"
    PROFILE_PICTURE = "profilePicture"
    CSR_INFO_JSON = "csr_info_json"
    SATISFACTION_LEVEL = "satisfaction_level"
    ADDITIONAL_COMMENTS = "additional_comments"
    BLOB_NAME = "blob_name"
    PUBLIC_URL = "public_url"
    URL = "url"
    TYPE = "type"
    START_TIME = "start_time"
    TICKET_ID = "ticket_id"
    SUMMARY = "summary"
    USER_DETAILS = "user_details"
    FILE_NAME = "file_name"
    SATISFACTION_CHOICES = ["Poor" , "Average" , "Great"]
    USER_ID = "user_id"
    STATUS = "status"
    ASSIGNED_TIME = "assigned_time"
    USER_STATUS_ENDPOINT = "users/online"
    BOT_ONGOING= "BOT_ONGOING"
    CSR_RESOLVED = "manually_resolved"
    BOT_RESOLVED = "ai_resolved"
    CLOSED = "CLOSED"
    OFFLINE = "Offline"
    ONLINE = "Online"
    ASSIGNED = "Assigned"
    CONVERSATIONS_STATUS = "conversation_status"
    CONVERSATION_UUID = "conversation_uuid"
    CHAT_CONVERSATION_UUID = "chat_conversation_uuid"
    APPLICATION_UUID="application_uuid"
    CUSTOMER_UUID="customer_uuid"
    CONNECTION_UUID="connection_uuid"
    CSR_STATUS = "csr_status"
    POST = "post"
    GET = "get"
    PUT = "put"
    CONTAINER_NAME = "connected-enterprise"
    CSR_ONGOING = "CSR_ONGOING"
    COUNT = 'count'
    ROLE_ID = "f4242f59-2ff2-424b-9b0d-197faa807874"
    ANONYMOUS = "Anonymous"
    TYPING_INDICATOR = "typingIndicator"
    MESSAGE = "message"
    NO_CSR_ONLINE = "Sorry,Currently no Agents are Online"
    NO_HEADERS = "Missing required headers or parameters."
    NO_FILE_PROVIDED = "No files provided in the request."
    AUTHORIZATION_ATTRIBUTE = "Authorization"
    CSR_RESOLVED_MESSAGE="your issue has been resolved"
    NOTIFICATION="notification"
    CHAT_CHANNEL_TYPE_UUID = "154355d4-8b3f-4242-8d91-f8430837f244"
    CHANNEL_TYPE_UUID = "154355d4-8b3f-4242-8d91-f8430837f244"
    MESSAGE_DETAILS_JSON = "message_details_json"
    DIMENSION_ACTION_JSON = "dimension_action_json"
    DIMENSIONS = "dimensions"
    DIMENSION = "dimension"
    DIMENSION_INTENT = "Intent"
    VALUE = "value"
    INITIAL_MESSAGE = "Hello, what can I help you with today?"
    MESSAGE_TEXT = "message_text"
    INITIAL_MESSAGE_INTENT = "Banter"
    SOURCE = "source"
    USER = "user"
    BUTTON = "button"
    DIMENSION_TYPE_NAME_INTENT = "INTENT"
    MAX_REGENERATE_COUNT = 2
    INACTIVE = "Inactive"
    HOT_HANDOFF_SUCCESSFUL_MESSAGE = "Transfer was successful"
    HOT_HANDOFF_UNSUCCESSFUL_MESSAGE = "Transfer was unsuccessful"
    BROADCAST_TO_CSR_SUCCESS_MESSAGE = "broadcasting to csr is successful"
    NOTIFY_USER_SUCCESS_MESSAGE = "notification to user is successful"
    TURN = "turn"
    TEMPLATE_LANGUAGE_CODE = "en_US"
    WHATSAPP_MAX_MESSAGE_CHAR_LIMIT = 4096
    INVISIBLE_SPACE = "ㅤ" *2 #Special Character to add space before whatsapp message
    LIST_DOT = "•"
    CHAT = "chat"
    END_CONVO="end_convo"
    START_CONVO = "start_convo"
    CONVERSATION_STATUS = "conversation_status"
    INSERT_TS = "insert_ts"
    APPROVED_TEMPLATE_STATUS = "APPROVED"
    GENERATED='generated'
    GENERATING='generating'
    TO_BE_GENERATED='to_be_generated'
    IMAGE='image'
    VIDEO='video'
    CHAT_CONVERSATION_UUID = "chat_conversation_uuid"
    INSERTED_TS = "inserted_ts"
    ADD = "Add"
    EDIT = "Edit"
    TIME = "time"
class CustomCloseCodes:
    # close_code 4001 means hot_handoff successful : current csr is successfully transferred the conversation to new csr. so need to close his connection
    HOT_HANDOFF_SUCCESSFUL_CODE = 4001
    # when csr click mark as resolved button , UI will send 4000 closed code while disconnecting csr
    CSR_MARK_AS_RESOLVED_CODE = 4000


class AgentDashboardConstants:
    CONVERSATION = "conversation"
    ACTIVE = "Active"
    VALID_CSR_STATUS = {"Active", "Assigned"}
    USER_DETAILS_JSON = "user_details_json"
    MESSAGE_DETAILS_JSON = "message_details_json"
    MESSAGE_TEXT = "message_text"
    CREATED_AT = "created_at"
    USER_PROFILE_PICTURE = "user_profile_picture"
    PROFILE_PICTURE = "profilePicture"
    LATEST_MESSAGE = "latest_message"
    NAME = "name"
    TIME = "time"
    MEDIA_URL = "media_url"
    SUMMARY = "summary"
    ROLE_ID_NOT_GIVEN = "Role_id is not provided"
    MESSAGE_INDEX=-1


class Suggestions(Enum):
    ORDER_STATUS = "Order Status"
    PRODUCT_AVAILABILITY = "Product Availability"
    DAMAGE = "Damage"
    TRADE_APP = "Trade App"


class Placeholder(Enum):
    PLACE_HOLDER = "Please select from the below suggestions or type in your query"


class InputType(Enum):
    BUTTON = "button"
    TEXT = "text"


class AdditionalText(Enum):
    SELECT_VALUE = "please select the value from here"


specification_json = {
    "suggestion_text": "Please select from the options below or type in your response",
    "suggestions": [
        {
            InputType.BUTTON.value: {
                "Is_single_selection": False,
                "options": [
                    Suggestions.ORDER_STATUS.value,
                    Suggestions.PRODUCT_AVAILABILITY.value,
                    Suggestions.DAMAGE.value,
                    Suggestions.TRADE_APP.value
                ]
            }
        }
    ],
    "placeholder": Placeholder.PLACE_HOLDER.value
}


class CaptchaConstants:
    CAPTCHA_IMAGE = "captcha_image"
    ENCODE_TEXT = "encoded_text"
    WIDTH = 196
    HEIGHT = 36
    LENGTH = 5



class KnowledgeSourceTypes(Enum):
    PDF = 'pdf'
    WORD = 'word'
    PPT = 'ppt'
    VIDEO = 'video'
    WEB = 'web'
    EXCEL = 'excel'
    IMAGE = 'image'
class KnowledgeSourceConstants:
    KNOWLEDGE_SOURCE_TYPE_MAP = {
        '.ppt': KnowledgeSourceTypes.PPT.value,
        '.pdf': KnowledgeSourceTypes.PDF.value,
        '.pptx': KnowledgeSourceTypes.PPT.value,
        '.mp4': KnowledgeSourceTypes.VIDEO.value,
        '.avi': KnowledgeSourceTypes.VIDEO.value,
        '.webm': KnowledgeSourceTypes.VIDEO.value,
        '.mpg': KnowledgeSourceTypes.VIDEO.value,
        '.mpeg': KnowledgeSourceTypes.VIDEO.value,
        '.mkv': KnowledgeSourceTypes.VIDEO.value,
        '.wmv': KnowledgeSourceTypes.VIDEO.value,
        '.docx': KnowledgeSourceTypes.WORD.value,
        '.doc': KnowledgeSourceTypes.WORD.value,
        '.csv': KnowledgeSourceTypes.EXCEL.value,
        '.xlsx': KnowledgeSourceTypes.EXCEL.value,
        '.xls': KnowledgeSourceTypes.EXCEL.value,
        '.jpg': KnowledgeSourceTypes.IMAGE.value,
        '.jpeg': KnowledgeSourceTypes.IMAGE.value,
        '.png': KnowledgeSourceTypes.IMAGE.value,
    }
    FILE_UPLOAD_MAX_MEMORY_SIZE = 1000 * 1024 * 1024
    INTERNALFORMAT_JSON_FILE_NAME = 'internalFormat.json'

    GOOGLE_DRIVE_MIME_TYPE_MAP = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ppt": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    FILE_UPLOAD_SOURCE_CHOICES=['google_drive','one_drive']
    GOOGLE_DRIVE_API_BASE_URL = "https://www.googleapis.com/drive/v3/files/"
    ONEDRIVE_API_BASE_URL = "https://graph.microsoft.com/v1.0/me/drive/items/"
    
    GOOGLE_APPS_MIME_TYPE_PREFIX = "application/vnd.google-apps"  # Add this constant

    REVIEW_FILE_PDF = "review_file.pdf"
    SME = 'sme'
    KNOWLEDGE_BASE = 'knowledge_base'
    VALID_IMAGE_TYPES = ['jpg','jpeg','png','tiff']
    VALID_IMAGE='Valid image'
    MAXIMUM_IMAGE_SIZE=5

    KNOWLEDGE_SOURCE_UUID = "knowledge_source_uuid"
    PROCESSING = "Processing",
    UNDER_REVIEW = "Under Review",
    REVIEWED = "Reviewed",
    FAILED = "Failed",
    REVIEWING = "Reviewing"
    QA_GENERATING = "QA Generating"
    CHUNKING = "chunking"
    PAGES = "pages"
    BAR_CHART = "Bar chart"
    PIE_CHART = "Pie chart"
    SCATTERPLOT = "Scatterplot"
    STACKED_BAR_CHART = "Stacked bar chart"
    BUBBLE_CHART = "Bubble chart"
    DONUT_CHART = "Donut chart"
    WATERFALL_CHART = "Waterfall chart"
    ORGANIZATIONAL_CHART = "Organizational chart"
    MISCELLANEOUS = "Miscellaneous"

    LIST_DATA_CHART_NAMES = [BAR_CHART, PIE_CHART, SCATTERPLOT, STACKED_BAR_CHART, BUBBLE_CHART, DONUT_CHART, WATERFALL_CHART]

    KEYWORDS = ["bar", "pie", "column", "donut", "scatter", "bubble"]

    PLAIN_TEXT = "plain_text"
    STRING = "string"
    LIST = "list"
    DICT = "dict"
    DATA = "data"
    JSON_KEY = "json_key"
    VALUE = "value"
    BLOCKS = "blocks"
class InternalJsonConstants:
    PAGE = "page"
    CONTENT_TYPE = "content_type"
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    CONTENT = "content"
    BLOCK_ID = "block_id"
    BLOCKS = "blocks"
    METADATA = "metadata"
    NAME = "name"
    CLASSIFICATION = "classification"
    IMAGE_DATA = "image_data"
    TITLE = "title"
    TYPE = "type"
    DATA = "data"

class EntityConstants:
    DEFAULT_ENTITY_NAME = "default"
    DEFAULT_ATTRIBUTE_NAME = "default"
    DEFAULT_ATTRIBUTE_VALUE = "default"
    DEFAULT_ENTITY_DESC = "default product",
    ASSIGN_UNASSIGN_CHOICES = ['assign','unassign']

class ErrorConstants:
    UNRESOLVED = "Unresolved"
    
class TeamsConstants:
    MESSAGE_TEXT = "message_text"
    CSR_INFO_JSON = "csr_info_json"
    TYPE = "type"
    TURN = "turn"
    QUEUE_MESSAGE = "One of our agents will be in touch with you shortly. You are currently in queue position: "
    MESSAGE = "message"
    TIME_OUT_TIME=300
    BANTER="banter"
    MIN_30=30


class UsermgmtApiUrls:
    API_URL_TO_FETCH_ROLES = "{usermgmt_base_url}/roles/application/{application_uuid}/customer/{customer_uuid}"
    API_URL_TO_FETCH_ONLINE_USERS_BY_CUSTOMER_AND_APPLICATION = "{usermgmt_base_url}/users/online/customer/{customer_uuid}/application/{application_uuid}"


class RequestMethodConstants:
    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"


class RoleConstants:
    ROLE_UUID = "role_uuid"
    ROLE_NAME = "role_name"


class DepartmentConstants:
    DEPARTMENT_ID = "department_id"
    DEPARTMENT_NAME = "department_name"


class UserConstants:
    USER_ID = "user_id"
    USER_NAME = "user_name"


class UsermgmtApiResponseConstants:
    MESSAGE = "message"
    RESULT = "result"
    STATUS_CODE = "statusCode"
    STATUS_CODE_DESCRIPTION = "statusCodeDescription"
    RESPONSE = "response"


class TagConstants:
    DEPARTMENT_TAG = ["Chatbot - Department"]
    AGENT_TAG = ["ChatBot - Agent"]
    INTENT_TAG = ["ChatBot - Intent"]
    HISTORY_TAG = ["ChatBot - History"]


class SwaggerHeadersConstants:
    CUSTOMER_UUID = 'customer-uuid'
    APPLICATION_UUID = 'application-uuid'
    USER_UUID = 'user-uuid'

    # Common Request Headers for Swagger
    CUSTOMER_UUID_HEADER = openapi.Parameter(name=CUSTOMER_UUID, in_=openapi.IN_HEADER, description="Customer UUID", type=openapi.TYPE_STRING)
    APPLICATION_UUID_HEADER = openapi.Parameter(name=APPLICATION_UUID, in_=openapi.IN_HEADER, description="Application UUID", type=openapi.TYPE_STRING)
    USER_UUID_HEADER = openapi.Parameter(name=USER_UUID, in_=openapi.IN_HEADER, description="User ID", type=openapi.TYPE_STRING)


class ApiRequestHeadersConstants:
    CUSTOMER_UUID = "customer-uuid"
    APPLICATION_UUID = "application-uuid"
    USER_UUID = "user-uuid"


class TestConstants:
    CUSTOMER_NAME = "testcustomer"
    EMAIL = "test@gmail.com"
    PURCHASED_PLAN = "purchased_plan"
    PRIMARY_CONTACT = "7669986594"
    SECONDARY_CONTACT = "7669986599"
    ADDRESS = "address"
    BILLING_ADDRESS = "billing_address"
    CUSTOMER_DETAILS_JSON = ""
    STATUS = True
    APPLICATION_NAME = "testapplication"
    APPLICATION_URL = "staging.testapplication.com"
    SCOPE_AND_ENDPOINT = "scope_end_point"
    DESCRIPTION = "description"
    ROLE_NAME = "testrolename"
    USER_NAME = "testuser_{user_id}"
    FIRST_NAME = "firstname"
    LAST_NAME = "lastname"
    AUTH_TYPE = "OAuth"
    USER_DETAILS_JSON = '{ "status":["abcd"] }'
    PASSWORD_HASH = "password hash"
    EMAIL_ID = "testuser@gmail.com_{user_id}"
    MOBILE_NUMBER = "user_mobile_number_{user_id}"

class FeedbackConstants:
    CHAT_CONVERSATION_UUID = "chat_conversation_uuid"
    SATISFACTION_LEVEL = "satisfaction_level"
    ADDITIONAL_COMMENTS = "additional_comments"

class RawSqlQueryConstants:
    QUERY_TO_FETCH_ONLINE_USERS_BY_EXCLUDE_CURRENT_USER = (
            """
                SELECT DISTINCT user_id, user_name 
                FROM (
                    SELECT 
                        user_id, 
                        username AS user_name, 
                        global_scope,
                        CASE 
                            WHEN jsonb_typeof(global_scope::jsonb->'status') = 'array' THEN jsonb_array_length(global_scope::jsonb->'status')
                            ELSE 0 
                        END AS status_array_length
                    FROM 
                        usermgmt.user_details_view
                    WHERE 
                        global_scope IS NOT NULL  
                        AND global_scope <> '{}'  
                        AND jsonb_typeof(global_scope::jsonb) = 'object'  
                        AND customer_id = %s  
                        AND application_id = %s  
                        AND user_id <> %s    
                        AND status = 'true'  
                ) AS user_status
                WHERE status_array_length > 0  
                ORDER BY user_id;
            """
        )




class TestEntityConstants:
    ENTITY_NAME = "testentity"
    ATTRIBUTE_NAME1 = "testattribute"
    ATTRIBUTE_VALUE1 = "testvalue"
    ATTRIBUTE_NAME2 = "testattribute2"
    ATTRIBUTE_VALUE2 = "testvalue2"
    ENTITY_ATTRIBUTE_DETAILS_JSON = AttributeDetailsJson(entity_name=ENTITY_NAME,
                                                         attributes={ATTRIBUTE_NAME1: [ATTRIBUTE_VALUE1],
                                                                     ATTRIBUTE_NAME2: [ATTRIBUTE_VALUE2]})

class TestKnowledgeSourceConstants:
    KNOWLEDGE_SOURCE_NAME = "test knowledge source.pdf"
    KNOWLEDGE_SOURCE_TYPE = KnowledgeSourceTypes.PDF.value
    KNOWLEDGE_SOURCE_PATH = "blob/name/pdf/test knowledge source.pdf"
    KNOWLEDGE_SOURCE_METADATA = {'file_name': KNOWLEDGE_SOURCE_NAME, 'page_count': 12}
    KNOWLEDGE_SOURCE_ATTRIBUTE_DETAILS_JSON = FileAttributeDetailsJson(entity_name=TestEntityConstants.ENTITY_NAME,
                                                                       attributes={TestEntityConstants.ATTRIBUTE_NAME1: TestEntityConstants.ATTRIBUTE_VALUE1})

class TestSmeConstants:
    TEST_QUESTION = "test question"
    TEST_ANSWER = "test answer"
    TEST_ATTACHMENTS = [ImageAttachment(url="blob/name.ext", type=KnowledgeSourceTypes.IMAGE.value, name=["test.png"], source="test_source").__dict__,
                        VideoAttachment(url="blob/name2.ext", type=KnowledgeSourceTypes.VIDEO.value, name=["test.mp4"],start_time="00:00:00").__dict__]

class SMEConstants:
    SME_VERIFIED = 'SME Verified'
    QA_VERIFIED = 'QA Verified'
    NOT_VERIFIED = 'Not Verified'

    QA_GENERATED = 'generated'
    QA_GENERATING = 'generating'
    QA_PENDING = 'pending'


class CsrConstants:
    CSR_ROOM_NAME = "csr_{csr_uuid}"
    IS_CSR = "is_csr"
    CSR_ID = "csr_id"
    CSR_INFO_JSON = "csr_info_json"
    CSR_UUID = "csr_uuid"
    CSR_ONGOING = "CSR_ONGOING"
    CSR_ASSIGN_TIME = "csr_assign_time"
    CSR_STATUS = "csr_status"
    CSR_ONQUEUE_CONVERSATIONS = "csr_onqueue_conversations"
    CSR_NAME = "csr_name"
    CSR_ONQUEUE_CONVERSATIONS_SET = "csr_onqueue_conversations:{csr_uuid}"
    CSR_ONGOING_CONVERSATIONS_SET = "csr_ongoing_conversations:{csr_uuid}"
    CSR_STATUS_FAILURE = "csr_status_failure:{csr_uuid}"
    INACTIVE = "Inactive"
    ACTIVE = "Active"
    ASSIGNED = "Assigned"
    CSR_PROFILE_PICTURE = "csr_profile_picture"
    CSR_TRANSFER_REASON = "csr_transfer_reason"

class MessageConstants:
    MESSAGE_DETAILS_JSON = "message_details_json"
    MESSAGE_TEXT = "message_text"
    LAST_MESSAGE = "latest_message"
    MESSAGE = "message"
    MESSAGE_UUID = "message_uuid"
    SOURCE = "source"
    MESSAGE_MARKER = "message_marker"
    DIMENSION_ACTION_JSON = "dimension_action_json"
    MEDIA_URL = "media_url"
    PARENT_MESSAGE_UUID = "parent_message_uuid"
    CREATED_AT = "created_at"
    LOGGED = "LOGGED"
    MESSAGE_TYPE = "message_type"
    DIMENSIONS = "dimensions"
    DIMENSION = "dimension"
    VALUE = "value"


class ConversationConstants:
    CONVERSATION = "conversation"
    CONVERSATION_PATTERN = "conversation:*"
    ONQUEUE_CONVERSATIONS = "onqueue_conversations"
    CONVERSATION_ROOM = "room_{chat_conversation_uuid}"
    CONVERSATION_KEY = "conversation:{chat_conversation_uuid}"
    CONVERSATION_STATUS = "conversation_status"
    CHAT_CONVERSATION_UUID = "chat_conversation_uuid"
    INSERTED_TS = "inserted_ts"


class UserDetailConstants:
    USER_DETAILS_JSON = "user_details_json"
    USER_PROFILE_PICTURE = 'user_profile_picture'
    USER_NAME = "user_name"
    USER_INFO = "user_info"
    USER_UUID = "user_uuid"
    USER = "user"

class SubDimensionConstants:
    SUB_DIMENSIONS = "sub_dimensions"
    SUB_DIMENSION = "sub_dimension"
    DIMENSION_SUB_INTENT = "sub_intent"

class TicketConstants:
    TICKET_UUID = "ticket_uuid"
    TICKET_KEY = "ticket:{ticket_uuid}"

class FileUploadNames(Enum):
    ATTACHMENTS_FILE_NAME = "{chat_uuid}/attachments/{attachment_name}"


class FileContentTypes(Enum):
    HTML = "html"
    TEXT = "txt"
    JSON = "json"


