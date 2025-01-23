# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from email.policy import default

from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid

from datetime import datetime


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
    password_last_updated_at = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    last_login_ts = models.DateTimeField(blank=True, null=True)
    created_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True, auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt"."users'
        unique_together = ('email_id','mobile_number','username')


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
    created_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.cust_uuid)

    class Meta:
        db_table = 'usermgmt"."customers'


class Applications(models.Model):
    application_uuid = models.CharField(primary_key=True, max_length=45, db_column="application_id")
    application_name = models.CharField(unique=True, max_length=255)
    application_url = models.CharField(unique=True, max_length=255)
    scope_end_point = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    created_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt"."applications'


class CustomerApplicationMapping(models.Model):
    customer_application_id = models.CharField(primary_key=True, max_length=45)
    customer = models.ForeignKey(Customers, models.CASCADE)
    application = models.ForeignKey(Applications, models.CASCADE)
    customer_application_details_json = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt"."customer_application_mapping'
        unique_together = ('customer', 'application_id')


class Roles(models.Model):
    role_uuid = models.CharField(max_length=45, primary_key=True, db_column="role_id")
    role_name = models.CharField(max_length=255, db_column="role_name", null=False, blank=False)
    role_details_json = models.TextField(blank=True, null=True, db_column="role_details_json")
    application_uuid = models.CharField(max_length=45, blank=True, null=True, db_column="application_id")
    customer_uuid = models.CharField(max_length=45, blank=True, null=True, db_column="customer_id")
    description = models.TextField(blank=True, null=True, db_column="description")
    status = models.BooleanField(default=True, db_column="status")
    created_ts = models.DateTimeField(blank=True, null=True, auto_now_add=True, db_column="created_ts")
    updated_ts = models.DateTimeField(blank=True, null=True, auto_now=True, db_column="updated_ts")
    created_by = models.CharField(max_length=255, blank=True, null=True, db_column="created_by")
    updated_by = models.CharField(max_length=255, blank=True, null=True, db_column="updated_by")

    class Meta:
        managed = True
        db_table = 'usermgmt"."roles'


class UserDetailsView(models.Model):
    view_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=45)
    user_name = models.CharField(max_length=255, db_column="username")
    mobile_number = models.CharField(max_length=255)
    email_id = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    last_login_ts = models.DateTimeField()
    title = models.TextField()
    status = models.BooleanField()
    created_ts = models.DateTimeField()
    group_id = models.CharField(max_length=45)
    role_id = models.CharField(max_length=45)
    role_name = models.CharField(max_length=255)
    application_id = models.CharField(max_length=45)
    application_name = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=45)
    resource_id = models.CharField(max_length=255)
    resource_name = models.CharField(max_length=255)
    resource_type_name = models.CharField(max_length=255)
    global_scope = models.TextField()
    user_role_scope = models.TextField()
    resource_scope = models.TextField()
    actions = models.TextField()

    class Meta:
        managed = True
        db_table = 'usermgmt"."user_details_view'

