from DBServices.models import Conversations
import uuid
from datetime import datetime
import json


def create_rateby_user_data():
    # Sample JSON data
    message_details = [
        {
            "id": "12345678-9012-3456-7890-123456789abc",
            "user_id": "ghi789",
            "csr_id": None,
            "source": "bot",
            "message_marker": "DELIVERED",
            "message_text": "Hello, how can I help you?",
            "media_url": "",
            "parent_message_uuid": "",
            "created_at": "2024-05-30T09:05:00",
            "dimension_action_json": [
                {
                    "dimensions":
                        {
                            "dimension": "Intent",
                            "value": "Greeting"
                        },
                    "action": "Bot"
                }
            ]
        }
    ]

    conversation_feedback_transaction = {
        "satisfaction_level": "Average",
        "additional_comments": "Great service!"
    }

    conversation_stats = {
        "conversationStartTime": "2024-05-25T10:30:00",
        "humanHandoffTime": "2024-05-25T11:00:00",
        "firstAgentAssignmentTime": "2024-05-25T11:15:00",
        "firstAgentMessageTime": "2024-05-25T11:20:00",
        "lastUserMessageTime": "2024-05-25T11:25:00",
        "lastAgentMessageTime": "2024-05-25T11:30:00",
        "conversationResolutionTime": "2024-05-25T12:00:00"
    }

    task_details = {
        "taskName": "Resolve Issue",
        "taskDescription": "Resolve customer's technical issue."
    }

    # Create a dummy data object
    conversation = Conversations.objects.create(
        conversation_uuid=uuid.uuid4(),
        name="Test Conversation",
        user_details_json={"user_id": "12345", "user_name": "John Doe"},
        conversation_status="active",
        csr_info_json={"csr_id": "54321", "csr_name": "Jane Smith"},
        csr_hand_off=False,
        conversation_stats_json=conversation_stats,
        conversation_feedback_transaction_json=conversation_feedback_transaction,
        task_details_json=task_details,
        summary="This is a summary of the conversation.",
        application_uuid=str(uuid.uuid4()),
        customer_uuid=str(uuid.uuid4()),
        message_details_json=message_details,
        insert_ts=datetime.now()
    )

    return conversation
