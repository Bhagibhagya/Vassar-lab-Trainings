from typing import Any
from abc import ABC, abstractmethod


class Factory(ABC):
    
    CLASSNAME_CLASS_MAP: dict[str, type]
    
    @classmethod
    @abstractmethod
    def instantiate(cls, class_name: str, config: dict) -> Any:
        pass