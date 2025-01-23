import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

import traceback
import logging
from typing import Union

from ce_shared_services.datatypes.datatypes import Chunk
from ce_shared_services.llm.interface.llm import LLM
from ce_shared_services.reranking.interface.reranker import Reranker
from ce_shared_services.exceptions.exceptions import LLMException, RerankingException

logger = logging.getLogger(__name__)


class ParallelLLMReranker(Reranker):
    
    _THREAD_POOL_MAX_WORKERS = 5
    _PROMPT = """ 
System: You are an advanced relevance identification bot. 
Given a passage and a question, identify whether the passage is relevant or similar to the question or
includes an answer to the question or is important in generating an answer to the question.
Provide a response with either `Yes` or `No`.

Passage:
{}

Query:
{}
"""

    def __init__(self, llm : LLM):
        
        self._llm = llm
     
    def _llm_call_sync(self, prompt):
        
        return self._llm.run_sync(prompt)

    async def _llm_call_async(self, prompt):
        
        return await self._llm.run_async(prompt)
    
    def _parse_llm_responses(self, llm_responses : list[str]):
        
        return [ response.strip().lower() == 'yes' for response in llm_responses ] 
    
    def _get_reranked_chunks(self, llm_responses : list[str], chunks : list[Chunk], top_n : Union[int, None]):
        
        boolean_responses = self._parse_llm_responses(llm_responses)
        
        reranked_chunks = []
        for i, boolean in enumerate(boolean_responses):
            
            if boolean:
                reranked_chunks.append(chunks[i])
        
        if top_n is None or top_n <= len(reranked_chunks):
            return reranked_chunks
    
        for chunk in chunks:
            
            if chunk not in reranked_chunks:
                reranked_chunks.append(chunk)
                
                if len(reranked_chunks) == top_n:
                    break
        
        return reranked_chunks
      
    async def rerank_async(self, query: str, chunks: list[Chunk], top_n: Union[int, None] = None) -> list[Chunk]:
        
        logger.info('In ParallelLLMReranker class :: rerank_async method')
        
        try:
            tasks = []
            for chunk in chunks:
                
                prompt = ParallelLLMReranker._PROMPT.format(chunk.document, query)
                task = asyncio.create_task(self._llm_call_async(prompt))
                tasks.append(task)
            
            llm_responses = await asyncio.gather(*tasks)
            
            logger.info(f'llm response for reranking :: {llm_responses}')
            return self._get_reranked_chunks(llm_responses, chunks, top_n)
        
        except LLMException as llm_exception:
            
            logger.info('LLMException in rerank_async method')
            raise llm_exception

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In rerank_async raising RerankingException')
            
            raise RerankingException(*exception.args)
    
    def rerank_sync(self, query: str, chunks: list[Chunk], top_n: Union[int, None] = None) -> list[Chunk]:
        
        logger.info('In ParallelLLMReranker class :: rerank_sync method')
        
        try:
            
            with ThreadPoolExecutor(max_workers=ParallelLLMReranker._THREAD_POOL_MAX_WORKERS) as executor:
                
                future_index_map = {}
                for i, chunk in enumerate(chunks):
                    
                    prompt = ParallelLLMReranker._PROMPT.format(chunk.document, query)
                    future = executor.submit(self._llm_call_sync, prompt)
                    future_index_map[future] = i

                index_result_map = {}
                for future in as_completed(future_index_map):
                    
                    index = future_index_map[future]
                    index_result_map[index] = future.result()
            
            llm_responses = [ index_result_map[i] for i in range(len(chunks))]
            
            logger.info(f'llm response for reranking :: {llm_responses}')        
            return self._get_reranked_chunks(llm_responses, chunks, top_n)
        
        except LLMException as llm_exception:
            
            logger.info('LLMException in rerank_sync method')
            raise llm_exception

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In rerank_sync raising RerankingException')
            
            raise RerankingException(*exception.args)