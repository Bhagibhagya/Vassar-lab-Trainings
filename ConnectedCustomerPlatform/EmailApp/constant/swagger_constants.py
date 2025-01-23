from drf_yasg import openapi
from EmailApp.constant.constants import EmailDashboardParams, EmailConversationParams
from drf_yasg import openapi

CUSTOMER_UUID = "Customer UUID"
# Common Request Params for Swagger
customer_uuid_params = openapi.Parameter(
    name='customer-uuid', in_=openapi.IN_HEADER, description=CUSTOMER_UUID, type=openapi.TYPE_STRING, required=True)

user_id_params = openapi.Parameter(
    name=EmailDashboardParams.USER_UUID, in_=openapi.IN_HEADER, description='User ID', type=openapi.TYPE_STRING)

role_id_params = openapi.Parameter(
    name=EmailDashboardParams.ROLE_UUID, in_=openapi.IN_HEADER, description='Role ID', type=openapi.TYPE_STRING)

application_id_params = openapi.Parameter(
    name=EmailDashboardParams.APPLICATION_UUID, in_=openapi.IN_HEADER, description='Application ID',
    type=openapi.TYPE_STRING)

channel_type_params = openapi.Parameter(
    name=EmailDashboardParams.CHANNEL_TYPE_UUID, in_=openapi.IN_QUERY, description='Channel Type UUID',
    type=openapi.TYPE_STRING)

start_date_params = openapi.Parameter(
    name=EmailDashboardParams.START_DATE, in_=openapi.IN_QUERY, description="START DATE", type=openapi.TYPE_STRING,
    format="date")

end_date_params = openapi.Parameter(
    name=EmailDashboardParams.END_DATE, in_=openapi.IN_QUERY, description="END DATE", type=openapi.TYPE_STRING,
    format="date")

customer_client_uuid_params = openapi.Parameter(
    name=EmailDashboardParams.CUSTOMER_CLIENT_UUID, in_=openapi.IN_QUERY, description="CUSTOMER CLIENT UUID",
    type=openapi.TYPE_STRING)

sender_name_params = openapi.Parameter(
    name=EmailDashboardParams.SENDER_NAME, in_=openapi.IN_QUERY, description="List of sender names",
    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), required=False, default="[]"
)

email_id_params = openapi.Parameter(
    name=EmailDashboardParams.EMAIL_ID, in_=openapi.IN_QUERY, description="List of email IDs", type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING), required=False, default="[]"
)

intent_params = openapi.Parameter(
    name=EmailDashboardParams.INTENT, in_=openapi.IN_QUERY, description="List of intents", type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING), required=False, default="[]"
)

status_params = openapi.Parameter(
    name=EmailDashboardParams.STATUS, in_=openapi.IN_QUERY, description="List of statuses", type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING), required=False, default="[]"
)

customer_name_params = openapi.Parameter(
    name=EmailDashboardParams.CUSTOMER_NAME, in_=openapi.IN_QUERY, description="List of customer names",
    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), required=False, default="[]"
)

geography_params = openapi.Parameter(
    name=EmailDashboardParams.GEOGRAPHY, in_=openapi.IN_QUERY, description="List of geographies",
    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), required=False, default="[]"
)

customer_tier_params = openapi.Parameter(
    name=EmailDashboardParams.CUSTOMER_TIER, in_=openapi.IN_QUERY, description="List of customer tiers",
    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), required=False, default="[]"
)

page_number_params = openapi.Parameter(
    name=EmailDashboardParams.PAGE_NUMBER, in_=openapi.IN_QUERY, description="PAGE NUMBER", type=openapi.TYPE_NUMBER)

total_entry_per_page_params = openapi.Parameter(
    name=EmailDashboardParams.TOTAL_ENTRY_PER_PAGE, in_=openapi.IN_QUERY, description="TOTAL ENTRY PER PAGE",
    type=openapi.TYPE_NUMBER)

email_action_flow_status_params = openapi.Parameter(
    name=EmailDashboardParams.EMAIL_ACTION_FLOW_STATUS, in_=openapi.IN_QUERY,
    description="Email action flow status as param", type=openapi.TYPE_STRING)

email_uuid_params = openapi.Parameter(
    name=EmailConversationParams.EMAIL_UUID, in_=openapi.IN_QUERY, description="Email UUID", type=openapi.TYPE_STRING)

