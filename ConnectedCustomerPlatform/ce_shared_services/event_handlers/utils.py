import logging
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from ce_shared_services.configuration_models.configuration_models import IntentSpecificationConfig, \
    IntentSubIntentsConfig
from ce_shared_services.event_handlers.constants import IntentPrompt, ChatHistoryFormatKeys, MessageSourceType, \
    NO_SIMILAR_QUERIES_FOUND, ChromadbMetaDataParams, ChromaOperators, Chromadb
from ce_shared_services.event_handlers.error_messages import IntentClassificationHandler

logger=logging.getLogger(__name__)
def format_intents_sub_intents(intents_list: List[IntentSpecificationConfig]) -> str:
    """
    Formats a list of intents with their names and descriptions for display.Order should be old to new

    Args:
        intents_list (List[IntentDataConfig]): A list of IntentDataConfig objects, each having 'name' and 'description' attributes.

    Returns:
        str: A formatted string containing numbered intent names and descriptions,
             including an 'OTHERS' intent added at the end.

    Raises:
        ValueError: If any intent lacks a valid name or description.
    """
    logger.debug("In Utils :: format_intents_sub_intents")
    formatted_output = "\n"

    # Iterate through the intents list with enumeration for numbering
    for idx, intent in enumerate(intents_list, start=1):
        # Validate that the intent has both a name and a description
        if not intent.name or not intent.description:
            raise ValueError('Invalid Intent name/Description')

        # Format Intent Name and Description
        # Append the intent name in uppercase, indented for readability
        formatted_output += f"\t{idx}. {intent.name.upper()}:\n"
        # Append the intent description, further indented
        formatted_output += f"\t\t- {intent.description}\n"

    # Return the fully formatted string
    return formatted_output



def format_conversation_history(conversation_history_list,conversation_length):
    """
    Formats chat history into a structured format based on the message source (AI or user).

    Args:
        conversation_history_list (list): List of dictionaries containing chat history data.
        conversation_length(int): Length of maximum conversations to be taken

    Returns:
        list: A list of formatted messages (as strings) from the chat history.
    """
    logger.debug("In Utils::format_conversation_history")

    # Initialize an empty list to store the formatted chat history.
    result = []
    if not conversation_history_list:
        return None
    # Iterate through each chat history entry in the provided list.
    for conversation_history in conversation_history_list:
        # Check if the source is 'user'.
        if conversation_history.get(ChatHistoryFormatKeys.SOURCE.value).lower() == MessageSourceType.USER.value.lower():
            # Format the message as a human message and append it to the result list.
            result.append(get_human_message(conversation_history.get(ChatHistoryFormatKeys.MESSAGE.value)))
        # Check if the source is 'AI'.
        elif conversation_history.get(ChatHistoryFormatKeys.SOURCE.value).lower() == MessageSourceType.AI.value.lower():
            # Format the message as an AI message and append it to the result list.
            result.append(get_ai_message(conversation_history.get(ChatHistoryFormatKeys.MESSAGE.value)))

        if len(conversation_history_list) >= conversation_length:
            break

    # Return the final formatted list of messages.
    return result

def format_chroma_examples(results, limit,main_intent=None):
    """
    Formats ChromaDB results into a string suitable for use in prompts.

    Steps:
    1. Validate the  content of `results`.
    2. Extract documents and metadata entries from the results.
    3. Format the examples based on the provided `main_intent`.
    4. Limit the number of formatted examples to the given `limit`.

    Args:
        results (List): Results returned by ChromaDB, containing documents and metadata.
        main_intent (str, optional): The primary intent to filter and format sub-intent results. Defaults to None.
        limit (int, optional): Maximum number of formatted examples to return. Defaults to the configured limit.

    Returns:
        str: A string of formatted examples or a default "no similar queries" message if no examples are available.
    """
    logger.debug("In Utils::format_chroma_examples")
    #formatting chroma examples according to prompt,if examples are not there then providing below string
    # Validate results structure and content


    if not results:
        return NO_SIMILAR_QUERIES_FOUND
    formatted_queries = []

    for chunk in results:
        if main_intent is None:
            #fetching intents marked for that specific example
            main_intents = get_intent_name_from_metadata(chunk.metadata)
            if main_intents:
                # Format the query for user message and intents identified
                formatted_queries.append(f"{IntentPrompt.USER_MESSAGE.value}: {chunk.document} - {IntentPrompt.INTENTS_IDENTIFIED.value}: {', '.join(main_intents)}")
        else:
            #fetching sub intents marked for that specific example
            sub_intents = get_sub_intent_name_from_metadata(chunk.metadata, main_intent)
            if sub_intents:
                # Format the query for user message and sub-intents identified
                formatted_queries.append(f"{IntentPrompt.USER_MESSAGE.value}: {chunk.document} - {IntentPrompt.SUB_INTENTS_IDENTIFIED.value}: {', '.join(sub_intents)}")
        if len(formatted_queries) >= limit:
            break
    #Join the formatted queries into a single string
    return "\n".join(formatted_queries) if formatted_queries else NO_SIMILAR_QUERIES_FOUND


