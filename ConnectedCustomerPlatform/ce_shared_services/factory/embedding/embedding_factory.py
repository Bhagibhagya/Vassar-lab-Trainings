import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from ce_shared_services.factory.scope.singleton import Singleton
from ce_shared_services.embedding.azure_openai.azure_openai_embedding import AzureOpenAIEmbeddingModel


class EmbeddingModelFactory(Singleton):
    
    CLASSNAME_CLASS_MAP = {
        AzureOpenAIEmbeddingModel.__name__ : AzureOpenAIEmbeddingModel
    }