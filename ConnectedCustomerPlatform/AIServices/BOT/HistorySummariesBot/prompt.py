from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate

HISTORY_SUMMARIZE_PROMPT = """
You are a summarization bot. Your task is to create a concise summary of the conversation history between the user and the bot based on the data provided.
Conversation History:
{history}
Please generate a summary that includes:
1. Key topics discussed.
2. Important questions and responses.
3. Problem-solving steps or advice provided.
4. Any actions or follow-ups suggested.
Ensure the summary captures the essence of the interaction and reflects the overall tone and flow of the conversation.
"""

history_summarize_bot_template = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(HISTORY_SUMMARIZE_PROMPT),
    ],
    input_variables=["history"],
)