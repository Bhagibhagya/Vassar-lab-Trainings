import uuid
from DBServices.models import Entities
import uuid
from datetime import datetime
from DatabaseApp.models import ChatConversation, Applications, Customers, Ticket, UserMgmtUsers
from ChatBot.dao.impl.customer_dao_impl import CustomerDaoImpl

from ChatBot.dao.impl.application_dao_impl import ApplicationDaoImpl

from ChatBot.dao.impl.role_dao_impl import RoleDaoImpl

from ChatBot.utils import create_customer_dataclass_object, create_application_dataclass_object, create_role_dataclass_object, create_user_dataclass_object, get_collection_names

from ChatBot.constant.constants import TestConstants, TestKnowledgeSourceConstants, TestSmeConstants

from ChatBot.dao.impl.user_dao_impl import UserDaoImpl
from DatabaseApp.models import Applications, Customers
from DatabaseApp.models import DimensionType, Dimension, DimensionCustomerApplicationMapping, \
    CustomerApplicationMapping
from DatabaseApp.models import DimensionTypeCustomerApplicationMapping
from ChatBot.dao.impl.entity_dao_impl import EntityDaoImpl
from ChatBot.dao.impl.knowledge_sources_dao_impl import KnowledgeSourcesDaoImpl
from ChatBot.dao.impl.error_dao_impl import ErrorCorrectionDaoImpl
from ChatBot.dao.impl.sme_dao_impl import SMEDaoImpl
from AIServices.VectorStore.chromavectorstore import chroma_obj

customer_dao = CustomerDaoImpl()
application_dao = ApplicationDaoImpl()
role_dao = RoleDaoImpl()
user_dao = UserDaoImpl()


entity_dao = EntityDaoImpl()
knowledge_sources_dao = KnowledgeSourcesDaoImpl()
error_dao = ErrorCorrectionDaoImpl()
sme_dao = SMEDaoImpl()

def create_department_test_data():
    customer_create_result = create_customer_test_data()
    application_create_result = create_application_test_data()
    user_create_result = create_user_test_data_by_customer_id_and_customer_name(customer_uuid=customer_create_result.cust_uuid, customer_name=customer_create_result.cust_name)
    role_create_result = create_role_test_data_by_application_id_and_customer_id(application_uuid=application_create_result.application_uuid, customer_uuid=customer_create_result.cust_uuid)
    return application_create_result.application_uuid, customer_create_result.cust_uuid, user_create_result.user_id


def create_agents_test_data():
    customer_create_result = create_customer_test_data()
    application_create_result = create_application_test_data()
    current_user_create_result = create_user_test_data_by_customer_id_and_customer_name(customer_uuid=customer_create_result.cust_uuid, customer_name=customer_create_result.cust_name)
    create_user_test_data_by_customer_id_and_customer_name(customer_uuid=customer_create_result.cust_uuid, customer_name=customer_create_result.cust_name)
    create_role_test_data_by_application_id_and_customer_id(application_uuid=application_create_result.application_uuid, customer_uuid=customer_create_result.cust_uuid)
    return application_create_result.application_uuid, customer_create_result.cust_uuid, current_user_create_result.user_id


def create_customer_test_data():
    customer_dataclass_object = create_customer_dataclass_object(customer_uuid=str(uuid.uuid4()),
                                                                 customer_name=TestConstants.CUSTOMER_NAME,
                                                                 email=TestConstants.EMAIL,
                                                                 purchased_plan=TestConstants.PURCHASED_PLAN,
                                                                 primary_contact=TestConstants.PRIMARY_CONTACT,
                                                                 secondary_contact=TestConstants.SECONDARY_CONTACT,
                                                                 address=TestConstants.ADDRESS,
                                                                 billing_address=TestConstants.BILLING_ADDRESS,
                                                                 customer_details_json=None,
                                                                 status=TestConstants.STATUS)
    customer_create_result = customer_dao.create_customer(customer_data=customer_dataclass_object)
    return customer_create_result


