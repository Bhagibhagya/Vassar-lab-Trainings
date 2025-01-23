import json
import logging
import traceback
from collections import Counter

from ChatBot.constant.constants import Constants
from django.utils import timezone
from channels.layers import get_channel_layer

from ChatBot.services.user_service import UserService
from ChatBot.services.redis_service import RedisService
from ChatBot.user_management_services import UserManagementServices
from django.conf import settings

logger = logging.getLogger(__name__)


class CsrService:
    def __init__(self):
        self.user_service = UserService()
        self.redis_service = RedisService()
        pass

    def append_new_csr_data(self, conversation, csr_id, csr_name, profile_picture, csr_status, assigned_time=None):
        """
            Method to update "csr_info_json" field of conversation json data by adding new csr data
            Parameters:
                - conversation :
                - csr_id (str) :
                - csr_name (str) :
                - profile_picture (str) :
                - csr_status (str) :
                - assigned_time (str timestamp) :
            Returns:

        """
        logger.info("csr_service.py :: :: :: CsrService :: :: :: append_new_csr_data")
        if assigned_time is None:
            assigned_time = timezone.now().isoformat()
        new_csr_info = {
            Constants.CSR_UID: csr_id,
            Constants.NAME: csr_name,
            Constants.PROFILE_PICTURE: profile_picture,
            Constants.STATUS: csr_status,
            Constants.ASSIGNED_TIME: assigned_time
        }
        logger.info(f"new csr data :: {new_csr_info}")
        # check if conversation is of type dict/json or if its db instance
        csr_info_list = conversation.get(Constants.CSR_INFO_JSON, []) if isinstance(conversation, dict) else json.loads(
            conversation.csr_info_json or '[]')
        logger.info(f"before appending new csr in csr_info_json:: csr_info_json data:: {csr_info_list}")
        csr_info_list.append(new_csr_info)

        if isinstance(conversation, dict):
            conversation[Constants.CSR_INFO_JSON] = csr_info_list
        else:
            conversation.csr_info_json = csr_info_list

        return conversation, True

    def change_previous_csr_status(self, conversation, current_csr_id, current_csr_status):
        """
                    Method to update "csr_info_json" field of conversation json data by adding new csr data
                    Parameters:
                        - conversation :
                        - csr_id (str) :
                        - csr_name (str) :
                        - profile_picture (str) :
                        - csr_status (str) :
                        - assigned_time (str timestamp) :
                    Returns:
                        - return conversation
        """

        logger.info("csr_service.py :: :: :: CsrService :: :: :: change_previous_csr_status")
        csr_info_list = conversation.get(Constants.CSR_INFO_JSON, []) if isinstance(conversation, dict) else json.loads(
            conversation.csr_info_json or '[]')
        for csr in csr_info_list:
            if isinstance(csr, dict):
                if csr.get(Constants.CSR_UID) == current_csr_id:
                    csr[Constants.STATUS] = current_csr_status
                    break
        logger.info(f"new csr info list after updating current csr status :: {csr_info_list}")
        if isinstance(conversation, dict):
            conversation[Constants.CSR_INFO_JSON] = csr_info_list
        else:
            conversation.csr_info_json = csr_info_list

        return conversation, True

    async def broadcast_onqueue_conversations_to_csr(self, csr_id, conversation_uuid=None):
        try:
            """
                Method to broadcast onqueue users conversation  to new csr
                Parameters:
                    - csr_id {str}: user_id of new csr
                    - conversation_uuid {str} : uuid of conversation
                Returns:

            """
            logger.info("csr_service.py :: :: :: CsrService :: :: :: broadcast_onqueue_conversations_to_csr")
            from ChatBot.services.conversation_service import ConversationService
            conversation_service = ConversationService()
            onqueue_conversation_list, method_response_status = conversation_service.get_onqueue_conversations_list(
                csr_id=csr_id, conversation_uuid=conversation_uuid)
            logger.info(f"onqueue conversation list :: {onqueue_conversation_list}")
            reply_data_json = {
                "csr_id": csr_id,
                "onqueue_conversations": onqueue_conversation_list
            }
            channel_layer = get_channel_layer()
            logger.info(f"before broadcasting to csr_id :: {csr_id} :: broadcasting_data :: {reply_data_json}")
            await channel_layer.group_send(
                f"csr_{csr_id}",
                {
                    'type': 'send_message',
                    'message': json.dumps(reply_data_json)
                }
            )
            logger.info(f"broadcast successfully to csr_id :: {csr_id}")
            return {"result": Constants.BROADCAST_TO_CSR_SUCCESS_MESSAGE, "status": True, "turn": len(onqueue_conversation_list)}
        except Exception as e:
            logger.info(f"got exception in broadcast_onqueue_conversations_to_csr method of CsrService class")
            logger.info(f"exception:: {str(e)}")
            # Get the traceback information
            tb_info = traceback.extract_tb(e.__traceback__)
            # Extract the line number from the traceback
            line_number = tb_info[-1].lineno
            # Print the line number
            logger.info(f"Exception occurred at line number: {line_number}")
            traceback.print_exc()
            return {"result": str(e), "status": False}

    async def fetch_csr_to_be_assigned(self, role_id, exclude_csr_id=None):
        """
           Retrieves the CSR with the minimum number of assigned conversations
           and assigns a new conversation to them.

           Parameters:
           - role_id: The identifier for the user role which is used to filter the online users.

        """
        logger.info("csr_service.py :: :: :: CsrService :: :: :: fetch_csr_to_be_assigned")
        response_data = self.get_online_csr_conversation_count(role_id)
        """
            response_data = [
                {
                    "csr_uid":"c120",
                    "name": "mahipal"
                    "count": 2
                }
            ]
        """
        if exclude_csr_id is not None:
            response_data = [csr for csr in response_data if csr["csr_uid"] != exclude_csr_id]
        if response_data:
            min_csr = min(response_data, key=lambda x: x[Constants.COUNT])
            return min_csr
        else:
            return {}

    def get_online_csr_conversation_count(self, role_id):
        """
            Fetches the count of conversations assigned to each CSR who are online

            Parameters:
            - role_id: The identifier for the user role which is used to filter the online users.
        """
        logger.info("csr_service.py :: :: :: CsrService :: :: :: get_online_csr_conversation_count")
        response_data = self.get_online_csr_by_role_id(role_id)
        logger.info(f"online csr data :: {response_data}")
        '''
            response_data = [
                                {
                                    "user_id":"",
                                    "name":""
                                }, 
                                {}
                            ]
        '''
        user_data = {user[Constants.USER_ID]: user[Constants.NAME] for user in response_data}
        """
            user_data = {"user_id":"name"}
        """
        conversation_keys = self.redis_service.get_all_redis_keys("conversation:*")
        total_conversation_data = self.redis_service.get_all_conversation_data(
            conversation_keys)
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

    def get_online_csr_by_role_id(self, role_id):
        logger.info("csr_service.py :: :: :: CsrService :: :: :: get_online_csr_by_role_id")
        user_service = UserManagementServices()
        api_url = f"{settings.USERMGMT_API_BASE_URL}/{Constants.USER_STATUS_ENDPOINT}/{role_id}"
        logger.info(f"usermgmt api_url :: {api_url}")
        logger.info("calling usermgmt to fetch online csrs")
        response = user_service.make_request('GET', api_url)
        logger.info(f"response from usrmgmt :: {response}")
        response_data = response.get("response")
        users = []
        if response_data:
            if isinstance(response_data, list):
                for user in response_data:
                    data = {
                        Constants.USER_ID: user.get('userId'),
                        Constants.NAME: user.get('username'),
                    }
                    users.append(data)
        return users
