from uuid import uuid4

import pandas as pd
from typing import Dict, List, Tuple, Any, Union

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException
from EmailApp.constant.constants import CategoriesForPersonalization, ChromadbMetaDataParams
from Platform.constant.constants import ChromaExcelSheet, ReasonForFailure, ChromaUtils
from time import time
import logging
logger = logging.getLogger(__name__)

def get_current_unix_timestamp():
    """
        Get the current Unix timestamp in milliseconds.

        This function calculates the current Unix timestamp (number of milliseconds
        since January 1, 1970, 00:00:00 UTC) by multiplying the result of `time()`
        from the `time` module by 1000 and rounding it to the nearest integer.

        Returns:
            int: The current Unix timestamp in milliseconds.
    """
    current_timestamp = round(time()*1000)

    return current_timestamp


def intent_list_to_map_sub_intents(intent_list : List[str], sub_intents_list : List[str], base_intent_sub_intent_map : Dict[str, List[str]] ) -> dict:
    """
        Maps intents to their respective sub-intents based on a predefined mapping.

        Args:
            intent_list (list of str): A list of intents to be mapped.
            sub_intents_list (list of str): A list of sub-intents to be matched with the intents.
            base_intent_sub_intent_map (dict): A dictionary where keys are intents (in uppercase) and
                                               values are lists of valid sub-intents (in uppercase).

        Returns:
            dict: A dictionary mapping each intent (from `intent_list`) to a list of matching sub-intents
                  (from `sub_intents_list`) that exist in the `base_intent_sub_intent_map`.
        If an intent has no valid sub-intents, it is omitted from the result.
    """

    intent_subintent_map = {}

    for intent in intent_list:
        all_sub_intents = base_intent_sub_intent_map.get(intent.upper())
        #Checking whether the intent is present or not
        if all_sub_intents is not None:
            intent_subintent_map[intent] = [sub_intent for sub_intent in sub_intents_list if
                                        sub_intent.upper() in all_sub_intents]
    return intent_subintent_map


def add_combinations( metadata : dict, intent : str, sub_intents : list):
    """
        Adds combinations of intent and sub-intents to the metadata dictionary.

        Args:
            metadata (dict): The dictionary to which intent-sub-intent combinations are added.
            intent (str): The intent associated with the sub-intents.
            sub_intents (list of str): A list of sub-intents to be combined with the intent.
    """

    # EX: SUBINTENT,intent_value,sub intent value: True
    for sub_intent in sub_intents:
        metadata[f'{ChromadbMetaDataParams.SUB_INTENT.value}{ChromadbMetaDataParams.SEPARATOR.value}{intent}{ChromadbMetaDataParams.SEPARATOR.value}{sub_intent}'] = True
    metadata[ChromadbMetaDataParams.SUB_INTENT_FILTER.value]  = True if sub_intents else False


def get_metadata_for_creation(parent_dimension_name: str, child_dimension_names: Union[list, set]):
    logger.debug("In Chroma utils :: get_metadata_for_creation")
    # Prepare metadata for the utterances
    metadata = {
        ChromadbMetaDataParams.CATEGORY.value: CategoriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value}

    for child_dimension_name in child_dimension_names:
        if parent_dimension_name:
            # For sub-intent
            metadata[ChromadbMetaDataParams.SUB_INTENT.value +
                     ChromadbMetaDataParams.SEPARATOR.value +
                     parent_dimension_name.lower() +
                     ChromadbMetaDataParams.SEPARATOR.value +
                     child_dimension_name.lower()] = True
        else:
            # For primary intent
            metadata[ChromadbMetaDataParams.INTENT.value +
                     ChromadbMetaDataParams.SEPARATOR.value +
                     child_dimension_name.lower()] = True

    metadata[ChromadbMetaDataParams.SUB_INTENT_FILTER.value] = False
    if parent_dimension_name:
        metadata[ChromadbMetaDataParams.INTENT.value +
                 ChromadbMetaDataParams.SEPARATOR.value +
                 parent_dimension_name.lower()] = True
        metadata[ChromadbMetaDataParams.SUB_INTENT_FILTER.value] = True
    return metadata

