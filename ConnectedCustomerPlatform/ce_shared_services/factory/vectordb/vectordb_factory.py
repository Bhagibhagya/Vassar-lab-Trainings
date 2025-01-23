import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(path)

from ce_shared_services.factory.scope.singleton import Singleton
from ce_shared_services.vectordb.chroma.chroma_vectordb import ChromaDB

class VectorDBFactory(Singleton):

    CLASSNAME_CLASS_MAP = {
        ChromaDB.__name__ : ChromaDB
    }