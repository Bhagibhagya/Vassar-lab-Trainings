
from ChatBot.dao.interface.media_dao_interface import IMediaDao
from DatabaseApp.models import  Media

from uuid import uuid4
import logging

# Configure logger
logger = logging.getLogger(__name__)

class MediaDaoImpl(IMediaDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MediaDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        # Ensures initialization only occurs once (Singleton pattern)
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            self.initialized = True

    def delete_media_of_knowledge_source(self,knowledge_source_uuid):
        """
        Deletes all media associated with the specified knowledge source UUID.
        
        Args:
            knowledge_source_uuid (str): UUID of the knowledge source.
        """
        Media.objects.filter(knowledge_source_uuid=knowledge_source_uuid).delete()