def prepare_metadata(intent_sub_intent_map: Dict[str, List[str]]) -> dict:
    """
        Prepares a metadata dictionary based on the intent-to-sub-intent mapping.

        Args:
            intent_sub_intent_map (dict): A dictionary where:
                - Keys are intents (str) and row_index(str).
                - Values are lists of associated sub-intents (list of str). For key row_index value should be int.
    """

    if not intent_sub_intent_map:
        raise InvalidValueProvidedException("No intent-sub_intent mapping found")

    metadata = dict()
    #Ex - INTENT,intent_value : True
    for intent, sub_intents in intent_sub_intent_map.items():
        # skip if the key is row index
        if intent  == ChromaExcelSheet.TRAINING_PHRASE_ID.value:
            continue
        metadata.update(get_metadata_for_creation(intent,sub_intents))

    return metadata


def get_intent_sub_intents(row: List[str]) -> Dict[str, Any]:
    """
    Converts a row of intents and sub-intents into a dictionary.

    Args:
        row (list): A list where even-indexed elements are intents and odd-indexed elements are sub-intents separated by comma.

    Returns:
        dict: A mapping of intents to their respective sub-intent lists.
    """
    intent_sub_intent_map = {}

    # Check if row has an even number of elements
    if len(row) % 2 != 0:
        raise ValueError("Row must contain an even number of elements (intent-sub_intent pairs).")

    # Iterate over the row in steps of 2 (intent, sub_intent pairs)
    for i in range(0, len(row), 2):

        intent = row[i].strip().lower()
        sub_intents = row[i + 1].strip().split(',')
        # Clean sub-intent strings and filter out empties
        sub_intents = {sub_intent.strip().lower() for sub_intent in sub_intents if sub_intent.strip()}

        # Only add to map if intent is not empty
        if intent:
            # if intent is present in dict then append to the existing list
            intent_sub_intent_map.setdefault(intent,set()).update(sub_intents)
        #intent is absent but sub intents are present
        elif sub_intents:
            # invalid_rows.append(
            #     {
            #         ChromaExcelSheet.TRAINING_PHRASE_ID.value: query_id,
            #         ChromaExcelSheet.TRAINING_PHRASE.value: training_phrase,
            #         ChromaExcelSheet.ERROR_REASON.value: ReasonForFailure.INVALID_INTENT_SUBINTENT_PAIR.value
            #
            #     }
            # )
            logger.debug("Found Training Phrase for which intent is absent but sub intents are present")

    return intent_sub_intent_map

def update_intent_sub_intent_map(existing_map, current_map):
    """
        Updates the existing intent-to-sub-intent mapping with the current mapping.

        Args:
            existing_map (dict): The existing map of intents to sub-intents.
            current_map (dict): The current map of intents to sub-intents to merge into the existing map.
    """
    for intent, sub_intents in current_map.items():
        if intent in existing_map:
            # Use set to avoid duplicate sub-intents
            existing_map[intent].update(sub_intents)
        else:
            # Add new intent with its sub-intents
            existing_map[intent] = sub_intents



def map_intent_sub_intents_for_query(dataframe : pd.DataFrame) -> Dict[str, dict]:
    """
        Maps each unique query to its corresponding intents and sub-intents from a DataFrame.

        Args:
            dataframe (pd.DataFrame): The DataFrame containing query, intent, and sub-intent data.

        Returns:
            Tuple [dict, list]: A dictionary where keys are queries and values are mappings of intents to their respective sub-intents and list to keep track of invalid rows.
    """
    resultant_map = dict()

    # Predefine frequently accessed column values for better performance
    training_phrases_col = ChromaExcelSheet.TRAINING_PHRASES.value
    training_phrase_id = ChromaExcelSheet.TRAINING_PHRASE_ID.value

    for idx, row in dataframe.iterrows():
        # Validate the index type early
        if not isinstance(idx, int):
            raise InvalidValueProvidedException(f"TypeError :: Index {idx} is not an integer!")

        # Strip and check training phrase
        training_phrase = str(row[training_phrases_col]).strip()
        query_id = row[ChromaExcelSheet.ID_COLUMN.value]
        if not training_phrase:
            continue  # Skip empty queries

        # Generate intent and sub-intent mappings
        intent_sub_intent_map = get_intent_sub_intents(row.tolist()[2:])
        if intent_sub_intent_map:

            if training_phrase in resultant_map:
                # Update the existing mapping
                update_intent_sub_intent_map(resultant_map[training_phrase], intent_sub_intent_map)
            else:
                # Create a new mapping
                resultant_map[training_phrase] = intent_sub_intent_map

            intent_sub_intent_map[training_phrase_id] = query_id

        else:
            # Add row to error_rows if no intent/sub-intent found
            logger.debug(f"No intent/sub-intent found for the training phrase ID : {query_id}")
            # error_rows.append({
            #     training_phrase_id: query_id,
            #     training_phrases_col: training_phrase,
            #     error_reason_col: reason_no_intent
            # })

    return resultant_map


