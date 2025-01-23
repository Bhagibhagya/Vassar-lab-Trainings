import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

import json
import time
import asyncio
import traceback
import logging

from langchain_openai.chat_models.azure import AzureChatOpenAI
from openai._exceptions import APITimeoutError, RateLimitError

from ce_shared_services.exceptions.exceptions import LLMException

from ce_shared_services.llm.interface.llm import LLM

logger = logging.getLogger(__name__)


class AzureOpenAILLM(LLM):
    
    _JSON_MODE = False
    _INITIAL_DELAY = 2
    _MAX_RETRIES = 2
    _EXPONENT_BASE = 2
    _TEMPERATURE = 0.0
    
    def __init__(
        self,
        deployment_name : str,
        model_name : str,
        endpoint : str,
        api_type :str,
        api_key : str,
        api_version : str,
        temperature : float = _TEMPERATURE
    ):
      
        self.deployment_name = deployment_name,
        self.model_name = model_name
        self.endpoint = endpoint
        self.api_type = api_type
        self.api_key = api_key
        self.api_version = api_version
        self.temperature = temperature
        
        self._api_client = AzureChatOpenAI(
            deployment_name=deployment_name,
            model_name=model_name,
            azure_endpoint=endpoint,
            openai_api_type=api_type,
            openai_api_key=api_key,
            openai_api_version=api_version,
            temperature=temperature
        )
    
    def _backoff(self, initial_delay, max_retries, retries_left):
        
        return initial_delay + (AzureOpenAILLM._EXPONENT_BASE ** (2 + max_retries - retries_left))
    
    def _run_sync(self, prompt, json_mode, max_retries, retries_left, initial_delay):

        try:
            
            kwargs = {}
            if json_mode:
                kwargs.update(response_format={"type" : "json_object"})
                
            response = self._api_client.invoke(prompt, **kwargs)
            
            if json_mode:
                
                logger.debug('loading the json content to validate json structure')
                json.loads(response.content)
            
            return response.content
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _run_sync :: raising LLMException')
                
                raise LLMException(*retryable_exception.args)
            
            time.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return self._run_sync(prompt, json_mode, max_retries, retries_left-1, initial_delay)  

        except json.JSONDecodeError as json_decode_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _run_sync :: json decode error, raising LLMException')
                
                raise LLMException(*json_decode_exception.args)
        
            time.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return self._run_sync(prompt, json_mode, max_retries, retries_left-1, initial_delay)
    
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _run_sync :: raising LLMException')
            
            raise LLMException(*non_retryable_exception.args)      
           
    def run_sync(self, prompt: str, json_mode: bool = _JSON_MODE, max_retries: int = _MAX_RETRIES, initial_delay : int = _INITIAL_DELAY):
        
        logger.info("In AzureOpenAILLM class :: run_sync method")
        
        retries_left = max_retries + 1
        return self._run_sync(prompt, json_mode, max_retries, retries_left, initial_delay)
                
    async def _run_async(self, prompt, json_mode, max_retries, retries_left, initial_delay):
        
        try:
            
            kwargs = {}
            if json_mode:
                kwargs.update(response_format={"type" : "json_object"})
            
            response = await self._api_client.ainvoke(prompt, **kwargs)
            
            if json_mode:
                
                logger.debug('loading the json content to validate json structure')
                json.loads(response.content)
            
            return response.content
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _run_async :: raising LLMException')
                
                raise LLMException(*retryable_exception.args)
            
            await asyncio.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return await self._run_async(prompt, json_mode, max_retries, retries_left-1, initial_delay) 
    
        except json.JSONDecodeError as json_decode_exception:
            
            if retries_left == 1:
                
                logger.error(traceback.format_exc())
                logger.info('In _run_async :: json decode error, raising LLMException')
                
                raise LLMException(*json_decode_exception.args)
        
            await asyncio.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return await self._run_async(prompt, json_mode, max_retries, retries_left-1, initial_delay) 
    
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _run_async :: raising LLMException')
            
            raise LLMException(*non_retryable_exception.args)  

    async def run_async(self, prompt: str, json_mode: bool = _JSON_MODE, max_retries: int = _MAX_RETRIES, initial_delay : int = _INITIAL_DELAY):
        
        logger.info("In AzureOpenAILLM class :: run_async method")
        
        retries_left = max_retries + 1
        return await self._run_async(prompt, json_mode, max_retries, retries_left, initial_delay)
    
    def _stream_sync(self, prompt, json_mode, max_retries, retries_left, initial_delay):
        
        try:
            
            kwargs = {}
            if json_mode:
                kwargs.update(response_format={"type" : "json_object"})
            
            iterator = self._api_client.stream(prompt, **kwargs)
            for chunk in iterator:
                yield chunk.content
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:
    
                logger.error(traceback.format_exc())
                logger.info('In _stream_sync :: raising LLMException')            
        
                raise LLMException(*retryable_exception.args)
            
            time.sleep(self._backoff(initial_delay, max_retries, retries_left))
            return self._stream_sync(prompt, json_mode, max_retries, retries_left-1, initial_delay)   
    
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _stream_sync :: raising LLMException')
            
            raise LLMException(*non_retryable_exception.args)   
    
    def stream_sync(self, prompt: str, json_mode: bool = _JSON_MODE, max_retries: int = _MAX_RETRIES, initial_delay: int = _INITIAL_DELAY):
        
        logger.info("In AzureOpenAILLM class :: stream_sync method")
        
        retries_left = max_retries + 1
        return self._stream_sync(prompt, json_mode, max_retries, retries_left, initial_delay)
    
    async def _stream_async(self, prompt, json_mode, max_retries, retries_left, initial_delay):
        
        try:
            
            kwargs = {}
            if json_mode:
                kwargs.update(response_format={"type" : "json_object"})
            
            aiterator = self._api_client.astream(prompt, **kwargs)
            async for chunk in aiterator:
                yield chunk.content
            
        except (APITimeoutError, RateLimitError) as retryable_exception:
            
            if retries_left == 1:

                logger.error(traceback.format_exc())
                logger.info('In _stream_async :: raising LLMException')                

                raise LLMException(*retryable_exception.args)
            
            await asyncio.sleep(self._backoff(initial_delay, max_retries, retries_left))
            
            aiterator = self._stream_async(prompt, json_mode, max_retries, retries_left-1, initial_delay) 
            async for content in aiterator:
                yield content
                
        except Exception as non_retryable_exception:
            
            logger.error(traceback.format_exc())
            logger.info('In _stream_async :: raising LLMException')
            
            raise LLMException(*non_retryable_exception.args)  
    
    async def stream_async(self, prompt: str, json_mode: bool = _JSON_MODE, max_retries: int = _MAX_RETRIES, initial_delay: int = _INITIAL_DELAY):
        
        logger.info("In AzureOpenAILLM class :: stream_async method")
        
        retries_left = max_retries + 1
        return self._stream_async(prompt, json_mode, max_retries, retries_left, initial_delay)

    def __hash__(self) -> int:
        
        config = {
            'deployment_name': self.deployment_name,
            'model_name': self.model_name,
            'endpoint': self.endpoint,
            'api_type': self.api_type,
            'api_key': self.api_key,
            'api_version': self.api_version,
            'temperature': self.temperature
        }
        return frozenset(config.items()).__hash__()