def create_application_test_data():
    application_dataclass_object = create_application_dataclass_object(application_uuid=str(uuid.uuid4()),
                                                                       application_name=TestConstants.APPLICATION_NAME,
                                                                       application_url=TestConstants.APPLICATION_URL,
                                                                       scope_end_point=TestConstants.SCOPE_AND_ENDPOINT,
                                                                       description=TestConstants.DESCRIPTION,
                                                                       status=TestConstants.STATUS)
    application_create_result = application_dao.create_application(application_data=application_dataclass_object)
    return application_create_result


def create_role_test_data_by_application_id_and_customer_id(application_uuid, customer_uuid):
    role_dataclass_object = create_role_dataclass_object(role_uuid=str(uuid.uuid4()),
                                                         role_name=TestConstants.ROLE_NAME,
                                                         application_uuid=application_uuid,
                                                         customer_uuid=customer_uuid,
                                                         role_details_json=None, description=TestConstants.DESCRIPTION,
                                                         status=TestConstants.STATUS)
    role_create_result = role_dao.create_role(role_data=role_dataclass_object)
    return role_create_result


def create_user_test_data_by_customer_id_and_customer_name(customer_uuid, customer_name):
    user_id = str(uuid.uuid4())
    user_name = TestConstants.USER_NAME.format(user_id=user_id)
    email_id = TestConstants.EMAIL_ID.format(user_id=user_id)
    mobile_number = TestConstants.MOBILE_NUMBER.format(user_id=user_id)
    user_dataclass_object = create_user_dataclass_object(user_id=user_id, user_name=user_name, first_name=TestConstants.FIRST_NAME, last_name=TestConstants.LAST_NAME, email_id=email_id, mobile_number=mobile_number, auth_type=TestConstants.AUTH_TYPE, user_details_json=TestConstants.USER_DETAILS_JSON, customer_name=customer_name, customer_id=customer_uuid, status=TestConstants.STATUS, password_hash=TestConstants.PASSWORD_HASH)
    user_create_result = user_dao.create_user(user_data=user_dataclass_object)
    return user_create_result



def create_conversation_data():
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
            "created_at": datetime.now().isoformat(),  # Use the current timestamp
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

    # Fetch or create an Applications and Customers instance
     # Generate a unique ticket UUID
    # Create a dummy data object
    ticket_uuid = uuid.uuid4()
    ticket = Ticket.objects.create(
        ticket_uuid=ticket_uuid,
        ticket_external_id="CH12345",
        assigned_to=user,
        client_name="Client ABC",
        email_id="client@abc.com",
        status="Open",
        application_uuid=application,
        customer_uuid=customer,
        created_by="System",
        updated_by="System",
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
    )

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
        ticket_uuid = ticket,
        inserted_ts=datetime.now(),  # Use the current timestamp
        updated_ts=datetime.now()   # Use the current timestamp
    )

    return customer,application,user,chat_conversation,ticket

def create_ticket_instance():
    ticket_uuid = uuid.uuid4()  # Generate a unique ticket UUID
    application = Applications.objects.create(application_uuid=str(uuid.uuid4()))
    customer = Customers.objects.create(cust_uuid=str(uuid.uuid4()))
    user = UserMgmtUsers.objects.create(
        user_id=uuid.uuid4()
    )
    ticket = Ticket.objects.create(
        ticket_uuid=ticket_uuid,
        ticket_external_id="CH12345",
        assigned_to=user,
        client_name="Client ABC",
        email_id="client@abc.com",
        status="Open",
        application_uuid=application,
        customer_uuid=customer,
        created_by="System",
        updated_by="System",
        inserted_ts=datetime.now(),
        updated_ts=datetime.now(),
    )
    return ticket


def create_customer_application_instances():
    application = Applications.objects.create(
        application_uuid=uuid.uuid4()
    )
    customer = Customers.objects.create(
        cust_uuid=uuid.uuid4()
    )
    return application, customer
