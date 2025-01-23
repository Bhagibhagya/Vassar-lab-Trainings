import json

from AIServices.LLM.llm import llm
from AIServices.LLM.llm_chain import llm_chain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder

prompt_template_mapping = {
    "SYSTEM":SystemMessagePromptTemplate,
    "CONTEXT":HumanMessagePromptTemplate,
    "DISPLAY":SystemMessagePromptTemplate,
    "REMEMBER": SystemMessagePromptTemplate,
}


class LLMChain:
    def __init__(self, prompt : dict):
        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM","")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT","")),
            SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY","")),
            SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER",""))
        ]

        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)

        
        self.chain = llm_chain(prompt=chat_prompt,llm=llm)


    
    def query(self, inputs={}):

        
        response = self.chain.run(inputs=inputs)

            
        
        return response

