import json
import logging

from django.db.models.functions import Coalesce

from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.sql_queries import get_question_details_query
from ChatBot.dataclasses.sme_data import Question, Answer, Draft
from ChatBot.constant.constants import TestConstants, TestSmeConstants, SMEConstants
from ConnectedCustomerPlatform.exceptions import UnauthorizedByScopeException
from DatabaseApp.models import Questions, Answers, Drafts, QuestionDetailsView, Entities
from django.db.models import F, Func, Value, Q, When, Case, BooleanField
from django.db import models, connection
from uuid import uuid4

from ChatBot.dao.interface.sme_dao_interface import ISMEDao
from DatabaseApp.models import Answers
from django.db.models import Prefetch

from django.db.models.expressions import RawSQL, Subquery, OuterRef
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

class SMEDaoImpl(ISMEDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SMEDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.initialized = True
            logger.info("SMEDaoImpl initialized")


    def update_entity_uuid_in_answer(self, old_entity_uuid, new_entity_uuid, user_uuid):
        logger.debug(f"updating answers with entity UUID: {old_entity_uuid} to entity UUID : {new_entity_uuid}")

        cnt = Answers.objects.filter(entity_details_json__contains=[old_entity_uuid]).update(
            entity_details_json=RawSQL(
                        """
                        (SELECT jsonb_agg(
                            CASE
                                WHEN elem::text = %s THEN %s
                                ELSE elem
                            END
                        )
                        FROM jsonb_array_elements_text(entity_details_json) AS elem)
                        """,
                        (str(old_entity_uuid), str(new_entity_uuid))
                    ),
            updated_by=user_uuid
        )
        logger.debug(f"updated {cnt} answers records with entity UUID: {old_entity_uuid} to entity UUID : {new_entity_uuid}")
        return cnt

    # Fetch all questions for a specific customer and application with pagination
    def get_questions(self, customer_uuid, application_uuid, filter, entity_uuids_list):
        logger.debug(
            f"Fetching all questions for customer UUID: {customer_uuid}, application UUID: {application_uuid}, entity_uuids: {entity_uuids_list}")

        # Initialize filters
        filters = Q(application_uuid=application_uuid, customer_uuid=customer_uuid)

        # Apply entity details filter
        if entity_uuids_list:
            filters &= Q(entity_details_json__contained_by=entity_uuids_list)

        # Apply question_type filter if specified
        question_type = filter.get('question_type')

        if question_type is None or question_type == 'all':
            # No additional filter for 'all'; fetch all questions
            pass  # No action needed for 'all'

        elif question_type == 'draft':
            # Filter for draft questions (where draft_uuid is not null)
            filters &= Q(draft_uuid__isnull=False)

        elif question_type == 'feedback':
            # Filter for feedback questions (where feedback is not null)
            filters &= Q(feedback__isnull=False)

        # Apply additional filters 'question' if provided
        if filter.get('question'):
            filters &= Q(question__icontains=filter.get('question'))

        questions = QuestionDetailsView.objects.filter(filters).annotate(
                feedback_status=Case(
                    When(feedback__isnull=True, then=False),
                    default=True,
                    output_field=models.BooleanField()
                ),
                draft_status=Case(
                    When(draft_uuid__isnull=True, then=False),
                    default=True,
                    output_field=models.BooleanField()
                )
            ).order_by('-updated_ts').values(
                        'question_uuid',
                        'question',
                        'is_system_generated',
                        'answer_uuid',
                        'feedback_status',
                        'file_details_json',
                        'is_verified',
                        'sme_verified',
                        'qa_verified',
                        'draft_status'
                    )

        return questions

    # Fetch a question by its UUID and log the details
    def get_question_details(self, question_uuid, entity_uuids_list):
        logger.debug(f"Fetching question with UUID: {question_uuid} and  scope of entity uuids: {entity_uuids_list}")
        qyery = get_question_details_query
        if entity_uuids_list:
            qyery += """
            AND a.entity_details_json <@ to_jsonb(%s::text[]) GROUP BY q.question_uuid, a.answer_uuid, d.draft_uuid;
            """
            params = [
                settings.SME_EDIT_RESOURCE_ACTION_ID,
                settings.QA_EDIT_RESOURCE_ACTION_ID,
                settings.SME_EDIT_RESOURCE_ACTION_ID,
                settings.QA_EDIT_RESOURCE_ACTION_ID,
                question_uuid,
                entity_uuids_list  # Only include this if list is not empty
            ]
        else:
            # If the list is empty, we don't include the entity condition
            qyery += """
            GROUP BY q.question_uuid, a.answer_uuid, d.draft_uuid;
            """
            params = [
                settings.SME_EDIT_RESOURCE_ACTION_ID,
                settings.QA_EDIT_RESOURCE_ACTION_ID,
                settings.SME_EDIT_RESOURCE_ACTION_ID,
                settings.QA_EDIT_RESOURCE_ACTION_ID,
                question_uuid
            ]
        with connection.cursor() as cursor:
            cursor.execute(qyery, params)
            row = cursor.fetchone()

        if row is None:
            if entity_uuids_list:
                raise UnauthorizedByScopeException(ErrorMessages.BEYOND_SCOPE)
            return None
        question_details = {'question_uuid': row[0],
                            'question': row[1],
                            'answer_uuid': row[2],
                            'answer': row[3],
                            'attachments': json.loads(row[4]),
                            'draft_uuid': row[5],
                            'draft_status': row[5] is not None,
                            'draft': row[6],
                            'draft_attachments': json.loads(row[7]) if row[7] is not None else [],
                            'is_verified': row[8],
                            'feedback': row[9],
                            'feedback_status': row[9] is not None,
                            'sme_verified': row[10],
                            'qa_verified': row[11],
                            'entity_details': json.loads(row[12])}
        logger.debug(f"Fetched question details for UUID: {question_uuid}")
        return question_details

    # Create a new question and log the process
    def create_question(self, question: Question, user_uuid):
        logger.info(f"Creating question with UUID: {question.question_uuid}")
        _ = Questions.objects.create(
            question_uuid=question.question_uuid,
            question=question.question_text,
            answer_uuid_id=question.answer_uuid,
            is_system_generated=question.is_system_generated,
            author_user_uuid=question.author_user_uuid,
            author_role_uuid=question.author_role_uuid,
            application_uuid_id=question.application_uuid,
            customer_uuid_id=question.customer_uuid,
            created_by=user_uuid,
            updated_by=user_uuid
        )
        logger.info(f"Question created successfully with UUID: {question.question_uuid}")

    # Create a new answer and log the process
    def create_answer(self, answer: Answer, user_uuid):
        logger.info(f"Creating answer with UUID: {answer.answer_uuid}")
        _ = Answers.objects.create(
            answer_uuid=answer.answer_uuid,
            answer=answer.answer_text,
            attachment_details_json=answer.attachment_details_json,
            file_details_json=answer.file_details_json,
            entity_details_json=answer.entity_details_json,
            feedback=answer.feedback,
            is_verified=answer.is_verified,
            in_cache = answer.in_cache,
            verifier_user_uuid=answer.verifier_user_uuid,
            verifier_role_uuid=answer.verifier_role_uuid,
            is_system_generated=answer.is_system_generated,
            author_user_uuid=answer.author_user_uuid,
            author_role_uuid=answer.author_role_uuid,
            application_uuid_id=answer.application_uuid,
            customer_uuid_id=answer.customer_uuid,
            created_by=user_uuid,
            updated_by=user_uuid
        )
        logger.info(f"Answer created successfully with UUID: {answer.answer_uuid}")

    # Retrieve question UUIDs by associated answer UUID
    def get_question_uuids_by_answer_uuid(self, answer_uuid):
        logger.debug(f"Fetching question UUIDs for answer UUID: {answer_uuid}")
        question_uuids = QuestionDetailsView.objects.filter(answer_uuid=answer_uuid).values_list('question_uuid', flat=True).all()
        logger.debug(f"Found {len(question_uuids)} questions for answer UUID: {answer_uuid}")
        return question_uuids

    # Fetch question UUIDs not present in the cache
    def get_question_uuids_by_answer_uuid_and_cache(self, answer_uuid, cache, entity_uuids_list):
        logger.info(f"Fetching question UUIDs with cache {cache} for answer UUID: {answer_uuid} and in the scope of entites with: {entity_uuids_list}")
        answer = Answers.objects.filter(answer_uuid=answer_uuid, entity_details_json__contained_by=entity_uuids_list)
        if (entity_uuids_list and answer) or not entity_uuids_list:
            question_uuids = Questions.objects.filter(answer_uuid=answer_uuid, answer_uuid__in_cache=cache).values_list('question_uuid', flat=True).all()
            logger.info(f"Found {len(question_uuids)} question UUIDs with cache {cache} for answer UUID: {answer_uuid}")
            return question_uuids
        else:
            logger.debug(f"Answer with UUID: {answer_uuid} not in the scope of user.")
            raise UnauthorizedByScopeException(ErrorMessages.BEYOND_SCOPE)

    def get_question_uuids_by_answer_uuid(self, answer_uuid: str) -> list[str]:
        
        question_uuids = list(Questions.objects.filter(answer_uuid=answer_uuid).values_list('question_uuid', flat=True))
        return question_uuids
    
    # Delete an answer based on the answer UUID
    def delete_answer_by_answer_uuid(self, answer_uuid, entity_uuids_list):
        logger.debug(f"Deleting answer with UUID: {answer_uuid}")
        answer = Answers.objects.filter(answer_uuid=answer_uuid, entity_details_json__contained_by=entity_uuids_list)
        if (entity_uuids_list and answer) or not entity_uuids_list:
            rows_deleted, _ = Answers.objects.filter(answer_uuid=answer_uuid).delete()
            logger.debug(f"Answer with UUID: {answer_uuid} deleted successfully")
            return rows_deleted
        else:
            logger.debug(f"Answer with UUID: {answer_uuid} not in the scope to be deleted.")
            raise UnauthorizedByScopeException(ErrorMessages.BEYOND_SCOPE)


    # Save a draft to the database and log the operation
    def save_draft(self, draft: Draft, user_uuid):
        logger.info(f"Saving draft with UUID: {draft.draft_uuid}")
        draft_obj = Drafts(
            draft_uuid=draft.draft_uuid,
            answer_uuid=Answers(answer_uuid=draft.answer_uuid),
            draft=draft.draft_content,
            attachment_details_json=draft.attachment_details_json,
            author_user_uuid=draft.author_user_uuid,
            author_role_uuid=draft.author_role_uuid,
            application_uuid_id=draft.application_uuid,
            customer_uuid_id=draft.customer_uuid,
            created_by=user_uuid,
            updated_by=user_uuid
        )
        draft_obj.save()
        logger.info(f"Draft with UUID: {draft.draft_uuid} saved successfully")


    # updates all associated questions for a specific answer with given cache status
    def update_question_cache_details(self, answer_uuid, user_uuid, cache):
        logger.info(f"updating questions as cache: {cache} for answer UUID: {answer_uuid}")
        _ = Questions.objects.filter(answer_uuid_id=answer_uuid).update(in_cache=cache, updated_by=user_uuid)
        logger.info(f"Questions cache data updated for answer UUID: {answer_uuid}")


    # Update an existing answer with new details and log the changes
    def update_answer(self, answer: Answer, user_uuid):
        logger.debug(f"Updating answer with UUID: {answer.answer_uuid}")
        update_fields = {
            'answer': answer.answer_text,
            'attachment_details_json': answer.attachment_details_json,
            'author_user_uuid': user_uuid,
            'author_role_uuid': answer.author_role_uuid,
            'application_uuid': answer.application_uuid,
            'customer_uuid': answer.customer_uuid,
            'is_system_generated': answer.is_system_generated,
            'feedback': None,
            'in_cache': answer.in_cache,
            'updated_by': user_uuid
        }

        # Conditionally add entity_details_json only if it is not None
        if answer.entity_details_json is not None:
            update_fields['entity_details_json'] = answer.entity_details_json

        row_matched = Answers.objects.filter(answer_uuid=answer.answer_uuid).update(**update_fields)
        logger.debug(f"Answer with UUID: {answer.answer_uuid} updated successfully")

        return row_matched

    # Set verification details for an answer and log the update
    def update_answer_verification_details(self, answer_uuid, is_verified, verifier_role_uuid, user_uuid, entity_uuids_list):
        query_filter = {'answer_uuid': answer_uuid}

        # Add the entity filter only if entity_uuids_list is not empty
        if entity_uuids_list:
            query_filter['entity_details_json__contained_by'] = entity_uuids_list

        # Perform the update operation
        rows_cnt = Answers.objects.filter(**query_filter).update(
            is_verified=is_verified,
            verifier_role_uuid=verifier_role_uuid,
            verifier_user_uuid=user_uuid,
            updated_by=user_uuid
        )

        if rows_cnt == 0:
            logger.debug(f"Answer with UUID: {answer_uuid} not in the scope or no records updated.")
            raise UnauthorizedByScopeException(ErrorMessages.BEYOND_SCOPE)

        logger.debug(f"Verification details updated for answer UUID: {answer_uuid}, updated rows: {rows_cnt}")
        return rows_cnt

    # Set feedback for an answer
    def update_answer_feedback_and_cache(self, answer_uuid, feedback, in_cache, user_uuid):
        logger.debug(f"Setting feedback for answer UUID: {answer_uuid}")
        rows_matched = Answers.objects.filter(answer_uuid=answer_uuid).update(feedback=feedback, in_cache=in_cache, updated_by=user_uuid)
        logger.debug(f"Feedback set for answer UUID: {answer_uuid}")
        return rows_matched

    def delete_draft_by_answer_uuid(self, answer_uuid):
        logger.debug(f"Deleting draft with answer UUID: {answer_uuid}")
        rows_deleted, _ = Drafts.objects.filter(answer_uuid=answer_uuid).delete()
        logger.debug(f"Draft with answer UUID: {answer_uuid} deleted {rows_deleted}")


    # Create a test answer for testing purposes
    def create_test_answer(self, customer_uuid, application_uuid, user_uuid, entity_details_json):
        logger.info(f"Creating test answer for customer UUID: {customer_uuid}, application UUID: {application_uuid}")
        answer = Answers.objects.create(
            answer_uuid=uuid4(),
            answer=TestSmeConstants.TEST_ANSWER,
            attachment_details_json=TestSmeConstants.TEST_ATTACHMENTS,
            entity_details_json=entity_details_json,
            is_system_generated=True,
            author_user_uuid=user_uuid,
            application_uuid_id=application_uuid,
            customer_uuid_id=customer_uuid,
            created_by=user_uuid,
            updated_by=user_uuid
        )
        logger.info(f"Test answer created successfully with UUID: {answer.answer_uuid}")
        return answer

    # Create a test question for testing purposes
    def create_test_question(self, question_uuid, answer_uuid, customer_uuid, application_uuid, user_uuid):
        logger.info(f"Creating test question with UUID: {question_uuid}")
        question = Questions.objects.create(
            question_uuid=question_uuid,
            question=TestSmeConstants.TEST_QUESTION,
            answer_uuid_id=answer_uuid,
            is_system_generated=False,
            author_user_uuid=user_uuid,
            application_uuid_id=application_uuid,
            customer_uuid_id=customer_uuid,
            created_by=user_uuid,
            updated_by=user_uuid
        )
        logger.info(f"Test question created successfully with UUID: {question.question_uuid}")
        return question


    
    def in_cache_update_for_answers_of_knowledge_source(self, answer_list):
        """
        Updates the 'in_cache' status to False for all answers linked to the specified knowledge source name.
        
        Args:
            answer_list (str): list of answers will  update.
        """
        Answers.objects.filter(
            answer_uuid__in = answer_list
        ).update(in_cache=False)


    def questions_answers_of_knowledge_source(self, knowledge_source_uuid):
        """
           returns questions and answers        
        Args:
            knowledge_source_uuid (str): The knowledge_source_uuid of the knowledge source to update.
        """ 
        return Answers.objects.filter(
                file_details_json__contains=[{'knowledge_source_uuid': knowledge_source_uuid}]
            ).values(
                'answer_uuid',
                'questions__question_uuid'  # Adjust this field name as per your model
            )
    
    def delete_answers_of_knowledge_source(self, knowledge_source_uuid):
        """
           deletes answers based on knowledge_source_uuid
        Args:
            knowledge_source_uuid (str): The knowledge_source_uuid of the knowledge source to update.
        """ 
        Answers.objects.filter(
                file_details_json__contains=[{'knowledge_source_uuid': knowledge_source_uuid}]
            ).delete()
        
    def get_answer_uuids_by_source(self, knowledge_source_name: str, customer_uuid: str, application_uuid: str) -> list[str]:
        
        """
        Fetches the list of answer uuids which are answered from the given knowledge source.

        :param knowledge_source_name: The name of the knowledge source.
        :param customer_uuid: Unique identifier for the customer.
        :param application_uuid: Unique identifier for the application.

        :return: list of answer uuids.
        """
        
        logger.info('In SMEDaoImpl class :: get_answer_uuids_by_source method.')
        
        answer_uuids = Answers.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            file_details_json__contains=[knowledge_source_name]
        ).values_list('answer_uuid', flat=True)

        return list(answer_uuids)
    
    def delete_by_answer_uuids(self, answer_uuids):
                
        """
        Delete answers by the given list of answer uuids

        :param answer_uuids: The list of answer uuids to delete.

        :return: None
        """
        
        logger.info('In SMEDaoImpl class :: get_answer_uuids_by_source method.')
        if len(answer_uuids) > 0:
            Answers.objects.filter(answer_uuid__in=answer_uuids).delete()

