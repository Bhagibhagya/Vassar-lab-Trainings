from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db.utils import DatabaseError
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db import (
    DatabaseError,
    IntegrityError,
    OperationalError,
    DataError,
    ProgrammingError,
    InternalError
)
from EmailApp.constant import constants
from EmailApp.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.error_messages import ErrorMessages as global_error_message
from .responses import CustomResponse
import imaplib

import traceback


def generate_false_response(detail, code=status.HTTP_400_BAD_REQUEST):
    """
    Args:
        detail (Any): The actual result data (message, data, etc.).
        code (int): HTTP status code. Default is 400.
    """

    return CustomResponse(result=detail, status=False, code=code)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Log the exception
    traceback.print_exc()

    # Mapping exceptions to error messages and statuses
    exception_mapping = {
        serializers.ValidationError: (global_error_message.BAD_REQUEST, status.HTTP_400_BAD_REQUEST),
        IOError: (global_error_message.IO_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR),
        DatabaseError: (f"{global_error_message.DATABASE_ERROR}: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR),  # General database error, usually indicates a failure with the database operation.
        IntegrityError: (f"{global_error_message.INTEGRITY_ERROR}: {str(exc)}", status.HTTP_400_BAD_REQUEST),  # Indicates a violation of database integrity constraints, like unique constraints.
        OperationalError: (f"{global_error_message.OPERATIONAL_ERROR}: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR),  # Indicates operational issues, such as connection problems with the database.
        DataError: (f"{global_error_message.DATA_ERROR}: {str(exc)}", status.HTTP_400_BAD_REQUEST),  # Indicates issues with the data being processed, such as exceeding a field's size limit.
        ProgrammingError: (f"{global_error_message.PROGRAMMING_ERROR}: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR),  # Raised for SQL syntax errors or misuse of SQL commands.
        InternalError: (f"{global_error_message.DATABASE_ERROR}: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR),  # A general internal error that is not covered by other specific exceptions.
        ValueError: (str(exc), status.HTTP_400_BAD_REQUEST),
        PageNotAnInteger: (str(exc), status.HTTP_400_BAD_REQUEST),
        EmptyPage: (global_error_message.PAGE_EMPTY, status.HTTP_400_BAD_REQUEST),
        ConnectionError: (global_error_message.CONNECTION_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE)  # Handling for connection errors
    }

    false_response = None

    # Check for specific exceptions
    
    if exception_mapping.get(type(exc)) is not None:
        
        detail, status_code = exception_mapping.get(type(exc))
        false_response = generate_false_response(detail, status_code)
    
        return false_response
    
    if isinstance(exc, (TypeError, AttributeError)) and 'NoneType' in str(exc):
        false_response = generate_false_response(ErrorMessages.NONE_TYPE_ACCESS, status.HTTP_404_NOT_FOUND),

    # Handle Custom Exception separately
    elif isinstance(exc, CustomException):
        false_response = generate_false_response(exc.detail, exc.status_code)

    elif isinstance(exc, imaplib.IMAP4.error) and '[AUTHENTICATIONFAILED]' in str(exc):
        false_response = generate_false_response(ErrorMessages.AUTHENTICATION_FAILED, status.HTTP_401_UNAUTHORIZED)

    else:
        code = response.status_code if response is not None else status.HTTP_500_INTERNAL_SERVER_ERROR
        false_response = generate_false_response(str(exc), code)

    return false_response


class CustomException(APIException):
    default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail, status_code=None):
        self.status_code = status_code if status_code is not None else self.default_status_code
        self.detail = detail


class InvalidValueProvidedException(CustomException):
    """
    Custom exception for validation errors.
    """
    default_status_code = status.HTTP_400_BAD_REQUEST


class ResourceNotFoundException(CustomException):
    """
    Exception raised when a requested resource is not found.
    """
    default_status_code = status.HTTP_404_NOT_FOUND


class InvalidCollectionException(CustomException):
    """
    Exception raised with invalid collection provided
    """
    default_status_code = status.HTTP_404_NOT_FOUND

class UnauthorizedByScopeException(CustomException):
    """
    Exception raised when action is performing beyond scope.
    """
    default_status_code = status.HTTP_404_NOT_FOUND