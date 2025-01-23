import logging
import mimetypes
import os
import re
from inspect import signature

import backoff
from typing import Optional
from datetime import datetime
from urllib.parse import unquote

from ce_shared_services.cloud_storage.azure.constants import ErrorMessages, BlobUrl, FileTypes
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError, \
    ClientAuthenticationError, AzureError, HttpResponseError, ServiceRequestError, ServiceResponseError, \
    StreamConsumedError, StreamClosedError, IncompleteReadError, ServiceRequestTimeoutError, ServiceResponseTimeoutError

from ce_shared_services.cloud_storage.azure.constants import DateTypes

from ce_shared_services.cloud_storage.azure.constants import BLOB_PATTERN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_read_permission(file_path: str):
    """Check if the folder is readable."""
    logger.info("In Utils :: check_read_permission")
    if not file_path:
        raise ValueError(ErrorMessages.INVALID_FILE_NAME)

    if not os.access(file_path, os.R_OK):
        logger.error(ErrorMessages.NO_READ_PERMISSION.format(file_path=file_path))
        raise PermissionError(ErrorMessages.NO_READ_PERMISSION.format(file_path=file_path))

def validate_folder_path(folder: str):
    """Check if the folder is writable."""
    logger.info("In Utils :: validate_folder_path")
    if not folder:
        logger.error(ErrorMessages.INVALID_DESTINATION_FOLDER.format(folder_path=folder))
        raise ValueError(ErrorMessages.INVALID_DESTINATION_FOLDER.format(folder_path=folder))
    if not os.path.isdir(folder):
        logger.error(ErrorMessages.INVALID_DESTINATION_FOLDER.format(folder_path=folder))
        raise ValueError(ErrorMessages.INVALID_DESTINATION_FOLDER.format(folder_path=folder))

    if not os.access(folder, os.W_OK):
        logger.error(ErrorMessages.NO_WRITE_PERMISSION.format(folder=folder))
        raise PermissionError(ErrorMessages.NO_WRITE_PERMISSION.format(folder=folder))

def validate_file_path(file_path: Optional[str] = None) -> bool:
    """Validate file path for upload in the directory(OS)"""
    logger.info("In Utils :: validate_file_path")
    if not file_path:
        logger.error(ErrorMessages.FILE_REQUIRED)
        raise ValueError(ErrorMessages.FILE_REQUIRED)
    if  not os.path.isfile(file_path):
        error = ErrorMessages.INVALID_FILE_PATH.format(file_path=file_path)
        logger.error(error)
        raise ValueError(error)
    return True

def generate_blob_name(file_name: str, customer_uuid: str, application_uuid: str, channel_type: str) -> str:
    """Generate a unique blob name with the given parameters."""
    logger.info("In Utils :: generate_blob_name")

    # Validation for mandatory parameters
    if not file_name:
        raise ValueError(ErrorMessages.FIELD_MANDATORY_CANNOT_BE_NONE.format('file_name'))
    if not customer_uuid:
        raise ValueError(ErrorMessages.FIELD_MANDATORY_CANNOT_BE_NONE.format('customer_uuid'))
    if not application_uuid:
        raise ValueError(ErrorMessages.FIELD_MANDATORY_CANNOT_BE_NONE.format('application_uuid'))
    if not channel_type:
        raise ValueError(ErrorMessages.FIELD_MANDATORY_CANNOT_BE_NONE.format('channel_type'))

    logger.info("In AzureStorageManager :: _generate_blob_name")
    current_datetime = datetime.now()
    year = current_datetime.year
    month = current_datetime.strftime(DateTypes.MONTH) # full month name
    day = current_datetime.strftime(DateTypes.DAY)# day of month(01,02,..)
    return BLOB_PATTERN.format(customer_uuid=customer_uuid,application_uuid=application_uuid,channel_type=channel_type,year=year,month=month,day=day,file_name=file_name)

