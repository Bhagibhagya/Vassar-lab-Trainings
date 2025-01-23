from datetime import datetime, timezone
import inspect
import json
from zipfile import BadZipFile
from azure.core.exceptions import ResourceNotFoundError
from msal import ConfidentialClientApplication
from openpyxl.styles import Font, PatternFill

from AIServices.BOT.LLMChain import LLMChain
from AIServices.prompts import EMAIL_CONVERSATION_SUMMARY_PROMPT
import pycountry
import us
from requests import Response

from DatabaseApp.models import EmailInfoDetail
from EmailApp.dao.impl.prompt_dao_impl import PromptDaoImpl
from EventHub.send_sync import EventHubProducerSync

import re
from typing import List, Any, Dict, Optional

from ConnectedCustomerPlatform.azure_key_vault_utils import KeyVaultService
from Platform.dao.impl.redis_dao_impl import RedisDaoImpl
from .DataClasses.response.email_info_data import EmailInfo, EmailRecipient

from .constant.error_messages import AzureBlobErrorMessages, ErrorMessages, PersonalizationErrorMessages

from .constant.constants import EMAIL_ADDRESS_PATTERN, BlobConstants, DateFormats, FWD_SENDER_NAME_REGEX, \
    FWD_MAILTO_REGEX, INVENTORY_FILEPATH, PromptCategory, RegexTypes, CsrChromaDbFields, ChannelTypes, \
    DefaultResponsesTemplate, Role_names, Configure,OutlookUrlsEndPoints, MicrosoftSecretDetailsKeys, \
    CODE_FOR_AUTHENTICATION_ERROR_GRAPH_API, ChromaParams, ChromadbMetaDataParams, CategeriesForPersonalization

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException
from datetime import datetime
from .constant.constants import EmailTaskStatus, EmailActionFlowStatus
from datetime import datetime
from email.utils import formatdate
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from django.db import transaction
from django.db.models import Q as QuerySet
from EmailApp.constant.constants import (
    TimelineTypes,
)
from EmailApp.constant import constants
from django.conf import settings
import pandas as pd
from guardrails.hub import ToxicLanguage, ProfanityFree
from guardrails import Guard
from ConnectedCustomerPlatform.exceptions import CustomException
from magic_profanity import ProfanityFilter
import requests
from EmailApp.DataClasses.response.prompt_dimension_details import PromptDimensionDetails
import subprocess
import os
from ConnectedCustomerPlatform.responses import CustomResponse
from rest_framework import status
from EmailApp.constant.constants import ATTACHMENTS_FOLDER_PATH
from azure.storage.blob import BlobServiceClient
from urllib.parse import urlparse
import hashlib
from django.conf import settings

from AIServices.LLM.llm import llm
from EmailApp.dao.impl.usermgmt_user_details_view_dao_impl import UsersDetailsViewDaoImpl
from .dao.impl.dimension_dao_impl import DimensionDaoImpl

from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


logger = logging.getLogger(__name__)

import inspect

import pytz


def convert_to_utc(datetime_obj):
    # Set the timezone to UTC
    utc_timezone = pytz.timezone('UTC')
    # Localize the datetime object to the UTC timezone
    return utc_timezone.localize(datetime_obj)

#TODO Move this Datetimeutils
#Validate start and end date (startdate,enddate,format)
#ValidateDate(date,format)
def validate_start_and_end_date(start_date, end_date):
    """
    This method is used for validating start and end date with Date format MM/dd/yyyy.

    """
    if not validate_date_format(start_date, DateFormats.MM_DD_YYYY.value):
        raise InvalidValueProvidedException(
            detail=ErrorMessages.INVALID_DATE_FORMAT.format(start_date, DateFormats.MM_DD_YYYY.value))

    if not validate_date_format(end_date, DateFormats.MM_DD_YYYY.value):
        raise InvalidValueProvidedException(
            detail=ErrorMessages.INVALID_DATE_FORMAT.format(start_date, DateFormats.MM_DD_YYYY.value))

    # Convert date strings to datetime objects
    start_date_obj = datetime.strptime(start_date, constants.DateFormats.MM_DD_YYYY.value)
    end_date_obj = datetime.strptime(end_date, constants.DateFormats.MM_DD_YYYY.value)
    #Todo no need to convert to utc again
    start_date_utc = convert_to_utc(start_date_obj)
    end_date_utc = convert_to_utc(end_date_obj)
    end_date_utc_ext = end_date_utc.replace(hour=23, minute=59, second=59)

    logger.debug(f"Start date (UTC): {start_date_utc}, End date (UTC extended): {end_date_utc_ext}")

    # Check if start date is greater than end date
    if start_date_utc > end_date_utc:
        raise InvalidValueProvidedException(detail=ErrorMessages.START_DATE_GREATER_THAN_END_DATE)

    logger.debug(start_date_utc.timestamp())
    logger.debug(end_date_utc_ext.timestamp())
    return start_date_utc, end_date_utc_ext


# utils.py

from datetime import datetime


def make_offset_naive(dt):
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def get_email_statistics(customer_list, start_date, end_date, customer_client_id=None, customer_name=None,
                         geography=None, customer_tier=None):
    """
    Calculate aggregate email statistics based on the provided criteria.

    Args:
        customer_list (list): List of customer dictionaries.
        start_date (int): Start date timestamp for filtering.
        end_date (int): End date timestamp for filtering.
        customer_client_id (str, optional): Customer client UUID for filtering. Defaults to None.
        search_criteria (str, optional): Search criteria. Defaults to None.
        search_value (str, optional): Search value. Defaults to None.

    Returns:
        dict: Dictionary containing the aggregate email statistics.
    """
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    # Initialize email statistics
    email_statistics = {
        "total_emails_received": 0,
        "ai_resolved": 0,
        "ai_assisted": 0,
        "manually_resolved": 0,
        "need_assistance": 0
    }
    customer_name = normalize_list_params(customer_name)
    geography = normalize_list_params(geography)
    customer_tier = normalize_list_params(customer_tier)

    # Iterate over customer list
    for customer in customer_list:
        start_date = make_offset_naive(start_date)
        end_date = make_offset_naive(end_date)

        customer_inserted_ts = customer['inserted_ts']
        customer_inserted_ts = make_offset_naive(customer_inserted_ts)

        # Check if the customer falls within the date range
        if (not customer_name or customer['customerName'] in customer_name) and \
                (not geography or customer['geography'] in geography) and \
                (not customer_tier or customer['customerTier'] in customer_tier) and \
                (not customer_client_id or customer['customer_client_uuid'] == customer_client_id):
            # Aggregate email statistics
            email_statistics["total_emails_received"] += customer['emailStatistics']['total_emails_received']
            email_statistics["ai_resolved"] += customer['emailStatistics']['ai_resolved']
            email_statistics["ai_assisted"] += customer['emailStatistics']['ai_assisted']
            email_statistics["manually_resolved"] += customer['emailStatistics']['manually_resolved']
            email_statistics["need_assistance"] += customer['emailStatistics']['need_assistance']
    return email_statistics


