import asyncio
import json
import uuid

import pytz
import redis
import redis.cluster
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from asgiref.sync import sync_to_async
import logging

from ChatBot.constant.constants import Constants, specification_json, CustomCloseCodes, AgentDashboardConstants
from DBServices.models import Conversations, Dimensions
from django.db.models import Q
from asgiref.sync import sync_to_async
from ChatBot.utils import get_redis_connection
from datetime import datetime
from AIServices.BOT.bot import ChatbotIntentClassification
from AIServices.BOT.HistorySummariesBot.bot import HistorySummarize
from rest_framework import status
from ConnectedCustomerPlatform.exceptions import CustomException

# from EventHub.send_sync import EventHubProducerSync

from ChatBot.wiseflow import start_wise_flow


from ChatBot.services.hot_handoff_service import HotHandoffService

# from EventHub.send import EventHubProducer

from EventHub.EventHubProducerSingleton import EventHubProducerSingleton

from ChatBot.constant.error_messages import ErrorMessages
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager

from django.conf import settings

logger = logging.getLogger(__name__)
classify_intent = ChatbotIntentClassification()
history_summarize = HistorySummarize()

ist = pytz.timezone('Asia/Kolkata')
class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.connection_uuid = None
        self.conversation_key = None
        self.conversation = None
        self.redis = get_redis_connection()
        self.room_name = None
        self.start_time = ""
        self.end_time = ""
        self.is_csr = "false"
        self.csr_id = None
        self.destination = ""
        self.application_uuid = None
        self.customer_uuid = None
    async def connect(self):
        await self.accept()
        received_data = self.scope['query_string']
        query_params = dict(x.split('=') for x in received_data.decode().split('&') if '=' in x)
        conversation_uuid = query_params.get('conversation_uuid')

        logger.info(f"WebSocket connected. Channel name: {self.channel_name}")
        self.is_csr = query_params.get('is_csr', "false")

        self.destination = query_params.get('destination')
        self.csr_id = query_params.get('csr_id')
        self.application_uuid = query_params.get('application_uuid')
        self.customer_uuid = query_params.get('customer_uuid')

        if self.is_csr == "true" and self.destination == "server":
            self.room_name = f"csr_{self.csr_id}"
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            logger.info(f"CSR connected to room: {self.room_name}")
            await self.broadcast_csr_onqueue_conversations(self.csr_id,conversation_uuid=None)
            from ChatBot.views.user_info import UserInfoViewSet
            user_info = UserInfoViewSet()
            user_info.update_user(self.csr_id,self.channel_name,Constants.ONLINE)
            logger.info(f"CSR connected to room: {self.room_name}")

        if self.is_csr == "true" and self.destination == "endUser":
            self.connection_uuid = conversation_uuid
            self.conversation_key = f"conversation:{self.connection_uuid}"
            if conversation_uuid:
                self.room_name = f"room_{conversation_uuid}"
                logger.info("ROOM NAME")
                logger.info(self.room_name)
                await self.channel_layer.group_add(
                    self.room_name,
                    self.channel_name
                )

        if self.is_csr == "false" and conversation_uuid:
            self.connection_uuid = conversation_uuid
            self.conversation_key = f"conversation:{self.connection_uuid}"

            # Check if conversation exists in Redis
            conversation_data = self.redis.get(self.conversation_key)
            if conversation_data:
                conversation_data = json.loads(conversation_data)
                logger.info(f"Loaded existing conversation from Redis with UUID: {self.connection_uuid}")
                conversation_status = conversation_data["conversation_status"]
                if conversation_status == "CSR_ONGOING":
                    await self.add_to_room()
            else:
                # Check if conversation exists in the database and is not resolved
                try:
                    conversation = await self.get_conversation_from_db(conversation_uuid)
                    conversation_status = conversation.conversation_status
                    if conversation_status in [Constants.CLOSED, Constants.CSR_RESOLVED, Constants.BOT_RESOLVED]:
                        conversation_status = Constants.BOT_ONGOING
                        conversation_stats = conversation.conversation_stats_json
                        conversation_stats.append({
                            "conversationStartTime": datetime.now().isoformat(),
                        })

                        conversation.conversation_stats_json = conversation_stats
                    if conversation:
                        conversation_data = {
                            "conversation_uuid": conversation.conversation_uuid,
                            "name": conversation.name,
                            "user_details_json": conversation.user_details_json,
                            "conversation_status": conversation_status,
                            "csr_info_json": conversation.csr_info_json,
                            "csr_hand_off": conversation.csr_hand_off,
                            "conversation_stats_json": conversation.conversation_stats_json,
                            "conversation_feedback_transaction_json": conversation.conversation_feedback_transaction_json,
                            "task_details_json": conversation.task_details_json,
                            "summary": conversation.summary,
                            "application_uuid": conversation.application_uuid,
                            "customer_uuid": conversation.customer_uuid,
                            "message_details_json": conversation.message_details_json,
                            "insert_ts": conversation.insert_ts.isoformat() if conversation.insert_ts else None,
                        }
                        # Load conversation data to Redis
                        self.redis.set(self.conversation_key, json.dumps(conversation_data))
                        logger.info(f"Loaded existing conversation from DB to Redis with UUID: {self.connection_uuid}")
                        conversation_status = conversation_data["conversation_status"]
                        if conversation_status == "CSR_ONGOING":
                            await self.add_to_room()
                    else:
                        # Conversation is resolved, create a new one
                        # TODO :: need to update methode here,
                        self.create_new_conversation()
                        await self.send_json({"connection_uuid": self.connection_uuid})
                        #await self.send_reply(Constants.INITIAL_MESSAGE,specification_json)
                except Conversations.DoesNotExist:
                    # Conversation does not exist, create a new one
                    self.create_new_conversation()
                    await self.send_json({"connection_uuid": self.connection_uuid})
                    # TODO :: need to update methode here,
                    #await self.send_reply(Constants.INITIAL_MESSAGE,specification_json)

        elif self.is_csr == "false" and not conversation_uuid:
            self.create_new_conversation()
            await self.add_to_room()
            await self.send_json({"connection_uuid": self.connection_uuid})
            # TODO :: need to update methode here,
            #await self.send_reply(Constants.INITIAL_MESSAGE,specification_json)

        else:
            pass
            # await self.add_to_room()

    async def disconnect(self, close_code):
        logger.info(f"Connection with UUID: {self.connection_uuid}")
        logger.info(f"close_code: {close_code}")

        if self.is_csr == "true" and self.destination == "server":
            from ChatBot.views.user_info import UserInfoViewSet
            user_info = UserInfoViewSet()
            user_info.update_user(self.csr_id,self.channel_name,Constants.OFFLINE)
        # close_code 4001 means hot_handoff successful : current csr is successfully transferred the conversation to new csr
        # because we dont need to store redis conversation data into db
        elif close_code == CustomCloseCodes.HOT_HANDOFF_SUCCESSFUL_CODE and self.is_csr == "true" and self.destination == "endUser":
            logger.info("closing current csr connection after new csr is assigned")
            pass
        # when csr clicked "mark as resolved"  button
        elif close_code == CustomCloseCodes.CSR_MARK_AS_RESOLVED_CODE and self.is_csr == "true" and self.destination == "endUser":
            logger.info("closing csr connection when he clicked mark as resolved button")
            self.end_time = datetime.now().isoformat()
            conversation_data = self.redis.get(self.conversation_key)
            conversation_data = json.loads(conversation_data)
            await self.send_to_room(Constants.NOTIFICATION, Constants.CSR_RESOLVED_MESSAGE)
            conversation_data[Constants.CONVERSATIONS_STATUS] = Constants.CSR_RESOLVED
            csr_info = conversation_data.get("csr_info_json", [])
            for csr in csr_info:
                if csr["csr_uid"] == self.csr_id:
                    csr["status"] = "Inactive"
            conversation_stats = conversation_data.get("conversation_stats_json", [])
            last_stat = conversation_stats[-1]
            last_stat["conversationResolutionTime"] = self.end_time
            self.redis.set(self.conversation_key, json.dumps(conversation_data))
            await sync_to_async(self.save_conversation_to_db)(self.conversation_key)

        elif close_code == None and self.is_csr == "false":
            logger.info("closing user connection")
            self.end_time = datetime.now().isoformat()
            conversation_data = self.redis.get(self.conversation_key)
            conversation_data = json.loads(conversation_data)
            conversation_data["conversation_status"] = "CLOSED"
            csr_info = conversation_data.get("csr_info_json", [])
            if csr_info:
                csr = csr_info[-1]
                csr["status"] = "Inactive"
            conversation_stats = conversation_data.get("conversation_stats_json", [])
            last_stat = conversation_stats[-1]
            last_stat["conversationResolutionTime"] = self.end_time
            conversation_data[Constants.CONVERSATIONS_STATUS] = Constants.CLOSED
            self.redis.set(self.conversation_key, json.dumps(conversation_data))
            await sync_to_async(self.save_conversation_to_db)(self.conversation_key)
        await self.discard_from_room()
        await self.close()


    @sync_to_async
    def get_conversation_from_db(self, conversation_uuid):
        try:
            return Conversations.objects.get(conversation_uuid=conversation_uuid)
        except Conversations.DoesNotExist:
            return None

    async def receive_json(self, data):
        local_time = datetime.now()
        ist_time = local_time.astimezone(ist)
        logger.info(f"Time profile :: main microservice :: receive_json :: message receiving time:: {ist_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        logger.info(f"Received data from UUID {self.connection_uuid}: {data}")
        if "user_info" in data:
            user_info_json = data["user_info"]
            name = user_info_json.get('name')
            user_uuid = user_info_json.get('user_uuid')
            conversation_data = self.redis.get(self.conversation_key)
            conversation_data = json.loads(conversation_data)
            user_details = conversation_data.get('user_details_json', {})
            user_details['name'] = name
            user_details['user_uuid'] = user_uuid
            conversation_data['user_details_json'] = user_details
            self.redis.set(self.conversation_key, json.dumps(conversation_data))
        if 'message' in data:
            message_json = data['message']
            message_json_dict = json.loads(message_json)

            regenerate = message_json_dict.get("regenerate",False)
            role_id = Constants.ROLE_ID
            logger.info(
                f"\nTime profile :: main chatbot microservice :: time before get_updated_message_detail  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            message_detail = self.get_updated_message_detail(message_json)
            logger.info(
                f"\nTime profile :: main chatbot microservice :: time after get_updated_message_detail  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            user_query = message_detail["message_text"]
            message_type = message_detail["message_type"]
            mobile_number_with_country_code = message_detail.get("wa_id", None) # fetching mobile number with country code  wa_id : whatsapp id
            logger.info(
                f"\nTime profile :: main chatbot microservice :: time before remove_country_code  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            if mobile_number_with_country_code is not None:
                mobile_number = self.remove_country_code(mobile_number_with_country_code)
            else:
                mobile_number = None
            logger.info(
                f"\nTime profile :: main chatbot microservice :: time after remove_country_code  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

            logger.info(
                f"\nTime profile :: main chatbot microservice :: time before fetch_conversation_status  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            conversation_status = self.fetch_conversation_status()
            logger.info(
                f"\nTime profile :: main chatbot microservice :: time after fetch_conversation_status  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            if self.is_csr == "false" and conversation_status != "CSR_ONGOING":

                answer_id = message_json_dict.get("message_answer_id", "")
                question_uuid = message_json_dict.get("question_uuid", "")
                user_details = self.get_user_details()
                regenerate_level = 0
                if regenerate and answer_id:
                    regenerate_level = await self.handle_regenerate_count(answer_id)
                    if regenerate_level is None:
                        return

                # Intent classification
                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time before fetch_chat_history  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                chat_history = self.fetch_chat_history()
                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time after fetch_chat_history  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time before start_wise_flow  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                next_step_uuid, next_topic = await sync_to_async(start_wise_flow)(self.customer_uuid, self.application_uuid, Constants.CHANNEL_TYPE_UUID)
                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time after start_wise_flow  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time before get_json_for_eventhub  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                eventhub_json = await self.get_json_for_eventhub(self.connection_uuid, self.channel_name, self.customer_uuid,
                                                       self.application_uuid, user_query, chat_history,
                                                       next_step_uuid, mobile_number, message_detail.get("id"),
                                                       message_type, regenerate_level, answer_id, question_uuid, user_details)
                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time after get_json_for_eventhub  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time before store_message_in_cache  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                if not regenerate:
                    await self.store_message_in_cache(message_detail)
                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time after store_message_in_cache  ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                logger.info(
                    f"\nTime profile :: main chatbot microservice :: time before producing event to {next_topic} ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                await EventHubProducerSingleton.send_event_data_batch(eventhub_json, next_topic)

                logger.info(
                        f"\nTime profile :: main chatbot microservice :: time after publishing ::  {self.connection_uuid}  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                logger.info(
                        "\n\n------Produced successfully from Main Micro Service to Intent Classification Micro Service----------\n\n")

                # await asyncio.create_task(publish_event())
                # await task  # Ensure the task completes
                # producer.close()
            else:
                logger.info("user and csr conversation")
                logger.info(f"message_dtails :: {message_detail}")
                await self.store_message_in_cache(message_detail)
                media_url = message_detail.get(AgentDashboardConstants.MEDIA_URL, [])
                if media_url is None:
                    media_url = []
                if len(media_url) > 0:
                    azure_service_utils = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)
                    # TODO : need to change media_url of private url into public urls
                    media_url = azure_service_utils.create_presigned_url_for_media_url(Constants.CONTAINER_NAME, media_url)
                message_detail[AgentDashboardConstants.MEDIA_URL] = media_url
                await self.send_to_room(Constants.MESSAGE, message_detail)

        if 'deliveryMarker' in data:
            delivery_marker = json.loads(data['deliveryMarker'])
            logger.info(f"delivery_marker::{delivery_marker}")
            conversation_data = self.redis.get(self.conversation_key)
            conversation_status = None
            if conversation_data:
                conversation_data = json.loads(conversation_data)
                logger.info(f"Loaded existing conversation from Redis with UUID: {self.connection_uuid}")
                conversation_status = conversation_data["conversation_status"]
            if self.is_csr == "true" and self.destination == "endUser":
                await self.send_to_room(Constants.DELIVERY_MARKER, delivery_marker)
                self.update_marker_status(delivery_marker)
            elif self.is_csr == "false" and conversation_status == "CSR_ONGOING":
                await self.send_to_room(Constants.DELIVERY_MARKER, delivery_marker)
                self.update_marker_status(delivery_marker)
            else:
                self.update_marker_status(delivery_marker)
        if 'typingIndicator' in data:
            typing_data = json.loads(data['typingIndicator'])
            if self.is_csr == "true" and self.destination == "endUser":
                # CSR is typing, send to user room
                await self.send_to_room(Constants.TYPING_INDICATOR, typing_data)
            elif self.is_csr == "false":
                conversation_data = self.redis.get(self.conversation_key)
                if conversation_data:
                    conversation_data = json.loads(conversation_data)
                    logger.info(f"Loaded existing conversation from Redis with UUID: {self.connection_uuid}")
                    conversation_status = conversation_data["conversation_status"]
                    if conversation_status == "CSR_ONGOING":
                        # User is typing, send to CSR room
                        await self.send_to_room(Constants.TYPING_INDICATOR, typing_data)
        if "hotHandoff" in data:
            hot_handoff_data = data['hotHandoff']
            hot_handoff_service = HotHandoffService()
            hot_handoff_method_response = await hot_handoff_service.hot_handoff(hot_handoff_data=hot_handoff_data, channel_id=self.channel_name)
            hot_handoff_response_object = {
                "hot_handoff_status_message": hot_handoff_method_response.get("result"),
                "status": hot_handoff_method_response.get("status")
            }
            await self.send_json({Constants.NOTIFICATION: hot_handoff_response_object})

    async def handle_regenerate_count(self, message_id):
        # Retrieve conversation data from Redis
        conversation_data = self.redis.get(self.conversation_key)
        conversation_data = json.loads(conversation_data)
        message_details_json = conversation_data.get("message_details_json", [])

        regenerate_level = 0
        updated = False
        # Iterate through message_details_json to find and update the regenerate level
        for message in message_details_json:
            if message.get('id') == message_id:
                regenerate_level = message.get('regenerate_level')
                if regenerate_level < Constants.MAX_REGENERATE_COUNT:
                    updated = True
                    message['regenerate_level'] = regenerate_level + 1
                    break
                elif regenerate_level >= Constants.MAX_REGENERATE_COUNT:
                    notification_message = ErrorMessages.MAX_REGENERATE_MESSAGE.format(
                        answer_id=message_id,
                        regenerate_level=regenerate_level,
                        max_regenerate_count=Constants.MAX_REGENERATE_COUNT
                    )
                    await self.send_event({Constants.NOTIFICATION: notification_message},
                                          status.HTTP_400_BAD_REQUEST)
                    return 

        if updated:
            regenerate_level += 1
            self.redis.set(self.conversation_key, json.dumps(conversation_data))

        return regenerate_level

    def fetch_conversation_status(self):
        conversation_data = self.redis.get(self.conversation_key)
        conversation_data = json.loads(conversation_data)
        return conversation_data["conversation_status"]

    def create_new_conversation(self):
            self.connection_uuid = str(uuid.uuid4())
            self.conversation_key = f"conversation:{self.connection_uuid}"
            logger.info(f"Creating new conversation with UUID: {self.connection_uuid}")
            self.start_time = datetime.now().isoformat()
            conversation_data = {
                "conversation_uuid": self.connection_uuid,
                "name": "",
                "user_details_json":
                {
                    "name": Constants.ANONYMOUS,
                    "userType": Constants.USER_TYPE
                },
                "csr_info_json":[],
                "csr_hand_off":False,
                "conversation_stats_json":[{
                    "conversationStartTime": self.start_time
                }],
                "conversation_feedback_transaction_json":{},
                "task_details_json":{},
                "conversation_status": Constants.BOT_ONGOING,
                "summary": "Conversation initiated",
                "application_uuid": self.application_uuid,  # Replace with actual application UUID
                "customer_uuid": self.customer_uuid,  # Replace with actual customer UUID
                "message_details_json": [],
                "insert_ts":timezone.now().isoformat(),
            }
            self.redis.set(self.conversation_key, json.dumps(conversation_data))

    def get_updated_message_detail(self, message_detail):
        message_detail = json.loads(message_detail)
        message_detail.update({
            "id": message_detail.get("id", str(uuid.uuid4())),  # Unique message ID
            "csr_id": message_detail.get("csr_id", None),  # Use provided csr_id or default to None
            "source": message_detail.get("source", "user"),
            "message_marker": message_detail.get("message_marker", "LOGGED"),
            "dimension_action_json": message_detail.get("dimension_action_json", {}),
            "message_text": message_detail.get("message_text", ""),
            "media_url": message_detail.get("media_url", []),
            "parent_message_uuid": message_detail.get("parent_message_uuid", None),
            "created_at": message_detail.get("created_at", timezone.now().isoformat()),
            "message_type": message_detail.get("message_type",None),
        })
        return message_detail
    #
    def print_redis_conversation(self):
        keys = self.redis.keys('*')
        logger.info(self.redis.keys('*'))
        for key in keys:
            # we cannot print value of group/room key
            if not str(key).__contains__("group"):
                value = self.redis.get(key)
                logger.info(f"Key: {key}, Value: {value}")

    async def send_reply(self, message_text,specification_json=None):
        # Send response back ** need modification **
        conversation_data = self.redis.get(self.conversation_key)
        conversation_data = json.loads(conversation_data)

        # Get the parent message UUID (last message's UUID if available)
        last_message = conversation_data["message_details_json"][-1] if conversation_data[
            "message_details_json"] else None
        parent_message_uuid = last_message["id"] if last_message else None
        reply_data = {
            "id": str(uuid.uuid4()),  # Unique message ID
            "csr_id": None,  # Use provided csr_id or default to None
            "source": "bot",
            "message_marker": "LOGGED",
            "dimension_action_json": {},
            "message_text": message_text,
            "media_url": [],
            "parent_message_uuid": parent_message_uuid,
            "created_at": timezone.now().isoformat(),
            "specifications": specification_json

        }

        reply_data_json = {
            "message": reply_data,
            "connection_uuid": self.connection_uuid
        }

        conversation_data["message_details_json"].append(reply_data)
        self.redis.set(self.conversation_key, json.dumps(conversation_data))
        await self.send_json(reply_data_json)

        
    async def get_json_for_eventhub(self, conversation_uuid, channel_id, customer_uuid, application_uuid, user_query, chat_history, next_step_uuid, mobile_number, message_id , message_type , regenerate_level, message_answer_id, question_uuid, user_details):
        if message_type == Constants.BUTTON:
            intent_dimension_value = await self.get_intent_from_button_text(user_query)
        else:
            intent_dimension_value = self.find_user_previous_message_intent()
            
        event_data = {
            "conversation_uuid": conversation_uuid,
            "channel_id": channel_id,
            "customer_uuid": customer_uuid,
            "application_uuid": application_uuid,
            "query": user_query,
            "message_id": message_id,
            "chat_history": chat_history,
            "mobile_number": mobile_number,
            "step_info": {"step_uuid": next_step_uuid},
            "previous_intent": intent_dimension_value,
            "regenerate_level": regenerate_level,
            "message_answer_id": message_answer_id,
            "question_uuid": question_uuid,
            "user_details": user_details
        }
        return json.dumps(event_data)

    def find_user_previous_message_intent(self):
        redis_conversation_data = self.redis.get(self.conversation_key)
        conversation_data = json.loads(redis_conversation_data)
        logger.info("find_user_previous_message_intent :: conversation_data :: ", conversation_data)
        message_details_json = conversation_data.get(Constants.MESSAGE_DETAILS_JSON, [])
        last_user_message = {}
        intent_dimension_value = Constants.INITIAL_MESSAGE_INTENT
        for single_message_object in message_details_json[::-1]:
            if single_message_object.get(Constants.SOURCE) == Constants.USER:
                last_user_message = single_message_object
                break
        dimension_action_json = last_user_message.get(Constants.DIMENSION_ACTION_JSON, {})
        dimensions = dimension_action_json.get(Constants.DIMENSIONS, [])
        for dimension in dimensions:
            if dimension.get(Constants.DIMENSION, "") == Constants.DIMENSION_INTENT:
                intent_dimension_value = dimension.get(Constants.VALUE)
                break
        if intent_dimension_value is None:  # if intent_dimension_value is None
            intent_dimension_value = Constants.INITIAL_MESSAGE_INTENT
        return intent_dimension_value

    async def get_intent_from_button_text(self, message_text):
        dimension = await sync_to_async(
            Dimensions.objects.filter(Q(dimension_details_json__default_text=message_text)).first)()
        if dimension:
            return dimension.dimension_name
        else:
            return Constants.INITIAL_MESSAGE_INTENT

    async def store_message_in_cache(self, message_detail):
        # Retrieve the current conversation data from Redis
        conversation_data = self.redis.get(self.conversation_key)
        conversation_data = json.loads(conversation_data)
        # logger.info(conversation_data)

        # Get the parent message UUID (last message's UUID if available)
        last_message = conversation_data["message_details_json"][-1] if conversation_data[
            "message_details_json"] else None
        parent_message_uuid = last_message["id"] if last_message else None

        # Update the message detail with the parent_message_uuid
        message_detail["parent_message_uuid"] = parent_message_uuid
        conversation_data["message_details_json"].append(message_detail)
        # Save the updated conversation data back to Redis
        self.redis.set(self.conversation_key, json.dumps(conversation_data))

    def save_conversation_to_db(self, conversation_key=None):
        # Retrieve the conversation data from Redis
        conversation_key = conversation_key or self.conversation_key
        conversation_data = self.redis.get(conversation_key)
        if conversation_data:
            conversation_data = json.loads(conversation_data)
            # Create a new Conversations instance
            conversation = Conversations(
                conversation_uuid=conversation_data["conversation_uuid"],
                name=conversation_data["name"],
                user_details_json=conversation_data["user_details_json"],
                conversation_status=conversation_data["conversation_status"],
                csr_info_json=conversation_data["csr_info_json"],
                csr_hand_off=conversation_data["csr_hand_off"],
                conversation_stats_json=conversation_data["conversation_stats_json"],
                conversation_feedback_transaction_json=conversation_data["conversation_feedback_transaction_json"],
                task_details_json=conversation_data["task_details_json"],
                summary=conversation_data["summary"],
                application_uuid=conversation_data["application_uuid"],
                customer_uuid=conversation_data["customer_uuid"],
                message_details_json=conversation_data["message_details_json"],
                insert_ts=conversation_data["insert_ts"]
            )
            # Save the instance to the database
            conversation.save()
            # delete the data from Redis
            self.redis.delete(conversation_key)

    def update_marker_status(self, delivery_marker):
        logger.debug(f"Updating marker status...{delivery_marker}")

        message_id = delivery_marker.get('id')
        marker_status = delivery_marker.get('marker_status')
        if message_id is not None and marker_status in Constants.VALID_MARKER_STATUS:
            conversation_data = self.redis.get(self.conversation_key)
            if conversation_data:
                conversation_data = json.loads(conversation_data)
                message = next((msg for msg in conversation_data['message_details_json'] if msg["id"] == message_id),
                               None)
                if message:
                    message['message_marker'] = marker_status
                    logger.info(f"Updated marker status for message ID {message_id} to {marker_status}.")
                self.redis.set(self.conversation_key, json.dumps(conversation_data))
            else:
                logger.warning("Conversation data not found in Redis.")
        else:
            logger.error("Invalid message ID or marker status.")

    async def send_marker_status(self, message_id, marker_status):
        """Send status updates and a reply message."""
        await self.send_json({Constants.DELIVERY_MARKER: {'id': message_id, 'marker_status': marker_status}})

    def update_conversation_field(self, field, value):
        # Retrieve the current conversation data from Redis
        conversation_data = self.redis.get(self.conversation_key)
        if conversation_data:
            conversation_data = json.loads(conversation_data)
            # Update the specified field with the new value
            conversation_data[field] = value
            # Save the updated conversation data back to Redis
            self.redis.set(self.conversation_key, json.dumps(conversation_data))
        else:
            logger.info(f"No conversation data found for key: {self.conversation_key}")

    def fetch_chat_history(self):
        conversation_data = json.loads(self.redis.get(self.conversation_key))
        message_details_json = conversation_data['message_details_json']
        from ChatBot.utils import refactor_history_from_conversation
        history = refactor_history_from_conversation(message_details_json)
        return history

    def remove_country_code(self, mobile_number):
        # Assuming the country code is always the first 2 or 3 digits (e.g., '91' for India)
        if len(mobile_number) > 10:  # Assuming a valid mobile number length is 10 digits
            return mobile_number[-10:]  # Slice the last 10 digits
        return mobile_number  # Return as is if no country code is detected

    def update_dimension(self, dimension_name, dimension_value, message_details_json):
        # Retrieve the dimensions list from dimension_action_json, initializing if it doesn't exist
        dimension_action_json = message_details_json.get("dimension_action_json", {})
        dimensions = dimension_action_json.get("dimensions", [])

        # Flag to check if the dimension exists
        dimension_exists = False

        # Iterate over dimensions to find if the dimension_name already exists
        for dimension in dimensions:
            if dimension.get('dimension') == dimension_name:
                # Update the value if dimension is found
                dimension['value'] = dimension_value
                dimension_exists = True
                break

        # If the dimension does not exist, add a new one
        if not dimension_exists:
            dimensions.append({
                'dimension': dimension_name,
                'value': dimension_value
            })

        # Update the dimension_action_json with the modified dimensions list
        dimension_action_json['dimensions'] = dimensions
        message_details_json['dimension_action_json'] = dimension_action_json

        return message_details_json



    async def broadcast_csr_onqueue_conversations(self,csr_id,conversation_uuid=None):
        csr_data = await self.onqueue_conversations_list(csr_id,conversation_uuid)
        logger.info(csr_data)
        reply_data_json = {
            "csr_id": csr_id,
            "onqueue_conversations": csr_data
        }

        await self.channel_layer.group_send(
            f"csr_{csr_id}",
            {
                'type': 'send_message',
                'message': json.dumps(reply_data_json)
            }
        )

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=message)
    async def chat_message(self, event):
        message = event['message']
        await self.send_json(message)

    async def onqueue_conversations_list(self, csr_uid,conversation_uuid):
        try:
            if not csr_uid:
                return CustomException("csr_uid parameter is missing", status_code=status.HTTP_400_BAD_REQUEST)

            onqueue_conversations = []
            if conversation_uuid:
                conversation_keys = [f"conversation:{conversation_uuid}"]
            else:
                conversation_keys = self.redis.keys("conversation:*")
            for key in conversation_keys:
                conversation_data = self.redis.get(key)
                if conversation_data:
                    conversation_data = json.loads(conversation_data)

                    csr_info = conversation_data.get("csr_info_json", [])
                    for csr in csr_info:
                        if csr.get("csr_uid") == csr_uid and csr.get("status") == "Assigned":
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
                                "assigned_time":  assigned_time.isoformat() if assigned_time else None,
                                "time": created_at
                            })
                            break
            onqueue_conversations.sort(key=lambda x: datetime.fromisoformat(x["assigned_time"]))
            return onqueue_conversations

        except Exception as e:
            logger.debug(f"Exception occurred: {str(e)}")
            raise CustomException({"error": "An error occurred while retrieving onqueue conversations"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    async def send_csr_details(self, instance ,csr_details):
        """Send CSR details to User"""
        csr_id = csr_details[Constants.CSR_UID]
        csr_name = csr_details[Constants.NAME]
        turn = csr_details['turn']
        await instance.send_json(
            {"csrInfoJson": {'csr_id': csr_id, 'csr_name': csr_name,'turn':turn}}
        )


    async def add_to_room(self):
        self.room_name = f"room_{self.connection_uuid}"
        logger.info(f"add_to_room :: room_name :: {self.room_name}")

        try:
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name,
            )
        except Exception as e:
            # Handle the exception appropriately
            logger.debug(f"Exception occurred in add_to_room: {e}")
            # Optionally, you can log the error, send an error message, or perform cleanup actions

    async def send_to_room(self, key, value):
        logger.info(f"send_to_room :: room_name ::{self.room_name}")

        try:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'broadcast_message',
                    key: value,
                    'exclude_channel': self.channel_name,
                }
            )
        except Exception as e:
            # Handle the exception appropriately
            logger.debug(f"Exception occurred in send_to_room: {e}")
            # Optionally, you can log the error, send an error message, or perform cleanup actions

    async def discard_from_room(self):
        logger.info(f"discard_from_room :: room_name :: {self.room_name}")
        if self.room_name is not None:
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name,
            )

    """
        When using channel layer's group_send, your consumer has to have a method for every JSON message type you use. 
        In our situation, type is equaled to broadcast_message. Thus, we added a method called broadcast_message.
    """

    async def broadcast_message(self, event):
        exclude_channel = event.get('exclude_channel')
        if self.channel_name != exclude_channel:
            await self.send_json(event)


    async  def send_event(self, message ,status_code):
        event_payload = message
        if status_code is not None:
            event_payload["status_code"] = status_code

        await self.send_json(event_payload)
        
    async def notify_user_message(self, event):
        print(f"event_data :: {event}")
        exclude_channel = event.get('exclude_channel')
        if self.channel_name != exclude_channel:
            send_event_data = {
                Constants.CSR_INFO_JSON: event.get(Constants.CSR_INFO_JSON)
            }
            await self.send_json(send_event_data)

    def get_user_details(self):
        conversation_data = self.redis.get(self.conversation_key)
        conversation_data = json.loads(conversation_data)
        user_details = conversation_data.get('user_details_json', {})
        return user_details