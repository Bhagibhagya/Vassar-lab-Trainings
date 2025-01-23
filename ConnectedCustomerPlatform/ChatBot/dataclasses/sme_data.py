from dataclasses import  field, dataclass, asdict
from typing import Optional, List, Literal, Union
from uuid import UUID

@dataclass
class Question:
    question_uuid: UUID
    question_text: str
    answer_uuid: UUID
    is_system_generated: bool
    author_user_uuid: UUID
    author_role_uuid: UUID
    application_uuid: UUID
    customer_uuid: UUID

@dataclass
class Attachments:
    url: str
    type: str
    name: List[str]

@dataclass
class ImageAttachment(Attachments):
    source: Optional[str] = None


@dataclass
class VideoAttachment(Attachments):
    start_time: str


@dataclass
class FileDetailsJson:
    file_name: str
    file_uuid: str

@dataclass
class EntityDetailsJson:
    entity_name: str
    entity_uuid: str

@dataclass
class Answer:
    answer_uuid: UUID
    answer_text: str
    attachment_details_json: List[Union[ImageAttachment, VideoAttachment]]
    is_system_generated: bool
    author_user_uuid: UUID
    author_role_uuid: UUID
    application_uuid: UUID
    customer_uuid: UUID

    in_cache: bool = True
    is_verified: Optional[bool] = False
    verifier_user_uuid: Optional[UUID] = None
    verifier_role_uuid: Optional[UUID] = None
    file_details_json: Optional[List[FileDetailsJson]] = field(default_factory=list)
    entity_details_json: Optional[List[EntityDetailsJson]] = field(default_factory=list)
    feedback: Optional[str] = None

@dataclass
class Draft:
    draft_content: str
    attachment_details_json: List[Union[ImageAttachment, VideoAttachment]]
    author_user_uuid: UUID
    author_role_uuid: UUID
    application_uuid: UUID
    customer_uuid: UUID

    answer_uuid: Optional[UUID] = None
    draft_uuid: Optional[UUID] = None