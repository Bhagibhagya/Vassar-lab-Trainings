from drf_yasg import openapi

# Custom swagger response for getting scope types
APPLICATION_JSON = 'application/json'
SCOPE_CATEGORY_VALUES_SUCCESS = openapi.Response(
    description="Scope types retrieved successfully",
    content={
        APPLICATION_JSON: openapi.Schema(
            type='object',
            properties={
                'result': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Result of the scope value response retrieval"
                ),
                'status_code': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="HTTP status code"
                ),
                'status_code_description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of the status code"
                ),
                'message': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    nullable=True,
                    description="Additional message, if any"
                ),
                'response': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING
                    ),
                    description="List of response items"
                )
            }
        )
    }
)

SCOPE_CATEGORIES_RESPONSE_SUCCESS = openapi.Response(
    description="Scope values response retrieved successfully",
    content={
        APPLICATION_JSON: openapi.Schema(
            type='object',
            properties={
                'result': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Result of the scope types response retrieval"
                ),
                'status_code': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="HTTP status code"
                ),
                'status_code_description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of the status code"
                ),
                'message': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    nullable=True,
                    description="Additional message, if any"
                ),
                'response': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING
                    ),
                    description="List of response items"
                )
            }
        )
    }
)

SCOPE_TYPES_VALUES_RESPONSE_SUCCESS = "List of Customer Tiers, Customers under specific tier, Intent, Sentiment or Geography values)"
