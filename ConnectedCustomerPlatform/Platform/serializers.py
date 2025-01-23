from importlib.metadata import requires

from rest_framework import serializers

from DatabaseApp.models import UserEmailSetting, ChatConfiguration, DimensionType, DimensionTypeCustomerApplicationMapping, DimensionCustomerApplicationMapping, PromptTemplate, Prompt, Dimension, \
    CustomerClient, ClientUser, EmailServer, EmailServerCustomerApplicationMapping, PromptCategory, LLMConfiguration, LLMProviderMetaData, Ticket
from EmailApp.utils import validate_start_and_end_date

from Platform.dataclass import EmailDetails, DimensionTypeDetailsJson, DimensionDetailsJson
from ConnectedCustomerPlatform.exceptions import CustomException
from rest_framework import status
from Platform.constant.error_messages import ErrorMessages

class PromptTemplateSerializer(serializers.Serializer):
    mapping_uuid = serializers.CharField(required=False)
    prompt_template_description = serializers.CharField(required=True)
    prompt_template_uuid = serializers.CharField(required=False)
    prompt_template_name = serializers.CharField(required=True)
    prompt_template_details_json = serializers.JSONField(required=True)
    prompt_category_uuid = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        # Check if prompt_uuid is provided for the edit operation
        if self.status == "Edit":
            if not data.get('mapping_uuid'):
                raise serializers.ValidationError({
                    'prompt_uuid': 'This field is required for editing.'
                })
        elif self.status == "Add":
            if data.get('mapping_uuid'):
                raise serializers.ValidationError({
                    'prompt_uuid': 'UUID should not be provided for creation.'
                })

        return data


class PromptTemplateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = '__all__'


class PromptSerializer(serializers.Serializer):
    prompt_uuid = serializers.UUIDField(required=False)
    prompt_name = serializers.CharField(required=True)
    prompt_category_uuid = serializers.CharField(required=True)
    prompt_details_json = serializers.JSONField(required=True)

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        # Check if prompt_uuid is provided for the edit operation
        if self.status == "Edit":
            if not data.get('prompt_uuid'):
                raise serializers.ValidationError({
                    'prompt_uuid': 'This field is required for editing.'
                })
        elif self.status == "Add":
            if data.get('prompt_uuid'):
                raise serializers.ValidationError({
                    'prompt_uuid': 'UUID should not be provided for creation.'
                })

        return data


class PromptModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = '__all__'


