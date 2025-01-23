import uuid
from django.test import TestCase
from DatabaseApp.models import Applications, Customers, Entities, KnowledgeSources, Errors
from ChatBot.dao.impl.error_dao_impl import ErrorsDaoImpl
from ChatBot.constant.constants import Constants


class ErrorsDaoImplTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

        cls.knowledge_source = KnowledgeSources.objects.create(
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

        cls.error_resolved = Errors.objects.create(
            error_uuid=str(uuid.uuid4()),
            error_type='Type1',
            error_status=Constants.RESOLVED,
            error_details_json={"detail": "No error"},
            knowledge_source_uuid=cls.knowledge_source,
            application_uuid=cls.application,
            customer_uuid=cls.customer
        )

        cls.error_unresolved = Errors.objects.create(
            error_uuid=str(uuid.uuid4()),
            error_type='Type2',
            error_status=Constants.UN_RESOLVED,
            error_details_json={"detail": "Some error"},
            knowledge_source_uuid=cls.knowledge_source,
            application_uuid=cls.application,
            customer_uuid=cls.customer
        )

        cls.dao = ErrorsDaoImpl()

    def test_has_unresolved_errors_returns_true(self):
        result = self.dao.has_unresolved_errors(self.knowledge_source.knowledge_source_uuid)
        self.assertTrue(result)

    def test_has_unresolved_errors_returns_false(self):
        other_knowledge_source = KnowledgeSources.objects.create(
            knowledge_source_uuid='456',
            knowledge_source_name='test_file_2',
            knowledge_source_path='/path/to/source2',
            knowledge_source_type='video',
            knowledge_source_status=KnowledgeSources.KnowledgeSourceStatus.REVIEWED,
            knowledge_source_metadata={'key': 'value2'},
            parent_knowledge_source_uuid=None,
            is_deleted=False,
            application_uuid=self.application,
            customer_uuid=self.customer,
            entity_uuid=self.entity,
            attribute_details_json={"attribute": "value2"},
            qa_status=False,
            created_by='Test User',
            updated_by='Test User'
        )

        Errors.objects.create(
            error_uuid=str(uuid.uuid4()),
            error_type='Type1',
            error_status=Constants.RESOLVED,
            error_details_json={"detail": "No error"},
            knowledge_source_uuid=other_knowledge_source,
            application_uuid=self.application,
            customer_uuid=self.customer
        )

        result = self.dao.has_unresolved_errors(other_knowledge_source.knowledge_source_uuid)
        self.assertFalse(result)
