from drf_yasg import openapi
class ErrorMessages:
    EMAILS_ERROR = openapi.Response(
        description="Bad request: Internal error occurred",
        content={
            'application/json': openapi.Schema(
                type='object',
                properties={
                    'detail': openapi.Schema(
                        type='string',
                        description="Error message "
                    )
                }
            )
        }
    )