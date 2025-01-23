import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

import time
import asyncio
import traceback
import logging

from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings
from openai._exceptions import APITimeoutError, RateLimitError

from ce_shared_services.embedding.interface.embedding import EmbeddingModel

from ce_shared_services.exceptions.exceptions import EmbeddingException

logger = logging.getLogger(__name__)


class AzureOpenAIEmbeddingModel(EmbeddingModel):
    
    _INITIAL_DELAY = 2
    _MAX_RETRIES = 2
    _EXPONENT_BASE = 2
    _VALIDATE_BASE = False
    
    def __init__(
        self,
        deployment_name : str,
        model_name : str,
        endpoint : str,
        api_type : str,
        api_key : str,
        api_version : str,
        validate_base : bool = _VALIDATE_BASE
    ):
    
        self.deployment_name = deployment_name,
        self.model_name = model_name
        self.endpoint = endpoint
        self.api_type = api_type
        self.api_key = api_key
        self.api_version = api_version
        self.validate_base = validate_base

        self._api_client = AzureOpenAIEmbeddings(
            azure_deployment=deployment_name,
            model=model_name,
            azure_endpoint=endpoint,
            openai_api_type=api_type,
            api_key=api_key,
            openai_api_version=api_version,
            validate_base_url=validate_base
        )
    
    def _backoff(self, initial_delay, max_retries, retries_left):
        
        return initial_delay + ( AzureOpenAIEmbeddingModel._EXPONENT_BASE ** (2 + max_retries - retries_left) )
    
    def _embed_query_sync(self, query, max_retries, retries_left, initial_delay):
    
        try:
            query_embedding = self._api_client.embed_query(query)
            return query_embedding
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _embed_query_sync :: raising EmbeddingException')
                
                raise EmbeddingException(*retryable_exception.args)
            
            time.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return self._embed_query_sync(query, max_retries, retries_left-1, initial_delay)  
            
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _embed_query_sync :: raising EmbeddingException')
            
            raise EmbeddingException(*non_retryable_exception.args)  
    
    def embed_query_sync(self, query: str, max_retries : int = _MAX_RETRIES, initial_delay : int = _INITIAL_DELAY) -> list[float]:
        
        logger.info('In AzureOpenAIEmbeddingModel class :: embed_query_sync method')
        
        retries_left = max_retries + 1
        return self._embed_query_sync(query, max_retries, retries_left, initial_delay)

    async def _embed_query_async(self, query, max_retries, retries_left, initial_delay):
    
        try:
            query_embedding = await self._api_client.aembed_query(query)
            return query_embedding
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _embed_query_async :: raising EmbeddingException')
                
                raise EmbeddingException(*retryable_exception.args)
            
            await asyncio.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return self._embed_query_sync(query, max_retries, retries_left-1, initial_delay)  
            
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _embed_query_async :: raising EmbeddingException')
            
            raise EmbeddingException(*non_retryable_exception.args)  
    
    async def embed_query_async(self, query: str, max_retries : int = _MAX_RETRIES, initial_delay : int = _INITIAL_DELAY) -> list[float]:
        
        logger.info('In AzureOpenAIEmbeddingModel class :: embed_query_async method')
        
        retries_left = max_retries + 1
        return await self._embed_query_async(query, max_retries, retries_left, initial_delay)
    
    def _embed_documents_sync(self, documents, max_retries, retries_left, initial_delay):
    
        try:
            document_embeddings = self._api_client.embed_documents(documents)
            return document_embeddings
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _embed_documents_sync :: raising EmbeddingException')
                
                raise EmbeddingException(*retryable_exception.args)
            
            time.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return self._embed_documents_sync(documents, max_retries, retries_left-1, initial_delay)  
            
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _embed_documents_sync :: raising EmbeddingException')
            
            raise EmbeddingException(*non_retryable_exception.args)  
    
    def embed_documents_sync(self, documents: list[str], max_retries : int = _MAX_RETRIES, initial_delay : int = _INITIAL_DELAY) -> list[list[float]]:
        
        logger.info('In AzureOpenAIEmbeddingModel class :: embed_documents_sync method')
        
        retries_left = max_retries + 1
        return self._embed_documents_sync(documents, max_retries, retries_left, initial_delay)
    
    async def _embed_documents_async(self, documents, max_retries, retries_left, initial_delay):
    
        try:
            document_embeddings = await self._api_client.aembed_documents(documents)
            return document_embeddings
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _embed_documents_async :: raising EmbeddingException')
                
                raise EmbeddingException(*retryable_exception.args)
            
            await asyncio.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return await self._embed_documents_async(documents, max_retries, retries_left-1, initial_delay)  
            
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _embed_documents_async :: raising EmbeddingException')
            
            raise EmbeddingException(*non_retryable_exception.args)  
    
    async def embed_documents_async(self, documents: list[str], max_retries : int = _MAX_RETRIES, initial_delay : int = _INITIAL_DELAY) -> list[list[float]]:
        
        logger.info('In AzureOpenAIEmbeddingModel class :: embed_documents_async method')
        
        retries_left = max_retries + 1
        return await self._embed_documents_async(documents, max_retries, retries_left, initial_delay)

    def __hash__(self) -> int:
        
        config = {
            'deployment_name' : self.deployment_name,
            'model_name' : self.model_name,
            'endpoint' : self.endpoint,
            'api_type' : self.api_type,
            'api_key' : self.api_key,
            'api_version' : self.api_version,
            'validate_base' : self.validate_base
        }
        return frozenset(config.items()).__hash__()