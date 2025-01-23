import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from abc import ABC, abstractmethod
from typing import Union

from ce_shared_services.datatypes.datatypes import Chunk


class Reranker(ABC):
    
    """
    Interface for a reranker. The reranker is responsible for 
    reordering or filtering a list of document chunks based on their relevance to a given query.
    """
    
    @abstractmethod
    def rerank_sync(self, query: str, chunks: list[Chunk], top_n: Union[int, None]) -> list[Chunk]:
        """
        Reranks a list of document chunks synchronously based on the provided query.

        Args:
            query (str): The query string used to rerank the chunks.
            chunks (list[Chunk]): A list of document chunks to be reranked.
            top_n (Union[int, None]): The maximum number of top results to return.

        Returns:
            list[Chunk]: A list of chunks reranked based on their relevance to the query.
        """
        pass
    
    @abstractmethod
    async def rerank_async(self, query: str, chunks: list[Chunk], top_n: Union[int, None]) -> list[Chunk]:
        """
        Asynchronously reranks a list of document chunks based on the provided query.

        Args:
            query (str): The query string used to rerank the chunks.
            chunks (list[Chunk]): A list of document chunks to be reranked.
            top_n (Union[int, None]): The maximum number of top results to return.

        Returns:
            list[Chunk]: A list of chunks reranked based on their relevance to the query.
        """
        pass