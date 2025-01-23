from abc import ABC, abstractmethod
from ChatBot.dataclasses.entity_data import Entity


class IMediaDao(ABC):
    @abstractmethod
    def delete_media_of_knowledge_source(self,knowledge_source_uuid):
        """
        Deletes all media associated with the specified knowledge source UUID.
        
        Args:
            knowledge_source_uuid (str): UUID of the knowledge source.
        """
