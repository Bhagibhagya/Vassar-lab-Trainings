from enum import Enum

# Email status codes
class Action(Enum):
    AI_RESPONDED = "AI_RESPONDED"
    AI_ASSISTED = "AI_ASSISTED"
    CSR = "CSR"

class PromptType(Enum):
    Prompt = "PROMPT"
    PromptChain="PROMPT_CHAIN"

class PromptCategory(Enum):
    IntentSentimentClassification = "INTENT_AND_SENTIMENT_CLASSFICATION"
    CustomerGeographyIdentification = "CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION"
    DetailsExtraction = "DETAILS_EXTRACTION"
    SummaryResponseGeneration = "SUMMARY_AND_RESPONSE_GENERATION"

    