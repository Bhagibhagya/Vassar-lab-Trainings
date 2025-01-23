import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from typing import Union, Callable
import logging
import traceback

import chromadb
from chromadb.config import Settings
from chromadb.types import Where

from ce_shared_services.datatypes.datatypes import Chunk, ScoredChunk
from ce_shared_services.embedding.interface.embedding import EmbeddingModel
from ce_shared_services.vectordb.interface.vectordb import VectorDB
from ce_shared_services.exceptions.exceptions import VectorDBException, EmbeddingException

logger = logging.getLogger(__name__)


class ChromaDB(VectorDB):
    
    _ALLOW_RESET = True
    _ANONYMIZED_TELEMETRY = False
    
    _DEFAULT_TENANT = "default_tenant"
    _DEFAULT_DATABASE = "default_database"
    
    _SIMILARITY_EVALUATION_MODEL_NAME = "cross-encoder/quora-distilroberta-base"
    _CACHE_THRESHOLD = 0.92
    _CACHE_TOP_N = 20
    
    def __init__(
        self,
        embedding_model : EmbeddingModel,
        host : str,
        port : int,
        database : str = _DEFAULT_DATABASE,
        tenant : str = _DEFAULT_TENANT,
        allow_reset : str = _ALLOW_RESET,
        anonymized_telemetry : str = _ANONYMIZED_TELEMETRY,
        cache_evaluator : Callable[[str, str], float] = None
    ):
        
        self._api_client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(
                allow_reset=allow_reset,
                anonymized_telemetry=anonymized_telemetry
            ),
            database=database,
            tenant=tenant
        )
        
        self._embedding_model = embedding_model
        
        self._cache_evaluator = cache_evaluator
    
    def create_collection_sync(self, collection_name: str) -> None:
        
        logger.info('In ChromaDB class :: create_collection_sync method')
        
        try:
            self._api_client.create_collection(name=collection_name)
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In create_collection_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def delete_collection_sync(self, collection_name: str) -> None:
        
        logger.info('In ChromaDB class :: delete_collection_sync method')
        
        try:
            self._api_client.delete_collection(name=collection_name)
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In delete_collection_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)

    def rename_collection_sync(self, collection_name: str, new_name : str) -> None:
        
        logger.info('In ChromaDB class :: rename_collection_sync method')
        
        try:
            
            collection = self._api_client.get_or_create_collection(name=collection_name)
            collection.modify(name=new_name)
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In rename_collection_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def get_collection_count_sync(self, collection_name: str) -> int:
        
        logger.info('In ChromaDB class :: get_collection_count_sync method')
        
        try:
                        
            collection = self._api_client.get_or_create_collection(name=collection_name)
            return collection.count()
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In rename_collection_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
        
    
    def add_chunks_sync(self, collection_name: str, chunks: list[Chunk]) -> None:
        
        logger.info('In ChromaDB class :: add_sync method')
        
        try:
            ids = []
            documents = []
            metadatas = []
            vectors = []
            
            for chunk in chunks:
                
                if chunk.vector is None:
                    chunk.vector = self._embedding_model.embed_query_sync(chunk.document)
                
                ids.append(chunk.id)
                documents.append(chunk.document)
                metadatas.append(chunk.metadata)
                vectors.append(chunk.vector)
            
            collection = self._api_client.get_or_create_collection(name=collection_name)
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=vectors
            )

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in add_sync method')
            raise embedding_exception

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In add_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
        
    async def add_chunks_async(self, collection_name: str, chunks: list[Chunk]) -> None:
        
        logger.info('In ChromaDB class :: add_async method')
        
        try:
            ids = []
            documents = []
            metadatas = []
            vectors = []
            
            for chunk in chunks:
                
                if chunk.vector is None:
                    chunk.vector = await self._embedding_model.embed_query_async(chunk.document)
                
                ids.append(chunk.id)
                documents.append(chunk.document)
                metadatas.append(chunk.metadata)
                vectors.append(chunk.vector)
            
            collection = self._api_client.get_or_create_collection(name=collection_name)
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=vectors
            )

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in add_async method')
            raise embedding_exception

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In add_async raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def get_by_ids_sync(self, collection_name: str, ids: list[str]) -> list[Chunk]:
        
        logger.info('In ChromaDB class :: get_by_ids_sync method')
        
        try:
            chunks = []  
                      
            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.get(ids=ids)
            
            ids = data['ids']
            metadatas = data['metadatas']
            documents = data['documents']
            
            for i, id in enumerate(ids):
            
                chunks.append(Chunk(
                    id=id,
                    document=documents[i],
                    metadata=metadatas[i]
                ))
            
            return chunks
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In get_by_ids_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def get_by_filter_sync(self, collection_name: str, filter: Union[Where, None] = None) -> list[Chunk]:
        
        logger.info('In ChromaDB class :: get_by_filter_sync method')
        
        try:
            chunks = []  
                      
            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.get(where=filter)
            
            ids = data['ids']
            metadatas = data['metadatas']
            documents = data['documents']
            
            for i, id in enumerate(ids):
            
                chunks.append(Chunk(
                    id=id,
                    document=documents[i],
                    metadata=metadatas[i]
                ))
            
            return chunks
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In get_by_filter_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def similarity_search_sync(self, collection_name: str, query: str, filter: Union[Where, None] = None, top_n: int = 10) -> list[Chunk]:
        
        logger.info('In ChromaDB class :: similarity_search_sync method')
        
        try:
            chunks = []  
                      
            query_embedding = self._embedding_model.embed_query_sync(query)
                      
            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.query(
                query_embeddings=query_embedding,
                where=filter,
                n_results=top_n
            )
        
            ids = data['ids'][0]
            metadatas = data['metadatas'][0]
            documents = data['documents'][0]
            
            for i, id in enumerate(ids):
            
                chunks.append(Chunk(
                    id=id,
                    document=documents[i],
                    metadata=metadatas[i]
                ))
            
            return chunks

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in similarity_search_sync method')
            raise embedding_exception        

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In similarity_search_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def similarity_search_with_score_sync(self, collection_name: str, query: str, filter: Union[Where, None] = None, top_n: int = 10) -> list[ScoredChunk]:

        logger.info('In ChromaDB class :: similarity_search_with_score_sync method')
        
        try:
            scored_chunks = []  
                      
            query_embedding = self._embedding_model.embed_query_sync(query)
                      
            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.query(
                query_embeddings=query_embedding,
                where=filter,
                n_results=top_n
            )
        
            ids = data['ids'][0]
            metadatas = data['metadatas'][0]
            documents = data['documents'][0]
            distances = data['distances'][0]

            for i, id in enumerate(ids):
            
                scored_chunks.append(
                    ScoredChunk(
                        chunk=Chunk(
                            id=id,
                            document=documents[i],
                            metadata=metadatas[i]
                        ),
                        score=1-distances[i]
                    )
                )
            
            return scored_chunks

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in similarity_search_with_score_sync method')
            raise embedding_exception        

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In similarity_search_with_score_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)

    async def similarity_search_async(self, collection_name: str, query: str, filter: Union[Where, None] = None, top_n: int = 10) -> list[Chunk]:
        
        logger.info('In ChromaDB class :: similarity_search_async method')
        
        try:
            chunks = []  
                      
            query_embedding = await self._embedding_model.embed_query_async(query)
                      
            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.query(
                query_embeddings=query_embedding,
                where=filter,
                n_results=top_n
            )
        
            ids = data['ids'][0]
            metadatas = data['metadatas'][0]
            documents = data['documents'][0]
            
            for i, id in enumerate(ids):
            
                chunks.append(Chunk(
                    id=id,
                    document=documents[i],
                    metadata=metadatas[i]
                ))
            
            return chunks

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in similarity_search_async method')
            raise embedding_exception 

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In similarity_search_async raising VectorDBException')
            
            raise VectorDBException(*exception.args)

    async def similarity_search_with_score_async(self, collection_name: str, query: str, filter: Union[Where, None] = None, top_n: int = 10) -> list[ScoredChunk]:
        
        logger.info('In ChromaDB class :: similarity_search_with_score_async method')
        
        try:
            scored_chunks = []  
                      
            query_embedding = await self._embedding_model.embed_query_async(query)
                      
            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.query(
                query_embeddings=query_embedding,
                where=filter,
                n_results=top_n
            )
        
            ids = data['ids'][0]
            metadatas = data['metadatas'][0]
            documents = data['documents'][0]
            distances = data['distances'][0]
            
            for i, id in enumerate(ids):
            
                scored_chunks.append(
                    ScoredChunk(
                        chunk=Chunk(
                            id=id,
                            document=documents[i],
                            metadata=metadatas[i]
                        ),
                        score=1-distances[i]
                    )
                )
            
            return scored_chunks

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in similarity_search_with_score_async method')
            raise embedding_exception 

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In similarity_search_with_score_async raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def similarity_search_by_vector_sync(self, collection_name: str, vector: list[float], filter: Union[Where, None] = None, top_n: int = 10) -> list[Chunk]:
        
        logger.info('In ChromaDB class :: similarity_search_by_vector_sync method')
        
        try:
            chunks = []  

            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.query(
                query_embeddings=vector,
                where=filter,
                n_results=top_n
            )
        
            ids = data['ids'][0]
            metadatas = data['metadatas'][0]
            documents = data['documents'][0]
            
            for i, id in enumerate(ids):
            
                chunks.append(Chunk(
                    id=id,
                    document=documents[i],
                    metadata=metadatas[i]
                ))
            
            return chunks
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In similarity_search_by_vector_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
        
    def similarity_search_by_vector_with_score_sync(self, collection_name: str, vector: list[float], filter: Union[Where, None] = None, top_n: int = 10) -> list[ScoredChunk]:
        
        logger.info('In ChromaDB class :: similarity_search_by_vector_with_score_sync method')
        
        try:
            scored_chunks = []  

            collection = self._api_client.get_or_create_collection(name=collection_name)
            data = collection.query(
                query_embeddings=vector,
                where=filter,
                n_results=top_n
            )
        
            ids = data['ids'][0]
            metadatas = data['metadatas'][0]
            documents = data['documents'][0]
            distances = data['distances'][0]
            
            for i, id in enumerate(ids):
            
                scored_chunks.append(
                    ScoredChunk(
                        chunk=Chunk(
                            id=id,
                            document=documents[i],
                            metadata=metadatas[i]
                        ),
                        score=1-distances[i]
                    )
                )
            
            return scored_chunks
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In similarity_search_by_vector_with_score_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def cache_get_sync(self, cache_collection_name: str, query: str, filter: Union[Where, None] = None, threshold: float = _CACHE_THRESHOLD, top_n: int = _CACHE_TOP_N) -> Union[Chunk, None]:
        
        logger.info('In ChromaDB class :: cache_get_sync method')
        
        try:
            query_embedding = self._embedding_model.embed_query_sync(query)
            collection = self._api_client.get_or_create_collection(name=cache_collection_name)
            
            data = collection.query(
                query_embeddings=query_embedding,
                where=filter,
                n_results=top_n
            )
            
            ids = data['ids'][0]
            documents = data['documents'][0]
            metadatas = data['metadatas'][0]
            distances = data['distances'][0]
            
            if len(ids) == 0:
                return None
                
            if 1 - distances[0] >= threshold:
                
                return Chunk(
                    id=ids[0],
                    document=documents[0],
                    metadata=metadatas[0]
                )
            
            return None

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in cache_get_sync method')
            raise embedding_exception 

        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In cache_get_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    async def cache_get_async(self, cache_collection_name: str, query: str, filter: Union[Where, None] = None, threshold: float = _CACHE_THRESHOLD, top_n: int = _CACHE_TOP_N) -> Union[Chunk, None]:
        
        logger.info('In ChromaDB class :: cache_get_async method')
        
        try:
            query_embedding = await self._embedding_model.embed_query_async(query)
            collection = self._api_client.get_or_create_collection(name=cache_collection_name)
            
            data = collection.query(
                query_embeddings=query_embedding,
                where=filter,
                n_results=top_n
            )
            
            ids = data['ids'][0]
            documents = data['documents'][0]
            metadatas = data['metadatas'][0]
            distances = data['distances'][0]
            
            if len(ids) == 0:
                return None
            
            if 1 - distances[0] >= threshold:
                
                return Chunk(
                    id=ids[0],
                    document=documents[0],
                    metadata=metadatas[0]
                )
            
            return None
            
        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in cache_get_async method')
            raise embedding_exception     
        
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In cache_get_async raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def cache_get_by_vector_sync(self, cache_collection_name: str, query : str, vector: list[float], filter: Union[Where, None] = None, threshold: float = _CACHE_THRESHOLD, top_n: int = _CACHE_TOP_N) -> Union[Chunk, None]:
        
        logger.info('In ChromaDB class :: cache_get_by_vector_sync method')
        
        try:
            collection = self._api_client.get_or_create_collection(name=cache_collection_name)
            
            data = collection.query(
                query_embeddings=vector,
                where=filter,
                n_results=top_n
            )
            
            ids = data['ids'][0]
            documents = data['documents'][0]
            metadatas = data['metadatas'][0]
            distances = data['distances'][0]
            
            if len(ids) == 0:
                return None
            
            if 1 - distances[0] >= threshold:
                
                return Chunk(
                    id=ids[0],
                    document=documents[0],
                    metadata=metadatas[0]
                )
                
            return None
            
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In cache_get_by_vector_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def cache_put_sync(self, cache_collection_name: str, chunk: Chunk) -> None:
        
        logger.info('In ChromaDB class :: cache_put_sync method')
        
        try:
            if chunk.vector is None:
                chunk.vector = self._embedding_model.embed_query_sync(chunk.document)
            
            collection = self._api_client.get_or_create_collection(name=cache_collection_name)
            collection.add(
                ids=[chunk.id],
                documents=[chunk.document],
                metadatas=[chunk.metadata],
                embeddings=[chunk.vector]
            )
            
        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in cache_put_sync method')
            raise embedding_exception  
            
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In cache_put_sync raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    async def cache_put_async(self, cache_collection_name: str, chunk: Chunk) -> None:
        
        logger.info('In ChromaDB class :: cache_put_async method')
        
        try:
            if chunk.vector is None:
                chunk.vector = await self._embedding_model.embed_query_async(chunk.document)
            
            collection = self._api_client.get_or_create_collection(name=cache_collection_name)
            collection.add(
                ids=[chunk.id],
                documents=[chunk.document],
                metadatas=[chunk.metadata],
                embeddings=[chunk.vector]
            )

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in cache_put_async method')
            raise embedding_exception  
            
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In cache_put_async raising VectorDBException')
            
            raise VectorDBException(*exception.args)
    
    def update_metadatas_sync(self, collection_name: str, ids: list[str], metadatas: list[dict]) -> None:
        
        logger.info('In ChromaDB class :: update_metadatas_sync method')
        
        try:
            collection = self._api_client.get_or_create_collection(name=collection_name)
            collection.update(
                ids=ids,
                metadatas=metadatas
            )
            
        except Exception as exception:

            logger.error(traceback.format_exc())
            logger.info('In update_metadatas_sync raising VectorDBException')            
            
            raise VectorDBException(*exception.args)
    
    def update_documents_sync(self, collection_name: str, ids: list[str], documents: list[str]) -> None:
        
        logger.info('In ChromaDB class :: update_documents_sync method')
        
        try:
            
            collection = self._api_client.get_or_create_collection(name=collection_name)
            document_embeddings = self._embedding_model.embed_documents_sync(documents)
            
            collection.update(
                ids=ids,
                documents=documents,
                embeddings=document_embeddings
            )

        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in update_documents_sync method')
            raise embedding_exception  

        except Exception as exception:

            logger.error(traceback.format_exc())
            logger.info('In update_documents_sync raising VectorDBException')            
            
            raise VectorDBException(*exception.args)
    
    async def update_documents_async(self, collection_name: str, ids: list[str], documents: list[str]) -> None:

        logger.info('In ChromaDB class :: update_metadatas_async method')
        
        try:
            
            collection = self._api_client.get_or_create_collection(name=collection_name)
            document_embeddings = await self._embedding_model.embed_documents_async(documents)
            
            collection.update(
                ids=ids,
                documents=documents,
                embeddings=document_embeddings
            )
        
        except EmbeddingException as embedding_exception:
            
            logger.info('EmbeddingException in update_documents_async method')
            raise embedding_exception
            
        except Exception as exception:

            logger.error(traceback.format_exc())
            logger.info('In update_metadatas_async raising VectorDBException')            
            
            raise VectorDBException(*exception.args)
    
    def delete_by_ids_sync(self, collection_name: str, ids: list[str]) -> None:
        
        logger.info('In ChromaDB class :: delete_by_ids_sync method')
        
        try:
            collection = self._api_client.get_or_create_collection(name=collection_name)
            collection.delete(
                ids=ids
            )
            
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In delete_by_ids_sync raising VectorDBException')            
            
            raise VectorDBException(*exception.args)
    
    def delete_by_filter_sync(self, collection_name: str, filter: Where) -> None:

        logger.info('In ChromaDB class :: delete_by_filter_sync method')
        
        try:
            collection = self._api_client.get_or_create_collection(name=collection_name)
            collection.delete(
                where=filter
            )
            
        except Exception as exception:
            
            logger.error(traceback.format_exc())
            logger.info('In delete_by_filter_sync raising VectorDBException')            
            
            raise VectorDBException(*exception.args)