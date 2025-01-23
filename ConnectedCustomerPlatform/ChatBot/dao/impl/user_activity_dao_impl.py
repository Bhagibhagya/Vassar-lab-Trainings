import logging
from uuid import uuid4

from django.db.models import Count
from django.db.models.functions import TruncDate

from django.db import connection
from django.utils import timezone
from datetime import timedelta, datetime

from ChatBot.dao.interface.user_activity_dao_interface import UserActivityDaoInterface
from DatabaseApp.models import UserActivity

logger = logging.getLogger(name=__name__)


class UserActivityDaoImpl(UserActivityDaoInterface):
    
    def add_feedback_activity(self, user_id: str, customer_uuid: str, application_uuid: str, question_uuid: str, answer_uuid: str, feedback: str) -> None:
        
        logger.debug('In UserActivityDaoImpl class :: add_feedback_activity method')
        
        UserActivity.objects.create(
            user_activity_uuid = str(uuid4()),
            activity_name = UserActivity.ActivityChoices.FEEDBACK,
            user_id = user_id,
            application_uuid_id = application_uuid,
            customer_uuid_id = customer_uuid,
            question_uuid = question_uuid,
            answer_uuid = answer_uuid,
            feedback = feedback
        )
    
    def get_leaderboard(self, customer_uuid: str) -> list[tuple[str, str, str, int]]:
        
        logger.debug('In UserActivityDaoImpl class :: get_leaderboard method')
        
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT u.user_id, u.first_name, u.last_name, COUNT(ua.user_id) AS query_count
                FROM user_activity ua
                JOIN usermgmt.users u ON ua.user_id = u.user_id
                WHERE ua.activity_name = %s
                AND ua.customer_uuid = %s
                GROUP BY u.user_id
                ORDER BY query_count DESC
                """, [UserActivity.ActivityChoices.QUERY.value, customer_uuid]
            )
            leaderboard = cursor.fetchall()
        
        return leaderboard
    
    def get_timeseries(self, user_id: str, days: int) -> list[dict]:
        
        logger.debug('In UserActivityDaoImpl class :: get_timeseries method')
        
        time = timezone.now()
        date = time.date()
        
        date_days_ago = date - timedelta(days=days)
        
        timeseries = UserActivity.objects.filter(
            user_id=user_id,
            activity_name=UserActivity.ActivityChoices.QUERY,
            inserted_ts__gte=date_days_ago
        ).annotate(date=TruncDate('inserted_ts')).values('date').annotate(count=Count('user_activity_uuid')).order_by('date')
        
        return list(timeseries)

    def get_query_activity_count(self, user_id: str) -> int:
        
        logger.debug('In UserActivityDaoImpl class :: get_query_activity_count method')
        
        return UserActivity.objects.filter(user_id=user_id, activity_name=UserActivity.ActivityChoices.QUERY).count()

    def get_feedback_questions(self, user_id: str) -> list[tuple[str, str]]:
        
        logger.debug('In UserActivityDaoImpl class :: get_feedback_questions method')
        
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT ua.question_uuid, q.question
                FROM user_activity ua
                JOIN questions q 
                ON ua.question_uuid = q.question_uuid
                WHERE ua.activity_name = %s AND ua.user_id = %s
                """, [UserActivity.ActivityChoices.FEEDBACK.value, user_id]
            )
            feedback_questions = cursor.fetchall()
        
        return list(feedback_questions)
    
    def get_query_activity_count_for_date_range(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        
        logger.debug('In UserActivityDaoImpl class :: get_query_activity_count_for_date_range method')
        
        count = UserActivity.objects.filter(
            user_id=user_id,
            activity_name=UserActivity.ActivityChoices.QUERY,
            inserted_ts__range=(start_date, end_date)
        ).count()

        return count