email_conversation_uuid_params = openapi.Parameter(
    name=EmailConversationParams.EMAIL_CONVERSATION_UUID, in_=openapi.IN_QUERY, description="Email Conversation UUID",
    type=openapi.TYPE_STRING)

from_email_id_params = openapi.Parameter(
    name=EmailConversationParams.FROM_EMAIL_ID, in_=openapi.IN_QUERY, description="From Email ID",
    type=openapi.TYPE_STRING)

post_order_details_body = openapi.Schema(
    type="object",
    required=["email_conversation_uuid", "details_extracted_json"],
    properties={
        "email_conversation_uuid": openapi.Schema(type="string", description="The UUID of the email conversation."),
        "channel_type_uuid": openapi.Schema(type="string", description="The UUID of the channel_type for post order"),
        "details_extracted_json": openapi.Schema(
            type="object", description="JSON data containing extracted order details."
        ),
    },
)
email_statistics_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=[EmailDashboardParams.START_DATE, EmailDashboardParams.END_DATE,
              ],
    properties={
        EmailDashboardParams.START_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="Start date timestamp for filtering for email statistics"
        ),
        EmailDashboardParams.END_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="End date timestamp for filtering for email statistics"
        ),
        EmailDashboardParams.CUSTOMER_CLIENT_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="UUID of the customer client for email statistics"
        ),
        EmailDashboardParams.CHANNEL_TYPE_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="Channel type UUID for email statistics"
        ),
        EmailDashboardParams.SENDER_NAME: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of sender names for filtering for email statistics", default=[]
        ),
        EmailDashboardParams.EMAIL_ID: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of email IDs for filtering for email statistics", default=[]
        ),
        EmailDashboardParams.INTENT: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of intents for filtering for email statistics", default=[]
        ),
        EmailDashboardParams.STATUS: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of statuses for filtering for email statistics", default=[]
        ),
        EmailDashboardParams.CUSTOMER_NAME: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of customer names for filtering for email statistics", default=[]
        ),
        EmailDashboardParams.GEOGRAPHY: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of geographies for filtering for email statistics", default=[]
        ),
        EmailDashboardParams.CUSTOMER_TIER: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of customer tiers for filtering for email statistics", default=[]
        ),
    }
)
emails_by_client_id_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=[EmailDashboardParams.START_DATE, EmailDashboardParams.END_DATE,
              ],
    properties={
        EmailDashboardParams.START_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="Start date timestamp for filtering for emails_by_client_id "
        ),
        EmailDashboardParams.END_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="End date timestamp for filtering for emails_by_client_id"
        ),
        EmailDashboardParams.CUSTOMER_CLIENT_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="UUID of the customer client for emails_by_client_id"
        ),
        EmailDashboardParams.EMAIL_ACTION_FLOW_STATUS: openapi.Schema(
            type=openapi.TYPE_STRING, description="Email action flow status for emails_by_client_id"
        ),
        EmailDashboardParams.PAGE_NUMBER: openapi.Schema(
            type=openapi.TYPE_NUMBER, description="Page number of response for emails_by_client_id"
        ),
        EmailDashboardParams.TOTAL_ENTRY_PER_PAGE: openapi.Schema(
            type=openapi.TYPE_NUMBER, description="Total entry per page for emails_by_client_id"
        ),
        EmailDashboardParams.CHANNEL_TYPE_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="Channel type UUID for emails_by_client_id"
        ),
        EmailDashboardParams.SENDER_NAME: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of sender names for filtering for emails_by_client_id", default=[]
        ),
        EmailDashboardParams.EMAIL_ID: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of email IDs for filtering for emails_by_client_id", default=[]
        ),
        EmailDashboardParams.INTENT: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of intents for filtering for emails_by_client_id", default=[]
        ),
        EmailDashboardParams.STATUS: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of statuses for filtering for emails_by_client_id", default=[]
        ),
    }
)

create_draft_response_body = openapi.Schema(
    type="object",
    required=[EmailDashboardParams.CUSTOMER_CLIENT_UUID, EmailConversationParams.EMAIL_UUID,
              EmailConversationParams.FROM_EMAIL_ID, EmailConversationParams.IN_REPLY_TO, EmailConversationParams.TO,
              EmailConversationParams.SUBJECT,
              ],
    properties={
        EmailDashboardParams.CUSTOMER_CLIENT_UUID: openapi.Schema(
            type="string", description="The UUID of the customer client."
        ),
        EmailConversationParams.EMAIL_UUID: openapi.Schema(
            type="string", description="The UUID of the email."
        ),
        EmailConversationParams.FROM_EMAIL_ID: openapi.Schema(
            type="string", description="The email address to send from."
        ),
        EmailConversationParams.IN_REPLY_TO: openapi.Schema(
            type="string", description="The UUID of the parent email conversation (for replies)."
        ),
        EmailConversationParams.TO: openapi.Schema(
            type="array", items=openapi.Items(type=openapi.TYPE_STRING), description="The recipient email address."
        ),
        EmailConversationParams.SUBJECT: openapi.Schema(
            type="string", description="The email subject."
        ),
    },
)

