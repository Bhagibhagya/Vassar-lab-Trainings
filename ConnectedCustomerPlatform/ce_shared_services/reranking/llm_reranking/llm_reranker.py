import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

import logging
import traceback
from typing import Union

from ce_shared_services.datatypes.datatypes import Chunk
from ce_shared_services.llm.interface.llm import LLM
from ce_shared_services.reranking.interface.reranker import Reranker
from ce_shared_services.exceptions.exceptions import LLMException, RerankingException

logger = logging.getLogger(__name__)


class LLMReranker(Reranker):
    
    _PROMPT = """
System: 
You are an advanced relevance identififcation bot. You will be given 30 context documents along awith a query.
Each of the context document will have an id i.e., a number identifier [].
You have to analyze all the context documents with the query and identify a list of documents that are
relevant or in importance to answer that particular query.
Just provide a list of comma separated ids such that they are the most relevant documents for the query.
Limit the no. of ids you respond with to 10. You have top provide the top 10 relevant document ids.

Context Documents:
{}

Query:
{}

Ensure that the most relevant documents are provided as the response.
Only provide the comma separated ids as the response. 
"""

    def __init__(self, llm : LLM):
    
        self._llm = llm

    def _get_prompt(self, query : str, chunks : list[Chunk]):

        docs_string = ""
        for i, chunk in enumerate(chunks): 
            docs_string += f"[{str(i+1)}] " + chunk.document + "\n\n"
        
        prompt = LLMReranker._PROMPT.format(docs_string, query)
        return prompt
        
    def _parse_ids_string(self, ids_string : str):
        
        ids_string = ids_string.replace('[', '').replace(']', '').strip()
        ids = ids_string.split(',')
        ids = [int(id.strip()) for id in ids]
        return ids
        
    def _get_reranked_chunks(self, llm_response : str, chunks : list, top_n : Union[int, None]):
        
        indices = self._parse_ids_string(llm_response)

        reranked_chunks = []
        for index in indices:
            index -= 1
            
            if index >=0 and index < len(chunks):
                reranked_chunks.append(chunks[index])
        
        if top_n is None or top_n <= len(reranked_chunks):
            return reranked_chunks
                
        for chunk in chunks:
            
            if chunk not in reranked_chunks:
                reranked_chunks.append(chunk)
                
                if len(reranked_chunks) == top_n:
                    break
            
        return reranked_chunks

    def rerank_sync(self, query: str, chunks: list[Chunk], top_n: Union[int, None] = None) -> list[Chunk]:

        logger.info('In LLMReranker :: rerank_sync method')

        try:
            prompt = self._get_prompt(query, chunks)
            llm_response = self._llm.run_sync(prompt)
            
            logger.info(f'llm response for reranking :: {llm_response}')
            return self._get_reranked_chunks(llm_response, chunks, top_n)
    
        except LLMException as llm_exception:
          
            logger.info('LLMException in rerank_sync method')  
            raise llm_exception
    
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In rerank_sync raising RerankingException')
            
            raise RerankingException(*exception.args)
        
    async def rerank_async(self, query: str, chunks: list[Chunk], top_n: Union[int, None] = None) -> list[Chunk]:

        logger.info('In LLMReranker :: rerank_async method')

        try:
            prompt = self._get_prompt(query, chunks)
            llm_response = await self._llm.run_async(prompt)
            
            logger.info(f'llm response for reranking :: {llm_response}')
            return self._get_reranked_chunks(llm_response, chunks, top_n)
    
        except LLMException as llm_exception:
          
            logger.info('LLMException in rerank_async method')  
            raise llm_exception

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In rerank_async raising RerankingException')
            
            raise RerankingException(*exception.args)