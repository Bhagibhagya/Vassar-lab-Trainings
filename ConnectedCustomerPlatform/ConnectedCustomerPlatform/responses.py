from rest_framework.response import Response


class CustomResponse(Response):
    """
    Custom response class to ensure consistent response structure.
    """
    def __init__(self, result=None, status=True, code=200, **kwargs):
        """
        Initialize the custom response.

        Args:
            result (Any): The actual result data (message, data, etc.).
            status_code (int): HTTP status code. Default is 200.
        """
        data = {
            'result': result,
            'status': status,
            'code': code,
        }
        super().__init__(data, status=code, **kwargs)
