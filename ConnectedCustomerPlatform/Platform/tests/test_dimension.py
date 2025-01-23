import json
import uuid

from dataclasses import asdict
from unittest.mock import MagicMock, patch

from django.forms import model_to_dict
from io import BytesIO
import pandas as pd
from django.test import TestCase

from django.urls import reverse
from django.utils.datetime_safe import datetime
from rest_framework import status
from rest_framework.test import APIClient

from DatabaseApp.models import DimensionsView
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from ConnectedCustomerPlatform.responses import CustomResponse
from EmailApp.constant.constants import BULK_IMPORT_EXCEL_FILE, FileExtensions

from Platform.constant.constants import ChromaExcelSheet, SPREAD_SHEET_MACRO_ENABLED, ChromaUtils

from Platform.constant.success_messages import SuccessMessages
from Platform.constant.error_messages import ErrorMessages
from Platform.services.impl.dimension_service_impl import DimensionServiceImpl
from Platform.tests.test_data import create_dimension_test_data, insert_test_intents


class BaseTestCase(TestCase):
    # Creates dummy data and setting up required variables
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Import test data from test_data module
        (self.dimension_type,
         self.parent_dimension,
         self.parent_dimension_mapping,
         self.dimension,
         self.dimension_mapping
         ) = create_dimension_test_data()

        self.headers = {
            'customer-uuid': self.dimension_mapping.customer_uuid_id,
            'application-uuid': self.dimension_mapping.application_uuid_id,
            'user-uuid': self.dimension_mapping.created_by,
        }


