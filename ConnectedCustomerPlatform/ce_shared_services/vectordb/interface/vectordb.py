import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from abc import ABC, abstractmethod
from typing import Union

from ce_shared_services.datatypes.datatypes import Chunk, ScoredChunk


class VectorDB(ABC):
    
    """
    Interface for a Vector Database client. A vector database client is responsible interacting
    with a vector database for CRUD operations, similarity search.
    """

    @abstractmethod
    def create_collection_sync(self, collection_name: str) -> None:
        """
        Creates a new collection in the database synchronously.

        Args:
            collection_name (str): The name of the collection to be created.
        """
        pass

    @abstractmethod
    def delete_collection_sync(self, collection_name: str) -> None:
        """
        Deletes an existing collection from the database synchronously.

        Args:
            collection_name (str): The name of the collection to be deleted.
        """
        pass

    @abstractmethod
    def rename_collection_sync(self, collection_name: str, new_name: str) -> None:
        """
        Renames an existing collection in the database synchronously.

        Args:
            collection_name (str): The current name of the collection.
            new_name (str): The new name for the collection.
        """
        pass

    @abstractmethod
    def get_collection_count_sync(self, collection_name: str) -> int:
        """ 
        Retrieves the number of records in a collection synchronously.
        
        Args:
            collection_name (str): The name of the collection.
        """
        pass

    @abstractmethod
    def add_chunks_sync(self, collection_name: str, chunks: list[Chunk]) -> None:
        """
        Adds a list of chunks to a collection synchronously.

        Args:
            collection_name (str): The name of the collection to which the chunks will be added.
            chunks (list[Chunk]): A list of chunks to add to the collection.
        """
        pass

    @abstractmethod
    async def add_chunks_async(self, collection_name: str, chunks: list[Chunk]) -> None:
        """
        Adds a list of chunks to a collection asynchronously.

        Args:
            collection_name (str): The name of the collection to which the chunks will be added.
            chunks (list[Chunk]): A list of chunks to add to the collection.
        """
        pass

    @abstractmethod
    def get_by_ids_sync(self, collection_name: str, ids: list[str]) -> list[Chunk]:
        """
        Retrieves chunks by their IDs from a collection synchronously.

        Args:
            collection_name (str): The name of the collection to retrieve chunks from.
            ids (list[str]): A list of chunk IDs to retrieve.
        
        Returns:
            list[Chunk]: A list of chunks corresponding to the provided IDs.
        """
        pass

    @abstractmethod
    def get_by_filter_sync(self, collection_name: str, filter: Union[dict, None]) -> list[Chunk]:
        """
        Retrieves chunks from a collection based on a filter synchronously.

        Args:
            collection_name (str): The name of the collection to retrieve chunks from.
            filter (Union[dict, None]): A filter in dictionary form to filter the chunks.
        
        Returns:
            list[Chunk]: A list of chunks that match the filter.
        """
        pass

    @abstractmethod
    def similarity_search_sync(self, collection_name: str, query: str, filter: Union[dict, None], top_n: int) -> list[Chunk]:
        """
        Performs a similarity search using a query string and optional filter synchronously.

        Args:
            collection_name (str): The name of the collection to search.
            query (str): The query string for the similarity search.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            list[Chunk]: A list of chunks that match the query based on similarity.
        """
        pass
    
    @abstractmethod
    def similarity_search_with_score_sync(self, collection_name: str, query: str, filter: Union[dict, None], top_n: int) -> list[ScoredChunk]:
        """
        Performs a similarity search using a query string and optional filter synchronously.

        Args:
            collection_name (str): The name of the collection to search.
            query (str): The query string for the similarity search.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            list[ScoredChunk]: A list of chunks that match the query based on similarity.
        """
        pass

    @abstractmethod
    async def similarity_search_async(self, collection_name: str, query: str, filter: Union[dict, None], top_n: int) -> list[Chunk]:
        """
        Performs a similarity search using a query string and optional filter asynchronously.

        Args:
            collection_name (str): The name of the collection to search.
            query (str): The query string for the similarity search.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            list[Chunk]: A list of chunks that match the query based on similarity.
        """
        pass

    @abstractmethod
    async def similarity_search_with_score_async(self, collection_name: str, query: str, filter: Union[dict, None], top_n: int) -> list[ScoredChunk]:
        """
        Performs a similarity search using a query string and optional filter asynchronously.

        Args:
            collection_name (str): The name of the collection to search.
            query (str): The query string for the similarity search.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            list[ScoredChunk]: A list of chunks that match the query based on similarity.
        """
        pass

    @abstractmethod
    def similarity_search_by_vector_sync(self, collection_name: str, vector: list[float], filter: Union[dict, None], top_n: int) -> list[Chunk]:
        """
        Performs a similarity search using a vector and optional filter synchronously.

        Args:
            collection_name (str): The name of the collection to search.
            vector (list[float]): The vector for the similarity search.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            list[Chunk]: A list of chunks that match the vector based on similarity.
        """
        pass

    @abstractmethod
    def similarity_search_by_vector_with_score_sync(self, collection_name: str, vector: list[float], filter: Union[dict, None], top_n: int) -> list[ScoredChunk]:
        """
        Performs a similarity search using a vector and optional filter synchronously.

        Args:
            collection_name (str): The name of the collection to search.
            vector (list[float]): The vector for the similarity search.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            list[ScoredChunk]: A list of chunks that match the vector based on similarity.
        """
        pass

    @abstractmethod
    def cache_get_sync(self, cache_collection_name: str, query: str, filter: Union[dict, None], threshold: float, top_n: int) -> Union[Chunk, None]:
        """
        Retrieves a chunk from the cache based on a query and filter synchronously.

        Args:
            cache_collection_name (str): The name of the cache collection.
            query (str): The query string.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            threshold (float): The similarity threshold to use for the search.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            Union[Chunk, None]: The chunk that matches the query or None if no match is found.
        """
        pass

    @abstractmethod
    async def cache_get_async(self, cache_collection_name: str, query: str, filter: Union[dict, None], threshold: float, top_n: int) -> Union[Chunk, None]:
        """
        Retrieves a chunk from the cache based on a query and filter asynchronously.

        Args:
            cache_collection_name (str): The name of the cache collection.
            query (str): The query string.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            threshold (float): The similarity threshold to use for the search.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            Union[Chunk, None]: The chunk that matches the query or None if no match is found.
        """
        pass

    @abstractmethod
    def cache_get_by_vector_sync(self, cache_collection_name: str, query: str, vector: list[float], filter: Union[dict, None], threshold: float, top_n: int) -> Union[Chunk, None]:
        """
        Retrieves a chunk from the cache based on a vector and filter synchronously.

        Args:
            cache_collection_name (str): The name of the cache collection.
            query (str): The query string.
            vector (list[float]): The vector for the similarity search.
            filter (Union[dict, None]): An optional filter to narrow the search results.
            threshold (float): The similarity threshold to use for the search.
            top_n (int): The maximum number of search results to return.
        
        Returns:
            Union[Chunk, None]: The chunk that matches the vector or None if no match is found.
        """
        pass

    @abstractmethod
    def cache_put_sync(self, cache_collection_name: str, chunk: Chunk) -> None:
        """
        Stores a chunk in the cache synchronously.

        Args:
            cache_collection_name (str): The name of the cache collection.
            chunk (Chunk): The chunk to be stored in the cache.
        """
        pass

    @abstractmethod
    async def cache_put_async(self, cache_collection_name: str, chunk: Chunk) -> None:
        """
        Stores a chunk in the cache asynchronously.

        Args:
            cache_collection_name (str): The name of the cache collection.
            chunk (Chunk): The chunk to be stored in the cache.
        """
        pass

    @abstractmethod
    def update_metadatas_sync(self, collection_name: str, ids: list[str], metadatas: list[dict]) -> None:
        """
        Updates the metadata for chunks in a collection synchronously.

        Args:
            collection_name (str): The name of the collection to update.
            ids (list[str]): A list of chunk IDs whose metadata will be updated.
            metadatas (list[dict]): A list of dictionaries representing the new metadata for each chunk.
        """
        pass

    @abstractmethod
    def update_documents_sync(self, collection_name: str, ids: list[str], documents: list[str]) -> None:
        """
        Updates the documents for chunks in a collection synchronously.

        Args:
            collection_name (str): The name of the collection to update.
            ids (list[str]): A list of chunk IDs whose documents will be updated.
            documents (list[str]): A list of new documents for each chunk.
        """
        pass

    @abstractmethod
    async def update_documents_async(self, collection_name: str, ids: list[str], documents: list[str]) -> None:
        """
        Updates the documents for chunks in a collection asynchronously.

        Args:
            collection_name (str): The name of the collection to update.
            ids (list[str]): A list of chunk IDs whose documents will be updated.
            documents (list[str]): A list of new documents for each chunk.
        """
        pass

    @abstractmethod
    def delete_by_ids_sync(self, collection_name: str, ids: list[str]) -> None:
        """
        Deletes chunks from a collection by their IDs synchronously.

        Args:
            collection_name (str): The name of the collection from which to delete the chunks.
            ids (list[str]): A list of chunk IDs to delete.
        """
        pass

    @abstractmethod
    def delete_by_filter_sync(self, collection_name: str, filter: dict) -> None:
        """
        Deletes chunks from a collection based on a filter synchronously.

        Args:
            collection_name (str): The name of the collection from which to delete the chunks.
            filter (dict): A dictionary-based filter to identify which chunks to delete.
        """
        pass