import logging
import asyncio
import websockets
import json
import re
import  os
import uuid
import requests
import aiohttp
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from channels.db import database_sync_to_async
from urllib.parse import urlencode, unquote
from DBServices.models import ChatConfiguration
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager
from django.conf import settings
import markdown2
import imgkit
import pytz
from bs4 import  BeautifulSoup
from markdownify import markdownify as md
from ChatBot.constant.constants import Constants, AgentDashboardConstants
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory

BOOTSRAP_CDN = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">'
azure_service_utils = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)

azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

ist = pytz.timezone('Asia/Kolkata')
# Global dictionaries to keep track of active listeners, connections and last_activity
active_listeners = {}
active_connections = {}
last_activity_of_users = {}

def set_active_listener(wa_id, listener):
    active_listeners[wa_id] = listener

def get_active_listener(wa_id):
    return active_listeners.get(wa_id)

def set_active_connection(wa_id, conn):
    active_connections[wa_id] = conn

def get_active_connection(wa_id):
    return active_connections.get(wa_id)

def update_last_activity_of_user(wa_id):
    last_activity_of_users[wa_id] = timezone.now()

def get_last_activity_of_user(wa_id):
    return last_activity_of_users.get(wa_id)

def split_message(text):
    messages = []
    while len(text) > Constants.WHATSAPP_MAX_MESSAGE_CHAR_LIMIT:
        split_point = text.rfind(' ', 0, Constants.WHATSAPP_MAX_MESSAGE_CHAR_LIMIT)
        if split_point == -1:  # No space found, fallback to max chars
            split_point = Constants.WHATSAPP_MAX_MESSAGE_CHAR_LIMIT
        messages.append(text[:split_point])
        text = text[split_point:].lstrip()  # Remove leading spaces only
    messages.append(text)  # Append the last part
    return messages

def process_text_for_whatsapp(text):
    conversions = [
        (r'\*\*(.*?)\*\*', r'*\1*'),  # Bold (**text**)
        (r'__(.*?)__', r'*\1*'),  # Bold (__text__)
        # (r'\*(.*?)\*', r'_\1_'),  # Italics (*text*)
        (r'_(.*?)_', r'_\1_'),  # Italics (_text_)
        (r'~~(.*?)~~', r'~\1~'),  # Strikethrough (~~text~~)
        (r'`(.*?)`', r'```\1```'),  # Inline code (`text`)
        (r'^(\t+)-', lambda m: Constants.INVISIBLE_SPACE * len(m.group(1)) + Constants.LIST_DOT), # Replace leading tabs and hyphen with invisible spaces and LIST_DOT
        (r'^(#{1,6})\s*(.*)', lambda m: '*' + m.group(2).strip() + '*'),  # Headers
        (r'\n{2}', '\n'),  # Remove one of two consecutive newlines
    ]
    for pattern, replacement in conversions:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return text

def html_to_markdown(html_content):
    return md(html_content, heading_style="ATX", escape_asterisks=False, escape_underscores=False,escape_misc=False,bullets="-").strip()


def extract_all_tables_from_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # Find all table tags
    tables = soup.find_all('table')

    for table in tables:
        table['class'] = "table table-striped"

    # Return a list of all table tags as strings
    tables = [table for table in tables]
    table_list = []
    for i, table in enumerate(tables):
        new_p = soup.new_tag("p")
        new_p.string = f"Refer to Table {i+1} image below"
        table.replace_with(new_p)
        table_list.append((BOOTSRAP_CDN + str(table), f"Table_{i + 1}"))
    return str(soup), table_list


def table_html_to_image(html_code, file_name):
    imgkit.from_string(html_code, file_name)


def get_table_image_urls(table_list):
    result = []
    for table in table_list:
        table_html,table_name = table
        img_path = str(uuid.uuid4()) + ".png"
        table_html_to_image(table_html,img_path)
        url = azure_blob_manager.upload_data(data=open(img_path,"rb"),file_name="whatsapp/temp/"+img_path)
        container_name, blob_name = azure_service_utils.parse_blob_url(url)
        presigned_url = azure_blob_manager.create_presigned_url(unquote(blob_name))
        os.remove(img_path)
        result.append((presigned_url,table_name))
    return  result


