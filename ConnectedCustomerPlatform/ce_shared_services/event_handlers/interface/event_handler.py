from abc import ABC, abstractmethod


class IEventHandler(ABC):

    @abstractmethod
    async def run_event_handler(self, chat_history: list, user_query: str):
        """
        Main handler for intent classification.

        This method handles the classification of intents based on the provided chat history and user query.
        It determines whether to perform parallel or sequential classification based on whether a previous intent
        is available in the configuration. The intent classification logic is executed by invoking appropriate helper methods.

        Args:
            chat_history (list): A list of previous chat messages that provide context for intent classification.
            user_query (str): The current user query that needs to be classified.

        Returns:
            dict: The model's output after performing intent classification, represented as a dictionary.
        """
        pass