def update_dimension_wise_count(intent_sub_intent_map, dimension_wise_count):

    for intent, sub_intents in intent_sub_intent_map.items():
        if intent == ChromaExcelSheet.TRAINING_PHRASE_ID.value:
            continue

        count_dict = dimension_wise_count.get(intent)

        #if intent is not present in dimension_wise_count then initialize the counts
        if count_dict is None:
            temp = dict()
            temp[intent] = 1
            for sub_intent in sub_intents:
                temp[sub_intent] = 1
            dimension_wise_count[intent] = temp

        #if intent already in the dimension_wise_count then just update the things
        else:
            for sub_intent in sub_intents:
                #update the sub intent count
                count_dict[sub_intent] = count_dict.get(sub_intent,0)+1

            #update the intent count
            count_dict[intent] = count_dict.get(intent,0)+1

def update_dimension_wise_count_for_missing_keys(missing_keys: List[str], dimension_wise_count):

    for each_key in missing_keys:

        if each_key.startswith(ChromadbMetaDataParams.INTENT.value):

            _, intent_name = each_key.split(ChromadbMetaDataParams.SEPARATOR.value)

            count_dict = dimension_wise_count.get(intent_name)

            if count_dict is None:

                dimension_wise_count[intent_name] = { intent_name : 1}

            else:
                count_dict[intent_name] = count_dict.get(intent_name, 0) + 1

        elif each_key.startswith(ChromadbMetaDataParams.SUB_INTENT.value):

            _, intent_name, sub_intent_name = each_key.split(ChromadbMetaDataParams.SEPARATOR.value)

            count_dict = dimension_wise_count.get(intent_name)

            if count_dict is None:

                dimension_wise_count[intent_name] = {sub_intent_name : 1}

            else:

                count_dict[sub_intent_name] = count_dict.get(sub_intent_name, 0) + 1


def compare_chroma_metadatas(current_metadata: dict, existing_metadata: dict, ignore_keys: set = None) -> list:
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
    missing_keys = []
    for key, value in filtered_current_metadata.items():

        if key not in filtered_existing_metadata:
            missing_keys.append(key)

    return missing_keys


def get_duplicate_rows(duplicates_df : pd.DataFrame, duplicate_examples: list) -> List[int]:
    """
    Identifies and processes duplicate rows in a DataFrame.

    Parameters:
        duplicates_df (pd.DataFrame): The DataFrame containing potential duplicate rows.
        duplicate_examples (list) : To keep track of invalid rows

    Returns:
        tuple: A tuple containing:
            - duplicate_row_indices (list): List of row indices for duplicates.
            - duplicate_examples (list): List of dictionaries representing duplicate row details,
              including row number, training phrase, and error reason.

    Raises:
        InvalidValueProvidedException: If the row index is not an integer.
    """

    duplicate_row_indices = []
    if duplicates_df.empty:
        return duplicate_row_indices

    for idx, row in duplicates_df.iterrows():

        if not isinstance(idx, int):
            raise InvalidValueProvidedException(f"TypeError :: Index {idx} is not an integer!")

        training_phrase = row[ChromaExcelSheet.TRAINING_PHRASES.value]
        query_id = row[ChromaExcelSheet.ID_COLUMN.value]

        intent_sub_intent_map = get_intent_sub_intents(row  = row[2:].tolist())

        #if training phrase is an empty string we are not considering
        if training_phrase.strip():
            duplicate_examples.append(
                {
                   ChromaExcelSheet.TRAINING_PHRASE_ID.value: query_id,
                   ChromaExcelSheet.TRAINING_PHRASE.value : training_phrase,
                    ChromaExcelSheet.ERROR_REASON.value : ReasonForFailure.DUPLICATE_ROW.value,
                    ChromaExcelSheet.INTENT_SUBINTENT_MAP.value : intent_sub_intent_map


                }
                                      )

        duplicate_row_indices.append(idx)

    return duplicate_row_indices


