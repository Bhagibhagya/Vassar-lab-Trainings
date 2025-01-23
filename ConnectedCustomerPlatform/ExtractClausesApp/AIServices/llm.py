from langchain.chat_models import AzureChatOpenAI

gpt_config = {
    "4omini": {
        "OPENAI_API_KEY" : "DWDh8ZelTMEab6XAys0wo0d4p71l2i58QHe8GTiWOwYo5bHzkTisJQQJ99ALACYeBjFXJ3w3AAABACOGJVPB",
        "OPENAI_DEPLOYMENT_NAME" : "vassar-4o-mini",
        "OPENAI_EMBEDDING_MODEL_NAME": "vassar-text-ada002",
        "OPENAI_API_BASE" : "https://vassar-openai.openai.azure.com/",
        "MODEL_NAME" : "gpt-4o-mini",
        "OPENAI_API_TYPE" : "azure",
        "OPENAI_API_VERSION" : "2024-02-15-preview",
    }
}

config = gpt_config.get("4omini")
# Unpack configuration settings
OPENAI_API_KEY = config["OPENAI_API_KEY"]
OPENAI_DEPLOYMENT_NAME = config["OPENAI_DEPLOYMENT_NAME"]
OPENAI_EMBEDDING_MODEL_NAME = config["OPENAI_EMBEDDING_MODEL_NAME"]
OPENAI_API_BASE = config["OPENAI_API_BASE"]
MODEL_NAME = config["MODEL_NAME"]
OPENAI_API_TYPE = config["OPENAI_API_TYPE"]
OPENAI_API_VERSION = config["OPENAI_API_VERSION"]


# chroma setup
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings
OPENAI_EMBEDDING_API_KEY = "DWDh8ZelTMEab6XAys0wo0d4p71l2i58QHe8GTiWOwYo5bHzkTisJQQJ99ALACYeBjFXJ3w3AAABACOGJVPB"
OPENAI_EMBEDDING_DEPLOYMENT_NAME = "vassar-text-ada002"
OPENAI_EMBEDDING_API_BASE = "https://vassar-openai.openai.azure.com/"
OPENAI_EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
OPENAI_EMBEDDING_API_TYPE = "azure"
OPENAI_EMBEDDING_API_VERSION = "2023-07-01-preview"
OPENAI_EMBEDDING_VALIDATE_BASE_URL = False

embedding_config = {
    'azure_deployment' : OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    'model' : OPENAI_EMBEDDING_MODEL_NAME,
    'azure_endpoint' : OPENAI_EMBEDDING_API_BASE,
    'openai_api_type' : OPENAI_EMBEDDING_API_TYPE,
    'api_key' : OPENAI_EMBEDDING_API_KEY,
    'openai_api_version' : OPENAI_EMBEDDING_API_VERSION,
    'validate_base_url' : OPENAI_EMBEDDING_VALIDATE_BASE_URL
}

embeddings = AzureOpenAIEmbeddings(**embedding_config)


llm = AzureChatOpenAI(
    deployment_name=OPENAI_DEPLOYMENT_NAME,
    model_name=MODEL_NAME,
    azure_endpoint=OPENAI_API_BASE,
    openai_api_type=OPENAI_API_TYPE,
    openai_api_key=OPENAI_API_KEY,
    openai_api_version=OPENAI_API_VERSION,
    temperature=0.0
)
