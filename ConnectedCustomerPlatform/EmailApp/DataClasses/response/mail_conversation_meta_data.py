from dataclasses import dataclass
from typing import Any

from .email_info_data import EmailInfo

@dataclass
class EmailConversation:
    email_conversation_id: str
    sender_name: str
    email_subject: str
    email_flow_status: str
    email_task_status: str
    email_info_json: EmailInfo  
    dimension_action_json: "{}"
    inserted_ts: int
    updated_ts: int
