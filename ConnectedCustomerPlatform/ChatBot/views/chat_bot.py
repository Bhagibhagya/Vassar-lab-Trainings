from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
import uuid
import os
import json
from rest_framework.response import Response
from rest_framework import status
from azure.storage.blob import BlobServiceClient
import logging
from DBServices.models import Conversations
#from ChatBot.serializers import RatingSerializer
from ConnectedCustomerPlatform.responses import CustomResponse
from ChatBot.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException
from ChatBot.utils import get_redis_connection
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager
from django.conf import settings
from ChatBot.constant.constants import Constants
from ChatBot.constant.error_messages import ErrorMessages

from DBServices.models import DimensionTypes
from DBServices.models import Dimensions

logger = logging.getLogger(__name__)
# Create your views here.
class ChatBotViewSet(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redis = get_redis_connection()
        self.azureblobmanager = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)

    @action(detail=False, methods=['get'])
    def get_message(self, request):
        return Response(data={"message": "hello"}, status=200)


    def change_conversation_status(self, conversation_uuid, new_status, csr_id , csr_name , csr_profile,csr_status,assigned_time):

        logger.info("chat_bot.py :: :: :: ChatBotViewSet :: :: :: change_conversation_status")
        """
        Logic to change the status of a conversation.
        Parameters:
            conversation_uuid (str): The UUID of the conversation.
            new_status (str): The new status of the conversation. Should be one of ['resolved', 'bot_ongoing', 'csr_ongoing'].
        """
        conversation_key = f"conversation:{conversation_uuid}"
        conversation_data = self.redis.get(conversation_key)
        if conversation_data:
            conversation_data = json.loads(conversation_data)
            conversation_data["conversation_status"] = new_status

            if new_status == 'CSR_ONGOING':
                conversation_data['csr_hand_off'] = True

                conversation_data = self.append_csr(conversation_data,csr_id,csr_name,csr_profile,csr_status,assigned_time)
            self.redis.set(conversation_key, json.dumps(conversation_data))
            return 1
        else:
            conversation = Conversations.objects.get(conversation_uuid=conversation_uuid)
            if not conversation:
                logger.error(f"Conversation with UUID {conversation_uuid} does not exist in the database.")
                raise ResourceNotFoundException(f"{conversation_uuid} does not exist in the database.")

            conversation.conversation_status = new_status
            if new_status == 'CSR_ONGOING':
                conversation.csr_hand_off = True

                conversation = self.append_csr(conversation_data,csr_id,csr_name,csr_profile,csr_status,assigned_time)
            conversation.save()
            logger.info(f"Updated conversation {conversation_uuid} status to {new_status}")
            return 1



    def append_csr(self,conversation, csr_id, name, profile_picture,csr_status,assigned_time):

        new_csr_info = {
            Constants.CSR_UID: csr_id,
            Constants.NAME: name,
            Constants.PROFILE_PICTURE: profile_picture,
            Constants.STATUS: csr_status,
            Constants.ASSIGNED_TIME: assigned_time
        }
        csr_info_list = conversation.get(Constants.CSR_INFO_JSON, []) if isinstance(conversation, dict) else json.loads(conversation.csr_info_json or '[]')
        csr_info_list.append(new_csr_info)

        if isinstance(conversation, dict):
            conversation[Constants.CSR_INFO_JSON] = csr_info_list
        else:
            conversation.csr_info_json = csr_info_list

        return conversation

    @action(detail=False, methods=['get'])
    def get_all_intents(self, request):
        logger.info("dimension_intent.py :: :: :: DimensionIntentViewSet :: :: :: get_all_intents")
        """
        Get all intents In Dimension table from platform.
        """
        # Retrieve application_uuid and customer_uuid from headers
        application_uuid = request.headers.get('application-uuid')
        customer_uuid = request.headers.get('customer-uuid')
        dimension_type = DimensionTypes.objects.filter(dimension_type_name=Constants.DIMENSION_TYPE_NAME_INTENT,customer_uuid=customer_uuid,application_uuid=application_uuid,status = True,is_deleted = False).first()
        if dimension_type is None:
            return CustomResponse({Constants.INTENTS: []})
        dimension_type_uuid = dimension_type.dimension_type_uuid
        if not application_uuid or not customer_uuid :
            return CustomResponse(
                Constants.NO_HEADERS,
                status=False,code = status.HTTP_400_BAD_REQUEST
            )

        dimensions = Dimensions.objects.filter(
            application_uuid=application_uuid,
            customer_uuid=customer_uuid,
            is_deleted=False,
            dimension_type_uuid=dimension_type_uuid
        )

        intents = [dimension.dimension_name for dimension in dimensions]
        result = {Constants.INTENTS: intents}
        return CustomResponse(result)
