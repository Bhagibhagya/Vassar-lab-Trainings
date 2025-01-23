import uuid
from datetime import datetime
from typing import Union

from rest_framework import serializers
from rest_framework.fields import DictField

from DBServices.models import Conversations
from ChatBot.constant.constants import Constants, KnowledgeSourceTypes
from Platform.serializers import PagiNationSerializer
from ChatBot.constant.constants import Constants,KnowledgeSourceConstants,EntityConstants


class ConversationFeedBackSerializer(serializers.Serializer):
    chat_conversation_uuid = serializers.CharField(max_length=45,required=True)
    satisfaction_level = serializers.ChoiceField(choices=Constants.SATISFACTION_CHOICES, required=True)
    additional_comments = serializers.CharField(max_length=1000, required=False, allow_blank=True)

class AttributeDetailSerializer(serializers.Serializer):
    values = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,  # Ensure at least one value
    )
    description = serializers.CharField()

     
class AttributeDetailsSerializer(serializers.Serializer):
    attributes = serializers.DictField(child=AttributeDetailSerializer(),allow_empty=False)
    entity_name = serializers.CharField(required=True)

class EntitySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    attributes = serializers.DictField(child=AttributeDetailSerializer(),allow_empty=False)
    entity_uuid = serializers.UUIDField(required=False)

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        # Check if entity_uuid is provided for the edit operation
        if self.status == Constants.EDIT and not data.get('entity_uuid'):
            raise serializers.ValidationError({
                'entity_uuid': 'This field is required for editing.'
            })
        elif self.status == Constants.ADD and data.get('entity_uuid'):
            raise serializers.ValidationError({
                'entity_uuid': 'UUID should not be provided for creation.'
            })

        return data

class UploadFilesSerializer(serializers.Serializer):
    knowledge_sources = serializers.ListField(child=serializers.FileField(required=False), allow_empty=True, default=[])
    web_url = serializers.CharField(required=False)
    i3s=serializers.ListField(
        child=serializers.BooleanField(),
        allow_empty=True,
        default=[]# Set to True if the list can be empty
    )
    def validate(self, data):
        # Check if both fields are empty
        if not data.get('knowledge_sources') and not data.get('web_url'):
            raise serializers.ValidationError({"knowledge_sources/web_url":"At least one of 'knowledge_sources' or 'web_url' must be provided."})
        return data
class ReUploadFilesSerializer(serializers.Serializer):
    knowledge_source_uuid = serializers.UUIDField()
    knowledge_sources = serializers.ListField(child=serializers.FileField(required=False), allow_empty=True, default=[])
    web_url = serializers.CharField(required=False)
class ListQuestionsSerializer(PagiNationSerializer):
    question_type = serializers.CharField(required=True)
    question = serializers.CharField(required=False)

class AttachmentSerializer(serializers.Serializer):
    url = serializers.CharField()
    name = serializers.ListField(child=serializers.CharField(), required=False)
    type = serializers.ChoiceField(choices=[KnowledgeSourceTypes.IMAGE.value, KnowledgeSourceTypes.VIDEO.value])
    source = serializers.CharField(required=False, allow_null=True)
    start_time = serializers.CharField(required=False)

    def validate(self, data):
        attachment_type = data.get('type')
        if attachment_type == 'video':
            # For videos, `start_time` should be present
            if not data.get('start_time'):
                raise serializers.ValidationError({"start_time": "Start time is required for video attachments."})
        return data

class AddQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()
    author_role_uuid = serializers.UUIDField()
    entity_uuids = serializers.ListField(child=serializers.CharField(required=False), allow_empty=True, default=[])
    attachments = serializers.ListField(child=AttachmentSerializer(), allow_empty=True,
                                        default=[])
    is_draft = serializers.BooleanField(default=False)


class UpdateAnswerSerializer(serializers.Serializer):
    answer_uuid = serializers.UUIDField()
    answer = serializers.CharField()
    entity_uuids = serializers.ListField(child=serializers.CharField(required=False), allow_empty=True, default=[])
    attachments = serializers.ListField(child=AttachmentSerializer(), allow_empty=True,
                                        default=[])
    is_draft = serializers.BooleanField(default=False, required=False)
    draft_uuid = serializers.UUIDField(allow_null=True)
    author_role_uuid = serializers.UUIDField()
    conversation_uuid = serializers.CharField(max_length=45,required=False)
    message_id  = serializers.UUIDField(required=False)
    source = serializers.CharField(required=False)