email_statistics_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=[EmailDashboardParams.START_DATE, EmailDashboardParams.END_DATE,
              ],
    properties={
        EmailDashboardParams.START_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="Start date timestamp for filtering for email_statistics_body"
        ),
        EmailDashboardParams.END_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="End date timestamp for filtering for email_statistics_body"
        ),
        EmailDashboardParams.CUSTOMER_CLIENT_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="UUID of the customer client for email_statistics_body"
        ),
        EmailDashboardParams.CHANNEL_TYPE_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="Channel type UUID for email_statistics_body"
        ),
        EmailDashboardParams.SENDER_NAME: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of sender names for filtering for email_statistics_body", default=[]
        ),
        EmailDashboardParams.EMAIL_ID: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of email IDs for filtering for email_statistics_body", default=[]
        ),
        EmailDashboardParams.INTENT: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of intents for filtering for email_statistics_body", default=[]
        ),
        EmailDashboardParams.STATUS: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of statuses for filtering for email_statistics_body", default=[]
        ),
        EmailDashboardParams.CUSTOMER_NAME: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of customer names for filtering", default=[]
        ),
        EmailDashboardParams.GEOGRAPHY: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of geographies for filtering for email_statistics_body", default=[]
        ),
        EmailDashboardParams.CUSTOMER_TIER: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of customer tiers for filtering for email_statistics_body", default=[]
        ),
    }
)

emails_by_client_id_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=[EmailDashboardParams.START_DATE, EmailDashboardParams.END_DATE,
              ],
    properties={
        EmailDashboardParams.START_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="Start date timestamp for filtering"
        ),
        EmailDashboardParams.END_DATE: openapi.Schema(
            type=openapi.TYPE_STRING, description="End date timestamp for filtering"
        ),
        EmailDashboardParams.CUSTOMER_CLIENT_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="UUID of the customer client"
        ),
        EmailDashboardParams.EMAIL_ACTION_FLOW_STATUS: openapi.Schema(
            type=openapi.TYPE_STRING, description="Email action flow status"
        ),
        EmailDashboardParams.PAGE_NUMBER: openapi.Schema(
            type=openapi.TYPE_NUMBER, description="Page number of response"
        ),
        EmailDashboardParams.TOTAL_ENTRY_PER_PAGE: openapi.Schema(
            type=openapi.TYPE_NUMBER, description="Total entry per page"
        ),
        EmailDashboardParams.CHANNEL_TYPE_UUID: openapi.Schema(
            type=openapi.TYPE_STRING, description="Channel type UUID"
        ),
        EmailDashboardParams.SENDER_NAME: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of sender names for filtering", default=[]
        ),
        EmailDashboardParams.EMAIL_ID: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of email IDs for filtering", default=[]
        ),
        EmailDashboardParams.INTENT: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of intents for filtering", default=[]
        ),
        EmailDashboardParams.STATUS: openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
            description="List of statuses for filtering", default=[]
        ),
    }
)

get_filter_values_by_customer_client_uuid_details_body = openapi.Schema(
    type="object",
    required=["email_action_flow_status", "start_date", "end_date", "customer_client_uuid"],
    properties={

        "start_date": openapi.Schema(type="string",
                                     description="The start date as MM/DD/YYYY of get_filter_values_by_customer_client_uuid"),
        "end_date": openapi.Schema(type="string", description="The end date MM/DD/YYYY"),
        "email_action_flow_status": openapi.Schema(type="string",
                                                   description="The email action flow status of get_filter_values_by_customer_client_uuid "),
        "channel_type_uuid": openapi.Schema(type="string",
                                            description="The UUID of the channel_type of get_filter_values_by_customer_client_uuid"),
        "customer_client_uuid": openapi.Schema(type="string", description="The UUID of the customer_client."),

    },
)

