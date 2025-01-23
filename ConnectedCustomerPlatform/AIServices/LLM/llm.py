import os
from .ModelFactory import ModelFactory, LLM_MODEL_MAPPING, EMBEDDING_MODEL_MAPPING


# GPT 4o Mini
GPT4_OPENAI_API_KEY = "DWDh8ZelTMEab6XAys0wo0d4p71l2i58QHe8GTiWOwYo5bHzkTisJQQJ99ALACYeBjFXJ3w3AAABACOGJVPB"
GPT4_OPENAI_DEPLOYMENT_NAME = "vassar-4o-mini"
GPT4_OPENAI_API_BASE = "https://vassar-openai.openai.azure.com/"
GPT4_MODEL_NAME = "gpt-4o-mini"
GPT4_OPENAI_API_TYPE = "azure"
GPT4_OPENAI_API_VERSION = "2024-02-15-preview"

OPENAI_EMBEDDING_MODEL_API_KEY = "DWDh8ZelTMEab6XAys0wo0d4p71l2i58QHe8GTiWOwYo5bHzkTisJQQJ99ALACYeBjFXJ3w3AAABACOGJVPB"
OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME = "vassar-text-ada002"
OPENAI_EMBEDDING_MODEL_API_BASE = "https://vassar-openai.openai.azure.com/"
OPENAI_EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
OPENAI_EMBEDDING_API_TYPE = "azure"



gpt4_llm_params = {
    "deployment_name":GPT4_OPENAI_DEPLOYMENT_NAME,
    "model_name":GPT4_MODEL_NAME,
    "azure_endpoint":GPT4_OPENAI_API_BASE,
    "openai_api_type":GPT4_OPENAI_API_TYPE,
    "openai_api_key":GPT4_OPENAI_API_KEY,
    "openai_api_version":GPT4_OPENAI_API_VERSION,
    "temperature" :0.0
}



embeddings_params = {
    "deployment":OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME,
    "model":OPENAI_EMBEDDING_MODEL_NAME,
    "azure_endpoint":OPENAI_EMBEDDING_MODEL_API_BASE,
    "openai_api_type":OPENAI_EMBEDDING_API_TYPE,
    "openai_api_key":OPENAI_EMBEDDING_MODEL_API_KEY
}


llm_factory = ModelFactory(LLM_MODEL_MAPPING)
llm = llm_factory.create_model_instance(model_map_name="AzureChatOpenAI",**gpt4_llm_params)

embeddings_factory = ModelFactory(EMBEDDING_MODEL_MAPPING)
embeddings = embeddings_factory.create_model_instance(model_map_name="AzureOpenAIEmbeddings", **embeddings_params)

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
def get_human_message(content):
    return HumanMessage(content=content)

def get_system_message(prompt):
    return SystemMessage(content=prompt)

def get_ai_message(content):
    return AIMessage(content=content)