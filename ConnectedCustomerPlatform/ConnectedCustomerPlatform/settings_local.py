import os
import dj_db_conn_pool
from dotenv import load_dotenv
from ConnectedCustomerPlatform.settings import *

load_dotenv()
load_dotenv('.env.local')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
IDENTITY_CLIENT_ID = os.getenv('IDENTITY_CLIENT_ID')
# Fernet Encryption Key
ENCRYPTION_SECRET_KEY = os.getenv('ENCRYPTION_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['*']

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')
AWS_BUCKET_STORAGE_NAME = os.getenv('AWS_BUCKET_STORAGE_NAME')

# Websocket
WEBSOCKET_BASE_URL = os.getenv('WEBSOCKET_BASE_URL')
WEBSOCKET_PROTOCOL = os.getenv('WEBSOCKET_PROTOCOL')
WEBSOCKET_END_POINT = os.getenv('WEBSOCKET_END_POINT')

# Static data
USERMGMT_API_BASE_URL = os.getenv("USERMGMT_API_BASE_URL")
CONSUMER_EVENT_HUB_NAME = os.getenv('CONSUMER_EVENT_HUB_NAME')

# Configuration settings without keyvault
# DB configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ce_new',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': 5432
    }
}
CRONTAB_COMMAND_PREFIX = 'DJANGO_SETTINGS_MODULE=ConnectedCustomerPlatform.settings_local'

# Azure Storage Configuration
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')

# Redis config
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
REDIS_DECODE_RESPONSES = True
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# Chroma DB config
CHROMADB_PORT = os.getenv('CHROMADB_PORT')
CHROMADB_HOST = os.getenv('CHROMADB_HOST')
CHROMADB_NAME = os.getenv('CHROMADB_NAME')
CHROMADB_CLASS_NAME =os.getenv('CHROMADB_CLASS_NAME')
DEFAULT_ENTITY_COLLECTION_NAME=os.getenv('DEFAULT_ENTITY_COLLECTION_NAME')
FILE_CONSUMER_EVENT_TOPIC = os.getenv('FILE_CONSUMER_EVENT_TOPIC')
LLM_AGENT_EVENT_TOPIC = os.getenv('LLM_AGENT_EVENT_TOPIC')

# phone config secrets
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
VERSION = os.getenv('VERSION')

# whatsapp config secrets
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_CLEANUP_INTERVAL_SECONDS = os.getenv('WHATSAPP_CLEANUP_INTERVAL_SECONDS')
WHATSAPP_INACTIVE_USER_THRESHOLD_MINUTES = os.getenv('WHATSAPP_INACTIVE_USER_THRESHOLD_MINUTES')
WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION')

# Teams cred
APP_ID = os.getenv('APP_ID')
APP_PASSWORD = os.getenv('APP_PASSWORD')

#response config azure blob url 
#should upload in new container and change url if container changes
RESPONSE_CONFIGS_TEMPLATE_URL=os.getenv("RESPONSE_CONFIGS_TEMPLATE_URL")    
BLOB_SERVICE_URL = os.getenv("BLOB_SERVICE_URL")



# REDIS CACHE CONFIGURATION
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "db": "1",
            "pool_class": "redis.BlockingConnectionPool",
        },
    }
}

SME_EDIT_RESOURCE_ACTION_ID = os.getenv("SME_EDIT_RESOURCE_ACTION_ID")
QA_EDIT_RESOURCE_ACTION_ID = os.getenv("QA_EDIT_RESOURCE_ACTION_ID")

CONNECTED_ENTERPRISE_APP_ID = os.getenv("CONNECTED_ENTERPRISE_APP_ID")

USERMGMT_AUTH_URL = 'http://localhost:8081/um/multi-resource-auth'

CONSUMER_EVENT_HUB_NAME = os.getenv('CONSUMER_EVENT_HUB_NAME')
EVENTHUB_CONNECTION_STR = os.getenv('EVENTHUB_CONNECTION_STR')
CHECKPOINT_STORAGE_CONNECTION_STR = os.getenv('CHECKPOINT_STORAGE_CONNECTION_STR')
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
EMAIL_PDF_PROCESSING_EVENTHUB_TOPIC = os.getenv("EMAIL_PDF_PROCESSING_EVENTHUB_TOPIC")

