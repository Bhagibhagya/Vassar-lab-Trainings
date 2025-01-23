import hashlib
import logging
import uuid

import redis
import os
from django.conf import settings
import pandas as pd
import jwt
from ChatBot.constant.constants import KnowledgeSourceConstants, EntityConstants, Constants
from urllib.parse import urlparse, unquote
import requests
import validators
from datetime import datetime
from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import Customers, Applications, Entities, CustomerApplicationMapping
from uuid import uuid4
import  json
import base64

from ChatBot.dataclasses.customer_data import CustomerData

from ChatBot.dataclasses.application_data import ApplicationData

from ChatBot.dataclasses.role_data import RoleData

from ChatBot.dataclasses.user_data import UserData
from django.core.cache import cache


from markdownify import markdownify as md

from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager
from ChatBot.dao.impl.customer_application_mapping_dao_impl import CustomerApplicationMappingDaoImpl
from django.conf import settings
from rest_framework import status
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory

azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

logger = logging.getLogger(__name__)
redis_pool = None

azure_service_utils = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)


customer_application_mapping_dao = CustomerApplicationMappingDaoImpl()

def validate_input(data):
    """
    This is the Method to Validate the given data to ensure it is not None, not empty, and not blank.

    Args:
        data: The input data to validate.
        error_message: The error message to return if validation fails.

    Returns:
        True if the data is valid, False otherwise.
    """
    print(data)
    if data is None:
        return False
    elif isinstance(data, str) and (data.strip() == '' or data.strip() == ''):
        return False
    elif isinstance(data, (list, tuple, dict, set)) and not data:
        return False
    else:
        return True


def init_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                                          decode_responses=settings.REDIS_DECODE_RESPONSES)


def get_redis_connection():
    if redis_pool is None:
        init_redis_pool()
    return redis.Redis(connection_pool=redis_pool)


def refactor_history_from_conversation(message_details_json):
    """
    Method to get chat history from conversation

    Parameters:
        message_details_json : list of message objects
    Returns:
        history : list of formatted messages
    """
    logger.info("Inside refactor_history_from_conversation in ChatBot utils.py")
    history = []
    # TODO : Need to move all hardcoded texts in constants.py file
    """
    Response :

        history = 
        [
           {"input": "Hi"},
           {"output": "Hello, what can I help you with today?"},
           {"input": "What is update on Order status"},
           {"output": "fine"}
           .
           .

        ]
    """
    if isinstance(message_details_json, list) and len(message_details_json) > 1:
        # Slice the list to get the last 4 messages only
        recent_messages = message_details_json[-4:]
        for message in recent_messages:
            if isinstance(message, dict):
                if message.get('source') == "bot":  # output
                    history.append({"output": message.get('message_text', '')})
                elif message.get('source') == "user":  # input
                    history.append({"input": message.get('message_text', '')})
    return history


def get_knowledge_source_type(knowledge_source_name):
    _, extension = os.path.splitext(knowledge_source_name)
    return KnowledgeSourceConstants.KNOWLEDGE_SOURCE_TYPE_MAP.get(extension.lower())



def get_user_id_from_jwt_token(token):
    token = token.split(' ')[1]
    try:
        user_info = jwt.decode(token, os.getenv('KEYCLOAK_PUBLIC_RSA'),
                               algorithms=["RS256"], audience='account')
    except Exception:
        payload = token.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        user_info = json.loads(base64.b64decode(payload).decode())
    return user_info['sub']


def get_columns_and_matrix(table):
    if len(table):
        if isinstance(table[0], list):
            table = normailize_rows(table)

            data_frame = pd.DataFrame(table[1:], columns=table[0])
            columns = data_frame.columns.tolist()
            matrix = data_frame.to_numpy().tolist()

            return columns, matrix

        else:

            data_frame = pd.DataFrame(table)
            columns = data_frame.columns.tolist()
            matrix = data_frame.to_numpy().tolist()

            return columns, matrix

    return [], []


def normailize_rows(table):
    if table:
        max_size = max(len(row) for row in table)

        for row in table:
            row_size = len(row)
            row.extend(["" for _ in range(max_size - row_size)])

    return table


def get_knowledge_source_path(application_uuid, customer_uuid, knowledge_source_type, folder_name, channel_type=KnowledgeSourceConstants.KNOWLEDGE_BASE):
    """Generates a structured path for storing knowledge sources based on UUIDs and metadata."""
    year = datetime.now().year
    month = datetime.now().strftime("%B")
    day = datetime.now().strftime("%d")
    knowledge_source_url = f"{str(customer_uuid)}/{str(application_uuid)}/{channel_type}/{year}/{month}/{day}/{knowledge_source_type}/{folder_name}/"
    return knowledge_source_url

