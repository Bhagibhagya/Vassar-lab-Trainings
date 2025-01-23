import logging
import langchain
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents import AgentExecutor

from AIServices.BOT.ChatBot.Prompts.prompt import chatbot_intent_classification_prompt
from AIServices.LLM import gpt3_llm
from AIServices.BOT.ChatBot.Tools.tool import tools
logger = logging.getLogger(__name__)
from AIServices.BOT.utils import llm_buffer_memory


class ChatbotIntentClassification:
    def __init__(self):
        self.llm = gpt3_llm

    def query(self, question, history):
        print()
        memory = ConversationBufferMemory(return_messages=True)
        buffer_memory = llm_buffer_memory(memory, history)
        logger.info(f"buffer memory ::{buffer_memory}")
        # Tools list
        tools_list = tools()

        prompt = chatbot_intent_classification_prompt
        llm_with_tools = self.llm.bind(functions=[format_tool_to_openai_function(t) for t in tools_list])
        agent = (
                {
                    "question": lambda x: x["question"],
                    "chat_history": lambda x: x["chat_history"],
                    "agent_scratchpad": lambda x: format_to_openai_function_messages(
                        x["intermediate_steps"]
                    )
                }
                | prompt  # Custom prompt
                | llm_with_tools  # Language model with tools
                | OpenAIFunctionsAgentOutputParser()  # Output parser
        )

        # Initialize agent executor
        agent_executor = AgentExecutor(agent=agent, tools=tools_list, verbose=True)

        # langchain.debug = True
        result = agent_executor({
            "question": question,
            "chat_history": buffer_memory
        })

        # langchain.debug = False
        logger.info(f'LLM output::{result["output"]}')
        return result["output"]
