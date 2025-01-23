import pandas as pd
from django.test import TestCase
from unittest.mock import patch
from Platform.chroma_utils import (
    get_current_unix_timestamp, intent_list_to_map_sub_intents, add_combinations,
    prepare_metadata, get_intent_sub_intents, update_intent_sub_intent_map,
    map_intent_sub_intents_for_query, update_dimension_wise_count,
    compare_chroma_metadatas, get_duplicate_rows, update_or_skip_examples, get_metadata_for_creation
)

class TestPlatformChromaUtils(TestCase):

    @patch('Platform.chroma_utils.time')
    def test_get_current_unix_timestamp(self, mock_time):
        mock_time.return_value = 1690000000.123
        result = get_current_unix_timestamp()
        self.assertEqual(result, 1690000000123)

    def test_intent_list_to_map_sub_intents(self):
        intent_list = ['Intent 1', 'Intent 2']
        sub_intents = ['Sub Intent 1', 'Sub Intent 2']
        mapping = {'INTENT 1': ['SUB INTENT 1'], 'INTENT 2': ['SUB INTENT 2']}
        result = intent_list_to_map_sub_intents(intent_list, sub_intents, mapping)
        expected = {'Intent 1': ['Sub Intent 1'], 'Intent 2': ['Sub Intent 2']}
        self.assertEqual(result, expected)

    def test_add_combinations(self):
        metadata = {}
        intent = 'Intent 1'
        sub_intents = ['Sub Intent 1', 'Sub Intent 2']
        with patch('Platform.chroma_utils.ChromadbMetaDataParams') as mock_params:
            mock_params.SUB_INTENT.value = 'SUB_INTENT'
            mock_params.SEPARATOR.value = ':'
            mock_params.SUB_INTENT_FILTER.value = 'SUB_INTENT_FILTER'
            add_combinations(metadata, intent, sub_intents)
            self.assertIn('SUB_INTENT:Intent 1:Sub Intent 1', metadata)

    @patch('Platform.chroma_utils.get_metadata_for_creation')
    def test_prepare_metadata(self, mock_get_metadata):
        mock_get_metadata.return_value = {'mock_key': 'mock_value'}
        intent_map = {'Intent 1': ['Sub Intent 1']}
        result = prepare_metadata(intent_map)
        self.assertIn('mock_key', result)

    def test_get_intent_sub_intents(self):
        row = ['Intent 1', 'Sub Intent 1,Sub Intent 2', 'Intent 2', 'Sub Intent 3']
        result = get_intent_sub_intents(row)
        expected = {'intent 1': {'sub intent 1', 'sub intent 2'}, 'intent 2': {'sub intent 3'}}
        self.assertEqual(result, expected)

    def test_update_intent_sub_intent_map(self):
        existing_map = {'Intent 1': {'Sub Intent 1'}}
        current_map = {'Intent 1': {'Sub Intent 2'}, 'Intent 2': {'Sub Intent 3'}}
        update_intent_sub_intent_map(existing_map, current_map)
        self.assertEqual(existing_map['Intent 1'], {'Sub Intent 1', 'Sub Intent 2'})
        self.assertIn('Intent 2', existing_map)

    @patch('Platform.chroma_utils.get_intent_sub_intents')
    def test_map_intent_sub_intents_for_query(self, mock_get_intents):
        mock_get_intents.return_value = {'Intent 1': {'Sub Intent 1'}}
        data = {
            'ID': [1],
            'Training Phrases': ['Sample phrase'],
            'Intent 1': ['Intent 1'],
            'Sub Intent 1': ['Sub Intent 1'],
            'Intent 2': [None],
            'Sub Intent 2': [None],
        }
        dataframe = pd.DataFrame(data)
        result = map_intent_sub_intents_for_query(dataframe)
        self.assertIsInstance(result, dict)

    def test_update_dimension_wise_count(self):
        dimension_map = {}
        intent_map = {'Intent 1': {'Sub Intent 1'}}
        update_dimension_wise_count(intent_map, dimension_map)
        self.assertIn('Intent 1', dimension_map)

    def test_compare_chroma_metadatas(self):
        metadata1 = {'key1': 'value1', 'key2': 'value2'}
        metadata2 = {'key1': 'value1', 'key2': 'value2'}
        ignore_keys = {'key2'}
        result = compare_chroma_metadatas(metadata1, metadata2, ignore_keys)
        self.assertTrue(result)

    @patch('Platform.chroma_utils.chroma_obj.upload_utterances_at_once')
    def test_get_duplicate_rows(self, mock_chroma_obj):
        mock_chroma_obj.return_value = None
        data = {
            'ID': [1, 2],
            'Training Phrases': ['Sample phrase 1', 'Sample phrase 2'],
            'Intent 1': ['Intent 1', 'Intent 2'],
            'Sub Intent 1': ['Sub Intent 1', 'Sub Intent 2'],
        }
        dataframe = pd.DataFrame(data)
        duplicate_examples = []
        result = get_duplicate_rows(dataframe, duplicate_examples)
        self.assertIsInstance(result, list)

    @patch('Platform.chroma_utils.chroma_obj.update_the_metadata_with_document_id')
    def test_update_or_skip_examples(self, mock_update):
        mock_update.return_value = None
        nearest_queries = [[{'metadata': {}, 'document_id': 'doc1'}]]
        resultant_map = {'Sample phrase': {'metadata': {}}}
        vector_embeddings = [[0.1, 0.2]]
        collection_name = 'test_collection'
        error_rows = []
        result = update_or_skip_examples(nearest_queries, resultant_map, vector_embeddings, collection_name, error_rows)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 6)

    @patch("Platform.chroma_utils.chroma_obj.update_the_metadata_with_document_id")
    @patch("Platform.chroma_utils.get_current_unix_timestamp", return_value=1690000000123)
    @patch("Platform.chroma_utils.prepare_metadata", return_value={"mock_metadata": "value"})
    @patch("Platform.chroma_utils.compare_chroma_metadatas", side_effect=[False, True])
    def test_update_or_skip_examples(
            self, mock_compare, mock_prepare_metadata, mock_get_timestamp, mock_update_metadata
    ):
        # Mock inputs
        nearest_queries = [
            [
                {"metadata": {"existing_key": "value1"}, "document_id": "doc1"},
            ]
        ]
        resultant_map = {
            "Training Phrase 1": {
                "metadata": {"existing_key1": "value1"},
                "Intent 1": {"Sub Intent 1", "Sub Intent 2"}
            }
        }
        vector_embeddings = [[0.1, 0.2, 0.3]]
        collection_name = "test_collection"
        error_rows = []

        # Call the function
        (
            filtered_queries,
            filtered_embeddings,
            doc_ids_list,
            metadata_list,
            dimension_wise_count,
            updated_count,
        ) = update_or_skip_examples(
            nearest_queries, resultant_map, vector_embeddings, collection_name, error_rows
        )

        # Assertions
        # Check updated count
        self.assertEqual(updated_count, 1)


    @patch("Platform.chroma_utils.compare_chroma_metadatas", return_value=True)
    @patch("Platform.chroma_utils.prepare_metadata")
    def test_handle_duplicates(self, mock_prepare_metadata, mock_compare):
        nearest_queries = [
            [{"metadata": {"existing_key": "value"}, "document_id": "doc1"}]
        ]
        resultant_map = {
            "Training Phrase 2": {
                "metadata": {},
                "Intent 1": {"Sub Intent 1"}
            }
        }
        vector_embeddings = [[0.5, 0.6, 0.7]]
        collection_name = "test_collection"
        error_rows = []

        # Call the function
        filtered_queries, filtered_embeddings, doc_ids_list, metadata_list, dimension_wise_count, updated_count = update_or_skip_examples(
            nearest_queries, resultant_map, vector_embeddings, collection_name, error_rows
        )

        # Assertions
        self.assertEqual(updated_count, 0)
        self.assertEqual(len(error_rows), 1)
        self.assertEqual(len(filtered_queries), 0)

    @patch("Platform.chroma_utils.compare_chroma_metadatas", return_value=False)
    @patch("Platform.chroma_utils.prepare_metadata")
    def test_insert_new_data(self, mock_prepare_metadata, mock_compare):
        nearest_queries = [[]]
        resultant_map = {
            "Training Phrase 3": {
                "metadata": {},
                "Intent 2": {"Sub Intent 3"}
            }
        }
        vector_embeddings = [[0.8, 0.9, 1.0]]
        collection_name = "test_collection"
        error_rows = []

        # Call the function
        filtered_queries, filtered_embeddings, doc_ids_list, metadata_list, dimension_wise_count, updated_count = update_or_skip_examples(
            nearest_queries, resultant_map, vector_embeddings, collection_name, error_rows
        )

        # Assertions
        self.assertEqual(updated_count, 0)
        self.assertEqual(len(error_rows), 0)
        self.assertEqual(len(filtered_queries), 1)
        self.assertEqual(filtered_queries[0], "Training Phrase 3")

    def test_empty_resultant_map(self):
        nearest_queries = []
        resultant_map = {}
        vector_embeddings = []
        collection_name = "test_collection"
        error_rows = []

        # Call the function
        filtered_queries, filtered_embeddings, doc_ids_list, metadata_list, dimension_wise_count, updated_count = update_or_skip_examples(
            nearest_queries, resultant_map, vector_embeddings, collection_name, error_rows
        )

        # Assertions
        self.assertEqual(updated_count, 0)
        self.assertEqual(len(filtered_queries), 0)
        self.assertEqual(len(metadata_list), 0)

    @patch("Platform.chroma_utils.ChromadbMetaDataParams")
    @patch("Platform.chroma_utils.CategoriesForPersonalization")
    def test_metadata_for_sub_intents(self, mock_categories, mock_params):
        # Mock constants
        mock_params.CATEGORY.value = "category"
        mock_params.SUB_INTENT.value = "sub_intent"
        mock_params.SEPARATOR.value = ":"
        mock_params.INTENT.value = "intent"
        mock_params.SUB_INTENT_FILTER.value = "sub_intent_filter"
        mock_categories.INTENT_CLASSIFICATION_CATEGORY.value = "intent_classification"

        # Inputs
        parent_dimension_name = "ParentIntent"
        child_dimension_names = {"SubIntent1", "SubIntent2"}

        # Call the function
        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        # Expected Metadata
        expected_metadata = {
            "category": "intent_classification",
            "sub_intent:parentintent:subintent1": True,
            "sub_intent:parentintent:subintent2": True,
            "intent:parentintent": True,
            "sub_intent_filter": True,
        }

        # Assertions
        self.assertEqual(result, expected_metadata)

    @patch("Platform.chroma_utils.ChromadbMetaDataParams")
    @patch("Platform.chroma_utils.CategoriesForPersonalization")
    def test_metadata_for_primary_intents(self, mock_categories, mock_params):
        # Mock constants
        mock_params.CATEGORY.value = "category"
        mock_params.SUB_INTENT.value = "sub_intent"
        mock_params.SEPARATOR.value = ":"
        mock_params.INTENT.value = "intent"
        mock_params.SUB_INTENT_FILTER.value = "sub_intent_filter"
        mock_categories.INTENT_CLASSIFICATION_CATEGORY.value = "intent_classification"

        # Inputs
        parent_dimension_name = None
        child_dimension_names = {"PrimaryIntent1", "PrimaryIntent2"}

        # Call the function
        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        # Expected Metadata
        expected_metadata = {
            "category": "intent_classification",
            "intent:primaryintent1": True,
            "intent:primaryintent2": True,
            "sub_intent_filter": False,
        }

        # Assertions
        self.assertEqual(result, expected_metadata)

    @patch("Platform.chroma_utils.ChromadbMetaDataParams")
    @patch("Platform.chroma_utils.CategoriesForPersonalization")
    def test_metadata_with_empty_child_dimensions(self, mock_categories, mock_params):
        # Mock constants
        mock_params.CATEGORY.value = "category"
        mock_params.SUB_INTENT.value = "sub_intent"
        mock_params.SEPARATOR.value = ":"
        mock_params.INTENT.value = "intent"
        mock_params.SUB_INTENT_FILTER.value = "sub_intent_filter"
        mock_categories.INTENT_CLASSIFICATION_CATEGORY.value = "intent_classification"

        # Inputs
        parent_dimension_name = "ParentIntent"
        child_dimension_names = set()  # Empty child dimensions

        # Call the function
        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        # Expected Metadata
        expected_metadata = {
            "category": "intent_classification",
            "intent:parentintent": True,
            "sub_intent_filter": True,
        }

        # Assertions
        self.assertEqual(result, expected_metadata)

    @patch("Platform.chroma_utils.ChromadbMetaDataParams")
    @patch("Platform.chroma_utils.CategoriesForPersonalization")
    def test_metadata_with_no_parent_or_children(self, mock_categories, mock_params):
        # Mock constants
        mock_params.CATEGORY.value = "category"
        mock_params.SUB_INTENT.value = "sub_intent"
        mock_params.SEPARATOR.value = ":"
        mock_params.INTENT.value = "intent"
        mock_params.SUB_INTENT_FILTER.value = "sub_intent_filter"
        mock_categories.INTENT_CLASSIFICATION_CATEGORY.value = "intent_classification"

        # Inputs
        parent_dimension_name = None
        child_dimension_names = set()  # No child dimensions

        # Call the function
        result = get_metadata_for_creation(parent_dimension_name, child_dimension_names)

        # Expected Metadata
        expected_metadata = {
            "category": "intent_classification",
            "sub_intent_filter": False,
        }

        # Assertions
        self.assertEqual(result, expected_metadata)

