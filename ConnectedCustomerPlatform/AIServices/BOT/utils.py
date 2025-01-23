import logging

logger = logging.getLogger(__name__)


def llm_buffer_memory(memory, history):
    logger.info(f"Inside llm_buffer_memory history : {history}")

    index = 0
    while index < len(history):
        if index + 1 < len(history):
            memory.save_context(history[index], history[index + 1])
        index += 2

    # Log the current state of memory after processing the history
    logger.info(
        f"Inside llm_buffer_memory in utils.py :: buffer_memory : {memory.load_memory_variables({})['history']}")

    return memory.load_memory_variables({})['history']