class RoleDetailsView(models.Model):
    view_id = models.UUIDField(primary_key=True)
    role_id = models.CharField(max_length=45, blank=True, null=True)
    role_name = models.CharField(max_length=255, blank=True, null=True)
    role_details_json = models.TextField(blank=True, null=True)
    role_status = models.BooleanField(blank=True, null=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_ts = models.DateTimeField(blank=True, null=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE)
    application_name = models.CharField(max_length=255, blank=True, null=True)
    scope_end_point = models.CharField(max_length=50, blank=True, null=True)
    resource_id = models.CharField(max_length=255, blank=True, null=True)
    resource_name = models.CharField(max_length=255, blank=True, null=True)
    resource_status = models.BooleanField(blank=True, null=True)
    resource_type_id = models.CharField(max_length=45, blank=True, null=True)
    resource_type_name = models.CharField(max_length=255, blank=True, null=True)
    action_id = models.CharField(max_length=45, blank=True, null=True)
    action_name = models.CharField(max_length=255, blank=True, null=True)
    role_resource_action_id = models.CharField(max_length=45, blank=True, null=True)
    resource_action_id = models.CharField(max_length=45, blank=True, null=True)
    role_resource_action_details_json = models.TextField(blank=True, null=True)
    resource_details_json = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt"."role_details_view'

class RoleResourceActionMapping(models.Model):
    role_resource_action_id = models.CharField(primary_key=True, max_length=45)
    role = models.ForeignKey(Roles, models.CASCADE)
    resource_action_id = models.CharField(max_length=45)
    role_resource_action_details_json = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usermgmt"."role_resource_action_mapping'
        unique_together = (('role', 'resource_action_id'),)


class Agent(models.Model):
    agent_uuid = models.CharField(primary_key=True, max_length=45)
    agent_name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    dimension_details_json = models.JSONField(blank=True, null=True)
    agent_details_json = models.JSONField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'agent'


class AgentCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    agent_uuid = models.ForeignKey(Agent, models.CASCADE, db_column='agent_uuid')
    description = models.TextField(blank=True, null=True)
    agent_details_json = models.JSONField(blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'agent_customer_application_mapping'
        unique_together = ('agent_uuid', 'application_uuid', 'customer_uuid')


class Answers(models.Model):
    answer_uuid = models.CharField(primary_key=True, max_length=45)
    answer = models.TextField(blank=True, null=True)
    attachment_details_json = models.JSONField(default=list)
    file_details_json = models.JSONField(default=list)
    entity_details_json = models.JSONField(default=list)
    feedback = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verifier_user_uuid = models.CharField(max_length=45, blank=True, null=True)
    verifier_role_uuid = models.CharField(max_length=45, blank=True, null=True)
    is_system_generated = models.BooleanField(blank=True, null=True)
    author_user_uuid = models.CharField(max_length=45, blank=True, null=True)
    author_role_uuid = models.CharField(max_length=45, blank=True, null=True)
    in_cache = models.BooleanField(default=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    inserted_ts = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'answers'


class ApiConfiguration(models.Model):
    api_configuration_uuid = models.CharField(primary_key=True, max_length=45)
    api_name = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)
    params_details_json = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    is_default = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'api_configuration'


class ApiBodyTemplate(models.Model):
    api_body_template_uuid = models.CharField(primary_key=True, max_length=45)
    api_configuration_uuid = models.ForeignKey(ApiConfiguration, models.CASCADE, db_column='api_configuration_uuid')
    api_payload = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'api_body_template'


class ApiConfigurationCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    api_configuration_uuid = models.ForeignKey(ApiConfiguration, models.CASCADE, db_column='api_configuration_uuid')
    auth_value = models.JSONField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'api_configuration_customer_application_mapping'


class ApiHeader(models.Model):
    api_header_uuid = models.CharField(primary_key=True, max_length=45)
    api_configuration_uuid = models.ForeignKey(ApiConfiguration, models.CASCADE, db_column='api_configuration_uuid')
    header_type = models.CharField(max_length=45)
    header_key = models.CharField(max_length=255)
    header_value = models.CharField(max_length=255, blank=True, null=True)
    is_required = models.BooleanField()
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'api_header'


class Ticket(models.Model):
    ticket_uuid = models.CharField(primary_key=True, max_length=45)
    ticket_external_id = models.CharField(max_length=254,unique=True)
    ticket_details_json = models.JSONField(blank=True, null=True)
    channel = models.TextField(max_length=255,null=False)
    client_name = models.TextField(blank=True, null=True)
    customer_client_uuid = models.ForeignKey('CustomerClient', on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, db_column='customer_client_uuid')
    email_id = models.TextField(blank=True, null=True)
    dimension_details_json = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=False)
    is_merged = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    assigned_to = models.ForeignKey(UserMgmtUsers,on_delete=models.SET_DEFAULT,default=None,blank=True,null=True,to_field='user_id',db_column='assigned_to')

    class Meta:
        managed = True
        db_table = 'ticket'



class ChatConfiguration(models.Model):
    chat_configuration_uuid = models.CharField(primary_key=True, max_length=45)
    chat_configuration_name = models.CharField(max_length=255)
    chat_configuration_type = models.CharField(max_length=255)
    chat_configuration_provider = models.CharField(max_length=255,default = "web")
    description = models.TextField(blank=True, null=True)
    chat_details_json = models.JSONField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add = True)
    updated_ts = models.DateTimeField(blank=True, null=True, auto_now = True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    pre_created = models.BooleanField(blank=True, null=True,default=False)
    class Meta:
        managed = True
        db_table = 'chat_configuration'


class ChatConfigurationCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    chat_configuration_uuid = models.ForeignKey(ChatConfiguration, on_delete=models.CASCADE, db_column='chat_configuration_uuid', blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, null=True,default=False)
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add = True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now = True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'chat_configuration_customer_application_mapping'
        unique_together = (('chat_configuration_uuid', 'application_uuid', 'customer_uuid'),)


class ChatConversation(models.Model):
    chat_conversation_uuid = models.CharField(primary_key=True, max_length=45)
    user_details_json = models.JSONField(blank=True, null=True)
    conversation_status = models.CharField(max_length=100)
    csr_info_json = models.JSONField(blank=True, null=True)
    csr_hand_off = models.BooleanField(blank=True, null=True)
    conversation_stats_json = models.JSONField(blank=True, null=True)
    conversation_feedback_transaction_json = models.JSONField(blank=True, null=True)
    summary = models.TextField()
    is_deleted = models.BooleanField(default=False)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    message_details_json = models.JSONField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    ticket_uuid = models.ForeignKey(Ticket,blank=True,null=True,db_column='ticket_uuid',on_delete=models.CASCADE)


    class Meta:
        managed = True
        db_table = 'chat_conversation'


class DimensionType(models.Model):
    dimension_type_uuid = models.CharField(primary_key=True, max_length=45)
    dimension_type_name = models.CharField(unique=True, max_length=255)
    is_deleted = models.BooleanField(default=False,)
    is_default = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dimension_type'


class Dimension(models.Model):
    dimension_uuid = models.CharField(primary_key=True, max_length=45)
    dimension_name = models.CharField(max_length=255)
    dimension_type_uuid = models.ForeignKey('DimensionType', models.CASCADE, db_column='dimension_type_uuid')
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    status = models.BooleanField(default=True,)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dimension'
        unique_together = ('dimension_name', 'dimension_type_uuid')


class DimensionCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    dimension_uuid = models.ForeignKey('Dimension', models.CASCADE, db_column='dimension_uuid', related_name='dimensions')
    description = models.TextField(blank=True, null=True)
    dimension_details_json = models.JSONField(blank=True, null=True)
    parent_dimension_uuid = models.ForeignKey('Dimension', models.CASCADE, db_column='parent_dimension_uuid', null=True)
    application_uuid = models.ForeignKey('Applications', on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(default=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dimension_customer_application_mapping'
        unique_together = ('dimension_uuid', 'application_uuid', 'customer_uuid')


class CustomerClient(models.Model):
    customer_client_uuid = models.CharField(primary_key=True, max_length=45)
    customer_client_name = models.CharField(max_length=255)
    customer_client_geography_uuid = models.ForeignKey(Dimension, models.SET_NULL, db_column='customer_client_geography_uuid', null=True)
    customer_client_domain_name = models.CharField(max_length=255, blank=True, null=True)
    customer_client_emails = ArrayField(models.CharField(max_length=255))
    customer_client_address = models.TextField(blank=True, null=True)
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, default=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True, auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'customer_client'
        unique_together = (('customer_client_name', 'customer_uuid'), ('customer_client_emails', 'customer_uuid'))


class ClientUser(models.Model):
    client_user_uuid = models.CharField(primary_key=True, max_length=45)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_id = models.CharField(unique=True, max_length=255)
    geography_uuid = models.ForeignKey(Dimension, models.SET_NULL, db_column='geography_uuid', null=True)
    customer_client_uuid = models.ForeignKey(CustomerClient, models.CASCADE, db_column='customer_client_uuid')
    user_info_json = models.JSONField(blank=True, null=True)
    status = models.BooleanField(blank=True, default=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'client_user'
        unique_together = (('first_name', 'last_name','customer_client_uuid'), ('email_id', 'customer_client_uuid'))



class Countries(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    iso3 = models.CharField(max_length=255,blank=True, null=True)
    numeric_code = models.CharField(max_length=255,blank=True, null=True)
    iso2 = models.CharField(max_length=255,blank=True, null=True)
    phonecode = models.CharField(max_length=255, blank=True, null=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=255, blank=True, null=True)
    currency_name = models.CharField(max_length=255, blank=True, null=True)
    currency_symbol = models.CharField(max_length=255, blank=True, null=True)
    tld = models.CharField(max_length=255, blank=True, null=True)
    native = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    region_id = models.BigIntegerField(blank=True, null=True)
    subregion = models.CharField(max_length=255, blank=True, null=True)
    subregion_id = models.BigIntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    timezones = models.TextField(blank=True, null=True)
    translations = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    emoji = models.CharField(max_length=191, blank=True, null=True)
    emojiu = models.CharField(max_length=191, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()
    flag = models.SmallIntegerField()
    wikidataid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'countries'


class CustomerClientTierMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    customer_client_uuid = models.ForeignKey(CustomerClient, models.CASCADE, db_column='customer_client_uuid')
    tier_mapping_uuid = models.ForeignKey(DimensionCustomerApplicationMapping, models.CASCADE, db_column='tier_mapping_uuid')
    extractor_template_details_json = models.JSONField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'customer_client_tier_mapping'
        unique_together = (('customer_client_uuid', 'tier_mapping_uuid'),)


class DimensionTypeCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    dimension_type_uuid = models.ForeignKey('DimensionType', models.CASCADE, db_column='dimension_type_uuid')
    description = models.TextField(blank=True, null=True)
    dimension_type_details_json = models.JSONField(blank=True, null=True)
    application_uuid = models.ForeignKey('Applications', on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(default=True,)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dimension_type_customer_application_mapping'
        unique_together = ('dimension_type_uuid', 'application_uuid', 'customer_uuid',)


class Drafts(models.Model):
    draft_uuid = models.CharField(primary_key=True, max_length=45)
    draft = models.TextField(blank=True, null=True)
    attachment_details_json = models.JSONField(default=list)
    author_user_uuid = models.CharField(max_length=45, blank=True, null=True)
    author_role_uuid = models.CharField(max_length=45, blank=True, null=True)
    answer_uuid = models.ForeignKey(Answers, on_delete=models.CASCADE, unique=True, db_column='answer_uuid')
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'drafts'


class EmailConversation(models.Model):
    email_conversation_uuid = models.CharField(primary_key=True, max_length=45)
    customer_client_uuid = models.ForeignKey(CustomerClient, models.SET_NULL, db_column='customer_client_uuid', blank=True, null=True)
    email_conversation_flow_status = models.CharField(max_length=255, blank=True, null=True)
    email_activity = models.JSONField(blank=True, null=True)
    dimension_uuid = models.ForeignKey(Dimension, models.SET_NULL, db_column='dimension_uuid', blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    is_deleted = models.BooleanField(default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    assigned_to = models.ForeignKey(UserMgmtUsers,on_delete=models.SET_DEFAULT,default=None,blank=True,null=True,to_field='user_id',db_column='assigned_to')
    ticket_uuid = models.ForeignKey(Ticket,blank=True,null=True,db_column='ticket_uuid',on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'email_conversation'


class Email(models.Model):
    email_uuid = models.CharField(primary_key=True, max_length=100)
    email_conversation_uuid = models.ForeignKey(EmailConversation, models.CASCADE, db_column='email_conversation_uuid')
    email_status = models.CharField(max_length=255)
    email_flow_status = models.CharField(max_length=255, blank=True)
    dimension_action_json = models.JSONField(blank=True, null=True)
    role_uuid = models.CharField(max_length=45, blank=True, null=True)
    parent_uuid = models.ForeignKey('self', models.CASCADE, db_column='parent_uuid', blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'email'


class EmailInfoDetail(models.Model):
    email_info_uuid = models.CharField(primary_key=True, max_length=45)
    email_uuid = models.ForeignKey(Email, models.CASCADE, db_column='email_uuid')
    email_subject = models.CharField(max_length=255, blank=True, null=True)
    email_body_url = models.TextField(blank=True, null=True)
    attachments = models.JSONField(blank=True, null=True)
    sender = models.TextField(blank=True, null=True)
    sender_name = models.TextField(blank=True, null=True)
    email_type = models.CharField(max_length=255, blank=True, null=True)
    recipient_name = models.TextField(blank=True, null=True)
    recipient = models.TextField(blank=True, null=True)
    recipients = models.JSONField(blank=True, null=True)
    cc_recipients = models.JSONField(blank=True, null=True)
    bcc_recipients = models.JSONField(blank=True, null=True)
    email_body_summary = models.TextField(blank=True, null=True)
    email_meta_body = models.TextField(blank=True, null=True)
    html_body = models.TextField(blank=True, null=True)
    extracted_order_details = models.TextField(blank=True, null=True)
    validated_details = models.TextField(blank=True, null=True)
    verified = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'email_info_detail'


class EmailConversationView(models.Model):
    email_uuid = models.CharField(max_length=100)
    email_conversation_uuid = models.CharField(primary_key=True,max_length=45)
    email_subject = models.CharField(max_length=255, null=True, blank=True)
    email_status = models.CharField(max_length=255)
    dimension_action_json = models.JSONField(null=True, blank=True)
    parent_uuid = models.CharField(max_length=100, null=True, blank=True)
    inserted_ts = models.DateTimeField()
    updated_ts = models.DateTimeField()
    email_info_uuid = models.CharField(max_length=45)
    email_body_url = models.TextField(null=True, blank=True)
    html_body = models.TextField(blank=True, null=True)
    attachments = models.JSONField(null=True, blank=True)
    sender = models.TextField(null=True, blank=True)
    sender_name = models.TextField(null=True, blank=True)
    recipient = models.TextField(null=True, blank=True)
    recipients = models.JSONField(null=True, blank=True)
    cc_recipients = models.JSONField(null=True, blank=True)
    bcc_recipients = models.JSONField(null=True, blank=True)
    email_body_summary = models.TextField(null=True, blank=True)
    email_meta_body = models.TextField(null=True, blank=True)
    extracted_order_details = models.TextField(null=True, blank=True)
    validated_details = models.TextField(null=True, blank=True)
    verified = models.BooleanField(null=True)
    email_flow_status = models.CharField(max_length=255, blank=True)
    email_activity = models.JSONField(null=True, blank=True)
    ticket_uuid=models.CharField(max_length=45)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = True  # No migrations will be created for this model
        db_table = 'email_conversation_view'


class EmailServer(models.Model):
    email_server_uuid = models.CharField(max_length=45, primary_key=True)
    server_type = models.CharField(max_length=255)
    server_url = models.CharField(max_length=255)
    email_provider_name = models.CharField(max_length=255)
    port = models.CharField(max_length=45)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'email_server'


class EmailServerCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(max_length=45, primary_key=True)
    email_server_uuid = models.ForeignKey(EmailServer, on_delete=models.CASCADE, db_column='email_server_uuid')
    is_ssl_enabled = models.BooleanField(default=True)
    sync_time_interval = models.BigIntegerField(default=5)
    application_uuid = models.ForeignKey('Applications', on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(default=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
    microsoft_client_id = models.CharField(max_length=255, null=True, blank=True)
    microsoft_tenant_id = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        managed = True
        db_table = 'email_server_customer_application_mapping'
        unique_together = ('email_server_uuid', 'application_uuid', 'customer_uuid')


class Entities(models.Model):
    entity_uuid = models.CharField(primary_key=True, max_length=45)
    entity_name = models.CharField(max_length=30)
    entity_description = models.TextField(blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    attribute_details_json = models.JSONField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'entities'
        unique_together = ('customer_uuid', 'application_uuid', 'entity_name')



class KnowledgeSources(models.Model):
    
    class KnowledgeSourceStatus(models.TextChoices):
        PROCESSING = "Processing"
        UNDER_REVIEW = "Under Review"
        REVIEWED = "Reviewed"
        FAILED = "Failed"
        CHUNKING = "Chunking"
        QA_GENERATING = "QA Generating"
        QA_GENERATED = "QA Generated"
        
    knowledge_source_uuid = models.CharField(primary_key=True, max_length=45)
    knowledge_source_name = models.CharField(max_length=254)
    knowledge_source_path = models.TextField()
    knowledge_source_type = models.CharField(max_length=30)
    knowledge_source_status = models.CharField(choices=KnowledgeSourceStatus.choices, default=KnowledgeSourceStatus.PROCESSING, max_length=30)
    knowledge_source_metadata = models.JSONField(blank=True, null=True)
    parent_knowledge_source_uuid = models.CharField(max_length=45, blank=True, null=True)
    is_reuploaded = models.BooleanField(blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    entity_uuid = models.ForeignKey(Entities, models.DO_NOTHING, db_column='entity_uuid')
    attribute_details_json = models.JSONField(blank=True, null=True)
    qa_status = models.BooleanField(default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'knowledge_sources'


class Errors(models.Model):
    error_uuid = models.CharField(primary_key=True, max_length=45)
    error_type = models.CharField(max_length=30)
    error_status = models.CharField(max_length=30)
    error_details_json = models.JSONField(blank=True, null=True)
    knowledge_source_uuid = models.ForeignKey(KnowledgeSources, models.CASCADE, db_column='knowledge_source_uuid')
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'errors'


class LLMProviderMetaData(models.Model):
    llm_provider_uuid = models.CharField(primary_key=True, max_length=45)
    llm_provider_name = models.CharField(unique=True, max_length=255)
    llm_provider_details_json = models.JSONField(blank=True, null=True)
    llm_column_details = models.JSONField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'llm_provider_meta_data'


class LLMConfiguration(models.Model):
    llm_configuration_uuid = models.CharField(primary_key=True, max_length=45)
    llm_configuration_name = models.CharField(max_length=255)
    llm_provider_uuid = models.ForeignKey(LLMProviderMetaData, models.SET_NULL, db_column='llm_provider_uuid', null=True)
    llm_configuration_details_json = models.JSONField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'llm_configuration'
class LLMConfigurationCustomerMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    llm_configuration_uuid = models.ForeignKey(LLMConfiguration, models.CASCADE, db_column='llm_configuration_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, null=True,default=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'llm_configuration_customer_mapping'
        unique_together = (('llm_configuration_uuid', 'customer_uuid'),)

class ConfigurationDetails(models.Model):
    configuration_details_uuid = models.CharField(primary_key=True, max_length=45)
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    configuration_details_json = models.JSONField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'configuration_details'

class Media(models.Model):
    media_uuid = models.CharField(primary_key=True, max_length=45)
    media_name = models.CharField(max_length=254)
    media_path = models.TextField()
    media_details_json = models.JSONField(blank=True, null=True)
    knowledge_source_uuid = models.CharField(max_length=45, blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'media'


class PromptCategory(models.Model):
    prompt_category_uuid = models.CharField(primary_key=True, max_length=45)
    prompt_category_name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'prompt_category'


class Prompt(models.Model):
    prompt_uuid = models.CharField(primary_key=True, max_length=45)
    prompt_name = models.CharField(max_length=255)
    prompt_category_uuid = models.ForeignKey(PromptCategory, models.DO_NOTHING, db_column='prompt_category_uuid')
    prompt_details_json = models.JSONField(blank=True, null=True)
    prompt_dimension_details_json = models.JSONField(blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, null=True,default=True)
    is_deleted = models.BooleanField(blank=True, null=True,default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'prompt'
        unique_together = (('prompt_name', 'application_uuid', 'customer_uuid'),)


class PromptTemplate(models.Model):
    prompt_template_uuid = models.CharField(primary_key=True, max_length=45)
    prompt_template_name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    prompt_template_details_json = models.JSONField(blank=True, null=True)
    prompt_category_uuid = models.ForeignKey(PromptCategory, models.CASCADE, db_column='prompt_category_uuid')
    is_default = models.BooleanField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True,default=True)
    is_deleted = models.BooleanField(blank=True, null=True,default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'prompt_template'


class PromptTemplateCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    prompt_template_uuid = models.ForeignKey(PromptTemplate, models.CASCADE, db_column='prompt_template_uuid')
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, null=True,default=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'prompt_template_customer_application_mapping'
        unique_together = (('prompt_template_uuid', 'application_uuid', 'customer_uuid'),)


class Questions(models.Model):
    question_uuid = models.CharField(primary_key=True, max_length=45)
    question = models.TextField(blank=True, null=True)
    answer_uuid = models.ForeignKey(Answers, models.CASCADE, db_column='answer_uuid',related_name='questions')
    is_system_generated = models.BooleanField(blank=True, null=True)
    author_user_uuid = models.CharField(max_length=45, blank=True, null=True)
    author_role_uuid = models.CharField(max_length=45, blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True, auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'questions'

class QuestionDetailsView(models.Model):
    question_uuid = models.CharField(max_length=45, blank=True, null=True)
    question = models.TextField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    answer_uuid = models.CharField(max_length=45, blank=True, null=True)
    file_details_json = models.JSONField(blank=True, null=True)
    draft_uuid = models.CharField(max_length=45, blank=True, null=True)
    is_system_generated = models.BooleanField(blank=True, null=True)
    customer_uuid = models.CharField(max_length=45, blank=True, null=True)
    application_uuid = models.CharField(max_length=45, blank=True, null=True)
    is_verified = models.BooleanField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    sme_verified = models.IntegerField(blank=True, null=True)  # This field type is a guess.
    qa_verified = models.IntegerField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'question_details_view'


class States(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Countries, models.CASCADE)
    country_code = models.CharField(max_length=255)
    fips_code = models.CharField(max_length=255, blank=True, null=True)
    iso2 = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=191, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()
    flag = models.SmallIntegerField()
    wikidataid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'states'


class Wiseflow(models.Model):
    wiseflow_uuid = models.CharField(primary_key=True, max_length=45)
    wiseflow_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    wiseflow_details_json = models.JSONField(blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    channel_uuid = models.CharField(max_length=45, blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'wiseflow'
        unique_together = (('customer_uuid', 'application_uuid', 'channel_uuid'),)


class Step(models.Model):
    step_uuid = models.CharField(primary_key=True, max_length=45)
    wiseflow_uuid = models.ForeignKey(Wiseflow, models.CASCADE, db_column='wiseflow_uuid')
    step_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    step_details_json = models.JSONField(blank=True, null=True)
    step_type = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'step'


class Tool(models.Model):
    tool_uuid = models.CharField(primary_key=True, max_length=45)
    tool_name = models.CharField(unique=True, max_length=255)
    tool_details_json = models.JSONField(blank=True, null=True)
    is_built_in = models.BooleanField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tool'


class ToolCustomerApplicationMapping(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    tool_uuid = models.ForeignKey(Tool, on_delete=models.CASCADE, db_column='tool_uuid')
    description = models.TextField(blank=True, null=True)
    tool_details_json = models.JSONField(blank=True, null=True)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True)
    updated_ts = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tool_customer_application_mapping'
        unique_together = (('tool_uuid', 'application_uuid', 'customer_uuid'),)


class UserEmailSetting(models.Model):
    user_email_uuid = models.CharField(primary_key=True, max_length=45)
    email_id = models.CharField(unique=True, max_length=255)
    encrypted_password = models.CharField(max_length=255)
    email_type = models.CharField(max_length=255)
    email_details_json = models.JSONField(blank=True, null=True)
    is_primary_sender_address = models.BooleanField(default=False)
    application_uuid = models.ForeignKey('Applications', on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='customer_uuid')
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    last_read_ts = models.DateTimeField(blank=True, null=True)
    in_queue = models.BooleanField(default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True,auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_email_setting'


class WiseflowExecutionDetails(models.Model):
    execution_details_uuid = models.CharField(primary_key=True, max_length=45)
    entity_uuid = models.CharField(max_length=45)
    entity_type = models.CharField(max_length=255)
    step_uuid = models.ForeignKey(Step, models.CASCADE, db_column='step_uuid')
    wiseflow_uuid = models.ForeignKey(Wiseflow, models.CASCADE, db_column='wiseflow_uuid')
    wiseflow_execution_info = models.JSONField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'wiseflow_execution_details'

class UserActivity(models.Model):
    
    class ActivityChoices(models.TextChoices):
        
        QUERY = 'query'
        FEEDBACK = 'feedback'    
    
    user_activity_uuid = models.CharField(primary_key=True, max_length=45)
    activity_name = models.CharField(choices=ActivityChoices.choices, default=ActivityChoices.QUERY, max_length=255)
    user_id =  models.CharField(max_length=45)
    application_uuid = models.ForeignKey('Applications', on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='customer_uuid')
    question_uuid = models.CharField(max_length=45)
    answer_uuid = models.CharField(max_length=45)
    intent = models.CharField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    inserted_ts = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True, auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        
        managed = True
        db_table = 'user_activity'


class UserTicketMapping(models.Model):
    mapping_uuid = models.CharField(max_length=45, primary_key=True)
    ticket_uuid = models.ForeignKey(Ticket, on_delete=models.CASCADE, db_column='ticket_uuid')
    user_id = models.ForeignKey(UserMgmtUsers, on_delete=models.CASCADE, db_column='user_id')
    is_active = models.BooleanField(default=True)
    action_details_json = models.JSONField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    inserted_ts = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_ts = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = 'user_ticket_mapping'

class DimensionsView(models.Model):
    mapping_uuid = models.CharField(primary_key=True, max_length=45)
    dimension_uuid = models.CharField(max_length=255)
    dimension_name = models.CharField(max_length=255)
    dimension_description = models.TextField(null=True, blank=True)
    customer_uuid = models.CharField(max_length=255, null=True, blank=True)
    application_uuid = models.CharField(max_length=255, null=True, blank=True)
    dimension_type_name = models.CharField(max_length=255)
    dimension_type_uuid = models.CharField(max_length=255, null=True, blank=True)  # Added field
    is_default = models.BooleanField(default=False)  # Added field
    dimension_details_json = models.JSONField(blank=True, null=True)  # Added field
    inserted_ts = models.DateTimeField(null=True, blank=True)  # Added field
    updated_ts = models.DateTimeField(null=True, blank=True)  # Added field
    child_dimensions = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False  # No migrations will be created for this model
        db_table = 'dimensions_view'

class WiseflowEntity(models.Model):

    class OwnershipEnum(models.TextChoices):
        SYSTEM = 'SYSTEM'
        CUSTOM = 'CUSTOM'

    entity_uuid = models.CharField(primary_key=True, default=str(uuid.uuid4), editable=False)
    entity_name = models.CharField(max_length=255)
    description = models.TextField()
    parent_entity_uuid = models.ForeignKey('self',db_column='parent_entity_uuid', on_delete=models.CASCADE, blank=True, null=True)
    output_format = models.JSONField(blank=True, null=True)
    instructions = models.TextField()
    ownership = models.CharField(max_length=255, choices=OwnershipEnum.choices, default=OwnershipEnum.SYSTEM)
    application_uuid = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_uuid')
    customer_uuid = models.ForeignKey(Customers, on_delete=models.CASCADE, db_column='customer_uuid')
    is_deleted = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = 'wiseflow"."entity'