####
# =========================== Tests for DimensionViewSet ===================================
####
class DimensionViewSetTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.dimension_type_uuid = self.dimension_type.dimension_type_uuid
        self.description = "Description for Geography dimension"
        self.parent_mapping_uuid = self.parent_dimension_mapping.mapping_uuid
        self.mapping_uuid = self.dimension_mapping.mapping_uuid
        self.dimensions_view = DimensionsView(
                mapping_uuid="mapping_uuid",
                dimension_uuid="uuid-reset-password",
                dimension_name="Reset Password",
                dimension_description="A request to reset a password",
                customer_uuid=self.dimension_mapping.customer_uuid_id,
                application_uuid=self.dimension_mapping.application_uuid_id,
                dimension_type_name=self.dimension_type.dimension_type_name,
                dimension_type_uuid=self.dimension_type.dimension_type_uuid,
                is_default=False,
                dimension_details_json={},
                inserted_ts = datetime.now(),
                updated_ts = datetime.now(),
                child_dimensions=[]
            )
        self.uploading_excel_endpoint = reverse('Platform:upload_examples_to_chromadb')
        self.download_intents_endpoint = reverse('Platform:download_training_phrases')
        self.resolve_duplicates_endpoint = reverse('Platform:resolve_duplicates')
        self.download_template_endpoint = reverse('Platform:download_template')
        self.dimension_service_impl = DimensionServiceImpl()
        self.sample_df = pd.DataFrame({
            0: ["ID", "Training Phrases", "Intent 1", "Sub Intent 1"],
            1: [1, "Phrase 1", "Order", None],
            2: [2, "Phrase 2", "Intent", "Sub Intent"]
        })

    ###
    # ========= Tests for "add dimension" API ==========
    ###

    # 1. With valid payload and headers - without parent_dimension_name
    def test_add_dimension_success(self):
        payload = {
            "dimension_name": "USA",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description,
            "utterances": ["Can you please check the status of my order?"]
        }

        response = self.client.post(reverse('Platform:dimension'), payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(SuccessMessages.ADD_DIMENSION_SUCCESS, response.data.get('result'))

    # 2. With valid payload and headers - with parent_dimension_name
    def test_add_dimension_success_with_parent_dimension_name_tp_duplicate(self):
        payload = {
            "dimension_name": "Intent",
            "parent_dimension_name": "ParentIntent",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description,
            "utterances":["tp1"]
        }
        similar_phrase = {"metadata":{"category":"intent_classification","INTENT,parentintent":True,"SUBINTENT,parentintent,intent":True,"is_subintent":True},"document_id":str(uuid.uuid4())}
        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',
                   return_value=["embeddings"]) as mock_embeddings:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',
                       return_value=[[similar_phrase]]) as mock_embeddings:

                response = self.client.post(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(SuccessMessages.ADD_DIMENSION_SUCCESS, response.data.get('result'))

    def test_add_dimension_success_with_parent_dimension_name(self):
        payload = {
            "dimension_name": "Intent",
            "parent_dimension_name": "ParentIntent",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description,
            "utterances":["tp1"]
        }
        similar_phrase = {"metadata":{"category":"intent_classification","INTENT,intent":True,"is_subintent":False},"document_id":str(uuid.uuid4())}
        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',
                   return_value=["embeddings"]) as mock_embeddings:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',
                       return_value=[[similar_phrase]]) as mock_embeddings:

                response = self.client.post(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(SuccessMessages.ADD_DIMENSION_SUCCESS, response.data.get('result'))


    # 3. Dimension already exists
    def test_add_dimension_dimension_already_exists(self):
        payload = {
            "dimension_name": "INDIA",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }

        response = self.client.post(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(ErrorMessages.DIMENSION_EXISTS, response.data.get('result'))

    # 4. Invalid payload
    def test_add_dimension_invalid_payload(self):
        payload = {
            "dimension_name": "",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }

        response = self.client.post(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('This field may not be blank.', str(response.data.get('result')['dimension_name']))


    ###
    # ========= Tests for "edit dimension" API ==========
    ###

    # 1. Edit dimension success - without parent dimension
    def test_edit_dimension_success(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_name": "TAMILNADU",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description,
            "utterances": [{
                "id": None,
                "utterance": "Resolved"
            }, ]
        }

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings') as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:
                with patch(
                        'Platform.services.impl.dimension_service_impl.ChromaVectorStore.upload_utterances_at_once',return_value=1) as mock_upload:



                    response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers, format='json')

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(SuccessMessages.UPDATE_DIMENSION_SUCCESS, response.data.get('result'))

    # 2. Edit dimension success - with parent dimension
    def test_edit_dimension_success_with_parent_dimension_name(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "parent_dimension_name": "INDIA",
            "dimension_name": "DELHI",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }
        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings') as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:

                response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_chroma.assert_called()
        mock_chroma_update.assert_called()

        self.assertEqual(SuccessMessages.UPDATE_DIMENSION_SUCCESS, response.data.get('result'))

    # 3. Dimension already exists
    def test_edit_dimension_dimension_exists(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "parent_dimension_name":"INDIA",
            "dimension_name": "TELANGANA",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings') as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:

                response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(ErrorMessages.DIMENSION_EXISTS, response.data.get('result'))

    # # 4. Children exist for parent dimension
    # def test_edit_dimension_children_exist(self):
    #     payload = {
    #         "mapping_uuid": self.parent_mapping_uuid,
    #         "dimension_name": "USA",
    #         "dimension_type_uuid": self.dimension_type_uuid,
    #         "description": self.description
    #     }
    #
    #     response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers)
    #
    #     # Check if the response is successful
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     self.assertEqual(ErrorMessages.DIMENSION_HAS_DEPENDENTS, response.data.get('result'))

    # 5. Invalid mapping_uuid
    def test_edit_dimension_invalid_mapping_uuid(self):
        payload = {
            "mapping_uuid": str(uuid.uuid4()),
            "dimension_name": "USA",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }

        response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(ErrorMessages.DIMENSION_NOT_FOUND, response.data.get('result'))

    # 6. Invalid payload
    def test_edit_dimension_invalid_payload(self):
        payload = {
            "mapping_uuid": str(uuid.uuid4()),
            "dimension_name": "",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }

        response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('This field may not be blank.', str(response.data.get('result')['dimension_name']))

    # 7. Edit utterance failed
    def test_edit_dimension_edit_utterance_failed(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_name": "INTENT",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description,
            "utterances": [{
                "id": uuid.uuid4(),
                "utterance": "Resolved"
            }, ]
        }
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,otherintent":True,"is_subintent":False}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings') as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:
                with patch(
                        'Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
                    with patch(
                            'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id',side_effect=Exception()) as update_metadata:
                                response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers, format='json')
        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(ErrorMessages.UPDATE_UTTERANCE_FAILED, response.data.get('result'))
        mock_chroma.assert_called()
        mock_fetch_existing_records.assert_called()
        mock_chroma_update.assert_called()
        update_metadata.assert_called()

    def test_edit_dimension_edit_utterance_success_other_intents(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_name": "INTENT",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description,
            "utterances": [{
                "id": uuid.uuid4(),
                "utterance": "Resolved"
            }, ]
        }
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,otherintent":True,"is_subintent":False}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings') as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:
                with patch(
                        'Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
                    with patch(
                            'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as update_metadata:
                                response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers, format='json')
        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_chroma.assert_called()
        mock_fetch_existing_records.assert_called()
        mock_chroma_update.assert_called()
        update_metadata.assert_called()


    def test_edit_dimension_dimension_success_metadata_updated(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_name": "INTENT",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,ap":True,"INTENT,otherintent":True,"is_subintent":False}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}


        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings',return_value=training_phrase) as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:
                with patch(
                        'Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
                    with patch(
                            'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as update_metadata:
                                response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers, format='json')
        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_chroma.assert_called()
        mock_chroma_update.assert_called()


    def test_edit_dimension_dimension_success_metadata_updated_parent_dimension(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_name": "INTENT",
            "parent_dimension_name":"parentIntent",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description
        }
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,ap":True,"INTENT,otherintent":True,"SUBINTENT,parentintent,ap":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}


        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings',return_value=training_phrase) as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:
                    response = self.client.put(reverse('Platform:dimension'), data=payload, headers=self.headers, format='json')
        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_chroma.assert_called()
        mock_chroma_update.assert_called()



    def test_edit_dimension_edit_utterance_success(self):
        payload = {
            "mapping_uuid": self.mapping_uuid,
            "dimension_name": "INTENT",
            "dimension_type_uuid": self.dimension_type_uuid,
            "description": self.description,
            "utterances": [{
                "id": uuid.uuid4(),
                "utterance": "Resolved"
            }, ]
        }
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"is_subintent":False}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings') as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:
                with patch(
                        'Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
                    with patch(
                            'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as update_metadata:
                        with patch(
                                'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_email_document_embedding') as update_embedding:
                            with patch('Platform.services.impl.dimension_service_impl.DimensionCAMDaoImpl.save_dimension_mapping') as mock_save_mapping:
                                with patch(
                                        'Platform.services.impl.dimension_service_impl.DimensionServiceImpl.add_training_phrase_to_chroma',return_value=(1,1,[])) as mock_adding:
                                    response = self.client.put(reverse('dimension'), data=payload, headers=self.headers, format='json')

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_chroma.assert_called()
        mock_save_mapping.assert_called()
        mock_fetch_existing_records.assert_called()
        mock_chroma_update.assert_called()


    ###
    # ========= Tests for "get dimensions by type" API ==========
    ###

    # 1. Get dimensions by dimension type success
    @patch('Platform.services.impl.dimension_service_impl.DimensionDaoImpl.fetch_parent_and_child_dimension_details')
    def test_get_dimensions_by_type_success(self,mock_dimension_dao):
        # Send a POST request to the endpoint with the specified data and headers
        mock_dimension_dao.return_value = [model_to_dict(self.dimensions_view)]

        response = self.client.post(
            reverse('Platform:dimensions_by_type', args=[self.dimension_type_uuid]),
            headers=self.headers,
            data={
                "params": {
                    "total_entry_per_page": 5,
                    "page_number": 1
                }
            }
            ,format='json'
        )

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Parse the response data
        response_data = response.json()

        # Check if 'result' exists in the response and contains data
        result = response_data.get('result', [])
        if result:
            # Assert that the first item in 'result' contains the key 'dimension_name'
            self.assertIn('dimension_name', result.get('data')[0].keys())
        else:
            # Fail the test if 'result' is empty when it shouldn't be
            self.fail("The 'result' field is empty or missing in the response.")

    ###
    # ========= Tests for "get dimension by id" API ==========
    ###

    # 1. Get dimension by mapping uuid success
    def test_get_dimension_by_mapping_uuid_success(self):
        response = self.client.get(reverse('Platform:dimension_by_id', args=[self.mapping_uuid]), headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        if response_data.get('result') is not None:
            self.assertIn('dimension_name', list(response_data.get('result').keys()))

    ###
    # ========= Tests for "get dimension by id" API ==========
    ###

    # 1. Delete dimension by mapping uuid success
    def test_delete_dimension_by_mapping_uuid_success(self):
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,india":True,"INTENT,intent2":True,"SUBINTENT,india,ap":True,"is_subintent":True},{"category":"intent_classification","INTENT,india":True,"SUBINTENT,india,ap":True,"is_subintent":True}],"documents":["document","document1"],"embeddings":["embeddings","embeddings2"],"ids":[str(uuid.uuid4()),str(uuid.uuid4())]}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_records_by_metadata_include_embeddings',return_value=training_phrase) as mock_chroma:
            with patch(
                    'Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_training_phrases') as mock_chroma_update:
                with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.delete_record_by_ids') as mock_delete:

                    response = self.client.delete(reverse('Platform:dimension_by_id', args=[self.parent_mapping_uuid]), headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(SuccessMessages.DELETE_DIMENSION_SUCCESS, response.data.get('result'))

    # 2. Invalid mapping uuid
    def test_delete_dimension_invalid_mapping_uuid(self):
        response = self.client.delete(reverse('Platform:dimension_by_id', args=[str(uuid.uuid4())]), headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(ErrorMessages.DIMENSION_NOT_FOUND, response.data.get('result'))

    # 3. Children exist for parent dimension
    # def test_delete_dimension_children_exist(self):
    #     response = self.client.delete(reverse('Platform:dimension_by_id', args=[self.parent_mapping_uuid]), headers=self.headers)
    #
    #     # Check if the response is successful
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     self.assertEqual(ErrorMessages.DIMENSION_HAS_DEPENDENTS, response.data.get('result'))

    ###
    # ========= Tests for "get geography dimensions" API ==========
    ###

    # 1. Get geography dimensions - Country success
    def test_get_geography_dimensions_country_success(self):
        response = self.client.get(reverse('Platform:geography_dimensions'), headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        if len(response_data.get('result')) > 0:
            self.assertIn('dimension_name', list(response_data.get('result')[0].keys()))

    # 2. Get geography dimensions - States success
    def test_get_geography_dimensions_states_success(self):
        response = self.client.get(reverse('Platform:geography_dimensions_by_id', args=[self.parent_dimension.dimension_uuid]), headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        if len(response_data.get('result')) > 0:
            self.assertIn('dimension_name', list(response_data.get('result')[0].keys()))


    ###
    # ========= Tests for "get country state dropdown" API ==========
    ###
    # 1. Get list of all countries success
    def test_get_country_state_dropdown_success_countries(self):
        response = self.client.get(reverse('Platform:country_state_dropdown'), headers=self.headers)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 2. Get list of all states under a country with parent_dimension_uuid
    def test_get_country_state_dropdown_states(self):
        response = self.client.get(
            reverse('Platform:country_state_dropdown_by_id',
                    args=[self.parent_dimension.dimension_uuid]),
                    headers=self.headers
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _create_mock_excel_file(self):
        # Create a sample Excel file with the required structure
        data = [
        [None, None, "Intent 1", None, "Intent 2", None, "Intent 3", None, "Intent 4", None, "Intent 5", None],
        ["ID", "Training Phrases", "Intent 1", "Sub Intent 1", "Intent 2", "Sub Intent 2", "Intent 3", "Sub Intent 3", "Intent 4", "Sub Intent 4", "Intent 5", "Sub Intent 5"],
        [1, "hello", "order_status", "stock_status", None, None, None, None, None, None, None, None],
    ]
        df = pd.DataFrame(data)

        # Write to a BytesIO stream as an Excel file
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=ChromaExcelSheet.TRAINING_PHRASES.value)

        excel_buffer.seek(0)
        return excel_buffer, df

    def test_missing_file_in_request(self):
        response = self.client.post(self.uploading_excel_endpoint, data={}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_file_type(self):
        mock_file = MagicMock()
        mock_file.content_type = 'application/vnd.ms-excel'
        mock_file.name = 'invalid_file.xlsx'

        data = {BULK_IMPORT_EXCEL_FILE: mock_file}
        response = self.client.post(self.uploading_excel_endpoint, data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_uuids_in_headers(self):
        mock_file = MagicMock()
        mock_file.content_type = SPREAD_SHEET_MACRO_ENABLED
        mock_file.name = f'test_file.{FileExtensions.XLSM.value}'

        data = {BULK_IMPORT_EXCEL_FILE: mock_file}
        response = self.client.post(self.uploading_excel_endpoint, data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.update_the_metadatas_with_document_ids',return_value = 2)
    @patch("Platform.services.impl.dimension_service_impl.DimensionServiceImpl._DimensionServiceImpl__validate_dropdowntable_sheet", return_value = None)
    @patch("Platform.services.impl.dimension_service_impl.update_or_skip_examples")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.upload_utterances_at_once', return_value = 1)

    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.embed_query_list', return_value = [])

    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.find_similar_records', return_value = [[]])

    @patch("Platform.services.impl.dimension_service_impl.DimensionServiceImpl._DimensionServiceImpl__read_excel")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application', return_value = "email_12345")
    @patch('Platform.views.dimension.validate_uuids_dict', return_value = None)
    def test_upload_examples_success(self, mock_validate_uuids, mock_collection_name,
                                     mock_read_excel, find_similar_records, embed_query_list,
                                     mock_upload_utterances_at_once, mock_update_or_skip, mock_validate_dropdownsheet, mock_update_the_metadatas_with_document_ids):

        application, customer = insert_test_intents()
        headers = {
            'customer-uuid': customer.cust_uuid,
            'application-uuid': application.application_uuid,
        }
        dimension_wise_count = {'order_status': {'order_status': 1, 'stock_status': 1}}
        filtered_queries = filtered_embeddings  = metadata_list = []
        doc_ids_list = ["id1"]
        updated_doc_ids = ["id2"]
        updated_metadata_list = []
        error_rows = []
        mock_update_or_skip.return_value =  {
        ChromaUtils.FILTERED_QUERIES.value: filtered_queries,
        ChromaUtils.FILTERED_EMBEDDINGS.value: filtered_embeddings,
        ChromaUtils.DOC_IDS_LIST.value: doc_ids_list,
        ChromaUtils.METADATA_LIST.value: metadata_list,
       ChromaUtils.DIMENSION_WISE_COUNT.value: dimension_wise_count,
        ChromaUtils.UPDATED_DOC_IDS.value: updated_doc_ids,
        ChromaUtils.UPDATED_METADATA_LIST.value: updated_metadata_list,
       ChromaUtils.ERROR_ROWS.value: error_rows,
    }
        file, df = self._create_mock_excel_file()
        mock_excel_file = file
        mock_file = MagicMock()
        mock_file.content_type = SPREAD_SHEET_MACRO_ENABLED
        mock_file.name = f'test_file.{FileExtensions.XLSM.value}'
        mock_file.read.return_value = mock_excel_file.read()
        mock_read_excel.return_value = df

        data = {BULK_IMPORT_EXCEL_FILE: mock_file}

        response = self.client.post(self.uploading_excel_endpoint, data=data, format='multipart', headers = headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('Platform.services.impl.dimension_service_impl.pd.read_excel')
    def test_read_excel_success(self, mock_read_excel):
        mock_read_excel.return_value = self.sample_df
        result = self.dimension_service_impl._DimensionServiceImpl__read_excel(MagicMock())
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape, self.sample_df.shape)

    @patch('Platform.services.impl.dimension_service_impl.pd.read_excel')
    def test_read_excel_error(self, mock_read_excel):
        mock_read_excel.side_effect = Exception("File error")
        result = self.dimension_service_impl._DimensionServiceImpl__read_excel(MagicMock())
        self.assertIsInstance(result, CustomResponse)
        self.assertEqual(result.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_delete_rows_by_row_numbers(self):
        df = self.sample_df.copy()
        self.dimension_service_impl._DimensionServiceImpl__delete_rows_by_row_numbers(df, [1])
        expected_df = self.sample_df.drop(index=[1]).reset_index(drop=True)
        pd.testing.assert_frame_equal(df, expected_df)


    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_records_by_metadata')
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application',
        return_value="email_12345")
    @patch('Platform.views.dimension.validate_uuids_dict', return_value=None)
    def test_download_intents_success(self, mock_validate_uuids, mock_get_chroma_collection_name_by_customer_application,
                               mock_get_records_by_metadata):

        mock_get_records_by_metadata.return_value = {
            "metadatas" : [
                {
                    'INTENT,returns': True,
                    'SUBINTENT,returns,refund': True,
                    'SUBINTENT,returns,return_policy': True,
                    'is_subintent': True,

                },
                {
                    'INTENT,order_status': True,
                    'SUBINTENT,order_status,stock_status': True,
                    'is_subintent': True,
                }
            ],
            "documents"  : [
                "TP1",
                "TP2"
            ]
        }
        response = self.client.get(self.download_intents_endpoint, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    @patch("Platform.services.impl.dimension_service_impl.pd.DataFrame")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_records_by_metadata')
    @patch(
        'AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application',
        return_value="email_12345")
    @patch('Platform.views.dimension.validate_uuids_dict', return_value=None)
    def test_download_intents_failure(self, mock_validate_uuids_dict, mock_chroma_collection_name, mock_records, mock_df):
        mock_records.return_value = {
            "metadatas": [
                {
                    'INTENT,returns': True,
                    'SUBINTENT,returns,refund': True,
                    'SUBINTENT,returns,return_policy': True,
                    'is_subintent': True,

                },
                {
                    'INTENT,order_status': True,
                    'SUBINTENT,order_status,stock_status': True,
                    'is_subintent': True,
                }
            ],
            "documents": [
                "TP1",
                "TP2"
            ]
        }
        mock_df.return_value = None
        response = self.client.get(self.download_intents_endpoint, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    @patch('Platform.views.dimension.validate_uuids_dict', return_value=None)
    def test_resolve_duplicates_invalid_payload(self, mock_validation):

        response = self.client.post(self.resolve_duplicates_endpoint, **self.headers, format= "json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.upsert_utterances_at_once',
        return_value="email_12345")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.embed_query_list',
        return_value="email_12345")
    @patch('AIServices.VectorStore.chromavectorstore.ChromaVectorStore.get_chroma_collection_name_by_customer_application',
        return_value="email_12345")
    @patch('Platform.views.dimension.validate_uuids_dict', return_value=None)
    def test_resolve_duplicates_valid_payload(self, mock_validation, mock_collection_name,mock_embed_query_list ,mock_upsert_utterances_at_once):

        #Insert data into DB
        application, customer = insert_test_intents()

        headers = {
            'customer-uuid':customer.cust_uuid,
            'application-uuid': application.application_uuid,
        }
        data = {'utterances': [
            {'training_phrase_id': 42, 'training_phrase': 'Dear [Customer],\n\nThank you for your follow-up. Your order has been dispatched and is set to arrive by 05/04/2024. We are committed to resolving this as soon as possible and appreciate your patience. If you need any further assistance, feel free to reach out.\n\nThanks once again Kind regards,\n[Your Name]\n[Your Position]', 'reason': 'Duplicate entries found in the sheet.',
             "intent_subintent_map": {
                                 "order_status": [
            "stock_status"
        ]
        }},
            {'training_phrase_id': 205,
             'training_phrase': 'Is the Synco Chair available at any of your locations, or can you tell me where I can find it nearby? I’m having trouble locating it online.',
             'reason': 'Duplicate entry - record exists in ChromaDB.', 'doc_id': '67b14c94-b489-4386-b210-c30957a00bc0'}
        ]
             }
        mock_embed_query_list.return_value = [ [], []]
        mock_upsert_utterances_at_once.return_value = 2

        response = self.client.post(self.resolve_duplicates_endpoint,data= data ,headers = headers,format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_group_error_rows(self):

        error_rows  = [{
            ChromaExcelSheet.TRAINING_PHRASE.value: "Sample Training Phrase"
        }]
        groups = self.dimension_service_impl._DimensionServiceImpl__group_error_rows(error_rows)

        self.assertEqual(len(groups), 1)

    @patch("ce_shared_services.cloud_storage.azure.azure_storage_manager.AzureStorageManager.download_data_with_url")
    @patch('Platform.views.dimension.validate_uuids_dict', return_value=None)
    @patch("ce_shared_services.factory.storage.azure_storage_factory.CloudStorageFactory")
    @patch("django.conf.settings")
    def test_download_template_success(self, mock_settings, mock_cloud_storage_factory, mock_validate_uuids, mock_data):
        # Mock settings
        mock_settings.TRAINING_PHRASES_IMPORT_TEMPLATE = "https://example.com/training_phrases_import_template.xlsm"
        # Mock Azure Manager's download method
        mock_azure_manager = MagicMock()
        mock_azure_manager.download_data_with_url.return_value = b"mock_binary_data"

        # Mock CloudStorageFactory instantiation
        mock_cloud_storage_factory.return_value = mock_azure_manager
        mock_data.return_value = b"mock_binary_data"

        response = self.client.get(self.download_template_endpoint,**self.headers)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("ce_shared_services.cloud_storage.azure.azure_storage_manager.AzureStorageManager.download_data_with_url")
    @patch('Platform.views.dimension.validate_uuids_dict', return_value=None)
    @patch("ce_shared_services.factory.storage.azure_storage_factory.CloudStorageFactory")
    @patch("django.conf.settings")
    def test_download_template_failure(self, mock_settings, mock_cloud_storage_factory, mock_validate_uuids, mock_data):
        # Mock settings
        mock_settings.TRAINING_PHRASES_IMPORT_TEMPLATE = "https://example.com/training_phrases_import_template.xlsm"
        mock_data.side_effect = Exception("Mock download error")

        response = self.client.get(self.download_template_endpoint,**self.headers)


        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_validate_dropdowntable_sheet_success(self):
        # Arrange: Setup valid base intent-sub-intent map and dropdown table DataFrame
        base_intent_sub_intent_map = {
            "INTENT1": ["SUB_INTENT1", "SUB_INTENT2"],
            "INTENT2": ["SUB_INTENT3"],
        }

        # Mock DataFrame for dropdown table
        drop_down_sheet_df = pd.DataFrame({
            "Intent": ["Intent1", "Intent2", None],  # Mock intents in column
            "Intent1": ["Sub_Intent1", "Sub_Intent2", None],
            "Intent2": ["Sub_Intent3", None, None],
        })


        self.dimension_service_impl._DimensionServiceImpl__validate_dropdowntable_sheet(
            drop_down_sheet_df, base_intent_sub_intent_map
        )

    def test_validate_dropdowntable_sheet_invalid_intent_excel(self):

        # Arrange: Setup invalid DataFrame (Intent3 not in base map)
        base_intent_sub_intent_map = {
            "INTENT1": ["SUB_INTENT1", "SUB_INTENT2"],
            "INTENT2": ["SUB_INTENT3"],
        }

        drop_down_sheet_df = pd.DataFrame({
            "Intent": ["Intent1", "Intent3", None],  # Intent3 is invalid
            "Intent1": ["Sub_Intent1", "Sub_Intent2", None],
            "Intent2": ["Sub_Intent3", None, None],
        })

        # Act & Assert: Expect an exception for invalid intent
        with self.assertRaises(CustomException) as context:
            self.dimension_service_impl._DimensionServiceImpl__validate_dropdowntable_sheet(
                drop_down_sheet_df, base_intent_sub_intent_map
            )
    def test_validate_dropdowntable_sheet_no_intent(self):

        # Arrange: Setup invalid DataFrame (Intent3 not in base map)
        base_intent_sub_intent_map = {
            "INTENT1": ["SUB_INTENT1", "SUB_INTENT2"],
            "INTENT2": ["SUB_INTENT3"],
        }

        drop_down_sheet_df = pd.DataFrame({
            "Intent": [],  #No intent present
            "Intent1": [],
            "Intent2": [],
        })

        # Act & Assert: Expect an exception for invalid intent
        with self.assertRaises(CustomException) as context:
            self.dimension_service_impl._DimensionServiceImpl__validate_dropdowntable_sheet(
                drop_down_sheet_df, base_intent_sub_intent_map
            )


    def test_validate_dropdowntable_sheet_invalid_intent_db(self):

        # Arrange: Setup invalid DataFrame (Intent3 not in base map)
        base_intent_sub_intent_map = {
            "INTENT1": ["SUB_INTENT1", "SUB_INTENT2"],
            "INTENT2": ["SUB_INTENT3"],
        }

        # Mock DataFrame for dropdown table
        drop_down_sheet_df = pd.DataFrame({
            "Intent": ["Intent1", "Intent3", None],  # Mock intents in column
            "Intent1": ["Sub_Intent1", "Sub_Intent2", "Sub_Intent5"],
            "Intent3": ["Sub_Intent4", None, None],
        })

        # Act & Assert: Expect an exception for invalid intent
        with self.assertRaises(CustomException) as context:
            self.dimension_service_impl._DimensionServiceImpl__validate_dropdowntable_sheet(
                drop_down_sheet_df, base_intent_sub_intent_map
            )


    def test_edit_training_phrases(self):
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,intent2":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}
        similar_phrase = {"metadata":{"category":"intent_classification","INTENT,intent1":True,"SUBINTENT,intent1,subintent1":True,"is_subintent":True},"document_id":str(uuid.uuid4())}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',return_value=["embeddings"]) as mock_embeddings:
                with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',return_value=[[similar_phrase]]) as mock_embeddings:
                    with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as mock_update:

                        response=self.client.post(reverse('Platform:edit_training_phrase'),headers=self.headers,data={"dimension_names":["subintent"],"parent_dimension_name":"intent","utterance":{"id":"1234","utterance":"utterance1"}},format='json')

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_training_phrases_no_id_provided(self):
        response = self.client.post(reverse('Platform:edit_training_phrase'), headers=self.headers,
                            data={"dimension_names": ["subintent"],
                                  "parent_dimension_name": "intent",
                                  "utterance": {"id": None, "utterance": "utterance1"}},
                            format='json')

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_training_phrases_duplicate(self):
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,intent2":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}
        similar_phrase = {"metadata":{"category":"intent_classification","INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True},"document_id":str(uuid.uuid4())}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',return_value=["embeddings"]) as mock_embeddings:
                with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',return_value=[[similar_phrase]]) as mock_embeddings:
                    with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as mock_update:

                        response=self.client.post(reverse('Platform:edit_training_phrase'),headers=self.headers,data={"dimension_names":["subintent"],"parent_dimension_name":"intent","utterance":{"id":"1234","utterance":"utterance1"}},format='json')


        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_training_phrases_other_sub_intents_present_no_similar_records(self):
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,intent2":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}
        similar_phrase = {"metadata":{"category":"intent_classification","INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True},"document_id":str(uuid.uuid4())}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',return_value=["embeddings"]) as mock_embeddings:
                with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',return_value=[[]]) as mock_embeddings:
                    with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as mock_update:
                        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.upload_utterances_at_once') as mock_upload:

                            response=self.client.post(reverse('Platform:edit_training_phrase'),headers=self.headers,data={"dimension_names":["subintent"],"parent_dimension_name":"intent","utterance":{"id":"1234","utterance":"utterance1"}},format='json')


        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_edit_training_phrases_no_other_intents(self):
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}
        similar_phrase = {"metadata":{"category":"intent_classification","INTENT,intent1":True,"SUBINTENT,intent1,subintent1":True,"is_subintent":True},"document_id":str(uuid.uuid4())}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',return_value=["embeddings"]) as mock_embeddings:
                with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',return_value=[[similar_phrase]]) as mock_embeddings:
                    with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as mock_update:

                        response=self.client.post(reverse('Platform:edit_training_phrase'),headers=self.headers,data={"dimension_names":["intent"],"utterance":{"id":"1234","utterance":"utterance1"}},format='json')

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_edit_training_phrases_no_other_intents_no_similar_records(self):
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}
        #similar_phrase = {"metadata":{"category":"intent_classification","INTENT,intent1":True,"SUBINTENT,intent1,subintent1":True,"is_subintent":True},"document_id":str(uuid.uuid4())}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',return_value=["embeddings"]) as mock_embeddings:
                with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',return_value=[[]]) as mock_embeddings:
                    with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as mock_update:
                        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_email_document_embedding') as mock_update_embedding:

                            response=self.client.post(reverse('Platform:edit_training_phrase'),headers=self.headers,data={"dimension_names":["intent"],"utterance":{"id":"1234","utterance":"utterance1"}},format='json')

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_add_training_phrases(self):
        training_phrase = {"metadatas":[{"category":"intent_classification","INTENT,intent":True,"INTENT,intent2":True,"SUBINTENT,intent,subintent":True,"is_subintent":True}],"documents":["document"],"embeddings":["embeddings"],"ids":[str(uuid.uuid4())]}
        similar_phrase = {"metadata":{"category":"intent_classification","INTENT,intent1":True,"SUBINTENT,intent1,subintent1":True,"is_subintent":True},"document_id":str(uuid.uuid4())}

        with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.get_record_by_id',return_value=training_phrase) as mock_fetch_existing_records:
            with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.embed_query_list',return_value=["embeddings"]) as mock_embeddings:
                with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.find_similar_records',return_value=[[similar_phrase]]) as mock_embeddings:
                    with patch('Platform.services.impl.dimension_service_impl.ChromaVectorStore.update_metadata_by_id') as mock_update:

                        response=self.client.post(reverse('Platform:add_training_phrase'),headers=self.headers,data={"dimension_name":"subIntent","parent_dimension_name":"parentIntent","utterances":["utterance1"]},format='json')

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)