def update_or_skip_examples(nearest_queries, resultant_map, vector_embeddings, collection_name, error_rows) -> dict:
    """
    Updates metadata for training phrases or skips duplicates based on comparison.

    Args:
        nearest_queries (list): List of nearest documents with metadata and similarity scores.
        resultant_map (dict): Map of training phrases to intent and sub-intent metadata.
        vector_embeddings (list): List of vector embeddings for the training phrases.
        collection_name (str): Name of the collection in the database.
        error_rows (list): List to log skipped rows due to duplication.

    Returns:
        A Dictionary consists of filtered_queries,filtered_embeddings,doc_ids_list,metadata_list,dimension_wise_count, updated_doc_ids, updated_metadata_list keys and it's values

    Logs:
        Logs duplicate records, updates, and final counts of resultant and filtered data.

    Example:
        update_or_skip_duplicates(
            nearest_queries=[[{"document_id": "doc1", "metadata": {...}}]],
            resultant_map={"phrase1": {...}},
            vector_embeddings=[[0.1, 0.2]],
            collection_name="example_collection",
            error_rows=[]
        )
    """
    logger.info("Starting duplicate check and update process for collection '%s'.", collection_name)

    filtered_embeddings = []
    filtered_queries = []
    doc_ids_list = []
    metadata_list = []
    updated_doc_ids = []
    updated_metadata_list = []
    dimension_wise_count = dict()
    for idx, (training_phrase, intent_sub_intent_map) in enumerate(resultant_map.items()):
        # Prepare metadata
        metadata = prepare_metadata(intent_sub_intent_map)
        nearest_documents = nearest_queries[idx]
        is_duplicate = False
        is_updated  = False
        dup_id = None
        for nearest_document in nearest_documents:
            doc_metadata = nearest_document.get('metadata')
            doc_id = nearest_document.get('document_id')
            missing_keys = compare_chroma_metadatas(current_metadata=metadata, existing_metadata=doc_metadata)
            if missing_keys:
                # Update the record
                doc_metadata.update(metadata)
                doc_metadata.update({
                    ChromadbMetaDataParams.UPDATED_TIME_STAMP.value : get_current_unix_timestamp()
                })
                # chroma_obj.update_the_metadata_with_document_id(doc_metadata, doc_id, collection_name)
                updated_doc_ids.append(doc_id)
                updated_metadata_list.append(doc_metadata)
                update_dimension_wise_count_for_missing_keys(missing_keys, dimension_wise_count)
                is_updated = True
                logger.info("Updated metadata for document ID '%s' in collection '%s'.", doc_id, collection_name)
            else:
                is_duplicate = True
                dup_id = doc_id
                logger.warning("Duplicate training phrase detected: '%s'. Skipping update.", training_phrase)




        if is_duplicate:
            # Add to error rows for logging skipped duplicates
            error_rows.append(
                {
                    ChromaExcelSheet.TRAINING_PHRASE_ID.value: intent_sub_intent_map.get(
                        ChromaExcelSheet.TRAINING_PHRASE_ID.value, -1),
                    ChromaExcelSheet.TRAINING_PHRASE.value: training_phrase,
                    ChromaExcelSheet.ERROR_REASON.value: ReasonForFailure.DUPLICATE_ENTRY.value,
                    ChromaExcelSheet.DOC_ID.value : dup_id
                }
            )
            continue

        if is_updated:
            continue

        filtered_queries.append(training_phrase)
        filtered_embeddings.append(vector_embeddings[idx])
        doc_ids_list.append(str(uuid4()))
        metadata_list.append(metadata)
        # Add ChromaDB-specific metadata
        metadata[ChromadbMetaDataParams.CATEGORY.value] = CategoriesForPersonalization.INTENT_CLASSIFICATION_CATEGORY.value

        current_timestamp = get_current_unix_timestamp()

        metadata[ChromadbMetaDataParams.CREATED_TIMESTAMP.value] = current_timestamp
        metadata[ChromadbMetaDataParams.UPDATED_TIME_STAMP.value] = current_timestamp

        update_dimension_wise_count(intent_sub_intent_map= intent_sub_intent_map, dimension_wise_count= dimension_wise_count)

        # Return results as a structured dictionary
    return {
        ChromaUtils.FILTERED_QUERIES.value: filtered_queries,
        ChromaUtils.FILTERED_EMBEDDINGS.value: filtered_embeddings,
        ChromaUtils.DOC_IDS_LIST.value: doc_ids_list,
        ChromaUtils.METADATA_LIST.value: metadata_list,
       ChromaUtils.DIMENSION_WISE_COUNT.value: dimension_wise_count,
        ChromaUtils.UPDATED_DOC_IDS.value: updated_doc_ids,
        ChromaUtils.UPDATED_METADATA_LIST.value: updated_metadata_list,
       ChromaUtils.ERROR_ROWS.value: error_rows,
    }









