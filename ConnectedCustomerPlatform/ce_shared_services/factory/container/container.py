import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from ce_shared_services.factory.llm.llm_factory import LLMFactory
from ce_shared_services.factory.embedding.embedding_factory import EmbeddingModelFactory
from ce_shared_services.factory.vectordb.vectordb_factory import VectorDBFactory
from ce_shared_services.factory.reranking.reranker_factory import RerankerFactory


class Container():

    llm = LLMFactory
    embedding = EmbeddingModelFactory
    vectordb = VectorDBFactory
    reranker = RerankerFactory