import logging

from AIServices.LLM.llm_chain import llm_chain
from AIServices.BOT.HistorySummariesBot.prompt import history_summarize_bot_template
from langchain.memory import ConversationBufferMemory
logger = logging.getLogger(__name__)
from AIServices.BOT.utils import llm_buffer_memory

class HistorySummarize:
    def __init__(self):
        self.query_params_chain = llm_chain(prompt=history_summarize_bot_template)

    def query(self, history):
        memory = ConversationBufferMemory(return_messages=True)
        buffer_memory = llm_buffer_memory(memory, history)
        logger.info(f"buffer memory ::{buffer_memory}")
        result = self.query_params_chain.run({
            "history": buffer_memory})

        return result


history_summarize_bot = HistorySummarize()