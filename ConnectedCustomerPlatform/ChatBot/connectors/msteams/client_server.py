import asyncio
import json
import os
from rest_framework import status
import websockets
import logging
from datetime import datetime, timezone
import uuid
from .adapter import adapter
from botbuilder.core import TurnContext
from django.utils import timezone
from django.db import DatabaseError
from DBServices.models import ChatConfiguration
from channels.db import database_sync_to_async
from ChatBot.utils import get_redis_connection
from .teamsbot import MyBot
from ChatBot.constant.constants import TeamsConstants, Constants
from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.constant.error_messages import ErrorMessages
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)
bot = MyBot()
# Global dictionaries to keep track of active listeners, connections and last_activity
active_listeners = {}
active_connections = {}
last_activity_of_users = {}
user_name={}


def set_active_listener(team_id, listener):
    active_listeners[team_id] = listener


def get_active_listener(team_id):
    return active_listeners.get(team_id)


def set_active_connection(team_id, conn):
    active_connections[team_id] = conn


def get_active_connection(team_id):
    return active_connections.get(team_id)


def update_last_activity_of_user(team_id):
    last_activity_of_users[team_id] = timezone.now()


def get_last_activity_of_user(team_id):
    return last_activity_of_users.get(team_id)


@database_sync_to_async
def get_application_customer_uuid_by_bot_id(bot_id):
    """Retrieve the application and customer UUID from the database using the bot ID."""
    try:
        # Query the database for the chat configuration
        chat_config = ChatConfiguration.objects.filter(chat_details_json__contains={'bot_id': bot_id}).first()

        # Check if a valid chat configuration was found
        if chat_config:
            return chat_config.application_uuid, chat_config.customer_uuid

        # Log and raise an exception if the bot ID was not found
        logging.error(f"Bot ID {bot_id} not found in chat configuration")
        raise CustomException(
            ErrorMessages.BOT_ID_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND
        )

    except DatabaseError as e:
        # Log and raise an exception for database-related errors
        logging.error(f"****Error fetching conversation UUID from database****** {e}")
        raise CustomException(
            ErrorMessages.DATABASE_FETCH_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        # Log and raise a generic exception for other errors
        logging.error(f"****Unexpected error fetching conversation UUID****** {e}")
        raise CustomException(
            ErrorMessages.DATABASE_FETCH_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class WebSocketClient:
    _instance = None

    def __init__(self, *args, **kwargs):
        super()
        self.redis_client = get_redis_connection()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WebSocketClient, cls).__new__(cls, *args, **kwargs)
            # Initialize any resources or tasks
            logging.info("********Inside WebSocketClient Instance********")
        return cls._instance

    async def periodic_cleanup(self):
        logging.info("********inside periodic_cleanup*******")
        while True:
            await asyncio.sleep(TeamsConstants.TIME_OUT_TIME)  # Sleep for 5 minutes (1800 seconds)
            await self.cleanup_inactive_users()

    async def connect(self, uri):
        """Establish a WebSocket connection."""
        try:
            # Attempt to connect to the WebSocket server
            conn = await websockets.connect(uri)
            logging.info(f"****Connected to WebSocket server at {uri}****")
            return conn
        except Exception as e:
            # Log detailed error information
            logging.error(f"********Error connecting to WebSocket server at {uri}: {e}**********")
            # Raise a custom exception with a descriptive message and a suitable HTTP status code
            raise CustomException(ErrorMessages.WEBSOCKET_CONNECTION_FAILED, status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def send_message(self, message, conn, team_id):
        """Send a message over the WebSocket connection."""
        logger.info(f"****send_message :: :: {conn}****")
        try:
            if conn:
                # Parse and prepare the message
                try:
                    message_dict = json.loads(message)
                except json.JSONDecodeError as e:
                    # Handle JSON decoding errors
                    logging.error(f"Error decoding JSON message for team_id {team_id}: {e}")
                    raise CustomException(ErrorMessages.JSON_DECODE_ERROR, status.HTTP_400_BAD_REQUEST)

                message = get_message_json_ms_team(message_dict, team_id)
                message_json = json.dumps(message)

                # Send the message
                await conn.send(message_json)
                logging.info(f"*****Sent message to team_id {team_id} ****** {message_json}")

                # Update last activity
                update_last_activity_of_user(team_id)

                return conn
            else:
                # Raise an exception if the connection is not established
                raise CustomException(ErrorMessages.CONNECTION_NOT_ESTABLISHED, status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other exceptions
            logging.error(f"Error sending message to team_id {team_id}: {e}")
            raise CustomException(ErrorMessages.MESSAGE_SEND_FAILED, status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def listen(self, team_id, conn, activity, auth_header, client,bot_id):
        """Listen for messages on the WebSocket connection and process them."""
        logging.info(f"*****Socket listening started for team_id: {team_id} with conn: {conn}")

        if conn:
            try:
                async for message in conn:
                    update_last_activity_of_user(team_id)
                    logging.debug(f"**********Received New Message**************: {message}")

                    if not message:
                        logging.warning(f"Received empty message for team_id: {team_id}")
                        continue

                    try:
                        response_data = json.loads(message)
                        logging.info(f"response_data: {response_data}")

                        message_type = response_data.get(TeamsConstants.TYPE)
                        result = {}

                        if message_type == "broadcast_message":
                            broadcast_message = response_data.get("message")

                            if broadcast_message:
                                logging.info(f"Broadcast message: {broadcast_message}")
                                result["message_text"] = broadcast_message.get(TeamsConstants.MESSAGE_TEXT)
                                result["specifications"] = {}
                                await send_reply_to_ms_teams(activity, auth_header, result)
                            else:
                                csr_resolved = response_data.get(Constants.NOTIFICATION)
                                if csr_resolved:
                                    logging.info(f"csr_resolved: {csr_resolved}")
                                    await self.delete_conversation_uuid_from_redis(team_id)  # Delete from Redis
                                    await self.cleanup_listeners_and_connections(team_id)
                        else:
                            message_data = response_data.get(TeamsConstants.MESSAGE)
                            csr_data = response_data.get(TeamsConstants.CSR_INFO_JSON)

                            if message_data:
                                conversation_uuid = self.redis_client.get(team_id)
                                logging.debug(f"conversation_uuid: {conversation_uuid}")

                                if conversation_uuid is None:
                                    conversation_uuid = response_data.get("connection_uuid")
                                    if conversation_uuid and team_id:
                                        await self.save_conversation_uuid_to_redis(team_id, conversation_uuid)

                                message_text = message_data.get(TeamsConstants.MESSAGE_TEXT)
                                if message_text.lower()==Constants.END_CONVO:
                                    await self.cleanup_listeners_and_connections(team_id)
                                    # Delete chat configuration from Redis
                                    await self.delete_conversation_uuid_from_redis(team_id)
                                else:
                                    specifications = message_data.get("specifications")
                                    result["message_text"] = message_text
                                    result["specifications"] = specifications
                                    result["bot_id"] = bot_id
                                    logging.info(f"message_text for message: {message_text}")
                                    await send_reply_to_ms_teams(activity, auth_header, result)
                            elif csr_data:
                                turn_number = csr_data.get(TeamsConstants.TURN)
                                logging.info(f"csr queue position: {turn_number}")

                                turn_number_str = f"{turn_number:02d}"
                                queue_info = TeamsConstants.QUEUE_MESSAGE + turn_number_str
                                logging.info(f"queue_number_info for csr: {queue_info}")

                                result["message_text"] = queue_info
                                result["specifications"] = {}
                                message = {"name": user_name.get(team_id, "Unknown")}
                                message_json = json.dumps(message)

                                if conn.open:
                                    await self.send_message(message_json, conn, team_id)
                                else:
                                    logging.error("WebSocket connection is closed, cannot send message.")

                                await send_reply_to_ms_teams(activity, auth_header, result)
                            else:
                                logging.info("Message data or CSR data not found in response.")
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decode error: {e}")
                        raise CustomException(ErrorMessages.JSON_DECODE_ERROR, status.HTTP_400_BAD_REQUEST)
            except websockets.ConnectionClosed as e:
                logging.error(f"Connection closed: {e}")
                raise CustomException(ErrorMessages.CONNECTION_CLOSED, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logging.error(f"Error in WebSocket listening: {e}")
                raise CustomException(ErrorMessages.LISTENING_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                # Clean up active listeners and connections
                await self.cleanup_listeners_and_connections(team_id)
        else:
            logging.error("WebSocket connection is not established")
            raise CustomException(ErrorMessages.CONNECTION_NOT_ESTABLISHED, status.HTTP_400_BAD_REQUEST)

    async def close_connection(self, conn):
        """Close the WebSocket connection."""
        if conn is not None:
            try:
                # Attempt to close the connection
                await conn.close()
                logging.info("**********WebSocket connection closed*********")
            except Exception as e:
                # Log and raise a custom exception if an error occurs
                logging.error(f"*********Error closing WebSocket connection***************: {e}")
                raise CustomException(
                    ErrorMessages.WEBSOCKET_CONNECTION_CLOSE_FAILED,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Log a warning if trying to close a non-existent connection
            logging.warning("******Attempted to close a WebSocket connection that is None******")
            raise CustomException(
                ErrorMessages.CONNECTION_NONE,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def fetch_from_websocket(self, data, team_id, bot_id, activity, auth_header, client):
        """Manages WebSocket communication for a specific team, establishing connections and sending messages."""

        # Retrieve conversation UUID using team_id as the key
        conversation_uuid = self.redis_client.get(team_id)
        logger.info(f"conversation_uuid: {conversation_uuid}")
        try:
            # Retrieve application and customer UUIDs
            application_uuid, customer_uuid = await get_application_customer_uuid_by_bot_id(bot_id)
            logger.info(f"application_uuid: {application_uuid}")
            logger.info(f"customer_uuid: {customer_uuid}")

            # Construct WebSocket URL
            WEBSOCKET_BASE_URL = os.getenv('WEBSOCKET_BASE_URL')
            WEBSOCKET_PROTOCOL = os.getenv('WEBSOCKET_PROTOCOL')
            WEBSOCKET_END_POINT = os.getenv('WEBSOCKET_END_POINT')

            if WEBSOCKET_BASE_URL is None or WEBSOCKET_PROTOCOL is None or WEBSOCKET_END_POINT is None:
                raise CustomException(ErrorMessages.ENV_VARIABLES_NOT_SET, status.HTTP_500_INTERNAL_SERVER_ERROR)

            if conversation_uuid is not None:
                websocket_url = f"{WEBSOCKET_PROTOCOL}{WEBSOCKET_BASE_URL}{WEBSOCKET_END_POINT}?{Constants.CONVERSATION_UUID}={conversation_uuid}&{Constants.APPLICATION_UUID}={application_uuid}&{Constants.CUSTOMER_UUID}={customer_uuid}"

            else:
                websocket_url = f"{WEBSOCKET_PROTOCOL}{WEBSOCKET_BASE_URL}{WEBSOCKET_END_POINT}?{Constants.APPLICATION_UUID}={application_uuid}&{Constants.CUSTOMER_UUID}={customer_uuid}"
            logger.info(f"websocket_url: {websocket_url}")
        # Connect to the WebSocket
            logger.info("Fetching from the WebSocket")
            conn = get_active_connection(team_id)
            logger.info(f"Connection: {conn}")

            if conn is None:
                conn = await client.connect(websocket_url)
                if conn:
                    set_active_connection(team_id, conn)
                listener = get_active_listener(team_id)
                if listener is None:
                    listener_task = asyncio.create_task(client.listen(team_id, conn, activity, auth_header, client,bot_id))
                    set_active_listener(team_id, listener_task)

            # Send a message to the server
            await client.send_message(message=data, conn=conn, team_id=team_id)

        except CustomException as ce:
            logging.error(f"CustomException encountered: {ce.detail}")
            raise  # Re-raise custom exceptions to be handled upstream
        except Exception as e:
            logging.error(f"Error in WebSocket communication: {e}")
            raise CustomException(ErrorMessages.GENERIC_ERROR_MESSAGE, status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def save_conversation_uuid_to_redis(self,team_id, conversation_uuid):
        """Save the conversation_uuid to Redis using team_id as the key."""
        self.redis_client.set(team_id, conversation_uuid)

    async def delete_conversation_uuid_from_redis(self,team_id):
        """Delete the conversation_uuid from Redis using team_id as the key."""
        self.redis_client.delete(team_id)

    async def cleanup_inactive_users(self):
        """Clean up inactive users who have not been active for a specified period."""
        current_time = timezone.now()
        inactive_threshold = current_time - timezone.timedelta(minutes=TeamsConstants.MIN_30)

        # List to keep track of team_ids to be removed
        teams_to_remove = []

        # Identify inactive teams
        for team_id, last_active_time in list(last_activity_of_users.items()):
            if last_active_time < inactive_threshold:
                teams_to_remove.append(team_id)

        # Perform cleanup operations for inactive teams
        for team_id in teams_to_remove:
            try:
                logging.info(f"*****Cleaning up inactive user team_id: {team_id}********")
                await self.cleanup_listeners_and_connections(team_id)

                # Remove from active users
                if team_id in last_activity_of_users:
                    del last_activity_of_users[team_id]

                # Delete chat configuration from Redis
                await self.delete_conversation_uuid_from_redis(team_id)

            except Exception as e:
                logging.error(f"******Error during cleanup for team_id: {team_id} - {e}******")
                raise CustomException(
                    ErrorMessages.INACTIVE_USER_CLEANUP_FAILED,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    async def cleanup_listeners_and_connections(self, team_id):
        """Clean up listeners and connections for a given team_id."""

        # Clean up active listeners
        listener = active_listeners.pop(team_id, None)  # Remove and get the listener, or None if not present
        if listener:
            listener.cancel()
            try:
                await listener  # Ensure any cancellation is completed
                logging.info(f"Listener task for team_id {team_id} was successfully canceled")
            except asyncio.CancelledError:
                logging.info(f"Listener task for team_id {team_id} was successfully canceled")
            except Exception as e:
                logging.error(f"Failed to cancel listener task for team_id {team_id}: {e}")
                raise CustomException(
                    ErrorMessages.LISTENER_CANCEL_FAILED,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Clean up active connections
        conn = active_connections.pop(team_id, None)  # Remove and get the connection, or None if not present
        if conn:
            try:
                await self.close_connection(conn)  # Ensure you await the asynchronous close_connection method
                logging.info(f"Connection for team_id {team_id} was successfully closed")
            except Exception as e:
                logging.error(f"Failed to close connection for team_id {team_id}: {e}")
                raise CustomException(
                    ErrorMessages.WEBSOCKET_CONNECTION_CLOSE_FAILED,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        # remove from the active user
        last_activity_of_users.pop(team_id,None)

def get_message_json_ms_team(response, team_id):
    global user_name
    if not isinstance(response, dict):
        raise TypeError("Expected response to be a dictionary")
    if "name" in response:
        return {"user_info":{
            "name":user_name[team_id]
        }}
    if "text" not in response:
        raise ValueError("Response must contain a 'text' key")
    if team_id not in user_name and "from" in response:
        if "name" in response["from"]:
            user_name[team_id] = response["from"]["name"]

    return {
        "message": json.dumps({
            "id": str(uuid.uuid4()),
            "csr_id": None,
            "source": "user",
            "message_marker": "LOGGED",
            "dimension_action_json": {},
            "message_text": response["text"],
            "media_url": None,
            "parent_message_uuid": None,
            "file_list": [],
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
    }


async def send_reply_to_ms_teams(activity, auth_header, result):
    """Send replies to Microsoft Teams by processing activities through a bot adapter."""

    async def turn_call(turn_context: TurnContext):
        try:
            await bot.on_message_activity(turn_context, result)
        except Exception as e:
            logging.error(f"Error in on_message_activity: {e}")
            raise CustomException(
                ErrorMessages.MESSAGE_ACTIVITY_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def process_activity():
        try:
            await adapter.process_activity(activity, auth_header, turn_call)
            logging.debug("Activity processed successfully")
        except Exception as e:
            logging.error(f"Error processing activity: {e}")
            raise CustomException(
                ErrorMessages.ACTIVITY_PROCESSING_FAILED,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    await process_activity()
