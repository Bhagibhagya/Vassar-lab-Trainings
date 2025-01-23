import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from ce_shared_services.factory.scope.singleton import Singleton
from ce_shared_services.reranking.llm_reranking.llm_reranker import LLMReranker
from ce_shared_services.reranking.llm_reranking.parallel_llm_reranker import ParallelLLMReranker


class RerankerFactory(Singleton):
    
    CLASSNAME_CLASS_MAP = {
        LLMReranker.__name__ : LLMReranker,
        ParallelLLMReranker.__name__ : ParallelLLMReranker
    }