get_filter_values_by_customer_uuid_details_body = openapi.Schema(
    type="object",
    required=["email_action_flow_status", "start_date", "end_date", "customer_client_uuid"],
    properties={

        "start_date": openapi.Schema(type="string", description="The start date as MM/DD/YYYY"),
        "end_date": openapi.Schema(type="string", description="The end date MM/DD/YYYY"),
        "email_action_flow_status": openapi.Schema(type="string", description="The email action flow status "),
        "channel_type_uuid": openapi.Schema(type="string", description="The UUID of the channel_type")

    },
)

get_customers_body = openapi.Schema(
    type="object",
    required=["email_action_flow_status", "start_date", "end_date", "total_entry_per_page", "page_number"],
    properties={

        "start_date": openapi.Schema(type="string", description="The start date as MM/DD/YYYY"),
        "end_date": openapi.Schema(type="string", description="The end date as MM/DD/YYYY"),
        "email_action_flow_status": openapi.Schema(type="string", description="The email action flow status "),
        "channel_type_uuid": openapi.Schema(type="string", description="The UUID of the channel_type"),
        "geography_list": openapi.Schema(type="array", items=openapi.Items(type="string"),
                                         description="geography_list"),
        "customer_tier_list": openapi.Schema(type="array", items=openapi.Items(type="string"),
                                             description="customer_tier_list"),
        "customer_name_list": openapi.Schema(type="array", items=openapi.Items(type="string"),
                                             description="customer_name_list"),
        "page_number": openapi.Schema(type="integer", description="page_number"),
        "total_entry_per_page": openapi.Schema(type="integer", description="total_entry_per_page"),

    },
)

reply_to_mail_body = openapi.Schema(
    type="object",
    required=[
        "email_conversation_uuid",
        "from_email_id",
        "to",
        "in_reply_to",
        "subject",
        "body"
    ],
    properties={
        "email_conversation_uuid": openapi.Schema(type="string", description="UUID of the email conversation"),
        "from_email_id": openapi.Schema(type="string", format="email", description="Email ID of the sender"),
        "to": openapi.Schema(
            type="array",
            items=openapi.Items(type="string", format="email"),
            description="List of recipient email addresses"
        ),
        "bcc": openapi.Schema(
            type="array",
            items=openapi.Items(type="string", format="email"),
            description="List of BCC email addresses"
        ),
        "cc": openapi.Schema(
            type="array",
            items=openapi.Items(type="string", format="email"),
            description="List of CC email addresses"
        ),
        "in_reply_to": openapi.Schema(type="string", description="UUID of the email being replied to"),
        "subject": openapi.Schema(type="string", description="Subject of the email"),
        "body": openapi.Schema(type="string", description="Body of the email"),
        "attachments": openapi.Schema(
            type="array",
            items=openapi.Items(type="string"),
            description="List of attachment file names"
        ),
        "channel_type_uuid": openapi.Schema(type="string", description="UUID of the channel type")
    }
)

# Swagger Tags
EMAIL_CONVERSATION_TAG = ["EmailApp - Email Conversations"]
EMAIL_SERVER_TAG = "EmailApp - EmailServer"
EMAILS_TAG = "EmailApp - Emails"
DIMENSIONS_TAG = "EmailApp - Dimensions"
CUSTOMER_CLIENT_TAG = "EmailApp-CustomerClient"

# Headers
customer_uuid_header = openapi.Parameter(
    'customer_uuid', openapi.IN_HEADER, description=CUSTOMER_UUID, type=openapi.TYPE_STRING, required=True)
application_uuid_header = openapi.Parameter(
    'application_uuid', openapi.IN_HEADER, description="Application UUID", type=openapi.TYPE_STRING, required=True)
user_id_header = openapi.Parameter(
    'user_id', openapi.IN_HEADER, description="User ID", type=openapi.TYPE_STRING, required=True)

# Query Parameters
customer_uuid_query = openapi.Parameter(
    'customer_uuid', openapi.IN_QUERY, description=CUSTOMER_UUID, type=openapi.TYPE_STRING, required=True)
customer_client_uuid_query = openapi.Parameter(
    'customer_client_uuid', openapi.IN_QUERY, description="Customer Client UUID", type=openapi.TYPE_STRING,
    required=True)
start_date_query = openapi.Parameter(
    'start_date', openapi.IN_QUERY, description="Start date in MM/dd/yyyy format", type=openapi.TYPE_STRING,
    required=True)
end_date_query = openapi.Parameter(
    'end_date', openapi.IN_QUERY, description="End date in MM/dd/yyyy format", type=openapi.TYPE_STRING, required=True)
