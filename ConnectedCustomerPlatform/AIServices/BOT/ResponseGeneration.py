import json

from AIServices.LLM.llm import llm
from AIServices.LLM.llm_chain import llm_chain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from AIServices.prompts.prompts  import TROUBLESHOOTING_RESPONSE_GENERATION

prompt_template_mapping = {
    "SYSTEM":SystemMessagePromptTemplate,
    "CONTEXT":HumanMessagePromptTemplate,
    "DISPLAY":SystemMessagePromptTemplate,
    "REMEMBER": SystemMessagePromptTemplate,
}

class ResponseGeneration:
    def __init__(self, prompt:dict=TROUBLESHOOTING_RESPONSE_GENERATION):
        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM","")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT",""))
        ]
        
        
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY","")))
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER","")))
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)
        
        self.response_generation_chain = llm_chain(prompt=chat_prompt,llm=llm)
    
    def query(self, email_content,customer_data):

        response = self.response_generation_chain.run(inputs={
            "question": email_content,
            "customer_data":customer_data
        })
        
        try:
            response_json = json.loads(response)
        except json.JSONDecodeError:
            print(f"In {self.__class__}: Error: {e}")
            return {}
            
        response_json = {key.lower(): value for key, value in response_json.items()}
        
        return response_json


    
    
    