class VerifyAnswerSerializer(serializers.Serializer):
    answer_uuid = serializers.UUIDField()
    verified = serializers.BooleanField()
    verifier_role_uuid = serializers.UUIDField()
    conversation_uuid = serializers.CharField(max_length=45, required=False)
    message_id = serializers.UUIDField( required=False)
    source = serializers.CharField(required=False)



class UploadImagesSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.FileField(),required=True)


class PageBlockSerializer(serializers.Serializer):
    block_type = serializers.CharField()
    content = serializers.CharField(allow_blank=True, allow_null=True,required=False)
    text_type = serializers.CharField(allow_blank=True, allow_null=True,required=False)
    name = serializers.ListField(child=serializers.CharField(allow_blank=True, allow_null=True), required=False)
    url = serializers.CharField(allow_blank=True, allow_null=True,required=False)
    columns = serializers.ListField(child=serializers.CharField(allow_blank=True, allow_null=True), required=False)
    matrix = serializers.ListField(child=serializers.ListField(child=serializers.CharField(allow_blank=True, allow_null=True)), required=False)

    def validate(self, attrs):
        
        block_type = attrs.get('block_type')
        if block_type == 'text':
            
            text_type = attrs.get('text_type')
            content = attrs.get('content')
            
            if text_type is None or text_type.strip() == "":
                raise serializers.ValidationError("Text type cannot be empty.")
            
            if content is None or content.strip() == "":
                raise serializers.ValidationError("Text content cannot be empty.")

        elif block_type == 'image':
            
            name = attrs.get('name')
            if name is None or len(name) == 0:
                raise serializers.ValidationError("Image name cannot be empty.")
            
            for n in name:
                if n is None or n.strip() == "":
                    raise serializers.ValidationError("Image name cannot be empty.")
            
            content = attrs.get('content')
            if content is None or content.strip() == "":
                raise serializers.ValidationError("Image content cannot be empty.")
            
            url = attrs.get('url')
            if url is None or url.strip() == "":
                raise serializers.ValidationError("Image url cannot be empty.") 
        
        elif block_type == 'table':
            
            name = attrs.get('name')
            if name is None or len(name) == 0:
                raise serializers.ValidationError("Table name cannot be an empty.")
            
            for n in name:
                if n is None or n.strip() == "":
                    raise serializers.ValidationError("Table name cannot be empty.")
            
            columns = attrs.get('columns')
            if columns is None or len(columns) == 0:
                raise serializers.ValidationError("Headers cannot be empty.")
        
            for col in columns:
                if col is None or col.strip() == "":
                    raise serializers.ValidationError("Header cells in the table cannot be empty. Please provide values for all required headers.")
            
            columns = [ col.strip() for col in columns ]
            n = len(columns)
            
            if len(list(set(columns))) != n:
                raise serializers.ValidationError("Duplicate header values are detected in the table. Please ensure each header has a unique name")
        else:
            raise serializers.ValidationError(f"Invalid block type : {block_type}")  
        
        return attrs    


class PageCorrectionSerializer(serializers.Serializer):
    file_uuid = serializers.UUIDField()
    error_uuid = serializers.UUIDField()
    page = serializers.IntegerField(min_value=1)
    blocks = PageBlockSerializer(many=True)


class ProcessCSVSerializer(serializers.Serializer):
    csvfile = serializers.FileField()


class TextBlockSerializer(serializers.Serializer):
    text_type = serializers.CharField()
    content = serializers.CharField(allow_blank=True)


class InsertTextBlockSerializer(serializers.Serializer):
    file_uuid = serializers.CharField()
    previous_block_id = serializers.CharField(allow_null=True)
    block = TextBlockSerializer()


class DeleteBlockSerializer(serializers.Serializer):
    file_uuid = serializers.UUIDField()
    block_id = serializers.UUIDField()


class HeaderBlockSerializer(serializers.Serializer):
    block_id = serializers.CharField()
    block_type = serializers.CharField()
    text_type = serializers.CharField()
    content = serializers.CharField(allow_blank=True)


class UpdateHeaderSerializer(serializers.Serializer):
    file_uuid = serializers.UUIDField()
    blocks = HeaderBlockSerializer(many=True)
    error_uuid = serializers.UUIDField()


