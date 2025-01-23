import unittest
from unittest.mock import patch, Mock, mock_open, MagicMock, call

import requests
from django.core.exceptions import ObjectDoesNotExist
from requests import Response

from DatabaseApp.models import Email, UserDetailsView
from EmailApp.Exceptions.api_exception import ResourceNotFoundException
from EmailApp.dao.impl.usermgmt_user_details_view_dao_impl import UsersDetailsViewDaoImpl
from EmailApp.utils import is_valid_dimension_name, validate_invoice_details, get_sensormatic_order_status, \
    validate_sensormatic_order_details, \
    TimelineTypes, extract_text_from_pdf, \
    get_timestamp_from_date, parse_date, \
    generate_email_summary, check_profanity, convert_docx_to_pdf, Azurebucket, is_user_admin, \
    validate_chroma_results, extract_intent_subintents, update_existing_training_phrase_metadata, \
    get_sub_intent_keys_from_metadata, remove_intent_and_sub_intents_from_metadata, get_metadata_for_creation, \
    get_metadata_for_fetching, get_intent_and_sub_intent, compare_chroma_metadatas, check_intent_present_in_metadata, generate_detailed_summary,hit_and_retry_with_new_token, retry_by_generating_token, update_token_in_secret, get_access_token, call_api
import pandas as pd
import json
from datetime import datetime
import fitz
import os
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.constant.constants import PromptCategory, TimelineTypes, ChromadbMetaDataParams, \
    CategeriesForPersonalization, OutlookUrlsEndPoints
from EmailApp.constant.constants import PromptCategory, TimelineTypes, OutlookUrlsEndPoints
from django.test import TestCase
import pandas as pd
from EmailApp.utils import parse_excel_to_list_of_examples, CustomException, DefaultResponsesTemplate
from EmailApp.utils import get_metadata_and_presigned_url, extract_container_and_blob
from EmailApp.utils import extract_container_and_blob
from EmailApp.utils import get_metadata_and_presigned_url, extract_container_and_blob
from rest_framework import status
from uuid import uuid4
from EmailApp.utils import validate_uuids_dict


