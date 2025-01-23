import os
import json
from urllib.parse import unquote

from django.conf import settings

from EmailApp.constant.constants import ReturnTypes

from ChatBot.constant.constants import KnowledgeSourceConstants

from ChatBot.services.interface.video_service_interface import VideoCorrectionServiceInterface
from ChatBot.dao.impl.error_dao_impl import ErrorCorrectionDaoImpl
from ChatBot.dao.interface.error_dao_interface import ErrorCorrectionDaoInterface

from ChatBot.views.files import add_knowledge_source_chunks, delete_knowledge_source_chunks

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


class VideoCorrectionServiceImpl(VideoCorrectionServiceInterface):
    
    def __init__(self):
        
        self._error_dao : ErrorCorrectionDaoInterface = ErrorCorrectionDaoImpl()
        self.__azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))


    def get_video_transcription(self, file_uuid):
        
        """get the transciption of the video

        Returns:
            list of internal json blocks, video url
        """
        logger.info("In video_service.py :: VideoCorrectionServiceImpl :: get_video_transcription")
        
        knowledge_source_name, knowledge_source_path, _, _, _ = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        blocks = internal_json['blocks']
        
        return blocks, knowledge_source_path,knowledge_source_name
    
    def update_video_transcription(self, file_uuid, error_uuid, transcription):
        
        """update the transciption of the video

        Returns:
            None
        """
        logger.info("In video_service.py :: VideoCorrectionServiceImpl :: update_video_transcription")
        
        knowledge_source_name, knowledge_source_path, status, customer_uuid, application_uuid = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        internal_json['blocks'] = transcription
        self.__azure_blob_manager.update_data(blob_name=unquote(internal_json_path), data=json.dumps(internal_json).encode('utf-8'), return_type=ReturnTypes.URL.value,
                                              file_name=unquote(internal_json_path))
        self._error_dao.update_error_status(error_uuid, 'Resolved')
        
        if status == 'Reviewed':
            
            chunk_collection, _, _ = self._error_dao.get_collections_by_customer_application(customer_uuid, application_uuid)
            self._error_dao.update_knowledge_source_status(file_uuid, 'Reviewing')
            
            delete_knowledge_source_chunks(knowledge_source_name, chunk_collection)
            add_knowledge_source_chunks(file_uuid, chunk_collection)