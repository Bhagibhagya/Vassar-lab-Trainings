from dataclasses import dataclass

@dataclass
class MailMetadata:
    mail_id: str
    sender_name: str
    subject: str
    intent: str
    status: str
    inserted_ts: int
    updated_ts: int
