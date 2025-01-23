import json
import hashlib
import inspect
import logging
from urllib.parse import unquote

from django.utils import timezone
from rest_framework import status
from dateutil import parser
from datetime import datetime, timedelta
from django.conf import settings

from ChatBot.dao.impl.redis_dao_impl import RedisDaoImpl
from ChatBot.dao.impl.ticket_dao_impl import TicketDaoImpl
from ChatBot.utils import get_redis_connection
from ChatBot.dao.impl.conversations_dao_impl import ConversationsDaoImpl
from ChatBot.constant.constants import Constants, AgentDashboardConstants, CsrConstants, ConversationConstants, \
    UserDetailConstants, MessageConstants, TicketConstants
from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException, CustomException
from ChatBot.constant.error_messages import ErrorMessages
from DatabaseApp.models import Ticket
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager
from ChatBot.services.interface.conversation_service import IConversationService
from rest_framework import status as http_status

from ChatBot.constant.constants import SubDimensionConstants
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory

logger = logging.getLogger(__name__)
class ConversationServiceImpl(IConversationService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConversationServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure __init__ is only called once
        if not hasattr(self, 'initialized'):
            self.redis = get_redis_connection()
            self.ticket_dao = TicketDaoImpl()
            self.conversations_dao_impl = ConversationsDaoImpl()
            self.redis_dao = RedisDaoImpl()
            self.azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))
            self.initialized = True

    def update_conversation_status(self, conversation_uuid, csr_uid, csr_status):
        """
        Update the CSR status in either Redis or DB.

        Args:
            conversation_uuid (str): Unique identifier of the conversation.
            csr_uid (int): Unique identifier of the CSR.
            csr_status (str): New status for the CSR.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        # Try to update in Redis first
        if self._update_csr_status_in_redis(conversation_uuid, csr_uid, csr_status):
            return True

        # If not found in Redis, update in the database
        return self._update_csr_status_in_db(conversation_uuid, csr_uid, csr_status)

    def _update_csr_status_in_redis(self, conversation_uuid, csr_uid, csr_status):
        """
        Update the CSR status in Redis cache.
        """
        conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{conversation_uuid}"
        conversation_data = self.redis.get(conversation_key)

        if conversation_data is not None:
            conversation_data = json.loads(conversation_data)
            csr_info = conversation_data.get(CsrConstants.CSR_INFO_JSON) or []

            csr = next((c for c in csr_info[::-1] if c.get(CsrConstants.CSR_UUID) == csr_uid), None)
            if csr is not None:
                csr[CsrConstants.CSR_STATUS] = csr_status
                conversation_data[CsrConstants.CSR_INFO_JSON] = csr_info
                self.redis.set(conversation_key, json.dumps(conversation_data))
                return True

        return False

    def _update_csr_status_in_db(self, conversation_uuid, csr_uid, csr_status):
        """
        Update the CSR status in the database using ConversationsDAO.
        """
        conversation = self.conversations_dao_impl.get_conversation_by_uuid(conversation_uuid)
        if conversation is None:
            raise ResourceNotFoundException(ErrorMessages.CONVERSATION_UUID_NOT_FOUND,status_code=status.HTTP_400_BAD_REQUEST)

        csr_info = conversation.csr_info_json or []
        csr = next((c for c in csr_info[::-1] if c.get(CsrConstants.CSR_UUID) == csr_uid), None)

        if csr is not None:
            csr[CsrConstants.CSR_STATUS] = csr_status
            self.conversations_dao_impl.update_csr_info(conversation, csr_info)
            return True

        return False


    def get_ongoing_conversations(self, csr_uid):
        """
        Retrieve a list of ongoing conversations for a specific CSR.

        Args:
            csr_uid (str): Unique identifier of the CSR.

        Returns:
            list: A list of ongoing conversations.
        """
        ongoing_conversations = []
        conversation_keys = self.redis.keys(f"{AgentDashboardConstants.CONVERSATION}:*")

        for key in conversation_keys:
            conversation_data = self.redis.get(key)
            if conversation_data is not None:
                conversation_data = json.loads(conversation_data)
                csr_info = conversation_data.get(CsrConstants.CSR_INFO_JSON, []) or []

                # Check if CSR is active in the conversation
                for csr in csr_info:
                    if csr.get(CsrConstants.CSR_UUID) == csr_uid and csr.get(CsrConstants.CSR_STATUS) == AgentDashboardConstants.ACTIVE:
                        user_details = conversation_data.get(UserDetailConstants.USER_DETAILS_JSON, {})
                        message_details = conversation_data.get(MessageConstants.MESSAGE_DETAILS_JSON, [])

                        latest_message = message_details[-1].get(AgentDashboardConstants.MESSAGE_TEXT, "") if message_details else ""
                        created_at = message_details[-1].get(AgentDashboardConstants.CREATED_AT, "") if message_details else ""

                        ongoing_conversations.append({
                            ConversationConstants.CHAT_CONVERSATION_UUID: conversation_data.get(ConversationConstants.CHAT_CONVERSATION_UUID),
                            UserDetailConstants.USER_PROFILE_PICTURE: user_details.get(UserDetailConstants.USER_PROFILE_PICTURE, ""),
                            MessageConstants.LAST_MESSAGE: latest_message,
                            UserDetailConstants.USER_NAME: user_details.get(UserDetailConstants.USER_NAME, Constants.ANONYMOUS),
                            Constants.TIME: created_at
                        })
                        break
        return ongoing_conversations


    def get_conversation_history_details(self, conversation_uuid):
        """
        Retrieve the conversation history details.

        Args:
            conversation_uuid (str): Unique identifier of the conversation.

        Returns:
            list: A list of message details with updated media URLs.
        """
        conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{conversation_uuid}"

        # Try to get data from Redis
        conversation_data = self.redis.get(conversation_key)

        if conversation_data is not None:
            conversation_data = json.loads(conversation_data)
            message_details = self._update_media_urls(conversation_data.get(AgentDashboardConstants.MESSAGE_DETAILS_JSON))
            return message_details

        # If not found in Redis, get from the database
        conversation = self.conversations_dao_impl.get_conversation_by_uuid(conversation_uuid)
        if conversation is None:
            raise ResourceNotFoundException(ErrorMessages.CONVERSATION_UUID_NOT_FOUND, status_code=status.HTTP_400_BAD_REQUEST)

        message_details = self._update_media_urls(conversation.message_details_json)
        return message_details

    def get_conversation_history_by_ticket_uuid(self, ticket_uuid):
        """
        Retrieve the conversation history for a given ticket UUID.
        Args:
            ticket_uuid (str): The unique identifier for the ticket.
        Returns:
            dict: A dictionary containing the conversation history details.
        """
        # Generate the Redis key for the ticket
        ticket_key = TicketConstants.TICKET_KEY.format(ticket_uuid=ticket_uuid)
        logger.info(f"Fetching conversation UUID for ticket key: {ticket_key}")

        # Fetch the conversation UUID from Redis
        conversation_uuid = self.redis_dao.get_data_by_key(key=ticket_key)
        if not conversation_uuid:
            conversation = self.conversations_dao_impl.get_conversation_by_ticket_uuid(ticket_uuid)
            if conversation is not None:
                conversation_uuid = conversation.chat_conversation_uuid
            else:
                raise CustomException(ErrorMessages.CHAT_CONVERSATION_NOT_FOUND, status_code=status.HTTP_400_BAD_REQUEST)

        # Retrieve and return the conversation history details
        logger.info(f"Fetching conversation history for UUID: {conversation_uuid}")
        result = self.get_conversation_history_details(conversation_uuid)
        return result

    def _update_media_urls(self, message_details):
        """
        Update media URLs in the message details with presigned URLs.

        Args:
            message_details (list): List of message details.

        Returns:
            list: Updated message details with presigned media URLs.
        """
        for message_detail in message_details:
            blob_list = message_detail.get(AgentDashboardConstants.MEDIA_URL, [])
            media_url_list = []

            if len(blob_list) > 0:
                for blob in blob_list:
                    url = blob.get(Constants.URL, None)
                    name = blob.get(Constants.NAME, None)
                    attachment_type = blob.get(Constants.TYPE, None)

                    media_object = {
                        Constants.URL: url,
                        Constants.NAME: name,
                        Constants.TYPE: attachment_type
                    }

                    # Add additional properties based on attachment type
                    if attachment_type == Constants.IMAGE:
                        media_object[Constants.SOURCE] = blob.get(Constants.SOURCE, None)
                    elif attachment_type == Constants.VIDEO:
                        media_object[Constants.START_TIME] = blob.get(Constants.START_TIME, None)

                    media_url_list.append(media_object)
                message_detail[AgentDashboardConstants.MEDIA_URL] = media_url_list

        return message_details



    def get_total_conversation_information(self, conversation_uuid):
        """
        Retrieve total conversation information including summary, intents, and sentiment.

        Args:
            conversation_uuid (str): The conversation UUID.

        Returns:
            dict: The conversation information.

        Raises:
            ResourceNotFoundException: If the conversation is not found.
        """
        conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{conversation_uuid}"

        # Try to retrieve from Redis
        conversation_data = self.redis.get(conversation_key)

        if conversation_data is not None:
            conversation_data = json.loads(conversation_data)
            return self._prepare_conversation_summary(conversation_data)

        # Fallback to the database

        conversation = self.conversations_dao_impl.get_conversation_by_uuid(conversation_uuid)
        if conversation is None:
            raise ResourceNotFoundException(ErrorMessages.CONVERSATION_UUID_NOT_FOUND, status_code=status.HTTP_400_BAD_REQUEST)

        # Prepare the conversation summary from the database
        intent, sentiment = self._extract_intents_and_sentiment(conversation.message_details_json)
        csr_transfer_reason = self._get_csr_transfer_reason(conversation.csr_info_json)
        ticket_external_id = self.ticket_dao.get_ticket_external_uuid(conversation.ticket_uuid.ticket_uuid)
        return {
            Constants.INTENT: intent,
            Constants.SENTIMENT: sentiment,
            Constants.TICKET_ID: ticket_external_id,
            Constants.SUMMARY: conversation.summary,
            Constants.USER_DETAILS: conversation.user_details_json,
            CsrConstants.CSR_TRANSFER_REASON: csr_transfer_reason
        }
    def get_total_conversation_information_by_ticket_uuid(self,ticket_uuid):
        """
        Retrieve the total conversation information for a given ticket UUID.

        This method fetches the conversation UUID associated with the ticket UUID
        from Redis and then retrieves the complete conversation information.

        Args:
        ticket_uuid (str): The unique identifier for the ticket.
        """
        ticket_key = TicketConstants.TICKET_KEY.format(ticket_uuid=ticket_uuid)
        logger.info(f"Fetching conversation UUID for ticket key: {ticket_key}")

        # Fetch the conversation UUID from Redis
        conversation_uuid = self.redis_dao.get_data_by_key(key=ticket_key)
        if not conversation_uuid:
            conversation = self.conversations_dao_impl.get_conversation_by_ticket_uuid(ticket_uuid)
            if conversation is not None:
                conversation_uuid = conversation.chat_conversation_uuid
            else:
                raise CustomException(ErrorMessages.CHAT_CONVERSATION_NOT_FOUND, status_code=status.HTTP_400_BAD_REQUEST)


        result = self.get_total_conversation_information(conversation_uuid)
        return result
    def _prepare_conversation_summary(self, conversation_data):
        """
        Prepare the summary of a conversation.

        Args:
            conversation_data (dict): The conversation data.

        Returns:
            dict: The conversation summary including intents, sentiment, ticket ID, and other information.
        """
        conversation_uuid = conversation_data[ConversationConstants.CHAT_CONVERSATION_UUID]
        user_details = conversation_data[UserDetailConstants.USER_DETAILS_JSON]
        message_details_json = conversation_data.get(MessageConstants.MESSAGE_DETAILS_JSON, [])
        csr_info_json = conversation_data.get(CsrConstants.CSR_INFO_JSON,[])
        intent, sentiment = self._extract_intents_and_sentiment(message_details_json)
        csr_transfer_reason = self._get_csr_transfer_reason(csr_info_json)
        ticket_external_id = self.ticket_dao.get_ticket_external_uuid(conversation_data.get("ticket_uuid"))
        chat_summary = conversation_data.get(AgentDashboardConstants.SUMMARY, "")

        return {
            Constants.INTENT: intent,
            Constants.SENTIMENT: sentiment,
            Constants.TICKET_ID: ticket_external_id,
            Constants.SUMMARY: chat_summary,
            Constants.USER_DETAILS: user_details,
            CsrConstants.CSR_TRANSFER_REASON: csr_transfer_reason
        }

    def _extract_intents_and_sentiment(self, message_details_json):
        """
        Extract intents and sentiment from message details.

        Args:
            message_details_json (list): List of message details from conversation data.

        Returns:
            tuple: A tuple containing a list of intents and the sentiment.
        """
        intent_structure = {}
        sentiment_list = []

        for message in message_details_json:
            dimension_action_json = message.get(MessageConstants.DIMENSION_ACTION_JSON, {})
            source = message.get(MessageConstants.SOURCE, None)
            dimensions = dimension_action_json.get(MessageConstants.DIMENSIONS, [])
            for dimension in dimensions:
                if dimension.get(Constants.DIMENSION) == Constants.INTENT:
                    intent_name = dimension.get(Constants.VALUE)
                    # Extract sub-intent details if available
                    sub_dimensions = dimension.get(SubDimensionConstants.SUB_DIMENSIONS, {})
                    if sub_dimensions and sub_dimensions.get(
                            SubDimensionConstants.SUB_DIMENSION) == SubDimensionConstants.DIMENSION_SUB_INTENT:
                        sub_intent_name = sub_dimensions.get(Constants.VALUE)
                    else:
                        sub_intent_name = None

                    # Build intent structure
                    intent_structure = {
                        "name": intent_name
                    }
                    if sub_intent_name is not None:
                        intent_structure[SubDimensionConstants.DIMENSION_SUB_INTENT] = {
                            "name": sub_intent_name
                        }

                elif source == Constants.USER and dimension.get(Constants.DIMENSION) == Constants.SENTIMENT:
                    sentiment_list.append(dimension.get(Constants.VALUE))
        # Determine sentiment
        if sentiment_list:
            sentiment = sentiment_list[AgentDashboardConstants.MESSAGE_INDEX] if len(sentiment_list) > 1 else \
                sentiment_list[0]
        else:
            sentiment = None

        return intent_structure, sentiment


    def process_conversations(self):
        """
        Process conversations to check if any have exceeded the threshold and need to be saved.
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.info("ConversationServiceImpl :: process_conversations() started")
        conversation_keys = self.redis.keys(f"{AgentDashboardConstants.CONVERSATION}:*")
        if not conversation_keys:
            logger.info("No conversation data to process")
            return

        now = parser.isoparse(timezone.now().isoformat())
        conversation_keys_data = self.redis.mget(conversation_keys)

        for conversation_data in conversation_keys_data:
            if conversation_data is not None:
                conversation_data = json.loads(conversation_data)
                message_details = conversation_data.get(Constants.MESSAGE_DETAILS_JSON, [])
                if not message_details:  # This handles both None and empty list
                    print("message is empty:::")
                    inserted_ts = conversation_data.get('inserted_ts')
                    if inserted_ts:
                        created_at = parser.isoparse(inserted_ts)
                        logger.info(
                            f"No message details found. Using inserted_ts for conversation_uuid: {conversation_data.get('chat_conversation_uuid')}")
                    else:
                        logger.error(
                            f"Inserted timestamp is missing for conversation_uuid: {conversation_data.get('chat_conversation_uuid')}")
                        continue  # Skip processing this conversation
                else:
                    created_at = self.get_latest_message_time(message_details)
                if self.is_threshold_exceeded(created_at, now):
                    self.save_conversation_to_db_and_remove_from_redis(conversation_data)

    def get_latest_message_time(self, message_details):
        """
        Get the creation time of the latest message in the conversation.
        :param message_details: List of message details
        :return: Datetime of the latest message or None
        """
        if message_details:
            latest_message = message_details[-1]
            created_at_str = latest_message['created_at']
            return parser.isoparse(created_at_str)
        return None

    def is_threshold_exceeded(self, created_at, now):
        """
        Check if the message creation time has exceeded the defined threshold.
        :param created_at: Datetime of the latest message
        :param now: Current datetime
        :return: Boolean whether the threshold is exceeded
        """
        threshold = timedelta(minutes=Constants.CACHE_THRESHOLD)
        # Ensure created_at is timezone-aware (in UTC)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        # Now ensures now is timezone-aware (in UTC)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return created_at and now - created_at > threshold

    def save_conversation_to_db_and_remove_from_redis(self, conversation_data):
        """
        Saves the conversation data to the database and removes it from Redis after successful saving.
        """

        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        try:
            # Saving the conversation to the database
            self.conversations_dao_impl.save_conversation(conversation_data)

            # deleting the conversation to the redis
            chat_conversation_uuid=conversation_data.get(Constants.CHAT_CONVERSATION_UUID)
            conversation_key = f"{AgentDashboardConstants.CONVERSATION}:{chat_conversation_uuid}"
            self.redis.delete(conversation_key)

        except Exception as e:
            logger.error(f"Error saving conversation to DB or deleting key: {str(e)}")


    def _get_csr_transfer_reason(self, csr_info_json):
        """
        Extracts the `csr_transfer_reason` from the last CSR entry in the `csr_info_json` array.

        Parameters:
            - csr_info_json (list): List of CSR details containing dictionaries.

        Returns:
            - str: The transfer reason of the last CSR if available; otherwise, returns None.
        """
        if not csr_info_json or not isinstance(csr_info_json, list):
            logger.warning("Invalid or empty `csr_info_json` provided.")
            return None

        # Get the last CSR entry
        last_csr_entry = csr_info_json[-1]

        # Extract the transfer reason if present
        csr_transfer_reason = last_csr_entry.get(CsrConstants.CSR_TRANSFER_REASON)
        logger.debug(f"Extracted csr_transfer_reason: {csr_transfer_reason}")

        return csr_transfer_reason


    # def get_active_conversation(self, application_uuid, customer_uuid, active_list,user_uuid, start_date, end_date):
    #     """
    #             Method to fetch active conversations in organization application
    #             Parameters:
    #                     application_uuid (str) : uuid of application
    #                     customer_uuid (str)    : uuid of customer
    #                     active_list (list)     : list of "CSR_ONGOING" keywords
    #                     user_uuid(str)         : uuid of csr
    #                     start_date (date)      : datetime field
    #                     end_date (date)        : datetime field
    #             Returns :
    #                     List of UnifiedActivity objects
    #     """
    #     logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
    #     logger.debug(f"application_uuid :: {application_uuid}  and customer_uuid :: {customer_uuid}")
    #     logger.debug(f"active_list :: {active_list}")
    #     conversation_keys = self.redis.keys(ConversationConstants.CONVERSATION_PATTERN)
    #     total_conversation_data = self.redis.mget(conversation_keys)
    #     unified_activity_data_list = []
    #     for data in total_conversation_data:
    #             if not data:
    #                 continue
    #             if isinstance(data, str):
    #                 try:
    #                     conversation_data = json.loads(data)
    #                 except json.JSONDecodeError as e:
    #                     logger.error(f"Error parsing JSON for conversation_data :: {data}")
    #                     raise CustomException("The conversation_data is not valid JSON and cannot be parsed.", status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
    #             elif isinstance(data, dict):
    #                 conversation_data = data
    #             else:
    #                 conversation_data = {}
    #             # check if conversation_data is empty or not
    #             if conversation_data:
    #                 user_details_data = conversation_data.get(UserDetailConstants.USER_DETAILS_JSON, {}) or {}
    #                 user_name = user_details_data.get(UserDetailConstants.USER_NAME) or Constants.ANONYMOUS
    #                 csr_details_data = conversation_data.get(CsrConstants.CSR_INFO_JSON,{}) or {}
    #                 if csr_details_data:
    #                     # Check if the list is not empty
    #                     last_csr = csr_details_data[-1]  # Get the last dictionary in the list
    #                     csr_uuid = last_csr.get(CsrConstants.CSR_UUID, None)
    #                 else:
    #                     csr_uuid = None
    #                 inserted_ts = conversation_data.get(ConversationConstants.INSERTED_TS)
    #                 # Convert start_date and end_date to datetime objects
    #                 # start_date_dt = datetime.strptime(start_date, "%m/%d/%Y")
    #                 # end_date_dt = datetime.strptime(end_date, "%m/%d/%Y")
    #                 # Ensure inserted_ts is a datetime object
    #                 if isinstance(inserted_ts, str):
    #                     # Convert inserted_ts to a datetime object
    #                     inserted_ts = datetime.fromisoformat(inserted_ts)
    #                 # finding last user message intent
    #                 intent = self._find_latest_message_intent(conversation_data=conversation_data)
    #                 if conversation_data.get(Constants.APPLICATION_UUID) == application_uuid and conversation_data.get(Constants.CUSTOMER_UUID) == customer_uuid and (conversation_data.get(ConversationConstants.CONVERSATION_STATUS) in active_list) and csr_uuid == user_uuid and start_date <= inserted_ts <= end_date:
    #                     unified_activity_data_list.append(
    #                                 UnifiedActivity(
    #                                     activity_uuid=conversation_data.get(ConversationConstants.CHAT_CONVERSATION_UUID),
    #                                     status=conversation_data.get(ConversationConstants.CONVERSATION_STATUS),
    #                                     timestamp=conversation_data.get(ConversationConstants.INSERTED_TS),
    #                                     client_name=user_name,
    #                                     email_id=None,
    #                                     intent=intent,
    #                                     channel=Constants.CHAT,
    #                                     application_uuid=application_uuid,
    #                                     customer_uuid=customer_uuid,
    #                                     assigned_to = user_uuid
    #                                 )
    #                     )
    #     # sort conversations
    #     unified_activity_data_list.sort(key=lambda x: x.timestamp if isinstance(x.timestamp, datetime) else datetime.fromisoformat(x.timestamp), reverse=True)
    #     logger.info(f"get_active_conversation :: active conversation data :: {unified_activity_data_list}")
    #     return unified_activity_data_list

    # def _find_latest_message_intent(self, conversation_data):
    #     """method to find latest user message intent"""
    #     intent = None
    #     message_details_json = conversation_data.get(MessageConstants.MESSAGE_DETAILS_JSON) or []
    #     for single_message in reversed(message_details_json):
    #         if single_message.get(MessageConstants.SOURCE) == Constants.USER:
    #             dimension_action_json = single_message.get(MessageConstants.DIMENSION_ACTION_JSON) or {}
    #             dimensions = dimension_action_json.get(MessageConstants.DIMENSIONS) or []
    #             for single_dimension in dimensions:
    #                 if single_dimension.get(MessageConstants.DIMENSION) is not None and single_dimension.get(MessageConstants.DIMENSION).lower() == Constants.INTENT.lower():
    #                     intent = single_dimension.get(MessageConstants.VALUE)
    #                     break
    #             break
    #     return intent

