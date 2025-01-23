from drf_yasg import openapi

class SuccessMessages:
    EMAIL_SENT_SUCCESS = "Email sent successfully."
    DRAFT_MAIL_DELETED_SUCCESS = "Draft conversation deleted successfully."
    POST_ORDER_SUCCESS = "extracted_order_details_json successfully updated."
    APPLICATION_JSON = 'application/json'
    TASK_STATUS_EMAIL = "Task status of the email"
    EMAIL_STATISTICS_SUCCESS = openapi.Response(
            description="Email statistics retrieved successfully",
            content={
                APPLICATION_JSON: openapi.Schema(
                    type='object',
                    properties={
                        'emailStatistics': openapi.Schema(
                            type='object',
                            properties={
                                'total_emails_received': openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="Total number of emails received"
                                ),
                                'ai_resolved': openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="Number of emails responded to by AI"
                                ),
                                'ai_assisted': openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="Number of emails where AI assisted humans"
                                ),
                                'manually_resolved': openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="Number of emails handled manually"
                                ),
                                'need_assistance': openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="Number of emails requiring human assistance"
                                )
                            }
                        )
                    }
                )
            }
        )
    
    MAILS_BY_CLIENT_ID_SUCCESS = openapi.Response(
        description="Emails retrieved successfully based on provided filters",
        content={
            APPLICATION_JSON: openapi.Schema(
                type='object',
                properties={
                    'result': openapi.Schema(
                        type='object',
                        properties={
                            'page_num': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Current page number"
                            ),
                            'total_entry_per_page': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Number of entries per page"
                            ),
                            'total_pages': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Total number of pages"
                            ),
                            'total_mails': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Total number of emails matching the filters (before pagination)"
                            ),
                            'mails_list': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type='object',
                                    properties={
                                        'mail_id': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Unique identifier of the email"
                                        ),
                                        'sender_name': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Sender name (if available)"
                                        ),
                                        'subject': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Email subject (if available)"
                                        ),
                                        'email_id': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Sender email address (if available)"
                                        ),
                                        'intent': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Extracted intent from the email (if available)"
                                        ),
                                        'status': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Email action flow status"
                                        ),
                                        'email_task_status' : openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description=TASK_STATUS_EMAIL
                                        ),
                                        'comment' : openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Comment associated with the email (if available)"
                                        ),
                                        'inserted_ts': openapi.Schema(
                                            type=openapi.TYPE_INTEGER,
                                            description="Timestamp when the email was inserted (in milliseconds)"
                                        ),
                                        'updated_ts': openapi.Schema(
                                            type=openapi.TYPE_INTEGER,
                                            description="Timestamp when the email was last updated (in milliseconds)"
                                        )
                                    }
                                )
                            )
                        }
                    )
                }
            )
        }
    )

    MAIL_CONVERSATIONS_BY_MAIL_ID_SUCCESS = openapi.Response(
        description="Mail conversations retrieved successfully for the specified email UUID",
        content={
            APPLICATION_JSON: openapi.Schema(
                type='object',
                properties={
                    'result': openapi.Schema(
                        type='object',
                        properties={
                            'email_data': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type='object',
                                    properties={
                                        'email_conversation_uuid': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Unique identifier of the email conversation"
                                        ),
                                        'sender_name': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Sender name (if available)"
                                        ),
                                        'email_subject': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Email subject"
                                        ),
                                        'email_flow_status': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Email flow status (preferred over deprecated email_status)"
                                        ),
                                        'email_task_status': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description=TASK_STATUS_EMAIL
                                        ),
                                        'parent_uuid': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Unique identifier of the parent conversation (if applicable)"
                                        ),
                                        'email_info_json': openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            description="Object containing parsed email information (may include sender name, attachments, etc.)"
                                        ),
                                        'dimension_action_json': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="JSON string containing dimension action data (format not specified)"
                                        ),
                                        'inserted_ts': openapi.Schema(
                                            type=openapi.TYPE_INTEGER,
                                            description="Timestamp when the conversation was inserted (in milliseconds)"
                                        ),
                                        'updated_ts': openapi.Schema(
                                            type=openapi.TYPE_INTEGER,
                                            description="Timestamp when the conversation was last updated (in milliseconds)"
                                        ),
                                        'draft': openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            description="Draft conversation data (only present for draft conversations with a parent)"
                                        ),
                                        "timeline": openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            description="List of email activities associated with the email"
                                        )
                                    }
                                )
                            )
                        }
                    )
                }
            )
        }
    )

    CONVERSATION_BY_CONVERSATION_ID_SUCCESS = openapi.Response(
        description="Conversation retrieved successfully for the specified conversation UUID",
        content={
            APPLICATION_JSON: openapi.Schema(
                type='object',
                properties={
                    'result': openapi.Schema(
                        type='object',
                        properties={
                            'conversation_uuid': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Unique identifier of the email conversation"
                            ),
                            'email_subject': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Email subject"
                            ),
                            'email_flow_status': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Email flow status (preferred over deprecated email_status)"
                            ),
                            'email_task_status': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description=TASK_STATUS_EMAIL
                            ),
                            'email_info_json': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                description="Object containing parsed email information (may include sender name, attachments, etc.)"
                            ),
                            'dimension_action_json': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="JSON string containing dimension action data (format not specified)"
                            ),
                            'insert_ts': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Timestamp when the conversation was inserted (in milliseconds)"
                            ),
                            'updated_ts': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Timestamp when the conversation was last updated (in milliseconds)"
                            ),
                            'parent_uuid': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Unique identifier of the parent conversation (if applicable)"
                            ),
                            'email_uuid': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Unique identifier of the email this conversation belongs to"
                            )
                        }
                    )
                }
            )
        }
    )

    GET_ORDER_DETAILS_SUCCESS = openapi.Response(
        description="Order details extracted successfully from the conversation",
        content={
            APPLICATION_JSON: openapi.Schema(
                type='object',
                properties={
                    'result': openapi.Schema(
                        type=openapi.TYPE_OBJECT,  # Assuming details_extracted_json is an object
                        description="Extracted order details in JSON format"
                    )
                }
            )
        }
    )

    GET_DOWNLOADABLE_URL_SUCCESS = openapi.Response(
        description="List of downloadable URLs and metadata for conversation attachments retrieved successfully",
        content={
            APPLICATION_JSON: openapi.Schema(
                type='object',
                properties={
                    'result': openapi.Schema(
                        type='object',
                        properties={
                            'url_data_list': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type='object',
                                    properties={
                                        'downloadable_url': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Pre-signed downloadable URL for the attachment"
                                        ),
                                        'metadata': openapi.Schema(
                                            type='object',
                                            description="Metadata associated with the attachment (e.g., filename)",
                                            properties={
                                                'filename': openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description="Extracted filename of the attachment"
                                                )
                                            }
                                        )
                                    }
                                )
                            )
                        }
                    )
                }
            )
        }
    )

    CREATE_DRAFT_SUCCESS = openapi.Response(
        description="Draft email created successfully.",
        content={
            APPLICATION_JSON: {
                "schema": openapi.Schema(
                    type="object",
                    properties={
                        "result": openapi.Schema(
                            type="object",
                            properties={"email_data": openapi.Schema(type="object", description="Conversation data.")},
                        )
                    },
                )
            }
        },
    )