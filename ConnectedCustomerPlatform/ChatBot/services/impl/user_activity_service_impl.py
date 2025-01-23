import logging
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
import math

from django.conf import settings
from django.utils import timezone

from ChatBot.services.interface.user_activity_service_interface import UserActivityServiceInterface

from ChatBot.dao.interface.conversations_dao import IConversationsDao
from ChatBot.dao.interface.user_activity_dao_interface import UserActivityDaoInterface
from ChatBot.dao.interface.user_dao_interface import IUserDao
from ChatBot.dao.impl.conversations_dao_impl import ConversationsDaoImpl
from ChatBot.dao.impl.user_activity_dao_impl import UserActivityDaoImpl
from ChatBot.dao.impl.user_dao_impl import UserDaoImpl

logger = logging.getLogger(name=__name__)


class UserActivityServiceImpl(UserActivityServiceInterface):
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        
        if cls._instance is None:
            cls._instance = super(UserActivityServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):

        if not hasattr(self, 'initialized'):
            
            super().__init__(**kwargs)
            
            self.initialized = True
            
            self.__conversation_dao: IConversationsDao = ConversationsDaoImpl()
            self.__user_activity_dao: UserActivityDaoInterface = UserActivityDaoImpl()
            self.__user_dao: IUserDao = UserDaoImpl()
            
            logger.debug("UserActivityServiceImpl instance initialized.")
    
    def get_user_chats(self, customer_uuid: str, user_id: str) -> list[dict[str, str]]:
        
        logger.debug('In UserActivityServiceImpl class :: get_user_chats method')
        
        chats = self.__conversation_dao.get_user_chats(customer_uuid, user_id)
        for chat in chats:
            
            updated_ts: datetime = chat['updated_ts']
            updated_ts = updated_ts.replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
            chat['updated_ts'] = updated_ts

            inserted_ts: datetime = chat['inserted_ts']
            inserted_ts = inserted_ts.replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
            chat['inserted_ts'] = inserted_ts
            
        return chats
    
    def get_leaderboard(self, customer_uuid: str) -> list[dict]:
        
        logger.debug('In UserActivityServiceImpl class :: get_leaderboard method')
        
        query_activity = self.__user_activity_dao.get_leaderboard(customer_uuid)
        leaderboard = []
        
        for user_id, first_name, last_name, query_count in query_activity:
            leaderboard.append({
                'user_id' : user_id,
                'name' : first_name + " " + last_name,
                'score' : query_count
            })    
            
        return leaderboard

    def get_timeseries(self, user_id: str) -> dict:
        
        logger.debug('In UserActivityServiceImpl class :: get_timeseries method')
        
        n = 5
        data = self.__user_activity_dao.get_timeseries(user_id, n)
        
        labels = []
        values = []
        for record in data:
            
            labels.append(record['date'])
            values.append(record['count'])
            
        timeseries = {
            'labels' : labels,
            'values' : values
        }
        return timeseries

    def get_feedback_details(self, user_id: str) -> dict:
        
        logger.debug('In UserActivityServiceImpl class :: get_feedback_details method')
        
        query_activity_count = self.__user_activity_dao.get_query_activity_count(user_id)
        
        feedback_questions = self.__user_activity_dao.get_feedback_questions(user_id)
        feedback_activity = []
        
        for question_uuid, question in feedback_questions:
            
            feedback_activity.append({
                'question_uuid' : question_uuid,
                'question' : question
            })
        
        level, progress = self._get_level_and_progress(query_activity_count)
        
        return {
            'total_questions' : query_activity_count,
            'level' : level,
            'progress' : progress,
            'thumbs_down_questions' : len(feedback_activity),
            'questions' : feedback_activity
        }
    
    def _get_level_and_progress(self, query_activity_count: int) -> tuple[int, int]:
        
        level = math.floor(query_activity_count/10)
        progress = (query_activity_count % 10) * 10
        
        return level, progress
    
    def get_query_activity_stats(self, user_id: str) -> list[dict]:
        
        logger.debug('In UserActivityServiceImpl class :: get_query_activity_stats method')
        
        days = [
            ('1 week', 'week', 7),
            ('1 month', 'month', 30)
        ]
        end_date = timezone.now()
        
        activity_stats = []
        for label, period, delta in days:
            
            start_date = end_date - timedelta(days=delta)
            start_date = datetime.combine(start_date, datetime.min.time())
            
            count = self.__user_activity_dao.get_query_activity_count_for_date_range(user_id, start_date, end_date)
            stat = count/delta
           
            activity_stats.append({
                'label' : label,
                'value' : period,
                'statisticValue' : stat
            })
        
        return activity_stats    
    
    def get_user_info(self, user_id: str) -> dict:
        
        logger.debug('In UserActivityServiceImpl class :: get_user_info method')

        first_name, last_name, email_id, designation = self.__user_dao.get_user_info(user_id)
        return {
            'userRole' : designation,
            'username' : first_name + " " + last_name,
            'userEmail' : email_id
        }