def  extract_tables_from_markdown(markdown_text):
    html_text = markdown2.markdown(markdown_text,extras=['tables'])
    html_text, table_list = extract_all_tables_from_html(html_text)
    table_urls_list = get_table_image_urls(table_list)
    return html_to_markdown(html_text),table_urls_list

def get_template_message(recipient, template_name) :
    """Create a JSON payload for a WhatsApp template message."""
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": Constants.TEMPLATE_LANGUAGE_CODE
                }
        }
    }

def get_text_message_input(recipient, text):
    """Create a JSON payload for a WhatsApp text message."""
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }

def get_image_message_input(recipient, caption, url):
    """Create a JSON payload for a WhatsApp image message."""
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "image",
        "image": {
            "link": url, 
            "caption": caption
        }
    }

async def send_whatsapp_message(data, phone_number_id, whatsapp_business_account_id):
    """Send a message to WhatsApp via the API."""
    access_token = await get_access_token_by_waba_id(whatsapp_business_account_id)
    if access_token:
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_number_id}/messages"
        logging.info(f"******:::::::Graph Api Url :::::::{url}*******")

        # Set a proper timeout for aiohttp
        timeout = aiohttp.ClientTimeout(total=15)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=data, headers=headers) as response:
                    response_data = await response.json()                
                    if not (200 <= response.status < 300):  # Check for any non-2xx status code
                        logging.error(f"***********Response error - Status: {response.status}, Body: {response_data}************")
                        response.raise_for_status()  # Raise an error for non-2xx status codes
                    
                    logging.info(f"*************Message sent successfully to WhatsApp: {response_data}************")
        
        except aiohttp.ClientResponseError as e:
            logging.error(f"**************Client response error - Status: {e.status}, Message: {e.message}***********")
        
        except aiohttp.ClientConnectionError as e:
            logging.error(f"***************Connection error: {e}****************")
        
        except aiohttp.ClientTimeout as e:
            logging.error(f"*********Aiohttp client timeout occurred: {e}***************")
        
        except Exception as e:
            logging.error(f"**********An unexpected error occurred: {e}**************", exc_info=True)
    else:
        logging.error("**********No access token  provided *************")

@database_sync_to_async
def get_conversation_uuid_by_wa_id(wa_id):
    """Retrieve the conversation UUID from the database using the WhatsApp ID."""
    try:
        chat_config = ChatConfiguration.objects.filter(chat_details_json__contains={'wa_id': wa_id}).first()
        if chat_config:
            return chat_config.chat_details_json.get(Constants.CONVERSATION_UUID)
    except Exception as e:
        logging.error(f"****Error fetching conversation UUID****** {e}")
    return None


@database_sync_to_async
def get_application_and_customer_uuid_by_business_and_phone(business_id, phone_number_id):
    """Retrieve application_uuid and customer_uuid from the database using businessId and phoneNumberId."""
    try:
        # Filter the ChatConfiguration by businessId and phoneNumberId in chat_details_json
        chat_config = ChatConfiguration.objects.filter(
            chat_details_json__whatsApp__businessId=business_id,
            chat_details_json__whatsApp__phoneNumberId=phone_number_id
        ).first()

        if chat_config:
            # Return application_uuid and customer_uuid
            return {
                Constants.APPLICATION_UUID: chat_config.application_uuid,
                Constants.CUSTOMER_UUID: chat_config.customer_uuid
            }
    except Exception as e:
        logging.error(f"*****Error fetching application_uuid and customer_uuid****** {e}")
    return None

