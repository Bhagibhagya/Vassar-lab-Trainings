import base64
import os
import uuid
from time import time

import dns.resolver

from cryptography.fernet import Fernet
from django.db.models import Q
import imaplib
import logging

from dotenv import load_dotenv

from EmailApp.constant.constants import PaginationParams
from DatabaseApp.models import Customers , Applications
from Platform.constant import constants
from Platform.constant.success_messages import SuccessMessages
from datetime import datetime

from django.core.paginator import Paginator, EmptyPage
from rest_framework import status
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from django.db import connection
from django.conf import settings
from DatabaseApp.models import Applications, Customers
import base64
from Crypto.Cipher import AES
from urllib.parse import unquote
import re

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def validate_input(data):
    """
    This is the Method to Validate the given data to ensure it is not None, not empty, and not blank.

    Args:
        data: The input data to validate.
        error message: The error message to return if validation fails.

    Returns:
        True if the data is valid, False otherwise.
    """
    if data is None:
        return False
    elif isinstance(data, str) and (data.strip() == '' or data.strip() == ''):
        return False
    elif isinstance(data, (list, tuple, dict, set)) and not data:
        return False
    else:
        return True

def is_valid_uuid(value):
    # Check if the value is a string
    if isinstance(value, str):
        try:
            uuid_obj = uuid.UUID(value, version=4)
            return True
        except ValueError:
            return False
    return True



# Function to validate headers are not None
def validate_headers(customer_uuid, application_uuid):
    if not validate_input(customer_uuid):
        raise CustomException(ErrorMessages.CUSTOMER_ID_NOT_NULL)
    if not validate_input(application_uuid):
        raise CustomException(ErrorMessages.APPLICATION_ID_NOT_NULL)

# Function to get customer_uuid, application_uuid and user_id from headers
def get_headers(headers):
    customer_uuid = headers.get(constants.CUSTOMER_UUID)
    application_uuid = headers.get(constants.APPLICATION_UUID)
    user_id = headers.get(constants.USER_ID)

    validate_headers(customer_uuid, application_uuid)
    return customer_uuid, application_uuid, user_id


def validate_customer_and_user_ids(customer_uuid, user_id):
    
    if not validate_input(customer_uuid):
        raise CustomException(ErrorMessages.CUSTOMER_ID_NOT_NULL)
    
    if not validate_input(user_id):
        raise CustomException(ErrorMessages.USER_ID_NOT_NULL)

def get_customer_and_user_ids(headers):
    
    customer_uuid = headers.get(constants.CUSTOMER_UUID)
    user_id = headers.get(constants.USER_ID)
    
    validate_customer_and_user_ids(customer_uuid, user_id)
    return customer_uuid, user_id
    

# Function to get customer_uuid, application_uuid and user_id from headers
def get_headers_and_validate(headers):
    customer_uuid = headers.get(constants.CUSTOMER_UUID)
    application_uuid = headers.get(constants.APPLICATION_UUID)
    user_uuid = headers.get(constants.USER_ID)
    if not validate_input(customer_uuid):
        raise CustomException(ErrorMessages.CUSTOMER_ID_NOT_NULL)
    if not validate_input(application_uuid):
        raise CustomException(ErrorMessages.APPLICATION_ID_NOT_NULL)
    if not is_valid_uuid(customer_uuid):
        raise CustomException("customer_uuid : "+ErrorMessages.NOT_VALID_UUID)
    if not is_valid_uuid(application_uuid):
        raise CustomException("application_uuid : "+ErrorMessages.NOT_VALID_UUID)
    if not is_valid_uuid(user_uuid):
        raise CustomException("user_uuid : "+ErrorMessages.NOT_VALID_UUID)
    return customer_uuid, application_uuid, user_uuid


# Function for preparing a query set based on the values
def get_filter_query_set(request, filter_query):
    if request.headers.get(constants.CUSTOMER_UUID) is not None:
        filter_query &= Q(customer_uuid=request.headers.get(constants.CUSTOMER_UUID))

    if request.headers.get(constants.APPLICATION_UUID) is not None:
        filter_query &= Q(application_uuid=request.headers.get(constants.APPLICATION_UUID))

    return filter_query

# Function to test IMAP connection for given email and password
def test_imap_connection(server_url, port, email, password, use_ssl=True):
    """
    This method is used to test the connection to an IMAP email server.

    Parameters:
        - server_url : The URL of the email server.
        - port : The port number of the email server.
        - email : The email address used for testing the connection.
        - password : The password for the email address.
        - use_ssl : (Optional) Indicates whether to use SSL/TLS. Default is True.

    Returns:
        - result (dict): A dictionary containing the success status and a message.
    """

    try:
        if use_ssl:
            mail = imaplib.IMAP4_SSL(server_url, port)
        else:
            mail = imaplib.IMAP4(server_url, port)

        mail.login(email, password)
        mail.logout()
        return {"success": True, "message": SuccessMessages.CONNECTION_SUCCESS}
    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP connection error: {e}")
        if '[AUTHENTICATIONFAILED]' in str(e):
            return {"success": False, "message": ErrorMessages.INVALID_CREDENTIALS_FOR_IMAP}
        return {"success": False, "message": ErrorMessages.LOGIN_FAILED_FOR_IMAP}
    except Exception as e:
        logger.error(f"General error: {e}")
        return {"success": False, "message": str(e)}

# Function to encrypt password using Fernet Algorithm
def encrypt_password(password):
    if not validate_input(password):
        return password

    fernet = Fernet(settings.ENCRYPTION_SECRET_KEY)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password.decode()

