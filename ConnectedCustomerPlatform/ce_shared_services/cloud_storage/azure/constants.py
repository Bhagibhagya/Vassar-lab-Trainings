class ErrorMessages:
    MISSING_AZURE_CONNECTION_STRING = "Azure connection string is missing."
    MISSING_AZURE_CONTAINER = "Azure container name is missing."
    CONTAINER_NOT_FOUND = "Container '{container}' not found."
    FILE_REQUIRED = "'file_path' must be provided."
    DATA_REQUIRED = "'data' must be provided"
    INVALID_FILE_PATH = "Invalid file path provided: {file_path}"
    MISSING_FILE_NAME = "File name must be provided when uploading binary data."
    BLOB_ALREADY_EXISTS = "Blob already exists and overwrite is not allowed."
    CONTAINER_OR_BLOB_NOT_FOUND = "Container or blob not found."
    AUTHENTICATION_ERROR = "Authentication error occurred while accessing Azure Storage."
    UPLOAD_FAILED = "Failed to upload blob."
    UPDATE_FAILED = "Failed to update blob."
    DOWNLOAD_FAILED = "Failed to download blob."
    BLOB_NOT_FOUND = "Blob not found."
    BLOB_MODIFIED_BY_ANOTHER = "Blob modified by another request."
    SAS_TOKEN_GENERATION_FAILED = "Failed to generate SAS token."
    PRESIGNED_URL_FAILED = "Failed to generate presigned URL."
    INVALID_BLOB_URL = "Invalid Blob URL format."
    INTERNAL_SERVER_ERROR = "Internal Server Error occurred :{error}"
    NO_WRITE_PERMISSION = "No write permission for the specified folder: {folder}"
    NO_READ_PERMISSION = "No read permission for the specified folder: {file_path}"
    INVALID_DESTINATION_FOLDER = "Invalid destination folder : {folder_path}"
    INVALID_BUFFER = "Invalid Buffer"
    INVALID_BLOB_NAME = "Invalid Blob name"
    INVALID_FILE_NAME = "Invalid File name"
    INVALID_AZURE_CONFIGURATION = "Invalid Configuration"
    INVALID_CUSTOMER_UUID = "INVALID CUSTOMER UUID"
    INVALID_APPLICATION_UUID = "INVALID APPLICATION UUID"
    INVALID_CHANNEL_TYPE = "INVALID_CHANNEL_TYPE"
    FIELD_MANDATORY_CANNOT_BE_NONE = "{} is a mandatory parameter and cannot be empty or None."
    PREPEND_BLOB_DOES_NOT_EXIST = "Prepend blob path does not exist: {prepend_blob_name}"
    INVALID_RETRY_PARAM="Invalid Retry Param"
    INVALID_MAX_CONCURRENCY_PARAM="Invalid max_concurrency param"
class BlobUrl:
    BLOB_URL = r"https://[^/]+/([^/]+)/(.+)"

class ReturnTypes:
    BLOB = "blob"
    URL = "url"

class FileTypes:
    APPLICATION_OCTET_STREAM = 'application/octet-stream'

class DateTypes:
    YEAR='%Y'
    MONTH='%B'
    DAY='%d'

BLOB_PATTERN="{customer_uuid}/{application_uuid}/{channel_type}/{year}/{month}/{day}/{file_name}"