class DimensionTypeSerializer(serializers.Serializer):
    mapping_uuid = serializers.UUIDField(required=False)
    dimension_type_uuid = serializers.UUIDField(required=False)
    dimension_type_name = serializers.CharField(required=True)
    dimension_type_details_json = serializers.JSONField(required=False, allow_null=True)
    status = serializers.BooleanField(default=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_default = serializers.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        # Get 'is_edit' flag from the serializer initialization
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # If it's an edit operation, make some fields required
        if is_edit:
            self.fields['status'].required = True

    @staticmethod
    def validate_dimension_type_details_json(value):
        if value is None:
            return value

        try:
            details = DimensionTypeDetailsJson.create(value)
        except (TypeError, ValueError) as e:
            raise serializers.ValidationError(str(e))

        return details

class DimensionTypeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimensionType
        fields = '__all__'


class DimensionTypeCAMModelSerializer(serializers.ModelSerializer):
    dimension_type_name = serializers.CharField(source='dimension_type_uuid.dimension_type_name')
    is_default = serializers.BooleanField(source='dimension_type_uuid.is_default')

    class Meta:
        model = DimensionTypeCustomerApplicationMapping
        fields = '__all__'


class DimensionTypeStatusSerializer(serializers.Serializer):
    dimension_type_uuid = serializers.CharField(required=True)
    status = serializers.BooleanField(required=True)


class DimensionSerializer(serializers.Serializer):
    dimension_uuid = serializers.UUIDField(required=False, allow_null=True)
    mapping_uuid = serializers.UUIDField(required=False, allow_null=True)
    dimension_type_uuid = serializers.UUIDField(required=True)
    dimension_names = serializers.ListField(
        child=serializers.CharField(min_length=1, allow_blank=False),
        required=True, allow_empty=False
    )
    dimension_name = serializers.CharField(required=False)
    dimension_details_json = serializers.JSONField(required=False, allow_null=True)
    parent_dimension_name = serializers.CharField(required=False)
    parent_dimension_uuid = serializers.UUIDField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    utterances = serializers.ListField(required=False)
    status = serializers.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        # Get 'is_edit' flag from the serializer initialization
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # If it's an edit operation, make some fields required
        if is_edit:
            self.fields['mapping_uuid'].required = True
            self.fields['dimension_name'].required = True
            self.fields['dimension_names'].required = False
            self.fields['dimension_names'].allow_empty = True

    @staticmethod
    def validate_dimension_details_json(value):
        if value is None:
            return value

        try:
            details = DimensionDetailsJson.create(value)
        except (TypeError, ValueError) as e:
            raise serializers.ValidationError(str(e))

        return details

class DimensionCAMModelSerializer(serializers.ModelSerializer):
    dimension_name = serializers.CharField(source='dimension_uuid.dimension_name')
    dimension_type_uuid = serializers.CharField(source='dimension_uuid.dimension_type_uuid_id')
    is_default = serializers.BooleanField(source='dimension_uuid.is_default', required=False)
    parent_dimension_name = serializers.CharField(source='parent_dimension_uuid.dimension_name', allow_null=True)

    class Meta:
        model = DimensionCustomerApplicationMapping
        fields = '__all__'

    def get_dimension_type_name(self, obj):
        return obj.dimension_uuid.dimension_type_uuid.dimension_type_name

    def __init__(self, *args, **kwargs):
        # Call the parent constructor
        super(DimensionCAMModelSerializer, self).__init__(*args, **kwargs)

        # Check if the context has a key 'include_dimension_type_name'
        if self.context.get('include_dimension_type_name'):
            # If the context has the flag, dynamically add the 'dimension_type_name'
            self.fields['dimension_type_name'] = serializers.SerializerMethodField()


class DimensionsScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dimension
        fields = ('dimension_uuid', 'dimension_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'label': representation['dimension_name'],
            'value': representation['dimension_uuid']
        }


class CustomerClientSerializer(serializers.Serializer):
    customer_client_uuid = serializers.UUIDField(required=False)
    customer_client_name = serializers.CharField(required=True)
    customer_client_geography_uuid = serializers.UUIDField(required=False)
    customer_client_domain_name = serializers.CharField(required=False)
    customer_client_emails = serializers.ListField(child=serializers.EmailField(), required=True, allow_empty=False)
    customer_client_address = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        # Get 'is_edit' flag from the serializer initialization
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # If it's an edit operation, make some fields required
        if is_edit:
            self.fields['customer_client_uuid'].required = True

    def validate_customer_client_emails(self, emails):
        # Get the allowed domain from the customer_client_domain_name field
        domain_name = self.initial_data.get('customer_client_domain_name')

        if emails:
            # Check if all emails are unique
            if len(emails) != len(set(emails)):
                raise serializers.ValidationError(ErrorMessages.DUPLICATES_NOT_ALLOWED)

            # Extract domains from emails
            domains = {email.split('@')[1] for email in emails}

            # Check if the domain of emails matches the customer_client_domain_name
            if len(domains) > 1 or (domain_name and domain_name not in domains):
                raise serializers.ValidationError(f"All emails must have the domain: {domain_name}.")

        return emails

class ClientUserSerializer(serializers.Serializer):
    client_user_uuid = serializers.UUIDField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email_id = serializers.EmailField(required=True)
    geography_uuid = serializers.UUIDField(required=True)
    user_info_json = serializers.JSONField(required=True)
    customer_client_uuid = serializers.UUIDField(required=True)
    def __init__(self, *args, **kwargs):
        # Get 'is_edit' flag from the serializer initialization
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # If it's an edit operation, make some fields required
        if is_edit:
            self.fields['client_user_uuid'].required = True


class CustomerClientModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerClient
        fields = '__all__'


class ClientUsersModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = '__all__'


class CustomerClientsScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerClient
        fields = ('customer_client_uuid', 'customer_client_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'label': representation['customer_client_name'],
            'value': representation['customer_client_uuid']
        }


# Email Server Serializers
class EmailServerSerializer(serializers.Serializer):
    mapping_uuid = serializers.UUIDField(required=False, allow_null=True)
    email_server_uuid = serializers.UUIDField(required=False)
    server_type = serializers.CharField(required=True)
    server_url = serializers.CharField(required=True)
    email_provider_name = serializers.CharField(required=True)
    port = serializers.CharField(required=True)
    is_ssl_enabled = serializers.BooleanField(default=True)
    sync_time_interval = serializers.IntegerField(default=5, allow_null=True)

    def __init__(self, *args, **kwargs):
        # Get 'is_edit' flag from the serializer initialization
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # If it's an edit operation, make some fields required
        if is_edit:
            self.fields['mapping_uuid'].required = True
            self.fields['email_server_uuid'].required = True


class EmailServerOutlookSerializer(serializers.Serializer):
    mapping_uuid = serializers.UUIDField(required=False, allow_null=True)  # Required only for update
    sync_time_interval = serializers.IntegerField(default=5, allow_null=True)
    microsoft_client_id = serializers.CharField(required=True)
    microsoft_tenant_id = serializers.CharField(required=True)
    secret_created_ts = serializers.IntegerField(required=True)
    secret_expiration_time = serializers.IntegerField(required=True)
    microsoft_client_secret = serializers.CharField(required=True)

class EmailServerModelSerializer(serializers.ModelSerializer):
    is_ssl_enabled = serializers.BooleanField(default=True)
    class Meta:
        model = EmailServer
        fields = '__all__'


class EmailServerCAMModelSerializer(serializers.ModelSerializer):
    server_type = serializers.CharField(source='email_server_uuid.server_type')
    server_url = serializers.CharField(source='email_server_uuid.server_url')
    email_provider_name = serializers.CharField(source='email_server_uuid.email_provider_name')
    port = serializers.CharField(source='email_server_uuid.port')
    is_default = serializers.BooleanField(source='email_server_uuid.is_default')

    class Meta:
        model = EmailServerCustomerApplicationMapping
        fields = '__all__'


# User Email Settings Serializers
class UserEmailSettingSerializer(serializers.Serializer):
    user_email_uuid = serializers.UUIDField(required=False)
    email_id = serializers.EmailField(max_length=255, required=True)
    encrypted_password = serializers.CharField(max_length=255, allow_null=True, required=False)
    email_type = serializers.CharField(max_length=255, required=True)
    cust_email_provider = serializers.CharField(max_length=255, required=False, allow_null=True)
    email_details_json = serializers.JSONField(allow_null=True, required=False)
    is_primary_sender_address = serializers.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        # Get 'is_edit' flag from the serializer initialization
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # If it's an edit operation, make user_email_uuid required
        if is_edit:
            self.fields['user_email_uuid'].required = True
            self.fields['is_primary_sender_address'].required = True
            self.fields['cust_email_provider'].required = True

    @staticmethod
    def validate_email_details_json(value):
        if value is None:
            return value

        try:
            details = EmailDetails.create(value)
        except (TypeError, ValueError) as e:
            raise serializers.ValidationError(str(e))

        return details


class UserEmailSettingModelSerializer(serializers.ModelSerializer):
    application_uuid = serializers.CharField(source='application_uuid.application_uuid')
    customer_uuid = serializers.CharField(source='customer_uuid.cust_uuid')

    class Meta:
        model = UserEmailSetting
        exclude = ('encrypted_password',)


class TestConnectionSerializer(serializers.Serializer):
    server_url = serializers.CharField(max_length=255)
    port = serializers.IntegerField()
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255, required=False, allow_null=True)
    is_ssl_enabled = serializers.BooleanField(default=True)
    email_uuid = serializers.CharField(max_length=255, required=False, allow_null=True)
    is_encrypted = serializers.BooleanField(default=False)

