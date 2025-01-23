from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    
    """
    Interface for embedding models that provides methods to generate embeddings 
    for queries and documents in both synchronous and asynchronous contexts. Each method 
    supports retry logic with configurable delays.
    """
    
    @abstractmethod
    def embed_query_sync(self, query: str, max_retries: int, initial_delay: int) -> list[float]:
        """
        Generates an embedding for the given query in a synchronous context.

        Args:
            query (str): The input query to embed.
            max_retries (int): The maximum number of retries for the request.
            initial_delay (int): The initial minimum delay (in seconds) for each retry.

        Returns:
            list[float]: A list of floats representing the embedding of the query.
        """
        pass
    
    @abstractmethod
    async def embed_query_async(self, query: str, max_retries: int, initial_delay: int) -> list[float]:
        """
        Generates an embedding for the given query in an asynchronous context.

        Args:
            query (str): The input query to embed.
            max_retries (int): The maximum number of retries for the request.
            initial_delay (int): The initial minimum delay (in seconds) for each retry.

        Returns:
            list[float]: A list of floats representing the embedding of the query.
        """
        pass
    
    @abstractmethod
    def embed_documents_sync(self, documents: list[str], max_retries: int, initial_delay: int) -> list[list[float]]:
        """
        Generates embeddings for a list of documents in a synchronous context.

        Args:
            documents (list[str]): A list of document strings to embed.
            max_retries (int): The maximum number of retries for the request.
            initial_delay (int): The initial minimum delay (in seconds) for each retry.

        Returns:
            list[list[float]]: A list of embeddings, where each embedding is a list of floats representing a document.
        """
        pass

    @abstractmethod
    async def embed_documents_async(self, documents: list[str], max_retries: int, initial_delay: int) -> list[list[float]]:
        """
        Generates embeddings for a list of documents in an asynchronous context.

        Args:
            documents (list[str]): A list of document strings to embed.
            max_retries (int): The maximum number of retries for the request.
            initial_delay (int): The initial minimum delay (in seconds) for each retry.

        Returns:
            list[list[float]]: A list of embeddings, where each embedding is a list of floats representing a document.
        """
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """
        Computes a hash value for the embedding model instance based on its initialization parameters.
        
        This method should generate a unique integer hash that reflects the state 
        of the embedding model instance, ensuring that instances with the same parameters 
        yield the same hash value.

        Returns:
            int: A hash value representing the instance, which should be consistent 
            with the equality comparison (i.e., instances considered equal should 
            have the same hash).
        """
        pass