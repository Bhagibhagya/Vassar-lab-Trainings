from .llm import llm, embeddings

from langchain.chains import LLMChain

from langchain.prompts import BasePromptTemplate
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast

from langchain_core.language_models import (
    BaseLanguageModel,
    LanguageModelInput,
)
from langchain_core.runnables import (
    Runnable,
    RunnableBinding,
    RunnableBranch,
    RunnableWithFallbacks,
)

from langchain_core.messages import BaseMessage

from langchain_community.chat_models import AzureChatOpenAI

GPT3_OPENAI_API_KEY = "95058a9e99794e4689d179dd726e7eec"
GPT3_OPENAI_DEPLOYMENT_NAME = "vassar-turbo35"
GPT3_OPENAI_API_BASE = "https://vassar-openai.openai.azure.com/"
GPT3_MODEL_NAME = "gpt-35-turbo" 
GPT3_OPENAI_API_TYPE = "azure"
GPT3_OPENAI_API_VERSION = "2023-07-01-preview"


# GPT3_OPENAI_API_KEY = "2752b82e2e3d41d59df518f56c7f9b3a"
# GPT3_OPENAI_DEPLOYMENT_NAME = "vassar-gpt-35-turbo-0125"
# GPT3_OPENAI_API_BASE = "https://vassar-openai-canada.openai.azure.com/"
# GPT3_MODEL_NAME = "gpt-35-turbo" 
# GPT3_OPENAI_API_TYPE = "azure"
# GPT3_OPENAI_API_VERSION = "2024-02-01"


gpt3_llm_params = {
    "deployment_name":GPT3_OPENAI_DEPLOYMENT_NAME,
    "model_name":GPT3_MODEL_NAME,
    "openai_api_base":GPT3_OPENAI_API_BASE,
    "openai_api_type":GPT3_OPENAI_API_TYPE,
    "openai_api_key":GPT3_OPENAI_API_KEY,
    "openai_api_version":GPT3_OPENAI_API_VERSION,
    "temperature" :0.0
}

gpt3_llm = AzureChatOpenAI(**gpt3_llm_params)


class llm_chain:
    
    prompt : BasePromptTemplate
    llm: Union[
        Runnable[LanguageModelInput, str], Runnable[LanguageModelInput, BaseMessage]
    ]
    
    def __init__(self, prompt,llm=gpt3_llm):
        self.prompt = prompt
        self.llm = llm
        self.chain = LLMChain(llm=self.llm,prompt=self.prompt,verbose=True)
        
    def run(self, inputs):

        # print(inputs)

        # print(LLMChain(prompt=self.prompt,))
        
        response = self.chain.run(inputs)

        # print("HERE")
        
        return response