def get_content_type(file_name: str, content_type: Optional[str] = None) -> str:
    """Determine the content type based on the file extension or provided content type."""
    logger.info("In Utils :: get_content_type")
    if content_type:
        return content_type
    if not file_name:
        raise ValueError(ErrorMessages.INVALID_FILE_NAME)
    try:
        guessed_type, _ = mimetypes.guess_type(file_name)
    except Exception as e:
        logger.error(f"Exception Occurred while fetching content type :: {e}")
        return FileTypes.APPLICATION_OCTET_STREAM
    return guessed_type or FileTypes.APPLICATION_OCTET_STREAM


def parse_blob_url(url: str) -> str:
    """Parse blob URL to extract the container name and blob name."""
    logger.info("In Utils :: parse_blob_url")
    if not url:
        raise ValueError(ErrorMessages.INVALID_BLOB_URL)
    match = re.match(BlobUrl.BLOB_URL, url)
    if match:
        blob_name = unquote(match.group(2))
        return blob_name
    else:
        raise ValueError(ErrorMessages.INVALID_BLOB_URL)

def handle_azure_exceptions(exceptions: tuple=(), give_up: tuple=()):
    """
    Decorator to handle Azure-specific exceptions in a centralized way.
    """

    def decorator(func):
        sig = signature(func)

        def wrapper(self, *args, **kwargs):
            # Bind args and kwargs to function parameters
            bound_args = sig.bind(self, *args, **kwargs)
            all_args = bound_args.arguments
            max_retries=all_args.get('max_retries')
            if max_retries and not isinstance(max_retries,int):
                raise ValueError(ErrorMessages.INVALID_RETRY_PARAM)
            # Get max_retries from kwargs if available, otherwise use config value
            @backoff.on_exception(
                backoff.expo,
                exceptions,
                max_tries=max_retries or self.azure_config.max_retries,
                giveup=lambda e: isinstance(e, give_up)
            )
            def wrapped_func(*args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except ServiceRequestTimeoutError as e:
                    logger.error(f"Request to the Azure service timed out: {e}")
                    raise
                except ServiceResponseTimeoutError as e:
                    logger.error(f"Response from the Azure service timed out: {e}")
                    raise
                except ServiceRequestError as e:
                    logger.error(f"Exception while getting Container client: {e}")
                    raise
                except ServiceResponseError as e:
                    logger.error(f"Failed to understand the response from the Azure service: {e}")
                    raise
                except ClientAuthenticationError as e:
                    logger.error(f"Exception with credentials ::{e}")
                    raise
                except ResourceExistsError as e:
                    logger.error(f"Blob already exists :: {e}")
                    raise FileExistsError(ErrorMessages.BLOB_ALREADY_EXISTS)
                # when uploading it checks for actual container so exception may raise here incase of get_container_client it wont actually make azure call it just returns client
                except ResourceNotFoundError as e:
                    logger.error(f"Resource Not Found :: {e}")
                    raise FileNotFoundError(ErrorMessages.CONTAINER_OR_BLOB_NOT_FOUND)
                except IncompleteReadError as e:
                    logger.error(f"Connection closed Unexpectedly :: {e}")
                    raise
                except HttpResponseError as e:
                    logger.error(f"Error in protocol :: {e}")
                    raise
                except StreamConsumedError as e:
                    logger.error(f"Stream already consumed :: {e}")
                    raise
                except StreamClosedError as e:
                    logger.error(f"Stream closed :: {e}")
                    raise
                except AzureError as e:
                    logger.error(f"An unexpected Azure error occurred :: {e}")
                    raise
                except ConnectionError as e:
                    logger.error(f"Error in establishing connection :: {e}")
                    raise
                except ValueError as e:
                    logger.error(f"Error in value : {e}")
                    raise
                except Exception as e:
                    logger.error(f"An Unknown exception occurred: {e}")
                    raise RuntimeError(ErrorMessages.INTERNAL_SERVER_ERROR.format(error=e))
            return wrapped_func(*args, **kwargs)
        return wrapper
    return decorator
