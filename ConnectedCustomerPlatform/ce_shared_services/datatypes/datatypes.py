from dataclasses import dataclass
from typing import Optional


@dataclass
class Chunk():
    
    id : str
    document : str
    metadata : dict
    vector : Optional[list[float]] = None


@dataclass
class ScoredChunk():
    
    chunk: Chunk
    score: float