from rest_framework.exceptions import APIException

class InvalidValueProvidedException(APIException):
    """
    Custom exception for validation errors.
    """
    status_code = 400
    default_detail = 'Validation error.'

    def __init__(self, detail, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        self.detail = detail

class ResourceNotFoundException(APIException):
    """
    Exception raised when a requested resource is not found.
    """

    status_code = 404
    default_detail = 'Resource not found'

    def __init__(self, detail, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        self.detail = detail