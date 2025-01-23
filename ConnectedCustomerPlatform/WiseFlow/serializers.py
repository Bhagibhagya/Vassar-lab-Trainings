from rest_framework import serializers

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import WiseflowEntity


class EntityExampleSerializer(serializers.Serializer):
    """
    Serializer for individual entity example items.
    """
    input = serializers.CharField(required=True,allow_blank=True,allow_null=False)
    output = serializers.CharField(required=True,allow_blank=True,allow_null=False)

class EntityExamplesRequestPayloadSerializer(serializers.Serializer):
    """
    Serializer for the request data to save examples.
    """
    entity_name = serializers.CharField(required=True)
    entity_uuid = serializers.CharField(required=True)
    examples = serializers.ListSerializer(
        child=EntityExampleSerializer(),
        allow_empty=False
    )
    is_default = serializers.BooleanField(required=True)

class ChatHistorySerializer(serializers.Serializer):
    source = serializers.ChoiceField(choices=["user","USER","User","AI","ai","Ai"], required=True)
    message = serializers.CharField(required=True)

class TestEntityPromptRequestPayloadSerializer(serializers.Serializer):
    """
        Serializer for the request data to test entity prompt.
        """
    entity_uuid = serializers.CharField(required=True)
    chat_history = serializers.ListSerializer(
        child=ChatHistorySerializer(),
        allow_empty=True,
        allow_null=True
    )
    previous_value_of_entity = serializers.CharField(allow_null=True,allow_blank=True)
    user_query = serializers.CharField(allow_null=False)

class WiseflowEntityRequestPayloadSerializer(serializers.Serializer):
    """ serializer for entity creation """
    entity_name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    parent_entity_name = serializers.ChoiceField(choices=["list", "prompt", "regex"], required=True)
    description = serializers.CharField(required=False, allow_null=False, allow_blank=False)
    output_format = serializers.JSONField(required=False)
    instructions = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    examples = serializers.ListSerializer(
        child=EntityExampleSerializer(),
        allow_empty=True,
        required=False
    )
    list_items = serializers.ListField(required=False, child=serializers.CharField())
    pattern = serializers.CharField(required=False)
    prompt = serializers.CharField(required=False)
    parent_entity_uuid = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    def validate(self, data):
        parent_entity_name = data.get('parent_entity_name')
        list_items = data.get('list_items')
        pattern = data.get('pattern')
        if parent_entity_name == "list":
            if not isinstance(list_items, list):
                raise CustomException(f"'list_items'  field should be list")
        elif parent_entity_name == "regex":
            if pattern is None or len(pattern) <= 0:
                raise CustomException(f"'pattern' field should not be null or empty")
        return data


class GetEntitiesRequestPayloadSerializer(serializers.Serializer):
    """ serializer for fetching entities """
    ownership = serializers.ChoiceField(choices=[WiseflowEntity.OwnershipEnum.SYSTEM, WiseflowEntity.OwnershipEnum.CUSTOM], required=True)
    page_number = serializers.IntegerField(default=1)
    total_entry_per_page = serializers.IntegerField(default=10)


class EntityEditExampleSerializer(EntityExampleSerializer):
    id = serializers.CharField(required=True, allow_null=False, allow_blank=False)


class EditEntityPayloadSerializer(serializers.Serializer):
    """ serializer for updating entity """
    entity_uuid = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    entity_name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    description = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    instructions = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    output_format = serializers.JSONField(required=False)
    pattern = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    parent_entity_name = serializers.ChoiceField(choices=["list", "prompt", "regex"], required=True)
    edit_list_item = serializers.DictField(required=False)
    add_list_item = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    delete_list_item = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    add_example = serializers.ListField(
        child=EntityExampleSerializer(),
        allow_empty=True,
        required=False
    )
    edit_example = serializers.ListField(
        child=EntityEditExampleSerializer(),
        allow_empty=True,
        required=False
    )
    delete_example = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)

    def validate(self, data):
        parent_entity_name = data.get("parent_entity_name")
        pattern = data.get("pattern")
        if parent_entity_name == "regex":
            if pattern is None or len(pattern) <= 0:
                raise CustomException(f"'pattern' field can't be null or empty")
        return data

class IntentClassificationInputSerializer(serializers.Serializer):
    """
    Serializer for input to the intent classification process.
    """
    user_input = serializers.CharField(required=True)
    conversation_history = serializers.ListSerializer(
        child=ChatHistorySerializer(),
        allow_empty=True,
        allow_null=True,
        required=False
    )


