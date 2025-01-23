import os
import dj_db_conn_pool
from dotenv import load_dotenv
from ConnectedCustomerPlatform.settings import *
from ce_shared_services.factory.key_vault.keyvault_factory import KeyVaultFactory
from ce_shared_services.configuration_models.configuration_models import AzureKeyVaultConfig

ALLOWED_HOSTS = ['*']
load_dotenv('.env')
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.qa')
load_dotenv(env_path)
AZURE_KEY_VAULT_URL = os.getenv('AZURE_KEY_VAULT_URL')
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
IDENTITY_CLIENT_ID = os.getenv('IDENTITY_CLIENT_ID')

config = {
    "vault_url": AZURE_KEY_VAULT_URL,
    "client_id": IDENTITY_CLIENT_ID
}
azure_secret = KeyVaultFactory.instantiate("AzureKeyVaultService", AzureKeyVaultConfig(**config))

# Fernet Encryption Key
ENCRYPTION_SECRET_KEY = azure_secret.get_secret(os.getenv('ENCRYPTION_SECRET_KEY'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = "us-west-2"
AWS_BUCKET_STORAGE_NAME = "connected-customer"

# Websocket
WEBSOCKET_BASE_URL = os.getenv('WEBSOCKET_BASE_URL')
WEBSOCKET_PROTOCOL = os.getenv('WEBSOCKET_PROTOCOL')
WEBSOCKET_END_POINT = os.getenv('WEBSOCKET_END_POINT')

# Static data
USERMGMT_API_BASE_URL = os.getenv("USERMGMT_API_BASE_URL")
CONSUMER_EVENT_HUB_NAME = os.getenv('CONSUMER_EVENT_HUB_NAME')

# Configuration settings using key vault
# DB configuration
db_config = azure_secret.get_secret_as_json(os.getenv('DB_CONFIG_SECRET_NAME'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_config['db_name'],
        'USER': db_config['db_user'],
        'PASSWORD': db_config['db_password'],
        'HOST': db_config['db_host'],
        'PORT': db_config['db_port']
    }
}

CRONTAB_COMMAND_PREFIX = 'DJANGO_SETTINGS_MODULE=ConnectedCustomerPlatform.settings_qa'

# Azure Storage Configuration
azure_storage_config = azure_secret.get_secret_as_json(os.getenv('AZURE_STORAGE_CONFIG_SECRET_NAME'))
AZURE_CONNECTION_STRING = azure_storage_config['connection_string']
AZURE_CONTAINER = azure_storage_config['container_name']

# Redis config
redis_config = azure_secret.get_secret_as_json(os.getenv('REDIS_CONFIG_SECRETS'))
REDIS_HOST = redis_config['redis_host']
REDIS_PORT = int(redis_config['redis_port'])  # Convert to integer
REDIS_DB = int(redis_config['redis_db'])      # Convert to integer
REDIS_DECODE_RESPONSES = redis_config['redis_decode_responses'].lower() == 'true'  # Convert to boolean
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# Chroma DB config
chroma_db_config = azure_secret.get_secret_as_json(os.getenv('CHROMA_DB_CONFIG_SECRET_NAME'))
CHROMADB_PORT = chroma_db_config['chromadb_port']
CHROMADB_HOST = chroma_db_config['chromadb_host']
CHROMADB_NAME = chroma_db_config['chromadb_name']
CHROMADB_CLASS_NAME =os.getenv('CHROMADB_CLASS_NAME')
DEFAULT_ENTITY_COLLECTION_NAME=os.getenv('DEFAULT_ENTITY_COLLECTION_NAME')
FILE_CONSUMER_EVENT_TOPIC = chroma_db_config['file_consumer_event_topic']
LLM_AGENT_EVENT_TOPIC = chroma_db_config['llm_agent_event_topic']

# phone config secrets
phone_config = azure_secret.get_secret_as_json(os.getenv('PHONE_CONFIG_SECRETS'))
PHONE_NUMBER_ID = phone_config['phone_number_id']
VERSION = phone_config['version']

# whatsapp config secrets
whatsapp_config = azure_secret.get_secret_as_json(os.getenv('WHATSAPP_CONFIG_SECRETS'))
WHATSAPP_VERIFY_TOKEN = whatsapp_config['whatsapp_verify_token']
WHATSAPP_ACCESS_TOKEN = whatsapp_config['whatsapp_access_token']
WHATSAPP_CLEANUP_INTERVAL_SECONDS = whatsapp_config['whatsapp_cleanup_interval_seconds']
WHATSAPP_INACTIVE_USER_THRESHOLD_MINUTES = whatsapp_config['whatsapp_inactive_user_threshold_minutes']
WHATSAPP_API_VERSION = whatsapp_config['whatsapp_api_version']

# Teams cred
microsoft_secrets = azure_secret.get_secret_as_json(os.getenv('MICROSOFT_SECRETS'))
APP_ID = microsoft_secrets["MicrosoftAppId"]
APP_PASSWORD = microsoft_secrets["MicrosoftAppPassword"]

#response config azure blob url 
#should upload in new container and change url if container changes
RESPONSE_CONFIGS_TEMPLATE_URL=os.getenv("RESPONSE_CONFIGS_TEMPLATE_URL")
BLOB_SERVICE_URL = os.getenv("BLOB_SERVICE_URL")


# REDIS CACHE CONFIGURATION
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}",
        "OPTIONS": {
            "db": "1",
            "pool_class": "redis.BlockingConnectionPool",
        },
    }
}


SME_EDIT_RESOURCE_ACTION_ID = os.getenv("SME_EDIT_RESOURCE_ACTION_ID")
QA_EDIT_RESOURCE_ACTION_ID = os.getenv("QA_EDIT_RESOURCE_ACTION_ID")

CONNECTED_ENTERPRISE_APP_ID = os.getenv("CONNECTED_ENTERPRISE_APP_ID")

USERMGMT_AUTH_URL = 'https://qa.ce.vassardigital.ai/um/multi-resource-auth'

CONSUMER_EVENT_HUB_NAME = os.getenv('CONSUMER_EVENT_HUB_NAME')

EVENTHUB_CONNECTION_STR = os.getenv('EVENTHUB_CONNECTION_STR')
CHECKPOINT_STORAGE_CONNECTION_STR = os.getenv('CHECKPOINT_STORAGE_CONNECTION_STR')

FULLY_QUALIFIED_NAMESPACE = os.getenv("FULLY_QUALIFIED_NAMESPACE")
SAS_KEY = os.getenv("SAS_KEY")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
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

EMAIL_PDF_PROCESSING_EVENTHUB_TOPIC = os.getenv("EMAIL_PDF_PROCESSING_EVENTHUB_TOPIC")



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