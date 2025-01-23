import json
import logging
import copy
import uuid
from datetime import datetime

from DatabaseApp.models import ChatConversation

from ChatBot.services.csr_service import CsrService
from django.utils import timezone

from ChatBot.services.redis_service import RedisService

from ChatBot.constant.constants import Constants, UserDetailConstants, ConversationConstants, \
    MessageConstants
from ConnectedCustomerPlatform.exceptions import CustomException
from rest_framework import status as http_status

from ChatBot.constant.constants import CsrConstants

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self):
        # self.redis = get_redis_connection()
        self.redis_class_instance = RedisService()
        self.csr_instance = CsrService()

    def change_conversation_data(self, conversation_uuid, new_status, csr_id, csr_name, csr_profile, csr_status,
                                 is_update_current_csr,current_csr_id, assigned_time=None):
        """
            Method to change the status of a conversation and add new csr data in csr_info_json fild of conversation json and make old csr status to "Inactive"
            Parameters:
                conversation_uuid (str): The UUID of the conversation.
                new_status (str): The new status of the conversation. Should be one of ['resolved', 'bot_ongoing', 'csr_ongoing'].
        """
        if assigned_time is None:
            assigned_time = timezone.now().isoformat()
        logger.info("conversation_service.py :: :: :: ConversationService :: :: :: change_conversation_status")
        conversation_key = f"conversation:{conversation_uuid}"
        # check if conversation data is in redis or not
        is_conversation_data_in_redis = self.redis_class_instance.check_if_redis_contains_data_by_conversation_key(
            conversation_key=conversation_key)
        logger.info(f"is conversation data present in redis or not :: {is_conversation_data_in_redis}")
        if is_conversation_data_in_redis:
            conversation_data = self.redis_class_instance.get_conversation_data_by_conversation_key(
                conversation_key=conversation_key)
            conversation_data = json.loads(conversation_data)
            conversation_data["conversation_status"] = new_status

            if new_status == Constants.CSR_ONGOING:
                conversation_data['csr_hand_off'] = True
                if is_update_current_csr:
                    conversation_data, change_previous_csr_status_method_response_status = self.csr_instance.change_previous_csr_status(
                        conversation=conversation_data, current_csr_id=current_csr_id, current_csr_status=Constants.INACTIVE)
                conversation_data, append_new_csr_data_method_response_status = self.csr_instance.append_new_csr_data(
                    conversation=conversation_data, csr_id=csr_id, csr_name=csr_name, profile_picture=csr_profile,
                    csr_status=csr_status)
            self.redis_class_instance.set_conversation_data_in_redis(conversation_key=conversation_key,
                                                                     conversation_data=json.dumps(conversation_data))
            return conversation_data, True
        else:
            conversation = ChatConversation.objects.filter(chat_conversation_uuid=conversation_uuid).first()
            if not conversation:
                logger.error(f"Conversation with UUID {conversation_uuid} does not exist in the database.")
                return conversation, False
                # raise ResourceNotFoundException(f"{conversation_uuid} does not exist in the database.")

            conversation.conversation_status = new_status
            if new_status == Constants.CSR_ONGOING:
                conversation.csr_hand_off = True
                if is_update_current_csr:
                    conversation, change_previous_csr_status_method_response_status = self.csr_instance.change_previous_csr_status(
                        conversation=conversation, current_csr_id="", current_csr_status=Constants.INACTIVE)
                conversation, append_new_csr_data_method_response_status = self.csr_instance.append_new_csr_data(
                    conversation=conversation, csr_id=csr_id, csr_name=csr_name, profile_picture=csr_profile,
                    csr_status=csr_status)
            conversation.save()
            logger.info(f"Updated conversation {conversation_uuid} status to {new_status}")
            return conversation, True

    def get_onqueue_conversations_list(self, csr_id, conversation_uuid):
        """
                    Method to fetch users onqueue conversation list to which csr is assigned
                    Parameters:
                        csr_id (str) : uuid of csr/agent in usermgmt
                        conversation_uuid (str): The UUID of the conversation.
                    Returns :
                        list of onqueue users objects
                """
        logger.info("conversation_service.py :: :: :: ConversationService :: :: :: get_onqueue_conversations_list")
        onqueue_conversations = []
        if conversation_uuid:
            conversation_keys = [f"conversation:{conversation_uuid}"]
        else:
            conversation_keys = self.redis_class_instance.get_all_redis_keys(pattern="conversation:*")
        for key in conversation_keys:
            conversation_data = self.redis_class_instance.get_conversation_data_by_conversation_key(
                conversation_key=key)
            if conversation_data:
                conversation_data = json.loads(conversation_data)

                csr_info = conversation_data.get("csr_info_json", [])
                for csr in csr_info:
                    if csr.get("csr_uid") == csr_id and csr.get("status") == "Assigned":
                        user_details = conversation_data.get("user_details_json", {})
                        message_details = conversation_data.get("message_details_json", [])
                        latest_message = message_details[-1]['message_text'] if message_details else ""
                        created_at = message_details[-1]['created_at'] if message_details else ""
                        assigned_time = csr.get("assigned_time")
                        if assigned_time:
                            assigned_time = datetime.fromisoformat(assigned_time)
                            if assigned_time.tzinfo is None:
                                assigned_time = assigned_time.replace(tzinfo=timezone.utc)
                            else:
                                assigned_time = assigned_time.astimezone(timezone.utc)

                        onqueue_conversations.append({
                            "conversation_uuid": conversation_data["conversation_uuid"],
                            "user_profile_picture": user_details.get("profilePicture", ""),
                            "latest_message": latest_message,
                            "name": user_details.get("name", Constants.ANONYMOUS),
                            "assigned_time": assigned_time.isoformat() if assigned_time else None,
                            "time": created_at
                        })
                        break
        onqueue_conversations.sort(key=lambda x: datetime.fromisoformat(x["assigned_time"]))
        return onqueue_conversations, True
