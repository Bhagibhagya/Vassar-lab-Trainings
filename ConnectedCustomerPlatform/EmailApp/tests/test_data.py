import uuid
from datetime import datetime

from ConnectedCustomerPlatform.wsgi import application
from DatabaseApp.models import Applications, CustomerClient, Customers, Dimension, DimensionType, Email, EmailConversation, EmailConversationView, EmailInfoDetail, EmailServer, UserEmailSetting, \
    UserMgmtUsers, Ticket

from dotenv import load_dotenv

load_dotenv()

def create_test_data():
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
        cust_uuid='af4bf2d8-fd3e-4b40-902a-1217952c0ff3',  
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
        customer_uuid=customer,
        customer_client_emails=["clienttestemail1@vassarlabs.com"],
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
        application_uuid='e912de61-96c0-4582-89aa-64de807a4635',  # Generate a unique UUID for application_id
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
        user_id="4d337ccb-1879-4557-b27b-158cd5e264df",
        first_name="Sensormatic",
        last_name="CSR",
        email_id="sensormaticuser@gmail.com",
        username="sensormaticuser",
        mobile_number='{"country":{"name":"United States","dial_code":"+1","code":"US","flag":"https://flagcdn.com/w320/us.png"}, "phoneNumber":"2019998999"}',
        title=None,  
        user_details_json='{"status":"Offline"}', 
        customer_name="Sensormatic",
        customer_id="af4bf2d8-fd3e-4b40-902a-1217952c0ff3",
        status=True,
        auth_type="vassar",
        password_hash="gAAAAABm4uLnvAGdOPszSbhzuZq_omdDIk9VDQzMX18OghuVDB65kpFD-y9ISEKU6eKs9NidExEU3UFg4Gr3VQqaG2jzdbUcKW-a5jUIIn8jRagRB35dfgI=", 
        activation_ts=None,  
        last_login_ts="2024-09-17 13:58:54.022",
        created_by=None,  
        updated_by=None 
    )

    # Create a dummy EmailConversation instance
    email_conversation = EmailConversation.objects.create(
        email_conversation_uuid="email_conversation_uuid1",  
        customer_client_uuid=customer_client,  
        email_conversation_flow_status='in_progress', 
        email_activity=None, 
        dimension_uuid=dimension,  
        application_uuid=application, 
        customer_uuid=customer, 
        inserted_ts=datetime(2024, 9, 27, 10, 0, 0),  
        updated_ts=datetime(2024, 9, 27, 12, 0, 0),  
        created_by='test_user',  
        updated_by='test_user',
        assigned_to=user   
    )

    # Create a dummy Email instance
    email = Email.objects.create(
        email_uuid="email_uuid1", 
        email_conversation_uuid=email_conversation,  
        email_status='email_status1',  
        email_flow_status='email_flow_status1',  
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
        email_body_url="https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-06/Attachments/c584d23f-eb68-459f-bd56-e45c0e186a71.json",
        attachments=["https://example.com/attachment.pdf"],
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

    email_server = EmailServer.objects.create(
        email_server_uuid="20a91f45-abd9-4f43-b85b-bf34b0b7deac",
        server_type="SMTP",
        server_url="smtp.gmail.com",
        email_provider_name="Gmail",
        port="587",
        is_deleted=False,
        is_default=True,
        status=True,
        created_by="system_user",
        updated_by="system_user"
    )


    user_email_setting = UserEmailSetting.objects.create(
        user_email_uuid="user_email_id",
        email_id="sensormaticservicechannel@gmail.com",
        encrypted_password="gAAAAABm4uLnvAGdOPszSbhzuZq_omdDIk9VDQzMX18OghuVDB65kpFD-y9ISEKU6eKs9NidExEU3UFg4Gr3VQqaG2jzdbUcKW-a5jUIIn8jRagRB35dfgI=",
        email_type="individual",
        email_details_json=None,  # Example without email details JSON
        is_primary_sender_address=True,
        application_uuid=application,
        customer_uuid=customer,
        status=True,
        is_deleted=False,
        last_read_ts="2024-09-17 14:05:09.688921",
        created_by=None,
        updated_by=None
    )

    ticket = Ticket.objects.create(
        ticket_uuid=uuid.uuid4(),
        ticket_external_id = 'EM09098',
        channel = 'email',
        client_name = 'Test Sender',
        email_id = 'testsender@example.com',
        status = 'Need Assistance',
        application_uuid = application,
        customer_uuid = customer,
        assigned_to = user,
        inserted_ts = datetime(2024, 9, 27, 10, 0, 0),
        updated_ts = datetime(2024, 9, 27, 10, 0, 0)
    )

    

    return dimension_type, dimension, customer_client, application, user,customer, email, email_conversation, email_info_detail, email_server, user_email_setting , ticket