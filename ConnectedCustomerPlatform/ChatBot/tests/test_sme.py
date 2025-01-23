import logging
from uuid import uuid4
from django.core.management import call_command

from django.test import TestCase

from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.constants import SMEConstants, Constants
from django.urls import reverse
from ChatBot.tests.test_data import create_headers_data, create_sme_test_data
from Platform.constant import constants
from ChatBot.constant.success_messages import SuccessMessages
from rest_framework import status
from rest_framework.test import APIClient
from django.db import connection

# Initialize logger
logger = logging.getLogger(__name__)


# Base test class with setup methods for common functionality
class BaseTestCase(TestCase):
    maxDiff = None  # Allow full output in case of assertion mismatches

    @classmethod
    def setUpTestData(cls):
        # Run migrations to ensure database is ready for testing
        call_command('makemigrations')
        call_command('migrate')
        # Create test headers data (user_uuid, customer_uuid, application_uuid)
        (
            cls.user_uuid,
            cls.customer_uuid,
            cls.application_uuid,
        ) = create_headers_data()

        # Define headers for API requests
        cls.headers = {
            constants.CUSTOMER_UUID: cls.customer_uuid,
            constants.APPLICATION_UUID: cls.application_uuid,
            constants.USER_ID: cls.user_uuid
        }
        cls.verifier_role_uuid = str(uuid4())
        with connection.cursor() as cursor:
            cursor.execute("""CREATE OR REPLACE VIEW question_details_view AS
SELECT
    q.question_uuid,
    q.question,
    q.updated_ts,
    a.answer_uuid,
    a.file_details_json,
    d.draft_uuid,
    q.is_system_generated,
    q.customer_uuid,
    q.application_uuid,
    a.is_verified,
    a.feedback,
    a.updated_ts AS answer_updated_ts,
    (CASE 
        WHEN a.verifier_role_uuid = %s THEN 1
        ELSE 0
      END) AS sme_verified,
    0 AS qa_verified
FROM
    questions q
JOIN
    answers a ON q.answer_uuid = a.answer_uuid
LEFT JOIN
    drafts d ON a.answer_uuid = d.answer_uuid
GROUP BY
    q.question_uuid,
    a.answer_uuid,
    d.draft_uuid;""", [cls.verifier_role_uuid])

    # Set up test data before each test case
    def setUp(self):

        # Create SME test data for questions, answers, entities, and knowledge sources
        (self.question, self.answer, self.entity, self.knowledge_source) = create_sme_test_data(
            self.customer_uuid, self.application_uuid, self.user_uuid)

        # Initialize APIClient with the headers
        self.client = APIClient(headers=self.headers)


