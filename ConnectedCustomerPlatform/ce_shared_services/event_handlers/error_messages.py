from enum import Enum


class IntentClassificationHandler(Enum):
    SYSTEM_MESSAGE_NOT_FOUND = "SYSTEM message not found in the Prompt"
    SUB_INTENT_PROMPT_UNIDENTIFIED = "Sub-Intent Prompt Not Found"
    INVALID_SUB_INTENT_CONFIG="Invalid sub-intent details in SubIntentConfig"