class TestConnectionSerializerOutlook(serializers.Serializer):
    microsoft_client_id = serializers.UUIDField(required=True, allow_null=False)
    microsoft_tenant_id = serializers.UUIDField(required=True, allow_null=False)
    user_email = serializers.EmailField()
    microsoft_client_secret = serializers.CharField(max_length=256, required=True, allow_null=False)

class EmailExtractorSerializer(serializers.Serializer):
    template_uuid = serializers.CharField(required=False, default=None)
    template_name = serializers.CharField(required=True)
    template_description = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    dimension_details_json = serializers.JSONField(required=True)
    template_details_json = serializers.JSONField(required=True)

    def validate_json_object(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(ErrorMessages.VALID_JSON_OBJECT)
        return value

    def validate_dimension_details_json(self, value):
        return self.validate_json_object(value)

    def validate_template_details_json(self, value):
        return self.validate_json_object(value)


class CustomResponseSerializer(serializers.Serializer):
    result = serializers.JSONField(required=False)
    status = serializers.BooleanField(required=True)
    code = serializers.IntegerField(required=True)


class ChatConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatConfiguration
        fields = '__all__'



class ActiveChatConfigurationSerializer(serializers.Serializer):
    customer_uuid = serializers.UUIDField(required=True)
    application_uuid = serializers.UUIDField(required=True)

class ValidateChatConfigurationSerializer(serializers.Serializer):
    chat_configuration_type = serializers.CharField(max_length=225, required=True)
    chat_configuration_name = serializers.CharField(max_length=225, required=True)
    chat_configuration_provider = serializers.CharField(max_length=225, required=True)

    def validate_chat_configuration_provider(self, value):
        # Check if provider is 'web'
        if value.lower() != "web":
            raise serializers.ValidationError("chat_configuration_provider must be 'web'.")
        return value


class PromptCategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptCategory
        fields = '__all__'


class LLMConfigurationSerializer(serializers.Serializer):
    llm_configuration_uuid = serializers.UUIDField(required=False)
    llm_configuration_name = serializers.CharField(required=True)
    llm_configuration_details_json = serializers.JSONField(required=True)
    llm_provider_uuid = serializers.UUIDField(required=True)

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        # Check if llm_configuration_uuid is provided for the edit operation
        if self.status == "Edit":
            if not data.get('llm_configuration_uuid'):
                raise serializers.ValidationError({
                    'llm_configuration_uuid': 'This field is required for editing.'
                })
        elif self.status == "Add":
            if data.get('llm_configuration_uuid'):
                raise serializers.ValidationError({
                    'llm_configuration_uuid': 'UUID should not be provided for creation.'
                })

        return data
    
class AssignOrganizationSerializer(serializers.Serializer):
    llm_configuration_uuid = serializers.UUIDField(required=True)
    organizations = serializers.ListField(child=serializers.UUIDField(), required=False)
    
class VerifyLLMConfigurationSerializer(serializers.Serializer):
    llm_configuration_details_json = serializers.JSONField(required=True)
class LLMConfigurationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMConfiguration
        fields = '__all__'


class LLMProvideMetaDataModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMProviderMetaData
        fields = '__all__'


class LLMConfigurationChannelMappingSerializer(serializers.Serializer):
    llm_configuration_uuid = serializers.CharField(required=True)
    channel_uuid = serializers.CharField(required=True)

    def create(self, validated_data):
        pass


class ListOrStrField(serializers.ListField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = [data]
        return super().to_internal_value(data)

class TicketParamsSerializer(serializers.Serializer):
    start_date = serializers.CharField(required=True)
    end_date = serializers.CharField()
    page_number = serializers.IntegerField(default=1)
    total_entry_per_page = serializers.IntegerField(default=10)
    status = ListOrStrField(child=serializers.CharField(), required=False)
    channels = ListOrStrField(child=serializers.CharField(), required=False)
    client_names = ListOrStrField(child=serializers.CharField(), required=False)
    email_ids = ListOrStrField(child=serializers.CharField(), required=False)
    intents = ListOrStrField(child=serializers.CharField(), required=False)

    def validate(self, data):

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date is None:
            raise CustomException(ErrorMessages.START_DATE_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        if end_date is None:
            raise CustomException(ErrorMessages.END_DATE_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        
        start_date, end_date = validate_start_and_end_date(start_date=start_date,end_date=end_date)

        data['start_date'], data['end_date'] = start_date, end_date

        return data

class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = '__all__'


class CustomerClientTierMappingSerializer(serializers.Serializer):
    mapping_uuid = serializers.UUIDField(required=False)
    tier_mapping_uuid = serializers.UUIDField(required=True)
    customer_client_uuid = serializers.UUIDField(required=True)
    extractor_template_details_json = serializers.JSONField(required=True,allow_null=True)

    def validate_extractor_template_details_json(self, value):
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError("extractor_template_details_json must be a valid JSON object or null.")
        return value

    def __init__(self, *args, **kwargs):
        # Get 'is_edit' flag from the serializer initialization
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # If it's an edit operation, make some fields required
        if is_edit:
            self.fields['mapping_uuid'].required = True

class PagiNationSerializer(serializers.Serializer):
    page_number = serializers.IntegerField()
    total_entry_per_page = serializers.IntegerField()