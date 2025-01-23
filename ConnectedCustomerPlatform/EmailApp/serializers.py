from rest_framework import serializers

from ConnectedCustomerPlatform.exceptions import CustomException
from datetime import datetime


from rest_framework import status
from DatabaseApp.models import Email, EmailConversation, EmailInfoDetail
from EmailApp.constant.constants import DateFormats
from EmailApp.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from EmailApp.utils import validate_start_and_end_date

class EmailConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConversation
        fields = '__all__'

class EmailInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailInfoDetail
        fields = '__all__'


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'





class ResponseConfigurationRequestPayloadSerializer(serializers.Serializer):
    """
    Serializer for the request data to save response configurations.
    """
    intent = serializers.CharField(required=True)
    sub_intent = serializers.CharField(required=True)
    sentiment = serializers.CharField(required=True)
    response_config_uuid = serializers.CharField(required=True,allow_null=True)
    is_default = serializers.BooleanField(required=True)
    response_file = serializers.FileField(required=True)
    textToShow=serializers.CharField(required=True)


class PaginationParamsSerializer(serializers.Serializer):
    """
    Serializer for the request data to save pagination params
    """
    total_entry_per_page = serializers.IntegerField(required=True)
    page_number = serializers.IntegerField(required=True)

class EmailConversationSerializer(serializers.Serializer):
    start_date = serializers.CharField(required=True)
    end_date = serializers.CharField(required=True)
    email_conversation_flow_status = serializers.CharField(required=True)
    page_number = serializers.IntegerField(default=1)
    total_entry_per_page = serializers.IntegerField(default=10)
    

    def validate(self, data):

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        start_date, end_date = validate_start_and_end_date(start_date=start_date,end_date=end_date)
        
        if start_date > end_date:
            raise InvalidValueProvidedException(ErrorMessages.START_DATE_GREATER_THAN_END_DATE)
        
        data['start_date'], data['end_date'] = start_date, end_date

        return data
    
class RecipientSerializer(serializers.Serializer):
    name = serializers.CharField()  # Name is a string
    email = serializers.EmailField()

class DraftMailSerializer(serializers.Serializer):
    email_conversation_uuid = serializers.CharField(required=False, allow_blank=True)
    from_email_id = serializers.EmailField(required=True)
    in_reply_to = serializers.CharField(required=False, allow_blank=True)
    to = serializers.ListField(
        child=RecipientSerializer(), required=True
    )
    cc = serializers.ListField(
        child=RecipientSerializer(), required=False, allow_empty=True
    )
    bcc = serializers.ListField(
        child=RecipientSerializer(), required=False, allow_empty=True
    )
    subject = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
    attachments = serializers.ListField(child=serializers.DictField(), required=False, allow_empty = True)

    
class SendMailSerializer(serializers.Serializer):
    send = serializers.BooleanField(required=False)
    email_uuid = serializers.CharField(required=False, allow_blank=True)
    from_email_id = serializers.EmailField(required=True)
    in_reply_to = serializers.CharField(required=False, allow_blank=True)
    to = serializers.ListField(
        child=RecipientSerializer(), required=True
    )
    cc = serializers.ListField(
        child=RecipientSerializer(), required=False, allow_empty=True
    )
    bcc = serializers.ListField(
        child=RecipientSerializer(), required=False, allow_empty=True
    )
    subject = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
    attachments = serializers.ListField(child=serializers.DictField(), required=False, allow_empty = True)#TODO change it to list of dicts
    remove_attachments = serializers.ListField(child=serializers.CharField(), required=False, allow_empty = True)
