# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid

from django.db import models
from datetime import datetime


class ActionFlowConfig(models.Model):
    afc_uuid = models.CharField(primary_key=True, max_length=45)
    action_flow_uuid = models.ForeignKey('ActionFlows', models.DO_NOTHING, db_column='action_flow_uuid')
    dimensions_details_json = models.JSONField(blank=True, null=True)
    customer_uuid = models.CharField(max_length=45)
    status = models.BooleanField(blank=True, null=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."action_flow_config'


class ActionFlows(models.Model):
    action_flow_uuid = models.CharField(primary_key=True, max_length=45)
    action_flow_name = models.CharField(max_length=255)
    channel_type_uuid = models.CharField(max_length=45, blank=True, null=True)
    application_uuid = models.CharField(max_length=45, null=False)
    dimension_details_json = models.JSONField(blank=True, null=True)
    customer_uuid = models.CharField(max_length=45, null=False)
    status = models.BooleanField(blank=True, null=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."action_flows'

    def save(self, *args, **kwargs):
        self.updated_ts = int(datetime.now().timestamp())  # Update the updated_ts field with current timestamp
        super(ActionFlows, self).save(*args, **kwargs)


class ClientEscalationsConfig(models.Model):
    client_escalation_uuid = models.CharField(primary_key=True, max_length=45)
    dimensions_details_json = models.JSONField(blank=True, null=True)
    escalation_rule_uuid = models.ForeignKey('EscalationRules', models.DO_NOTHING, db_column='escalation_rule_uuid',
                                             blank=True, null=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."client_escalations_config'


class ClientUsers(models.Model):
    client_user_uuid = models.CharField(primary_key=True, max_length=45)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_id = models.CharField(unique=True, max_length=255)
    dimension_uuid = models.ForeignKey('Dimensions', models.DO_NOTHING, db_column='dimension_uuid')
    customer_client_uuid = models.ForeignKey('CustomerClients', models.DO_NOTHING, db_column='customer_client_uuid',
                                             blank=True, null=True)
    info_json = models.JSONField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True,default=True)
    is_deleted = models.BooleanField(blank=True, null=True,default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."client_users'


class CustomerClients(models.Model):
    customer_client_uuid = models.CharField(primary_key=True, max_length=45)
    customer_client_geography_uuid = models.ForeignKey('Dimensions', on_delete=models.CASCADE,
                                                       db_column='customer_client_geography_uuid')
    customer_client_domain_name = models.CharField(max_length=255)
    customer_client_name = models.CharField(max_length=255)
    customer_client_tier_uuid = models.CharField(max_length=45, null=True)
    customer_uuid = models.CharField(max_length=45, null = False)
    customer_client_details_json = models.JSONField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True,default=True)
    is_deleted = models.BooleanField(blank=True, null=True, default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."customer_clients'


class DimensionTypes(models.Model):
    dimension_type_uuid = models.CharField(primary_key=True, max_length=45)
    dimension_type_name = models.CharField(max_length=255, null=False)
    dimension_type_details_json = models.JSONField(blank=True, null=True)
    parent_dimension_type_uuid = models.CharField(max_length=45, blank=True, null=True)
    channel_type_uuid = models.CharField(max_length=45, blank=True, null=True)
    application_uuid = models.CharField(max_length=45, null=True)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    status = models.BooleanField(blank=True, null=True,default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."dimension_types'


class DimensionUserGroupMapping(models.Model):
    dimension_user_group_uuid = models.CharField(primary_key=True, max_length=45)
    channel_type_uuid = models.CharField(max_length=45, null=False)
    application_uuid = models.CharField(max_length=45, null=False)
    customer_uuid = models.CharField(max_length=45, null=False)
    dimension_details_json = models.JSONField(blank=True, null=True)
    user_group_uuid = models.CharField(max_length=45, null=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."dimension_user_group_mapping'


class Dimensions(models.Model):
    dimension_uuid = models.CharField(primary_key=True, max_length=45)
    dimension_name = models.CharField(max_length=255, null=False)
    dimension_type_uuid = models.ForeignKey(DimensionTypes, on_delete=models.CASCADE, db_column='dimension_type_uuid')
    dimension_details_json = models.JSONField(blank=True, null=True)
    parent_dimension_uuid = models.ForeignKey('self', on_delete=models.CASCADE, db_column='parent_dimension_uuid', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    channel_type_uuid = models.CharField(max_length=45, blank=True, null=True)
    application_uuid = models.CharField(max_length=45, null=True)
    customer_uuid = models.CharField(max_length=45, null=True)
    status = models.BooleanField(blank=True, null=True, default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."dimensions'


class EmailConversations(models.Model):
    conversation_uuid = models.CharField(primary_key=True, max_length=100)
    email_uuid = models.ForeignKey('Emails', on_delete=models.CASCADE, db_column='email_uuid')
    email_subject = models.CharField(max_length=255, blank=True, null=True)
    email_flow_status = models.CharField(max_length=255, blank=True, null=True)
    email_status = models.CharField(max_length=255, null=False)
    email_info_json = models.JSONField(blank=True, null=True)
    dimension_action_json = models.JSONField(blank=True, null=True)
    email_process_details = models.JSONField(blank=True,null=True)
    insert_ts = models.DateTimeField()
    updated_ts = models.DateTimeField(auto_now=True)
    parent_uuid = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."email_conversations'


class Conversations(models.Model):
    conversation_uuid = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=255)
    user_details_json = models.JSONField(blank=True, null=True)
    conversation_status = models.CharField(max_length=255, null=False)
    csr_info_json = models.JSONField(blank=True, null=True)
    csr_hand_off = models.BooleanField(default=False)
    conversation_stats_json = models.JSONField(blank=True, null=True)
    conversation_feedback_transaction_json = models.JSONField(blank=True, null=True)
    task_details_json = models.JSONField(blank=True, null=True)
    summary = models.TextField()
    application_uuid = models.CharField(max_length=45, null=False)
    customer_uuid = models.CharField(max_length=45, null=False)
    message_details_json = models.JSONField(blank=True, null=True)
    insert_ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."conversations'

class UnifiedActivity(models.Model):
    activity_uuid = models.CharField(primary_key=True,max_length=45)
    status = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField()
    client_name = models.TextField(blank=True,null=True)
    email_id = models.TextField(blank=True,null=True)
    intent = models.CharField(max_length=255,blank=True,null=True)
    channel = models.TextField(null=False)
    application_uuid = models.CharField(max_length=45,null=True) #TODO should be changed to null=False
    customer_uuid = models.CharField(max_length=45,null=False)

    class Meta:
        managed = True
        db_table = 'old_schema"."unified_activity'


class EmailServer(models.Model):
    email_server_uuid = models.CharField(max_length=45, primary_key=True)
    server_type = models.CharField(max_length=255)
    server_url = models.CharField(max_length=255)
    email_provider_name = models.CharField(max_length=255)
    port = models.CharField(max_length=45)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    inserted_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."email_server'


class EmailServerCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(max_length=45, primary_key=True)
    email_server_uuid = models.ForeignKey(EmailServer, on_delete=models.CASCADE, db_column='email_server_uuid')
    is_ssl_enabled = models.BooleanField(default=True)
    sync_time_interval = models.BigIntegerField(default=5)
    application_uuid = models.ForeignKey('Applications', on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(default=True)
    inserted_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."email_server_customer_application_mapping'
        unique_together = ('email_server_uuid', 'application_uuid', 'customer_uuid')


class Emails(models.Model):
    email_uuid = models.CharField(primary_key=True, max_length=45)
    customer_uuid = models.CharField(max_length=45, null=False)
    application_uuid = models.CharField(max_length=45,null=True)
    customer_client_uuid = models.ForeignKey('CustomerClients', on_delete=models.CASCADE, db_column='customer_client_uuid', blank=True, null=True)
    email_task_status = models.CharField(max_length=255, null=False)
    email_action_flow_status = models.CharField(max_length=255, blank=True, null=True)
    email_activity = models.JSONField(blank=True, null=True)
    dimension_uuid = models.CharField(max_length=45, null=True)
    assigned_to = models.CharField(max_length=45, blank=True, null=True)
    role_uuid = models.CharField(max_length=45, blank=True, null=True)
    insert_ts = models.DateTimeField()
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."emails'


class EscalationActions(models.Model):
    action_uuid = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=225, null=False)
    description = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."escalation_actions'


class EscalationAssignment(models.Model):
    escalation_assignment_uuid = models.CharField(primary_key=True, max_length=45)
    role_uuid = models.CharField(max_length=45, blank=True, null=True)
    user_group_uuid = models.CharField(max_length=45, blank=True, null=True)
    escalation_uuid = models.ForeignKey('Escalations', on_delete=models.DO_NOTHING, db_column='escalation_uuid',
                                        blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."escalation_assignment'


class EscalationHistory(models.Model):
    escalation_history_uuid = models.CharField(primary_key=True, max_length=45)
    escalation_uuid = models.ForeignKey('Escalations', on_delete=models.DO_NOTHING, db_column='escalation_uuid',
                                        blank=True, null=True)
    action_uuid = models.ForeignKey('EscalationActions', on_delete=models.DO_NOTHING, db_column='action_uuid',
                                    blank=True, null=True)
    user_uuid = models.CharField(max_length=45, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    date_actioned = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."escalation_history'


class EscalationRules(models.Model):
    escalation_rule_uuid = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=True, null=True)
    condition_type = models.CharField(max_length=50, null=False)
    condition_operator = models.CharField(max_length=10, blank=True, null=True)
    condition_value = models.CharField(max_length=255, null=False)
    condition_unit = models.CharField(max_length=20, blank=True, null=True)
    level_number = models.IntegerField(null=False)
    status = models.BooleanField(default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."escalation_rules'


class Escalations(models.Model):
    escalation_uuid = models.CharField(primary_key=True, max_length=45)
    email_uuid = models.ForeignKey('Emails', on_delete=models.DO_NOTHING, db_column='email_uuid', null=False)
    escalation_reason = models.CharField(max_length=225, null=False)
    escalation_rule_uuid = models.ForeignKey('EscalationRules', on_delete=models.DO_NOTHING,
                                             db_column='escalation_rule_uuid', blank=True, null=True)
    date_escalated = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."escalations'


class PromptCategory(models.Model):
    prompt_category_uuid = models.CharField(primary_key=True, max_length=45)
    prompt_category_name = models.CharField(max_length=255, null=False)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."prompt_category'


class Prompt(models.Model):
    prompt_uuid = models.CharField(primary_key=True, max_length=45)
    prompt_name = models.CharField(max_length=255, null=False)
    prompt_category = models.CharField(max_length=255, null=False)
    prompt_details_json = models.JSONField(blank=True, null=True)
    prompt_dimension_details_json = models.JSONField(blank=True, null=True)
    channel_type_uuid = models.CharField(max_length=45, null=True)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    application_uuid = models.CharField(max_length=45, null=False)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."prompt'


class PromptTemplate(models.Model):
    prompt_template_uuid = models.CharField(primary_key=True, max_length=45)
    prompt_template_name = models.CharField(max_length=255, null=False)
    prompt_category_uuid = models.CharField(max_length=255, null=False)
    prompt_template_details_json = models.JSONField(blank=True, null=True)
    channel_type_uuid = models.CharField(max_length=45, null=True)
    application_uuid = models.CharField(max_length=45, null=False)
    customer_uuid = models.CharField(max_length=45, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."prompt_template'


class UserEmailSettings(models.Model):
    user_email_uuid = models.CharField(primary_key=True, max_length=45)
    email_id = models.CharField(unique=True, max_length=255)
    encrypted_password = models.CharField(max_length=255)
    email_type = models.CharField(max_length=255)
    email_details_json = models.JSONField(blank=True, null=True)
    is_primary_sender_address = models.BooleanField(blank=True, null=True)
    application_uuid = models.ForeignKey('Applications', on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, null=True, default=True)
    is_deleted = models.BooleanField(blank=True, null=True, default=False)
    last_read_ts = models.DateTimeField(blank=True, null=True)
    inserted_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."user_email_setting'
        unique_together = ('email_id', 'application_uuid', 'customer_uuid',)


# chatbot Database
class ChatConfiguration(models.Model):
    chat_configuration_uuid = models.CharField(primary_key=True, max_length=45)
    chat_configuration_name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    chat_details_json = models.JSONField(blank=True, null=True)
    chat_configuration_provider = models.CharField(max_length=255, null=False, default='web')
    code = models.TextField(blank=True, null=True)
    application_uuid = models.CharField(max_length=45, null=True)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    chat_configuration_type = models.CharField(max_length=255, null=False)
    status = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'old_schema"."chat_configuration'


class ChannelTypes(models.Model):
    channel_type_uuid = models.CharField(primary_key=True, max_length=45)
    channel_type_name = models.CharField(max_length=255, null=False)
    application_uuid = models.CharField(max_length=255, null=False)
    channel_type_details_json = models.JSONField(null=True)
    status = models.BooleanField(default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."channel_types'


class Channels(models.Model):
    channel_uuid = models.CharField(primary_key=True, max_length=45)
    channel_name = models.CharField(max_length=255, null=False)
    channel_type_uuid = models.CharField(max_length=45, null=False)
    application_uuid = models.CharField(max_length=255, null=False)
    customer_uuid = models.CharField(max_length=45, null=False)
    channel_details_json = models.JSONField(null=True)
    status = models.BooleanField(default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."channels'


class ApplicationChannelClientMapping(models.Model):
    application_channel_client_uuid = models.CharField(primary_key=True, max_length=45)
    application_uuid = models.CharField(max_length=255, null=False)
    customer_uuid = models.CharField(max_length=45, null=False)
    channel_uuid = models.CharField(max_length=255, null=False)
    client_uuid = models.CharField(max_length=255, null=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."application_channel_client_mapping'


class ChannelDimensionUserGroupMapping(models.Model):
    dimension_user_group_uuid = models.CharField(primary_key=True, max_length=45)
    channel_type_uuid = models.CharField(max_length=45, null=False)
    application_uuid = models.CharField(max_length=255, null=False)
    customer_uuid = models.CharField(max_length=45, null=False)
    dimension_details_json = models.JSONField(null=True)
    user_group_uuid = models.CharField(max_length=45, null=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."channel_dimension_user_group_mapping'


class Tools(models.Model):
    tool_uuid = models.CharField(primary_key=True, max_length=45)
    tool_description = models.CharField(max_length=255)
    tool_name = models.CharField(max_length=255)
    is_built_in = models.BooleanField(default=True)
    code_details_json = models.JSONField(null=True)
    application_uuid = models.CharField(max_length=255, null=False)
    customer_uuid = models.CharField(max_length=45, null=True)
    status = models.BooleanField(default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."tools'


class Agent(models.Model):
    agent_uuid = models.CharField(primary_key=True, max_length=45)
    agent_name = models.CharField(max_length=255)
    agent_description = models.CharField(max_length=255)
    dimension_details_json = models.JSONField(null=True)
    agent_details_json = models.JSONField(null=True)
    application_uuid = models.CharField(max_length=255, null=False)
    customer_uuid = models.CharField(max_length=45, null=True)
    status = models.BooleanField(default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."agent'


class WorkFlow(models.Model):
    workflow_uuid = models.CharField(primary_key=True, max_length=45)
    workflow_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    customer_uuid = models.CharField(max_length=45, null=True)
    application_uuid = models.CharField(max_length=45, null=True)
    channel_type_uuid = models.CharField(max_length=45, null=True)
    workflow_details_json = models.JSONField()
    insert_ts = models.DateTimeField(auto_now_add=True),
    updated_ts = models.DateTimeField(auto_now=True),
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."workflow'


class Step(models.Model):
    step_uuid = models.CharField(primary_key=True, max_length=45)
    workflow_uuid = models.ForeignKey('WorkFlow', models.DO_NOTHING, db_column='workflow_uuid')
    step_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    step_details_json = models.JSONField()
    step_type = models.CharField(max_length=255)
    notes = models.TextField(null=True)
    insert_ts = models.DateTimeField(auto_now_add=True),
    updated_ts = models.DateTimeField(auto_now=True),
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."step'


class Countries(models.Model):
    id = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=100)
    iso3 = models.CharField(max_length=3, null=True)
    numeric_code = models.CharField(max_length=3, null=True)
    iso2 = models.CharField(max_length=2, null=True)
    phonecode = models.CharField(max_length=255, null=True)
    capital = models.CharField(max_length=255, null=True)
    currency = models.CharField(max_length=255, null=True)
    currency_name = models.CharField(max_length=255, null=True)
    currency_symbol = models.CharField(max_length=255, null=True)
    tld = models.CharField(max_length=255, null=True)
    native = models.CharField(max_length=255, null=True)
    region = models.CharField(max_length=255, null=True)
    region_id = models.BigIntegerField(null=True)
    subregion = models.CharField(max_length=255, null=True)
    subregion_id = models.BigIntegerField(null=True)
    nationality = models.CharField(max_length=255, null=True)
    timezones = models.TextField(null=True)
    translations = models.TextField(null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    emoji = models.CharField(max_length=191, null=True)
    emojiU = models.CharField(max_length=191, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    flag = models.SmallIntegerField(default=1)
    wikiDataId = models.CharField(max_length=255, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."countries'


class States(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    country_id = models.BigIntegerField()
    country_code = models.CharField(max_length=2)
    fips_code = models.CharField(max_length=255, null=True)
    iso2 = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=191, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    flag = models.SmallIntegerField(default=1)
    wikiDataId = models.CharField(max_length=255, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."states'

    
class LLMConfiguration(models.Model):
    llm_configuration_uuid = models.CharField(primary_key=True, max_length=45)
    llm_configuration_name = models.CharField(max_length=255, null=False)
    llm_configuration_details_json = models.JSONField(null=True)
    customer_uuid = models.CharField(max_length=255, null=False)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."llm_configuration'
        
class LLMConfigurationChannelMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    llm_configuration_uuid = models.CharField(max_length=255, null=False)
    mapping_details_json = models.JSONField(null=True)
    channel_uuid = models.CharField(max_length=255, null=False)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."llm_configuration_channel_mapping'


class LLMProviderMetaData(models.Model):
    llm_provider_uuid = models.CharField(primary_key=True, max_length=45)
    llm_provider_name = models.CharField(max_length=255, null=False)
    llm_provider_details_json = models.JSONField(null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."llm_provider_meta_data'

class CustomerClientTierApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    customer_client_uuid = models.ForeignKey('CustomerClients', models.DO_NOTHING, db_column='customer_client_uuid')
    tier_uuid = models.ForeignKey('Dimensions', models.DO_NOTHING, db_column='tier_uuid')
    application_uuid = models.CharField(max_length=255, null=False)
    template_details_json = models.JSONField(null=True)
    is_deleted = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."customer_client_tier_application_mapping'


class Entities(models.Model):
    entity_uuid = models.CharField(primary_key=True, max_length=45)
    entity_name = models.CharField(max_length=30)
    entity_description = models.TextField(blank=True, null=True)
    application_uuid = models.CharField(max_length=45, null=False)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    attribute_details_json = models.JSONField(default=dict)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."entities'        
        
        
class Files(models.Model):
    class FileStatus(models.TextChoices):
        PROCESSING = "Processing",
        UNDER_REVIEW = "Under Review",
        REVIEWED = "Reviewed",
        FAILED = "Failed",
        REVIEWING = "Reviewing"
        QA_GENERATING = "QA Generating"

    file_uuid = models.CharField(primary_key=True, max_length=45)
    file_name = models.CharField(max_length=254)
    file_path = models.TextField()
    error_details_json = models.JSONField(default=list)
    file_metadata = models.JSONField(default=dict)
    file_status = models.CharField(choices=FileStatus.choices, default=FileStatus.PROCESSING, max_length=64)
    file_type = models.CharField(max_length=30)
    application_uuid = models.CharField(max_length=45, null=False)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    entity = models.ForeignKey(Entities, models.DO_NOTHING, db_column='entity_uuid')
    image_map = models.JSONField(default=dict)
    attribute_details_json = models.JSONField(default=dict)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."files'


def default_verification_details():
    return {
        'sme': {
            'verified': False,
            'user_uuid': None
        },
        'qa': {
            'verified': False,
            'user_uuid': None
        }
    }


def default_draft():
    return {
        "content": None,
        "attachments": [],
        "draft_status": False,
        "user_id": None
    }


def default_author():
    return {
        'user_generated': True,
        'user_uuid': None
    }


class Answers(models.Model):
    answer_uuid = models.CharField(primary_key=True, max_length=45)
    answer = models.TextField()
    attachment_details_json = models.JSONField(default=list)
    application_uuid = models.CharField(max_length=45, null=False)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    draft = models.JSONField(default=default_draft)
    feedback = models.TextField(blank=True, null=True)
    verification_details_json = models.JSONField(default=default_verification_details)
    author_details_json = models.JSONField(default=default_author)
    file_details_json = models.JSONField(default=list)
    entity_details_json = models.JSONField(default=list)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."answers'


class Questions(models.Model):
    question_uuid = models.CharField(primary_key=True, max_length=45)
    question = models.TextField()
    answer = models.ForeignKey(Answers, models.CASCADE, db_column='answer_uuid')
    application_uuid = models.CharField(max_length=45, null=False)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    author_details_json = models.JSONField(default=default_author)
    in_cache = models.BooleanField(default=True)
    insert_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'old_schema"."questions'


class UserMgmtUsers(models.Model):
    user_id = models.CharField(max_length=45, primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_id = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    mobile_number = models.CharField(max_length=255, unique=True)
    title = models.TextField(blank=True, null=True)
    user_details_json = models.TextField(blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_id = models.CharField(max_length=45, blank=True, null=True)
    status = models.BooleanField(default=True)
    auth_type = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)
    activation_ts = models.DateTimeField(blank=True, null=True)
    password_last_updated_at = models.DateTimeField(auto_now_add=True)
    last_login_ts = models.DateTimeField(blank=True, null=True)
    created_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt2"."users'
        unique_together = (
            ('email_id',),
            ('mobile_number',),
            ('username',),
        )


class Customers(models.Model):
    cust_uuid = models.CharField(max_length=45, primary_key=True, default=uuid.uuid4, editable=False,
                                 db_column="customer_id")
    cust_name = models.CharField(max_length=255, db_column="customer_name")
    purchased_plan = models.CharField(max_length=45, null=True, blank=True)
    email = models.CharField(max_length=255)
    primary_contact = models.CharField(max_length=255, null=True, blank=True)
    secondary_contact = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    billing_address = models.CharField(max_length=255, null=True, blank=True)
    customer_details_json = models.JSONField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.cust_uuid)

    class Meta:
        db_table = 'usermgmt2"."customers'

        
class Applications(models.Model):
    application_uuid = models.CharField(primary_key=True, max_length=45, db_column="application_id")
    application_name = models.CharField(unique=True, max_length=255)
    application_url = models.CharField(unique=True, max_length=255)
    scope_end_point = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    created_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt2"."applications'


class CustomerApplicationMapping(models.Model):
    customer_application_id = models.CharField(primary_key=True, max_length=45)
    customer = models.ForeignKey(Customers, models.CASCADE)
    application = models.ForeignKey(Applications, models.CASCADE)
    customer_application_details_json = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt2"."customer_application_mapping'
        unique_together = (('customer', 'application_id'),)