def get_email_statistics_by_customer_client(emails_list: list, sender_name=None, email_id=None, intent=None,
                                            status=None):
    """
    Calculate aggregate email statistics based on the provided criteria for each customer client.

    Args:
        customer_client_uuid_list (list): List of dictionaries containing customer client UUIDs and other attributes.
        start_date (int): Start date timestamp for filtering.
        end_date (int): End date timestamp for filtering.
        sender_name (list, optional): List of sender names for filtering. Defaults to None.
        email_id (list, optional): List of email IDs for filtering. Defaults to None.
        intent (list, optional): List of intents for filtering. Defaults to None.
        status (list, optional): List of statuses for filtering. Defaults to None.

    Returns:
        dict: Dictionary containing the aggregate email statistics for each customer client.
    """
    logger.info(f" In {inspect.currentframe().f_code.co_name}")

    # Initialize email statistics
    email_statistics = {
        "total_emails_received": 0,
        "ai_resolved": 0,
        "ai_assisted": 0,
        "manually_resolved": 0,
        "need_assistance": 0
    }
    sender_name = normalize_list_params(sender_name)
    email_id = normalize_list_params(email_id)
    intent = normalize_list_params(intent)
    status = normalize_list_params(status)

    # Iterate over customer client UUID list
    for client_data in emails_list:
        # Check if the client data falls within the date range and matches the filtering criteria
        if (not sender_name or client_data['sender_name'] in sender_name) and \
                (not email_id or client_data['email_id'] in email_id) and \
                (not intent or client_data['intent'] in intent) and \
                (not status or client_data['status'] in status):
            # Aggregate email statistics
            email_statistics["ai_resolved"] += 1 if client_data['status'] == 'ai_resolved' else 0
            email_statistics["ai_assisted"] += 1 if client_data['status'] == 'ai_assisted' else 0
            email_statistics["manually_resolved"] += 1 if client_data['status'] == 'manually_resolved' else 0
            email_statistics["need_assistance"] += 1 if client_data['status'] == 'need_assistance' else 0

    # Calculate the total number of emails received
    email_statistics["total_emails_received"] = email_statistics["ai_resolved"] + email_statistics["ai_assisted"] + \
                                                email_statistics["manually_resolved"] + email_statistics[
                                                    "need_assistance"]

    return email_statistics



