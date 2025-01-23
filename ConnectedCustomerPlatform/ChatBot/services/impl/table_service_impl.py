import os
import json
from urllib.parse import unquote

import pandas

from django.conf import settings

from EmailApp.constant.constants import ReturnTypes
from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException

from ChatBot.constant.constants import KnowledgeSourceConstants

from ChatBot.services.interface.table_service_interface import TableCorrectionServiceInterface
from ChatBot.dao.impl.error_dao_impl import ErrorCorrectionDaoImpl
from ChatBot.dao.interface.error_dao_interface import ErrorCorrectionDaoInterface

from ChatBot.views.files import add_knowledge_source_chunks, delete_knowledge_source_chunks

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


class TableCorrectionServiceImpl(TableCorrectionServiceInterface):
    
    def __init__(self):
        
        self._error_dao : ErrorCorrectionDaoInterface = ErrorCorrectionDaoImpl()
        self.__azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

    
    def _get_columns_and_matrix(self, table):
        
        def normailize_rows(table):
            
            if table:
                max_size = max(len(row) for row in table)

                for row in table:
                    row_size = len(row)
                    row.extend(["" for _ in range(max_size - row_size)])

            return table
        
        if len(table):
            
            if isinstance(table[0], list):
                
                table = normailize_rows(table)
                data_frame = pandas.DataFrame(table[1:], columns=table[0])

            else:
                data_frame = pandas.DataFrame(table)
                
            columns = data_frame.columns.tolist()
            matrix = data_frame.to_numpy().tolist()

            return columns, matrix
                  
        return [], []
    
    def get_table(self, file_uuid, table_id):
        
        """get the table details of a table in internal json
        
        Returns:
            columns, matrix and table image url of the table
        """
        logger.info("In table_service.py :: TableCorrectionServiceImpl :: get_table")
        
        _, knowledge_source_path, _, _, _ = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        
        blocks = internal_json['blocks']
        
        image_url = None
        columns, matrix = [], []
        
        for block in blocks:

            if block['content_type'] == 'table' and block['block_id'] == str(table_id):
                table_data = json.loads(block['table']['content'])
                columns, matrix = self._get_columns_and_matrix(table_data)

                table_image_path = block['table']['image_path']
                
                if table_image_path:
                    image_url = table_image_path

                break
        
        return columns, matrix, image_url
    
    def get_table_from_file(self, binary_file):

        """get the table data from an uploaded xlsx or csv
        
        Returns:
            columns, matrix of the table
        """
        logger.info("In table_service.py :: TableCorrectionServiceImpl :: get_table_from_file")

        file_name = binary_file.name

        if str(file_name).endswith('xlsx') or str(file_name).endswith('xls'):
            data_frame = pandas.read_excel(binary_file, header=None).dropna(how='all')

        elif str(file_name).endswith('csv'):
            data_frame = pandas.read_csv(binary_file, encoding='ISO-8859-1', header=None).dropna(how='all')

        else:
            return ValueError("Unsupported file")

        data_frame = data_frame.fillna('')
        columns = data_frame.to_numpy()[0].tolist()
        matrix = data_frame.to_numpy().tolist()
        matrix = matrix[1:]

        return columns, matrix
    
    def update_table(self, file_uuid, error_uuid, table_id, columns, matrix):

        """update the table of the internal json
        
        Returns:
            None
        """
        logger.info("In table_service.py :: TableCorrectionServiceImpl :: get_table")

        file_name, knowledge_source_path, file_status, customer_uuid, application_uuid = self._error_dao.get_filedetails_by_fileuuid(file_uuid)
        
        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path), KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
   
        blocks = internal_json['blocks']
        found = False

        for block in blocks:

            if block['content_type'] == 'table' and block['block_id'] == str(table_id):
                found = True
                data_frame = pandas.DataFrame(matrix, columns=columns)
                json_string = data_frame.to_json(orient='records')
                block['table']['content'] = json_string
                
                break

        if not found:
            raise InvalidValueProvidedException(f"no table found with table_id :: {table_id}")

        internal_json['blocks'] = blocks
        self.__azure_blob_manager.update_data(blob_name=unquote(internal_json_path), data=json.dumps(internal_json).encode('utf-8'), return_type=ReturnTypes.URL.value,
                                              file_name=unquote(internal_json_path))
        self._error_dao.update_error_status(error_uuid, 'Resolved')
        
        if file_status == 'Reviewed':
            
            chunk_collection, _, _ = self._error_dao.get_collections_by_customer_application(customer_uuid, application_uuid)
            self._error_dao.update_knowledge_source_status(file_uuid, 'Reviewing')
            
            delete_knowledge_source_chunks(file_name, chunk_collection)
            add_knowledge_source_chunks(file_uuid, chunk_collection)
