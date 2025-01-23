from django.test import TestCase
from django.core.management import call_command
from DatabaseApp.models import KnowledgeSources, Applications, Customers, Entities
from ChatBot.dao.impl.knowledge_sources_dao_impl import KnowledgeSourcesDaoImpl
import uuid


class KnowledgeSourcesDaoImplTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('makemigrations', interactive=False)
        call_command('migrate', interactive=False)

    @classmethod
    def setUpTestData(cls):
        # Create dummy data once for all test cases
        cls.knowledge_source_uuid = uuid.uuid4()

        cls.application = Applications.objects.create(
            application_uuid='application-uuid-456',
            application_name='Test App',
            application_url='https://testapp.com',
            scope_end_point='test-endpoint'
        )

        cls.customer = Customers.objects.create(
            cust_uuid='customer-uuid-123',
            cust_name='Test Customer',
            email='testcustomer@test.com'
        )

        cls.entity = Entities.objects.create(
            entity_uuid='ent-uuid',
            entity_name='Test Entity',
            application_uuid=cls.application,
            customer_uuid=cls.customer
        )

        cls.knowledge_source_1 = KnowledgeSources.objects.create(
            knowledge_source_uuid='123',
            knowledge_source_name='test_file_1',
            knowledge_source_path='/path/to/source1',
            knowledge_source_type='video',
            knowledge_source_status=KnowledgeSources.KnowledgeSourceStatus.REVIEWED,
            knowledge_source_metadata={'key': 'value1'},
            parent_knowledge_source_uuid=None,
            is_deleted=False,
            application_uuid=cls.application,
            customer_uuid=cls.customer,
            entity_uuid=cls.entity,
            attribute_details_json={"attribute": "value1"},
            qa_status=False,
            created_by='Test User',
            updated_by='Test User'
        )

        cls.knowledge_source_2 = KnowledgeSources.objects.create(
            knowledge_source_uuid='456',
            knowledge_source_name='test_file_2',
            knowledge_source_path='/path/to/source2',
            knowledge_source_type='Type2',
            knowledge_source_status=KnowledgeSources.KnowledgeSourceStatus.REVIEWED,
            knowledge_source_metadata={'key': 'value2'},
            parent_knowledge_source_uuid='ks-uuid-1',
            is_deleted=False,
            application_uuid=cls.application,
            customer_uuid=cls.customer,
            entity_uuid=cls.entity,
            attribute_details_json={"attribute": "value2"},
            qa_status=False,
            created_by='Test User',
            updated_by='Test User'
        )

        cls.knowledge_source_3 = KnowledgeSources.objects.create(
            knowledge_source_uuid=cls.knowledge_source_uuid,
            knowledge_source_name='test_file_2',
            knowledge_source_path='/path/to/source2',
            knowledge_source_type='Type2',
            knowledge_source_status=KnowledgeSources.KnowledgeSourceStatus.PROCESSING,
            knowledge_source_metadata={'key': 'value2'},
            parent_knowledge_source_uuid='ks-uuid-1',
            is_deleted=False,
            application_uuid=cls.application,
            customer_uuid=cls.customer,
            entity_uuid=cls.entity,
            attribute_details_json={"attribute": "value2"},
            qa_status=True,
            created_by='Test User',
            updated_by='Test User'
        )

    def setUp(self):
        # Initialize the DAO class
        self.dao = KnowledgeSourcesDaoImpl()

    def test_get_knowledge_source_by_uuid(self):
        knowledge_source = self.dao.get_knowledge_source_by_uuid(self.knowledge_source_uuid)
        self.assertEqual(knowledge_source.knowledge_source_name, 'test_file_2')

    def test_get_reviewed_knowledge_sources_by_customer_and_application(self):
        reviewed_sources = self.dao.get_reviewed_knowledge_sources_by_customer_and_application(
            customer_uuid=self.customer.cust_uuid,
            application_uuid=self.application.application_uuid
        )
        self.assertEqual(len(reviewed_sources), 2)

    def test_get_video_type_knowledge_sources_by_customer_and_application(self):
        video_sources = self.dao.get_video_type_knowledge_sources_by_customer_and_application(
            customer_uuid=self.customer.cust_uuid,
            application_uuid=self.application.application_uuid
        )
        self.assertEqual(video_sources[0]['knowledge_source_name'], 'test_file_1')
        self.assertEqual(len(video_sources), 1)
