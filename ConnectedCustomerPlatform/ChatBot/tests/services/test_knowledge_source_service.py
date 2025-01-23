from django.test import TestCase
from unittest.mock import patch, MagicMock
from ChatBot.services.impl.knowledge_source_service_impl import KnowledgeSourceServiceImpl
from ChatBot.constant.constants import KnowledgeSourceTypes
from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException


class KnowledgeSourceServiceImplTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mock_knowledge_source_dao = MagicMock()
        cls.mock_error_dao = MagicMock()
        cls.mock_entity_dao = MagicMock()

        cls.service = KnowledgeSourceServiceImpl(knowledge_source_dao=cls.mock_knowledge_source_dao,entity_dao=cls.mock_entity_dao,
                                                 error_dao=cls.mock_error_dao)

    def test_get_knowledge_sources_for_question_and_answer(self):
        self.mock_knowledge_source_dao.get_reviewed_knowledge_sources_by_customer_and_application.return_value = [
            MagicMock(knowledge_source_name='test_file_1', knowledge_source_uuid='uuid-1')
        ]
        customer_uuid = 'customer-uuid-123'
        application_uuid = 'application-uuid-456'
        result = self.service.get_knowledge_sources_for_question_and_answer(customer_uuid, application_uuid)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].knowledge_source_name, 'test_file_1')

    @patch("ChatBot.services.impl.knowledge_source_service_impl.azure_blob_manager")
    def test_get_video_type_knowledge_sources_in_application(self, mock_azure_blob_manger):
        mock_video_sources = [
            {
                "knowledge_source_name": "test_video",
                "knowledge_source_uuid": "uuid-video-1",
                "knowledge_source_metadata": {"duration": 120},
                "knowledge_source_path": "test_path"
            }
        ]
        self.mock_knowledge_source_dao.get_video_type_knowledge_sources_by_customer_and_application.return_value = mock_video_sources

        customer_uuid = 'customer-uuid-123'
        application_uuid = 'application-uuid-456'

        result = self.service.get_video_type_knowledge_sources_in_application(customer_uuid, application_uuid)
        print(result)
        self.assertEqual(result['message'], 'videos fetched successfully')
        self.assertEqual(len(result['videos']), 1)
        self.assertEqual(result['videos'][0]['knowledge_source_name'], 'test_video')

    @patch('ChatBot.services.impl.knowledge_source_service_impl.azure_blob_manager')
    def test_get_knowledge_source_internal_json_file_not_found(self, mock_azure_blob_manager):
        self.mock_knowledge_source_dao.get_knowledge_source_by_uuid.return_value = None

        mock_azure_blob_manager.download_data.side_effect = ResourceNotFoundException(
            detail="File Not Found")

        knowledge_source_uuid = 'uuid-1'

        with self.assertRaises(ResourceNotFoundException):
            self.service.get_knowledge_source_internal_json(knowledge_source_uuid)

    @patch('ChatBot.services.impl.knowledge_source_service_impl.azure_blob_manager')
    def test_get_knowledge_source_internal_json_with_errors(self, mock_azure_blob_manager):
        mock_knowledge_source = MagicMock(
            knowledge_source_path='path/to/knowledge/source',
            knowledge_source_type=KnowledgeSourceTypes.VIDEO.value,
            knowledge_source_status='Reviewed'
        )
        self.mock_knowledge_source_dao.get_knowledge_source_by_uuid.return_value = mock_knowledge_source

        mock_azure_blob_manager.download_data.return_value = '{"blocks": [], "metadata": {}}'

        self.mock_error_dao.has_unresolved_errors.return_value = True

        knowledge_source_uuid = 'uuid-1'

        result = self.service.get_knowledge_source_internal_json(knowledge_source_uuid)

        self.assertFalse(result['enable_review'])

    @patch('ChatBot.services.impl.knowledge_source_service_impl.azure_blob_manager')
    def test_get_knowledge_source_internal_json_without_errors(self, mock_azure_blob_manager):
        mock_knowledge_source = MagicMock(
            knowledge_source_path='path/to/knowledge/source',
            knowledge_source_type=KnowledgeSourceTypes.VIDEO.value,
            knowledge_source_status='Reviewed'
        )
        self.mock_knowledge_source_dao.get_knowledge_source_by_uuid.return_value = mock_knowledge_source
        mock_azure_blob_manager.download_data.return_value = '{"blocks": [], "metadata": {}}'
        self.mock_error_dao.has_unresolved_errors.return_value = False
        knowledge_source_uuid = 'uuid-1'
        result = self.service.get_knowledge_source_internal_json(knowledge_source_uuid)

        self.assertTrue(result['enable_review'])




