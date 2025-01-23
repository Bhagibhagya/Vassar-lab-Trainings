import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from ce_shared_services.factory.scope.singleton import Singleton
from ce_shared_services.llm.azure_openai.azure_openai_llm import AzureOpenAILLM


class LLMFactory(Singleton):
    
    CLASSNAME_CLASS_MAP = {
        AzureOpenAILLM.__name__ : AzureOpenAILLM
    }