import hashlib
import json
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from ConnectedCustomerPlatform.exceptions import CustomException

from ChatBot.utils import validate_input
from DBServices.models import Conversations

from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.constants import Constants, AgentDashboardConstants

from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException
from rest_framework.response import Response

from ChatBot.utils import get_redis_connection

from ConnectedCustomerPlatform.responses import CustomResponse


from django.conf import settings
from ChatBot.views.user_info import UserInfoViewSet

logger = logging.getLogger(__name__)
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


class AgentDashboardViewSet(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redis = get_redis_connection()
        self.__azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))



    @action(detail=False, method=[Constants.POST])
    def update_conversation_status(self, request):
        logger.info("In agent_dashboard.py :: :: ::  AgentDashboardViewSet :: :: ::update_conversation_status")
        """
           Update the status of a CSR in a conversation.
           Args:
               request (Request): Contains conversation_uuid (str), csr_uid (int), and csr_status (str).
           Returns:
               Indicates the result of the operation.
           """

        data = request.data
        conversation_uuid = data.get(Constants.CONVERSATION_UUID)
        csr_uid = data.get(Constants.CSR_UID)
        csr_status = data.get(Constants.CSR_STATUS)
        logger.info(f"csr_uid :: {csr_uid} and csr_status :: {csr_status}")
        if not validate_input(conversation_uuid):
            raise CustomException(ErrorMessages.CONVERSATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        if not validate_input(csr_uid):
            raise CustomException(ErrorMessages.CSR_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        if not validate_input(csr_status):
            raise CustomException(ErrorMessages.CSE_STATUS_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        if csr_status in AgentDashboardConstants.VALID_CSR_STATUS:
            conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{conversation_uuid}"
            conversation_data = self.redis.get(conversation_key)
            if conversation_data:
                conversation_data = json.loads(conversation_data)
                csr_info = conversation_data.get(Constants.CSR_INFO_JSON) or []
                logger.info(f"before updating status of csr in redis:: csr_info_json :: {csr_info}")
                updated = False
                for csr in csr_info[::-1]:
                    if csr.get(Constants.CSR_UID) == csr_uid:
                        print(csr)
                        csr[Constants.STATUS] = csr_status
                        updated = True
                        break
                logger.info(f"after updating status of csr in redis:: csr_info_json :: {csr_info}")
                if updated:
                    conversation_data[Constants.CSR_INFO_JSON] = csr_info
                    # Update the modified data back in the Redis cache
                    self.redis.set(conversation_key, json.dumps(conversation_data))
                    # return Response(data={"updated in redis": conversation_data}, status=status.HTTP_200_OK)
                    return CustomResponse(SuccessMessages.CONVERSATION_STATUS_UPDATED)
                else:
                    # return Response(data={"message": "CSR not found in Redis"}, status=status.HTTP_404_NOT_FOUND)
                    raise CustomException(ErrorMessages.CSR_ID_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)


            else:
                conversation = Conversations.objects.filter(conversation_uuid=conversation_uuid).first()
                if conversation is None:
                    raise ResourceNotFoundException(ErrorMessages.CONVERSATION_UUID_NOT_FOUND,
                                                    status_code=status.HTTP_400_BAD_REQUEST)

                csr_info = conversation.csr_info_json or []
                updated = False
                logger.info(f"before updating status of csr in db:: csr_info_json :: {csr_info}")
                for csr in csr_info[::-1]:
                    if csr.get(Constants.CSR_UID) == csr_uid:
                        csr[Constants.STATUS] = csr_status
                        updated = True
                        break
                logger.info(f"after updating status of csr in db:: csr_info_json :: {csr_info}")
                if not updated:
                    raise CustomException(ErrorMessages.CSR_ID_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)

                conversation.csr_info_json = csr_info
                conversation.save()
                return CustomResponse(SuccessMessages.CONVERSATION_STATUS_UPDATED)



    @action(detail=False, methods=[Constants.GET])
    def ongoing_conversations_list(self, request):
        logger.info("In agent_dashboard.py :: :: ::  AgentDashboardViewSet :: :: ::ongoing_conversations_list")
        """
            Retrieve a list of ongoing conversations for a specific CSR.
            Args:
                request (Request): Contains the csr_uid as a query parameter.
            Returns:
                A list of ongoing conversations with details such as 
                conversation UUID, user profile picture, latest message, user name, and message creation time.
            """

        csr_uid = request.query_params.get(Constants.CSR_UID)

        ongoing_conversations = []
        conversation_keys = self.redis.keys(f"{AgentDashboardConstants.CONVERSATION}:*")

        for key in conversation_keys:
            conversation_data = self.redis.get(key)
            if conversation_data:
                conversation_data = json.loads(conversation_data)
                csr_info = conversation_data.get(Constants.CSR_INFO_JSON,"")

                for csr in csr_info:
                    if csr.get(Constants.CSR_UID) == csr_uid and csr.get(
                            Constants.STATUS) == AgentDashboardConstants.ACTIVE:
                        user_details = conversation_data.get(AgentDashboardConstants.USER_DETAILS_JSON, {})
                        message_details = conversation_data.get(AgentDashboardConstants.MESSAGE_DETAILS_JSON, [])
                        latest_message = message_details[-1][
                            AgentDashboardConstants.MESSAGE_TEXT] if message_details else ""
                        created_at = message_details[-1][AgentDashboardConstants.CREATED_AT] if message_details else ""

                        ongoing_conversations.append({
                            Constants.CONVERSATION_UUID: conversation_data[Constants.CONVERSATION_UUID],
                            AgentDashboardConstants.USER_PROFILE_PICTURE: user_details.get(
                                AgentDashboardConstants.PROFILE_PICTURE, ""),
                            AgentDashboardConstants.LATEST_MESSAGE: latest_message,
                            AgentDashboardConstants.NAME: user_details.get(AgentDashboardConstants.NAME, ""),
                            AgentDashboardConstants.TIME: created_at
                        })

                        break
        return CustomResponse(ongoing_conversations)



    @action(detail=False, methods=[Constants.GET])
    def conversation_history_details(self, request):
        logger.info("In agent_dashboard.py :: :: ::  AgentDashboardViewSet :: :: ::conversation_history_details")
        """
            Retrieve the conversation history details.
            Args:
                request (Request): Contains the conversation UUID as a query parameter.
            Returns:
                A list of message details with updated media URLs.
        """
        conversation_uuid = request.query_params.get(Constants.CONVERSATION_UUID)
        if not validate_input(conversation_uuid):
            raise CustomException(ErrorMessages.CONVERSATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{conversation_uuid}"

        conversation_data = self.redis.get(conversation_key)
        if conversation_data:
            conversation_data = json.loads(conversation_data)
            message_details = conversation_data.get(AgentDashboardConstants.MESSAGE_DETAILS_JSON)
            logger.info(f"message_details_json of conversation_uuid {conversation_uuid} :: {message_details}")
            for message_detail in message_details:
                blob_list = message_detail.get(AgentDashboardConstants.MEDIA_URL, [])
                media_url_list = []
                if blob_list:
                    for blob in blob_list:
                        url = blob.get('url', None)
                        name = blob.get('name', None)
                        attachment_type = blob.get('type', None)
                        blob_url = None
                        if url is not None and isinstance(url, str):
                            blob_url = url

                        media_object = {
                            "url": blob_url,
                            "name": name
                        }
                        # Add source for images or start_time for videos
                        if attachment_type == Constants.IMAGE:
                            media_object['type'] = attachment_type
                            media_object['source'] = blob.get('source', None)  # Add source for images
                        elif attachment_type == Constants.VIDEO:
                            media_object['type'] = attachment_type
                            media_object['start_time'] = blob.get('start_time', None)  # Add start time for videos
                        media_url_list.append(media_object)
                    message_detail[AgentDashboardConstants.MEDIA_URL] = media_url_list

            return CustomResponse(message_details)

        else:
            conversation = Conversations.objects.filter(conversation_uuid=conversation_uuid).first()
            if conversation is None:
                raise ResourceNotFoundException(ErrorMessages.CONVERSATION_UUID_NOT_FOUND, status_code=status.HTTP_400_BAD_REQUEST)
            message_details = conversation.message_details_json
            logger.info(f"message_details_json of conversation_uuid {conversation_uuid} :: {message_details}")
            for message_detail in message_details:
                blob_list = message_detail.get(AgentDashboardConstants.MEDIA_URL, [])
                media_url_list = []
                if blob_list:
                    for blob in blob_list:
                        url = blob.get('url', None)
                        name = blob.get('name', None)
                        attachment_type = blob.get('type', None)
                        blob_url = None
                        if url is not None and isinstance(url, str):
                            blob_url = url

                        media_object = {
                            "url": blob_url,
                            "name": name
                        }
                        if attachment_type == Constants.IMAGE:
                            media_object['type'] = attachment_type
                            media_object['source'] = blob.get('source', None)  # Add source for images
                        elif attachment_type == Constants.VIDEO:
                            media_object['type'] = attachment_type
                            media_object['start_time'] = blob.get('start_time', None)  # Add start time for videos

                        media_url_list.append(media_object)
                    message_detail[AgentDashboardConstants.MEDIA_URL] = media_url_list

            return CustomResponse(message_details)

    @action(detail=False, methods=[Constants.GET])
    def conversation_summary(self, request):
        logger.info("In agent_dashboard.py :: :: ::  AgentDashboardViewSet :: :: ::conversation_summary")
        """
            Retrieve the summary of a conversation.
            Args:
                request (Request): Contains the conversation UUID as a query parameter.

            Returns:
                CustomResponse: The summary of the conversation.
            """
        conversation_uuid = request.query_params.get(Constants.CONVERSATION_UUID)
        if not validate_input(conversation_uuid):
            raise CustomException(ErrorMessages.CONVERSATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{conversation_uuid}"
        conversation_data = self.redis.get(conversation_key)
        if conversation_data:
            conversation_data = json.loads(conversation_data)
            chat_summary = conversation_data.get(AgentDashboardConstants.SUMMARY, "")
            return CustomResponse(chat_summary)
        else:
            conversation = Conversations.objects.filter(conversation_uuid=conversation_uuid).first()
            if conversation is None:
                raise ResourceNotFoundException(ErrorMessages.CONVERSATION_UUID_NOT_FOUND, status_code=status.HTTP_400_BAD_REQUEST)
            chat_summary = conversation.summary
            return CustomResponse(chat_summary)



    @action(detail=False, methods=[Constants.GET])
    def total_conversation_information(self, request):
        logger.info("In agent_dashboard.py :: :: ::  AgentDashboardViewSet :: :: ::total_conversation_information")
        """
            Retrieve the summary of a conversation.
            Args:
                request (Request): Contains the conversation UUID as a query parameter.

            Returns:
                CustomResponse: The summary of the conversation.
            """

        conversation_uuid = request.query_params.get(Constants.CONVERSATION_UUID)
        if not validate_input(conversation_uuid):
            raise CustomException(ErrorMessages.CONVERSATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)

        conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{conversation_uuid}"
        intents_list = []
        sentiment_list=[]
        conversation_data = self.redis.get(conversation_key)

        if conversation_data:
            conversation_data = json.loads(conversation_data)
            conversation_uuid = conversation_data["conversation_uuid"]
            user_details = conversation_data["user_details_json"]
            token_id = hashlib.sha256(conversation_uuid.encode()).hexdigest()[:16]
            message_details_json = conversation_data.get("message_details_json", [])
            for message in message_details_json:
                dimension_action_json = message.get("dimension_action_json", {})
                source=message.get(Constants.SOURCE,None)
                dimensions = dimension_action_json.get("dimensions", [])

                for dimension in dimensions:
                    if dimension.get("dimension") == "Intent":
                        intent_value = dimension.get("value")
                        if intent_value not in intents_list:
                            intents_list.append(intent_value)
                    elif source==Constants.USER and dimension.get("dimension") == "Sentiment":
                        sentiment_list.append(dimension.get("value"))

            if sentiment_list:
                if len(sentiment_list) > 1:
                    # Use MESSAGE_INDEX to get the desired sentiment value
                    sentiment = sentiment_list[AgentDashboardConstants.MESSAGE_INDEX]
                else:
                    # There's only one or no sentiment in the list
                    sentiment = sentiment_list[0] if sentiment_list else None
            else:
                sentiment = None

            chat_summary = conversation_data.get(AgentDashboardConstants.SUMMARY, "")
            result = {
                "intents": intents_list,
                "sentiment": sentiment,
                "ticket_id": token_id,
                "summary": chat_summary,
                "user_details": user_details
            }

            # return Response(data={"summary": message_details_json}, status=200)
            return CustomResponse(result)

        else:
            conversation = Conversations.objects.filter(conversation_uuid=conversation_uuid).first()
            if conversation is None:
                raise ResourceNotFoundException(ErrorMessages.CONVERSATION_UUID_NOT_FOUND,
                                                status_code=status.HTTP_400_BAD_REQUEST)

            conversation_uuid = conversation.conversation_uuid
            token_id = hashlib.sha256(conversation_uuid.encode()).hexdigest()[:16]
            chat_summary = conversation.summary
            user_details = conversation.user_details_json
            message_details_json = conversation.message_details_json
            for message in message_details_json:
                dimension_action_json = message.get("dimension_action_json", {})
                dimensions = dimension_action_json.get("dimensions", [])

                for dimension in dimensions:
                    if dimension.get("dimension") == "Intent":
                        intent_value = dimension.get("value")
                        if intent_value not in intents_list:
                            intents_list.append(intent_value)

            result = {
                "intents": intents_list,
                "ticket_id": token_id,
                "summary": chat_summary,
                "user_details": user_details
            }

            # return Response(data={"summary": chat_summary}, status=200)
            return CustomResponse(result)

