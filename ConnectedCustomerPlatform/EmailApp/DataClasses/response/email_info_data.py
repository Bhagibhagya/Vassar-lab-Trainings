from dataclasses import dataclass, field
from typing import List, Optional
from dataclasses import dataclass, asdict


@dataclass
class EmailInfo:
    email_body_url: str
    attachments: List[str] = field(default_factory=list)
    sender: Optional[str] = None
    sender_name: Optional[str] = None
    email_type: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    cc_recipients: List[str] = field(default_factory=list)
    bcc_recipients: List[str] = field(default_factory=list)
    email_body_summary: str = field(default=None)  # max 200 char
    email_meta_body: str = field(default=None)  # Additional metadata about email body
    html_body: str = field(default=None)  # HTML content of the email
    extracted_order_details: str = field(default=None)
    validated_details: str = field(default=None)
    verified: bool = field(default=None)

    # creating new entry while email is draft and adding body url

    @classmethod
    def from_json(cls, json_data):
        return cls(
            email_body_url=json_data.get('email_body_url', None),
            attachments=json_data.get('attachments', []),
            sender=json_data.get('sender', None),
            sender_name=json_data.get('sender_name', None),
            email_type=json_data.get('email_type', None),
            recipient_name=json_data.get('recipient_name', None),
            recipient=json_data.get('recipient', None),
            recipients=json_data.get('recipients', []),
            cc_recipients=json_data.get('cc_recipients', []),
            bcc_recipients=json_data.get('bcc_recipients', []),
            email_body_summary=json_data.get('email_body_summary', None),
            email_meta_body=json_data.get('email_meta_body', None),
            html_body=json_data.get('html_body', None),
            extracted_order_details=json_data.get('extracted_order_details', None),
            validated_details=json_data.get('validated_details', None),
            verified=json_data.get('verified', None)
        )

    @classmethod
    def create_email_info_json(cls, email_body_url: str, attachments: List[str] = [],
                               sender: Optional[str] = None, sender_name: Optional[str] = None, email_type: str = None,
                               recipient_name: str = None,
                               client_user_email: Optional[str] = None, recipients: List[str] = [],
                               cc_recipients: List[str] = [], bcc_recipients: List[str] = [],
                               email_body_summary: Optional[str] = None,
                               email_meta_body: Optional[str] = None, html_body: Optional[str] = None,
                               extracted_order_details: Optional[str] = None, validated_details: Optional[str] = None,
                               verified: bool = None) -> str:
        # Create an instance of EmailInfo with the provided values
        email_info = cls(
            email_body_url=email_body_url,
            attachments=attachments,
            sender=sender,
            sender_name=sender_name,
            email_type=email_type,
            recipient_name=recipient_name,
            recipient=client_user_email,
            recipients=recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            email_body_summary=email_body_summary,
            email_meta_body=email_meta_body,
            html_body=html_body,
            extracted_order_details=extracted_order_details,
            validated_details=validated_details,
            verified=verified
        )
        # Return the JSON representation of the EmailInfo instance
        return email_info.__dict__


from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class EmailRecipient(BaseModel):
    name: Optional[str]
    email: str


class Attachment(BaseModel):
    file_name: str
    file_size: int
    file_type: str
    file_path: str


class EmailInfoDetailModel(BaseModel):
    email_info_uuid: str
    email_uuid: str  # Foreign Key
    email_subject: Optional[str] = None
    email_body_url: Optional[str] = None
    attachments: Optional[List[Attachment]] = None
    sender: Optional[str] = None
    sender_name: Optional[str] = None
    email_type: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient: Optional[str] = None
    recipients: Optional[List[EmailRecipient]] = None
    cc_recipients: Optional[List[EmailRecipient]] = None
    bcc_recipients: Optional[List[EmailRecipient]] = None
    email_body_summary: Optional[str] = None
    email_meta_body: Optional[str] = None
    html_body: Optional[str] = None
    extracted_order_details: Optional[str] = None
    validated_details: Optional[str] = None
    verified: Optional[bool] = None
    timestamp: Optional[datetime] = None
    in_reply_to: Optional[str] = None
    references: Optional[str] = None

    class Config:
        from_attribute = True