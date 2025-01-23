import copy
import json
import logging
import traceback

from ChatBot.constant.constants import Constants

from ChatBot.services.csr_service import CsrService

from ChatBot.services.user_service import UserService

from ChatBot.services.conversation_service import ConversationService

from ChatBot.services.redis_service import RedisService

from ChatBot.utils import validate_input

logger = logging.getLogger(__name__)


class HotHandoffService:
    def __init__(self):
        self.conversation_service = ConversationService()
        self.csr_service = CsrService()
        self.user_service = UserService()
        self.redis_service = RedisService()
        pass

    async def hot_handoff(self, hot_handoff_data, channel_id):
        try:
            """
                Method to transfer conversation from current csr to next csr:
                Parameters:
                    hot_handoff_data (dict) :  contains necessary data
                    channel_id : current csr channel_id/session_id/channel_name
                Return:
                    dict object contains result and status
            """
            logger.info("hot_handoff_service.py :: HotHandoffService :: hot_handoff")
            logger.info(f"handoff_data :: {hot_handoff_data}")
            hot_handoff_data = json.loads(hot_handoff_data)
            conversation_uuid = hot_handoff_data.get('conversation_uuid')
            new_csr_id = hot_handoff_data.get('csr_id')
            new_csr_name = hot_handoff_data.get('csr_name')
            new_role_id = hot_handoff_data.get('role_id')
            new_role_name = hot_handoff_data.get('role_name')
            current_csr_id = hot_handoff_data.get('current_csr_id')
            conversation_key = f"conversation:{conversation_uuid}"

            # maintain deep copy of conversation_data. whenever there is issue in code or in broadcasting data to csr or in notifying the user, we can roll back the conversation_data in redis
            conversation_data_deep_copy = {}
            is_conversation_data_in_redis = self.redis_service.check_if_redis_contains_data_by_conversation_key(
                conversation_key)
            if is_conversation_data_in_redis:
                redis_conversation_data = self.redis_service.get_conversation_data_by_conversation_key(conversation_key)
                redis_conversation_data = json.loads(redis_conversation_data)
                conversation_data_deep_copy = copy.deepcopy(redis_conversation_data)
            # check if current csr selected "agent-transfer" option
            if new_csr_id:
                validation_response = validate_input(new_csr_name)
                if not validation_response:
                    return {"result": "csr_name cannot be empty or null", "status": False}
                conversation_data, change_conversation_data_method_response_status = self.conversation_service.change_conversation_data(
                    conversation_uuid=conversation_uuid, new_status=Constants.CSR_ONGOING, csr_id=new_csr_id,
                    csr_name=new_csr_name, csr_profile="", csr_status=Constants.ASSIGNED, is_update_current_csr=True, current_csr_id=current_csr_id)

                if change_conversation_data_method_response_status:
                    broadcast_method_response = await self.csr_service.broadcast_onqueue_conversations_to_csr(
                        csr_id=new_csr_id)
                    # if broadcast is successfull to csr then only notify the user
                    if broadcast_method_response.get("status"):
                        turn = broadcast_method_response.get("turn")
                        notify_user_response = await self.user_service.notify_user_with_new_csr_data(csr_id=new_csr_id,
                                                                                                     csr_name=new_csr_name,
                                                                                                     channel_id=channel_id,
                                                                                                     room_name=f"room_{conversation_uuid}", turn=turn)
                        # check notification to user is successful or not
                        if not notify_user_response.get("status"):
                            if is_conversation_data_in_redis:
                                # if there is issue in notifying the user we need to roll back the conversation data
                                self.redis_service.set_conversation_data_in_redis(conversation_key=conversation_key,
                                                                                  conversation_data=conversation_data_deep_copy)
                            return {"result": notify_user_response.get("result"), "status": False}
                    else:
                        if is_conversation_data_in_redis:
                            # if there is issue in broadcasting we need to roll back the conversation data
                            self.redis_service.set_conversation_data_in_redis(conversation_key=conversation_key,
                                                                              conversation_data=conversation_data_deep_copy)
                        return {"result": broadcast_method_response.get("result"), "status": False}
                    return {"result": Constants.HOT_HANDOFF_SUCCESSFUL_MESSAGE, "status": True}
                return {"result": Constants.HOT_HANDOFF_UNSUCCESSFUL_MESSAGE, "status": False}

            # if current csr selected "department-transfer" option
            else:
                validation_response = validate_input(new_role_name)
                if not validation_response:
                    return {"result": "department_name or role_name cannot be empty or null", "status": False}
                min_csr_data = await self.csr_service.fetch_csr_to_be_assigned(role_id=new_role_id, exclude_csr_id=current_csr_id)
                # if there are no csr
                if not min_csr_data:
                    return {"result": f"Sorry,Currently no Agents are Online in {new_role_name} department", "status": False}
                logger.info(f"after finding min_csr_data :: {min_csr_data}")
                min_csr_id = min_csr_data[Constants.CSR_UID]
                min_csr_name = min_csr_data[Constants.NAME]

                conversation_data, change_conversation_data_method_response_status = self.conversation_service.change_conversation_data(
                    conversation_uuid=conversation_uuid, new_status=Constants.CSR_ONGOING, csr_id=min_csr_id,
                    csr_name=min_csr_name, csr_profile="", csr_status=Constants.ASSIGNED, is_update_current_csr=True, current_csr_id=current_csr_id)

                if change_conversation_data_method_response_status:
                    broadcast_method_response = await self.csr_service.broadcast_onqueue_conversations_to_csr(
                        csr_id=min_csr_id)
                    # if broadcast is successfull to csr then only notify the user
                    if broadcast_method_response.get("status"):
                        turn = broadcast_method_response.get("turn")
                        notify_user_response = await self.user_service.notify_user_with_new_csr_data(csr_id=min_csr_id,
                                                                                                     csr_name=min_csr_name,
                                                                                                     channel_id=channel_id,
                                                                                                     room_name=f"room_{conversation_uuid}", turn=turn)
                        # check notification to user is successful or not
                        if not notify_user_response.get("status"):
                            if is_conversation_data_in_redis:
                                # if there is issue in notifying the user we need to roll back the conversation data
                                self.redis_service.set_conversation_data_in_redis(conversation_key=conversation_key,
                                                                                  conversation_data=conversation_data_deep_copy)
                            return {"result": notify_user_response.get("result"), "status": False}
                    else:
                        if is_conversation_data_in_redis:
                            # if there is issue in broadcasting we need to roll back the conversation data
                            self.redis_service.set_conversation_data_in_redis(conversation_key=conversation_key,
                                                                              conversation_data=conversation_data_deep_copy)
                        return {"result": broadcast_method_response.get("result"), "status": False}
                    return {"result": Constants.HOT_HANDOFF_SUCCESSFUL_MESSAGE + f" to {min_csr_name} of {new_role_name} department", "status": True}
                return {"result": Constants.HOT_HANDOFF_UNSUCCESSFUL_MESSAGE, "status": False}
        except Exception as e:
            logger.info(f"got exception :: {str(e)}")
            # Get the traceback information
            tb_info = traceback.extract_tb(e.__traceback__)
            # Extract the line number from the traceback
            line_number = tb_info[-1].lineno
            # Print the line number
            logger.info(f"Exception occurred at line number: {line_number}")
            traceback.print_exc()
            return {"result": str(e), "status": False}
