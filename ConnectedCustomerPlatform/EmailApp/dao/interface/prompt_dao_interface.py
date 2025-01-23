from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IPromptDao(ABC):

    @abstractmethod
    def fetch_prompt_by_category_filter_json(self, customer_uuid: str, application_uuid: str,
                                             filter_json: Dict[str, Any] = None, category_name: str = None) -> Optional[dict]:
        """
        fetches prompt based on filters
        Args:
            customer_uuid:
            application_uuid:
            filter_json:
            category_name:

        Returns:
        return prompt
        """


        pass