import json
import os
import uuid
from urllib.parse import unquote

from django.conf import settings

from EmailApp.constant.constants import ReturnTypes

from ChatBot.constant.constants import KnowledgeSourceConstants

from ChatBot.services.interface.header_service_interface import HeaderCorrectionServiceInterface
from ChatBot.dao.impl.error_dao_impl import ErrorCorrectionDaoImpl
from ChatBot.dao.interface.error_dao_interface import ErrorCorrectionDaoInterface

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException

from ChatBot.views.files import add_knowledge_source_chunks, delete_knowledge_source_chunks

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


class HeaderCorrectionServiceImpl(HeaderCorrectionServiceInterface):
    
    def __init__(self):
        
        self._error_dao : ErrorCorrectionDaoInterface = ErrorCorrectionDaoImpl()
        self.__azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

    def get_h1_headings(self, file_uuid):
        
        """get the level 1 blocks of the internal json

        Returns:
            level 1 blocks, application_uuid
        """
        
        logger.info("In header_service.py :: HeaderCorrectionServiceImpl :: get_h1_headings")

        _, knowledge_source_path, _, _, application_uuid = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        logger.info(f'internal json keys :: {internal_json.keys()}')
        
        blocks = internal_json['blocks']
        level1_blocks = []
        
        for block in blocks:

            if block['level'] == 1:
                
                block_type = block['content_type']

                if block_type == 'text':
                    level1_blocks.append({
                        'block_id': block['block_id'],
                        'block_type': block_type,
                        'text_type': str.capitalize(block[block_type]['type']),
                        'content': block[block_type]['content']
                    })

                else:
                    name = block[block_type]['name']
                    name = ', '.join(name)
                    if not name:
                        name = '-'

                    level1_blocks.append({
                        'block_id': block['block_id'],
                        'block_type': block_type,
                        'name': name
                    })
                    
        return level1_blocks, application_uuid
    
    def _get_sub_blocks(self, blocks, block_id):
        
        child_blocks = []
        for i, block in enumerate(blocks):
            
            level = block['level']            
            if block['block_id'] == block_id:

                for j in range(i+1, len(blocks)):
                    
                    if blocks[j]['level'] == level:
                        break
                    
                    elif blocks[j]['level'] == level + 1:
                        child_blocks.append(blocks[j])
                
                break
        
        return child_blocks
    
    def get_child_blocks(self, file_uuid, block_id):
        
        """get the child blocks under a block

        Returns:
            list of child blocks
        """
        logger.info("In header_service.py :: HeaderCorrectionServiceImpl :: get_child_blocks")
        
        _, knowledge_source_path, _ , _, _ = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        blocks = internal_json['blocks']
        sub_blocks = self._get_sub_blocks(blocks, block_id)
            
        logger.info(f"sub blocks length :: {len(sub_blocks)}")
            
        child_blocks = []    
        for block in sub_blocks:
            
            block_type = block['content_type']

            if block_type == 'text':

                child_blocks.append({
                    'block_id': block['block_id'],
                    'block_type': block_type,
                    'text_type': str.capitalize(block[block_type]['type']),
                    'content': block[block_type]['content'],
                    'parent_block_id': block_id
                })

            else:

                name = block[block_type]['name']
                if len(name) > 0:
                    name = ', '.join(name)
                else:
                    name = '-'

                child_blocks.append({
                    'block_id': block['block_id'],
                    'block_type': block_type,
                    'name': name,
                    'parent_block_id': block_id
                })
                
        return child_blocks
    
    def _increment_levels(self, contents):
        
        breaker = {
            'H1': ['H1'],
            'H2': ['H1', 'H2'],
            'H3': ['H1', 'H2', 'H3']
        }

        for key, value in breaker.items():

            i = 0
            n = len(contents)

            while i < n:
                if contents[i]['type'] != key:
                    i += 1
                    continue

                for j in range(i + 1, len(contents)):

                    if contents[j]['type'] in value:
                        i = j - 1
                        break
                    else:
                        contents[j]['level'] = contents[j]['level'] + 1
                i += 1

        return contents

    def _generate_levels(self, internal_json):
        
        blocks = internal_json['blocks']
        metadata = internal_json['metadata']

        contents = []
        for block in blocks:
            if block['content_type'] == 'text':
                contents.append({
                    'level': 1,
                    'type': block['text']['type']
                })
            else:
                contents.append({
                    'level': 1,
                    'type': block['content_type']
                })

        contents = self._increment_levels(contents)

        for i in range(len(contents)):
            blocks[i]['level'] = contents[i]['level']

        internal_json = {
            'blocks': blocks,
            'metadata': metadata
        }

        return internal_json
    
    def _add_text_block(self, internal_json, text_type, content, prev_id):
        
        blocks : list = internal_json['blocks']

        if prev_id is None:
                    
            new_block = {
                'page' : 0,
                'content_type' : 'text',
                'text' : {
                    'content' : content,
                    'type' : text_type
                },
                'block_id' : str(uuid.uuid4())
            }     
            blocks.insert(0, new_block)
            
        else:
            
            for i, block in enumerate(blocks):
                
                if block['block_id'] == prev_id:
                    
                    new_block = {
                        'page' : block['page'],
                        'content_type' : 'text',
                        'text' : {
                            'content' : content,
                            'type' : text_type
                        },
                        'block_id' : str(uuid.uuid4())
                    }
                    blocks.insert(i+1, new_block)
                    
                    break
            
        internal_json['blocks'] = blocks
        return self._generate_levels(internal_json)
    
    def insert_text_block(self, file_uuid, text_type, content, prev_id):

        """insert a text block in the internal json

        Returns:
            None
        """  
        logger.info("In header_service.py :: HeaderCorrectionServiceImpl :: insert_text_block")

        _, knowledge_source_path, _, _, _ = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        internal_json = self._add_text_block(internal_json, text_type, content, prev_id)
        self.__azure_blob_manager.update_data(blob_name=unquote(internal_json_path), data=json.dumps(internal_json).encode('utf-8'), return_type=ReturnTypes.URL.value,
                                              file_name=unquote(internal_json_path))
    def _remove_text_block(self, internal_json, block_id):
        
        blocks : list = internal_json['blocks']
        found = False
        
        for i, block in enumerate(blocks):
            
            if block['block_id'] == block_id:
                
                found = True
                if block['content_type'] != 'text':
                    raise InvalidValueProvidedException(f"block type of block with id {block_id} not text")
                    
                else:
                    blocks.pop(i)
                    break
        
        if not found:
            raise InvalidValueProvidedException(f"no block found with block id :: {block_id}")
        
        internal_json['blocks'] = blocks
        return self._generate_levels(internal_json)
        
    def delete_block(self, file_uuid, block_id):
        
        """delete a block from internal json

        Returns:
            None
        """ 
        logger.info("In header_service.py :: HeaderCorrectionServiceImpl :: delete_block")
        
        _, knowledge_source_path, _, _, _ = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        internal_json = self._remove_text_block(internal_json, block_id)
        
        self.__azure_blob_manager.update_data(blob_name=unquote(internal_json_path), data=json.dumps(internal_json).encode('utf-8'), return_type=ReturnTypes.URL.value,
                                              file_name=unquote(internal_json_path))
    def _update_text_blocks(self, internal_json, updated_blocks):
        
        existing_blocks : list = internal_json['blocks']

        id_map = {}
        for i in range(len(existing_blocks)):
            block = existing_blocks[i]
            id_map[block['block_id']] = i

        for block in updated_blocks:

            block_id = str(block['block_id'])
            index = id_map[block_id]

            if 'text' in existing_blocks[index]:
                existing_blocks[index]['text'] = {
                    'type': block['text_type'],
                    'content': block['content']
                }

        internal_json['blocks'] = existing_blocks

        internal_json = self._generate_levels(internal_json)
        return internal_json
    
    def update_headers(self, file_uuid, error_uuid, blocks):
        
        """updates the blocks of the internal json

        Returns:
            None
        """ 
        logger.info("In header_service.py :: HeaderCorrectionServiceImpl :: update_headers")
   
        knowledge_source_name, knowledge_source_path, status, customer_uuid, application_uuid = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        internal_json = self._update_text_blocks(internal_json, blocks)
        self.__azure_blob_manager.update_data(blob_name=unquote(internal_json_path), data=json.dumps(internal_json).encode('utf-8'), return_type=ReturnTypes.URL.value,
                                              file_name=unquote(internal_json_path))
        self._error_dao.update_error_status(error_uuid, 'Resolved')
        
        if status == 'Reviewed':
            
            chunk_collection, _, _ = self._error_dao.get_collections_by_customer_application(customer_uuid, application_uuid)
            self._error_dao.update_knowledge_source_status(file_uuid, 'Reviewing')
            
            delete_knowledge_source_chunks(knowledge_source_name, chunk_collection)
            add_knowledge_source_chunks(file_uuid, chunk_collection)