def validate_url(url):
    """Validates if the given string is a well-formed URL."""
    return validators.url(url)

def hit_url(url):
    """Checks if the given URL is reachable by sending a HEAD request."""
    try:
        response = requests.head(url)
        return response.ok  # Returns True if the response is successful (2xx)
    except requests.exceptions.RequestException as e:
        # Handle any exception (e.g., DNS failure, timeout, etc.)
        raise CustomException("The server is currently unavailable or the URL cannot be reached. Please check the URL and your network connection.",status.HTTP_503_SERVICE_UNAVAILABLE) from e

def get_base_url(url):
    """Extracts the base URL (scheme and domain) from a full URL."""
    return f"{urlparse(url).scheme}://{urlparse(url).netloc}"


def get_collection_name(customer_uuid, application_uuid):
    application = Applications.objects.filter(application_uuid=application_uuid).first()
    customer = Customers.objects.filter(cust_uuid=customer_uuid).first()
    cam_id = CustomerApplicationMapping.objects.filter(customer=customer, application=application).values_list('customer_application_id', flat=True).first()

    chunk_collection = f"cw_{str(cam_id)}"
    return chunk_collection


def get_cache_collection_name(customer_uuid, application_uuid):
    application = Applications.objects.filter(application_uuid=application_uuid).first()
    customer = Customers.objects.filter(cust_uuid=customer_uuid).first()
    cam_id = CustomerApplicationMapping.objects.filter(customer=customer, application=application).values_list('customer_application_id', flat=True).first()

    cache_collection = f"cw_cache_{str(cam_id)}"
    return cache_collection


def increment_levels(contents):
    breaker = {
        'H1': ['H1'],
        'H2': ['H1', 'H2'],
        'H3': ['H1', 'H2', 'H3']
    }

    for key, value in breaker.items():

        i = 0
        n = len(contents)

        while i < n:
            if contents[i]['type'] != key:
                i += 1
                continue

            for j in range(i + 1, len(contents)):

                if contents[j]['type'] in value:
                    i = j - 1
                    break
                else:
                    contents[j]['level'] = contents[j]['level'] + 1
            i += 1

    return contents


def generate_levels(internal_json):
    blocks = internal_json['blocks']
    metadata = internal_json['metadata']

    contents = []
    for block in blocks:
        if block['content_type'] == 'text':
            contents.append({
                'level': 1,
                'type': block['text']['type']
            })
        else:
            contents.append({
                'level': 1,
                'type': block['content_type']
            })

    contents = increment_levels(contents)

    for i in range(len(contents)):
        blocks[i]['level'] = contents[i]['level']

    internal_json = {
        'blocks': blocks,
        'metadata': metadata
    }

    return internal_json

def get_or_create_default_entity(customer_uuid, application_uuid):
    entity = Entities.objects.filter(entity_name=EntityConstants.DEFAULT_ENTITY_NAME,
                                     application_uuid=application_uuid, customer_uuid=customer_uuid).first()
    if entity:
        return entity
    attribute_details_json = {'entity_name': EntityConstants.DEFAULT_ENTITY_NAME, 'attributes': {
        EntityConstants.DEFAULT_ATTRIBUTE_NAME: {'values':[EntityConstants.DEFAULT_ATTRIBUTE_VALUE],'description':EntityConstants.DEFAULT_ENTITY_DESC}}}
    entity = Entities.objects.create(
            entity_uuid=uuid4(),
            entity_name=EntityConstants.DEFAULT_ENTITY_NAME,
            application_uuid=application_uuid,
            entity_description=EntityConstants.DEFAULT_ENTITY_DESC,
            attribute_details_json=attribute_details_json,
            customer_uuid=customer_uuid
        )
    return entity


def get_attachments(attachments):
    new_attachments = []
    if isinstance(attachments, list):
        for attachment in attachments:
            if isinstance(attachment, dict):
                if "url" in attachment:
                    attachment_data = {
                        "name": attachment.get("name"),
                        "url": attachment.get("url")
                    }
                    attachment_type = attachment.get("type", "")
                    if attachment_type == Constants.IMAGE:
                        attachment_data["type"] = Constants.IMAGE
                        attachment_data["source"] = attachment.get("source")
                    elif attachment_type == Constants.VIDEO:
                        attachment_data["type"] = Constants.VIDEO
                        attachment_data["start_time"] = attachment.get("start_time")
                    new_attachments.append(attachment_data)

    return new_attachments


