import os
from pathlib import Path
import warnings
import logging
from langchain._api import LangChainDeprecationWarning

# Ignore specific warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'ConnectedCustomerPlatform.exceptions.custom_exception_handler'
}

# Define the log directory
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Create the log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'django_crontab',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'DBServices',
    'EmailApp',
    'AIServices',
    'ChatBot',
    'drf_yasg',
    'WiseFlow',
    'DatabaseApp',
    'Platform.apps.ClassInitializationConfig',
    'ExtractClausesApp'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    #custome middlewares
    'ConnectedCustomerPlatform.middleware.user_middleware.RequestLoggerMiddleware',
]

ROOT_URLCONF = 'ConnectedCustomerPlatform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRONJOBS = [('*/10 * * * *', 'ChatBot.views.scheduler.run_conversation_scheduler', f'>> {BASE_DIR}/ChatBot/views/scheduler.log 2>&1')]

WSGI_APPLICATION = 'ConnectedCustomerPlatform.wsgi.application'
ASGI_APPLICATION = 'ConnectedCustomerPlatform.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'no_warnings': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno < logging.WARNING,
        },
    },
    'handlers': {
        'console_error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['no_warnings'],
        },
        'console_info': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'azure': {
            'handlers': ['console_error', 'console_info'],
            'level': 'INFO',  # INFO level captures both INFO and ERROR
            'propagate': True,
        },
        'langchain_core': {
            'handlers': ['console_error', 'console_info'],
            'level': 'INFO',  # INFO level captures both INFO and ERROR
            'propagate': False,
        },
        'chromadb': {
            'handlers': ['console_error', 'console_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'StorageServices': {
            'handlers': ['console_error', 'console_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['console_error', 'console_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'warnings': {
            'handlers': ['console_error'],
            'level': 'ERROR',  # Set to ERROR to suppress lower-level warnings
            'propagate': False,
        },
    }
}


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

SERVICES = {
    'knowledge_source_service': 'ChatBot.services.impl.knowledge_source_service_impl.KnowledgeSourceServiceImpl',
    'entity_service':'ChatBot.services.impl.entity_service_impl.EntityServiceImpl',
}

DAO={
    'knowledge_source_dao': 'ChatBot.dao.impl.knowledge_sources_dao_impl.KnowledgeSourcesDaoImpl',
    'error_dao':'ChatBot.dao.impl.error_dao_impl.ErrorCorrectionDaoImpl',
    'entity_dao':'ChatBot.dao.impl.entity_dao_impl.EntityDaoImpl',
    'media_dao':'ChatBot.dao.impl.media_dao_impl.MediaDaoImpl',
    'sme_dao':'ChatBot.dao.impl.sme_dao_impl.SMEDaoImpl',
}

MAXIMUM_IMAGE_SIZE = 5


OPENAI_EMBEDDING_API_KEY = "DWDh8ZelTMEab6XAys0wo0d4p71l2i58QHe8GTiWOwYo5bHzkTisJQQJ99ALACYeBjFXJ3w3AAABACOGJVPB"
OPENAI_EMBEDDING_DEPLOYMENT_NAME = "vassar-text-ada002"
OPENAI_EMBEDDING_API_BASE = "https://vassar-openai.openai.azure.com/"
OPENAI_EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
OPENAI_EMBEDDING_API_TYPE = "azure"
OPENAI_EMBEDDING_API_VERSION = "2023-07-01-preview"
OPENAI_EMBEDDING_VALIDATE_BASE_URL = False

EMBEDDING_CLASS_NAME = 'AzureOpenAIEmbeddingModel'
EMBEDDING_CONFIG = {
    'deployment_name' : OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    'model_name' : OPENAI_EMBEDDING_MODEL_NAME,
    'endpoint' : OPENAI_EMBEDDING_API_BASE,
    'api_type' : OPENAI_EMBEDDING_API_TYPE,
    'api_key' : OPENAI_EMBEDDING_API_KEY,
    'api_version' : OPENAI_EMBEDDING_API_VERSION,
    'validate_base' : OPENAI_EMBEDDING_VALIDATE_BASE_URL
}

VECTORDB_CLASS_NAME = 'ChromaDB'