def create_dimensions_intents_data():
    application, customer = create_customer_application_instances()
    user_uuid = str(uuid.uuid4())
    dimension_type = DimensionType.objects.create(
        dimension_type_uuid="102376df-081e-40b4-9d46-0528de49ac72",
        dimension_type_name="INTENT",
        created_by=user_uuid,
        updated_by=user_uuid,
        is_default=True,
    )
    dimension_type_mapping = DimensionTypeCustomerApplicationMapping.objects.create(
        mapping_uuid=uuid.uuid4(),
        dimension_type_uuid=dimension_type,
        description="Description for Dim 1",
        application_uuid=application,
        customer_uuid=customer,
        created_by='508825ca-5e1b-47ab-920c-63c7ca721562',
        updated_by='508825ca-5e1b-47ab-920c-63c7ca721562')
    dimension = Dimension.objects.create(
        dimension_uuid=str(uuid.uuid4()),
        dimension_name="AP",
        dimension_type_uuid=dimension_type,
        created_by=user_uuid,
        updated_by=user_uuid,
    )

    dimension_mapping =  DimensionCustomerApplicationMapping.objects.create(
        mapping_uuid=str(uuid.uuid4()),
        dimension_uuid=dimension,
        parent_dimension_uuid=dimension,
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
    return dimension_type,application, customer



def create_headers_data():
    application = create_application_test_data()
    customer = create_customer_test_data()
    user = create_user_test_data_by_customer_id_and_customer_name(customer.cust_uuid, customer.cust_name)

    return user.user_id, customer.cust_uuid, application.application_uuid

def create_knowledge_source_test_data(entity_uuid, customer_uuid, application_uuid, user_uuid):
    knowledge_source = knowledge_sources_dao.create_test_knowledge_source(entity_uuid, customer_uuid, application_uuid, user_uuid)
    chunk_collection, _ = get_collection_names(customer_uuid, application_uuid)
    chunks = [{'document': 'document text',
               'metadata': {'source': TestKnowledgeSourceConstants.KNOWLEDGE_SOURCE_NAME}}]
    chroma_obj.insert_test_knowledge_chunks(chunks, chunk_collection)

    return knowledge_source

def create_entity_test_data(customer_uuid, application_uuid):
    entity = entity_dao.create_test_entity(customer_uuid, application_uuid)
    return entity



def create_sme_test_data(customer_uuid, application_uuid, user_uuid):

    entity = create_entity_test_data(customer_uuid, application_uuid)

    knowledge_source = create_knowledge_source_test_data(entity.entity_uuid, customer_uuid, application_uuid, user_uuid)

    _, cache_collection_name = get_collection_names(customer_uuid, application_uuid)
    answer = sme_dao.create_test_answer(customer_uuid, application_uuid, user_uuid, [str(entity.entity_uuid)])
    question_uuid = uuid.uuid4()
    chroma_obj.put_in_cache(question_uuid, answer.answer_uuid, TestSmeConstants.TEST_QUESTION, cache_collection_name, False)
    question = sme_dao.create_test_question(question_uuid, answer.answer_uuid, customer_uuid, application_uuid, user_uuid)

    return question, answer, entity, knowledge_source


def create_test_knowledge_source_data():
    customer = create_customer_test_data()
    application = create_application_test_data()
    customer_uuid = customer.cust_uuid
    application_uuid = application.application_uuid
    entity = create_entity_test_data(customer_uuid, application_uuid)
    # create_user_test_data_by_customer_id_and_customer_name(customer_uuid=customer_uuid, customer_name=customer.cust_name)
    knowledge_sources = knowledge_sources_dao.create_test_knowledge_source(entity.entity_uuid, customer_uuid, application_uuid, str(uuid.uuid4()))
    return knowledge_sources, application_uuid, customer_uuid

def create_test_error_data(knowledge_source_uuid, application_uuid, customer_uuid):
    print("inside create_test_error_data method")
    error = error_dao.create_error_data(error_uuid=str(uuid.uuid4()),error_type="abc",error_status="Unresolved", knowledge_source_uuid=knowledge_source_uuid,application_uuid=application_uuid, customer_uuid=customer_uuid)
    return error

def get_mocked_knowledge_source_data(knowledge_source):

    return {
                'knowledge_source_name': knowledge_source.knowledge_source_name,
                'knowledge_source_type': knowledge_source.knowledge_source_type,
                'knowledge_source_status': knowledge_source.knowledge_source_status,
                'knowledge_source_path': knowledge_source.knowledge_source_path,
                'knowledge_source_metadata': knowledge_source.knowledge_source_metadata
        }

def fetch_internal_json():
    internal_json = {
        "metadata": {
            "source": "sample-pdf.pdf",
            "title": "",
            "page_count": 4,
            "language": "en-US",
            "duration": None
        },
        "blocks": [
            {
                "page": "1",
                "content_type": "text",
                "block_id": "6b4ae5b9-9a42-4d2f-9f82-65c9971cb838",
                "text": {
                    "type": "Body",
                    "content": "Lorem ipsum "
                },
                "level": 1
            },
            {
                "page": "1",
                "content_type": "table",
                "block_id": "da05847d-f57c-4509-8641-632698a09e7b",
                "table": {
                    "name": [
                        "Table_M_1"
                    ],
                    "content": "[{\"No.\":null,\"HR Term\":\"Employee Engagement\",\"Definition\":\"The emotional commitment employees have to an organization and its goals.\",\"Importance\":\"Enhances productivity and job satisfaction\",\"Example Use-Case\":\"Implementing employee recognition programs\",\"Related HR Position\":\"Employee Engagement Specialist\"},{\"No.\":\"2\",\"HR Term\":\"Performance Management\",\"Definition\":\"A process to evaluate, develop, and improve employee performance.\",\"Importance\":\"Drives organizational success\",\"Example Use-Case\":\"Setting performance goals and KPIs\",\"Related HR Position\":\"HR Specialist\"},{\"No.\":\"3\",\"HR Term\":\"Talent Acquisition\",\"Definition\":\"The process of finding, attracting, and hiring skilled Individuals.\",\"Importance\":\"Fills open positions with quality hires\",\"Example Use-Case\":\"Developing a strong employer branding\",\"Related HR Position\":\"Talent Acquisition Specialist\"},{\"No.\":\"4\",\"HR Term\":\"Workforce Planning\",\"Definition\":\"The process of aligning workforce requirements with business objectives.\",\"Importance\":\"Optimizes workforce allocation\",\"Example Use-Case\":\"Analyzing future hiring needs\",\"Related HR Position\":\"HR Analyst\"},{\"No.\":\"s\",\"HR Term\":\"Diversity and Inclusion\",\"Definition\":\"Creating a workplace that values diverse backgrounds and perspectives.\",\"Importance\":\"Enhances creativity and innovation\",\"Example Use-Case\":\"Implementing D&I training programs\",\"Related HR Position\":\"Diversity & Inclusion Specialist\"},{\"No.\":\"6\",\"HR Term\":\"Succession Planning\",\"Definition\":\"A strategy for identifying and developing future leaders.\",\"Importance\":\"Ensures organizational continuity\",\"Example Use-Case\":\"Assessing leadership potential of employees\",\"Related HR Position\":\"HR Director\"}]",
                    "image_path": "17194e44-9a3d-407c-a65f-23dacf538b18/930430e5-36d9-4adf-8ff7-7324729636a3/knowledge_base/2024/November/29/image/HrGuidelines/ExtractedFolder/tables/fileoutpart1.png",
                    "data":[
                            {
                                "No.": None,
                                "HR Term": "Employee Engagement",
                                "Definition": "The emotional commitment employees have to an organization and its goals.",
                                "Importance": "Enhances productivity and job satisfaction",
                                "Example Use-Case": "Implementing employee recognition programs",
                                "Related HR Position": "Employee Engagement Specialist"
                            },
                            {
                                "No.": "2",
                                "HR Term": "Performance Management",
                                "Definition": "abd",
                                "Importance": "Drives organizational success",
                                "Example Use-Case": "Setting performance goals and KPIs",
                                "Related HR Position": "HR Specialist"
                            },
                            {
                                "No.": "3",
                                "HR Term": "Talent Acquisition",
                                "Definition": "The process of finding, attracting, and hiring skilled Individuals.",
                                "Importance": "Fills open positions with quality hires",
                                "Example Use-Case": "Developing a strong employer branding",
                                "Related HR Position": "Talent Acquisition Specialist"
                            },
                            {
                                "No.": "4",
                                "HR Term": "Workforce Planning",
                                "Definition": "The process of aligning workforce requirements with business objectives.",
                                "Importance": "Optimizes workforce allocation",
                                "Example Use-Case": "Analyzing future hiring needs",
                                "Related HR Position": "HR Analyst"
                            },
                            {
                                "No.": "s",
                                "HR Term": "Diversity and Inclusion",
                                "Definition": "Creating a workplace that values diverse backgrounds and perspectives.",
                                "Importance": "Enhances creativity and innovation",
                                "Example Use-Case": "Implementing D&I training programs",
                                "Related HR Position": "Diversity & Inclusion Specialist"
                            },
                            {
                                "No.": "6",
                                "HR Term": "Succession Planning",
                                "Definition": "A strategy for identifying and developing future leaders.",
                                "Importance": "Ensures organizational continuity",
                                "Example Use-Case": "Assessing leadership potential of employees",
                                "Related HR Position": "HR Director"
                            }
                    ]
                },
                "level": 1
            },
            {
                "page": "1",
                "content_type": "image",
                "block_id": "387e4f56-3b37-40ea-82da-8ccec61b5d57",
                "image": {
                    "name": [
                        "Figure_M_1"
                    ],
                    "content": "India GSTIN 36AAECT1234D2Z4 Image Reference : (http://1.Vassar_invoice.pdf/Figure_M_1.png) ",
                    "image_path": "17194e44-9a3d-407c-a65f-23dacf538b18/249d3942-8252-49ec-833b-1dab486aa09c/knowledge_base/2024/November/29/pdf/1.Vassar_invoice/ExtractedFolder/figures/fileoutpart0.png",
                    "classification": "Bar chart",
                    "data": [
                              {
                                "year": "2021A",
                                "total": 5.6,
                                "Vertically Integrated Utilities": 3.5,
                                "T&D Utilities": 1.1,
                                "Transcos/Transource": 1.0
                              },
                              {
                                "year": "2022A",
                                "total": 11.4,
                                "Vertically Integrated Utilities": 6.6,
                                "T&D Utilities": 2.5,
                                "Transcos/Transource": 2.3
                              },
                              {
                                "year": "2023E",
                                "total": 15.0,
                                "Vertically Integrated Utilities": 7.3,
                                "T&D Utilities": 4.4,
                                "Transcos/Transource": 3.3
                              },
                              {
                                "year": "2024E",
                                "total": 18.1,
                                "Vertically Integrated Utilities": 7.6,
                                "T&D Utilities": 6.3,
                                "Transcos/Transource": 4.2
                              },
                              {
                                "year": "2025E",
                                "total": 24.8,
                                "Vertically Integrated Utilities": 12.1,
                                "T&D Utilities": 8.0,
                                "Transcos/Transource": 4.7
                              },
                              {
                                "year": "2026E",
                                "total": 29.5,
                                "Vertically Integrated Utilities": 14.7,
                                "T&D Utilities": 9.5,
                                "Transcos/Transource": 5.3
                              },
                              {
                                "year": "2027E",
                                "total": 32.4,
                                "Vertically Integrated Utilities": 15.5,
                                "T&D Utilities": 10.9,
                                "Transcos/Transource": 6.0
                              },
                              {
                                "year": "2028E",
                                "total": 37.3,
                                "Vertically Integrated Utilities": 18.0,
                                "T&D Utilities": 12.3,
                                "Transcos/Transource": 7.0
                              }
                    ],
                    "level": 1
                }
            }
        ]
    }
    return internal_json