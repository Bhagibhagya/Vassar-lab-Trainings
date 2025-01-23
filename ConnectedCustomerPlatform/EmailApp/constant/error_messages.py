class ErrorMessages:
    # customer
    CUSTOMER_NOT_FOUND = "Customer not found."
    CUSTOMER_ID_NOT_NULL = "Customer_uuid should not be NULL"
    CUSTOMER_UUID_NOT_GIVEN = "Expecting UUID of a customer"
    APPLICATION_UUID_NOT_GIVEN = "Expecting UUID of a application"
    USER_UUID_NOT_GIVEN = "Expecting UUID of a user"

    # customer_client
    CUSTOMER_CLIENT_NOT_FOUND = "Customer Client not found."
    CUSTOMER_CLIENT_ID_NOT_NULL = "Customer_client_uuid should not be NULL"
    CUSTOMER_CLIENT_TIER_UUID_NOT_FOUND ="Customer client tier uuid not found"

    # dimensions
    DIMENSION_ID_NOT_FOUND = "Dimension uuid to find intent is not found"
    DIMENSION_UUID_NOT_FOUND = "Dimension uuid not found"
    DIMENSION_NOT_FOUND = "Dimension not found"

    # emails
    EMAIL_UUID_NULL_ERROR = "email uuid cannot be NULL"
    EMAIL_NOT_FOUND = "Email is not found"
    PARENT_EMAIL_NOT_FOUND = "Parent email not found"

    FROM_EMAIL_ID_NULL_ERROR = "from email uid cannot be NULL"
    EMAIL_INFO_NOT_FOUND = "Email info detail is not found"
    FILE_URL_NULL_ERROR = "File url cannot be null"
    FILES_URL_LIST_NULL_ERROR = "Files url list cannot be null"


    # email_conversations
    EMAIL_CONVERSATION_NOT_FOUND = "Email conversation not found."
    IN_REPLY_TO_CONVERSATION_NOT_FOUND = "In-replay-to conversation not found."
    EMAIL_CONVERSATION_ID_NOT_NULL = "Email conversation uuid cannot be NULL"
    PARENT_EMAIL_CONVERSATION_ID_NOT_FOUND = "Parent email conversation not found."
    EMAIL_SUBJECT_NOT_NULL = "Email Subject cannot be NULL"
    EMAIL_UUID_LIST_ERROR = "Email UUIDS should be list of UUIDS"
    TICKET_UUID_NOT_NULL = "Ticket uuid cannot be NULL"


    DRAFT_MAIL_NOT_FOUND = "Draft mail not found"
    CONVERSATION_UUID_NOT_NULL="Email conversation uuid not found"
    DETAILS_EXTRACTED_NULL_ERROR="Details extracted json should not be null"
    LATEST_CONVERSATION_NOT_FOUND="Latest received conversation not found"
    EXTRACTED_ORDER_DETAILS_NOT_FOUND = "Extracted order details not found"
    PARENT_EMAIL_ID_NOT_FOUND = "Parent email not found"

    # Dates
    START_DATE_NULL_ERROR = "Start Date cannot be NULL"
    END_DATE_NULL_ERROR = "End Date cannot be NULL"
    INVALID_DATE_FORMAT = "Invalid {0} format. Please provide dates in {1}"
    START_DATE_GREATER_THAN_END_DATE = "Start date should not be greater than end date"

    INVALID_EMAIL_ADDRESS = "Invalid email address."
    INVALID_REQUEST_PARAMETERS = "Invalid request parameters."
    EMAIL_ACTION_FLOW_STATUS_NOT_NULL = "Email Action Flow status cannot be NULL"

    # SMTP
    SMTP_SERVER_DETAILS_NOT_FOUND = "SMTP server details not found for the customer"
    SMTP_AUTHENTICATION_FAILED = "SMTP Authentication Failed"

    EMAIL_ID_NOT_FOUND_IN_EMAIL_SETTINGS = "email_id not found in email_settings"
    EMAIL_SENT_FAILED = "Error while Sending Email"
    PRIMARY_EMAIL_SETTING_NOT_FOUND="Primary email setting not found"
    DRAFT_UPDATE_FAILED = "Failed to update the draft"
    ATTACHMENTS_NOT_REMOVED = "Failed to remove attachments"
    USER_EMAIL_SETTING_NOT_FOUND = "User email setting not found"
    UNABLE_TO_FETCH_EMAIL_DETAILS = "Unable to fetch email details"

    # Pages
    PAGE_NUMBER_INVALID = "Requested page '{page_number}' is invalid."
    PAGE_EMPTY = "Requested page is empty"
    PAGE_NUMBER_POSITIVE = "page number should be positive"
    TOTAL_ENTRY_PER_PAGE_POSITIVE = "total entry per page should be positive"

    DATA_SHOULD_BE_DICT = "Request data should be a dictionary"
    MISSING_OR_EMPTY_VALUE = "Missing or empty value for '{field}' field"

    BAD_REQUEST = "Bad Request"
    INVALID_HTTP_METHOD = "Invalid HTTP method"
    ERROR_FROM_USERMGMT_API = "Error from user management api"
    NONE_TYPE_ACCESS = "An attribute or item on a NoneType object was accessed."
    IO_ERROR = "An IO error occurred."
    DATABASE_ERROR = "Database error occurred"
    INTERNAL_SERVER_ERROR = "Internal server error"
    AUTHENTICATION_FAILED = "Authentication failed: Invalid credentials for IMAP Server"

    # Azure Service
    CONTAINER_NAME_NOT_FOUND = "Container name not found!"
    PRESIGNED_URL_NOT_FOUND = "Error fetching data from the Presigned URL"
    #user management
    USER_NOT_FOUND_IN_USERMGMT="User not found in user management"
    ERROR_IN_GENERATING_UTTERANCES = 'Failed to generate training phrases. Please try again'


    VERIFICATION_FAILED_RETRY_AGAIN="Verification failed retry again"
    STEP_DETAILS_NOT_FOUND = "Step details not found"
    NEXT_STEP_INFO_NOT_FOUND = "next_step_info not found"
    OUTPUT_DATA_NOT_FOUND = "output data not found in the step"
    STEP_UUID_NOT_FOUND = "Step uuid not found"
    EMAIL_PROCESS_DETAILS_NOT_FOUND = "email process details not found"

    APPLICATION_ID_NOT_NULL="Application uuid should not be null"
    USER_ID_NOT_NULL="User uuid should not be null"
    EXCEL_FILE_NOT_FOUND="No excel file provided"
    RESPONSE_CONFIG_ID_NOT_NULL="Response config uuid should not be null"
    IS_DEFAULT_IS_NONE="IS_DEFAULT param for identifying admin is null"
    IS_DEFAULT_SHOULD_BE_BOOLEAN="is_default should be a boolean value"
    PROVIDED_UTTERANCE_UUID_IS_NOT_UUID="Provided utterance_uuid value is not uuid"
    PROVIDED_USER_UUID_IS_NOT_UUID="Provided user_uuid value is not uuid"
    PROVIDED_INTENT_UUID_IS_NOT_UUID="Provided intent_uuid value is not uuid"


    PROVIDED_CUSTOMER_UUID_IS_NOT_UUID="Provided customer_uuid value is not uuid"
    PROVIDED_APPLICATION_UUID_IS_NOT_UUID="Provided application_uuid value is not uuid"
    ERROR_IN_DELETING_UTTERANCE = "Failed to delete training phrase. Please try again"
    ERROR_IN_FETCHING_UTTERANCES = "Error in fetching utterances"
    EXCEL_SHEET_IS_EMPTY="The Excel sheet is empty. Please add example responses"
    RESPONSE_I_IS_REQUIRED="Response_I is required"
    MISSING_REQUIRED_COLUMN="Missing required column: {}"
    ERROR_PARSING_EXCEL="Error parsing the Excel file. Cannot parse the response row"
    INVALID_ENDPOINT="INVALID_ENDPOINT"
    ATTACHMENT_ID_NOT_FOUND = "attachment_id should not be null"

class PersonalizationErrorMessages:
    ERROR_DOWNLOADING_TEMPLATE = "An error occurred while downloading template: {}"
    FILENAME_NOT_PRESENT_FOR_FILE="filename is not present for {}"
    ERROR_CREATING_PRESIGNED_URL="Error creating presigned url {}"
    RESPONSE_CONFIG_NOT_PRESENT="The specified response configuration is not present"

class AzureBlobErrorMessages:
    ERROR_MSG_PRESIGNED_URL = "Error creating presigned URL: {}"
    INVALID_FILE_MSG = "Filename not present in the file URL: {}"
    BLOB_URL_NULL_ERROR = "Blob URL cannot be NULL"