class UpdateTableSerializer(serializers.Serializer):
    file_uuid = serializers.UUIDField()
    error_uuid = serializers.UUIDField()
    table_id = serializers.UUIDField()
    columns = serializers.ListField(child=serializers.CharField(allow_blank=True, allow_null=True))
    matrix = serializers.ListField(child=serializers.ListField(child=serializers.CharField(allow_null=True, allow_blank=True)),
                                   required=False)
    
    def validate_columns(self, value):
        
        if len(value) == 0:
            raise serializers.ValidationError("Headers cannot be empty.")
        
        if any(col is None or col.strip() == "" for col in value):
            raise serializers.ValidationError("Header cells in the table cannot be empty. Please provide values for all required headers.")
        
        value = [ col.strip() for col in value ]
        
        n = len(value)
        if len(list(set(value))) != n:
            raise serializers.ValidationError("Duplicate header values are detected in the table. Please ensure each header has a unique name")
            
        return value


class VideoTranscriptionSerializer(serializers.Serializer):
    file_uuid = serializers.UUIDField()
    error_uuid = serializers.UUIDField()
    transcription = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(allow_blank=True, required=False)), 
        default=[]  # Allow empty list initially
    )

    def validate_transcription(self, transcription):
        # Additional validation for each individual card in the transcription
        for index, card in enumerate(transcription):
            if not card.get('text'):
                raise serializers.ValidationError(
                    f"Record{index+1} has an empty transcript field. Please provide a transcript for that record."
                )

        return transcription
      

class ChatSessionSerializer(serializers.Serializer):
    application_uuid = serializers.UUIDField()


class UserQuerySerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    query = serializers.CharField()
    regenerate = serializers.BooleanField(required=False)
    cache = serializers.BooleanField(required=False)


class FeedbackSerializer(serializers.Serializer):
    answer_uuid = serializers.UUIDField()
    feedback = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    dislike = serializers.BooleanField()
    conversation_uuid = serializers.CharField(max_length=45, required=False)
    message_id = serializers.UUIDField(required=False)
    source = serializers.CharField(required=False)


class DriveFileSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    file_id = serializers.CharField()
    mime_type = serializers.CharField(required=False)


class DriveUploadSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    files = serializers.ListField(child=DriveFileSerializer(), min_length=1)
    file_upload_source = serializers.ChoiceField(choices=KnowledgeSourceConstants.FILE_UPLOAD_SOURCE_CHOICES, required=True)
    send_url=serializers.BooleanField(required=False)

class GenerateQASerializer(serializers.Serializer):
    knowledge_sources = serializers.ListField(child=serializers.UUIDField(required=False), min_length=1)
    author_role_uuid = serializers.UUIDField()

class DepartmentSerializer(serializers.Serializer):
    department_id = serializers.CharField(max_length=45)
    department_name = serializers.CharField(max_length=255)


class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=45)
    user_name = serializers.CharField(max_length=255)


class UserDetailsSerializer(serializers.Serializer):
    user_name = serializers.CharField()
    user_type = serializers.CharField()
    user_uuid = serializers.UUIDField(allow_null=True)
    user_profile_picture = serializers.CharField(allow_null=True)


class CustomerSerializer(serializers.Serializer):
    cust_name = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    cust_uuid = serializers.CharField(default=str(uuid.uuid4()), max_length=45)
    purchased_plan = serializers.CharField(max_length=45, required=False, allow_null=True)
    primary_contact = serializers.CharField(max_length=255, required=False, allow_null=True)
    secondary_contact = serializers.CharField(max_length=255, required=False, allow_null=True)
    address = serializers.CharField(max_length=255, required=False, allow_null=True)
    billing_address = serializers.CharField(max_length=255, required=False, allow_null=True)
    customer_details_json = serializers.JSONField(required=False, allow_null=True)
    status = serializers.BooleanField(default=True)
    created_ts = serializers.DateTimeField(default=datetime.now)
    updated_ts = serializers.DateTimeField(default=datetime.now)
    created_by = serializers.CharField(max_length=255, required=False, allow_null=True)
    updated_by = serializers.CharField(max_length=255, required=False, allow_null=True)


