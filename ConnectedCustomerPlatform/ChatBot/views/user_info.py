import json
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from django.utils import timezone
import secrets
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework import status
from ChatBot.user_management_services import UserManagementServices
from ConnectedCustomerPlatform.responses import CustomResponse
from ConnectedCustomerPlatform.exceptions import CustomException
import logging
from ChatBot.views.chat_bot import ChatBotViewSet
from ChatBot.constant.constants import Constants
from ChatBot.utils import get_redis_connection

from ChatBot.constant.constants import AgentDashboardConstants
from django.conf import settings

logger = logging.getLogger(__name__)


class UserInfoViewSet(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redis = get_redis_connection()


    def update_user(self, user_id, channel_id , status):
        logger.info("user_info.py :: :: :: UserInfoViewSet :: :: :: update_user")
        """
            Updates the status of a user by calling an external user management API.

            Parameters:
            - user_id: The unique identifier of the user whose status needs to be updated.
            - status: The new status to be set for the user.
        """
        user_service = UserManagementServices()
        try:
            api_url = f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{user_id}/{channel_id}/{status}"
            response_data = user_service.make_request('GET', api_url)
            return response_data
        except Exception as e:
            logger.debug(f"Exception occurred: {str(e)}")


    def get_online_users(self, role_id):
        logger.info("user_info.py :: :: :: UserInfoViewSet :: :: :: get_online_users")
        """
            Fetches and returns a list of online users based on their role ID by calling an external user management API.
            Parameters:
            - status: Used to provide status codes in case of errors.
            - role_id: The identifier for the user role which is used to filter the online users.
        """
        if role_id is None:
            return AgentDashboardConstants.ROLE_ID_NOT_GIVEN
        try:
            user_service = UserManagementServices()
            api_url = f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{role_id}"
            response = user_service.make_request('GET', api_url)
            response_data = response.get("response")
            users = []
            if response_data:
                for user in response_data:
                    data = {
                        Constants.USER_ID : user.get('userId'),
                        Constants.NAME: user.get('username'),
                    }
                    users.append(data)
            return users
        except Exception as e:
            return []
        # else:
        #     return CustomException(response,status=500)

    def get_user_conversation_count(self, role_id):
        logger.info("user_info.py :: :: :: UserInfoViewSet :: :: :: get_user_conversation_count")
        """
            Fetches the count of conversations assigned to each CSR who are online

            Parameters:
            - role_id: The identifier for the user role which is used to filter the online users.
        """
        response_data = self.get_online_users(role_id)
        user_data = {user[Constants.USER_ID]: user[Constants.NAME] for user in response_data}
        conversation_keys = self.redis.keys("conversation:*")
        total_conversation_data = self.redis.mget(conversation_keys)
        csr_assigned_counts = Counter()
        for data in total_conversation_data:
            if not data:
                continue
            conversation_data = json.loads(data)
            csr_info = conversation_data.get(Constants.CSR_INFO_JSON, [])
            for csr in csr_info:
                csr_id = csr.get(Constants.CSR_UID)
                csr_name = user_data.get(csr_id)
                if csr_id in user_data and csr.get(Constants.STATUS) == Constants.ASSIGNED:
                    csr_assigned_counts[csr_id, csr_name] += 1

        for csr_id, csr_name in user_data.items():
            if (csr_id, csr_name) not in csr_assigned_counts:
                csr_assigned_counts[(csr_id, csr_name)] = 0

        result = [{Constants.CSR_UID: csr_id, Constants.NAME: csr_name, Constants.COUNT: count} for
                  (csr_id, csr_name), count in csr_assigned_counts.items()]
        return result

    async def csr_to_be_assigned(self, instance, connections ,role_id):
        """
           Retrieves the CSR with the minimum number of assigned conversations
           and assigns a new conversation to them.

           Parameters:
           - role_id: The identifier for the user role which is used to filter the online users.

        """
        logger.info("user_info.py :: :: :: UserInfoViewSet :: :: :: get_csr_to_be_assigned")
        response_data = self.get_user_conversation_count(role_id)
        if response_data:
            for connection in connections:
              min_csr = min(response_data, key=lambda x: x[Constants.COUNT])
              csr_id = min_csr[Constants.CSR_UID]
              csr_name = min_csr[Constants.NAME]
              chat_bot_view_set = ChatBotViewSet()
              current_time = timezone.now().isoformat()
              status = chat_bot_view_set.change_conversation_status(connection, Constants.CSR_ONGOING, csr_id, csr_name,
                                                                    "", Constants.ASSIGNED, current_time)
              if status:
                  print(f"status::{status}")
                  min_csr[Constants.COUNT] += 1
                  await instance.broadcast_csr_onqueue_conversations(csr_id)
                  await self.notify_user(instance, csr_id, csr_name, min_csr[Constants.COUNT])
        else:
            message_text= Constants.NO_CSR_ONLINE
            await instance.send_reply(message_text)


    async def notify_user(self, instance, csr_id, csr_name, waiting_number):
        """
            Notifies a user about their assigned Csr_details and his waiting time.

            Parameters:
            - csr_id: The identifier for the CSR  being notified.
            - csr_name: The name of the CSR being notified.
            - waiting_number: The position of the user in the waiting queue.
        """
        result = {
            Constants.CSR_UID: csr_id,
            Constants.NAME: csr_name,
            "turn": waiting_number
        }

        await instance.send_json(
            {Constants.CSR_INFO_JSON: result}
        )
