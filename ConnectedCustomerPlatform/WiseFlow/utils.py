import logging
from datetime import datetime
from typing import List

from AIServices.LLM import get_human_message, get_ai_message, get_system_message
from DatabaseApp.models import DimensionsView
from WiseFlow.constants.constants import DataTypes, MessageSourceType, ChatHistoryFormatKeys
from ce_shared_services.configuration_models.configuration_models import IntentSubIntentsConfig, \
    IntentSpecificationConfig

logger=logging.getLogger(__name__)


def format_chat_history(chat_history_list):
    """
    Formats chat history into a structured format based on the message source (AI or user).

    Args:
        chat_history_list (list): List of dictionaries containing chat history data.

    Returns:
        list: A list of formatted messages (as strings) from the chat history.
    """
    logger.info("In Utils::get_previous_email_history")

    # Initialize an empty list to store the formatted chat history.
    result = []
    if not chat_history_list:
        return None
    # Iterate through each chat history entry in the provided list.
    for chat_history in chat_history_list:
        # Check if the source is 'user'.
        if chat_history.get(ChatHistoryFormatKeys.SOURCE.value).lower() == MessageSourceType.USER.value.lower():
            # Format the message as a human message and append it to the result list.
            result.append(get_human_message(chat_history.get(ChatHistoryFormatKeys.MESSAGE.value)))
        # Check if the source is 'AI'.
        elif chat_history.get(ChatHistoryFormatKeys.SOURCE.value).lower() == MessageSourceType.AI.value.lower():
            # Format the message as an AI message and append it to the result list.
            result.append(get_ai_message(chat_history.get(ChatHistoryFormatKeys.MESSAGE.value)))

    # Return the final formatted list of messages.
    return result


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
    logger.info("In Utils::create_prompt_with_chat_history_query")
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

    logger.info(f"Prompt before invoking the LLM::{llm_inputs}")
    logger.debug(f"llm_inputs::{llm_inputs}")

    return llm_inputs

def get_todays_date_and_day() -> str:
    return datetime.today().strftime("%A, %-d %B %Y")


def map_dimensions_to_intent_configs(dimensions: List[DimensionsView]) -> List[IntentSubIntentsConfig]:
    """
    Maps a list of DimensionsView objects to a list of IntentConfig objects.

    Args:
        dimensions (List[DimensionsView]): List of DimensionsView objects.

    Returns:
        List[IntentConfig]: A list of IntentConfig objects.
    """
    intent_config_list = []

    for dimension in dimensions:
        sub_intents = []

        # Process child dimensions if available
        if dimension.child_dimensions:
            for child in dimension.child_dimensions:
                sub_intents.append(IntentSpecificationConfig(
                    name=child.get('child_dimension_name'),
                    description=child.get('child_dimension_description'),
                    id=child.get('child_dimension_uuid'),
                ))

        # Add parent dimension as IntentConfig
        intent_config_list.append(IntentSubIntentsConfig(
            name=dimension.dimension_name,
            description=dimension.dimension_description,
            id=dimension.dimension_uuid,
            sub_intents=sub_intents
        ))

    return intent_config_list