# Function to decrypt password using Fernet Algorithm
def decrypt_password(encrypted_password):
    if not validate_input(encrypted_password):
        return encrypted_password

    fernet = Fernet(settings.ENCRYPTION_SECRET_KEY)
    decrypted_password = fernet.decrypt(encrypted_password.encode())
    return decrypted_password.decode()

# Function to get current timestamp
def get_current_timestamp():
    """Method for getting current timestamp"""
    logger.info("In utils.py :: :: ::  get_current_timestamp")
    # Get the current datetime object
    current_datetime = datetime.now()

    # Convert the datetime object to a Unix timestamp
    timestamp = current_datetime

    # Return the timestamp
    return timestamp

# Function to get email provider from the given email address
def get_email_provider(email):
    try:
        # Extract domain from email
        domain = email.split('@')[1]

        # Fetch MX records for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_hosts = [record.exchange.to_text() for record in mx_records]

        # Analyze MX records to determine the email provider
        for host in mx_hosts:
            if 'google' in host:
                return 'Gmail'
            elif 'outlook' in host or 'office365' in host:
                return 'Outlook'

        return 'Unknown Provider'

    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def paginate_queryset(queryset, params):
    page_number = int(params.get(PaginationParams.PAGE_NUM.value, 1))
    total_entry_per_page = int(params.get(PaginationParams.TOTAL_ENTRY_PER_PAGE.value, 10))

    if total_entry_per_page <= 0:
        raise CustomException(ErrorMessages.TOTAL_ENTRY_PER_PAGE_POSITIVE, status_code=status.HTTP_400_BAD_REQUEST)
    if page_number <= 0:
        raise CustomException(ErrorMessages.PAGE_NUMBER_POSITIVE, status_code=status.HTTP_400_BAD_REQUEST)

    paginator = Paginator(queryset, total_entry_per_page)

    if page_number > paginator.num_pages:
        raise CustomException(ErrorMessages.PAGE_NUMBER_INVALID.format(page_number=page_number), status_code=status.HTTP_400_BAD_REQUEST)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page, paginator

def execute_to_dict(query, params=None):
    with connection.cursor() as c:
        c.execute(query, params or [])
        names = [col[0] for col in c.description]
        return [dict(list(zip(names, values))) for values in c.fetchall()]


def get_customer_application_instances(customer_uuid, application_uuid):
    try:
        customer = Customers.objects.get(cust_uuid=customer_uuid)
        application = Applications.objects.get(application_uuid=application_uuid)
    except Applications.DoesNotExist:
        raise CustomException(ErrorMessages.APPLICATION_NOT_FOUND)
    except Customers.DoesNotExist:
        raise CustomException(ErrorMessages.CUSTOMER_NOT_FOUND)

    return customer, application


def get_current_unix_timestamp():
    """
        Get the current Unix timestamp in milliseconds.

        This function calculates the current Unix timestamp (number of milliseconds
        since January 1, 1970, 00:00:00 UTC) by multiplying the result of `time()`
        from the `time` module by 1000 and rounding it to the nearest integer.

        Returns:
            int: The current Unix timestamp in milliseconds.
    """
    current_timestamp = round(time() * 1000)

    return current_timestamp

def aes_encryption(data):
    """
    Encrypt data using AES encryption with a 32-byte secret key and GCM mode.

    Args:
        data : The data to be encrypted.

    Returns:
        str: A base64-encoded string containing the IV, tag, and encrypted data, separated by "::".
        None: Returns None if an error occurs during encryption.
    """

    try:
        with open(constants.AES_KEY_PATH, "rb") as key:
            pem_data = key.read()
        key_base64 = base64.b64encode(pem_data).decode('utf-8')
        secret_key = key_base64[:32].encode('utf-8')
        iv = os.urandom(12)
        cipher = AES.new(secret_key, AES.MODE_GCM, nonce=iv)
        encrypted_data, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        tag_b64 = base64.b64encode(tag).decode('utf-8')
        encrypted_data_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        return f"{iv_b64}::{tag_b64}::{encrypted_data_b64}"

    except Exception as e:
        logging.error(f"Error encrypting with aes: {e}")
        return None

def aes_decryption(encrypted_data):
    """
    Decrypt AES-encrypted data using a 32-byte secret key and GCM mode.

    Args:
        encrypted_data (str): A base64-encoded string containing the IV, tag, and
                                encrypted data, separated by "::".

    Returns:
        str: The decrypted plaintext data.
        None: Returns None if an error occurs during decryption.
    """

    try:
        with open(constants.AES_KEY_PATH, "rb") as key:
            pem_data = key.read()
        key_base64 = base64.b64encode(pem_data).decode('utf-8')
        iv_b64, tag_b64, encrypted_data_b64 = encrypted_data.split("::")
        iv = base64.b64decode(iv_b64)
        tag = base64.b64decode(tag_b64)
        encrypted_data = base64.b64decode(encrypted_data_b64)
        secret_key = key_base64[:32].encode('utf-8')
        cipher = AES.new(secret_key, AES.MODE_GCM, nonce=iv)
        decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)
        return decrypted_data.decode('utf-8')
    
    except Exception as e:
            logging.error(f"Error encrypting with aes: {e}")
            return None

def parse_blob_url(url):
        """
        Parses the URL to extract the container and blob names.

        :param url: URL of the blob.
        :return: Tuple containing container name and blob name.
        """
        match = re.match(r"https://[^/]+/([^/]+)/(.+)", url)
        if match:
            container_name = match.group(1)
            blob_name = match.group(2)
            blob_name = unquote(blob_name)
            logger.debug(f"container_name:: {container_name}")
            logger.debug(f"blob_name:: {blob_name}")
            return container_name, blob_name
        else:
            raise ValueError("Invalid Blob URL")