def build_api_url( url_template: str, **kwargs) -> str:
        logger.info(f"inside bulder_api_url of utils file")
        try:
            logger.info(f"url_template :: {url_template}")
            return url_template.format(**kwargs)
        except KeyError as e:
            error_message = f"Missing required key in URL template: {e}"
            logger.error(error_message)
            raise KeyError(error_message) from e


def create_customer_dataclass_object(customer_uuid, customer_name, email, purchased_plan, primary_contact, secondary_contact, address, billing_address, customer_details_json, status):

   return CustomerData(
        customer_name=customer_name,
        email=email,
        customer_uuid=customer_uuid,
        purchased_plan=purchased_plan,
        primary_contact=primary_contact,
        secondary_contact=secondary_contact,
        address=address,
        billing_address=billing_address,
        customer_details_json=customer_details_json,
        status=status
    )


def create_application_dataclass_object(application_uuid, application_name, application_url, scope_end_point, description, status):
    return ApplicationData(
        application_uuid=application_uuid,
        application_name=application_name,
        application_url=application_url,
        scope_end_point=scope_end_point,
        description=description,
        status=status
    )


def create_role_dataclass_object(role_uuid, role_name, application_uuid, customer_uuid, role_details_json, description, status):
    return RoleData(
        role_uuid=role_uuid,
        role_name=role_name,
        role_details_json=role_details_json,
        application_uuid=application_uuid,
        customer_uuid=customer_uuid,
        description=description,
        status=status
    )


def create_user_dataclass_object(
    user_name,
    user_id,
    first_name,
    last_name,
    email_id,
    mobile_number,
    auth_type,
    user_details_json,
    customer_name,
    customer_id,
    password_hash,
    status):

    return UserData(
        user_name=user_name,
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        email_id=email_id,
        mobile_number=mobile_number,
        auth_type=auth_type,
        user_details_json=user_details_json,
        customer_name=customer_name,
        customer_id=customer_id,
        password_hash=password_hash,
        status=status
    )


def get_customer_application_mapping_id(customer_uuid, application_uuid):
    """
     returns customer application mapping id
    """
    combined_id = str(customer_uuid) + str(application_uuid)
    result = cache.get(combined_id)
    # if combined id's hash in cache return from cache
    if result is not None:
        cam_id = result
    else:
        cam_id = customer_application_mapping_dao.get_customer_application_mapping_id(customer_uuid, application_uuid)
        # set combined id's hash in cache
        cache.set(combined_id, cam_id)

    return cam_id

def get_collection_names(customer_uuid, application_uuid):
    """
     returns collection name based on customer application mapping id
    """
    combined_id = get_customer_application_mapping_id(customer_uuid, application_uuid)
    chunk_collection = f"cw_{combined_id}"
    cache_collection = f"cw_cache_{combined_id}"

    return chunk_collection, cache_collection


def convert_html_to_markdown(text):
    return md(text, heading_style="ATX").strip()

def convert_signed_url_to_blob_name_in_attachments(attachments):
    for i in range(len(attachments)):
        _, blob_name = azure_service_utils.parse_blob_url(
            urlparse(attachments[i]['url'])._replace(query='').geturl())
        attachments[i]['url'] = blob_name
    return attachments


def get_default_entity_file_attributes(attribute_details_json):
    """
    Returns a modified version of 'attribute_details_json', setting each attribute's value to the first item if it is a non-empty list.
    """
    return {
            **attribute_details_json,
            "attributes": {
                k: v["values"] if isinstance(v, dict) and isinstance(v.get("values"), str) 
                else v["values"][0]
                for k, v in attribute_details_json.get("attributes", {}).items()
                if isinstance(v, dict) and "values" in v and (isinstance(v["values"], str) or (isinstance(v["values"], list) and v["values"]))
            }
        } 


def is_valid_uuid(data):
        """
            This is the Method to Validate the given data to ensure it is uuid or not
            Args:
                data: The input data to validate.
            Returns:
                True if the data is valid, False otherwise.
        """

        if isinstance(data, uuid.UUID):
            # If it's already a UUID object, it's valid
            return True
        elif isinstance(data, str):
            try:
                # Try to create a UUID object from the string
                uuid_obj = uuid.UUID(data)
                # Check if the string matches the UUID exactly
                return str(uuid_obj) == data
            except (ValueError, TypeError):
                logger.error(f"{data} should be valida UUID not {type(data)}")
                # If it raises an error, it's not a valid UUID
                return False
        else:
            logger.debug(f"data should be string or UUID to check valid uuid but not {type(data)} type")
            # If the value is neither a UUID object nor a string, it's invalid
            return False


