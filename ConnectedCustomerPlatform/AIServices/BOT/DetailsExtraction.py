import json

from AIServices.LLM.llm import llm
from AIServices.LLM.llm_chain import llm_chain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from AIServices.prompts.prompts import TROUBLESHOOTING_DETAILS_EXTRACTION

prompt_template_mapping = {
    "SYSTEM":SystemMessagePromptTemplate,
    "CONTEXT":HumanMessagePromptTemplate,
    "DISPLAY":SystemMessagePromptTemplate,
    "REMEMBER": SystemMessagePromptTemplate,
}

class DetailsExtraction:
    def __init__(self, prompt:dict=TROUBLESHOOTING_DETAILS_EXTRACTION):
        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM","")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT",""))
        ]
        
        prompt_messages.append(HumanMessagePromptTemplate.from_template('{question}'))
        
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY","")))
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER","")))
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)

        # print(chat_prompt)
        
        
        self.details_extraction_chain = llm_chain(prompt=chat_prompt,llm=llm)
    
    def query(self, email_content):

        # print(self.details_extraction_chain.prompt)
        
        response = self.details_extraction_chain.run(inputs={
            "question": email_content
        })

        # print(response)
        
        try:
            response_json = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"In {self.__class__}: Error: {e}")
            return {} 
            
        response_json = {key.lower(): value for key, value in response_json.items()}
        
        return response_json


    
    
    