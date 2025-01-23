import json
from channels.generic.websocket import AsyncWebsocketConsumer
from next_word_prediction import GPT2
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from AIServices.LLM.llm_chain import llm_chain
from AIServices.prompts.prompts import PARAPHRASING_WITH_TONE_TEMPLATE

gpt2 = GPT2()

class TextConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnected: Close code: {close_code}")
        if close_code == 1000:
            print("Normal closure - connection closed successfully")
        elif close_code == 1001:
            print("Going away - client or server is going away")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'predict_next')
        text = data.get('text', '')

        try:
            if message_type == 'predict_next':
                if not text:
                    text = "."
                prediction = gpt2.predict_next(text, 1)[0]
                await self.send(text_data=json.dumps({
                    'prediction': prediction
                }))
            elif message_type == 'tone_transform':
                tone = data.get('tone', 'Formal')
                result = await self.tone_transform(text, tone)
                await self.send(text_data=json.dumps(result))
        except Exception as e:
            error_response = {
                "paraphrased_text": "The text contains offensive content and cannot be processed.. Please modify your text and retry.",
                "error": True
            }
            await self.send(text_data=json.dumps(error_response))

    async def tone_transform(self, text, tone):
        prompt = PARAPHRASING_WITH_TONE_TEMPLATE
        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt["SYSTEM"]),
            HumanMessagePromptTemplate.from_template(prompt["CONTEXT"]),
            SystemMessagePromptTemplate.from_template(prompt["DISPLAY"]),
            SystemMessagePromptTemplate.from_template(prompt["REMEMBER"])
        ]
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)
        llm_chain_instance = llm_chain(prompt=chat_prompt)
        result = llm_chain_instance.run(inputs={"text": text, "tone": tone})
        result_json = json.loads(result)
        return result_json