def validate_input(data):
    """
    This is the Method to Validate the given data to ensure it is not None, not empty, and not blank.

    Args:
        data: The input data to validate.
        error_message: The error message to return if validation fails.

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


def validate_date_format(date_string, dateformat='%m/%d/%Y'):
    """
    Validate the date format as MM/dd/yyyy.

    Args:
        date_string: The date string to validate.

    Returns:
        True if the date is in the MM/dd/yyyy format, False otherwise.
    """
    try:
        datetime.strptime(date_string, dateformat)
        return True
    except ValueError:
        return False


import uuid


def generate_message_id(domain="vassarlabs.com"):
    """
    Generates a message ID for an email with the specified domain.

    Args:
        domain (str): The domain to use in the message ID. Default is "vassarlabs.com".

    Returns:
        str: The generated message ID.
    """
    unique_id = uuid.uuid4()
    message_id = f"<{unique_id}@{domain}>"
    return message_id


def get_current_timestamp():
    "Method for getting current timestamp"
    # Get the current datetime object
    current_datetime = datetime.now()

    # Convert the datetime object to a Unix timestamp
    timestamp = current_datetime

    # Return the timestamp
    return timestamp


def parse_date(date_string):
    if date_string is None:
        return None

    # Remove the timezone abbreviation if present
    date_string = date_string.split(" (")[0]

    formats = [
        '%a, %d %b %Y %H:%M:%S %z',  # Wed, 27 Mar 2024 01:37:39 -0700
        '%a, %d %b %Y %H:%M:%S %Z',  # Thu, 28 Mar 2024 07:59:10 GMT
        '%a, %d %b %Y %H:%M:%S',  # Mon, 1 Apr 2024 12:35:24 +0530
        '%a, %d %b %Y %H:%M:%S +%f',  # Wed, 3 Apr 2024 12:52:38 +0530
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.utc)
            return dt
        except ValueError as e:
            logger.info(f"parse_date :: {e}")
            return None
    return None


def get_timestamp_from_date(date):
    "method to convert a date to a timestamp "
    timestamp = parse_date(date)

    if timestamp is not None:
        utc_timezone = pytz.timezone('UTC')
        utc_time = timestamp.astimezone(utc_timezone)
        return utc_time
    else:
        logger.debug("Error while passing date")
        return None


def get_current_date_str():
    # Get the current date string in the desired format
    date_str = formatdate(localtime=True)

    # Return the date string
    return date_str


# TODO :: Need to save the email data to azure and DB before sending or replying to mail

def authenticate_smtp_credentials(smtp_server, smtp_port, user_name, password):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    try:
        # Log in to the SMTP server
        smtp_server = smtplib.SMTP(smtp_server, smtp_port)
    except Exception as e:
        logger.error(f"smtp server details are Invalid : {e}", exc_info=True)
        return None

    try:
        smtp_server.starttls()
        logger.debug("Logging in...")
        smtp_server.login(user_name, password)
        logger.debug("Logged in successfully...")
        return smtp_server

    except Exception as e:
        logger.error(f"user credentials for smtp server are Invalid: {e}", exc_info=True)
        return None

def send_or_reply_email(email_info, smtp_server, message_id, sender_email, email_to, subject=None, email_body=None, cc_emails=None,
                        bcc_emails=None, attachments=None, in_reply_to=None, date=None):
    #TODO reduce complexity
    """
    This method replies to an email with attachments or sends a new email if message_id is None.

    :param smtp_server: SMTP server object
    :param sender_email: Sender's email address
    :param email_body: Body of the email
    :param cc_emails: List of CC email addresses
    :param bcc_emails: List of BCC email addresses
    :param attachments: List of attachment file paths
    :param in_reply_to: Message-ID of the email being replied to
    :param date: Date and time of the email
    """

    logger.debug("Sending or replying to email.....")
    logger.info("In send_or_reply_email method")
    if subject is None:
        subject = email_info.email_subject

    # Create the MIME object for the email
    msg = MIMEMultipart()
    msg['Message-ID'] = message_id
    msg['From'] = sender_email
    msg['To'] = ', '.join(email_to)
    msg['Date'] = date
    msg['Subject'] = subject

    if in_reply_to:
        msg.add_header('In-Reply-To', in_reply_to)
    
    # Case 1: Handle the scenario when attachments are present in email info but no attachments sent
    if email_info.attachments and not attachments:
        attachments = email_info.attachments  # Use the existing attachments from the record


    # Case 2: Append existing attachments with new attachments
    elif attachments and email_info.attachments:
        attachments = email_info.attachments + attachments  # Append new attachments

    # Email body handling for both cases
    if email_body:
        msg.attach(MIMEText(email_body, 'plain'))  # Use provided email body
    elif email_info.email_body_url:
        # Fetch the body from the provided email_body_url in the record
        azureblobmanager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))
        email_body = azureblobmanager.download_data_with_url(email_info.email_body_url).decode('utf-8')
        msg.attach(MIMEText(email_body, 'plain'))  # Use body from the record

    # Add CC recipients
    if cc_emails:
        msg['Cc'] = ', '.join(cc_emails)

    # Add BCC recipients
    if bcc_emails:
        msg['Bcc'] = ', '.join(bcc_emails)

    # Add attachments if present
    if attachments:
        msg = add_attachments_in_mail(msg, attachments)

    try:
        # Send the email
        recipients = email_to.copy()  # Add primary recipients
        if cc_emails:
            recipients.extend(cc_emails)  # Add CC recipients
        if bcc_emails:
            recipients.extend(bcc_emails)  # Add BCC recipients
        smtp_server.sendmail(sender_email, recipients, msg.as_string())

        logger.debug(f"Email sent successfully. Message-ID: {message_id}")
        return True

    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        return False

    finally:
        smtp_server.quit()
        logger.debug("SMTP server connection closed.")

def get_metadata_presigned_url(file_data_dict):
    #TODO remove this method and only get pre signed URL 
    container_name, blob_name = extract_container_and_blob(file_data_dict.get('file_path'))
    if container_name and blob_name:
        downloadable_url = blob_name
        metadata = {"filename": file_data_dict.get('file_name'), "filesize": file_data_dict.get('file_size')}
        attachment_data = {
            "downloadable_url": downloadable_url,
            "metadata": metadata
        }
        return attachment_data

def parse_email_info_json(email_info_json):
        if isinstance(email_info_json, dict):
            return EmailInfo.from_json(email_info_json)
        elif isinstance(email_info_json, str):
            return EmailInfo.from_json(json.loads(email_info_json))

def add_attachments_in_mail(msg, attachments):
    for attachment in attachments:
        try:
            # Check if attachment is a dictionary
            if isinstance(attachment, dict):
                attachment = attachment.get('file_url')
            if attachment.startswith('http'):  # If attachment is a URL
                #TODO Use Azure Function and get content check if request takes more time
                response = requests.get(attachment)
                response.raise_for_status()  # Check if the request was successful
                file_data = response.content
                file_name = attachment.split('?')[0].split('/')[-1]  # Extract file name from URL
            else:  # If attachment is a file path
                with open(attachment, 'rb') as file:
                    file_data = file.read()
                file_name = attachment.split('/')[-1]

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={file_name}')
            msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to attach {attachment}: {e}", exc_info=True)

    return msg


def get_comment_from_email_dimension_json(dimension_action_json):
    """
    Extracts comments from the dimension_action_json field in an email conversation.

    Args:
    - dimension_action_json (dict or str): The JSON string or dictionary representing dimension_action_json.

    Returns:
    - str: The comment extracted from the dimension_action_json, or None if not found.
    """
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    logger.debug("dimension_action_json")
    data = dimension_action_json

    logger.debug("data %s", data)

    comment = data.get('comment')
    logger.debug("comment %s", comment)

    return comment


class Azurebucket():
    def __init__(self):
        self.azureblobmanager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

    def download_email_body(self, email_body_url):
        email_body = self.azureblobmanager.download_data_with_url(email_body_url).decode('utf-8')
        return email_body



import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_file:
        for page_num in range(len(pdf_file)):
            page = pdf_file[page_num]
            text += page.get_text()
    return text


def datetime_to_milliseconds(dt):
    if dt.tzinfo is None:
        # Assume UTC if no timezone is specified
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


from datetime import datetime



def parse_price(price):
    return float(price.replace("$", "")) if isinstance(price, str) else float(price)


def validate_item(json_item, excel_df):
    item_code = json_item["itemCode"]
    item_description = json_item["itemDescription"]
    quantity = int(json_item["quantity"])
    unit_price = parse_price(json_item["unitPrice"])
    total_price = parse_price(json_item["totalPrice"])
    expected_total_price = round(quantity * unit_price, 2)

    matching_rows = excel_df[excel_df["Item Code"].str.upper() == item_code.upper()]
    if len(matching_rows) == 0:
        return False, {
            "itemCode": f"{item_code} - Item not available",
        }, expected_total_price

    row = matching_rows.iloc[0]
    row["Unit Price"] = parse_price(row["Unit Price"])
    quantity_error = f"Requested quantity not available, actual quantity: {row['Quantity']}" if row[
                                                                                                    "Quantity"] < quantity else quantity
    price_error = f"Error in price, Actual price: {row['Unit Price']}" if row[
                                                                              "Unit Price"] != unit_price else unit_price
    total_price_error = f"Total price mismatch, expected: {expected_total_price}, found: {total_price}" if expected_total_price != total_price else total_price

    item_valid = row["Quantity"] >= quantity and row["Unit Price"] == unit_price and expected_total_price == total_price

    return item_valid, {
        "itemCode": item_code,
        "itemDescription": item_description,
        "Quantity": quantity_error,
        "Unit Price": price_error,
        "Total Price": total_price_error
    }, expected_total_price


def validate_subtotal(calculated_subtotal, json_subtotal):
    return calculated_subtotal == json_subtotal, f"Subtotal mismatch, expected: {calculated_subtotal}, found: {json_subtotal}"


def validate_total_amount(calculated_subtotal, json_tax, json_total_amount):
    expected_total_amount = round(calculated_subtotal + json_tax, 2)
    return expected_total_amount == json_total_amount, f"Total amount mismatch, expected: {expected_total_amount}, found: {json_total_amount}"


def validate_sensormatic_order_details(json_data, csv_file):
    logger.info(f"In {inspect.currentframe().f_code.co_name}")
    response = {"validated": True, "items": []}
    excel_df = pd.read_csv(csv_file)

    calculated_subtotal = 0

    for json_item in json_data.get("orderdetails", {}).get("items", []):
        item_valid, item_response, expected_total_price = validate_item(json_item, excel_df)
        response["validated"] &= item_valid
        response["items"].append(item_response)
        calculated_subtotal += expected_total_price

    json_subtotal = parse_price(json_data["orderdetails"]["subTotal"])
    subtotal_valid, subtotal_error = validate_subtotal(calculated_subtotal, json_subtotal)
    if not subtotal_valid:
        response["validated"] = False
        response["items"].append({"subTotalError": subtotal_error})

    json_total_amount = parse_price(json_data["orderdetails"]["totalAmount"])
    json_tax = parse_price(json_data["orderdetails"]["tax"]) if json_data["orderdetails"]["tax"] else 0.0
    total_amount_valid, total_amount_error = validate_total_amount(calculated_subtotal, json_tax, json_total_amount)
    if not total_amount_valid:
        response["validated"] = False
        response["items"].append({"totalAmountError": total_amount_error})

    json_data["validated"] = response["validated"]
    json_data["orderdetails"]["items"] = response["items"]

    return json_data


def get_sensormatic_order_status(order_details, csv_file_path):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    order_id = order_details.get("purchase_order_id", "")
    if not order_id:
        order_id = order_details.get("shipment_status_id", "")
    # Read the Excel file
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        logger.error(f"Error: Excel file not found: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error: An error occurred while reading the Excel file: {e}", exc_info=True)
        return None

    # Clean column names to avoid issues with leading/trailing spaces and case sensitivity
    df.columns = df.columns.str.strip()

    # Check if the required columns exist in the Excel file
    required_columns = ['orderID', 'status', 'ETA', 'trackingID']
    if not all(column in df.columns for column in required_columns):
        logger.debug(f"{{'error': 'The Excel file must contain the following columns: {required_columns}'}}")

        return None

    # Ensure orderID column is of string type and clean any leading/trailing spaces
    df['orderID'] = df['orderID'].astype(str).str.strip()

    # Clean the input order_id
    order_id = str(order_id).strip()

    # Find the orderID in the DataFrame
    order_row = df[df['orderID'] == order_id]

    # Check if orderID is found
    if order_row.empty:
        return json.dumps({"error": f"Order ID {order_id} not present."})

    # Get the details of the orderID
    order_details = order_row.iloc[0].dropna().to_dict()

    return order_details


def validate_invoice_details(invoice_details, invoice_file_path):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    invoice_number = invoice_details.get("invoiceinformation").get("invoiceNumber", "")
    total_amount = invoice_details.get("orderdetails").get("Total", "")
    match = re.search(r'\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?', total_amount)

    if match:
        # Extracted value
        total_amount = match.group(0)
        logger.debug(total_amount)

    try:
        df = pd.read_csv(invoice_file_path)
    except FileNotFoundError as e:
        logger.error(f"Error: Excel file not found: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error: An error occurred while reading the Excel file: {e}", exc_info=True)
        return None

    df.columns = df.columns.str.strip()
    required_columns = ['InvoiceNumber', 'TotalAmount']
    if not all(column in df.columns for column in required_columns):
        logger.debug("{'error': 'The Excel file must contain the following columns: %s'}", required_columns)
        return None

    df['InvoiceNumber'] = df['InvoiceNumber'].astype(str).str.strip()
    df['TotalAmount'] = df['TotalAmount'].astype(str).str.strip()

    # Clean the input invoice_number and total_amount
    invoice_number = str(invoice_number).strip()
    total_amount = str(total_amount).strip()

    # Find the invoice_number in the DataFrame
    invoice_row = df[df['InvoiceNumber'] == invoice_number]

    # Check if invoice_number is found
    if invoice_row.empty:
        return json.dumps({"error": f"Invoice number {invoice_number} not present."})

    logger.debug(
        f"invoice_row['TotalAmount'].values[0] != total_amount :: {invoice_row['TotalAmount'].values[0] != total_amount}")

    # Check if total_amount matches
    if invoice_row['TotalAmount'].values[0] != total_amount:
        return json.dumps({"error": f"Total amount for invoice number {invoice_number} does not match."})

    # Get the details of the invoice_number
    invoice_details_extracted = invoice_row.iloc[0].dropna().to_dict()
    return invoice_details_extracted


def resolve_country_alias(alias):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    country = pycountry.countries.get(alpha_2=alias.upper())
    if not country:
        country = pycountry.countries.get(alpha_3=alias.upper())
    if not country:
        try:
            country = pycountry.countries.lookup(alias)
        except LookupError:
            return alias
    if not country:
        return alias
    return country.name


def resolve_state_alias(alias):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    try:
        full_name = us.states.lookup(alias)
        if full_name:
            return full_name.name
        return alias
    except ValueError:
        return alias


def get_details_from_zipcode(zipcode):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    from uszipcode import SearchEngine
    engine = SearchEngine()
    zipcode = engine.by_zipcode(zipcode)
    if zipcode:
        return "United States", zipcode.state, zipcode.major_city
    return None, None, None


def normalize_list_params(param_input_list):
    if (param_input_list):
        if isinstance(param_input_list, str):
            param_input_list = [param_input_list]
        param_input_list = [name.strip("'") for name in param_input_list]
    return param_input_list


def check_profanity(text):
    #TODO need to review and add comments
    """
    Method to detect profane words using guardrails 
    """
    guard = Guard().use_many(
        ProfanityFree(),
        ToxicLanguage(threshold=0.1, validation_method="sentence", on_fail="exception"),
    )

    sentences = re.split(r'[.!?,]', text)
    cleaned_sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    combined_text = ". ".join(cleaned_sentences) + "."
    try:
        guard.validate(combined_text)
        return True
    except Exception as profanity_text_exception:
        pattern = r'-\s*(.*?)(?=\n|$)'

        # Find all matches
        matches = re.findall(pattern, str(profanity_text_exception))

        # Clean up and store results in the desired format
        result = [match.strip().strip('.,') for match in matches]
        return result


def parse_address(recipients_string):
    """
    Extracts names and email addresses from a comma-separated recipient string.

    Args:
        recipients_string: A string containing recipient information.

    Returns:
        A list of tuples, where each tuple contains (name, email).
    """
    logger.info(f" In {inspect.currentframe().f_code.co_name}")

    if not recipients_string:
        return []

    recipient_list = []

    recipient_strings = recipients_string.split(',')
    if ';' in recipients_string:
        recipient_strings = recipients_string.split(';')

    for recipient in recipient_strings:
        name = ""
        parts = recipient.strip().split('<')

        if len(parts) > 1:
            # Extract email address
            email = parts[1].strip('>')

            # Extract name (everything before '<')
            name = parts[0].strip()
        else:
            # No '<' and '>', assume whole string is email address (no name)
            email = recipient.strip()
            name, _ = email.split('@')

        recipient_list.append((name, email))

    return recipient_list


def extract_name_from_address(address):
    if '@' not in address:
        return address
    name, email = parse_address(address)[0]
    if not name:
        name, _ = parse_address(email)[0]
    return name




def extract_name_sublist(sublist):
    """
    Extracts the name from a sublist containing email information.

    Args:
        sublist (list or tuple): A list or tuple containing email parts.

    Returns:
        str: Extracted name.
    """
    if '@' in sublist[0]:
        return extract_name_from_address(sublist[0])
    elif sublist[0]:
        return sublist[0]
    else:
        return extract_name_from_address(sublist[1])


def extract_body_and_signature(email_body):
    # Function to extract and return Body and Signature from mail Body
    logger.info(" In Utils :: extract_body_and_signature")
    signature = None
    signature_pattern = re.compile(RegexTypes.SIGNATURE_BODY_SEGREGATION.value, re.DOTALL)
    match = signature_pattern.search(email_body)
    if match:
        signature = email_body[match.start():].strip()
        email_body = email_body[:match.start()].strip()
        signature = signature.lstrip('-').strip()
    return email_body, signature


def extract_name_email_recipient(email_recipient : EmailRecipient):
    """
    Extracts the name from a email recipient  containing email name and emailId.

    Args:
        email_recipient (EmailRecipient): Email Recipient model containing name and emailId.

    Returns:
        str: Extracted name.
    """
    if email_recipient.name:
        return email_recipient.name
    return extract_name_from_address(email_recipient.email)

def generate_email_summary(email_content, sender, recipient, conversation_uuid,customer_uuid,application_uuid, email_conversation):
    """
        Generates Email Summary and saves in Email Conversation Table
    Args:
        email_content:
        sender:
        recipient:
        conversation_uuid:
        customer_uuid:
        application_uuid:

    Returns:

    """
    logger.info("In Utils :: generate_email_summary")
    logger.debug(f"Params:{email_content, sender, recipient, conversation_uuid}")
    print(f"Params:{email_content, sender, recipient, conversation_uuid}")
    #Extract Sender name
    if is_valid_email_address(sender):
        sender = extract_name_from_address(sender)
    elif not isinstance(sender,str):
        raise InvalidValueProvidedException("Sender is invalid")
    #Extract Recipients ([email1,email2] / email1 / [[firstname,email]] / [(firstname,email)]
    # check if list
    if isinstance(recipient, list):
        #[[name,email]] / [(name,email)]
        if all(isinstance(item, EmailRecipient) for item in recipient):
            recipient_names = [extract_name_email_recipient(sublist) for sublist in recipient]
            recipient = " and ".join(recipient_names)
        #[email1, email2]
        else:
            extract_name = lambda email: extract_name_from_address(email)
            recipient_names = list(map(extract_name, recipient))
            recipient = " and ".join(recipient_names)
    #email1
    elif is_valid_email_address(recipient):
        recipient = extract_name_from_address(recipient)
    elif not isinstance(recipient,str):
        raise InvalidValueProvidedException("recipient is invalid")
    email_content, _ = extract_body_and_signature(email_content)
    #Fetch Email activity
    # email_activity = EmailConversationDaoImpl().fetch_email_activity_from_email_conversation(conversation_uuid=conversation_uuid)
    email_activity = email_conversation.email_activity
    current_summary = email_activity.get('email_summary', "")
    prompt = PromptDaoImpl().fetch_prompt_by_category_filter_json(customer_uuid=customer_uuid,application_uuid=application_uuid,category_name=PromptCategory.SummaryGeneration.value)

    #todo llm exception handling
    # llm_chain = LLMChain(llm=llm)
    #Execute Prompt to update summary
    #Todo execution of llm should be in llm service file
    llm_chain = LLMChain(prompt=prompt)
    try:
        response = llm_chain.query(
            inputs={'previous_email_thread_summary': {current_summary},
                    "current_email": {f"Sender:{sender}\nRecipient:{recipient}\nContent:{email_content}"}})

        response_data = json.loads(response)
        logger.info(f"LLM response : {response_data}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from LLM response: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while querying the LLM: {e}")
        return None

    email_activity['email_summary'] = response_data.get('email_summary', "")
    #Update and save email summary in db
    return conversation_uuid,email_activity

def is_valid_email_address(email_address):
    """
    Validates an email address using regular expressions.

    Args:
        email_address (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    if not email_address:
        return False
    # Define the regex pattern for a valid email address

    # Match the email with the pattern
    if re.match(EMAIL_ADDRESS_PATTERN, email_address):
        return True
    else:
        return False

def convert_docx_to_pdf(docx_path):
    base_name, extension = os.path.splitext(docx_path)
    pdf_path = f"{base_name}.pdf"
    process = subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_path, docx_path])
    if process.returncode != 0:
        logger.error(f"Conversion failed with return code {process.returncode}")
        raise CustomException(f"Failed to convert {docx_path} to PDF.")

    logger.debug(f"Conversion successful: {pdf_path}")
    return pdf_path


