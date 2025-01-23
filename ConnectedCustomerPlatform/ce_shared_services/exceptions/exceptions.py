class LLMException(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EmbeddingException(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class VectorDBException(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RerankingException(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class CachingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)