class ApplicationSerializer(serializers.Serializer):
    application_uuid = serializers.CharField(max_length=45)
    application_name = serializers.CharField(max_length=255)
    application_url = serializers.CharField(max_length=255)
    scope_end_point = serializers.CharField(max_length=50)
    description = serializers.CharField(allow_blank=True, required=False)
    status = serializers.BooleanField(required=False)
    created_ts = serializers.DateTimeField(required=False)
    updated_ts = serializers.DateTimeField(required=False)
    created_by = serializers.CharField(max_length=255, allow_blank=True, required=False)
    updated_by = serializers.CharField(max_length=255, allow_blank=True, required=False)


class RoleSerializer(serializers.Serializer):
    role_uuid = serializers.CharField(max_length=45)
    role_name = serializers.CharField(max_length=255)
    role_details_json = serializers.CharField(allow_blank=True, required=False)
    application_uuid = serializers.CharField(max_length=45, allow_blank=True, required=False)
    customer_uuid = serializers.CharField(max_length=45, allow_blank=True, required=False)
    description = serializers.CharField(allow_blank=True, required=False)

class DimensionResultSerializer(serializers.Serializer):
    result = serializers.ListField(
        child=serializers.CharField()  # List of dimension names (strings)
    )

class CaptchaSerializer(serializers.Serializer):
    captcha_image = serializers.CharField()
    encode_text = serializers.CharField()


def get_error_messages(errors):
    
    msgs = []
    if isinstance(errors, list):
        for error in errors:
            msgs.extend(get_error_messages(error))
    
    elif isinstance(errors, dict):
        for _, error in errors.items():
            msgs.extend(get_error_messages(error))
    
    elif isinstance(errors, str):
        msgs.append(str(errors))
    
    return msgs

class ConversationHistorySerializer(serializers.Serializer):
    message_uuid = serializers.UUIDField()
    source = serializers.CharField()
    message_marker = serializers.CharField()
    message_text = serializers.CharField()
    media_url = serializers.ListField(child=serializers.URLField(), required=False)
    parent_message_uuid = serializers.UUIDField(allow_null=True)
    created_at = serializers.DateTimeField()
    dimension_action_json = serializers.JSONField()
    message_type = serializers.CharField()
    is_knowledge_base = serializers.BooleanField()
    regenerate_level = serializers.IntegerField()
    cache = serializers.BooleanField()
    verification_details = serializers.JSONField()
    dislike = serializers.BooleanField()
    answer_uuid = serializers.UUIDField(allow_null=True)
    condensed_query = serializers.CharField(allow_null=True)
    question_uuid = serializers.UUIDField(allow_null=True)
    regenerate = serializers.BooleanField()

class SummarySerializer(serializers.Serializer):
    intents = serializers.ListField(child=serializers.CharField(), required=False)
    sentiment = serializers.CharField(allow_null=True)
    ticket_id = serializers.CharField()
    summary = serializers.CharField()
    user_details = UserDetailsSerializer()

class AttributeSerializer(serializers.Serializer):
    attributes = serializers.DictField(
        child=serializers.CharField(required=True),
        allow_empty=False  # Ensure the dictionary is not empty
    )
    entity_name = serializers.CharField(required=True)

class AssignEntitySerializer(serializers.Serializer):
    knowledge_source_uuid = serializers.UUIDField(required=True)
    entity_uuid = serializers.UUIDField(required=True)
    entity_assignment_status = serializers.ChoiceField(choices=EntityConstants.ASSIGN_UNASSIGN_CHOICES, required=True)
    attribute_details_json = AttributeSerializer(required=False) 
    prev_entity_uuid = serializers.UUIDField(required=False)
    
    def validate(self, data):
        entity_assignment_status = data.get('entity_assignment_status')
        if entity_assignment_status == EntityConstants.ASSIGN_UNASSIGN_CHOICES[0]:
            if data.get('prev_entity_uuid') is None:
                raise serializers.ValidationError({
                    'prev_entity_uuid': 'This field is required.'
                })
            if data.get('attribute_details_json') is None:
                raise serializers.ValidationError({
                    'attribute_details_json': 'This field is required.'
                })
        return data

class ErrorPagiNationSerializer(PagiNationSerializer):
    knowledge_source_uuid = serializers.UUIDField()
    error_type=serializers.CharField(required=False)

class KnowledgeSourceNamesSerializer(serializers.Serializer):
    knowledge_source_names = serializers.ListField(child=serializers.CharField(), min_length=1)
    knowledge_source_uuid=serializers.UUIDField(required=False)

