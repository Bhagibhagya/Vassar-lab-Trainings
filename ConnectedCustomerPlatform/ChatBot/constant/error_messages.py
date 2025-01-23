class ErrorMessages:
    INVALID_DATA = "Invalid Data"
    CONVERSATION_UUID_NOT_NULL = "Conversation UUID should not be NULL"
    CSR_ID_NOT_NULL = "CSR ID should not be NULL"
    CSE_STATUS_NOT_NULL = "CSR Status should not be NULL"
    CONVERSATION_UUID_NOT_FOUND = "Conversation UUID not found"
    CSR_ID_NOT_FOUND = "CSR ID not found"
    INVALID_INPUT = "Invalid input"
    INVALID_CSR_STATUS = "Invalid csr status"
    TICKET_UUID_NOT_NULL = "Ticket UUID should not be NULL"
    BAD_REQUEST = "Bad Request"
    PAGE_NUMBER_INVALID = "Requested page '{page_number}' is invalid."

    FILES_SIZE_TOO_LARGE = "Total files size too large"
    KNOWLEDGE_SOURCE_NOT_FOUND = "Knowledge source does not exist"
    FILE_RESOLVE_STATUS_ERROR = "File can only be resolved if status is 'Under Review'. Please review the file status and try again."
    KNOWLEDGE_SOURCE_ALREADY_EXISTS = "Knowledge source already exists"
    UPDATE_KNOWLEDGE_SOURCE_ENTITY_SUCCESS = "Knowledge source entity updated successfully"
    KNOWLEDGE_SOURCE_UUID_NULL_ERROR = "Knowledge source uuid cannot be NULL"
    KNOWLEDGE_SOURCE_UUID_NOT_NULL = "knowledge_source_uuid cannot be empty or null"
    PAGE_NUMBER_NOT_NULL = "page number cannot be empty or null"
    PAGES_LIST_NOT_EMPTY = "pages field cannot be empty list"
    FILE_RESOLVE_ERROR = "Solve the errors to resolve the file."

    SCOPE_TYPE_NOT_FOUND = "Scope type does not exists"
    SCOPE_NAME_NOT_FOUND = "Scope name does not exists"

    DUPLICATE_ENTITY = "Product Type with the name already exists"

    ENTITY_NOT_FOUND = "Product Type does not exist"
    ENTITY_DELETED = "Product Type deleted successfully"
    UNABLE_TO_DELETE_ENTITY = "Unable to delete product type"
    UNABLE_TO_UPDATE_ENTITY = "Unable to update product type"
    CANNOT_DELETE_ASSIGNED_ENTITY_ATTRIBUTES = "Assign product type attribute: {} deleted or renamed"
    CANNOT_DELETE_ASSIGNED_ENTITY_ATTRIBUTE_VALUES = "Assign product type attribute: {}, value: {} deleted"

    UNSUPPORTED_FILE = "Unsupported file format"
    ENTITY_NOT_ASSIGNED = "Product Type not assigned to file"
    CANNOT_ADD_DEFAULT_ENTITY = "Product Type with default name cannot be added"
    CANNOT_DELETE_DEFAULT_ENTITY = "Default product type cannot be deleted"
    ENTITY_NAME_CANNOT_BE_DEFAULT = "Product Type cannot be default"
    CANNOT_UNASSIGN_DEFAULT_ENTITY = "Default product type cannot be assigned"
    UNABLE_TO_UNASSIGN_ENTITY = "Unable to unassign product type and file"
    KNOWLEDGE_SOURCE_ENTITY_UPDATING_FAILED = "Cannot assign or unassign product type to file."

    DUPLICATE_COLUMNS = "column names should be unique"

    INVALID_WEB_URL = "Not a valid web url"
    DUPLICATE_WEB_URL = "web url already exists"
    WEB_URL_NOT_REACHABLE = "web url not reachable"

    QUESTION_NOT_FOUND = "question not found"
    ANSWER_NOT_FOUND = "Answer not found"
    NOT_A_TEXT_BLOCK = "Not a text block"

    CANNOT_REGENERATE = "Cannot regenerate"
    INVALID_SESSION = "Invalid session id"

    CANNOT_GENERATE_QA = "Q/A generation in progress or already completed"

    CUSTOMER_ID_NOT_NULL = "customer_uuid should not be NULL"

    APPLICATION_ID_NOT_NULL = "application_uuid should not be NULL"

    USERMGMT_ERROR_MESSAGE = "There is issue with user management"

    ROLE_ID_NOT_NULL = "role_id should not be NULL"

    USER_ID_NOT_NULL="user_uuid should not be NULL"

    UNSUPPORTED_FORMAT = 'Unsupported Format'
    INVALID_IMAGE = 'Invalid image type'   
    INVALID_IMAGE_SIZE = 'File size too large. Please upload an image smaller than 5 MB.'   
    FAILED_TO_GET_IMAGE = 'Failed to get image' 
    

    LISTENER_CANCEL_FAILED = "Failed to cancel listener task"
    INACTIVE_USER_CLEANUP_FAILED = "Failed to clean up inactive user"
    WEBSOCKET_CONNECTION_FAILED = "Failed to connect to WebSocket server"
    WEBSOCKET_CONNECTION_CLOSE_FAILED = "Failed to close WebSocket connection"
    CONNECTION_NONE = "Attempted to close a WebSocket connection that is None"
    ACTIVITY_PROCESSING_FAILED = "Failed to process activity"
    MESSAGE_ACTIVITY_ERROR = "Error handling message activity"
    DATABASE_FETCH_FAILED = "Failed to fetch data from the database"
    BOT_ID_NOT_FOUND = "Bot ID not found in the chat configuration"
    CONNECTION_NOT_ESTABLISHED = "WebSocket connection is not established"
    JSON_DECODE_ERROR = "Invalid JSON format in message"
    MESSAGE_SEND_FAILED = "Error sending message over WebSocket"
    CONNECTION_CLOSED = "WebSocket connection closed unexpectedly"
    LISTENING_ERROR = "Error in WebSocket listening"
    ENV_VARIABLES_NOT_SET = "Required environment variables for WebSocket are not set."
    MESSAGE_SENDING_ERROR = "Error sending message over WebSocket."
    GENERIC_ERROR_MESSAGE = "An unexpected error occurred."
    CONVERSATION_DATA_NOT_FOUND = "Conversation data not found for UUID: {uuid}"
    RETRIEVAL_ERROR = "Error retrieving dimension action JSON"
    RESPONSE_PROCESSING_ERROR = "Error processing the response in on_message_activity"
    DIMENSION_EXTRACTION_ERROR = "Error extracting dimension information from response"
    MESSAGE_TEXT_EXTRACTION_ERROR = "Error extracting message text from response"
    SPECIFICATION_EXTRACTION_ERROR = "Error extracting specifications from response"
    SUGGESTION_EXTRACTION_ERROR = "Error extracting suggestions from specifications"
    MAX_REGENERATE_MESSAGE = "Message {answer_id} has been regenerated more than {regenerate_level} times. Maximum allowed is {max_regenerate_count}."
    MESSAGE_ID_NOT_FOUND = "Message_id not found"
    TEMPLATE_NOT_FOUND = "Template not found"
    CANNOT_ABLE_TO_STORE_DATA = "Error in storing data"

    #whatsapp_configuration
    CONFIGURATION_NOT_EXIST = "ChatConfiguration does not exist with that business id"
    CANNOT_PROCESS_TEMPLATE = "Error processing template status update: {reason}"

    REQUEST_METHOD_NOT_PROVIDED = "Request method not provided."
    API_URL_NOT_PROVIDED = "API URL not provided."

    GENERIC_ERROR = "Generic error"
    MISSING_KEYS_WHILE_API_URL_BUILD_ERROR = "Missing required key in URL template"
    PYDANTIC_HEADERS_VALIDATION_ERROR = "Validation error occurred while parsing headers"

    DATABASE_OPERATION_FAILED = "Database operation failed"
    INTEGRITY_ERROR = "Integrity error: a violation occurred."
    OPERATIONAL_ERROR = "Operational error: an issue occurred while accessing the database."
    DATA_ERROR = "Data error: invalid data provided."
    PROGRAMMING_ERROR = "Programming error: a SQL syntax error occurred."
    TRANSACTION_MANAGEMENT_ERROR = "Transaction management error: issues managing transactions."
    PAGE_EMPTY = "Requested page is empty"
    IO_ERROR = "An IO error occurred."
    DATABASE_ERROR = "Database error occurred"
    NOT_VALID_UUID = "not a valid UUID"
    CHAT_CONVERSATION_NOT_FOUND = "Chat conversation not found"
    FAILED_T0_GENERATE_IMAGE = "Failed to generate CAPTCHA image or text"
    BEYOND_SCOPE = "User is not in scope"
