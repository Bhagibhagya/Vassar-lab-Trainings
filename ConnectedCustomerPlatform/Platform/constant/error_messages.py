class ErrorMessages:
    INVALID_DATA = "Invalid Data"
    TRANSACTION_FAILED = "Error occurred while updating the status. Check data and try again"
    VALID_JSON_OBJECT = 'This field must be a valid JSON object.'

    CUSTOMER_ID_NOT_NULL = "customer_uuid should not be NULL"
    USER_ID_NOT_NULL = "user_id should not be NULL"
    DIMENSION_NAMES_SHOULD_UNIQUE = "Please ensure that the names provided are distinct"
    INVALID_IS_READ_VALUE = "Invalid is read value"
    TICKET_UUID_NULL_ERROR = "Ticket uuid should not be NULL"
    TICKET_UUID_NOT_FOUND = "Ticket uuid not found"
    PRIMARY_TICKET_UUID_NOT_NULL = "Primary Ticket uuid should not be NULL"
    SECONDARY_TICKET_UUID_NOT_NULL = "Primary Ticket uuid should not be NULL"
    FAILED_TO_MERGE_TICKETS = "Failed to merge the tickets"
    FAILED_TO_GET_CONVERSATION_INFORMATION = "Failed to get conversation information"


    NOT_VALID_UUID = "not a valid UUID"
    APPLICATION_ID_NOT_NULL = "application_uuid should not be NULL"
    DIMENSION_TYPE_NAME_NOT_NULL = "dimension_type_name should not be NULL"
    DIMENSION_TYPE_UUID_NOT_NULL = "dimension_type_uuid should not be NULL"
    MAPPING_UUID_NOT_NULL = "mapping_uuid should not be NULL"
    DIMENSION_TYPE_EXISTS = "Dimension type already exists"
    DIMENSION_TYPE_UPDATE_FAILED = "Failed to updated dimension type"
    DIMENSION_TYPE_CREATE_FAILED = "Failed to create dimension type"
    DIMENSION_EXISTS = "Dimension already exists"
    DIMENSION_NOT_FOUND = "Dimension not found"
    DIMENSION_TYPE_NOT_FOUND = "Dimension type not found"
    DIMENSION_ADD_FAILED = "Failed to add dimension"
    DIMENSION_UPDATE_FAILED = "Failed to update dimension"
    DIMENSION_HAS_DEPENDENTS = "Dimension cannot be updated or deleted because it has mapped sub-dimension values."
    SCOPE_UPDATE_FAILED = "Failed to update scope"
    ADD_UTTERANCE_FAILED = "Failed to add utterance"
    UPDATE_UTTERANCE_FAILED = "Failed to update utterance"
    COLLECTION_NOT_EXIST = 'Collection does not exist'
    GEOGRAPHY_COUNTRY_SHOULD_BE_ADDED = "Please activate Geography country prior to enabling Geography state."
    STATUS_MISSING = "status key missing in payload"
    NOT_FOUND = "not found"
    CUSTOMER_CLIENT_ID_NOT_NULL = "Require customer_client_uuid query_param"
    CUSTOMER_NOT_FOUND = "Customer not found"
    APPLICATION_NOT_FOUND = "Application not found"

    DIMENSION_NAME_NOT_NULL = "dimension_name should not be NULL"
    DIMENSION_UUID_NOT_NULL = "dimension_uuid should not be NULL"
    PROMPT_TEMPLATE_NAME_NOT_NULL = "prompt template name should not be NULL"
    PROMPT_TEMPLATE_UUID_NOT_NULL = "prompt template uuid should not be NULL"
    PROMPT_TEMPLATE_EXISTS = "Prompt template already exists"
    PROMPT_TEMPLATE_NOT_FOUND = "Prompt template not found"
    PROMPT_NAME_NOT_NULL = "prompt name should not be NULL"
    PROMPT_CATEGORY_NAME_NOT_NULL = "prompt category name should not be NULL"
    PROMPT_UUID_NOT_NULL = "prompt uuid should not be NULL"
    PROMPT_EXISTS = "Prompt already exists"
    PROMPT_NOT_FOUND = "Prompt not found"
    PROMPT_CATEGORY_NOT_FOUND = "Prompt category not found"
    FAILED_TO_CREATE_PROMPT = "Failed to create prompt"
    FAILED_TO_CREATE_PROMPT_TEMPLATE = "Failed to create prompt_template"
    PROMPT_TEMPLATE_CANNOT_BE_DELETED = "This prompt template cannot be deleted because it is currently associated with one or more prompts"

    TOOL_DESCRIPTION_NOT_NULL = "tool description should not be NULL"
    TOOL_NAME_NOT_NULL = "tool name should not be NULL"
    TOOL_CATEGORY_NOT_NULL="tool category should not be null"
    TOOL_UUID_NOT_NULL="tool uuid should not be null"

    # Email Server
    ADD_EMAIL_SERVER_FAILED = "Failed to add email server"
    UPDATE_EMAIL_SERVER_FAILED = "Failed to update email server"
    EMAIL_SERVER_UUID_NOT_NULL = "email server uuid should not be NULL"
    EMAIL_SERVER_EXISTS = "Email Server already exists with this configuration"
    SERVER_TYPE_NOT_NULL = "server_type query parameter is required"
    EMAIL_SERVER_NOT_FOUND = "Email server not found"
    USER_EMAIL_SETTINGS_NOT_FOUND = "user email settings not found"
    EMAIL_EXISTS = "Email already exists"
    PRIMARY_EMAIL_EXISTS = "Primary Email already exists"
    ADD_EMAIL_FAILED = "Failed to add user email settings"
    UPDATE_EMAIL_FAILED = "Failed to update user email settings"
    INDIVIDUAL_EMAIL_ASSOCIATED_WITH_GROUP = 'Individual email cannot be edited or deleted when it is associated with a group email.'
    EMAIL_PROVIDER_MISMATCH = 'Please provide an email address matching the chosen provider'
    INVALID_EMAIL_DOMAIN = 'Unable to verify the domain name. Please check the domain and try again'
    INVALID_CREDENTIALS_FOR_IMAP = 'Invalid credentials. Please check your email and password and try again.'
    LOGIN_FAILED_FOR_IMAP = 'We couldn\'t log you in. Please check your email and password and try again.'
    DELETE_EMAIL_SERVER_FAILED = "Failed to delete email server"

    # Email Extraction Template
    CUSTOMER_CLIENT_TIER_UUID_NOT_NULL = "customer tier uuid should not be NULL"
    TEMPLATE_NAME_EXISTS = "Template name already exists"
    CUSTOMER_EXISTS = "Customer already exists"
    CUSTOMER_USER_EXISTS = "Customer user already exists"
    CUSTOMER_EMAIL_EXISTS="Customer email already exists"
    CUSTOMER_USER_EMAIL_EXISTS = "Customer user email already exists"
    CUSTOMER_USER_NOT_FOUND = "Customer user not found"
    CUSTOMER_NAME_EXISTS = "Customer name already exists"
    CUSTOMER_DOMAIN_NAME_EXISTS = "Customer domain name already exists"
    FAILED_TO_CREATE_CUSTOMER_USER = "Failed to add customer user"

    #CUSTOMER_CLIENT
    ADD_CUSTOMER_CLIENT_FAILED = "Add customer client failed"
    EDIT_CUSTOMER_CLIENT_FAILED = "Edit customer client failed"
    CUSTOMER_CLIENT_NOT_FOUND = "Customer client not found"

    CUSTOMER_CLIENT_TIER_MAPPING_EXISTS = "Customer client tier mapping already exists"
    ADD_CUSTOMER_CLIENT_TIER_FAILED = "Add customer client tier failed"
    #CHAT CONFIGURATION TEMPLATE
    CHAT_CONFIGURATION_NAME_NOT_NULL = "chat_configuration_name should not be NULL"
    CHAT_CONFIGURATION_UUID_NOT_NULL = "chat_configuration_uuid should not be NULL"
    SAVE_CONFIGURATION_BEFORE_PUBLISHING = "Save the chat configuration before publishing"
    CHAT_CONFIGURATION_NOT_FOUND = "chat configuration not found"
    CHAT_CONFIGURATION_TYPE_NOT_NULL = "chat_configuration_type should not be NULL"
    APPLICATION_UUID_NOT_NULL = "application_uuid should not be NULL"
    CUSTOMER_UUID_NOT_NULL = "customer_uuid should not be NULL"

    LLM_CONFIGURATION_EXISTS = "LLM Configuration already exists"
    USER_ID_NOT_NULL="user_uuid should not be NULL"
    DATABASE_ERROR = "Database error occurred"

    LLM_CONFIGURATION_NOT_FOUND = "LLM Configuration not found"
    LLM_CONFIGURATION_ID_NOT_NULL="LLM Configuration uuid should not be null"
    GENERIC_ERROR="Generic error"
    INVALID_LLM_CONFIGURATION_DETAILS="Invalid LLM configuration detail json"
    LLM_CONFIGURATION_CUSTOMER_MAPPING_NOT_FOUND = "LLM Configuration customer mapping not found"
    # Azure
    ERROR_KEY_VAULT_ACCESS = "Unable to access Azure Key Vault"

    INTENT_SHOULD_NOT_NULL = "Intent should not be null"
    FAILURE_IN_UPDATING_UTTERANCES = "Failure in updating of utterances"
    ID_SHOULD_NOT_NULL = "Id should not be null"

    PAGE_NUMBER_INVALID = "page number invalid"
    PAGE_NUMBER_POSITIVE = "page number should be positive"
    TOTAL_ENTRY_PER_PAGE_POSITIVE = "total entry per page should be positive"
    UTTERANCES_DELETION_FAILED = "Utterances Deletion failed"



    #whatsapp configuration
    TEMPLATE_NAME_INVALID = 'Invalid template name. It must be a non-empty string with a maximum length of 512 characters.'
    PENDING_TEMPLATE_EDITING_INVALID = 'cannot edit the template with pending status'
    TEMPLATE_UUID_NOT_NULL = 'Template UUID is required'
    MISSING_PARAMETERS = "Missing one of these required parameters app_id,file_name,file_length,file_type,access_token"
    CANNOT_EDIT_TEMPLATE = "cannot able to edit template"
    CANNOT_CREATE_TEMPLATE = "cannot able to create template"
    INVALID_ACCESS_TOKEN = "Invalid API key."
    INVALID_BUSINESS_ID = "Invalid Business ID Or Restricted for doing {operation}"
    INVALID_APPLICATION_ID = "Invalid Application ID"
    INVALID_PHONE_NUMBER_ID = "Invalid Phone number ID"
    CANNOT_ABLE_TO_GET_BUSINESS_INFO = "error in getting business information"
    INVALID_JSON = "invalid json data"
    CANNOT_GET_FILE_HANDLE = 'Failed to get file handle'
    CANNOT_UPLOAD_SESSION = "Cannot upload image"
    UNABLE_TO_FETCH_BUSINESS_PROFILE = 'Failed to fetch WhatsApp Business Profile details'
    UNABLE_TO_UPDATE_PROFILE = 'Unable to update profile picture'
    ACCESS_TOKEN_NOT_NULL = "api key should not be null"
    PHONE_NUMBER_ID_NOT_NULL = "phone number id should not be null"
    BUSINESS_ID_NOT_NULL = "business id should not be null"
    PERMISSION_ERROR = "Missing Permissions"
    INVALID_BUSINESS_ID_OR_TEMPLATE_NAME = "Invalid Business Id or Template name"
    INVALID_FILE_TYPE = "File should be png,jpg,pdf,jpeg"
    PROJECT_NAME_NOT_NULL = "Project Name should not be NULL"
    ORGANIZATION_UUID_NOT_NULL = "Organization UUID should not be NULL"
    CHANNEL_TYPE_UUID_NOT_NULL = "Channel_type UUID should not be NULL"

    ATTACHMENT_CANNOT_BE_EMPTY = "Attachment is empty or contains 0 bytes of data."
    CONTAINER_NAME_CANNOT_BE_EMPTY = "Container Name should not be NULL"
    BLOB_NAME_CANNOT_BE_EMPTY = "Blob Name should not be NULL"

    TEMPLATE_NAME_NOT_NULL = "Template name should not be NULL"
    WHATSAPP_BUSINESS_ACCOUNT_ID_NOT_NULL = "WhatsApp Business Account ID should not be NULL"
    UNABLE_TO_DELETE_TEMPLATE = "Unable to delete the template."

    TEMPLATE_NOT_FOUND = "Template name not found"
    MORE_THAN_ONE_TEMPLATE_CANNOT_BE_ACTIVE = "More than one template cannot be active"
    ONE_TEMPLATE_SHOULD_BE_ACTIVE = "One template should be active"
    INVALID_TEMPLATE_UUID = "Invalid template UUID"
    IMAGE_TOO_SMALL = "Image is too small"
    IMAGE_TOO_LARGE = "Image is too large"
    INVALID_IMAGE_FORMAT = "Image format is invalid"
    TEMPLATE_NAME_ALREADY_EXISTS = "Template with name '{template_name}' already exists."
    TEMPLATE_DELETED_SUCCESSFULLY = "Template deleted successfully."
    INVALID_MESSAGE_TEMPLATE = "The message template name can only have lower-case letters and underscores."
    CANNOT_GET_TEMPLATE = "Error fetching chat configurations"
    NONE_TYPE_ACCESS = "Attempted to access an attribute of a None type."
    UNEXPECTED_ERROR_OCCURED = "unexpected error occured."
    CHAT_CONFIGURATION_MAPPING_NOT_FOUND = "Chat configuration mapping was not found"
    MISSING_LANDING_PAGE_DATA = "Missing or empty 'landing_page_configuration' in JSON data."
    MISSING_INTENT_PAGE_DATA = "Missing or empty 'intent_page_configuration' in JSON data."
    CANNOT_UPDATE_ACTIVATION_STATUS = "Cannot able to update activation status"
    MAXIMUM_TEMPLATE_LIMIT_REACHED = "Maximum template limit reached"
    CHAT_CONFIGURATION_NAME_NOT_DUPLICATED = "Chat configuration name should not be duplicated"
    ERROR_IN_DELETING_UTTERANCE = "Error in deleting utterance"
    NOT_VALID_UUID = "not a valid UUID"
    ERROR_WHILE_ADDING_TRAINING_PHRASES = "Error while adding training phrases"
    LIST_LENGTHS_MISMATCH = "The lengths of the lists are not equal!"
    FAILED_TO_ADD_INTO_COLLECTION = "Error occurred while adding training phrases into collection"
    IDS_LIST_SHOULD_NOT_BE_EMPTY = "IDs List should not be empty"
    CHILD_DIMENSION_NOT_PROVIDED="Child Dimension name is not provided"

    # Outlook test connection error messages
    INVALID_SERVER_DETAILS = "Invalid server details provided."
    INTERNAL_ERROR_TEST_CONNECTION = "Cannot complete test connection"
    UNAUTHORISED_TEST_CONNECTION = "Unauthorized. Check your Tenant ID, Client ID, or Client Secret."
    PERMISSIONS_NOT_GRANTED = "Please grant API permissions to access user profile."
    USER_EMAIL_NOT_FOUND = "Resource {user_email} does not exist"
    CONNECTION_FAILED_WITH_EXCEPTION_MESSAGE = "Connection failed.{e}"
    MISSING_PERMISSIONS = "Missing permissions: {permissions}"