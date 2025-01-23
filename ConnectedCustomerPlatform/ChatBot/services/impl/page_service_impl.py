import json
import os

import uuid
import pandas
import base64
from urllib.parse import urlparse, unquote
from django.conf import settings

from EmailApp.constant.constants import ReturnTypes
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager

from ChatBot.constant.constants import KnowledgeSourceConstants
from ChatBot.utils import get_knowledge_source_path

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException

from ChatBot.services.interface.page_service_interface import PageCorrectionServiceInterface
from ChatBot.dao.impl.error_dao_impl import ErrorCorrectionDaoImpl
from ChatBot.dao.interface.error_dao_interface import ErrorCorrectionDaoInterface

from ChatBot.views.files import add_knowledge_source_chunks, delete_knowledge_source_chunks

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


class PageCorrectionServiceImpl(PageCorrectionServiceInterface):
    
    def __init__(self):
        
        self._error_dao : ErrorCorrectionDaoInterface = ErrorCorrectionDaoImpl()
        self.azure_service_utils = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)
        self.__azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))


    def _get_blocks_by_page(self, internal_json, page_number):
        
        blocks = internal_json['blocks']
        last_page = blocks[-1]['page']
        
        if page_number > int(last_page):
            raise InvalidValueProvidedException(f"no page exist with page :: {page_number}")
        
        page_blocks = []
        for block in blocks:
            
            if int(block['page']) == page_number:
                page_blocks.append(block)
                
        return page_blocks
    
    def get_page_blocks(self, file_uuid, page_number):

        """get the internal json blocks of a page
         
        Returns:
            list of blocks of that page
        """ 
        logger.info("In page_service.py :: PageCorrectionServiceImpl :: get_page_blocks")
        
        _, knowledge_source_path, _, _, _ = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        page_blocks = self._get_blocks_by_page(internal_json, page_number)
        result_blocks = []
        
        for block in page_blocks:
            
            block_type = block['content_type']
            
            if block_type == 'text':
                
                result_blocks.append({
                    'block_type': block_type,
                    'text_type': block[block_type]['type'],
                    'content': block[block_type]['content']
                })

            elif block_type == 'image':
                
                image_url = block[block_type]['image_path']

                result_blocks.append({
                    'block_type': block_type,
                    'name': block[block_type]['name'],
                    'content': block[block_type]['content'],
                    'url': image_url
                })

            elif block_type == 'table':

                image_path = block[block_type]['image_path']
                image_url = None
                
                if image_path:
                    image_url = image_path
                
                table_content = block[block_type]['content']
                table_json = json.loads(table_content)

                if not table_json:
                    continue

                data_frame = pandas.DataFrame(table_json[1:], columns=table_json[0])if isinstance(table_json[0], list)else pandas.DataFrame(table_json)
                columns = data_frame.columns.tolist()
                matrix = data_frame.to_numpy().tolist()

                result_blocks.append({
                    'block_type': block_type,
                    'name': block[block_type]['name'],
                    'columns': columns,
                    'matrix': matrix,
                    'url': image_url
                })
                
        return result_blocks
    
    def _add_media(self, name, path, content, page, source_uuid, customer_uuid, application_uuid):
        
        media_id = str(uuid.uuid4())
        details = {
            'page' : page,
            'content' : content
        }
        self._error_dao.add_media(media_id, name, path, details, source_uuid, customer_uuid, application_uuid)
        
    def _parse_blocks(self, page_number, blocks, file_uuid, customer_uuid, application_uuid):
        
        page_blocks = []
        for block in blocks:
            
            block_id = str(uuid.uuid4())
            block_type = block['block_type']
            
            if block_type == 'text' and block['content'] != "":

                internal_block = {
                    'block_id': block_id,
                    'page': page_number,
                    'content_type': block_type,
                    'text': {
                        'type': block['text_type'],
                        'content': block['content']
                    }
                }
                page_blocks.append(internal_block)

            elif block_type == 'image' and block['url']:
                
                url = block['url']
                _, blob_name = self.azure_service_utils.parse_blob_url(url)
                blob_name = urlparse(blob_name).path
                
                internal_block = {
                    'block_id': block_id,
                    'page': page_number,
                    'content_type': block_type,
                    'image': {
                        'name': block['name'],
                        'content': block['content'],
                        'image_path': blob_name
                    }
                }
                page_blocks.append(internal_block)
                
                self._add_media(block['name'], blob_name, block['content'], page_number, file_uuid, customer_uuid, application_uuid)
                
            elif block_type == 'table' and block['columns'] and block['matrix']:

                columns = block['columns']
                matrix = block['matrix']

                data_frame = pandas.DataFrame(matrix, columns=columns)
                table_json = data_frame.to_dict('records')
                table_content = json.dumps(table_json)

                blob_name = ""
                if 'url' in block and block['url']:
                    
                    url = block['url']
                    _, blob_name = self.azure_service_utils.parse_blob_url(url)
                    blob_name = urlparse(blob_name).path

                internal_block = {
                    'block_id': block_id,
                    'page': page_number,
                    'content_type': block_type,
                    'table': {
                        'name': block['name'],
                        'content': table_content,
                        'image_path': blob_name
                    }
                }
                page_blocks.append(internal_block)
                
                self._add_media(block['name'], blob_name, table_content, page_number, file_uuid, customer_uuid, application_uuid)

        return page_blocks        

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

    def _replace_page_blocks(self, internal_json, page_blocks, page_number):
        
        blocks : list = internal_json['blocks']
        n = len(blocks)
        last_page = blocks[n - 1]['page']
        if page_number > int(last_page):
            blocks.extend(page_blocks)
        
        else:
            
            blocks = [block for block in blocks if int(block['page']) != page_number]
            for i in range(len(blocks)):

                block = blocks[i]  
               
                if int(block['page']) >= page_number:

                    for new_block in page_blocks:
                        blocks.insert(i, new_block)
                        i += 1
                        
                    break    
        
        internal_json['blocks'] = blocks
        return self._generate_levels(internal_json)
    
    def page_correction(self, file_uuid, error_uuid, page_number, blocks):
        
        """update the blocks of a page
         
        Returns:
            None
        """
        logger.info("In page_service.py :: PageCorrectionServiceImpl :: page_correction")
        
        file_name, knowledge_source_path, file_status, customer_uuid, application_uuid = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        page_blocks = self._parse_blocks(page_number, blocks, file_uuid, customer_uuid, application_uuid)
        internal_json = self._replace_page_blocks(internal_json, page_blocks, page_number)
        self.__azure_blob_manager.update_data(blob_name=unquote(internal_json_path), data=json.dumps(internal_json).encode('utf-8'), return_type=ReturnTypes.URL.value,
                                              file_name=unquote(internal_json_path))
        self._error_dao.update_error_status(error_uuid, 'Resolved')
        
        if file_status == 'Reviewed':
            
            chunk_collection, _, _ = self._error_dao.get_collections_by_customer_application(customer_uuid, application_uuid)
            self._error_dao.update_knowledge_source_status(file_uuid, 'Reviewing')
            
            delete_knowledge_source_chunks(file_name, chunk_collection)
            add_knowledge_source_chunks(file_uuid, chunk_collection)