class KnowledgeSourceSerializer(PagiNationSerializer):
    knowledge_source_name=serializers.CharField(required=False)   

class RequirableBooleanField(serializers.BooleanField):
    default_empty_html = serializers.empty

class EntityPaginationSerializer(PagiNationSerializer):
    only_attribute_keys=RequirableBooleanField(required=True)
    entity_name=serializers.CharField(required=False)
    entity_uuid=serializers.UUIDField(required=False)


class RelevantChunksRequestSerializer(serializers.Serializer):
    
    query = serializers.CharField(required=True)
    top_n = serializers.IntegerField(required=True)
    entity_filter = serializers.DictField(required=True, allow_null=True)
    sort_by_sequence = serializers.BooleanField(required=False, default=True)
    metadata_keys = serializers.ListField(required=False, default=list())
    
    def validate_entity_filter(self, data: Union[dict, None]):
        
        print(f'In serializer :: {data}')
        
        if data is None:
            return data
        
        for entity_name, attributes in data.items():
            
            if not isinstance(entity_name, str):
                raise serializers.ValidationError(f"keys of entity filter should be str not {type(entity_name)}")
            
            if not isinstance(attributes, dict):
                raise serializers.ValidationError(f"value of entity filter should be dict not {type(attributes)}")
            
            for name, value in attributes.items():
                
                if not isinstance(name, str):
                    raise serializers.ValidationError(f"keys of attributes should be str not {type(name)}")
                
                if not isinstance(value, str):
                    raise serializers.ValidationError(f"value of attributes should be str not {type(value)}")
                
        return data

class ReferenceChunkSerializer(serializers.Serializer):
    
    chunk_id = serializers.CharField(required=True)
    sort_by_sequence = serializers.BooleanField(required=False, default=True)
    metadata_keys = serializers.ListField(required=False, default=list())


class NeighbouringChunkSerializer(serializers.Serializer):
    
    chunk_ids = serializers.ListField(required=True, child=serializers.CharField())
    sort_by_sequence = serializers.BooleanField(required=False, default=True)
    metadata_keys = serializers.ListField(required=False, default=list())

class UpdateKnowledgeSourceInternalJsonSerializer(serializers.Serializer):
    knowledge_source_uuid = serializers.UUIDField(required=True)
    pages = serializers.ListField(
        child=DictField(required=True),
        required=True,
        allow_empty=False,
    )

    def validate_pages(self, data):
        print(f'In serializer :: {data}')

        if data is None:
            raise serializers.ValidationError(f"`pages` field cannot be null")
        if not isinstance(data, list):
            raise serializers.ValidationError(f"The `pages` field must be a list.")
        for element in data:
            if not isinstance(element, dict):
                raise serializers.ValidationError("All items in the `pages` field must be objects/dictionaries.")
            for key, value in element.items():
                if not isinstance(value, dict):
                    raise serializers.ValidationError(f"values of every pages objects must be dict not {type(value)}")

        return data


class EditableInternalJsonSerializer(serializers.Serializer):
    knowledge_source_uuid = serializers.UUIDField(required=True)
    blocks = serializers.DictField(required=True)

    # def validate_blocks(self, blocks):
    #
    #     if blocks is None:
    #         raise serializers.ValidationError(f"`blocks` field cannot be null")
    #     if not isinstance(blocks, dict):
    #         raise serializers.ValidationError(f"The `blocks` field must be a dict.")
    #     for key, value_list in blocks.items():
    #         if not isinstance(value_list, list):
    #             raise serializers.ValidationError(f"page::{key} value must be list.")
    #         for index, single_block in enumerate(blocks):
    #             if not isinstance(single_block, dict):
    #                 raise serializers.ValidationError(f"block:{index+1} of page:{key} is not dict")
    #             if "content_type" not in single_block:
    #                 raise serializers.ValidationError(f"block:{index+1} of page:{key} should have content_type field")
    #             if "page" not in single_block or single_block.get("block_id") is None:
    #                 raise serializers.ValidationError(f"block:{index + 1} of page:{key} should have page field")
    #             if "block_id" not in single_block or single_block.get("block_id") is None:
    #                 raise serializers.ValidationError(f"block:{index + 1} of page:{key} should have block_id field and it should be uuid value")
    #
    #     return blocks