def get_intent_name_from_metadata(intent_metadata):
    logger.debug("In Utils :: get_intent_name_from_metadata")
    #fetching intent names from chroma metadata
    matching_keys = []
    if not intent_metadata:
        return matching_keys
    for key in intent_metadata.keys():
        key_parts = key.split(ChromadbMetaDataParams.SEPARATOR.value)
        #metadata:[{category:intent_classification},{INTENT,intent_name:True},{SUBINTENT,intent_name,sub_intent_name:True}] ---intent will have 2 parts and validating them
        if key_parts[0] == ChromadbMetaDataParams.INTENT.value and len(key_parts) == ChromadbMetaDataParams.LENGTH_FOR_INTENT.value:
            matching_keys.append(key_parts[1].upper())

    return matching_keys
def get_sub_intent_name_from_metadata(sub_intent_metadata,intent_identified):
    logger.debug("In Utils :: get_sub_intent_name_from_metadata")
    matching_keys = []
    if not sub_intent_metadata:
        return matching_keys
    for key in sub_intent_metadata.keys():
        key_parts = key.split(ChromadbMetaDataParams.SEPARATOR.value)
        #---metadata:[{category:intent_classification},{INTENT,intent_name:True},{SUBINTENT,intent_name,sub_intent_name:True}]---sub intent will have 3 parts and validating them
        if key_parts[0] == ChromadbMetaDataParams.SUB_INTENT.value and key_parts[1].lower()==intent_identified.lower() and len(key_parts) == ChromadbMetaDataParams.LENGTH_FOR_SUB_INTENT.value:
            matching_keys.append(key_parts[2].upper())
    return matching_keys


def create_prompt_with_chat_history_query(prompt, chat_history: list, query):
    """
    Constructs a list of inputs for the Language Learning Model (LLM) by combining a system message,
    chat history, and the user's query.

    Args:
        prompt (str): The initial system prompt to guide the LLM's behavior.
        chat_history (list): A list of chat history messages to maintain conversational context.
        query (str): The current user query to be appended as the latest human message.

    Returns:
        list: A list of formatted inputs (system message, chat history, and user query) for the LLM.
    """
    logger.debug("In Utils::create_prompt_with_chat_history_query")
    logger.debug(f"chat_history :: {chat_history} :: query :: {query}")

    # Initialize the list of LLM inputs.
    # The first input is always the system message to establish the behavior or role of the LLM.
    llm_inputs = [get_system_message(prompt)]

    # Add chat history if it exists to maintain continuity of the conversation.
    # This ensures the LLM has context from previous interactions.
    if chat_history:
        llm_inputs.extend(chat_history)

    # Append the user's query as a human message.
    # This simulates the user input at the end of the conversation.
    llm_inputs.append(get_human_message(query))

    logger.debug(f"Prompt before invoking the LLM::{llm_inputs}")
    logger.debug(f"llm_inputs::{llm_inputs}")

    return llm_inputs


def get_human_message(content):
    return HumanMessage(content=content)

def get_system_message(prompt):
    return SystemMessage(content=prompt)

def get_ai_message(content):
    return AIMessage(content=content)

def get_metadata_for_intent_examples(intents:List[IntentSubIntentsConfig]):
    logger.debug("In Utils :: get_metadata_for_intent_examples")
    # Prepare metadata for the utterances
    metadata = []
    for intent in intents:
        if intent.name:
            # For primary intent
            metadata.append({ChromadbMetaDataParams.INTENT.value +
                          ChromadbMetaDataParams.SEPARATOR.value +
                          intent.name.lower():True})
    or_fields={ChromaOperators.OR:metadata}
    mandatory_field={ChromadbMetaDataParams.CATEGORY.value: Chromadb.INTENT_CLASSIFICATION_CATEGORY.value}
    return {ChromaOperators.AND:[mandatory_field,or_fields]}

