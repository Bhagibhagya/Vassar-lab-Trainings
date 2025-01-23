import logging
from langchain.memory import ConversationBufferMemory

from AIServices.BOT.utils import llm_buffer_memory

from AIServices.BOT.ChatBot.bot import ChatbotIntentClassification

logger = logging.getLogger(__name__)

chat_bot = ChatbotIntentClassification()


def query(question, history):
    memory = ConversationBufferMemory(return_messages=True)
    buffer_memory = llm_buffer_memory(memory, history)
    logger.info(f"buffer memory ::{buffer_memory}")
    result = chat_bot.query(question=question, buffer_memory=buffer_memory)
    if "output" in result:
        return result['output']
    else:
        return "UNIDENTIFIED"
