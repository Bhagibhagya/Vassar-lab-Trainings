import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from Platform.utils import get_customer_and_user_ids

from ConnectedCustomerPlatform.responses import CustomResponse

from ChatBot.services.interface.user_activity_service_interface import UserActivityServiceInterface
from ChatBot.services.impl.user_activity_service_impl import UserActivityServiceImpl
from ChatBot.constant.constants import Constants

logger = logging.getLogger(name=__name__)


class UserActivityViewSet(ViewSet):
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        
        if cls._instance is None:
            cls._instance = super(UserActivityViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):

        if not hasattr(self, 'initialized'):
            
            super().__init__(**kwargs)
            
            self.initialized = True
            self.__user_activity_service: UserActivityServiceInterface = UserActivityServiceImpl()
            
            logger.debug("UserActivityViewSet instance initialized.")
    
    @action(detail=False, methods=[Constants.GET])
    def get_user_chats(self, request):
        
        """
        Get the chat sessions information of a user.
        """
        logger.debug('In UserActivityViewSet class :: get_user_chats method')
        
        customer_uuid, user_id = get_customer_and_user_ids(request.headers)
        
        chat_sessions = self.__user_activity_service.get_user_chats(customer_uuid, user_id)
        return CustomResponse(chat_sessions, status.HTTP_200_OK)
    
    @action(detail=False, methods=[Constants.GET])
    def get_leaderboard(self, request):
        
        """ 
        Get the users activity leaderboard for a customer and application.
        """
        logger.debug('In UserActivityViewSet class :: get_leaderboard method')
        
        customer_uuid, _ = get_customer_and_user_ids(request.headers)
        
        leaderboard = self.__user_activity_service.get_leaderboard(customer_uuid)
        return CustomResponse(leaderboard, status.HTTP_200_OK)
    
    @action(detail=False, methods=[Constants.GET])
    def get_timeseries(self, request):
        
        """ 
        Get the users query activity for the past n days.
        """
        logger.debug('In UserActivityViewSet class :: get_timeseries method')
        
        _, user_id = get_customer_and_user_ids(request.headers)
        
        timeseries = self.__user_activity_service.get_timeseries(user_id)
        return CustomResponse(timeseries, status.HTTP_200_OK)
    
    @action(detail=False, methods=[Constants.GET])
    def get_feedback_details(self, request):
        
        """ 
        Get the feedback activity details of a user.
        """
        logger.debug('In UserActivityViewSet class :: get_feedback_details method')
        
        _, user_id = get_customer_and_user_ids(request.headers)
        
        feedback_details = self.__user_activity_service.get_feedback_details(user_id)
        return CustomResponse(feedback_details, status.HTTP_200_OK)
    
    @action(detail=False, methods=[Constants.GET])
    def get_average_stats(self, request):
        
        """ 
        Get the average query stats for past n days.
        """
        logger.debug('In UserActivityViewSet class :: get_average_stats method')
        
        _, user_id = get_customer_and_user_ids(request.headers)
        
        average_stats = self.__user_activity_service.get_query_activity_stats(user_id)
        return CustomResponse(average_stats, status.HTTP_200_OK)
    
    @action(detail=False, methods=[Constants.GET])
    def get_user_info(self, request):
        
        """ 
        Get the user role information.
        """
        logger.debug('In UserActivityViewSet class :: get_user_info method')
        
        _, user_id = get_customer_and_user_ids(request.headers)
        
        user_info = self.__user_activity_service.get_user_info(user_id)
        return CustomResponse(user_info, status.HTTP_200_OK)