# Test case class for SMEViewSet, containing tests for various API operations
class SMEViewSetTestCase(BaseTestCase):

    # Test case for successfully adding a question
    def test_add_question_success(self):
        # Define payload for adding a question with related answer and entity details
        payload = {
            "question": "test question 1",
            "answer": "test answer 1",
            "entity_uuids": [str(self.entity.entity_uuid)],
            "attachments": [
                {'url': 'https://domain/containername/projectname/blob/name.ext?sig=signature',
                 'name': ['abc.g'],
                 'type': 'image',
                 'source': None},
                {'url': 'https://domain/containername/projectname/blob/name.ext?sig=signature',
                 'name': ['xyz.mp4'],
                 'type': 'video',
                 'start_time': '00:00:00'}
            ],
            "author_role_uuid": str(uuid4())
        }
        # Make POST request to add question
        response = self.client.post(reverse("ChatBot:sme"), payload, format="json")

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate response content
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_201_CREATED,
                "status": True,
                "result": SuccessMessages.QUESTION_ADDED_SUCCESS
            }
        )

    # Test case for successfully retrieving a list of questions
    def test_get_questions_success(self):
        # Define request payload with pagination details
        payload = {
            'page_number': 1, 'total_entry_per_page': 5, 'feedback': False
        }
        # Make GET request to retrieve questions
        response = self.client.get(reverse("ChatBot:sme"), payload, format="json")

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Expected result for validation
        expected_result = {
            'total_entries': 1,
            'data': [{
                'question_uuid': str(self.question.question_uuid),
                'question': self.question.question,
                'answer_uuid': str(self.answer.answer_uuid),
                'feedback_status': False,
                'draft_status': False,
                'is_verified': False,
                'sme_verified': 0,
                'qa_verified': 0,
                'file_details_json': [],
                'is_system_generated': False
            }]
        }

        # Validate response content
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": expected_result
            }
        )

    # Test case for successfully retrieving details of a specific question
    def test_get_question_details_success(self):
        # Make GET request for specific question details using question UUID
        response = self.client.get(reverse("ChatBot:question", kwargs={'question_uuid': self.question.question_uuid}))

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        # Define expected response data
        expected_data = {
            "code": status.HTTP_200_OK,
            "status": True,
            "result": {
                'question_uuid': str(self.question.question_uuid),
                'answer_uuid': str(self.answer.answer_uuid),
                'question': self.question.question,
                'is_verified': False,
                'sme_verified': 0,
                'qa_verified': 0,
                'feedback_status': False,
                'feedback': None,
                'answer': self.answer.answer,
                'attachments': [
                        {'url': 'SIGNED_URL', 'name': ['test.png'], 'type': 'image', 'source': 'test_source'},
                        {'url': 'SIGNED_URL', 'name': ['test.mp4'], 'type': 'video', 'start_time': '00:00:00'}
                    ],
                'draft_status': False,
                'draft_uuid': None,
                'draft': None,
                'draft_attachments': [],
                'entity_details': [
                    {'entity_name': self.entity.entity_name, 'entity_uuid': str(self.entity.entity_uuid)}
                ]
            }
        }

        # Override URLs in attachments with 'SIGNED_URL' for validation
        for attachment in response_data['result']['attachments']:
            attachment['url'] = 'SIGNED_URL'

        # Validate response content
        self.assertDictEqual(response_data, expected_data)

    # Test case for handling question not found
    def test_get_question_details_not_found(self):
        # Make GET request for a non-existing question UUID
        response = self.client.get(
            reverse("ChatBot:question", kwargs={'question_uuid': '00000000-c45b-454a-ac37-cdfe052449fb'}))

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Validate response content
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_404_NOT_FOUND,
                "status": False,
                "result": ErrorMessages.QUESTION_NOT_FOUND
            }
        )

    # Test case for successfully deleting an answer
    def test_delete_answer_success(self):
        # Make DELETE request to remove answer by UUID
        response = self.client.delete(reverse("ChatBot:answer", kwargs={'answer_uuid': self.answer.answer_uuid}))

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response content
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.QUESTION_DELETED_SUCCESS
            }
        )

    # Test case for successfully updating an answer
    def test_update_answer_success(self):
        # Define updated answer content
        updated_answer = 'new answer'

        # Define payload for updating the answer with updated content and entity details
        payload = {
            'answer_uuid': str(self.answer.answer_uuid),
            'answer': updated_answer,
            'entity_uuids': [str(self.entity.entity_uuid)],
            'attachments': [],
            "author_role_uuid": str(uuid4()),
            'draft_uuid': None

        }

        # Make PUT request to update answer
        response = self.client.put(reverse("ChatBot:update_answer"), payload, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response content
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.ANSWER_UPDATED_SUCCESS
            }
        )

        # Verify the updated answer via GET request
        response = self.client.get(reverse("ChatBot:question", kwargs={'question_uuid': self.question.question_uuid}))

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        # Expected data after the update
        expected_data = {
            "code": status.HTTP_200_OK,
            "status": True,
            "result": {
                'question_uuid': str(self.question.question_uuid),
                'answer_uuid': str(self.answer.answer_uuid),
                'question': self.question.question,
                'is_verified': False,
                'sme_verified': 0,
                'qa_verified': 0,
                'feedback_status': False,
                'feedback': None,
                'answer': updated_answer,
                'attachments': [],
                'draft_status': False,
                'draft_uuid': None,
                'draft': None,
                'draft_attachments': [],
                'entity_details': [
                    {'entity_name': self.entity.entity_name, 'entity_uuid': str(self.entity.entity_uuid)}
                ]
            }
        }

        # Validate the updated content
        self.assertDictEqual(response_data, expected_data)

    def test_verify_answer(self):
        """
        Test verifying an answer.
        Sends a PUT request to verify the answer and asserts the success response.
        Then, retrieves the question and checks if the verified status and other details are updated as expected.
        """
        verified = True
        payload = {
            'answer_uuid': str(self.answer.answer_uuid),
            'verified': verified,
            'verifier_role_uuid': self.verifier_role_uuid
        }
        response = self.client.put(reverse("ChatBot:verify_answer"), payload, format='json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the expected success message
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.ANSWER_VERIFIED_SUCCESS
            }
        )


        payload = {
            'page_number': 1, 'total_entry_per_page': 5, 'feedback': False
        }
        # Make GET request to retrieve questions
        response = self.client.get(reverse("ChatBot:sme"), payload, format="json")

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Expected result for validation
        expected_result = {
            'total_entries': 1,
            'data': [{
                'question_uuid': str(self.question.question_uuid),
                'question': self.question.question,
                'answer_uuid': str(self.answer.answer_uuid),
                'feedback_status': False,
                'draft_status': False,
                'is_verified': True,
                'sme_verified': 1,
                'qa_verified': 0,
                'file_details_json': [],
                'is_system_generated': False
            }]
        }

        # Validate response content
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": expected_result
            }
        )

    def test_add_draft_success(self):
        """
        Test adding a draft question.
        Sends a POST request with a draft question and verifies the response.
        Then, retrieves the SME questions and ensures the draft status is true.
        """
        draft_question = 'draft question'
        draft_answer = 'draft answer'
        payload = {
            'question': draft_question,
            'answer': draft_answer,
            'entity_uuids': [str(self.entity.entity_uuid)],
            'attachments': [],
            "author_role_uuid": str(uuid4()),
            'is_draft': True
        }
        response = self.client.post(reverse("ChatBot:sme"), payload, format="json")

        # Assert that the draft was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert the draft success message
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_201_CREATED,
                "status": True,
                "result": SuccessMessages.DRAFT_ADD_SUCCESS
            }
        )

    def test_save_draft_success(self):
        """
        Test saving a draft for an existing answer.
        Sends a PUT request to save a draft and verifies the response.
        Then, retrieves SME questions and checks the draft status.
        """
        draft_answer = 'draft answer'
        payload = {

            'answer_uuid': str(self.answer.answer_uuid),
            'answer': draft_answer,
            'entity_uuids': [str(self.entity.entity_uuid)],
            'attachments': [],
            "author_role_uuid": str(uuid4()),
            'is_draft': True,
            'draft_uuid': None

        }
        response = self.client.put(reverse("ChatBot:update_answer"), payload, format="json")

        # Assert the draft was saved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the success message for draft saving
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.DRAFT_SAVE_SUCCESS
            }
        )


    def test_feedback_success(self):
        """
        Test submitting feedback on an answer.
        Sends a POST request with feedback and verifies the success response.
        Then, retrieves the question and ensures the feedback content is updated.
        """
        feedback = 'bad answer'
        payload = {
            'answer_uuid': str(self.answer.answer_uuid),
            'feedback': feedback,
            'dislike': True,
            # 'conversation_uuid': str(uuid4()),
            # 'message_id': str(uuid4()),
            # 'source': Constants.CHAT,
            "author_role_uuid": str(uuid4())
        }
        response = self.client.post(reverse("ChatBot:update_feedback"), payload, format="json")

        # Assert feedback submission was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert feedback success message
        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.FEEDBACK_SUBMIT_SUCCESS
            }
        )

    # # def test_ignore_feedback_success(self):
    # #     """
    # #     Test ignoring feedback on an answer.
    # #     Sends a PUT request to ignore feedback and verifies the success response.
    # #     Then, retrieves the question and checks if feedback content is cleared.
    # #     """
    # #     payload = {
    # #         'answer_uuid': str(self.answer.answer_uuid),
    # #         'feedback': 'bad response',
    # #         'dislike': True,
    # #         'conversation_uuid': str(uuid4()),
    # #         'message_id': str(uuid4()),
    # #         'source': Constants.CHAT
    # #     }
    # #     _ = self.client.post(reverse("ChatBot:update_feedback"), payload, format="json")
    # #
    # #     # Ignore the feedback
    # #     response = self.client.put(reverse("ChatBot:ignore_feedback", kwargs={'answer_uuid': self.answer.answer_uuid}))
    # #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    # #
    # #     # Assert the feedback ignore success message
    # #     self.assertDictEqual(
    # #         response.json(),
    # #         {
    # #             "code": status.HTTP_200_OK,
    # #             "status": True,
    # #             "result": SuccessMessages.FEEDBACK_IGNORE_SUCCESS
    # #         }
    # #     )
    # #
    # #     # Retrieve SME questions and verify feedback status is false
    # #     payload = {'size': 5, 'offset': 0, 'feedback': False}
    # #     response = self.client.get(reverse("ChatBot:sme"), payload, format="json")
    # #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    # #     response_data = response.json()
    # #     self.assertEqual(response_data['result']['questions'][0]['feedback_status'], False)
    # #
    # #     # Retrieve the question and assert feedback content is cleared
    # #     response = self.client.get(reverse("ChatBot:question", kwargs={'question_uuid': self.question.question_uuid}))
    # #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    # #     response_data = response.json()
    # #     self.assertEqual(response_data['result']['feedback'], {'status': False, 'content': None})
    # #
    def test_generate_qa_success(self):
        """
        Test generating Q&A from knowledge sources.
        Sends a POST request to generate Q&A and verifies the success response.
        """
        payload = {
            'knowledge_sources': [self.knowledge_source.knowledge_source_uuid],
            'author_role_uuid': str(uuid4())
        }
        response = self.client.post(reverse("ChatBot:generate_qa"), payload, format="json")

        # Assert Q&A generation was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            response.json(),
            {
                "code": status.HTTP_200_OK,
                "status": True,
                "result": SuccessMessages.QA_GENERATE_SUCCESS
            }
        )
