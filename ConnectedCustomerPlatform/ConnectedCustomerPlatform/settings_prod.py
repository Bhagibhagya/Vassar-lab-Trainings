import os
import dj_db_conn_pool
from dotenv import load_dotenv
from ConnectedCustomerPlatform.settings import *

ALLOWED_HOSTS = ['*']
load_dotenv('.env')
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.prod')
load_dotenv(env_path)
AZURE_KEY_VAULT_URL = os.getenv('AZURE_KEY_VAULT_URL')
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
IDENTITY_CLIENT_ID = os.getenv('IDENTITY_CLIENT_ID')

from ConnectedCustomerPlatform.azure_key_vault_config import SecretClientService

# Fernet Encryption Key
ENCRYPTION_SECRET_KEY = SecretClientService.get_secret(os.getenv('ENCRYPTION_SECRET_KEY'))

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
db_config = SecretClientService.get_secret_json(os.getenv('DB_CONFIG_SECRET_NAME'))
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

# Azure Storage Configuration
azure_storage_config = SecretClientService.get_secret_json(os.getenv('AZURE_STORAGE_CONFIG_SECRET_NAME'))
AZURE_CONNECTION_STRING = azure_storage_config['connection_string']
AZURE_CONTAINER = azure_storage_config['container_name']

# Redis config
redis_config = SecretClientService.get_secret_json(os.getenv('REDIS_CONFIG_SECRETS'))
REDIS_HOST = redis_config['redis_host']
REDIS_PORT = int(redis_config['redis_port'])  # Convert to integer
REDIS_DB = int(redis_config['redis_db'])  # Convert to integer
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
chroma_db_config = SecretClientService.get_secret_json(os.getenv('CHROMA_DB_CONFIG_SECRET_NAME'))
CHROMADB_PORT = chroma_db_config['chromadb_port']
CHROMADB_HOST = chroma_db_config['chromadb_host']
CHROMADB_NAME = chroma_db_config['chromadb_name']
FILE_CONSUMER_EVENT_TOPIC = chroma_db_config['file_consumer_event_topic']
LLM_AGENT_EVENT_TOPIC = chroma_db_config['llm_agent_event_topic']

# phone config secrets
phone_config = SecretClientService.get_secret_json(os.getenv('PHONE_CONFIG_SECRETS'))
PHONE_NUMBER_ID = phone_config['phone_number_id']
VERSION = phone_config['version']

# whatsapp config secrets
whatsapp_config = SecretClientService.get_secret_json(os.getenv('WHATSAPP_CONFIG_SECRETS'))
WHATSAPP_VERIFY_TOKEN = whatsapp_config['whatsapp_verify_token']
WHATSAPP_ACCESS_TOKEN = whatsapp_config['whatsapp_access_token']
WHATSAPP_CLEANUP_INTERVAL_SECONDS = whatsapp_config['whatsapp_cleanup_interval_seconds']
WHATSAPP_INACTIVE_USER_THRESHOLD_MINUTES = whatsapp_config['whatsapp_inactive_user_threshold_minutes']
WHATSAPP_API_VERSION = whatsapp_config['whatsapp_api_version']

# Teams cred
microsoft_secrets = SecretClientService.get_secret_json(os.getenv('MICROSOFT_SECRETS'))
APP_ID = microsoft_secrets["MicrosoftAppId"]
APP_PASSWORD = microsoft_secrets["MicrosoftAppPassword"]

# response config azure blob url
# should upload in new container and change url if container changes
RESPONSE_CONFIGS_TEMPLATE_URL = os.getenv("RESPONSE_CONFIGS_TEMPLATE_URL")
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

# U
USERMGMT_AUTH_URL = 'https://ce.vassardigital.ai/um/multi-resource-auth'

FULLY_QUALIFIED_NAMESPACE = os.getenv("FULLY_QUALIFIED_NAMESPACE")
SAS_KEY = os.getenv("SAS_KEY")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")