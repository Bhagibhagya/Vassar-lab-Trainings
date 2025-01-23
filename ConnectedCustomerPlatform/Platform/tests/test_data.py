from datetime import datetime
import json
import uuid
from django.utils import timezone

from DatabaseApp.models import Email, EmailConversation, EmailInfoDetail, LLMConfiguration, LLMProviderMetaData, Prompt, PromptTemplateCustomerApplicationMapping, UserMgmtUsers, Ticket, \
    ChatConversation, UserTicketMapping, EmailConversationView
from DatabaseApp.models import Prompt, PromptTemplateCustomerApplicationMapping, ClientUser
from DatabaseApp.models import Customers, Applications, UserEmailSetting, EmailServer, EmailServerCustomerApplicationMapping , PromptTemplate,PromptCategory

from DatabaseApp.models import DimensionType, Dimension, DimensionTypeCustomerApplicationMapping, CustomerApplicationMapping, \
    CustomerClient, CustomerClientTierMapping, DimensionCustomerApplicationMapping, \
    ChatConfiguration, ChatConfigurationCustomerApplicationMapping,PromptCategory

from Platform.utils import encrypt_password



def create_customer_tier():
    dimension_type_details_json_dict = {
        "description": "Description for DimensionType"
    }
    dimension_type_details_json = json.dumps(dimension_type_details_json_dict)
    customer_tier = DimensionType.objects.create(dimension_type_uuid=uuid.uuid4(), dimension_type_name="CUSTOMER_TIER",
                                                  dimension_type_details_json=dimension_type_details_json,
                                                  customer_uuid=None,
                                                  application_uuid='efr56df-ac2e-4229-b027-2b0767506cde',
                                                  created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
                                                  updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')
    return customer_tier


def create_dimension_type_test_data():
    # Default dimension Type, Normal Dimension Type, Default Dimension
    application, customer = create_customer_application_instances()
    default_dimension_type = DimensionType.objects.create(dimension_type_uuid=uuid.uuid4(),
                                                           dimension_type_name="SENTIMENT",
                                                           is_default=True,
                                                           created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
                                                           updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')

    default_dimension_type2 = DimensionType.objects.create(dimension_type_uuid=uuid.uuid4(),
                                                           dimension_type_name="INTENT",
                                                           is_default=True,
                                                           created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
                                                           updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')

    dimension_type = DimensionType.objects.create(dimension_type_uuid=uuid.uuid4(),
                                                   dimension_type_name="Dimension Type 1",
                                                   created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
                                                   updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')
    dimension_type2 = DimensionType.objects.create(dimension_type_uuid=uuid.uuid4(),
                                                  dimension_type_name="Dimension Type 2",
                                                  created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
                                                  updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')

    dimension_type_mapping = DimensionTypeCustomerApplicationMapping.objects.create(
        mapping_uuid=uuid.uuid4(),
        dimension_type_uuid=dimension_type,
        description="Description for Dim 1",
        application_uuid=application,
        customer_uuid=customer,
        created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
        updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')

    DimensionTypeCustomerApplicationMapping.objects.create(
        mapping_uuid=uuid.uuid4(),
        dimension_type_uuid=dimension_type2,
        description="Description for Dim 2",
        application_uuid=application,
        customer_uuid=customer,
        created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
        updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')

    DimensionTypeCustomerApplicationMapping.objects.create(
        mapping_uuid=uuid.uuid4(),
        dimension_type_uuid=default_dimension_type2,
        description="Description for default dimension 2",
        application_uuid=application,
        customer_uuid=customer,
        created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
        updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')

    Dimension.objects.create(dimension_uuid=uuid.uuid4(),
                              dimension_type_uuid=default_dimension_type,
                              dimension_name="Test Sentiment",
                              is_default=True,
                              created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
                              updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')

    return default_dimension_type, dimension_type, dimension_type_mapping, dimension_type2

def create_email_server_test_data():
    application, customer = create_customer_application_instances()
    user_uuid = uuid.uuid4()
    email_server = EmailServer.objects.create(
        email_server_uuid=uuid.uuid4(),
        email_provider_name='Gmail',
        port=993,
        server_type='IMAP',
        server_url='imap.gmail.com',
        updated_by=user_uuid,
        created_by=user_uuid,
        is_default=True,
    )
    email_server2 = EmailServer.objects.create(
        email_server_uuid=uuid.uuid4(),
        email_provider_name='Outlook',
        port=993,
        server_type='IMAP',
        server_url='outlook.office365.com',
        updated_by=user_uuid,
        created_by=user_uuid,
        is_default=True,
    )
    email_server_mapping = EmailServerCustomerApplicationMapping.objects.create(
        mapping_uuid=uuid.uuid4(),
        email_server_uuid=email_server,
        is_ssl_enabled=True,
        sync_time_interval=5,
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
        inserted_ts=timezone.now(),
        updated_ts=timezone.now()
    )

    return email_server, email_server2, email_server_mapping

def create_customer_application_instances():
    application = Applications.objects.create(
        application_uuid=str(uuid.uuid4()),
        application_name="Test App "+str(uuid.uuid4()),
        application_url="https://connected-customer/"+str(uuid.uuid4()),
        scope_end_point="https://connected-customer/"+str(uuid.uuid4()),
        description = "Connected Enterprise Application"
    )
    customer = Customers.objects.create(
        cust_uuid=str(uuid.uuid4()),
        cust_name = "Test Cust"+str(uuid.uuid4()),
        email = "Test_"+str(uuid.uuid4())+"@gmail.com",
        primary_contact = uuid.uuid4()
    )
    return application, customer

def create_email_settings_test_data():
    application, customer = create_customer_application_instances()
    user_uuid = str(uuid.uuid4())
    # Creating a dummy UserEmailSettings object
    user_email_settings = UserEmailSetting.objects.create(
        user_email_uuid=str(uuid.uuid4()),
        email_id="bot.helpdesk.vl@gmail.com",
        encrypted_password=encrypt_password("jlne ihwz urtu twwh"),
        email_type="individual",
        customer_uuid=customer,
        application_uuid=application,
        status=True,
        created_by=user_uuid,
        updated_by=user_uuid
    )

    user_email_settings2 = UserEmailSetting.objects.create(
        user_email_uuid=str(uuid.uuid4()),
        email_id="test_user4@gmail.com",
        encrypted_password=encrypt_password("hashed_password"),
        email_details_json={'primary_email_address': 'test_user5@gmail.com'},
        email_type="group",
        customer_uuid=customer,
        application_uuid=application,
        status=True,
        created_by=user_uuid,
        updated_by=user_uuid
    )

    return user_email_settings, user_email_settings2


def create_dimension_test_data():
    """
    Geography dimension type
    Parent Dimension - INDIA, its mapping
    Child Dimension - AP, its mapping
    create_scope_test_data() also using this function.
    """

    application, customer = create_customer_application_instances()
    user_uuid = str(uuid.uuid4())
    dimension_type = DimensionType.objects.create(
        dimension_type_uuid=str(uuid.uuid4()),
        dimension_type_name="GEOGRAPHY",
        created_by=user_uuid,
        updated_by=user_uuid,
        is_default=True,
    )

    parent_dimension = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="INDIA",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    parent_dimension_mapping = DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=parent_dimension,
        description="Description for India",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    dimension = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="AP",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    child_dimension_mapping = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="TELANGANA",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=child_dimension_mapping,
        parent_dimension_uuid=parent_dimension,
        description="Description for AP",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )
    parent_intent = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="parentIntent",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )
    sub_intent = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="subIntent",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    parent_intent_mapping = DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid="6d0e7ea5-826c-463b-9329-2690f4ee9965",
        dimension_uuid=parent_intent,
        description="Description for AP",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=sub_intent,
        parent_dimension_uuid=parent_intent,
        description="Description for SUB INTENT",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    dimension_mapping =  DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=dimension,
        parent_dimension_uuid=parent_dimension,
        description="Description for AP",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    CustomerApplicationMapping.objects.create(
        customer_application_id=str(uuid.uuid4()),
        customer=customer,
        application=application,
    )

    return dimension_type, parent_dimension, parent_dimension_mapping, dimension, dimension_mapping


def create_prompt_template_test_data():
    # Create a valid prompt_template instance
    application , customer = create_customer_application_instances()
    prompt_category = create_prompt_category()

    prompt_template_details_json = {
        "system_prompt": "system_prompt for template name 01",
        "context_prompt": "context_prompt for template name 01",
        "display_prompt": "display_prompt for template name 01",
        "remember_prompt": "remember_prompt for template name 01"
    }
    PromptTemplate.objects.create(prompt_template_uuid=uuid.uuid4(),
                                                         prompt_template_name="Test_template_name"+str(uuid.uuid4()),
                                  description="prompt_template_description",
                                  prompt_category_uuid=prompt_category,
                                  prompt_template_details_json=prompt_template_details_json,
                                                         created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                                         updated_by="508825ca-5e1b-47ab-920c-63c7ca721562")
    prompt_template_uuid = uuid.uuid4()
    prompt_template = PromptTemplate.objects.create(prompt_template_uuid=prompt_template_uuid,
                                                    prompt_template_name="template name 01"+str(uuid.uuid4()),
                                                    description="prompt_template_description",
                                                    prompt_category_uuid=prompt_category,
                                                    prompt_template_details_json=prompt_template_details_json
                                                    )
    deleted_prompt_template = PromptTemplate.objects.create(prompt_template_uuid=uuid.uuid4(),
                                                            prompt_template_name="deleted template name"+str(uuid.uuid4()),
                                                            description="prompt_template_description",
                                                            prompt_category_uuid=prompt_category,
                                                            prompt_template_details_json=prompt_template_details_json,
                                                            created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                                            updated_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                                            status=True,is_deleted=True)
    prompt_details_json = {
        "prompt_template_uuid": str(prompt_template_uuid),
        "system_prompt": "system_prompt for template name 01",
        "context_prompt": "context_prompt for template name 01",
        "display_prompt": "display_prompt for template name 01",
        "remember_prompt": "remember_prompt for template name 01"
    }
    prompt_category = create_prompt_category()
    Prompt.objects.create(prompt_uuid=uuid.uuid4(), prompt_name="Test-Prompt"+str(uuid.uuid4()),
                                                        prompt_details_json=prompt_details_json,
                                                        prompt_category_uuid=prompt_category,
                                                        customer_uuid=customer,
                                                        application_uuid=application,
                                                        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                                        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562")

    return prompt_template, deleted_prompt_template

def create_prompt_template_mapping():
    application, customer = create_customer_application_instances()
    prompt_category = create_prompt_category()

    prompt_template_details_json = {
        "system_prompt": "system_prompt for template name 01",
        "context_prompt": "context_prompt for template name 01",
        "display_prompt": "display_prompt for template name 01",
        "remember_prompt": "remember_prompt for template name 01"
    }

    prompt_template = PromptTemplate.objects.create(prompt_template_uuid=uuid.uuid4(),
                                prompt_template_name="Test_template_name" + str(uuid.uuid4()),
                                description="prompt_template_description",
                                prompt_category_uuid=prompt_category,
                                prompt_template_details_json=prompt_template_details_json,
                                created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                updated_by="508825ca-5e1b-47ab-920c-63c7ca721562")
    prompt_template_1 = PromptTemplate.objects.create(prompt_template_uuid=uuid.uuid4(),
                                                    prompt_template_name="Test_template_name" + str(uuid.uuid4()),
                                                    description="prompt_template_description",
                                                    prompt_category_uuid=prompt_category,
                                                    prompt_template_details_json=prompt_template_details_json,
                                                    created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                                    updated_by="508825ca-5e1b-47ab-920c-63c7ca721562")
    prompt_template_2 = PromptTemplate.objects.create(prompt_template_uuid=uuid.uuid4(),
                                                      prompt_template_name="Test_template_name" + str(uuid.uuid4()),
                                                      description="prompt_template_description",
                                                      prompt_category_uuid=prompt_category,
                                                      prompt_template_details_json=prompt_template_details_json,
                                                      created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                                      updated_by="508825ca-5e1b-47ab-920c-63c7ca721562")


    mapping = PromptTemplateCustomerApplicationMapping(
        mapping_uuid=str(uuid.uuid4()),
        prompt_template_uuid=prompt_template,
        customer_uuid=customer,
        application_uuid=application,
        created_by=uuid.uuid4(),
        updated_by=uuid.uuid4(),
    )
    mapping.save()
    mapping2 = PromptTemplateCustomerApplicationMapping(
        mapping_uuid=str(uuid.uuid4()),
        prompt_template_uuid=prompt_template_2,
        customer_uuid=customer,
        application_uuid=application,
        created_by=uuid.uuid4(),
        updated_by=uuid.uuid4(),
    )
    mapping2.save()

    return prompt_template,prompt_template_1,prompt_template_2,mapping


def create_prompt_category():
    prompt_category = PromptCategory.objects.create(prompt_category_uuid=uuid.uuid4(), prompt_category_name='Classification'+str(uuid.uuid4()))
    return prompt_category

def create_prompt_test_data():
    # Create a valid prompt instance
    prompt_category = create_prompt_category()

    prompt_template, _ = create_prompt_template_test_data()
    prompt_template_uuid = str(prompt_template.prompt_template_uuid)
    prompt_details_json = {
        "prompt_template_uuid": prompt_template_uuid,
        "SYSTEM": "system_prompt for template name 01",
        "CONTEXT": "context_prompt for template name 01",
        "DISPLAY": "display_prompt for template name 01",
        "REMEMBER": "remember_prompt for template name 01"
    }
    application , customer = create_customer_application_instances()
    test_prompt = Prompt.objects.create(prompt_uuid=uuid.uuid4(), prompt_name="Test Prompt"+str(uuid.uuid4()),
                                        prompt_details_json=prompt_details_json, prompt_category_uuid=prompt_category,
                                        customer_uuid=customer,
                                        application_uuid=application,
                                        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562")
    prompt_uuid = uuid.uuid4()
    prompt = Prompt.objects.create(prompt_uuid=prompt_uuid, prompt_name="Prompt-1"+str(uuid.uuid4()),
                                   prompt_details_json=prompt_details_json, prompt_category_uuid=prompt_category,
                                   customer_uuid=customer, application_uuid=application,
                                   created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                   updated_by="508825ca-5e1b-47ab-920c-63c7ca721562")
    deleted_prompt = Prompt.objects.create(prompt_uuid=uuid.uuid4(), prompt_name="Deleted Prompt"+str(uuid.uuid4()),
                                           prompt_details_json=prompt_details_json, prompt_category_uuid=prompt_category,
                                           customer_uuid=customer,
                                           application_uuid=application,
                                           created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
                                           updated_by="508825ca-5e1b-47ab-920c-63c7ca721562", status=False,is_deleted=True)

    return prompt, deleted_prompt , prompt_category , test_prompt


def create_scope_test_data():
    # Intent dimension and Geography dimension with children
    *_, dimension_mapping = create_dimension_test_data()

    application, customer = dimension_mapping.application_uuid, dimension_mapping.customer_uuid
    user_uuid = uuid.uuid4()

    # Intent and its dimension value
    intent = DimensionType.objects.create(
        dimension_type_uuid=uuid.uuid4(),
        dimension_type_name="INTENT",
        is_default=True,
        created_by=user_uuid,
        updated_by=user_uuid
    )

    intent1 = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="intent1",
        dimension_type_uuid=intent,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    intent1_mapping = DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=intent1,
        description="Description for intent1",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    return intent1_mapping


def create_chat_configuration_test_data():
    #sample default data
    ChatConfiguration.objects.create(
        chat_configuration_uuid="9959a5b5-1952-4b90-8b28-7830d3406472",
        chat_configuration_name="Default Config",
        description="A default chat configuration",
        chat_details_json={"default_key": "default_value"},
        chat_configuration_provider="web",
        chat_configuration_type="landing_page",
        is_default=True,
        pre_created=True
    )
    ChatConfiguration.objects.create(
        chat_configuration_uuid="0059a5b5-1952-4b90-8b28-7830d3406472",
        chat_configuration_name="Default Config1",
        description="A default chat configuration",
        chat_details_json={"default_key": "default_value"},
        chat_configuration_provider="web",
        chat_configuration_type="intent_page",
        is_default=True,
        pre_created=True
    )

    test_data1 = ChatConfiguration.objects.create(
        chat_configuration_uuid="7759a5b5-1952-4b90-8b28-7830d3406472",
        chat_configuration_name="DEFAULT THEME",
        description=None,
        chat_details_json={
                "intent_page_configuration": {
                    "chat_avatar": {
                        "avatar": "",
                        "avatar_shape": "rounded",
                        "avatar_type": "ProfilePic",
                        "gender": "Female"
                    },
                    "intent_page_panel_configuration": {
                        "width": 360,
                        "height": 540,
                        "has_header": True,
                        "has_box_shadow": True,
                        "header": {
                            "title": "Chat Assistance",
                            "text_color": "#ffffff",
                            "background_fill_type": "Solid",
                            "background_color": "#363636",
                            "show_logo": True,
                            "show_close_button": True,
                            "enable_mute": True
                        },
                        "bot_message": {
                            "background_color": "#525252",
                            "text_color": "#ffffff",
                            "typing_indicator": "Typing...",
                            "is_speech_enabled": True,
                            "voice": "US English Male",
                            "suggestion_button_styles": "Popup Style"
                        },
                        "user_message": {
                            "background_color": "#404040",
                            "text_color": "#ffffff",
                            "delivery_status": True

                        },
                        "footer": {
                            "enable_attachments": True,
                            "enable_text": True,
                            "enable_speech": True,
                            "enable_send": True
                        }
                    }
                }

        },
        chat_configuration_provider="web",
        chat_configuration_type="intent_page",
        is_default=False,
        pre_created=False
    )

    application, customer = create_customer_application_instances()
    mapping = ChatConfigurationCustomerApplicationMapping.objects.create(
        mapping_uuid=uuid.uuid4(),
        chat_configuration_uuid=test_data1,
        application_uuid=application,
        customer_uuid=customer,
        status=True
    )


    return mapping,test_data1

def create_customer():
    customer_uuid = uuid.uuid4()
    customer=Customers.objects.create(
        cust_uuid=customer_uuid,
        cust_name='Test Customer',
        purchased_plan='Basic',
        email='test.customer@example.com',
        primary_contact='John Doe',
        secondary_contact='Jane Doe',
        address='123 Test Street',
        billing_address='456 Billing Ave',
        customer_details_json={"note": "This is a test customer."},
        status=True,
        created_by='admin',
        updated_by='admin'
    )
    return customer
def create_llm_provider():
    llm_provider_uuid = uuid.uuid4()
    user_uuid = uuid.uuid4()
    llm_provider = LLMProviderMetaData.objects.create(llm_provider_uuid=llm_provider_uuid,
                                                      llm_provider_name='Test LLM Provider',
                                                      llm_provider_details_json={"provider_key": "provider_value"},
                                                      status=True,
                                                      is_deleted=False, created_by=user_uuid, updated_by=user_uuid)
    return llm_provider
def create_llm_test_data():

    llm_configuration_details_json = {
        "llm_provider": "Azure Open AI",
        "api_key": "95058a9e99794e4689d179dd726e7eec",
        "deployment_name": "vassar-turbo35-16k",
        "model_name": "gpt-35-turbo-instruct",
        "api_base": "https://vassar-openai.openai.azure.com/",
        "api_type": "azure",
        "api_version": "2023-07-01-preview"
    }
    llm_provider=create_llm_provider()
    customer_uuid=create_customer()
    user_uuid = uuid.uuid4()
    default_llm = LLMConfiguration.objects.create(llm_configuration_uuid=uuid.uuid4(), llm_configuration_name='default_llm', llm_provider_uuid=llm_provider, llm_configuration_details_json=llm_configuration_details_json,
                                    is_default = True, created_by=user_uuid, updated_by=user_uuid)
    llm = LLMConfiguration.objects.create(llm_configuration_uuid=uuid.uuid4(), llm_configuration_name='llm_configuration_name', llm_provider_uuid=llm_provider, llm_configuration_details_json=llm_configuration_details_json,
                                    is_default = True, created_by=user_uuid, updated_by=user_uuid)

    return llm,customer_uuid,llm_provider

def create_assign_organization_test_data():
    llm_configuration_details_json = {
        "llm_provider": "Azure Open AI",
        "api_key": "95058a9e99794e4689d179dd726e7eec",
        "deployment_name": "vassar-turbo35-16k",
        "model_name": "gpt-35-turbo-instruct",
        "api_base": "https://vassar-openai.openai.azure.com/",
        "api_type": "azure",
        "api_version": "2023-07-01-preview"
    }
    llm_provider=create_llm_provider()
    customer_uuid=create_customer()
    user_uuid = uuid.uuid4()
    llm = LLMConfiguration.objects.create(llm_configuration_uuid=uuid.uuid4(), llm_configuration_name='llm_configuration_name', llm_provider_uuid=llm_provider, llm_configuration_details_json=llm_configuration_details_json,
                                    is_default = True, created_by=user_uuid, updated_by=user_uuid)
    
    return llm,customer_uuid,llm_provider

def create_customer_client_data():
    user_uuid = uuid.uuid4()
    dimension_type = DimensionType.objects.create(
        dimension_type_uuid="102376df-081e-40b4-9d46-0528de49ac72",
        dimension_type_name="GEOGRAPHY",
        created_by=user_uuid,
        updated_by=user_uuid,
        is_default=True,
    )
    dimension = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="INDIA",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )
    application, customer = create_customer_application_instances()
    customer_client = CustomerClient.objects.create(
        customer_client_uuid=uuid.uuid4(),
        customer_client_name="Customer Client",
        customer_client_domain_name="vassarlabs1.com",
        customer_client_geography_uuid=dimension,
        customer_client_emails=["clientemail@vassarlabs1.com"],
        customer_client_address="123 New York, USA",
        customer_uuid=customer,
        status=True,
        is_deleted=False,
        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562"
    )
    test_customer_client = CustomerClient.objects.create(
        customer_client_uuid=uuid.uuid4(),
        customer_client_name="Test Customer Client",
        customer_client_domain_name="vassarlabs2.com",
        customer_client_geography_uuid=dimension,
        customer_client_emails=["clienttestemail@vassarlabs1.com"],
        customer_client_address="123 New York, USA",
        customer_uuid=customer,
        status=True,
        is_deleted=False,
        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562"
    )

    return customer,application, dimension , customer_client,test_customer_client

def create_customer_client_tier_mapping_data():

    application, customer = create_customer_application_instances()
    user_uuid = uuid.uuid4()


    dimension_type = DimensionType.objects.create(
        dimension_type_uuid=uuid.uuid4(),
        dimension_type_name="GEOGRAPHY",
        created_by=user_uuid,
        updated_by=user_uuid,
        is_default=True,
    )

    dimension = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="INDIA",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    dimension_mapping = DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=dimension,
        description="Description for India",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )
    test_customer_client = CustomerClient.objects.create(
        customer_client_uuid=uuid.uuid4(),
        customer_client_name="Test Customer Client",
        customer_client_domain_name="vassarlabs.com",
        customer_client_geography_uuid=dimension,
        customer_client_emails=["clienttestemail@vassarlabs.com"],
        customer_client_address="123 New York, USA",
        customer_uuid=customer,
        status=True,
        is_deleted=False,
        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562"
    )
    test_customer_client1 = CustomerClient.objects.create(
        customer_client_uuid=uuid.uuid4(),
        customer_client_name="Test Customer Client1",
        customer_client_domain_name="vassarlabs.com",
        customer_client_geography_uuid=dimension,
        customer_client_emails=["clienttestemail1@vassarlabs.com"],
        customer_client_address="123 New York, USA",
        customer_uuid=customer,
        status=True,
        is_deleted=False,
        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562"
    )

    testing_customer_client_tier_mapping1 = CustomerClientTierMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        customer_client_uuid=test_customer_client,
        tier_mapping_uuid=dimension_mapping,
        extractor_template_details_json={"template_key": "template_value"},  # Example JSON data
        created_by="test_creator",
        updated_by="test_updater"
    )
    return customer,application,testing_customer_client_tier_mapping1,dimension_mapping,test_customer_client1

def activity_dashboard_data():

    # Create a valid DimensionType instance
    dimension_type = DimensionType.objects.create(
        dimension_type_uuid='dimension_type1',
        dimension_type_name='dim_type_name',
        is_deleted=False,
        is_default=True,
        status=True,
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
        created_by=None,
        updated_by=None
    )
    # Create a valid Dimension instance
    dimension = Dimension.objects.create(
        dimension_uuid='dimension_uuid1',
        dimension_name='dimension_name1',
        dimension_type_uuid=dimension_type,
        is_default=False,
        is_deleted=False,
        status=True,
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
        created_by='admin',
        updated_by='admin'
    )
    # Create a dummy Customers instance
    customer = Customers.objects.create(
        cust_uuid="af4bf2d8-fd3e-4b40-902a-1217952c0ff3",  
        cust_name='cust_name',
        purchased_plan=None, 
        email='email1',
        primary_contact='{"country":{"name":"United States","dial_code":"+1","code":"US","flag":"https://flagcdn.com/w320/us.png"},"phoneNumber":"2126565767"}',
        secondary_contact=None, 
        address='Hyd',
        billing_address='-',
        customer_details_json={
            "dropDownConfig": [
                {
                    "label": "logo",
                    "values": ["https://vassarstorage.blob.core.windows.net/customer-logos/0s0d7r24_1725883704669.jpg"]
                }
            ]
        },
        status=True,
        created_ts=datetime(2024, 8, 3, 7, 38, 32),
        updated_ts=datetime(2024, 8, 3, 7, 38, 32),
        created_by=None,  
        updated_by=None  
    )

    # Create a CustomerClient instance
    customer_client = CustomerClient.objects.create(
        customer_client_uuid= 'cust_client1',
        customer_client_geography_uuid= dimension,
        customer_client_domain_name= 'walmartservicechannel@gmail.com',
        customer_client_name= 'Walmart',
        customer_client_emails = ['walmartservicechannel@gmail.com'],
        customer_uuid=customer,
        customer_client_address='123 Walmart St, Bentonville, AR',  # Add address if applicable
        status=True,
        is_deleted=False,
        inserted_ts=datetime(2024, 8, 6, 7, 23, 10),
        updated_ts=datetime(2024, 8, 6, 7, 23, 10),
        created_by='admin',  # Example user
        updated_by='admin'   # Example user
    )

    # Create a dummy Applications instance
    application = Applications.objects.create(
        application_uuid="e912de61-96c0-4582-89aa-64de807a4635",  # Generate a unique UUID for application_id
        application_name='application_name1',  # Example application name
        application_url='https://staging.testapp.ai/408c7d88-82dc-4cb1-8a7c-2eca5ce2b323',  # Example application URL
        scope_end_point='https://staging.testapp.ai/api/platform',  # Example scope endpoint
        description='Test Description for Orders Application',  # Example description
        status=True,  # Status is active (True)
        created_ts=datetime(2024, 9, 27, 9, 0, 0),  # Example created timestamp
        updated_ts=datetime(2024, 9, 27, 9, 30, 0),  # Example updated timestamp
        created_by=None,  # Example created_by user
        updated_by=None   # Example updated_by user
    )
    user = UserMgmtUsers.objects.create(
        user_id="cdc764ee-affd-420a-a8b7-92d24d8f295e",
        first_name="Test",
        last_name="User",
        email_id="testuser@example.com",
        username="testuser123",
        mobile_number="1234567890",
        status=True,
        auth_type="password",
        password_hash="hashed_password_123"
    )

    dimension_details_json = {
                    "intent": {
                        "name": "HR POLICY"
                    },
                    "sentiment": {
                        "name": "NEUTRAL"
                    }
                }

    ticket = Ticket.objects.create(
        ticket_uuid=uuid.uuid4(),
        ticket_external_id='EM09076',
        channel='email',
        client_name='Test Sender',
        email_id='testsender@example.com',
        dimension_details_json=dimension_details_json,
        status='need_assistance',
        application_uuid=application,
        customer_uuid=customer,
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
        updated_ts=datetime(2024, 9, 27, 10, 0, 0)
    )

    user_ticket_mapping = UserTicketMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        ticket_uuid = ticket,
        user_id=user,
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
        updated_ts=datetime(2024, 9, 27, 10, 0, 0)
    )

    # Create a dummy EmailConversation instance
    email_conversation = EmailConversation.objects.create(
        email_conversation_uuid="email_conversation_uuid1",  
        customer_client_uuid=customer_client,  
        email_conversation_flow_status='need_assistance', 
        email_activity={"timeline": {"<CACVtJF9AqbAWQZ16EPfD0+97bVXMhnJpQtRXqZhrr=ghoNxm8g@mail.gmail.com>": [{"Email_Sent": 1722929001000, "Email_Received": 1722929051220, "Intent_Classified": 1722929054467}]},"email_summary":"sadkjdhkhdiwuewiej"},
        dimension_uuid=dimension,  
        application_uuid=application, 
        customer_uuid=customer, 
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),  
        updated_ts=datetime(2024, 9, 27, 12, 0, 0),  
        created_by='test_user',  
        updated_by='test_user' ,
        ticket_uuid = Ticket(ticket.ticket_uuid)

    )

    # Create a dummy Email instance
    email = Email.objects.create(
        email_uuid="email_uuid1", 
        email_conversation_uuid=email_conversation,  
        email_status='email_status1',  
        email_flow_status='Open',  
        dimension_action_json={"action": "ai_assisted", "intent": {"name": "PURCHASE_ORDER", "uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": {"name": "NEW_PO", "uuid": "9e563c2c-a961-456f-9326-202a1f2c0cce"}}, "geography": {"country": {"name": "United States", "uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": {"name": "Texas", "uuid": "e1ce93aa-33ea-47a4-aafb-d50d355cdba9"}}}, "sentiment": {"name": "NEUTRAL", "uuid": "1e141e6f-33ef-4a0b-870d-99158b0d4174"}, "customer_tier": {"name": "Tier 1", "uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"}, "customer_client": {"name": "Spencertech", "uuid": "2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22"}},  # Sample JSON field
        role_uuid=None,  
        parent_uuid=None,  
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),  
        updated_ts=datetime(2024, 9, 27, 10, 0, 0),  
        created_by=None,  
        updated_by=None   
    )

    # Create a dummy EmailInfoDetail instance
    email_info_detail = EmailInfoDetail.objects.create(
        email_info_uuid="email_info_uuid1",
        email_uuid=email,
        email_subject="Test PO Subject",
        email_body_url="https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-17/Email_body/3a3a2170-e554-429d-bf43-69cc46abae35.txt",
        attachments=[],
        sender="testsender@example.com",
        sender_name="Test Sender",
        email_type="email",
        recipient_name="Test Recipient",
        recipient="testrecipient@example.com",
        recipients=[{"name": "Test Recipient", "email": "testrecipient@example.com"}],
        cc_recipients=[],
        bcc_recipients=[],
        email_body_summary="Here is a test PO summary.",
        email_meta_body="Test email meta data",
        html_body="https://example.com/email_body.html",
        extracted_order_details="https://example.com/order_details.json",
        validated_details="Validated JSON Test",
        verified=True
    )

    return dimension_type, dimension, customer, customer_client, application,user, email_conversation, email, email_info_detail , ticket

def create_customer_client_user_data():
    cust,app,dimension,client,_ = create_customer_client_data()
    json = {
        "domain":"testcustomeruser@gmail.com",
        "address":"newyork"
    }
    customer_client_user1 = ClientUser.objects.create(
        client_user_uuid=uuid.uuid4(),
        first_name="Customer Client 1",
        last_name="last name",
        email_id="testcustomeruser1@gmail.com",
        geography_uuid=dimension,
        customer_client_uuid=client,
        user_info_json=json,
        status=True,
        is_deleted=False,
        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562"
    )

    customer_client_user2 = ClientUser.objects.create(
        client_user_uuid=uuid.uuid4(),
        first_name="Customer Client 2",
        last_name="last name",
        email_id="testcustomeruser2@gmail.com",
        geography_uuid=dimension,
        customer_client_uuid=client,
        user_info_json=json,
        status=True,
        is_deleted=False,
        created_by="508825ca-5e1b-47ab-920c-63c7ca721562",
        updated_by="508825ca-5e1b-47ab-920c-63c7ca721562"
    )

    return dimension,client,customer_client_user1,customer_client_user2

def insert_test_intents():
    user_uuid = str(uuid.uuid4())
    dim_type1 = DimensionType.objects.create(
        dimension_type_uuid= str(uuid.uuid4()) ,
        dimension_type_name="INTENT",
        created_by=user_uuid,
        updated_by=user_uuid,
        is_default=True,
    )

    dim_type2 = DimensionType.objects.create(
        dimension_type_uuid=str(uuid.uuid4()),
        dimension_type_name="SUB_INTENT",
        created_by=user_uuid,
        updated_by=user_uuid,
        is_default=True,
    )


    dim_1 = Dimension.objects.create(
        dimension_uuid='dimension_uuid1',
        dimension_name='ORDER_STATUS',
        dimension_type_uuid= dim_type1,
        is_default=False,
        is_deleted=False,
        status=True,
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
        created_by='admin',
        updated_by='admin'
    )
      
    dim_2 = Dimension.objects.create(
        dimension_uuid='dimension_uuid2',
        dimension_name='STOCK_STATUS',
        dimension_type_uuid=dim_type2,
        is_default=False,
        is_deleted=False,
        status=True,
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
        created_by='admin',
        updated_by='admin'
    )
    application, customer = create_customer_application_instances()
    dimension_mapping = DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid= dim_1,
        description="Order status Description",
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    dimension_mapping = DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=dim_2,
        description="stock status Description",
        dimension_details_json = {"training_phrases_count" : 1} ,
        parent_dimension_uuid = dim_1,
        application_uuid=application,
        customer_uuid=customer,
        created_by=user_uuid,
        updated_by=user_uuid,

    )
    return application, customer


def merged_ticket_data():
    # Create a valid DimensionType instance
    dimension_type = DimensionType.objects.create(
        dimension_type_uuid=str(uuid.uuid4()),
        dimension_type_name='dim_type_name'+str(uuid.uuid4()),
        is_deleted=False,
        is_default=True,
        status=True,
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
        created_by=None,
        updated_by=None
    )
    # Create a valid Dimension instance
    dimension = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name='dimension_name1'+str(uuid.uuid4()),
        dimension_type_uuid=dimension_type,
        is_default=False,
        is_deleted=False,
        status=True,
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
        created_by='admin',
        updated_by='admin'
    )
    # Create a dummy Customers instance
    customer = Customers.objects.create(
        cust_uuid=str(uuid.uuid4()),
        cust_name='cust_name'+str(uuid.uuid4()),
        purchased_plan=None,
        email='email1'+str(uuid.uuid4()),
        primary_contact='{"country":{"name":"United States","dial_code":"+1","code":"US","flag":"https://flagcdn.com/w320/us.png"},"phoneNumber":"2126565000"}',
        secondary_contact=None,
        address='Hyd',
        billing_address='-',
        customer_details_json={
            "dropDownConfig": [
                {
                    "label": "logo",
                    "values": ["https://vassarstorage.blob.core.windows.net/customer-logos/0s0d7r24_1725883704669.jpg"]
                }
            ]
        },
        status=True,
        created_ts=datetime(2024, 8, 3, 7, 38, 32),
        updated_ts=datetime(2024, 8, 3, 7, 38, 32),
        created_by=None,
        updated_by=None
    )

    # Create a CustomerClient instance
    customer_client = CustomerClient.objects.create(
        customer_client_uuid=str(uuid.uuid4()),
        customer_client_geography_uuid=dimension,
        customer_client_domain_name='walmartservicechannel@gmail.com',
        customer_client_name='Walmart'+str(uuid.uuid4()),
        customer_uuid=customer,
        customer_client_emails=['walmartservicechannel@gmail.com'],
        customer_client_address='123 Walmart St, Bentonville, AR',  # Add address if applicable
        status=True,
        is_deleted=False,
        inserted_ts=datetime(2024, 8, 6, 7, 23, 10),
        updated_ts=datetime(2024, 8, 6, 7, 23, 10),
        created_by='admin',  # Example user
        updated_by='admin'  # Example user
    )

    # Create a dummy Applications instance
    application = Applications.objects.create(
        application_uuid=str(uuid.uuid4()),  # Generate a unique UUID for application_id
        application_name='application_name1'+str(uuid.uuid4()),  # Example application name
        application_url='https://staging.testapp.ai/'+str(uuid.uuid4()),  # Example application URL
        scope_end_point='https://staging.testapp.ai/api/platform',  # Example scope endpoint
        description='Test Description for Orders Application',  # Example description
        status=True,  # Status is active (True)
        created_ts=datetime(2024, 9, 27, 9, 0, 0),  # Example created timestamp
        updated_ts=datetime(2024, 9, 27, 9, 30, 0),  # Example updated timestamp
        created_by=None,  # Example created_by user
        updated_by=None  # Example updated_by user
    )
    user = UserMgmtUsers.objects.create(
        user_id=str(uuid.uuid4()),
        first_name="Test",
        last_name="User",
        email_id="testuser12233@example.com",
        username="testuser1233",
        mobile_number="1234560000",
        status=True,
        auth_type="password",
        password_hash="hashed_password_123"
    )

    dimension_details_json = {
        "intent": {
            "name": "HR POLICY"
        },
        "sentiment": {
            "name": "NEUTRAL"
        }
    }

    email_tickets = []
    for i in range(3):
        email_ticket1 = Ticket.objects.create(
            ticket_uuid=str(uuid.uuid4()),
            ticket_external_id='EM00123'+str(i),
            channel='email',
            client_name='Test Sender',
            email_id='testsender@example.com',
            dimension_details_json=dimension_details_json,
            status='need_assistance',
            application_uuid=application,
            customer_uuid=customer,
            inserted_ts="2024-12-10 05:48:22.240069",
            updated_ts="2024-12-10 05:48:22.240069"
        )

        # Create a dummy EmailConversation instance
        email_conversation = EmailConversation.objects.create(
            email_conversation_uuid= str(uuid.uuid4()),
            customer_client_uuid=customer_client,
            email_conversation_flow_status='need_assistance',
            email_activity={
                "timeline": {"<CACVtJF9AqbAWQZ16EPfD0+97bVXMhnJpQtRXqZhrr=ghoNxm8g@mail.gmail.com>": [{"Email_Sent": 1722929001000, "Email_Received": 1722929051220, "Intent_Classified": 1722929054467}]},"email_summary":"sadkjdhkhdiwuewiej"},
            dimension_uuid=dimension,
            application_uuid=application,
            customer_uuid=customer,
            inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
            updated_ts=datetime(2024, 9, 27, 12, 0, 0),
            created_by='test_user',
            updated_by='test_user',
            ticket_uuid=Ticket(email_ticket1.ticket_uuid)

        )

        # Create a dummy Email instance
        email = Email.objects.create(
            email_uuid=str(uuid.uuid4()),
            email_conversation_uuid=email_conversation,
            email_status='email_status1',
            email_flow_status='Open',
            dimension_action_json={"action": "ai_assisted",
                                   "intent": {"name": "PURCHASE_ORDER", "uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": {"name": "NEW_PO", "uuid": "9e563c2c-a961-456f-9326-202a1f2c0cce"}},
                                   "geography": {
                                       "country": {"name": "United States", "uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": {"name": "Texas", "uuid": "e1ce93aa-33ea-47a4-aafb-d50d355cdba9"}}},
                                   "sentiment": {"name": "NEUTRAL", "uuid": "1e141e6f-33ef-4a0b-870d-99158b0d4174"}, "customer_tier": {"name": "Tier 1", "uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"},
                                   "customer_client": {"name": "Spencertech", "uuid": "2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22"}},  # Sample JSON field
            role_uuid=None,
            parent_uuid=None,
            inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
            updated_ts=datetime(2024, 9, 27, 10, 0, 0),
            created_by=None,
            updated_by=None
        )

        # Create a dummy EmailInfoDetail instance
        email_info_detail = EmailInfoDetail.objects.create(
            email_info_uuid=str(uuid.uuid4()),
            email_uuid=email,
            email_subject="Test PO Subject",
            email_body_url="https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-17/Email_body/3a3a2170-e554-429d-bf43-69cc46abae35.txt",
            attachments=[],
            sender="testsender@example.com",
            sender_name="Test Sender",
            email_type="email",
            recipient_name="Test Recipient",
            recipient="testrecipient@example.com",
            recipients=[{"name": "Test Recipient", "email": "testrecipient@example.com"}],
            cc_recipients=[],
            bcc_recipients=[],
            email_body_summary="Here is a test PO summary.",
            email_meta_body="Test email meta data",
            html_body="https://example.com/email_body.html",
            extracted_order_details="https://example.com/order_details.json",
            validated_details="Validated JSON Test",
            verified=True
        )
        email_tickets.append(email_ticket1)

    chat_tickets = []
    # Sample message details
    message_details = [
        {
            "id": str(uuid.uuid4()),  # Generate a unique ID for each message
            "user_id": "ghi789",
            "csr_id": None,  # Indicates this message is from the bot
            "source": "bot",
            "message_marker": "DELIVERED",
            "message_text": "Hello, how can I help you?",
            "media_url": "",
            "parent_message_uuid": None,
            "created_at": "2025-01-04T05:19:27.200377+00:00",  # Use the current timestamp
            "dimension_action_json":
                {
                    "dimensions": [{
                        "dimension": "Intent",
                        "value": "Greeting"
                    }],
                }

        }
    ]

    # Sample conversation feedback transaction
    conversation_feedback_transaction = {
        "satisfaction_level": "Average",
        "additional_comments": "Great service!"
    }

    # Sample conversation stats
    conversation_stats = [{
        "conversationStartTime": datetime.now().isoformat(),  # Use the current timestamp
        "humanHandoffTime": None,
        "firstAgentAssignmentTime": None,
        "firstAgentMessageTime": None,
        "lastUserMessageTime": None,
        "lastAgentMessageTime": None,
        "conversationResolutionTime": None
    }]
    for i in range(3):
        chat_ticket1 = Ticket.objects.create(
            ticket_uuid=str(uuid.uuid4()),
            ticket_external_id='CH00123' + str(i),
            channel='Chat',
            client_name='Test Sender',
            email_id='testsender@example.com',
            dimension_details_json=dimension_details_json,
            status='need_assistance',
            application_uuid=application,
            customer_uuid=customer,
            inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
            updated_ts=datetime(2024, 9, 27, 10, 0, 0)
        )

        # Create a dummy ChatConversation instance
        chat_conversation = ChatConversation.objects.create(
            chat_conversation_uuid=str(uuid.uuid4()),  # Generate a unique UUID for the conversation
            user_details_json={"user_id": "12345", "user_name": "John Doe"},
            conversation_status="active",
            csr_info_json={"csr_id": "54321", "csr_name": "Jane Smith"},
            csr_hand_off=False,
            conversation_stats_json=conversation_stats,
            conversation_feedback_transaction_json=conversation_feedback_transaction,
            summary="This is a summary of the conversation.",
            application_uuid=application,  # Assign the Applications instance here
            customer_uuid=customer,  # Assign the Customers instance here
            message_details_json=message_details,
            ticket_uuid=chat_ticket1,
            inserted_ts=datetime.now(),  # Use the current timestamp
            updated_ts=datetime.now()  # Use the current timestamp
        )

        chat_tickets.append(chat_ticket1)

    merged_ticket1 = Ticket.objects.create(
        ticket_uuid=str(uuid.uuid4()),
        ticket_external_id='EM12345',
        channel='email',
        client_name='Test Sender',
        email_id='testsender@example.com',
        dimension_details_json=dimension_details_json,
        status='need_assistance',
        application_uuid=application,
        customer_uuid=customer,
        inserted_ts="2024-12-10 05:48:22.240069",
        updated_ts="2024-12-10 05:48:22.240069"
    )

    # Create a dummy EmailConversation instance
    email_conversation = EmailConversation.objects.create(
        email_conversation_uuid=str(uuid.uuid4()),
        customer_client_uuid=customer_client,
        email_conversation_flow_status='need_assistance',
        email_activity={
            "timeline": {"<CACVtJF9AqbAWQZ16EPfD0+97bVXMhnJpQtRXqZhrr=ghoNxm8g@mail.gmail.com>": [{"Email_Sent": 1722929001000, "Email_Received": 1722929051220, "Intent_Classified": 1722929054467}]},"email_summary":"sadkjdhkhdiwuewiej"},
        dimension_uuid=dimension,
        application_uuid=application,
        customer_uuid=customer,
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
        updated_ts=datetime(2024, 9, 27, 12, 0, 0),
        created_by='test_user',
        updated_by='test_user',
        ticket_uuid=Ticket(merged_ticket1.ticket_uuid)
    )

    email = Email.objects.create(
        email_uuid=str(uuid.uuid4()),
        email_conversation_uuid=email_conversation,
        email_status='email_status1',
        email_flow_status='Open',
        dimension_action_json={"action": "ai_assisted",
                               "intent": {"name": "PURCHASE_ORDER", "uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": {"name": "NEW_PO", "uuid": "9e563c2c-a961-456f-9326-202a1f2c0cce"}},
                               "geography": {
                                   "country": {"name": "United States", "uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": {"name": "Texas", "uuid": "e1ce93aa-33ea-47a4-aafb-d50d355cdba9"}}},
                               "sentiment": {"name": "NEUTRAL", "uuid": "1e141e6f-33ef-4a0b-870d-99158b0d4174"}, "customer_tier": {"name": "Tier 1", "uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"},
                               "customer_client": {"name": "Spencertech", "uuid": "2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22"}},  # Sample JSON field
        role_uuid=None,
        parent_uuid=None,
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
        updated_ts=datetime(2024, 9, 27, 10, 0, 0),
        created_by=None,
        updated_by=None
    )

    email_info_detail = EmailInfoDetail.objects.create(
        email_info_uuid=str(uuid.uuid4()),
        email_uuid=email,
        email_subject="Test PO Subject",
        email_body_url="https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-17/Email_body/3a3a2170-e554-429d-bf43-69cc46abae35.txt",
        attachments=[],
        sender="testsender@example.com",
        sender_name="Test Sender",
        email_type="email",
        recipient_name="Test Recipient",
        recipient="testrecipient@example.com",
        recipients=[{"name": "Test Recipient", "email": "testrecipient@example.com"}],
        cc_recipients=[],
        bcc_recipients=[],
        email_body_summary="Here is a test PO summary.",
        email_meta_body="Test email meta data",
        html_body="https://example.com/email_body.html",
        extracted_order_details="https://example.com/order_details.json",
        validated_details="Validated JSON Test",
        verified=True
    )

    EmailConversationView.objects.create(
        email_uuid = email.email_uuid,
        email_conversation_uuid = email.email_conversation_uuid.email_conversation_uuid,
        email_subject = email_info_detail.email_subject,
        email_status= email.email_status,
        dimension_action_json = email.dimension_action_json,
        parent_uuid = email.parent_uuid,
        inserted_ts = email.inserted_ts,
        updated_ts = email.updated_ts,
        email_info_uuid = email_info_detail.email_info_uuid,
        email_body_url = email_info_detail.email_body_url,
        attachments = email_info_detail.attachments,
        sender = email_info_detail.sender,
        sender_name = email_info_detail.sender_name,
        recipient = email_info_detail.recipient,
        recipients = email_info_detail.recipients,
        cc_recipients = email_info_detail.cc_recipients,
        bcc_recipients = email_info_detail.bcc_recipients,
        email_body_summary = email_info_detail.email_body_summary,
        email_meta_body = email_info_detail.email_meta_body,
        extracted_order_details = email_info_detail.extracted_order_details,
        validated_details = email_info_detail.validated_details,
        verified = email_info_detail.verified,
        email_flow_status = email.email_flow_status,
        email_activity = email_conversation.email_activity,
        ticket_uuid = merged_ticket1.ticket_uuid
    )

    ChatConversation.objects.create(
        chat_conversation_uuid=str(uuid.uuid4()),  # Generate a unique UUID for the conversation
        user_details_json={"user_id": "12345", "user_name": "John Doe"},
        conversation_status="active",
        csr_info_json={"csr_id": "54321", "csr_name": "Jane Smith"},
        csr_hand_off=False,
        conversation_stats_json=conversation_stats,
        conversation_feedback_transaction_json=conversation_feedback_transaction,
        summary="This is a summary of the conversation.",
        application_uuid=application,  # Assign the Applications instance here
        customer_uuid=customer,  # Assign the Customers instance here
        message_details_json=message_details,
        ticket_uuid=merged_ticket1,
        inserted_ts=datetime.now(),  # Use the current timestamp
        updated_ts=datetime.now()  # Use the current timestamp
    )

    merged_ticket2 = Ticket.objects.create(
        ticket_uuid=str(uuid.uuid4()),
        ticket_external_id='EM12346',
        channel='email',
        client_name='Test Sender',
        email_id='testsender@example.com',
        dimension_details_json=dimension_details_json,
        status='need_assistance',
        application_uuid=application,
        customer_uuid=customer,
        inserted_ts="2024-12-10 05:48:22.240069",
        updated_ts="2024-12-10 05:48:22.240069"
    )

    # Create a dummy EmailConversation instance
    email_conversation = EmailConversation.objects.create(
        email_conversation_uuid=str(uuid.uuid4()),
        customer_client_uuid=customer_client,
        email_conversation_flow_status='need_assistance',
        email_activity={
            "timeline": {"<CACVtJF9AqbAWQZ16EPfD0+97bVXMhnJpQtRXqZhrr=ghoNxm8g@mail.gmail.com>": [{"Email_Sent": 1722929001000, "Email_Received": 1722929051220, "Intent_Classified": 1722929054467}]},
            "email_summary":"sadkjdhkhdiwuewiej"},
        dimension_uuid=dimension,
        application_uuid=application,
        customer_uuid=customer,
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
        updated_ts=datetime(2024, 9, 27, 12, 0, 0),
        created_by='test_user',
        updated_by='test_user',
        ticket_uuid=merged_ticket2
    )

    Email.objects.create(
        email_uuid=str(uuid.uuid4()),
        email_conversation_uuid=email_conversation,
        email_status='email_status1',
        email_flow_status='Open',
        dimension_action_json={"action": "ai_assisted",
                               "intent": {"name": "PURCHASE_ORDER", "uuid": "a6314d6e-0fdb-49c2-a4d2-6b60f3365a4d", "sub_intent": {"name": "NEW_PO", "uuid": "9e563c2c-a961-456f-9326-202a1f2c0cce"}},
                               "geography": {
                                   "country": {"name": "United States", "uuid": "d1d778b3-d9d6-4ef3-be92-afcce4c68063", "state": {"name": "Texas", "uuid": "e1ce93aa-33ea-47a4-aafb-d50d355cdba9"}}},
                               "sentiment": {"name": "NEUTRAL", "uuid": "1e141e6f-33ef-4a0b-870d-99158b0d4174"}, "customer_tier": {"name": "Tier 1", "uuid": "90d7fdc4-6fda-4eea-ae17-acbbb0255d92"},
                               "customer_client": {"name": "Spencertech", "uuid": "2b965e4e-f3a5-4e9b-8fb7-f6706fc06c22"}},  # Sample JSON field
        role_uuid=None,
        parent_uuid=None,
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),
        updated_ts=datetime(2024, 9, 27, 10, 0, 0),
        created_by=None,
        updated_by=None
    )

    ChatConversation.objects.create(
        chat_conversation_uuid=str(uuid.uuid4()),  # Generate a unique UUID for the conversation
        user_details_json={"user_id": "12345", "user_name": "John Doe"},
        conversation_status="active",
        csr_info_json={"csr_id": "54321", "csr_name": "Jane Smith"},
        csr_hand_off=False,
        conversation_stats_json=conversation_stats,
        conversation_feedback_transaction_json=conversation_feedback_transaction,
        summary="This is a summary of the conversation.",
        application_uuid=application,  # Assign the Applications instance here
        customer_uuid=customer,  # Assign the Customers instance here
        message_details_json=message_details,
        ticket_uuid=merged_ticket2,
        inserted_ts=datetime.now(),  # Use the current timestamp
        updated_ts=datetime.now()  # Use the current timestamp
    )

    ticket_with_no_conversations = Ticket.objects.create(
        ticket_uuid=str(uuid.uuid4()),
        ticket_external_id='EM12347',
        channel='email',
        client_name='Test Sender',
        email_id='testsender@example.com',
        dimension_details_json=dimension_details_json,
        status='need_assistance',
        application_uuid=application,
        customer_uuid=customer,
        inserted_ts="2024-12-10 05:48:22.240069",
        updated_ts="2024-12-10 05:48:22.240069"
    )

    return email_tickets[0],email_tickets[1],email_tickets[2],chat_tickets[0],chat_tickets[1],chat_tickets[2],application,customer,user,merged_ticket1,merged_ticket2,ticket_with_no_conversations
