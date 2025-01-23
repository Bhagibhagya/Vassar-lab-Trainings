import json
import uuid
from datetime import datetime
from urllib.parse import unquote

import pytz
from django.utils import timezone
from rest_framework.viewsets import ViewSet
import logging
from channels.layers import get_channel_layer
from ChatBot.utils import get_redis_connection, get_attachments
from django.conf import settings

from ChatBot.constant.constants import Constants
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory

logger = logging.getLogger(__name__)
ist = pytz.timezone('Asia/Kolkata')
azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))


class SendReplyViewSet(ViewSet):
    async def process_event(self, partition_context, events):
        logger.info(f"\nTime profile :: chatbot reply  microservice :: time at consuming  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        for event in events:
            logger.info(f"From chatbot reply  Execution Micro Service Received Reply Event Data :: {event}")
            event_data = event
            conversation_uuid = event_data['conversation_uuid']
            channel_id = event_data['channel_id']
            response = event_data['response']
            intent = event_data.get('intent')
            attachments = event_data.get("attachments")
            sentiment = event_data.get("sentiment")
            regenerate_level = event_data.get("regenerate_level", 0)
            cache = event_data.get("cache", "")
            verification_details = event_data.get("verification_details", "")
            is_knowledge_base = event_data.get("is_knowledge_base", "")
            message_question_id = event_data.get("message_question_id", "")
            message_answer_id = event_data.get("message_answer_id", "")
            dislike = event_data.get("dislike", False)
            answer_uuid = event_data.get("answer_uuid")
            condensed_query = event_data.get("condensed_query")
            question_uuid = event_data.get("question_uuid")
            message_object = await self.create_message_object(response, attachments,regenerate_level,cache,verification_details,is_knowledge_base,message_question_id,dislike,answer_uuid,condensed_query,message_answer_id, question_uuid)

            #logger.info(f"reeeeesponse{response}")

            await self.send_reply(conversation_uuid, channel_id, message_object)

            # After sending the reply, perform other operations asynchronously
            await self.store_conversation_data(conversation_uuid, intent, sentiment, message_object)

    async def send_reply(self, conversation_uuid, channel_id, message_object):
        logger.info(
            f"\nTime profile :: chatbot reply  microservice :: time before getting django channel  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        channel_layer = get_channel_layer()
        logger.info(
            f"\nTime profile :: chatbot reply  microservice :: time after getting django channel  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        attachments = message_object.get("media_url", [])

        reply_data_json = {
            "message": message_object,
            "connection_uuid": conversation_uuid
        }

        absolute_path_attachments = []
        for url_object in attachments:
            new_url_object = {}
            name = url_object.get("name")
            relative_url = url_object.get("url")
            public_url = azure_blob_manager.create_presigned_url(blob_name=unquote(relative_url), expiration=86400)
            new_url_object['name'] = name
            new_url_object['url'] = public_url
            attachment_type = url_object.get("type","")
            if attachment_type == Constants.IMAGE:
                new_url_object['type'] = Constants.IMAGE
                new_url_object['source'] = url_object.get("source")
            elif attachment_type == Constants.VIDEO:
                new_url_object['type'] = Constants.VIDEO
                new_url_object['start_time'] = url_object.get("start_time")
            absolute_path_attachments.append(new_url_object)
        reply_data_json['message']['media_url'] = absolute_path_attachments

        await channel_layer.send(
            channel_id,
            {
                'type': 'chat_message',
                'message': reply_data_json,
            }
        )

        logger.info(f"\nTime profile :: chatbot reply  microservice :: time after send reply back to user:: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        logger.info(f"Sent reply back to user from Chat Service")
    async def store_conversation_data(self, conversation_uuid, intent, sentiment, message_object):
        logger.info(
            f"\nTime profile :: chatbot reply  microservice :: time before getting redis conn  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        redis = get_redis_connection()
        logger.info(
            f"\nTime profile :: chatbot reply  microservice :: time after redis conn  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        conversation_key = f"conversation:{conversation_uuid}"
        conversation_data = redis.get(conversation_key)
        try:
            conversation_data = json.loads(conversation_data)
        except Exception:
            logger.info("The conversation_data is not valid JSON and cannot be parsed.")
            return

        logger.info(
            f"\nTime profile :: chatbot reply  microservice :: time after getting obj from redis  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

        if intent is not None:
            conversation_data = self.update_dimension("Intent", intent, conversation_data)
        if sentiment is not None:
            conversation_data = self.update_dimension("Sentiment", sentiment, conversation_data)

        # last_message = conversation_data["message_details_json"][-1] if conversation_data[
        #     "message_details_json"] else None
        # parent_message_uuid = last_message["id"] if last_message else None
        # message_object["parent_message_uuid"] = parent_message_uuid

        regenerate_level = message_object.get("regenerate_level",0)
        if regenerate_level>0:
            messages = conversation_data["message_details_json"]
            for message in reversed(messages):
                if message.get("id") == message_object["id"]:
                    message.update(message_object)
                    break
            conversation_data["message_details_json"] = messages
        else:
            conversation_data["message_details_json"].append(message_object)

        logger.info(
            f"\nTime profile :: chatbot reply  microservice :: time before setting to redis  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        redis.set(conversation_key, json.dumps(conversation_data))
        logger.info(
            f"\nTime profile :: chatbot reply  microservice :: time after setting to redis  :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

        logger.info(f"\nTime profile :: chatbot reply  microservice :: store_conversation_data\n")

    async def create_message_object(self, response, attachments,regenerate_level,cache,verification_details,is_knowledge_base,message_question_id,dislike,answer_uuid,condensed_query,message_answer_id, question_uuid):
        attachments = get_attachments(attachments)
        message_id = message_answer_id if regenerate_level > 0 and message_answer_id else str(uuid.uuid4())
        reply_data = {
            "id": message_id,
            "csr_id": None,
            "source": "bot",
            "message_marker": "LOGGED",
            "dimension_action_json": {},
            "message_text": response,
            "media_url": attachments,
            "parent_message_uuid": message_question_id,
            "created_at": timezone.now().isoformat(),
            "is_knowledgebase": is_knowledge_base
        }
        if is_knowledge_base:
            reply_data.update({
                "regenerate_level": regenerate_level,
                "cache": cache,
                "verification_details": verification_details,
                "dislike": dislike,
                "answer_uuid": answer_uuid,
                "condensed_query": condensed_query,
                "question_uuid": question_uuid
            })
        return reply_data


    def update_dimension(self, dimension_name, dimension_value, conversation_data):
        logger.info("Inside update_dimension of SendReplyViewSet class")
        # Retrieve the dimensions list from dimension_action_json, initializing if it doesn't exist
        if conversation_data:
            if isinstance(conversation_data, str):
                conversation_data = json.loads(conversation_data)
            message_details_json = conversation_data.get("message_details_json", [])
            last_message_json = message_details_json[-1] if len(message_details_json) > 0 else {}
            if last_message_json:
                dimension_action_json = last_message_json.get("dimension_action_json", {})
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
                last_message_json['dimension_action_json'] = dimension_action_json

                # Assign the updated last_message_json back to message_details_json
                message_details_json[-1] = last_message_json
                conversation_data['message_details_json'] = message_details_json

                # Save the updated conversation_data back to Redis
                # redis.set(conversation_key, json.dumps(conversation_data))
                return conversation_data

            else:
                logger.info(f"there is no message in message_details_json of conversation_data")
                return None

        else:
            logger.info(f"conversation data with conversation_key is not present")
            return None

