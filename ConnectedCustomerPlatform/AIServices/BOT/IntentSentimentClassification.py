import json

from AIServices.LLM.llm import llm
from AIServices.LLM.llm_chain import llm_chain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from AIServices.prompts.prompts import INTENT_SENTIMENT_CLASSIFICATION_PROMPT, EMAIL_TEMPLATE

prompt_template_mapping = {
    "SYSTEM":SystemMessagePromptTemplate,
    "CONTEXT":HumanMessagePromptTemplate,
    "DISPLAY":SystemMessagePromptTemplate,
    "REMEMBER": SystemMessagePromptTemplate,
}

import asyncio

class IntentSentimentClassification:
    def __init__(self, prompt=INTENT_SENTIMENT_CLASSIFICATION_PROMPT):
        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM","")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT",""))
        ]
        
        email_content_template = EMAIL_TEMPLATE
        prompt_messages.append(HumanMessagePromptTemplate.from_template(email_content_template))
        
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY","")))
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER","")))
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)

        
        self.classification_prompt_chain = llm_chain(prompt=chat_prompt,llm=llm)


    
    def query(self, email_content, email_thread_summary=""):
        # print(email_content)
        
        response = self.classification_prompt_chain.run(inputs={
            "question": email_content,
            "summary": email_thread_summary
        })

        
        print(response)
        try:
            response_json = json.loads(response)
        except json.JSONDecodeError as e:
            print(e.msg)
            response_json = {
                "intent": "UNIDENTIFIED",
                "sub_intent": "UNIDENTIFIED",
                "tone": "UNIDENTIFIED"
            } 
            
        response_json = {key.lower(): value.upper() if value is not None else "UNIDENTIFIED" for key, value in response_json.items()}
        
        return response_json

