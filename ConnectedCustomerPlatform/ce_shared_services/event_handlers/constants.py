from enum import Enum


class IntentPrompt(Enum):
    INTENTS = 'INTENTS'
    OTHERS = 'OTHERS'
    OTHERS_DESCRIPTION = 'If the email discussion falls outside the scope of the above INTENTS, classify it as \"OTHERS\".'
    USER_MESSAGE = 'User message'
    INTENTS_IDENTIFIED = 'Intents Identified'
    SUB_INTENTS_IDENTIFIED = 'Sub Intents Identified'
    INTENT_DETAILS='{intent_details}'
    EXAMPLES = '{examples}'
    INTENT = 'intent'
    SUB_INTENT = 'sub_intent'
    INTENT_NAME = '{intent_name}'
    SUB_INTENT_DETAILS = '{sub_intent_details}'


class ChatHistoryFormatKeys(Enum):
    SOURCE="source"
    MESSAGE="message"


class MessageSourceType(Enum):
    USER="user"
    AI="ai"

NO_SIMILAR_QUERIES_FOUND = "No similar queries found."

class ChromadbMetaDataParams(Enum):
    INTENT = "INTENT"
    SUB_INTENT = "SUBINTENT"
    SEPARATOR = ","
    LENGTH_FOR_INTENT = 2
    LENGTH_FOR_SUB_INTENT = 3
    SUB_INTENT_FILTER = "is_subintent"
    CATEGORY = "category"

class PromptParams(Enum):
    SYSTEM='SYSTEM'
    CONTEXT = 'CONTEXT'

class VariableOwner(Enum):
    SYSTEM = 'SYSTEM'

class ChromaOperators:
    AND="$and"
    OR="$or"

class Chromadb(Enum):
    INTENT_CLASSIFICATION_CATEGORY = "intent_classification"

class Variables(Enum):
    INTENT="intent"
    SUB_INTENT = "sub_intent"
class VariableTypes(Enum):
    STRING = "string"