email_action_flow_status_query = openapi.Parameter(
    'email_action_flow_status', openapi.IN_QUERY, description="Email action flow status", type=openapi.TYPE_STRING,
    required=True)

customer_uuid_query = openapi.Parameter(
    'customer-uuid',
    openapi.IN_QUERY,
    description="UUID of the customer",
    type=openapi.TYPE_STRING,
    required=True
)

start_date_query = openapi.Parameter(
    EmailDashboardParams.START_DATE,
    openapi.IN_QUERY,
    description="Start date in MM/DD/YYYY format",
    type=openapi.TYPE_STRING,
    required=True
)

end_date_query = openapi.Parameter(
    EmailDashboardParams.END_DATE,
    openapi.IN_QUERY,
    description="End date in MM/DD/YYYY format",
    type=openapi.TYPE_STRING,
    required=True
)

customer_name_query = openapi.Parameter(
    EmailDashboardParams.CUSTOMER_NAME,
    openapi.IN_QUERY,
    description="List of customer names for filtering",
    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
    required=False
)

geography_query = openapi.Parameter(
    EmailDashboardParams.GEOGRAPHY,
    openapi.IN_QUERY,
    description="List of geography for filtering",
    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
    required=False
)

customer_tier_query = openapi.Parameter(
    EmailDashboardParams.CUSTOMER_TIER,
    openapi.IN_QUERY,
    description="List of customer tiers for filtering",
    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
    required=False
)

page_number_query = openapi.Parameter(
    EmailDashboardParams.PAGE_NUMBER,
    openapi.IN_QUERY,
    description="Page number for pagination",
    type=openapi.TYPE_INTEGER,
    required=False,
    default=1
)

total_entry_per_page_query = openapi.Parameter(
    EmailDashboardParams.TOTAL_ENTRY_PER_PAGE,
    openapi.IN_QUERY,
    description="Total number of entries per page",
    type=openapi.TYPE_INTEGER,
    required=False,
    default=10
)

customer_uuid_header_param = openapi.Parameter(
    'customer-uuid', openapi.IN_HEADER, description="Customer ID", type=openapi.TYPE_STRING, required=True
)
user_uuid_header_param = openapi.Parameter(
    'user-uuid', openapi.IN_HEADER, description="User ID", type=openapi.TYPE_STRING, required=False
)
role_uuid_header_param = openapi.Parameter(
    'role-uuid', openapi.IN_HEADER, description="Role ID", type=openapi.TYPE_STRING, required=False
)
application_uuid_header_param = openapi.Parameter(
    'application-uuid', openapi.IN_QUERY, description="Application UUID", type=openapi.TYPE_STRING, required=False
)
conversation_uuid_query_param = openapi.Parameter(
    'email_conversation_uuid', openapi.IN_QUERY, description="Conversation UUID", type=openapi.TYPE_STRING,
    required=True
)

channel_type_query_param = openapi.Parameter(
    'channel_type', openapi.IN_QUERY, description="Channel Type", type=openapi.TYPE_STRING, required=False
)

entity_uuid_param = openapi.Parameter(
            name="entity_uuid",
            in_=openapi.IN_PATH,
            description="Unique identifier of the entity",
            type=openapi.TYPE_STRING,
            required=True
        )

APPLICATION_JSON = 'application/json'
CLIENT_1 = 'Client 1'
CLIENT_2 = 'Client 2'
BAD_REQUEST = 'Bad Request'
CUSTOMER_CLIENT_NOT_FOUND = 'Customer Client Not Found'
CUSTOMER_CLIENT_RESPONSE_EXAMPLE1 = {
    APPLICATION_JSON: {
        'result': {
            'filters': {
                'customer_client_names': [CLIENT_1, CLIENT_2],
                'geography': ['Geography 1', 'Geography 2'],
                'customer_tier': ['Tier 1', 'Tier 2']
            }
        },
        'status': True,
        'code': 200
    }
}

