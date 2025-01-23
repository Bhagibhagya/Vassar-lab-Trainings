from abc import ABC, abstractmethod

from typing import Any, List, Dict, Union, Optional
from typing import Generator, AsyncGenerator


class LLM(ABC):
    
    """
    Interface for language models (LLMs) that provides methods to interact with 
    an LLM for generating responses based on prompts. It supports both synchronous 
    and asynchronous operations for running and streaming requests with retry mechanisms.
    """
    
    @abstractmethod
    async def run_async(self, prompt: str, json_mode: Optional[bool], max_retries: Optional[int], initial_delay: Optional[int]) -> Union[str, List[Union[str, Dict]], Any, None]:
        """
        Executes an LLM request asynchronously with the given prompt.

        Args:
            prompt (str): The input prompt for the LLM request.
            json_mode (Optional[bool]): Whether to process the LLM request in JSON mode.
            max_retries (Optional[int]): The maximum number of retries for the request.
            initial_delay (Optional[int]): The initial minimum delay (in seconds) for each retry.

        Returns:
            Union[str, List[Union[str, Dict]], Any, None]: The response from the LLM, which could be a string, a list of strings or dictionaries, or other data types.
        """
        pass
    
    @abstractmethod
    def run_sync(self, prompt: str, json_mode: Optional[bool], max_retries: Optional[int], initial_delay: Optional[int]) -> Union[str, List[Union[str, Dict]], Any, None]:
        """
        Executes an LLM request synchronously with the given prompt.

        Args:
            prompt (str): The input prompt for the LLM request.
            json_mode (Optional[bool]): Whether to process the LLM request in JSON mode.
            max_retries (Optional[int]): The maximum number of retries for the request.
            initial_delay (Optional[int]): The initial minimum delay (in seconds) for each retry.

        Returns:
            Union[str, List[Union[str, Dict]], Any, None]: The response from the LLM, which could be a string, a list of strings or dictionaries, or other data types.
        """
        pass
    
    @abstractmethod
    async def stream_async(self, prompt: str, json_mode: Optional[bool], max_retries: Optional[int], initial_delay: Optional[int]) -> AsyncGenerator[Union[str, List[Union[str, Dict]], Any], Any]:
        """
        Executes an LLM request asynchronously for a streamed response.

        Args:
            prompt (str): The input prompt for the LLM request.
            json_mode (Optional[bool]): Whether to process the LLM request in JSON mode.
            max_retries (Optional[int]): The maximum number of retries for the request.
            initial_delay (Optional[int]): The initial minimum delay (in seconds) for each retry.

        Returns:
            AsyncGenerator[Union[str, List[Union[str, Dict]], Any], Any]: An async generator that yields chunks of the LLM response.
        """
        pass

    @abstractmethod
    def stream_sync(self, prompt: str, json_mode: Optional[bool], max_retries: Optional[int], initial_delay: Optional[int]) -> Generator[Union[str, List[Union[str, Dict]]], Any, Union[Any, None]]:
        """
        Executes an LLM request synchronously for a streamed response.

        Args:
            prompt (str): The input prompt for the LLM request.
            json_mode (Optional[bool]): Whether to process the LLM request in JSON mode.
            max_retries (Optional[int]): The maximum number of retries for the request.
            initial_delay (Optional[int]): The initial minimum delay (in seconds) for each retry.

        Returns:
            Generator[Union[str, List[Union[str, Dict]]], Any, Union[Any, None]]: A generator that yields chunks of the LLM response.
        """
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """
        Computes a hash value for the LLM instance based on its initialization parameters.
        
        This method should generate a unique integer hash that reflects the state 
        of the LLM instance, ensuring that instances with the same parameters 
        yield the same hash value.

        Returns:
            int: A hash value representing the instance, which should be consistent 
            with the equality comparison (i.e., instances considered equal should 
            have the same hash).
        """
        pass