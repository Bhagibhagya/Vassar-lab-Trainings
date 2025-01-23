import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from typing import Any
from threading import Lock

from ce_shared_services.factory.scope.prototype import Prototype


class Pool():
    
    def __init__(self, prototype: Prototype, class_name: str, config: dict, pool_size: int):
        
        self._lock = Lock()
        
        self._n = pool_size
        self._counter = -1
        
        self._pool = [
            prototype.instantiate(class_name, config) for _ in range(self._n)
        ]
    
    def get(self) -> Any:
        
        with self._lock:
            
            self._counter = (self._counter + 1) % self._n
            return self._pool[self._counter]