CUSTOMER_CLIENT_RESPONSE_EXAMPLE2 = {
    APPLICATION_JSON: {
        'status': False,
        'code': 400,
        'message': BAD_REQUEST
    }
}
CUSTOMER_CLIENT_RESPONSE_EXAMPLE3 = {
    APPLICATION_JSON: {
        'status': False,
        'code': 404,
        'message': CUSTOMER_CLIENT_NOT_FOUND
    }
}
DIMENSIONS_RESPONSE_EXAMPLE1 = {
    APPLICATION_JSON: {
        'result': {
            "page_num": 1,
            "total_entry_per_page": 10,
            "total_pages": 5,
            "total_customers": 50,
            "customer_list": [
                {
                    'customer_client_uuid': 'uuid1',
                    'customer_client_name': CLIENT_1,
                    'geography': 'Geography 1',
                    'customer_tier': 'Tier 1',
                    'total_mails': 100,
                    'inserted_ts': 1617811200000,
                    'updated_ts': 1627811200000,
                },
                # More customer data here
            ]
        },
        'status': True,
        'code': 200
    }
}
DIMENSIONS_RESPONSE_EXAMPLE2 = {
    APPLICATION_JSON: {
        'status': False,
        'code': 400,
        'message': BAD_REQUEST
    }
}
DIMENSIONS_RESPONSE_EXAMPLE3 = {
    APPLICATION_JSON: {
        'status': False,
        'code': 404,
        'message': CUSTOMER_CLIENT_NOT_FOUND
    }
}
EMAILS_RESPONSE_EXAMPLE1 = {
    APPLICATION_JSON: {
        'result': {
            'filters': {
                'customer_client_names': ['Client 1'],
                'geography': ['Dimension 1'],
                'customer_tier': ['Dimension 1']
            }
        },
        'status': True,
        'code': 200
    }
}
EMAILS_RESPONSE_EXAMPLE2 = {
    APPLICATION_JSON: {
        'status': False,
        'code': 400,
        'message': BAD_REQUEST
    }
}
EMAILS_RESPONSE_EXAMPLE3 = {
    APPLICATION_JSON: {
        'status': False,
        'code': 404,
        'message': CUSTOMER_CLIENT_NOT_FOUND
    }
}

EMAIL_SERVER_OPERATION_DESCRIPTION1 = "Api for Testing Email_lifecycle_flow"
EMAILS_RESPONSE_DESCRIPTION1 = "Lists of filter values"
EMAILS_RESPONSE_DESCRIPTION2 = "Invalid data "
EMAILS_RESPONSE_DESCRIPTION3 = "Customer client not found "
EMAILS_OPERATION_DESCRIPTION1 = "Get Values to be displayed in filters"

DIMENSIONS_RESPONSE_DESCRIPTION1 = "Paginated list of customers"
DIMENSIONS_RESPONSE_DESCRIPTION2 = "Invalid data  "
DIMENSIONS_RESPONSE_DESCRIPTION3 = "Customer client not found  "
DIMENSIONS_OPERATION_DESCRIPTION1 = "Get a paginated list of customers based on specified criteria."

CUSTOMER_CLIENTS_RESPONSE_DESCRIPTION1 = "Lists of filter values"
CUSTOMER_CLIENTS_RESPONSE_DESCRIPTION2 = "Invalid data"
CUSTOMER_CLIENTS_RESPONSE_DESCRIPTION3 = "Customer client not found"
CUSTOMER_CLIENTS_OPERATION_DESCRIPTION1 = "Get filter values (customer_client_names, geography, customer_tier) by customer UUID."



from drf_yasg import openapi

class ChromaDBParams:
    CUSTOMER_UUID = "customer_uuid"
    APPLICATION_UUID = "application_uuid"
    USER_UUID = "user_uuid"
    RESPONSE_CONFIG_UUID = "response_config_uuid"

# Define Swagger manual parameters for reuse
class ChromaDBSwaggerParams:
    CUSTOMER_UUID_HEADER = openapi.Parameter(
        ChromaDBParams.CUSTOMER_UUID,
        openapi.IN_HEADER,
        description="UUID of the customer",
        type=openapi.TYPE_STRING,
        required=True
    )
    APPLICATION_UUID_HEADER = openapi.Parameter(
        ChromaDBParams.APPLICATION_UUID,
        openapi.IN_HEADER,
        description="UUID of the application",
        type=openapi.TYPE_STRING,
        required=True
    )
    USER_UUID_HEADER = openapi.Parameter(
        ChromaDBParams.USER_UUID,
        openapi.IN_HEADER,
        description="UUID of the user",
        type=openapi.TYPE_STRING,
        required=True
    )
    RESPONSE_CONFIG_UUID_QUERY = openapi.Parameter(
        ChromaDBParams.RESPONSE_CONFIG_UUID,
        openapi.IN_QUERY,
        description="Response configuration UUID",
        type=openapi.TYPE_STRING,
        required=True
    )