@database_sync_to_async
def get_access_token_by_waba_id(whatsapp_business_account_id):
    """Retrieve the access token from the database using the WhatsApp Business Account ID i.e waba_id """
    try:
        chat_config = ChatConfiguration.objects.filter(chat_details_json__whatsApp__businessId=whatsapp_business_account_id).first()
        if chat_config:
            result = chat_config.chat_details_json.get('whatsApp')
            if 'apiKey' in result:
                return result['apiKey']
    except Exception as e:
        logging.error(f"*****Error fetching access token ****** {e}")
    return None

@database_sync_to_async
def get_welcome_message_active_template_name_by_waba_id(whatsapp_business_account_id):
    """Retrieve the active template name from the database using the WhatsApp Business Account ID i.e waba_id where 'active': 'true'."""
    try:
        chat_config = ChatConfiguration.objects.filter(chat_details_json__whatsApp__businessId=whatsapp_business_account_id).first()
        if chat_config:
             # Loop through the templates to find the active one
            templates = chat_config.chat_details_json.get('templates', [])
            for template in templates:
                if (template.get('active') == 'true' or template.get('active') == True) and (template.get('templateStatus') == Constants.APPROVED_TEMPLATE_STATUS):
                    # Return the template name for the active template
                    return template.get('templateName')
    except Exception as e:
        logging.error(f"*****Error fetching template name****** {e}")
    return None

@database_sync_to_async
def create_chat_configuration(chat_configuration_name, description, chat_details_json, code, application_uuid, customer_uuid, created_by, updated_by):
    """Create a new chat configuration in the database."""
    new_uuid = str(uuid.uuid4())
    try:
        new_config = ChatConfiguration(
            chat_configuration_uuid=new_uuid,
            chat_configuration_name=chat_configuration_name,
            description=description,
            chat_details_json=chat_details_json,
            code=code,
            application_uuid=application_uuid,
            customer_uuid=customer_uuid,
            insert_ts=timezone.now(),  # or datetime.now() if timezone is not used
            updated_ts=timezone.now(),  # or datetime.now() if timezone is not used
            created_by=created_by,
            updated_by=updated_by
        )
        new_config.save()
        logging.info("******ChatConfiguration created successfully******")
    except Exception as e:
        logging.error(f"******Error saving ChatConfiguration********* {e}")

@database_sync_to_async
def delete_chat_configuration(wa_id):
    """Delete a ChatConfiguration entry from the database by wa_id."""
    try:
        # Find the ChatConfiguration entry where chat_details_json contains the specified wa_id
        entry = ChatConfiguration.objects.filter(chat_details_json__contains={'wa_id': wa_id}).first()
        
        if entry:
            # Delete the found entry
            entry.delete()
            logging.info(f"******ChatConfiguration with wa_id {wa_id} deleted successfully******")
        else:
            logging.info(f"******No ChatConfiguration found with wa_id {wa_id}******")
    except Exception as e:
        logging.error(f"******Error deleting ChatConfiguration with wa_id {wa_id}********* {e}")

async def get_websocket_url(wa_id, whatsapp_business_account_id, phone_number_id):
    conversation_uuid = await get_conversation_uuid_by_wa_id(wa_id)
    result = await get_application_and_customer_uuid_by_business_and_phone(whatsapp_business_account_id, phone_number_id)
    if Constants.APPLICATION_UUID in result and Constants.CUSTOMER_UUID in result:
        base_url = f"{settings.WEBSOCKET_PROTOCOL}{settings.WEBSOCKET_BASE_URL}{settings.WEBSOCKET_END_POINT}"
        application_uuid = result[Constants.APPLICATION_UUID]
        customer_uuid = result[Constants.CUSTOMER_UUID]
        query_params = {
            Constants.APPLICATION_UUID: application_uuid,
            Constants.CUSTOMER_UUID: customer_uuid,
            Constants.CONVERSATION_UUID: conversation_uuid if conversation_uuid else None
        }

        # Construct the full URL
        websocket_url = base_url + '?' + urlencode({k: v for k, v in query_params.items() if v})
        logging.debug(f"********websocket_url::::::::::{websocket_url}::::************")
        return websocket_url

class WebSocketClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WebSocketClient, cls).__new__(cls, *args, **kwargs)
            # Initialize any resources or tasks
            logging.info("********Inside WebSocketClient Instance********")
        return cls._instance

    async def periodic_cleanup(self):
        logging.info("********inside periodic_cleanup*******")
        while True:
            await asyncio.sleep(settings.WHATSAPP_CLEANUP_INTERVAL_SECONDS)
            await self.cleanup_inactive_users()

    async def connect(self, uri):
        """Establish a WebSocket connection."""
        try:
            conn =  await websockets.connect(uri)
            logging.info(f"****Connected to WebSocket server****** {uri}")
            return conn
        except Exception as e:
            logging.error(f"********Error connecting to WebSocket server********** {e}")
            return None

    async def send_message(self, message, conn, wa_id):
        """Send a message over the WebSocket connection."""
        if conn is not None:
            try:
                await conn.send(message)
                logging.info(f"*****Sent message to wa_id {wa_id} ****** {message}")
                update_last_activity_of_user(wa_id)
            except Exception as e:
                logging.error(f"*****Error sending message to wa_id {wa_id} ***** {e}")
        else:
            logging.error("*****WebSocket connection is not established******")
           
    async def send_user_info_json(self, conn, user_name, wa_id):
        message = {
            "user_info": {
            "name": user_name
            }
        }
        message_json = json.dumps(message)
        logging.info(f"*****user message json::{message_json}::*********")
        if conn.open:
            await self.send_message(message_json, conn, wa_id)
        else:
            logging.info("******:::Connection closed while sending user_info json:::*******")

    async def close_connection(self, conn):
        """Close the WebSocket connection."""
        if conn is not None:
            try:
                await conn.close()
                logging.info("**********WebSocket connection closed*********")
            except Exception as e:
                logging.error(f"*********Error closing WebSocket connection***************: {e}")

    async def send_message_to_socket(self, message, wa_id, user_name, phone_number_id, whatsapp_business_account_id):
        """Send a message to the WebSocket and handle listener setup."""        
        try:
            conn = get_active_connection(wa_id)
            if conn is None:
                logging.info(f"\nTime profile :: websocket client :: send_message_to_socket:: time before connect :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                conn = await self.connect(await get_websocket_url(wa_id, whatsapp_business_account_id, phone_number_id))
                logging.info(f"\nTime profile :: websocket client :: send_message_to_socket:: time after connect :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                if conn:
                    set_active_connection(wa_id, conn)

            # Check if a listener is already active for this connection
            listener = get_active_listener(wa_id)
            if listener is None:
                # Start listening for messages in the background
                logging.info(f"\nTime profile :: websocket client :: time before :: send_message_to_socket::  asyncio.create_task :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")           
                listener_task = asyncio.create_task(self.listen(wa_id=wa_id, user_name=user_name, conn=conn, phone_number_id=phone_number_id, whatsapp_business_account_id=whatsapp_business_account_id))
                logging.info(f"\nTime profile :: websocket client :: time after :: send_message_to_socket:: asyncio.create_task :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")           
                if listener_task:
                    set_active_listener(wa_id, listener_task)

            # sending a message                                                                                  
            logging.info(f"\nTime profile :: websocket client :: time before :: send_message_to_socket:: send_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")           
            await self.send_message(message, conn, wa_id)
            logging.info(f"\nTime profile :: websocket client :: time after :: send_message_to_socket::  send_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

        except Exception as e:
            logging.error(f"*****Error in WebSocket communication****** {e}")

    async def listen(self, wa_id, user_name, conn, phone_number_id, whatsapp_business_account_id):
        """Listen for messages on the WebSocket connection and process them."""
        logging.info(f"*****Socket listening started for wa_id: {wa_id} with conn: {conn} *******")
        if conn:
            try:
                await self.send_user_info_json(conn, user_name, wa_id)
                async for message in conn:
                    logging.debug(f"**********Received New Message**************:{message}")
                    if message:
                        response_data = json.loads(message)
                        logging.info(f"\nTime profile :: websocket client :: listen :: time before get_conversation_uuid_by_wa_id :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                        conversation_uuid  = await get_conversation_uuid_by_wa_id(wa_id)
                        logging.info(f"\nTime profile :: websocket client :: listen ::  time after get_conversation_uuid_by_wa_id :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                        logging.debug(f"***********conversation_uuid**********:{conversation_uuid}")

                        if Constants.MESSAGE in response_data:
                            message_data = response_data[Constants.MESSAGE]
                            message_text = message_data.get(Constants.MESSAGE_TEXT)
                            logging.debug(f"***** message_text to send*****: {message_text}::::: ******* to :::::::wa_id:::{wa_id}")
                            if message_text and wa_id:
                                if message_text == "START_CONVO":
                                    logging.info(f"\nTime profile :: websocket client :: listen ::  START_CONVO:: time before get_template_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                                    template_name = await get_welcome_message_active_template_name_by_waba_id(whatsapp_business_account_id)
                                    if template_name:
                                        data = get_template_message(wa_id, template_name)
                                    else:
                                        logging.info("************No active template found with APPROVE status  ************")
                                    logging.info(f"\nTime profile :: websocket client :: listen :: START_CONVO:: time after get_template_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                                    logging.info(f"\nTime profile :: websocket client :: listen :: START_CONVO:: time before send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                                    await send_whatsapp_message(data, phone_number_id, whatsapp_business_account_id)
                                    logging.info(f"\nTime profile :: websocket client :: listen :: START_CONVO:: time after send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                                elif message_text == "END_CONVO":
                                    logging.debug(f"***** message_text*****: {message_text}**********")
                                    logging.info(f"\nTime profile :: websocket client :: listen :: END_CONVO:: time before cleanup_listeners_and_connections :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                                    await self.cleanup_listeners_and_connections(wa_id)
                                    logging.info(f"\nTime profile :: websocket client :: listen :: END_CONVO::  time after cleanup_listeners_and_connections :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                                    # delete chat configuration
                                    logging.info(f"\nTime profile :: websocket client :: listen :: END_CONVO:: time before delete_chat_configuration :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                    await delete_chat_configuration(wa_id)
                                    logging.info(f"\nTime profile :: websocket client :: listen :: END_CONVO:: time after delete_chat_configuration :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")

                                else:
                                    #removing table image references given by LLM for NU
                                    media_list = message_data.get(AgentDashboardConstants.MEDIA_URL,[])
                                    for media_item in media_list:
                                        image_names_list = media_item.get("name")
                                        for image_name in image_names_list:
                                            caption = image_name.replace(".png", "")
                                            if caption in message_text:
                                                ind = message_text.index(caption)
                                                line_start = message_text[:ind].rindex("\n")
                                                line_end = message_text[ind:].index("\n") + ind
                                                message_text = message_text.replace(message_text[line_start:line_end], "")
                                    
                                    logging.info(f"\nTime profile :: websocket client :: listen :: time before extract_tables_from_markdown :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                    message_text, tables = extract_tables_from_markdown(message_text)
                                    logging.info(f"\nTime profile :: websocket client :: listen :: time after extract_tables_from_markdown :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                    logging.info(f"\nTime profile :: websocket client :: listen :: time before split_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                    messages = split_message(message_text)
                                    logging.info(f"\nTime profile :: websocket client :: listen :: time after split_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                    for msg in messages:
                                        logging.info(f"\nTime profile :: websocket client :: listen :: time before process_text_for_whatsapp :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                        processed_message_text = process_text_for_whatsapp(msg)
                                        logging.info(f"\nTime profile :: websocket client :: listen :: time after process_text_for_whatsapp :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                        logging.info(f"\nTime profile :: websocket client :: listen :: time before get_text_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                        data = get_text_message_input(wa_id, processed_message_text)
                                        logging.info(f"\nTime profile :: websocket client :: listen :: time after get_text_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                        logging.debug(f"*****Message Data to send*****: {data}")
                                        logging.info(f"\nTime profile :: websocket client :: listen :: time before send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                        await send_whatsapp_message(data, phone_number_id, whatsapp_business_account_id)
                                        logging.info(f"\nTime profile :: websocket client :: listen :: time after send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                    # send media to the whatsapp
                                    # media_list = message_data.get("media_url")
                                    # for media_item in media_list:
                                    #     caption = media_item.get("name")
                                        # if caption in me
                                        #commenting sending table images from documents for NU as we are sending markdown tables
                                        # url = media_item.get("url")
                                        # if url:
                                        #     data = get_image_message_input(wa_id, caption, url)
                                        #     send_whatsapp_message(data)

                                    #sending Markdown tables
                                    for table in tables:
                                        url, caption = table
                                        if url:
                                            logging.info(f"\nTime profile :: websocket client :: listen :: time before get_image_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                            data = get_image_message_input(wa_id, caption, url)
                                            logging.info(f"\nTime profile :: websocket client :: listen  :: time before get_image_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                            logging.info(f"\nTime profile :: websocket client :: listen ::  time before send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                            await send_whatsapp_message(data, phone_number_id, whatsapp_business_account_id)
                                            logging.info(f"\nTime profile :: websocket client :: listen ::  time before send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                            
                                    #<-- Commented sending media for NU as it is leading to data duplication will have to discuss and make changes in Agent Service >
                                    #< Commented sending media for NU as it is leading to data duplication will have to discuss and make changes in Agent Service >
                                    # send media to the whatsapp 
                                    # media_list = message_data.get(AgentDashboardConstants.MEDIA_URL)
                                    # if media_list is not None:
                                    #     for media_item in media_list:
                                    #         caption = media_item.get("name")
                                    #         url = media_item.get("url")
                                    #         if url:
                                    #             logging.info(f"\nTime profile :: websocket client :: listen ::  SEND IMAGE :: time before get_image_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                    #             data = get_image_message_input(wa_id, caption, url)
                                    #             logging.info(f"\nTime profile :: websocket client :: listen :: SEND IMAGE:: time after get_image_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                    #             logging.info(f"\nTime profile :: websocket client :: listen :: SEND IMAGE:: time before send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                    #             await send_whatsapp_message(data, phone_number_id, whatsapp_business_account_id)
                                    #             logging.info(f"\nTime profile :: websocket client :: listen :: SEND IMAGE:: time before send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                        
                        elif Constants.NOTIFICATION in response_data:
                            await self.cleanup_listeners_and_connections(wa_id)
                            await delete_chat_configuration(wa_id)

                        elif Constants.CSR_INFO_JSON in response_data:
                            csr_data = response_data[Constants.CSR_INFO_JSON]
                            if conn.open:

                                QUEUE_MESSAGE = f"{csr_data.get('name')}, one of our agents will be in touch with you shortly. You are currently in queue position: "
                                turn_number = csr_data.get("turn")

                                # Format message_text as a two-digit string
                                turn_number = f"{turn_number:02d}"
                                logging.info(f"*****csr queue position::{turn_number}::*********")

                                msg = QUEUE_MESSAGE + turn_number
                                logging.info(f"*******queue_number_info for csr::{msg}::::********")

                                logging.info(f"\nTime profile :: websocket client :: listen :: time before process_text_for_whatsapp :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                processed_message_text = process_text_for_whatsapp(msg)
                                logging.info(f"\nTime profile :: websocket client :: listen :: time after process_text_for_whatsapp :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                logging.info(f"\nTime profile :: websocket client :: listen :: time before get_text_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                data = get_text_message_input(wa_id, processed_message_text)
                                logging.info(f"\nTime profile :: websocket client :: listen :: time after get_text_message_input :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                                logging.debug(f"*****Message Data to send*****: {data}")
                                logging.info(f"\nTime profile :: websocket client :: listen :: time before send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                await send_whatsapp_message(data, phone_number_id, whatsapp_business_account_id)
                                logging.info(f"\nTime profile :: websocket client :: listen :: time after send_whatsapp_message :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

                            else:
                                logging.error("******WebSocket connection is closed, cannot send message.*********")

                        if conversation_uuid is None:
                            connection_uuid = response_data.get(Constants.CONNECTION_UUID)
                            result = await get_application_and_customer_uuid_by_business_and_phone(whatsapp_business_account_id, phone_number_id)
                            logging.debug(f"**********connection_uuid**********{connection_uuid}")
                            chat_details_json = {"wa_id": wa_id, "user_name":user_name, "conversation_uuid": connection_uuid}
                            chat_configuration_name="chat_configuration_name"
                            description = "description"
                            code = "code"
                            application_uuid = result.get(Constants.APPLICATION_UUID)
                            customer_uuid = result.get(Constants.CUSTOMER_UUID)
                            created_by = "user"
                            updated_by = "user"

                            logging.debug(f":::application_uuid:::::{application_uuid}")
                            logging.debug(f":::customer_uuid:::::{customer_uuid}")
                            logging.debug(f"::::chat_details_json::::::{chat_details_json}")

                            if connection_uuid and wa_id:
                                logging.info(f"\nTime profile :: websocket client :: listen :: time before create_chat_configuration :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                                await create_chat_configuration(chat_configuration_name, description, chat_details_json, code, application_uuid, customer_uuid, created_by, updated_by)
                                logging.info(f"\nTime profile :: websocket client :: listen :: time after create_chat_configuration :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

            except websockets.ConnectionClosed as e:
                logging.error(f"*****Connection closed*******: {e}")
            finally:
                # Clean up active listeners and connections
                logging.info(f"*****At Finally start cleanup listeners and connections for wa_id {wa_id}********")
                logging.info(f"\nTime profile :: websocket client :: At Finally:: listen :: time before cleanup_listeners_and_connections :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 
                await self.cleanup_listeners_and_connections(wa_id)
                logging.info(f"\nTime profile :: websocket client :: At Finally:: listen :: time after cleanup_listeners_and_connections :: {datetime.now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n") 

        else:
            logging.error("******WebSocket connection is not established********")

    async def cleanup_inactive_users(self):
        current_time = timezone.now()
        inactive_threshold = current_time - timezone.timedelta(minutes=settings.WHATSAPP_INACTIVE_USER_THRESHOLD_MINUTES)
        for wa_id, last_active_time in list(last_activity_of_users.items()):
            if last_active_time < inactive_threshold:
                try:
                    logging.info(f"*****Cleaning up inactive user wa_id: {wa_id}********")
                    await self.cleanup_listeners_and_connections(wa_id)

                    # delete chat configuration 
                    await delete_chat_configuration(wa_id)
                except Exception as e:
                    logging.error(f"******Error during cleanup for wa_id: {wa_id} - {e}******")

    async def cleanup_listeners_and_connections(self, wa_id):

        logging.debug(f"*****Enterd At cleanup_listeners_and_connections for wa_id {wa_id}********")
        # Clean up active listeners
        listener = active_listeners.pop(wa_id, None)  # Remove and get the listener, or None if not present
        if listener:
            listener.cancel()
            try:
                await listener  # Ensure any cancellation is completed
            except asyncio.CancelledError:
                logging.info(f"*********Listener task for wa_id {wa_id} was successfully canceled*********")
            except Exception as e:
                logging.error(f"*********Failed to cancel listener task for wa_id {wa_id}**********: {e}")

        # Clean up active connections
        conn = active_connections.pop(wa_id, None)  # Remove and get the connection, or None if not present
        if conn:
            try:
                await self.close_connection(conn)  # Ensure you await the asynchronous close_connection method
            except Exception as e:
                logging.error(f"**********Failed to close connection for wa_id {wa_id}***********: {e}")

        # Remove from active users
        last_activity_of_users.pop(wa_id, None)