class ValidateInvoiceDetailsTestCase(unittest.TestCase):

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_validate_invoice_details_success(self, mock_read_csv, mock_logger):
        # Mock data
        invoice_details = {
            "invoiceinformation": {
                "invoiceNumber": "INV-001"
            },
            "orderdetails": {
                "Total": "$1,000.00"
            }
        }
        invoice_file_path = 'test_invoice.csv'

        # Mock CSV file content
        mock_csv_content = pd.DataFrame({
            'InvoiceNumber': ['INV-001'],
            'TotalAmount': ['$1,000.00']
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = validate_invoice_details(invoice_details, invoice_file_path)

        # Assertions
        self.assertIsNotNone(result)

        # Verify logger calls
        mock_logger.info.assert_called_once_with(" In validate_invoice_details")

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_validate_invoice_details_file_not_found(self, mock_read_csv, mock_logger):
        # Mock data
        invoice_details = {
            "invoiceinformation": {
                "invoiceNumber": "INV-001"
            },
            "orderdetails": {
                "Total": "$1,000.00"
            }
        }
        invoice_file_path = 'non_existing_file.csv'

        # Mock FileNotFoundError when reading CSV file
        mock_read_csv.side_effect = FileNotFoundError("Mocked file not found error")

        # Call the function
        result = validate_invoice_details(invoice_details, invoice_file_path)

        # Assertions
        self.assertIsNone(result)
        mock_logger.error.assert_called_once_with("Error: Excel file not found: Mocked file not found error",
                                                  exc_info=True)

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_validate_invoice_details_missing_columns(self, mock_read_csv, mock_logger):
        # Mock data
        invoice_details = {
            "invoiceinformation": {
                "invoiceNumber": "INV-001"
            },
            "orderdetails": {
                "Total": "$1,000.00"
            }
        }
        # Mock CSV file content with missing columns
        mock_csv_content = pd.DataFrame({
            'WrongColumnName': ['INV-001'],
            'WrongTotalAmount': ['$1,000.00']
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = validate_invoice_details(invoice_details, 'test_invoice.csv')

        # Assertions
        self.assertIsNone(result)

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_validate_invoice_details_mismatched_amount(self, mock_read_csv, mock_logger):
        # Mock data
        invoice_details = {
            "invoiceinformation": {
                "invoiceNumber": "INV-001"
            },
            "orderdetails": {
                "Total": "$1,000.00"
            }
        }
        # Mock CSV file content with correct invoice number but wrong amount
        mock_csv_content = pd.DataFrame({
            'InvoiceNumber': ['INV-001'],
            'TotalAmount': ['$2,000.00']  # Different total amount
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = validate_invoice_details(invoice_details, 'test_invoice.csv')

        # Assertions
        self.assertIsNotNone(result)
        expected_error = json.dumps({"error": "Total amount for invoice number INV-001 does not match."})
        self.assertEqual(result, expected_error)


class GetSensorMaticOrderStatusTestCase(unittest.TestCase):

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_get_sensormatic_order_status_success(self, mock_read_csv, mock_logger):
        # Mock data
        order_details = {
            "purchase_order_id": "PO-001"
        }
        csv_file_path = 'test_orders.csv'

        # Mock CSV file content
        mock_csv_content = pd.DataFrame({
            'orderID': ['PO-001'],
            'status': ['Shipped'],
            'ETA': ['2024-07-05'],
            'trackingID': ['TRK-001']
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = get_sensormatic_order_status(order_details, csv_file_path)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['orderID'], 'PO-001')
        self.assertEqual(result['status'], 'Shipped')
        self.assertEqual(result['ETA'], '2024-07-05')
        self.assertEqual(result['trackingID'], 'TRK-001')

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_get_sensormatic_order_status_missing_columns(self, mock_read_csv, mock_logger):
        # Mock data
        order_details = {
            "purchase_order_id": "PO-001"
        }
        # Mock CSV file content with missing columns
        mock_csv_content = pd.DataFrame({
            'WrongColumn': ['PO-001']
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = get_sensormatic_order_status(order_details, 'test_orders.csv')

        # Assertions
        self.assertIsNone(result)

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_get_sensormatic_order_status_order_id_not_found(self, mock_read_csv, mock_logger):
        # Mock data
        order_details = {
            "purchase_order_id": "PO-002"  # Non-existent order ID
        }
        # Mock CSV file content
        mock_csv_content = pd.DataFrame({
            'orderID': ['PO-001'],
            'status': ['Shipped'],
            'ETA': ['2024-07-05'],
            'trackingID': ['TRK-001']
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = get_sensormatic_order_status(order_details, 'test_orders.csv')

        # Assertions
        expected_error = json.dumps({"error": "Order ID PO-002 not present."})
        self.assertEqual(result, expected_error)


class ValidateSensorMaticOrderDetailsTestCase(unittest.TestCase):

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_validate_sensormatic_order_details_success(self, mock_read_csv, mock_logger):
        # Mock data
        json_data = {
            "orderdetails": {
                "subTotal": "$1000.00",
                "totalAmount": "$1050.00",
                "tax": "$50.00",
                "items": [
                    {
                        "itemCode": "A001",
                        "itemDescription": "Item A",
                        "quantity": "2",
                        "unitPrice": "$100.00",
                        "totalPrice": "$200.00"
                    },
                    {
                        "itemCode": "B001",
                        "itemDescription": "Item B",
                        "quantity": "1",
                        "unitPrice": "$500.00",
                        "totalPrice": "$500.00"
                    }
                ]
            }
        }

        csv_file = 'test_inventory.csv'

        # Mock CSV file content
        mock_csv_content = pd.DataFrame({
            'Item Code': ['A001', 'B001'],
            'Item Description': ['Item A', 'Item B'],
            'Quantity': [5, 2],
            'Unit Price': ['$100.00', '$500.00']
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = validate_sensormatic_order_details(json_data, csv_file)

        # Assertions
        self.assertEqual(len(result['orderdetails']['items']), 4)  # Two items validated successfully

    @patch('EmailApp.utils.logger')
    @patch('pandas.read_csv')
    def test_validate_sensormatic_order_details_item_not_found(self, mock_read_csv, mock_logger):
        # Mock data
        json_data = {
            "orderdetails": {
                "subTotal": "$1000.00",
                "totalAmount": "$1050.00",
                "tax": "$50.00",
                "items": [
                    {
                        "itemCode": "C001",  # Item not in CSV
                        "itemDescription": "Item C",
                        "quantity": "1",
                        "unitPrice": "$200.00",
                        "totalPrice": "$200.00"
                    }
                ]
            }
        }

        csv_file = 'test_inventory.csv'

        # Mock CSV file content
        mock_csv_content = pd.DataFrame({
            'Item Code': ['A001', 'B001'],
            'Item Description': ['Item A', 'Item B'],
            'Quantity': [5, 2],
            'Unit Price': ['$100.00', '$500.00']
        })
        mock_read_csv.return_value = mock_csv_content

        # Call the function
        result = validate_sensormatic_order_details(json_data, csv_file)

        # Assertions
        self.assertFalse(result['validated'])
        self.assertIn("C001 - Item not available", result['orderdetails']['items'][0]['itemCode'])


class TestExtractTextFromPdf(unittest.TestCase):

    def setUp(self):
        # Create a sample PDF file for testing
        self.pdf_path = "test_sample.pdf"
        self.create_sample_pdf(self.pdf_path)

    def tearDown(self):
        # Remove the sample PDF file after testing
        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)

    def create_sample_pdf(self, path):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Hello, world!")
        doc.save(path)

    def test_extract_text_from_pdf(self):
        expected_text = "Hello, world!"
        actual_text = extract_text_from_pdf(self.pdf_path)
        self.assertIn(expected_text, actual_text)


class TestAzurebucket(unittest.TestCase):

    def setUp(self):
        # Mock AzureBlobManager to avoid actual Azure service calls during tests
        self.mock_azure_blob_manager = MagicMock(AzureBlobManager)
        self.azurebucket = Azurebucket()
        self.azurebucket.azureblobmanager = self.mock_azure_blob_manager

    def test_download_email_body(self):
        # Mock data and behavior for the download_email_body_from_azure_blob method
        mock_email_body = b"Mock email body content"
        self.mock_azure_blob_manager.download_email_body_from_azure_blob.return_value = mock_email_body

        # Call the method under test
        email_body_url = "mock_url"
        email_body = self.azurebucket.download_email_body(email_body_url)

        # Assertions
        self.assertEqual(email_body, mock_email_body)
        self.mock_azure_blob_manager.download_email_body_from_azure_blob.assert_called_once_with(email_body_url)


class TestGetTimestampFromDate(unittest.TestCase):

    def test_parse_date_returns_none(self):
        # Mocking parse_date to return None
        parse_date_mock = MagicMock(return_value=None)

        date = '2024-07-05T12:00:00Z'

        # Patching the parse_date function to return None
        with unittest.mock.patch('EmailApp.utils.parse_date', parse_date_mock):
            result = get_timestamp_from_date(date)

        # Assertions
        self.assertIsNone(result)
        parse_date_mock.assert_called_once_with(date)


class TestParseDate(unittest.TestCase):

    def test_invalid_date_formats(self):
        # Test invalid date formats
        invalid_dates = [
            'Invalid date format',
            'Wed, 27 March 2024 01:37:39 -0700',  # Incorrect month abbreviation
            'Tue, 35 Mar 2024 01:37:39 -0700',  # Invalid day
            'Wed, 27 Mar 2024 01:37:39 ABC',  # Invalid timezone
        ]

        for date_string in invalid_dates:
            with self.subTest(date_string=date_string):
                self.assertIsNone(parse_date(date_string))

    def test_none_input(self):
        # Test None input
        self.assertIsNone(parse_date(None))

class EmailSummaryTestCase(unittest.TestCase):

    @patch('DatabaseApp.models.Email.objects.get')
    @patch('EmailApp.utils.LLMChain')
    def test_generate_email_summary(self, MockLLMChain, mock_get):
        # Mock objects
        mock_email_record = MagicMock()
        mock_response_data = {'email_summary': 'This is a summary'}

        # Mock LLMChain query method
        mock_llm_instance = MockLLMChain.return_value
        mock_llm_instance.query.return_value = json.dumps(mock_response_data)

        # Mock Emails.objects.get()
        mock_get.return_value = mock_email_record
        mock_email_record.email_activity = {}

        # Call the method
        email_content = "Hello, this is the email content."
        sender = "sender@example.com"
        recipient = "recipient@example.com"
        email_uuid = "abc123"

        generate_email_summary(email_content, sender, recipient, email_uuid)

        # Assertions
        self.assertIn('email_summary', mock_email_record.email_activity)
        self.assertEqual(mock_email_record.email_activity['email_summary'], mock_response_data.get('email_summary'))

        # Check if save method was called
        mock_email_record.save.assert_called_once()

    @patch('DatabaseApp.models.Email.objects.get')
    @patch('EmailApp.utils.LLMChain')
    def test_generate_email_summary_recipient_list(self, MockLLMChain, mock_get):
        # Mock objects
        mock_email_record = MagicMock()
        mock_response_data = {'email_summary': 'This is a summary'}

        # Mock LLMChain query method
        mock_llm_instance = MockLLMChain.return_value
        mock_llm_instance.query.return_value = json.dumps(mock_response_data)

        # Mock Emails.objects.get()
        mock_get.return_value = mock_email_record
        mock_email_record.email_activity = {}

        # Call the method
        email_content = "Hello, this is the email content."
        sender = "sender@example.com"
        recipient = ["recipient@example.com", "<recipient2@example.com>"]
        email_uuid = "abc123"

        generate_email_summary(email_content, sender, recipient, email_uuid)

        # Assertions
        self.assertIn('email_summary', mock_email_record.email_activity)
        self.assertEqual(mock_email_record.email_activity['email_summary'], mock_response_data.get('email_summary'))

        # Check if save method was called
        mock_email_record.save.assert_called_once()

    @patch('DatabaseApp.models.Email.objects.get')
    @patch('EmailApp.utils.LLMChain')
    def test_generate_email_summary_recipient_name(self, MockLLMChain, mock_get):
        # Mock objects
        mock_email_record = MagicMock()
        mock_response_data = {'email_summary': 'This is a summary'}

        # Mock LLMChain query method
        mock_llm_instance = MockLLMChain.return_value
        mock_llm_instance.query.return_value = json.dumps(mock_response_data)

        # Mock Emails.objects.get()
        mock_get.return_value = mock_email_record
        mock_email_record.email_activity = {}

        # Call the method
        email_content = "Hello, this is the email content."
        sender = "sender@example.com"
        recipient = "recipient"
        email_uuid = "abc123"

        generate_email_summary(email_content, sender, recipient, email_uuid)

        # Assertions
        self.assertIn('email_summary', mock_email_record.email_activity)
        self.assertEqual(mock_email_record.email_activity['email_summary'], mock_response_data.get('email_summary'))

        # Check if save method was called
        mock_email_record.save.assert_called_once()

    @patch('DatabaseApp.models.Email.objects.get')
    @patch('EmailApp.utils.LLMChain')
    def test_generate_email_summary_recipient_all_list(self, MockLLMChain, mock_get):
        # Mock objects
        mock_email_record = MagicMock()
        mock_response_data = {'email_summary': 'This is a summary'}

        # Mock LLMChain query method
        mock_llm_instance = MockLLMChain.return_value
        mock_llm_instance.query.return_value = json.dumps(mock_response_data)

        # Mock Emails.objects.get()
        mock_get.return_value = mock_email_record
        mock_email_record.email_activity = {}

        # Call the method
        email_content = "Hello, this is the email content."
        sender = "sender@example.com"
        recipient = [["recipient", "recipient1@example.com"]]
        email_uuid = "abc123"

        generate_email_summary(email_content, sender, recipient, email_uuid)

        # Assertions
        self.assertIn('email_summary', mock_email_record.email_activity)
        self.assertEqual(mock_email_record.email_activity['email_summary'], mock_response_data.get('email_summary'))

        # Check if save method was called
        mock_email_record.save.assert_called_once()

    @patch('DatabaseApp.models.Email.objects.get')
    @patch('EmailApp.utils.LLMChain')
    def test_generate_email_summary_exception_handling(self, MockLLMChain, mock_get):
        # Mock Emails.objects.get() raising ObjectDoesNotExist
        mock_get.side_effect = ObjectDoesNotExist

        # Call the method with an invalid email_uuid to trigger the exception handling
        email_content = "Hello, this is the email content."
        sender = "sender@example.com"
        recipient = "recipient@example.com"
        email_uuid = "invalid_uuid"

        result = generate_email_summary(email_content, sender, recipient, email_uuid)

        # Assertions
        self.assertIsNone(result)

    @patch('DatabaseApp.models.Email.objects.get')
    @patch('EmailApp.utils.LLMChain')
    def test_generate_email_summary_json_decode_error(self, MockLLMChain, mock_get):
        # Mock objects
        mock_email_record = MagicMock()
        mock_email_activity = {}

        # Mock LLMChain query method to raise JSONDecodeError
        mock_llm_instance = MockLLMChain.return_value
        mock_llm_instance.query.return_value = "Invalid JSON"

        # Mock Emails.objects.get()
        mock_get.return_value = mock_email_record
        mock_email_record.email_activity = mock_email_activity

        # Call the method
        email_content = "Hello, this is the email content."
        sender = "sender@example.com"
        recipient = "recipient@example.com"
        email_uuid = "abc123"

        with self.assertLogs('EmailApp.utils', level='ERROR') as cm:
            result = generate_email_summary(email_content, sender, recipient, email_uuid)
            self.assertIsNone(result)
            self.assertIn("Failed to decode JSON from LLM response", cm.output[0])

        # Ensure email_activity was not updated
        self.assertNotIn('email_summary', mock_email_record.email_activity)

    @patch('DatabaseApp.models.Email.objects.get')
    @patch('EmailApp.utils.LLMChain')
    def test_generate_email_summary_general_exception(self, MockLLMChain, mock_get):
        # Mock objects
        mock_email_record = MagicMock()
        mock_email_activity = {}

        # Mock LLMChain query method to raise a general exception
        mock_llm_instance = MockLLMChain.return_value
        mock_llm_instance.query.side_effect = Exception("LLM query failed")

        # Mock Emails.objects.get()
        mock_get.return_value = mock_email_record
        mock_email_record.email_activity = mock_email_activity

        # Call the method
        email_content = "Hello, this is the email content."
        sender = "sender@example.com"
        recipient = "recipient@example.com"
        email_uuid = "abc123"

        with self.assertLogs('EmailApp.utils', level='ERROR') as cm:
            result = generate_email_summary(email_content, sender, recipient, email_uuid)
            self.assertIsNone(result)
            self.assertIn("An error occurred while querying the LLM", cm.output[0])

        # Ensure email_activity was not updated
        self.assertNotIn('email_summary', mock_email_record.email_activity)


class TestCheckProfanity(unittest.TestCase):
    @patch('EmailApp.utils.Guard')
    def test_clean_text(self, mock_guard):
        """Tests if the function returns True for clean text."""
        text = "This is a perfectly normal sentence."
        mock_guard.return_value.validate.return_value = None  # Simulate successful validation
        self.assertTrue(check_profanity(text))
        mock_guard.assert_called_once()  # Assert Guard.validate is called once

    @patch('EmailApp.utils.Guard.validate')
    def test_profanity_detected(self, mock_validate):
        """Tests if the function returns a list of profanities found."""
        text = "This sentence contains a curse word like heck."
        mock_exception = Exception("Profanity detected: heck")
        mock_exception.args = ("- heck",)  # Mimic the exception format
        mock_validate.side_effect = mock_exception
        self.assertEqual(check_profanity(text), ["heck"])
        mock_validate.assert_called_once_with(text)  # Assert validate is called with the text


# Assuming the function is within a class named DocxConverter
class TestDocxConverter(unittest.TestCase):

    @patch('subprocess.run')
    def test_successful_conversion(self, mock_subprocess_run):
        """Tests successful conversion of a DOCX file to PDF."""
        docx_path = "valid_docx.docx"
        pdf_path = "valid_docx.pdf"
        mock_process = MagicMock()
        mock_process.returncode = 0  # Simulate successful conversion
        mock_subprocess_run.return_value = mock_process

        converted_pdf_path = convert_docx_to_pdf(docx_path)

        self.assertEqual(converted_pdf_path, pdf_path)
        mock_subprocess_run.assert_called_once_with(
            ['unoconv', '-f', 'pdf', '-o', pdf_path, docx_path]
        )

    @patch('subprocess.run')
    def test_conversion_failure(self, mock_subprocess_run):
        """Tests handling of conversion failure."""
        docx_path = "invalid_docx.docx"
        mock_process = MagicMock()
        mock_process.returncode = 1  # Simulate conversion error
        mock_subprocess_run.return_value = mock_process

        with self.assertRaises(CustomException) as cm:
            convert_docx_to_pdf(docx_path)

        self.assertEqual(str(cm.exception), f"Failed to convert {docx_path} to PDF.")
        mock_subprocess_run.assert_called_once_with(
            ['unoconv', '-f', 'pdf', '-o', 'invalid_docx.pdf', docx_path]
        )


class ParseExcelToListTestCase(TestCase):

    @patch('EmailApp.utils.pd.read_excel')
    def test_parse_excel_to_list_success(self, mock_read_excel):
        # Mock the DataFrame returned by read_excel
        mock_df = pd.DataFrame({
            DefaultResponsesTemplate.HEADER_1.value: ['Response I value'],
            DefaultResponsesTemplate.HEADER_2.value: ['Response II value'],
            DefaultResponsesTemplate.HEADER_3.value: ['Response III value']
        })
        mock_read_excel.return_value = mock_df

        # Call the function under test
        responses = parse_excel_to_list_of_examples('fake_path')

        # Assert the expected result
        self.assertEqual(responses, ['Response I value', 'Response II value', 'Response III value'])

    @patch('EmailApp.utils.pd.read_excel')
    def test_parse_excel_to_list_missing_columns(self, mock_read_excel):
        # Mock the DataFrame returned by read_excel with missing columns
        mock_df = pd.DataFrame({
            DefaultResponsesTemplate.HEADER_2.value: ['Response II value']
            # Missing HEADER_1
        })
        mock_read_excel.return_value = mock_df

        # Call the function under test and assert the exception
        with self.assertRaises(CustomException) as context:
            parse_excel_to_list_of_examples('fake_path')
        self.assertEqual(str(context.exception),
                         f"Error parsing the Excel file: Missing required column: {DefaultResponsesTemplate.HEADER_1.value}")

    @patch('EmailApp.utils.pd.read_excel')
    def test_parse_excel_to_list_missing_response(self, mock_read_excel):
        # Mock the DataFrame with a missing response
        mock_df = pd.DataFrame({
            DefaultResponsesTemplate.HEADER_1.value: [None],  # Missing response
            DefaultResponsesTemplate.HEADER_2.value: ['Response II value'],
            DefaultResponsesTemplate.HEADER_3.value: ['Response III value']
        })
        mock_read_excel.return_value = mock_df

        # Call the function under test and assert the exception
        with self.assertRaises(CustomException) as context:
            parse_excel_to_list_of_examples('fake_path')
        self.assertEqual(str(context.exception), "Error parsing the Excel file: Response_I is required")

    @patch('EmailApp.utils.pd.read_excel')
    def test_parse_excel_to_list_error_parsing_file(self, mock_read_excel):
        # Mock read_excel to raise an exception
        mock_read_excel.side_effect = Exception("Error reading file")

        # Call the function under test and assert the exception
        with self.assertRaises(CustomException) as context:
            parse_excel_to_list_of_examples('fake_path')
        self.assertTrue("Error parsing the Excel file" in str(context.exception))

    @patch('EmailApp.utils.pd.read_excel')
    def test_parse_excel_to_list_empty_sheet(self, mock_read_excel):
        # Mock the DataFrame returned by read_excel with missing columns
        mock_df = pd.DataFrame()
        mock_read_excel.return_value = mock_df

        # Call the function under test and assert the exception
        with self.assertRaises(InvalidValueProvidedException) as context:
            parse_excel_to_list_of_examples('fake_path')
        self.assertEqual(str(context.exception),
                         "Error parsing the Excel file: The Excel sheet is empty. Please add example responses")


class TestExtractContainerAndBlob(unittest.TestCase):

    def test_extract_container_and_blob_valid_url(self):
        # Mock a valid Azure Blob URL
        file_url = "https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx"

        # Call the function to test
        container_name, blob_name = extract_container_and_blob(file_url)

        # Expected container and blob name
        self.assertEqual(container_name, "connected-enterprise")
        self.assertEqual(blob_name,
                         "connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx")

    def test_extract_container_and_blob_invalid_url(self):
        # Mock an invalid URL with no container or blob
        file_url = "https://vassarstorage.blob.core.windows.net/invalid-url"

        # Call the function to test
        container_name, blob_name = extract_container_and_blob(file_url)

        # Should return None for both container and blob
        self.assertIsNone(container_name)
        self.assertIsNone(blob_name)

    def test_extract_container_and_blob_malformed_url(self):
        # Mock a malformed URL
        file_url = "https://vassarstorage.blob.core.windows.net"

        # Call the function to test
        container_name, blob_name = extract_container_and_blob(file_url)

        # Should return None for both container and blob
        self.assertIsNone(container_name)
        self.assertIsNone(blob_name)

    @patch('EmailApp.utils.logger.error')
    def test_extract_container_and_blob_raises_exception(self, mock_logger_error):
        # Mock an invalid URL that raises an exception
        file_url = None

        # Call the function to test
        container_name, blob_name = extract_container_and_blob(file_url)

        # Should return None for both container and blob
        self.assertIsNone(container_name)
        self.assertIsNone(blob_name)
        mock_logger_error.assert_called_once()


class TestGetMetadataAndPresignedUrl(unittest.TestCase):

    @patch('EmailApp.utils.AzureBlobManager.create_presigned_url')
    @patch('EmailApp.utils.extract_container_and_blob')
    def test_get_metadata_and_presigned_url_success(self, mock_extract, mock_create_presigned_url):
        # Mock a valid container and blob extraction
        mock_extract.return_value = ('connected-enterprise',
                                     'connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx')
        mock_create_presigned_url.return_value = "https://presigned_url"

        # Mock URL
        file_url = "https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx"

        # Call the function to test
        result = get_metadata_and_presigned_url(file_url)

        # Check if the returned data is correct
        self.assertEqual(result['downloadable_url'], "https://presigned_url")
        self.assertEqual(result['filename'], "order_status_RS.xlsx")
        mock_create_presigned_url.assert_called_once_with('connected-enterprise',
                                                          'connected_enterprise/sensormatic/email/September/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx')

    @patch('EmailApp.utils.AzureBlobManager.create_presigned_url')
    @patch('EmailApp.utils.extract_container_and_blob')
    def test_get_metadata_and_presigned_url_presigned_url_generation_fails(self, mock_extract,
                                                                           mock_create_presigned_url):
        # Mock valid container and blob extraction
        mock_extract.return_value = (
        'connected-enterprise', 'connected_enterprise/sensormatic/email/September/Attachments/order_status_RS.xlsx')

        # Mock presigned URL generation failure
        mock_create_presigned_url.side_effect = Exception("Presigned URL generation failed")

        file_url = "https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/September/Attachments/order_status_RS.xlsx"

        with self.assertRaises(CustomException) as context:
            get_metadata_and_presigned_url(file_url)

        self.assertIn("Presigned URL generation failed", str(context.exception))
        self.assertEqual(context.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('EmailApp.utils.AzureBlobManager.create_presigned_url')
    def test_get_metadata_and_presigned_url_invalid_container_blob(self, mock_create_presigned_url):
        # Mock URL with no valid container or blob name
        file_url = "https://vassarstorage.blob.core.windows.net/invalid-url"

        with self.assertRaises(CustomException) as context:
            get_metadata_and_presigned_url(file_url)

        # Check if the raised exception contains the appropriate error message and status code
        self.assertIn("Failed to extract container or blob name", str(context.exception))
        self.assertEqual(context.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_create_presigned_url.assert_not_called()

    @patch('EmailApp.utils.AzureBlobManager.create_presigned_url')
    def test_get_metadata_and_presigned_url_invalid_filename(self, mock_create_presigned_url):
        # Mock URL with no valid filename in blob
        file_url = "https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/September/Attachments/"

        with self.assertRaises(CustomException) as context:
            get_metadata_and_presigned_url(file_url)

        # Check if the raised exception contains the appropriate error message and status code
        self.assertIn("Filename not present in the file URL", str(context.exception))
        self.assertEqual(context.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_create_presigned_url.assert_not_called()


class TestValidateUUIDsDict(TestCase):

    def test_validate_uuids_dict_all_valid(self):
        # Dictionary with valid UUIDs
        uuids_dict = {
            "uuid1": str(uuid4()),
            "uuid2": str(uuid4())
        }

        # No exception should be raised
        try:
            validate_uuids_dict(uuids_dict)
        except CustomException:
            self.fail("CustomException was raised unexpectedly with all valid UUIDs.")

    def test_validate_uuids_dict_invalid_uuid(self):
        # Dictionary with an invalid UUID
        uuids_dict = {
            "uuid1": "invalid-uuid",
            "uuid2": str(uuid4())
        }

        with self.assertRaises(CustomException) as context:
            validate_uuids_dict(uuids_dict)

        # Assert that the error message contains the invalid field
        self.assertIn("uuid1 should be valid uuid", str(context.exception.detail))
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_uuids_dict_multiple_invalid_uuids(self):
        # Dictionary with multiple invalid UUIDs
        uuids_dict = {
            "uuid1": "invalid-uuid-1",
            "uuid2": "invalid-uuid-2"
        }

        with self.assertRaises(CustomException) as context:
            validate_uuids_dict(uuids_dict)

        # Assert that the error message contains both invalid fields
        self.assertIn("uuid1 should be valid uuid", str(context.exception.detail))
        self.assertIn("uuid2 should be valid uuid", str(context.exception.detail))
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_uuids_dict_empty_value(self):
        # Dictionary with an empty value
        uuids_dict = {
            "uuid1": "",
            "uuid2": str(uuid4())
        }

        with self.assertRaises(CustomException) as context:
            validate_uuids_dict(uuids_dict)

        # Assert that the error message contains the empty value field
        self.assertIn("uuid1 should be valid uuid", str(context.exception.detail))
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_uuids_dict_none_value(self):
        # Dictionary with None value
        uuids_dict = {
            "uuid1": None,
            "uuid2": str(uuid4())
        }

        with self.assertRaises(CustomException) as context:
            validate_uuids_dict(uuids_dict)

        # Assert that the error message contains the None value field
        self.assertIn("uuid1 should be valid uuid", str(context.exception.detail))
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)


class TestIsValidDimensionName(TestCase):
    def test_is_valid_dimension_name(self):
        # Valid names
        assert is_valid_dimension_name("John") == True  # Simple valid name
        assert is_valid_dimension_name("Mary-Jane") == True  # Hyphen in the middle
        assert is_valid_dimension_name("Mary Jane") == True  # Space in the middle
        assert is_valid_dimension_name("A" * 64) == True  # Name with exactly 64 characters
        assert is_valid_dimension_name("A B-C D") == True  # Mixed valid characters

        # Invalid names - Length
        assert is_valid_dimension_name("A") == False  # Less than 2 characters
        assert is_valid_dimension_name("A" * 65) == False  # More than 64 characters

        # Invalid names - Starts or ends with space or hyphen
        assert is_valid_dimension_name("-John") == False  # Starts with a hyphen
        assert is_valid_dimension_name("John-") == False  # Ends with a hyphen
        assert is_valid_dimension_name(" John") == False  # Starts with a space
        assert is_valid_dimension_name("John ") == False  # Ends with a space

        # Invalid names - Consecutive spaces, hyphens, or space-hyphen combinations
        assert is_valid_dimension_name("Mary  Jane") == False  # Consecutive spaces
        assert is_valid_dimension_name("Mary--Jane") == False  # Consecutive hyphens
        assert is_valid_dimension_name("Mary -Jane") == False  # Space followed by hyphen
        assert is_valid_dimension_name("Mary- Jane") == False  # Hyphen followed by space

        # Invalid names - Unsupported characters
        assert is_valid_dimension_name("John@Doe") == False  # Special character '@' not allowed
        assert is_valid_dimension_name("John_Doe") == False  # Special character '_' not allowed


class TestIsUserAdmin(unittest.TestCase):

    @patch('EmailApp.utils.UsersDetailsViewDaoImpl.get_role_name_of_user')
    def test_is_user_admin_admin_role(self, mock_get_role_name):
        # Arrange
        user_uuid = "user-123"
        customer_uuid = "customer-456"
        application_uuid = "app-789"

        # Simulate the return value of the patched method
        mock_get_role_name.return_value = ("customer_name app_name admin", "app_name", "customer_name")

        # Act
        result = is_user_admin(user_uuid, customer_uuid, application_uuid)

        # Assert
        self.assertTrue(result)
        mock_get_role_name.assert_called_once_with(user_uuid, customer_uuid, application_uuid)

    @patch('EmailApp.utils.UsersDetailsViewDaoImpl.get_role_name_of_user')
    def test_is_user_admin_non_admin_role(self, mock_get_role_name):
        # Arrange
        user_uuid = "user-123"
        customer_uuid = "customer-456"
        application_uuid = "app-789"

        # Simulate the return value of the patched method
        mock_get_role_name.return_value = ("customer_name app_name user", "customer_name", "app_name")

        # Act
        result = is_user_admin(user_uuid, customer_uuid, application_uuid)

        # Assert
        self.assertFalse(result)
        mock_get_role_name.assert_called_once_with(user_uuid, customer_uuid, application_uuid)


class TestUsersDetailsViewDaoImpl(unittest.TestCase):
    @patch('EmailApp.dao.impl.usermgmt_user_details_view_dao_impl.UserDetailsView.objects.filter')
    def test_get_role_name_of_user_success(self, mock_filter):
        # Arrange
        user_uuid = "user-123"
        customer_uuid = "customer-456"
        application_uuid = "app-789"
        expected_role_name = "CSR_ADMINISTRATOR"

        # Mock the behavior of filter().values_list().first()
        mock_filter.return_value.values_list.return_value.first.return_value = expected_role_name

        dao = UsersDetailsViewDaoImpl()

        # Act
        result = dao.get_role_name_of_user(user_uuid, customer_uuid, application_uuid)

        # Assert
        self.assertEqual(result, expected_role_name)
        mock_filter.assert_called_once_with(
            user_id=user_uuid, customer_id=customer_uuid, application_id=application_uuid
        )
        mock_filter.return_value.values_list.assert_called_once_with('role_name', 'application_name', 'customer_name')
        mock_filter.return_value.values_list.return_value.first.assert_called_once()

    @patch('EmailApp.dao.impl.usermgmt_user_details_view_dao_impl.UserDetailsView.objects.filter')
    def test_get_role_name_of_user_not_found(self, mock_filter):
        # Arrange
        user_uuid = "user-123"
        customer_uuid = "customer-456"
        application_uuid = "app-789"

        # Mock the behavior of filter().values_list().first() to return None
        mock_filter.return_value.values_list.return_value.first.return_value = None

        dao = UsersDetailsViewDaoImpl()

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            dao.get_role_name_of_user(user_uuid, customer_uuid, application_uuid)

        # Validate the exception details
        self.assertEqual(context.exception.detail, ErrorMessages.USER_NOT_FOUND_IN_USERMGMT)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

        mock_filter.assert_called_once_with(
            user_id=user_uuid, customer_id=customer_uuid, application_id=application_uuid
        )
        mock_filter.return_value.values_list.assert_called_once_with('role_name', 'application_name', 'customer_name')
        mock_filter.return_value.values_list.return_value.first.assert_called_once()


class TestValidateChromaResults(unittest.TestCase):

    def test_valid_input(self):
        results = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [["meta1", "meta2"]],
            "embeddings": [["embed1", "embed2"]]
        }
        documents, metadatas, embeddings = validate_chroma_results(results)
        self.assertEqual(documents, ["doc1", "doc2"])
        self.assertEqual(metadatas, ["meta1", "meta2"])
        self.assertEqual(embeddings, ["embed1", "embed2"])

    def test_missing_keys(self):
        results = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [["meta1", "meta2"]]
        }
        documents, metadatas, embeddings = validate_chroma_results(results)
        self.assertIsNone(documents)
        self.assertIsNone(metadatas)
        self.assertIsNone(embeddings)

    def test_invalid_types(self):
        results = {
            "documents": "not a list",
            "metadatas": [["meta1", "meta2"]],
            "embeddings": [["embed1", "embed2"]]
        }
        documents, metadatas, embeddings = validate_chroma_results(results)
        self.assertIsNone(documents)
        self.assertIsNone(metadatas)
        self.assertIsNone(embeddings)

    def test_empty_lists(self):
        results = {
            "documents": [],
            "metadatas": [],
            "embeddings": []
        }
        documents, metadatas, embeddings = validate_chroma_results(results)
        self.assertIsNone(documents)
        self.assertIsNone(metadatas)
        self.assertIsNone(embeddings)


class TestExtractIntentSubintents(unittest.TestCase):

    def test_valid_input_no_filters(self):
        input_dict = {
            "INTENT,Order": True,
            "SUBINTENT,Order,Track": True,
            "INTENT,Feedback": True,
            "SUBINTENT,Feedback,Positive": True
        }
        parent_dimension_name = None
        child_dimensions = []
        output = extract_intent_subintents(input_dict, parent_dimension_name, child_dimensions)
        expected_output = {
            "Order": ["Track"],
            "Feedback": ["Positive"]
        }
        self.assertEqual(output, expected_output)

    def test_filter_by_parent_dimension(self):
        input_dict = {
            "INTENT,order": True,
            "SUBINTENT,order,track": True,
            "INTENT,feedback": True,
            "SUBINTENT,feedback,positive": True
        }
        parent_dimension_name = "order"
        child_dimensions = []
        output = extract_intent_subintents(input_dict, parent_dimension_name, child_dimensions)
        expected_output = {
            "order": ["track"]
        }
        self.assertEqual(output, expected_output)

    def test_filter_by_parent_and_child_dimensions(self):
        input_dict = {
            "INTENT,order": True,
            "SUBINTENT,order,track": True,
            "SUBINTENT,order,cancel": True,
            "INTENT,feedback": True,
            "SUBINTENT,feedback,positive": True
        }
        parent_dimension_name = "order"
        child_dimensions = ["track"]
        output = extract_intent_subintents(input_dict, parent_dimension_name, child_dimensions)
        expected_output = {
            "order": ["track"]
        }
        self.assertEqual(output, expected_output)

    def test_filter_by_child_dimensions_only(self):
        input_dict = {
            "INTENT,order": True,
            "SUBINTENT,order,track": True,
            "INTENT,feedback": True,
            "SUBINTENT,feedback,positive": True
        }
        parent_dimension_name = None
        child_dimensions = ["order"]
        output = extract_intent_subintents(input_dict, parent_dimension_name, child_dimensions)
        expected_output = {
            "order": ["track"]
        }
        self.assertEqual(output, expected_output)

    def test_empty_input(self):
        input_dict = {}
        parent_dimension_name = None
        child_dimensions = []
        output = extract_intent_subintents(input_dict, parent_dimension_name, child_dimensions)
        expected_output = {}
        self.assertEqual(output, expected_output)

    def test_invalid_parent_dimension(self):
        input_dict = {
            "INTENT,Order": True,
            "SUBINTENT,Order,Track": True,
            "SUBINTENT,Order,Cancel": True,
            "INTENT,Feedback": True,
            "SUBINTENT,Feedback,Positive": True
        }
        parent_dimension_name = "InvalidDimension"
        child_dimensions = []
        output = extract_intent_subintents(input_dict, parent_dimension_name, child_dimensions)
        expected_output = {}
        self.assertEqual(output, expected_output)

    def test_invalid_child_dimensions(self):
        input_dict = {
            "INTENT,order": True,
            "SUBINTENT,order,track": True,
            "INTENT,feedback": True,
            "SUBINTENT,feedback,positive": True
        }
        parent_dimension_name = "order"
        child_dimensions = ["InvalidSubIntent"]
        output = extract_intent_subintents(input_dict, parent_dimension_name, child_dimensions)
        expected_output = {
            "order": []
        }
        self.assertEqual(output, expected_output)

class TestUpdateExistingTrainingPhraseMetadata(unittest.TestCase):

    def test_no_intents_or_sub_intents(self):
        metadata = {
            "other_key": "value"
        }
        are_there_other_intents, updated_metadata = update_existing_training_phrase_metadata(metadata)
        self.assertFalse(are_there_other_intents)
        self.assertFalse(updated_metadata.get(ChromadbMetaDataParams.SUB_INTENT_FILTER.value))

    def test_only_intent_key(self):
        metadata = {
            "INTENT,some_intent": "value"
        }
        are_there_other_intents, updated_metadata = update_existing_training_phrase_metadata(metadata)
        self.assertTrue(are_there_other_intents)
        self.assertFalse(updated_metadata.get(ChromadbMetaDataParams.SUB_INTENT_FILTER.value))

    def test_only_sub_intent_key(self):
        metadata = {
            "SUBINTENT,some_intent,some_sub_intent": "value"
        }
        are_there_other_intents, updated_metadata = update_existing_training_phrase_metadata(metadata)
        self.assertTrue(are_there_other_intents)
        self.assertTrue(updated_metadata.get(ChromadbMetaDataParams.SUB_INTENT_FILTER.value))

    def test_both_intent_and_sub_intent_keys(self):
        metadata = {
            "INTENT,some_intent": "value",
            "SUBINTENT,some_intent,some_sub_intent": "value"
        }
        are_there_other_intents, updated_metadata = update_existing_training_phrase_metadata(metadata)
        self.assertTrue(are_there_other_intents)
        self.assertTrue(updated_metadata.get(ChromadbMetaDataParams.SUB_INTENT_FILTER.value))

    def test_empty_metadata(self):
        metadata = {}
        are_there_other_intents, updated_metadata = update_existing_training_phrase_metadata(metadata)
        self.assertFalse(are_there_other_intents)
        self.assertFalse(updated_metadata.get(ChromadbMetaDataParams.SUB_INTENT_FILTER.value))

    def test_multiple_intent_and_sub_intent_keys(self):
        metadata = {
            "INTENT,intent1": "value1",
            "INTENT,intent2": "value2",
            "SUBINTENT,intent1,sub_intent1": "value3",
            "SUBINTENT,intent2,sub_intent2": "value4"
        }
        are_there_other_intents, updated_metadata = update_existing_training_phrase_metadata(metadata)
        self.assertTrue(are_there_other_intents)
        self.assertTrue(updated_metadata.get(ChromadbMetaDataParams.SUB_INTENT_FILTER.value))


class TestGetSubIntentKeysFromMetadata(unittest.TestCase):

    def test_empty_metadata(self):
        sub_intent_metadata = {}
        intent_identified = "order"
        result = get_sub_intent_keys_from_metadata(sub_intent_metadata, intent_identified)
        self.assertEqual(result, [])

    def test_no_matching_sub_intents(self):
        sub_intent_metadata = {
            "SUBINTENT,order,track": "value1",
            "SUBINTENT,feedback,positive": "value2"
        }
        intent_identified = "shipment"
        result = get_sub_intent_keys_from_metadata(sub_intent_metadata, intent_identified)
        self.assertEqual(result, [])

    def test_matching_sub_intents(self):
        sub_intent_metadata = {
            "SUBINTENT,order,track": "value1",
            "SUBINTENT,order,cancel": "value2",
            "SUBINTENT,feedback,positive": "value3"
        }
        intent_identified = "order"
        result = get_sub_intent_keys_from_metadata(sub_intent_metadata, intent_identified)
        self.assertEqual(result, ["track", "cancel"])

    def test_incorrect_structure_in_metadata(self):
        sub_intent_metadata = {
            "SUBINTENT,order,track,something_extra": "value1",  # Invalid structure
            "SUBINTENT,order,cancel": "value2"
        }
        intent_identified = "order"
        result = get_sub_intent_keys_from_metadata(sub_intent_metadata, intent_identified)
        self.assertEqual(result, ["cancel"])  # Only "cancel" should be returned

    def test_sub_intent_with_incorrect_intent_name(self):
        sub_intent_metadata = {
            "SUBINTENT,order,track": "value1",
            "SUBINTENT,order,cancel": "value2",
            "SUBINTENT,feedback,positive": "value3"
        }
        intent_identified = "feedback"  # Intent doesn't match
        result = get_sub_intent_keys_from_metadata(sub_intent_metadata, intent_identified)
        self.assertEqual(result, ["positive"])

    def test_case_insensitive_matching(self):
        sub_intent_metadata = {
            "SUBINTENT,Order,Track": "value1",
            "SUBINTENT,order,cancel": "value2"
        }
        intent_identified = "order"
        result = get_sub_intent_keys_from_metadata(sub_intent_metadata, intent_identified)
        self.assertEqual(result, ["Track", "cancel"])


class TestRemoveIntentAndSubIntentsFromMetadata(unittest.TestCase):


    def test_remove_intent_and_sub_intents(self):
        existing_metadata = {
            "INTENT,order": "value1",
            "SUBINTENT,order,track": "value2",
            "SUBINTENT,order,cancel": "value3",
            "SUBINTENT,feedback,positive": "value4"
        }
        intent = "order"
        sub_intents = ["track", "cancel"]
        result = remove_intent_and_sub_intents_from_metadata(existing_metadata, intent, sub_intents)
        expected_metadata = {
            "INTENT,order": "value1",
            "SUBINTENT,feedback,positive": "value4"
        }
        self.assertEqual(result, expected_metadata)

    def test_remove_only_intent(self):
        existing_metadata = {
            "INTENT,order": "value1",
            "SUBINTENT,order,track": "value2",
            "SUBINTENT,order,cancel": "value3",
            "SUBINTENT,feedback,positive": "value4"
        }
        intent = "order"
        sub_intents = []
        result = remove_intent_and_sub_intents_from_metadata(existing_metadata, intent, sub_intents)
        expected_metadata = {"INTENT,order": "value1",
            "SUBINTENT,feedback,positive": "value4"
        }
        self.assertEqual(result, expected_metadata)

    def test_remove_sub_intents_only(self):
        existing_metadata = {
            "INTENT,order": "value1",
            "SUBINTENT,order,track": "value2",
            "SUBINTENT,order,cancel": "value3",
            "SUBINTENT,feedback,positive": "value4"
        }
        intent = "order"
        sub_intents = "track"
        result = remove_intent_and_sub_intents_from_metadata(existing_metadata, intent, sub_intents)
        expected_metadata = {
            "INTENT,order": "value1",
            "SUBINTENT,order,cancel": "value3",
            "SUBINTENT,feedback,positive": "value4"
        }
        self.assertEqual(result, expected_metadata)

    def test_remove_intent_with_flag(self):
        existing_metadata = {
            "INTENT,order": "value1",
            "SUBINTENT,order,track": "value2",
            "SUBINTENT,order,cancel": "value3",
            "SUBINTENT,feedback,positive": "value4"
        }
        intent = "order"
        sub_intents = ["track", "cancel"]
        result = remove_intent_and_sub_intents_from_metadata(existing_metadata, intent, sub_intents, remove_intent=True)
        expected_metadata = {
            "SUBINTENT,feedback,positive": "value4"
        }
        self.assertEqual(result, expected_metadata)


class TestGetMetadataForCreation(unittest.TestCase):

    def test_no_parent_dimension(self):
        parent_dimension_name = None
        child_dimension_names = ["track", "cancel"]

        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        expected_metadata = {
            ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value,
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: False,
            ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "track": True,
            ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "cancel": True
        }

        self.assertEqual(result, expected_metadata)

    def test_with_parent_dimension(self):
        parent_dimension_name = "order"
        child_dimension_names = ["track", "cancel"]

        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        expected_metadata = {
            ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value,
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True,
            ChromadbMetaDataParams.SUB_INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order" + ChromadbMetaDataParams.SEPARATOR.value + "track": True,
            ChromadbMetaDataParams.SUB_INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order" + ChromadbMetaDataParams.SEPARATOR.value + "cancel": True,
            ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order": True
        }

        self.assertEqual(result, expected_metadata)

    def test_empty_child_dimension_names(self):
        parent_dimension_name = "order"
        child_dimension_names = []

        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        expected_metadata = {
            ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value,
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True,
            ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order": True
        }

        self.assertEqual(result, expected_metadata)

    def test_no_parent_and_empty_child_dimension(self):
        parent_dimension_name = None
        child_dimension_names = []

        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        expected_metadata = {
            ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value,
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: False
        }

        self.assertEqual(result, expected_metadata)

    def test_with_parent_dimension_and_empty_child_dimension(self):
        parent_dimension_name = "order"
        child_dimension_names = []

        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        expected_metadata = {
            ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value,
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True,
            ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order": True
        }

        self.assertEqual(result, expected_metadata)


class TestGetMetadataForFetching(unittest.TestCase):

    def test_no_parent_dimension(self):
        parent_dimension_name = None
        child_dimension_names = ["track"]

        result = get_metadata_for_fetching(parent_dimension_name, child_dimension_names)

        expected_metadata = [
            {ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value},
            {ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "track": True}
        ]

        self.assertEqual(result, expected_metadata)

    def test_with_parent_dimension(self):
        parent_dimension_name = "order"
        child_dimension_names = ["track"]

        result = get_metadata_for_fetching(parent_dimension_name, child_dimension_names)

        expected_metadata = [
            {ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value},
            {
                ChromadbMetaDataParams.SUB_INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order" + ChromadbMetaDataParams.SEPARATOR.value + "track": True},
            {ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order": True},
            {ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True}
        ]

        self.assertEqual(result, expected_metadata)

    def test_empty_child_dimension_names(self):
        parent_dimension_name = "order"
        child_dimension_names = []

        result = get_metadata_for_fetching(parent_dimension_name, child_dimension_names)
        expected_metadata = [
            {ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value},
            {ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order": True},
            {ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True}
        ]

        self.assertEqual(result, expected_metadata)

    def test_no_parent_and_empty_child_dimension(self):
        parent_dimension_name = None
        child_dimension_names = []

        result = get_metadata_for_fetching(parent_dimension_name, child_dimension_names)

        expected_metadata = [
            {ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value}
        ]

        self.assertEqual(result, expected_metadata)

    def test_with_parent_dimension_and_empty_child_dimension(self):
        parent_dimension_name = "order"
        child_dimension_names = []

        result = get_metadata_for_fetching(parent_dimension_name, child_dimension_names)

        expected_metadata = [
            {ChromadbMetaDataParams.CATEGORY.value: CategeriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value},
            {ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "order": True},
            {ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True}
        ]

        self.assertEqual(result, expected_metadata)


class TestGetIntentAndSubIntent(unittest.TestCase):

    def test_both_parent_and_child_provided(self):
        parent_dimension_name = "order"
        child_dimension_name = "track"

        result = get_intent_and_sub_intent(parent_dimension_name, child_dimension_name)

        # Expected intent is parent_dimension_name, and sub-intent is child_dimension_name
        expected_result = ("order", "track")

        self.assertEqual(result, expected_result)

    def test_only_child_provided(self):
        parent_dimension_name = None
        child_dimension_name = "track"

        result = get_intent_and_sub_intent(parent_dimension_name, child_dimension_name)

        # Expected intent is child_dimension_name, and no sub-intent
        expected_result = ("track", None)

        self.assertEqual(result, expected_result)

    def test_only_parent_provided(self):
        parent_dimension_name = "order"
        child_dimension_name = None

        result = get_intent_and_sub_intent(parent_dimension_name, child_dimension_name)

        # Expected intent is parent_dimension_name, and no sub-intent
        expected_result = ("order", None)

        self.assertEqual(result, expected_result)

    def test_both_none(self):
        parent_dimension_name = None
        child_dimension_name = None

        result = get_intent_and_sub_intent(parent_dimension_name, child_dimension_name)

        # Expected result should be (None, None)
        expected_result = (None, None)

        self.assertEqual(result, expected_result)


class TestCompareChromaMetadatas(unittest.TestCase):

    def setUp(self):
        self.current_metadata = {
            ChromadbMetaDataParams.CREATED_TIMESTAMP.value: "2025-01-01",
            ChromadbMetaDataParams.UPDATED_TIME_STAMP.value: "2025-01-02",
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True,
            ChromadbMetaDataParams.CATEGORY.value: "IntentClassification",
            "key1": "value1",
            "key2": "value2"
        }

        self.existing_metadata = {
            ChromadbMetaDataParams.CREATED_TIMESTAMP.value: "2025-01-01",
            ChromadbMetaDataParams.UPDATED_TIME_STAMP.value: "2025-01-02",
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True,
            ChromadbMetaDataParams.CATEGORY.value: "IntentClassification",
            "key1": "value1",
            "key2": "value2"
        }

    def test_identical_metadata_no_ignore_keys(self):
        result = compare_chroma_metadatas(self.current_metadata, self.existing_metadata)
        self.assertTrue(result)

    def test_identical_metadata_with_ignore_keys(self):
        ignore_keys = {ChromadbMetaDataParams.CREATED_TIMESTAMP.value, ChromadbMetaDataParams.UPDATED_TIME_STAMP.value}
        result = compare_chroma_metadatas(self.current_metadata, self.existing_metadata, ignore_keys)
        self.assertTrue(result)

    def test_different_metadata_no_ignore_keys(self):
        self.existing_metadata["key3"] = "different_value"
        result = compare_chroma_metadatas(self.existing_metadata, self.current_metadata)
        self.assertFalse(result)

    def test_different_metadata_with_ignore_keys(self):
        ignore_keys = {ChromadbMetaDataParams.CREATED_TIMESTAMP.value, ChromadbMetaDataParams.UPDATED_TIME_STAMP.value}
        self.existing_metadata["key1"] = "different_value"
        result = compare_chroma_metadatas(self.existing_metadata, self.current_metadata, ignore_keys)
        self.assertTrue(result)

    def test_different_keys_no_ignore_keys(self):
        self.existing_metadata = {
            ChromadbMetaDataParams.CREATED_TIMESTAMP.value: "2025-01-01",
            ChromadbMetaDataParams.UPDATED_TIME_STAMP.value: "2025-01-02",
            ChromadbMetaDataParams.SUB_INTENT_FILTER.value: True,
            ChromadbMetaDataParams.CATEGORY.value: "IntentClassification",
            "key3": "value3"
        }
        result = compare_chroma_metadatas(self.current_metadata, self.existing_metadata)
        self.assertFalse(result)

    def test_ignore_keys_is_none(self):
        # When ignore_keys is None, the default keys should be used
        ignore_keys = None
        result = compare_chroma_metadatas(self.current_metadata, self.existing_metadata, ignore_keys)
        self.assertTrue(result)

    def test_ignore_keys_is_empty_set(self):
        ignore_keys = set()
        result = compare_chroma_metadatas(self.current_metadata, self.existing_metadata, ignore_keys)
        self.assertTrue(result)

class TestCheckIntentPresentInMetadata(unittest.TestCase):

    def setUp(self):
        self.metadata = {
            ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "intent1": True,
            ChromadbMetaDataParams.INTENT.value + ChromadbMetaDataParams.SEPARATOR.value + "intent2": True
        }

    def test_intent_present_in_metadata(self):
        result = check_intent_present_in_metadata("intent1", self.metadata)
        self.assertTrue(result)

    def test_intent_not_present_in_metadata(self):
        result = check_intent_present_in_metadata("intent3", self.metadata)
        self.assertFalse(result)

    def test_intent_present_case_insensitive(self):
        result = check_intent_present_in_metadata("Intent1", self.metadata)
        self.assertTrue(result)

    def test_empty_metadata(self):
        empty_metadata = {}
        result = check_intent_present_in_metadata("intent1", empty_metadata)
        self.assertFalse(result)

    def test_incorrect_key_format_in_metadata(self):
        incorrect_metadata = {
            "INTENTintent1": True  # Incorrect format, missing separator
        }
        result = check_intent_present_in_metadata("intent1", incorrect_metadata)
        self.assertFalse(result)

class TestGenerateDetailedSummary(unittest.TestCase):

    @patch('EmailApp.utils.PromptDaoImpl.fetch_prompt_by_category_filter_json')
    @patch('EmailApp.utils.LLMChain.query')
    def test_short_email_body(self, mock_query, mock_fetch_prompt):
        """
        Test case for when the email body is shorter than or equal to the configured body length.
        """
        email_body = "Short email body."
        customer_uuid = "customer123"
        application_uuid = "app123"

        result = generate_detailed_summary(email_body, customer_uuid, application_uuid)
        assert result == email_body


    @patch('EmailApp.utils.PromptDaoImpl.fetch_prompt_by_category_filter_json')
    @patch('EmailApp.utils.LLMChain')
    def test_llm_json_decode_error(self, mock_query, mock_fetch_prompt):
        """
        Test case for JSON decoding error in LLM response.
        """
        email_body = "This is a long email body with many words."*50
        customer_uuid = "customer123"
        application_uuid = "app123"
        mock_fetch_prompt.return_value = "Mock prompt"
        mock_query.return_value.query.return_value = "Invalid JSON"

        result = generate_detailed_summary(email_body, customer_uuid, application_uuid)
        self.assertIsNone(result)

    @patch('EmailApp.utils.PromptDaoImpl.fetch_prompt_by_category_filter_json')
    @patch('EmailApp.utils.LLMChain')
    def test_llm_exception_handling(self, mock_query, mock_fetch_prompt):
        """
        Test case for generic exceptions during LLM query.
        """
        email_body = "This is a long email body with many words."*50
        customer_uuid = "customer123"
        application_uuid = "app123"
        mock_fetch_prompt.return_value = "Mock prompt"
        mock_query.return_value.query.side_effect = Exception("LLM error")

        result = generate_detailed_summary(email_body, customer_uuid, application_uuid)
        self.assertIsNone(result)
class TestHitAndRetryWithNewToken(unittest.TestCase):
    @patch("EmailApp.utils.retry_by_generating_token")
    @patch("EmailApp.utils.call_api")
    @patch("EmailApp.utils.KeyVaultService")
    @patch("EmailApp.utils.logger")
    def test_hit_and_retry_with_new_token_successful_response(self, mock_logger, mock_KeyVaultService,
                                                              mock_call_api, mock_retry_by_generating_token):
        """Test successful API call without needing to retry."""
        # Arrange
        secret_name = "test-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"
        end_point = "https://graph.microsoft.com/v1.0/me/"
        json_data = {"key": "value"}

        secret_details = {"access_token": "test-access-token"}
        response_mock = MagicMock()
        response_mock.ok = True

        # Mock KeyVaultService
        mock_KeyVaultService().get_secret_details_from_redis_or_keyvault.return_value = secret_details

        # Mock call_api
        mock_call_api.return_value = response_mock

        # Act
        result = hit_and_retry_with_new_token(end_point, secret_name, microsoft_client_id, microsoft_tenant_id,
                                              json_data)

        # Assert
        self.assertEqual(result, response_mock)
        mock_call_api.assert_called_once_with(
            headers={"Authorization": f"Bearer {secret_details['access_token']}"},
            endpoint=end_point,
            json_data=json_data,
            method="GET"
        )
        mock_logger.info.assert_any_call("Successfully fetched response from graph API")

    @patch("EmailApp.utils.retry_by_generating_token")
    @patch("EmailApp.utils.call_api")
    @patch("EmailApp.utils.KeyVaultService")
    @patch("EmailApp.utils.logger")
    def test_hit_and_retry_with_new_token_unauthorized_retry(self, mock_logger, mock_KeyVaultService,
                                                             mock_call_api, mock_retry_by_generating_token):
        """Test API call retries after receiving 401 Unauthorized response."""
        # Arrange
        secret_name = "test-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"
        end_point = "https://graph.microsoft.com/v1.0/me/"
        json_data = {"key": "value"}

        secret_details = {"access_token": "test-access-token"}
        exception = CustomException(status_code=401,
                                    detail=json.dumps({"error": {"code": "InvalidAuthenticationToken"}}))

        # Mock KeyVaultService
        mock_KeyVaultService().get_secret_details_from_redis_or_keyvault.return_value = secret_details

        # Mock call_api to raise exception
        mock_call_api.side_effect = exception

        # Mock retry_by_generating_token
        retry_response_mock = MagicMock()
        mock_retry_by_generating_token.return_value = retry_response_mock

        # Act
        result = hit_and_retry_with_new_token(end_point, secret_name, microsoft_client_id, microsoft_tenant_id,
                                              json_data)

        # Assert
        self.assertEqual(result, retry_response_mock)
        mock_call_api.assert_called_once()
        mock_retry_by_generating_token.assert_called_once_with(
            end_point, json_data, "GET", secret_name, secret_details, microsoft_client_id, microsoft_tenant_id
        )

    @patch("EmailApp.utils.retry_by_generating_token")
    @patch("EmailApp.utils.call_api")
    @patch("EmailApp.utils.KeyVaultService")
    @patch("EmailApp.utils.logger")
    def test_hit_and_retry_with_new_token_non_401_exception(self, mock_logger, mock_KeyVaultService,
                                                            mock_call_api, mock_retry_by_generating_token):
        """Test API call raises exception for non-401 errors."""
        # Arrange
        secret_name = "test-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"
        end_point = "https://graph.microsoft.com/v1.0/me/"
        json_data = {"key": "value"}

        secret_details = {"access_token": "test-access-token"}
        exception = CustomException(status_code=500, detail="Internal Server Error")

        # Mock KeyVaultService
        mock_KeyVaultService().get_secret_details_from_redis_or_keyvault.return_value = secret_details

        # Mock call_api to raise exception
        mock_call_api.side_effect = exception

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            hit_and_retry_with_new_token(end_point, secret_name, microsoft_client_id, microsoft_tenant_id, json_data)

        self.assertEqual(context.exception.status_code, 500)
        mock_call_api.assert_called_once()
        mock_retry_by_generating_token.assert_not_called()


class TestRetryByGeneratingToken(unittest.TestCase):
    @patch("EmailApp.utils.call_api")
    @patch("EmailApp.utils.update_token_in_secret")
    @patch("EmailApp.utils.get_access_token")
    @patch("EmailApp.utils.logger")
    def test_retry_by_generating_token_successful(self, mock_logger, mock_get_access_token,
                                                  mock_update_token_in_secret, mock_call_api):
        """Test retry is successful after generating a new token."""
        # Arrange
        end_point = "https://graph.microsoft.com/v1.0/me/"
        json_data = {"key": "value"}
        method = "POST"
        secret_name = "test-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"
        secret_details = {
            "client_secret": "test-client-secret",
            "access_token": "old-access-token"
        }

        new_access_token = "new-access-token"
        updated_secret_details = {
            "access_token": new_access_token
        }

        response_mock = MagicMock()
        response_mock.ok = True

        # Mock get_access_token
        mock_get_access_token.return_value = new_access_token

        # Mock update_token_in_secret
        mock_update_token_in_secret.return_value = updated_secret_details

        # Mock call_api
        mock_call_api.return_value = response_mock

        # Act
        result = retry_by_generating_token(
            end_point, json_data, method, secret_name, secret_details, microsoft_client_id, microsoft_tenant_id
        )

        # Assert
        self.assertEqual(result, response_mock)
        mock_get_access_token.assert_called_once_with(
            client_secret=secret_details["client_secret"],
            microsoft_client_id=microsoft_client_id,
            microsoft_tenant_id=microsoft_tenant_id
        )
        mock_update_token_in_secret.assert_called_once_with(
            secret_name, new_access_token, secret_details
        )
        mock_call_api.assert_called_once_with(
            headers={"Authorization": f"Bearer {new_access_token}"},
            endpoint=end_point,
            json_data=json_data,
            method=method
        )
        mock_logger.info.assert_any_call("Successfully fetched response from graph API")

    @patch("EmailApp.utils.call_api")
    @patch("EmailApp.utils.update_token_in_secret")
    @patch("EmailApp.utils.get_access_token")
    @patch("EmailApp.utils.logger")
    def test_retry_by_generating_token_failure(self, mock_logger, mock_get_access_token,
                                               mock_update_token_in_secret, mock_call_api):
        """Test retry fails and raises a CustomException."""
        # Arrange
        end_point = "https://graph.microsoft.com/v1.0/me/"
        json_data = {"key": "value"}
        method = "POST"
        secret_name = "test-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"
        secret_details = {
            "client_secret": "test-client-secret",
            "access_token": "old-access-token"
        }

        new_access_token = "new-access-token"
        updated_secret_details = {
            "access_token": new_access_token
        }

        response_mock = MagicMock()
        response_mock.ok = False
        response_mock.text = "Error response"

        # Mock get_access_token
        mock_get_access_token.return_value = new_access_token

        # Mock update_token_in_secret
        mock_update_token_in_secret.return_value = updated_secret_details

        # Mock call_api
        mock_call_api.return_value = response_mock

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            retry_by_generating_token(
                end_point, json_data, method, secret_name, secret_details, microsoft_client_id, microsoft_tenant_id
            )

        self.assertIn("API hit failed", str(context.exception))
        self.assertEqual(context.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_call_api.assert_called_once_with(
            headers={"Authorization": f"Bearer {new_access_token}"},
            endpoint=end_point,
            json_data=json_data,
            method=method
        )
        mock_logger.error.assert_called_once_with(f"API hit failed: {response_mock.text}")

    @patch("EmailApp.utils.call_api")
    @patch("EmailApp.utils.update_token_in_secret")
    @patch("EmailApp.utils.get_access_token")
    @patch("EmailApp.utils.logger")
    def test_retry_by_generating_token_exception_during_update(self, mock_logger, mock_get_access_token,
                                                               mock_update_token_in_secret, mock_call_api):
        """Test exception is raised if updating token in secret fails."""
        # Arrange
        end_point = "https://graph.microsoft.com/v1.0/me/"
        json_data = {"key": "value"}
        method = "POST"
        secret_name = "test-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"
        secret_details = {
            "client_secret": "test-client-secret",
            "access_token": "old-access-token"
        }

        new_access_token = "new-access-token"

        # Mock get_access_token
        mock_get_access_token.return_value = new_access_token

        # Mock update_token_in_secret to raise an exception
        mock_update_token_in_secret.side_effect = CustomException("Failed to update token in secret")

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            retry_by_generating_token(
                end_point, json_data, method, secret_name, secret_details, microsoft_client_id, microsoft_tenant_id
            )

        self.assertIn("Failed to update token in secret", str(context.exception))
        mock_get_access_token.assert_called_once_with(
            client_secret=secret_details["client_secret"],
            microsoft_client_id=microsoft_client_id,
            microsoft_tenant_id=microsoft_tenant_id
        )
        mock_update_token_in_secret.assert_called_once_with(
            secret_name, new_access_token, secret_details
        )
        mock_call_api.assert_not_called()


class TestUpdateTokenInSecret(unittest.TestCase):
    @patch("EmailApp.utils.KeyVaultService")
    @patch("EmailApp.utils.logger")
    def test_update_token_in_secret_successful(self, mock_logger, mock_KeyVaultService):
        """Test successful update of token in Azure Key Vault."""
        # Arrange
        secret_name = "test-secret"
        new_token = "new-access-token"
        previous_secret_details = {
            "access_token": "old-access-token",
            "client_secret": "test-client-secret"
        }

        # Mock KeyVaultService
        mock_key_vault_service_instance = mock_KeyVaultService.return_value
        mock_key_vault_service_instance.update_secret_in_redis_keyvault.return_value = None

        # Act
        result = update_token_in_secret(secret_name, new_token, previous_secret_details)

        # Assert
        self.assertEqual(result["access_token"], new_token)
        mock_key_vault_service_instance.update_secret_in_redis_keyvault.assert_called_once_with(
            secret_name, json.dumps(previous_secret_details), expiry_for_redis=3500
        )
        mock_logger.info.assert_any_call("Updating secret with new token")

    @patch("EmailApp.utils.KeyVaultService")
    @patch("EmailApp.utils.logger")
    def test_update_token_in_secret_secret_not_found(self, mock_logger, mock_KeyVaultService):
        """Test ResourceNotFoundException is raised when the secret does not exist."""
        # Arrange
        secret_name = "test-secret"
        new_token = "new-access-token"
        previous_secret_details = {
            "access_token": "old-access-token",
            "client_secret": "test-client-secret"
        }

        # Mock KeyVaultService to raise ResourceNotFoundException
        mock_key_vault_service_instance = mock_KeyVaultService.return_value
        mock_key_vault_service_instance.update_secret_in_redis_keyvault.side_effect = ResourceNotFoundException(
            f"Secret {secret_name} not found"
        )

        # Act & Assert
        with self.assertRaises(ResourceNotFoundException) as context:
            update_token_in_secret(secret_name, new_token, previous_secret_details)

        self.assertIn(f"Secret {secret_name} not found", str(context.exception))
        mock_key_vault_service_instance.update_secret_in_redis_keyvault.assert_called_once_with(
            secret_name, json.dumps(previous_secret_details), expiry_for_redis=3500
        )
        mock_logger.info.assert_any_call("Updating secret with new token")

    @patch("EmailApp.utils.KeyVaultService")
    @patch("EmailApp.utils.logger")
    def test_update_token_in_secret_logs_info(self, mock_logger, mock_KeyVaultService):
        """Test logger is called with correct messages."""
        # Arrange
        secret_name = "test-secret"
        new_token = "new-access-token"
        previous_secret_details = {
            "access_token": "old-access-token",
            "client_secret": "test-client-secret"
        }

        # Mock KeyVaultService
        mock_KeyVaultService.return_value.update_secret_in_redis_keyvault.return_value = None

        # Act
        update_token_in_secret(secret_name, new_token, previous_secret_details)

        # Assert
        mock_logger.info.assert_any_call("In microsoft_graph_utils :: update_token_in_secret")
        mock_logger.info.assert_any_call("Updating secret with new token")


class TestGetAccessToken(unittest.TestCase):
    @patch("EmailApp.utils.ConfidentialClientApplication")
    @patch("EmailApp.utils.logger")
    def test_get_access_token_successful(self, mock_logger, mock_ConfidentialClientApplication):
        """Test successful generation of an access token."""
        # Arrange
        client_secret = "test-client-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"
        expected_token = "new-access-token"

        # Mock ConfidentialClientApplication
        mock_client_instance = mock_ConfidentialClientApplication.return_value
        mock_client_instance.acquire_token_for_client.return_value = {"access_token": expected_token}

        # Act
        result = get_access_token(client_secret, microsoft_client_id, microsoft_tenant_id)

        # Assert
        self.assertEqual(result, expected_token)
        mock_ConfidentialClientApplication.assert_called_once_with(
            microsoft_client_id,
            authority=f"https://login.microsoftonline.com/{microsoft_tenant_id}",
            client_credential=client_secret
        )
        mock_client_instance.acquire_token_for_client.assert_called_once_with(
            scopes=["https://graph.microsoft.com/.default"]
        )
        mock_logger.info.assert_any_call("Token Generated Successfully")

    @patch("EmailApp.utils.ConfidentialClientApplication")
    @patch("EmailApp.utils.logger")
    def test_get_access_token_failure_invalid_token(self, mock_logger, mock_ConfidentialClientApplication):
        """Test failure when token generation does not return an access token."""
        # Arrange
        client_secret = "test-client-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"

        # Mock ConfidentialClientApplication
        mock_client_instance = mock_ConfidentialClientApplication.return_value
        mock_client_instance.acquire_token_for_client.return_value = {
            "error_description": "Invalid client credentials"}

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            get_access_token(client_secret, microsoft_client_id, microsoft_tenant_id)

        self.assertIn("Unable to generate access token", str(context.exception))
        mock_client_instance.acquire_token_for_client.assert_called_once_with(
            scopes=["https://graph.microsoft.com/.default"]
        )
        mock_logger.info.assert_called_once_with("In microsoft_graph_utils :: get_access_token")

    @patch("EmailApp.utils.ConfidentialClientApplication")
    @patch("EmailApp.utils.logger")
    def test_get_access_token_exception(self, mock_logger, mock_ConfidentialClientApplication):
        """Test failure when an exception is raised during token generation."""
        # Arrange
        client_secret = "test-client-secret"
        microsoft_client_id = "test-client-id"
        microsoft_tenant_id = "test-tenant-id"

        # Mock ConfidentialClientApplication to raise an exception
        mock_ConfidentialClientApplication.side_effect = Exception("Unexpected error")

        # Act & Assert
        with self.assertRaises(CustomException) as context:
            get_access_token(client_secret, microsoft_client_id, microsoft_tenant_id)

        self.assertIn("Unable to generate access token", str(context.exception))
        mock_logger.info.assert_called_once_with("In microsoft_graph_utils :: get_access_token")


class TestCallApi(unittest.TestCase):
    @patch("EmailApp.utils.requests.get")
    def test_call_api_get_success(self, mock_get):
        """Test successful GET API call."""
        endpoint = "http://example.com/api/resource"
        params = {"key": "value"}
        headers = {"Authorization": "Bearer token"}

        # Mock response
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        # Call function
        response = call_api(method="GET", endpoint=endpoint, params=params, headers=headers)

        # Assert
        mock_get.assert_called_once_with(endpoint, params=params, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

    @patch("EmailApp.utils.requests.post")
    def test_call_api_post_success(self, mock_post):
        """Test successful POST API call."""
        endpoint = "http://example.com/api/resource"
        json_data = {"name": "test"}
        headers = {"Authorization": "Bearer token"}

        # Mock response
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "name": "test"}
        mock_post.return_value = mock_response

        # Call function
        response = call_api(method="POST", endpoint=endpoint, json_data=json_data, headers=headers)

        # Assert
        mock_post.assert_called_once_with(endpoint, params=None, data=None, json=json_data, headers=headers, auth=None)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"id": 1, "name": "test"})

    def test_call_api_invalid_method(self):
        """Test invalid HTTP method."""
        endpoint = "http://example.com/api/resource"
        with self.assertRaises(ValueError) as context:
            call_api(method="PATCH", endpoint=endpoint)

        self.assertEqual(str(context.exception), "Unsupported HTTP method: PATCH")

    def test_call_api_invalid_endpoint(self):
        """Test invalid endpoint."""
        with self.assertRaises(InvalidValueProvidedException) as context:
            call_api(method="GET", endpoint="")

        self.assertEqual(context.exception.detail, ErrorMessages.INVALID_ENDPOINT)

    @patch("EmailApp.utils.requests.get")
    def test_call_api_client_error(self, mock_get):
        """Test API call with client error (4xx)."""
        endpoint = "http://example.com/api/resource"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        with self.assertRaises(CustomException) as context:
            call_api(method="GET", endpoint=endpoint)

        self.assertEqual(context.exception.detail, "Bad Request")
        self.assertEqual(context.exception.status_code, 400)

    @patch("EmailApp.utils.requests.get")
    def test_call_api_request_exception(self, mock_get):
        """Test RequestException during API call."""
        endpoint = "http://example.com/api/resource"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        with self.assertRaises(requests.exceptions.RequestException) as context:
            call_api(method="GET", endpoint=endpoint)

        self.assertIn("Connection error", str(context.exception))

    @patch("EmailApp.utils.requests.get")
    def test_call_api_unexpected_exception(self, mock_get):
        """Test unexpected exception during API call."""
        endpoint = "http://example.com/api/resource"
        mock_get.side_effect = Exception("Unexpected error")

        with self.assertRaises(Exception) as context:
            call_api(method="GET", endpoint=endpoint)

        self.assertIn("Unexpected error", str(context.exception))