def get_content_from_attachments(attachments_path):
    attachment_content = ""
    for attachment in attachments_path:
        if (attachment.endswith('.docx')):
            attachment = convert_docx_to_pdf(attachment)
        content = ""
        if attachment.endswith('.pdf'):
            content = extract_text_from_pdf(attachment)
        attachment_content += content
        if os.path.exists(attachment):
            os.remove(attachment)
    return attachment_content


def send_to_event_hub(next_step_info, output_data):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    next_step_uuid = next_step_info.get('uuid', '')
    next_event_hub = next_step_info.get('topic', '')
    producer = EventHubProducerSync(eventhub=next_event_hub)

    if isinstance(output_data, list):
        for next_step_params in output_data:
            next_event_data = {
                'step_uuid': next_step_uuid,
                'data': {
                    'params': next_step_params
                }
            }
            producer.send_event_data_batch(event_data=next_event_data)
    elif isinstance(output_data, dict):
        next_event_data = {
            'step_uuid': next_step_uuid,
            'data': {
                'params': output_data
            }
        }
        producer.send_event_data_batch(event_data=next_event_data)

    producer.close()

def parse_excel_to_list_of_examples(byte_array):
    """
    Parses excel file for response_configurations and returns as dict format
    """
    logger.info("In Utils:: parse_excel_to_list_of_examples")

    #finally block not necessary as  Pandas handles memory management internally for DataFrames.
    try:
        # Read the Excel file using pandas from the byte array, Load the 'Knowledge' sheet (with headers)
        df = pd.read_excel(byte_array, sheet_name=DefaultResponsesTemplate.SHEET_NAME_OF_RESPONSES.value,engine='openpyxl')
    except ImportError:
        logger.error("Missing 'openpyxl'. Please install it using 'pip install openpyxl'.")
        raise CustomException("Missing 'openpyxl'. Please install it using 'pip install openpyxl'.",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except (BadZipFile,ValueError):
        try:
            # If openpyxl fails, fallback to xlrd (for .xls files)
            df = pd.read_excel(byte_array, sheet_name=DefaultResponsesTemplate.SHEET_NAME_OF_RESPONSES.value, engine='xlrd')
        except ImportError:
            logger.error("Missing 'xlrd'. Please install it using 'pip install xlrd>=2.0.1'.")
            raise CustomException("Missing 'xlrd'. Please install it using 'pip install xlrd>=2.0.1'.",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            raise ValueError(f"Failed to read the file. Ensure it's a valid .xls or .xlsx file")

    #check if dataframe is empty
    if df.empty:
        logger.error("The Excel sheet is empty.")
        raise InvalidValueProvidedException(ErrorMessages.EXCEL_SHEET_IS_EMPTY)

    # Check if required columns exist in the DataFrame
    expected_columns = [DefaultResponsesTemplate.HEADER_1.value, DefaultResponsesTemplate.HEADER_2.value, DefaultResponsesTemplate.HEADER_3.value]
    responses=[]
    for col in expected_columns:
        if col in df.columns:
            #check whether the cell is not none
            try:
                if df[col].iloc[0] is not None:
                    response=str(df[col].iloc[0]).strip()# Extract value from cell
                    #check whether the cell value is empty string
                    if  response!='':
                        responses.append(response)  #  save  cell value in list
                        continue
            except Exception as e:
                logger.error(f"{ErrorMessages.ERROR_PARSING_EXCEL}{(str(e))}")
                raise InvalidValueProvidedException(ErrorMessages.ERROR_PARSING_EXCEL)

            #HEADER 1 is Mandatory Header
            if col== DefaultResponsesTemplate.HEADER_1.value :
                logger.error(ErrorMessages.RESPONSE_I_IS_REQUIRED)
                raise CustomException(ErrorMessages.RESPONSE_I_IS_REQUIRED, status_code=status.HTTP_400_BAD_REQUEST) #Required field
        #HEADER 1 is Mandatory Header
        elif col== DefaultResponsesTemplate.HEADER_1.value :
                logger.error(ErrorMessages.MISSING_REQUIRED_COLUMN.format(col))
                raise InvalidValueProvidedException(ErrorMessages.MISSING_REQUIRED_COLUMN.format(col))
    return responses


def extract_container_and_blob(url):
    """
    Extract container and blob name from the given Azure Blob Storage URL.
    
    Example: 
    URL: "https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx"
    Container: 'connected-enterprise'
    Blob: 'connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx'
    """
    logger.info("In utils :: extract_container_and_blob")
    try:
        # Strip the protocol(https/http) part of the URL to simplify further processing
        base_url = url.split('//')[-1]
        
        # Use regex pattern to extract container name and blob name from the base URL
        pattern = RegexTypes.CONTAINER_NAME_AND_BLOB_NAME.value
        match = re.search(pattern, base_url)

        if match:
            # Extracting container and blob names from the matched groups
            container_name = match.group(1)
            blob_name = match.group(2)
            return container_name, blob_name
        else:
            return None, None
    except Exception as e:
        logger.error(f"Error extracting container and blob: {str(e)}")
        return None, None


def get_metadata_and_presigned_url(file_url):
    """
    Returns filename and a presigned URL for the given blob URL.
    """
    logger.info("In utils:: get_metadata_and_presigned_url")
    try:
        # Extract container and blob names using helper function
        container_name, blob_name = extract_container_and_blob(file_url)
        #Container: 'connected-enterprise'
        #Blob: 'connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx'
        if container_name and blob_name:
            # Extract the file name from the blob path
            if blob_name.split(BlobConstants.BLOB_SEPARATOR)[-1]:
                filename_parts = blob_name.split(BlobConstants.BLOB_SEPARATOR)[-1].split(BlobConstants.FILENAME_PART_SEPARATOR)
                # Recreate the filename excluding the first part (e.g., ID)
                filename = BlobConstants.FILENAME_PART_SEPARATOR.join(filename_parts[1:])
            else:
                logger.info(AzureBlobErrorMessages.INVALID_FILE_MSG.format(file_url))
                raise InvalidValueProvidedException(AzureBlobErrorMessages.INVALID_FILE_MSG.format(file_url))

            attachment_data = {
                "downloadable_url": blob_name,
                "filename": filename
            }
            return attachment_data

        else:
            logger.error("Failed to extract container or blob name.")
            raise InvalidValueProvidedException("Failed to extract container or blob name.")

    except Exception as e:
        # Log the exception if presigned URL generation fails
        logger.info(AzureBlobErrorMessages.ERROR_MSG_PRESIGNED_URL.format(e))
        raise CustomException(AzureBlobErrorMessages.ERROR_MSG_PRESIGNED_URL.format(e),status.HTTP_500_INTERNAL_SERVER_ERROR)


def validate_uuids_dict(uuids_dict):
    """
    validates dictionary of uuids. If not a valid uuid raises exception
    """
    logger.info("In Utils :: validate_uuids_dict")
    #creates error message with key name if a value is not a valid uuid
    error_responses=[]
    #validate each uuid in dictionary
    for header_name in uuids_dict:
        if not is_valid_uuid(uuids_dict[header_name]):
            error_responses.append(f"{header_name} should be valid uuid")
    
    if error_responses:
        logger.error(f"{error_responses}")
        raise CustomException(detail=error_responses, status_code=status.HTTP_400_BAD_REQUEST)
    
def is_valid_uuid(value):
    #checks if input is None or empty
    if validate_input(value):
        # Check if the value is a string
        if isinstance(value, str):
            try:
                uuid_obj = uuid.UUID(value, version=4)
                return True
            except ValueError:
                return False

    return False

def style_header(cell):
    """
    Styles a cell as a header by making the font bold and setting the background color to red.

    :param cell: The cell to style
    """
    cell.font = Font(bold=True, color="FFFFFF")  # White text
    cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")  # Red background


def is_valid_dimension_name(name: str) -> bool:
    """
        Validate a name based on the following conditions:
        1. The name must be between 2 and 64 characters long.
        2. The name should not start or end with a space or hyphen.
        3. The name can only contain alphanumeric characters, spaces, and hyphens.
        4. The name should not contain:
            - Consecutive spaces,
            - Consecutive hyphens,
            - Space followed by hyphen, or underscore
            - Hyphen followed by space or underscore.
            
        Parameters:
        name (str): The name string to validate.
        
        Returns:
        bool: True if the name is valid according to the specified rules, False otherwise.
    """
    # Check length between 2 and 64 characters
    logger.info("In utils:: is_valid_dimension_name")
    logger.info(f"Validating name - {name}")
    if not (2 <= len(name) <= 64):
        logger.info("Name length is not valid")
        return False
    
    # Check for allowed characters and no starting/ending space or hyphen or underscore
    if not re.match(RegexTypes.VALIDATE_NAME_FOR_CHARS_WITHOUT_END_START_SPACE.value, name):
        logger.info("Characters are invalid")
        return False
    
    # Check for no consecutive spaces, hyphens, or space-hyphen combinations
    if re.search(RegexTypes.CONSECUTIVE_SPACE_HYPHEN.value, name):
        logger.info("Name contains Consecutive special characters")
        return False

    return True

def is_user_admin(user_uuid: str,customer_uuid : str,application_uuid: str) -> bool:
    logger.info("In :: is_user_admin")
    role_name, application_name, customer_name=UsersDetailsViewDaoImpl().get_role_name_of_user(user_uuid,customer_uuid,application_uuid)
    if role_name and str(customer_name.lower()+ " " + application_name.lower() +" "+ Role_names.ADMIN.value) == role_name.lower():
        return True
    return False

def generate_detailed_summary(email_body,customer_uuid,application_uuid):
    """
    Generates a detailed summary of an email body if its word count exceeds a specified limit.

    Args:
        email_body (str): The content of the email to be summarized.
        customer_uuid (str): The UUID of the customer for prompt personalization.
        application_uuid (str): The UUID of the application for prompt personalization.

    Returns:
        str: A summarized version of the email body if the word count exceeds the limit;
             otherwise, the original email body.
    """
    logger.info("In Utils :: generate_detailed_summary")
    # if no of words in emai body is greater than 50 then generating summary otherwise returning same body
    # Check the word count of the email body
    word_count_updated = len(re.findall(r'\S+', email_body))
    if word_count_updated <= Configure.BODY_LENGTH.value:
        # If the word count is within the limit, return the original email body
        return email_body
    # Fetch  prompt for email summary generation based on customer and application
    prompt =  PromptDaoImpl().fetch_prompt_by_category_filter_json(customer_uuid=customer_uuid,application_uuid=application_uuid,category_name=PromptCategory.email_summary_generation.value)
    llm_chain = LLMChain(prompt=prompt)
    try:
        response = llm_chain.query(inputs={'email': {email_body}})
        response_data = json.loads(response)
        logger.debug(f"LLM response : {response_data}")
        return response_data.get('email_summary')
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from LLM response: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while querying the LLM: {e}")
        return None
def call_api(method, endpoint, params=None, data=None, json_data=None, headers=None, auth=None):
    logger.info("In Utils : call_api")
    """
    Generic method to call APIs.

    :param method: HTTP method (e.g., 'GET', 'POST','PUT','DELETE')
    :param endpoint: API endpoint
    :param params: Dictionary of query parameters
    :param data: Dictionary of data to be sent in the body of the request (form-encoded)
    :param json_data: Dictionary of data to be sent in the body of the request (JSON-encoded)
    :param headers: Dictionary of headers to be sent with the request
    :return: Response object
    """
    if not isinstance(endpoint, str) or endpoint.strip() == '':
        raise InvalidValueProvidedException(ErrorMessages.INVALID_ENDPOINT)
    if not method:
        raise InvalidValueProvidedException(ErrorMessages.INVALID_HTTP_METHOD)
    try:
        if method == 'GET':
            response = requests.get(endpoint, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(endpoint, params=params, data=data, json=json_data, headers=headers, auth=auth)
        elif method == 'PUT':
            response = requests.put(endpoint, params=params, data=data, json=json_data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(endpoint, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        if status.HTTP_400_BAD_REQUEST <= response.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(f"Client error occurred: {response.status_code} - {response.text}")
            raise CustomException(response.text,status_code=response.status_code)  # Do not retry for 4xx errors

        response.raise_for_status()
        return response
    except CustomException:
        raise
    except requests.exceptions.RequestException as e:
        logger.debug(f"An error occurred with performing API call: {e}")
        raise
    except Exception as e:
        logger.debug(f"An unexpected error occurred while performing Api call :: {e}")
        raise


def update_token_in_secret(secret_name:str, new_token:str, previous_secret_details:dict) ->dict:
    logger.info("In microsoft_graph_utils :: update_token_in_secret")

    """
    Updates the Azure Key Vault secret with a new token.

    Args:
        secret_name (str): The name of the secret in Azure Key Vault.
        new_token (str): The new access token to be stored.
        previous_secret_details (dict): Existing secret details that need to be updated with the new token.

    Raises:
        ResourceNotFoundException: If the specified secret name does not exist in Azure Key Vault.
    """

    # Update the existing secret details dictionary with the new access token.
    previous_secret_details[MicrosoftSecretDetailsKeys.ACCESS_TOKEN.value] = new_token
    logger.info("Updating secret with new token")
    secret_details = json.dumps(previous_secret_details)
    # Store the updated secret back to Azure Key Vault.
    KeyVaultService().update_secret_in_redis_keyvault(secret_name, secret_details,expiry_for_redis=3500)
    return previous_secret_details


def hit_and_retry_with_new_token(end_point, secret_name, microsoft_client_id, microsoft_tenant_id,json_data,method:str="GET"):
    logger.info("In microsoft_graph_utils :: hit_and_retry_with_new_token")

    """
    Attempts to call an API endpoint using a provided access token.
    If the token is invalid or expired, it generates a new token and retries the call.

    Args:
        end_point (str): The API endpoint to call.
        secret_name (str): The name of the secret used for token generation.
        microsoft_client_id (str): Client ID for Microsoft authentication.
        microsoft_tenant_id (str): Tenant ID for Microsoft authentication.

    Returns:
        Response: The response from the API call if successful.

    Raises:
        CustomException: If the API call fails after retrying or due to other errors.
    """
    # get secrets from cache or keyvault
    secret_details = KeyVaultService().get_secret_details_from_redis_or_keyvault(secret_name)
    logger.info(f"Fetched secret details with secret name{secret_name}")

    try:
        # Initial API call with the current access token.
        response = call_api(
            headers={"Authorization": f"Bearer {secret_details[MicrosoftSecretDetailsKeys.ACCESS_TOKEN.value]}"},
            endpoint=end_point,
            json_data=json_data,
            method=method
        )
        logger.info("Successfully fetched response from graph API")

        # Check if the initial response is successful (HTTP 200 OK).
        if response.ok:
            return response
    except CustomException as error:
        # Handle custom exceptions, specifically invalid authentication token errors.
        if error.status_code == 401 and json.loads(error.detail).get("error", {}).get("code",
                                                                                      {}) == CODE_FOR_AUTHENTICATION_ERROR_GRAPH_API:
            # If authentication fails, generate a new access token and retry.
            return retry_by_generating_token(end_point, json_data,method,secret_name, secret_details, microsoft_client_id, microsoft_tenant_id)
        else:
            raise

def retry_by_generating_token(end_point,json_data,method,secret_name, secret_details, microsoft_client_id, microsoft_tenant_id) -> Response:
    logger.info("In microsoft_graph_utils :: retry_by_generating_token")
    access_token = get_access_token(client_secret=secret_details[MicrosoftSecretDetailsKeys.CLIENT_SECRET.value],
                                    microsoft_client_id=microsoft_client_id, microsoft_tenant_id=microsoft_tenant_id)

    # Update the secret in Azure Key Vault with the newly generated access token. Returns str of secret_details
    secret_details = update_token_in_secret(secret_name, access_token, secret_details)

    # Retry the API call with the new token.
    response = call_api(
        headers={"Authorization": f"Bearer {secret_details[MicrosoftSecretDetailsKeys.ACCESS_TOKEN.value]}"},
        endpoint=end_point,
        json_data=json_data,
        method=method
    )
    logger.info("Successfully fetched response from graph API")
    # Return the response if the retry is successful.
    if response.ok:
        return response

    # Log the error if the API call fails after retrying and raise a custom exception.
    logger.error(f"API hit failed: {response.text}")
    raise CustomException(
        f"API hit failed: {response.text}",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def get_access_token(client_secret:str, microsoft_client_id:str, microsoft_tenant_id:str) ->str:
    logger.info("In microsoft_graph_utils :: get_access_token")
    """
    Generates a new access token using the Microsoft OAuth2 client credentials flow
    and updates the secret in Azure Key Vault with the new token.

    Args:
        client_secret (str):The client secret for Microsoft authentication.
        microsoft_client_id (str): The client ID for Microsoft authentication.
        microsoft_tenant_id (str): The tenant ID for Microsoft authentication.

    Returns:
        str: Generated Access token.

    Raises:
        Exception: If the access token generation fails, raises an exception with an error description.
    """

    # Create a ConfidentialClientApplication instance using Microsoft OAuth2 client credentials flow.
    try:
        client = ConfidentialClientApplication(
            microsoft_client_id,
            authority=OutlookUrlsEndPoints.AUTHORITY_URL.value.format(microsoft_tenant_id=microsoft_tenant_id),
            client_credential=client_secret
        )
        # Acquire the access token for the client using the specified scopes.
        result = client.acquire_token_for_client(scopes=[OutlookUrlsEndPoints.DEFAULT_SCOPE.value])
        # Check if the token was successfully generated.
        if "access_token" in result:
            # Log the successful generation of the access token.
            logger.info("Token Generated Successfully")
            return result["access_token"]
        else:
            # Raise an exception if the token generation fails, with the error description.
            raise CustomException(f"Unable to generate access token {result.get('error_description', 'Unknown error')}")
    except Exception as e:
        raise CustomException(f"Unable to generate access token.")

def validate_chroma_results(results):
    """
    Validates the structure and content of ChromaDB results.

    Args:
        results (dict): The results returned by ChromaDB.

    Returns:
        tuple: Validated documents and metadata, or (None, None) if invalid.
    """
    documents = results.get(ChromaParams.DOCUMENTS.value)
    metadatas = results.get(ChromaParams.METADATAS.value)
    embeddings = results.get(ChromaParams.EMBEDDINGS.value)
    # Check if results, documents, or metadata are missing or improperly formatted
    if not results or not isinstance(documents, list) or not isinstance(metadatas, list) or not isinstance(embeddings,list):
        return None, None, None

    # Extract the first list of documents and metadata
    # Validate that documents and metadata are lists with non-zero length
    if len(documents) > 0 and len(metadatas) > 0 and len(embeddings)>0:
        return documents[0], metadatas[0], embeddings[0]

    return None, None,None


def extract_intent_subintents(input_dict,parent_dimension_name,child_dimensions):
    """
    Extracts intents and their corresponding sub-intents from a dictionary
    with keys in the format INTENT,intent_name and SUBINTENT,intent_name,sub_intent_name.

    Args:
        input_dict (dict): Dictionary with keys in the specified format.

    Returns:
        dict: A dictionary where keys are intent names, and values are lists of sub-intent names.
    """
    output_dict = {}
    for key in input_dict.keys():
        parts = key.split(",")  # Split the key into components

        if parts[0] == "INTENT":  # If the key starts with INTENT
            intent_name = parts[1]
            output_dict[intent_name] = set()  # Initialize a set for sub-intents

        elif parts[0] == "SUBINTENT":  # If the key starts with SUBINTENT
            intent_name = parts[1]
            sub_intent_name = parts[2]
            if intent_name not in output_dict:
                output_dict[intent_name] = set()  # Initialize the set if not already present
            output_dict[intent_name].add(sub_intent_name)  # Add the sub-intent to the set

    # Convert sets to lists for the final output
    output_dict = {key: list(value) for key, value in output_dict.items()}
    return identify_required_dimensions_in_metadata(parent_dimension_name=parent_dimension_name,child_dimensions=child_dimensions,output_dict=output_dict)



def identify_required_dimensions_in_metadata(parent_dimension_name,child_dimensions,output_dict):
    # Handle conditions based on parent_dimension_name and child_dimensions
    if not parent_dimension_name and not child_dimensions:
        # Condition 1: Both parent dimensions and child dimensions are not specified
        # Return all intents and their sub-intents
        return output_dict
    elif parent_dimension_name and not child_dimensions:
        # Condition 2: Only parent dimension is specified
        # Return the specified intent and all its sub-intents
        if parent_dimension_name.lower() not in output_dict:
            return {}
        return {parent_dimension_name: output_dict[parent_dimension_name]}

    elif parent_dimension_name and child_dimensions:
        # Condition 3: Both parent dimension and child dimensions are specified
        # Return the specified intent and only the specified sub-intents
        if parent_dimension_name.lower() not in output_dict:
            return {}
        filtered_sub_intents = [
            sub_intent
            for sub_intent in child_dimensions
            if sub_intent.lower() in output_dict[parent_dimension_name.lower()]
        ]
        return {parent_dimension_name: filtered_sub_intents}

    elif not parent_dimension_name and child_dimensions:
        # Condition 4: If parent dimension not specified and child dimensions are specified
        # Return the specified intent and only the specified sub-intents
            return {
                dimension: output_dict[dimension.lower()]
                for dimension in child_dimensions
                if dimension.lower() in output_dict
            }

    return {}  # Default fallback (shouldn't reach here)


def update_existing_training_phrase_metadata(metadata):
    logger.info("In Utils :: update_existing_training_phrase")
    metadata[ChromadbMetaDataParams.SUB_INTENT_FILTER.value] = False
    are_there_other_intents = False
    for key in metadata.keys():
        if key.startswith(ChromadbMetaDataParams.SUB_INTENT.value):
            metadata[ChromadbMetaDataParams.SUB_INTENT_FILTER.value] = True
            are_there_other_intents = True
            break
        elif key.startswith(ChromadbMetaDataParams.INTENT.value):
            are_there_other_intents = True
    return are_there_other_intents,metadata


def get_sub_intent_keys_from_metadata(sub_intent_metadata,intent_identified):
    logger.info("In Utils :: get_sub_intent_name_from_metadata")
    matching_keys = []
    if not sub_intent_metadata:
        return matching_keys
    for key in sub_intent_metadata.keys():
        key_parts = key.split(ChromadbMetaDataParams.SEPARATOR.value)
        #---metadata:[{category:intent_classification},{INTENT,intent_name:True},{SUBINTENT,intent_name,sub_intent_name:True}]---sub intent will have 3 parts and validating them
        if key_parts[0] == ChromadbMetaDataParams.SUB_INTENT.value and key_parts[1].lower()==intent_identified.lower() and len(key_parts) == ChromadbMetaDataParams.LENGTH_FOR_SUB_INTENT.value:
            matching_keys.append(key_parts[2])
    return matching_keys

def remove_intent_and_sub_intents_from_metadata(existing_metadata,intent,sub_intents,remove_intent=False):
    logger.info("In Utils :: remove_intent_and_sub_intents_from_metadata")
    if isinstance(sub_intents,str):
        sub_intents=[sub_intents]
    existing_metadata=existing_metadata.copy()
    if remove_intent and intent:
        existing_metadata.pop(ChromadbMetaDataParams.INTENT.value+ChromadbMetaDataParams.SEPARATOR.value+intent.lower())

    if intent and sub_intents:
        for sub_intent in sub_intents:
            existing_metadata.pop(ChromadbMetaDataParams.SUB_INTENT.value+ChromadbMetaDataParams.SEPARATOR.value+intent.lower()+ChromadbMetaDataParams.SEPARATOR.value+sub_intent.lower())
        return existing_metadata
    keys_to_remove = [
        key for key in existing_metadata.keys()
        if key.startswith(
            ChromadbMetaDataParams.SUB_INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + intent.lower())
    ]

    for key in keys_to_remove:
        existing_metadata.pop(key)

    return existing_metadata


def get_metadata_for_creation(parent_dimension_name: str,child_dimension_names: list):

    logger.info("In Utils :: get_metadata_for_creation")
    # Prepare metadata for the utterances
    metadata = {
        ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value}

    for child_dimension_name in child_dimension_names:
        if parent_dimension_name:
            # For sub-intent
            metadata[ChromadbMetaDataParams.SUB_INTENT.value +
                              ChromadbMetaDataParams.SEPARATOR.value +
                              parent_dimension_name.lower() +
                              ChromadbMetaDataParams.SEPARATOR.value +
                              child_dimension_name.lower()]=True
        else:
            # For primary intent
            metadata[ChromadbMetaDataParams.INTENT.value +
                          ChromadbMetaDataParams.SEPARATOR.value +
                          child_dimension_name.lower()]=True

    metadata[ChromadbMetaDataParams.SUB_INTENT_FILTER.value] = False
    if parent_dimension_name:
        metadata[ChromadbMetaDataParams.INTENT.value +
                      ChromadbMetaDataParams.SEPARATOR.value +
                      parent_dimension_name.lower()]=True
        metadata[ChromadbMetaDataParams.SUB_INTENT_FILTER.value] = True
    return metadata

def get_metadata_for_fetching(parent_dimension_name,child_dimension_names):
    logger.info("In Utils :: get_metadata_for_fetching")
    # Prepare metadata for the utterances
    metadata = [{
        ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value}]
    for child_dimension_name in child_dimension_names:
        if parent_dimension_name:
            # For sub-intent
            metadata.append({ChromadbMetaDataParams.SUB_INTENT.value +
                              ChromadbMetaDataParams.SEPARATOR.value +
                              parent_dimension_name.lower() +
                              ChromadbMetaDataParams.SEPARATOR.value +
                              child_dimension_name.lower():True})
        else:
            # For primary intent
            metadata.append({ChromadbMetaDataParams.INTENT.value +
                          ChromadbMetaDataParams.SEPARATOR.value +
                          child_dimension_name.lower():True})

    if parent_dimension_name:
        metadata.append({ChromadbMetaDataParams.INTENT.value +
                      ChromadbMetaDataParams.SEPARATOR.value +
                      parent_dimension_name.lower():True})
        metadata.append({ChromadbMetaDataParams.SUB_INTENT_FILTER.value:True})
    # else:
    #     metadata.append({ChromadbMetaDataParams.SUB_INTENT_FILTER.value: False})
    return metadata


def get_intent_and_sub_intent(parent_dimension_name,child_dimension_name):
    intents = parent_dimension_name or child_dimension_name
    sub_intents = child_dimension_name if parent_dimension_name else None
    return intents,sub_intents



def compare_chroma_metadatas(current_metadata: dict, existing_metadata: dict, ignore_keys: set = None) -> bool:
    """
    Compares two metadata dictionaries, ignoring specified keys.

    Args:
        current_metadata (dict): The first metadata dictionary to compare.
        existing_metadata (dict): The second metadata dictionary to compare.
        ignore_keys (list): A list of keys to ignore during comparison. Defaults to ['created_at', 'updated_at', 'is_subintent'].

    Returns:
        bool: True if the dictionaries are equal (ignoring the specified keys), False otherwise.
    """
    default_keys = {ChromadbMetaDataParams.CREATED_TIMESTAMP.value, ChromadbMetaDataParams.UPDATED_TIME_STAMP.value, ChromadbMetaDataParams.SUB_INTENT_FILTER.value, ChromadbMetaDataParams.CATEGORY.value}

    if ignore_keys is None:
        ignore_keys = default_keys
    else:
        ignore_keys.update(default_keys)

    # Filter out keys to ignore
    filtered_current_metadata = {k: v for k, v in current_metadata.items() if k not in ignore_keys}
    filtered_existing_metadata = {k: v for k, v in existing_metadata.items() if k not in ignore_keys}

    for key, value in filtered_current_metadata.items():

        if key not in filtered_existing_metadata:
            return False

    return True

def check_intent_present_in_metadata(intent_identified,metadata):
    logger.info("In Utils :: check_intent_present_in_metadata")
    key= ChromadbMetaDataParams.INTENT.value+ChromadbMetaDataParams.SEPARATOR.value+intent_identified.lower()
    return key in metadata

