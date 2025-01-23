import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

import logging
from typing import Any

from ce_shared_services.factory.scope.factory import Factory

logger = logging.getLogger(name=__name__)


class Prototype(Factory):
    
    CLASSNAME_CLASS_MAP: dict[str, type] = {}
    
    @classmethod
    def instantiate(cls, class_name: str, config: dict) -> Any:
    
        if not cls.CLASSNAME_CLASS_MAP:
            
            logger.error("CLASSNAME_CLASS_MAP must be defined by sub-classes.")
            raise ValueError("CLASSNAME_CLASS_MAP must be defined by sub-classes.")
    
        if class_name not in cls.CLASSNAME_CLASS_MAP:
            
            logger.error(f"class_name :: {class_name} not available for instantiation.")
            raise ValueError(f"class_name :: {class_name} not available for instantiation.")
        
        try:
            instance = cls.CLASSNAME_CLASS_MAP[class_name](**config)
            return instance
        
        except Exception as exception:
            
            logger.error(str(exception))
            raise exception