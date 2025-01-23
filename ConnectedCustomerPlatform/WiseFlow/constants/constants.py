from enum import Enum

ENTITY_ORIGIN="entity"
EXAMPLE_TYPE="example"
TOP_N_TO_FETCH_EXAMPLES=10
PREFIX_FOR_ENTITY_CHROMA_COLLECTION_NAME="entity_"
class ChromaOperators:
    AND="$and"
class EntityExamplesKeys:
    PROMPT_OUTPUT="prompt_output"
    ENTITY_UUID="entity_uuid"
    ENTITY_NAME="entity_name"
    TYPE="type"
    ORIGIN="origin"

class OwnerShipTypes(Enum):
    SYSTEM="SYSTEM"
    CUSTOM="CUSTOM"

class DataTypes(Enum):
    JSON="JSON"

class MessageSourceType(Enum):
    USER="USER"
    AI="AI"

class ChatHistoryFormatKeys(Enum):
    SOURCE="source"
    MESSAGE="message"

class EntityNames(Enum):
    DATE="DATE"
    DATE_RANGE="DATE RANGE"

ENTITY_PROMPT_TEMPLATE="""
You are highly skilled in understanding human language, analyzing the current user message and chat history context, and extracting the specified entity. Your primary task is to extract the {entity_name} entity from user input based on the provided description and instructions.
 
Entity Details:
- Name: {entity_name}
- Description: {entity_description}
 
Instructions:
{instructions}

Previous value of entity:
{previous_value_of_entity}

 
Output Format JSON:
{output_format}
 
Examples:
{examples}

"""
class DimensionTypeNames(Enum):
    INTENT = "INTENT"

class PromptCategory(Enum):
    IntentClassification = "INTENT_CLASSIFICATION_PROMPT"
    SubIntentClassification="SUB_INTENT_CLASSIFICATION_PROMPT"

class PromptParams(Enum):
    SYSTEM = 'SYSTEM'