FULLY_QUALIFIED_NAMESPACE = os.getenv("FULLY_QUALIFIED_NAMESPACE")
SAS_KEY = os.getenv("SAS_KEY")
STORAGE_CONFIG = {
    'azure_connection_string': AZURE_CONNECTION_STRING,
    'container_name': AZURE_CONTAINER,
    'max_retries': 3,
    'initial_backoff': 1,
    'increment_base': 2,
    'memory_limit': 5*1024*1024*1024*1024,
    'max_single_put_size': 5*1024*1024*1024,
    'max_single_get_size': 5*1024*1024*1024,
    'max_chunk_get_size': 5*1024*1024,
    'max_block_size': 5*1024*1024
}

TRAINING_PHRASES_IMPORT_TEMPLATE = os.getenv("TRAINING_PHRASES_IMPORT_TEMPLATE")

TEXT_ADA_002_EMBEDDING_DEPLOYMENT_NAME = 'vassar-text-ada002'
TEXT_ADA_002_EMBEDDING_MODEL_NAME = 'text-embedding-ada-002'
TEXT_ADA_002_EMBEDDING_API_ENDPOINT = 'https://vassar-openai.openai.azure.com/'
TEXT_ADA_002_EMBEDDING_API_KEY = 'DWDh8ZelTMEab6XAys0wo0d4p71l2i58QHe8GTiWOwYo5bHzkTisJQQJ99ALACYeBjFXJ3w3AAABACOGJVPB'
TEXT_ADA_002_EMBEDDING_API_TYPE = 'azure'
TEXT_ADA_002_EMBEDDING_API_VERSION = '2023-07-01-preview'

EMBEDDING_CLASS_NAME = 'AzureOpenAIEmbeddingModel'
EMBEDDING_CONFIG = {
    'deployment_name': TEXT_ADA_002_EMBEDDING_DEPLOYMENT_NAME,
    'model_name': TEXT_ADA_002_EMBEDDING_MODEL_NAME,
    'endpoint': TEXT_ADA_002_EMBEDDING_API_ENDPOINT,
    'api_type': TEXT_ADA_002_EMBEDDING_API_TYPE,
    'api_key': TEXT_ADA_002_EMBEDDING_API_KEY,
    'api_version': TEXT_ADA_002_EMBEDDING_API_VERSION,
}



GPT4OMINI_OPENAI_API_KEY = "DWDh8ZelTMEab6XAys0wo0d4p71l2i58QHe8GTiWOwYo5bHzkTisJQQJ99ALACYeBjFXJ3w3AAABACOGJVPB"
GPT4OMINI_OPENAI_DEPLOYMENT_NAME = "vassar-4o-mini"
GPT4OMINI_OPENAI_API_BASE = "https://vassar-openai.openai.azure.com/"
GPT4OMINI_OPENAI_MODEL_NAME = "gpt-4o-mini"
GPT4OMINI_OPENAI_API_TYPE = "azure"
GPT4OMINI_OPENAI_API_VERSION = "2024-02-15-preview"
GPT4OMINI_OPENAI_TEMPERATURE = 0.0

LLM_CLASS_NAME = 'AzureOpenAILLM'
LLM_MAX_RETRIES = 2
LLM_INITIAL_DELAY = 1
LLM_CONFIG = {
    'deployment_name': GPT4OMINI_OPENAI_DEPLOYMENT_NAME,
    'model_name': GPT4OMINI_OPENAI_MODEL_NAME,
    'endpoint': GPT4OMINI_OPENAI_API_BASE,
    'api_type': GPT4OMINI_OPENAI_API_TYPE,
    'api_key': GPT4OMINI_OPENAI_API_KEY,
    'api_version': GPT4OMINI_OPENAI_API_VERSION,
    'temperature': GPT4OMINI_OPENAI_TEMPERATURE
}
