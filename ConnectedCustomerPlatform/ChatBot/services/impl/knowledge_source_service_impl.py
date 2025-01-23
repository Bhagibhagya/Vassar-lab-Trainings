from collections import Counter

import inspect
import logging
import os
import json
import re
import traceback
from urllib import response
from urllib.parse import unquote
from uuid import uuid4

from EmailApp.constant.constants import ReturnTypes
from Platform.utils import paginate_queryset
from ..interface.knowledge_source_service_interface import IKnowledgeSource
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.constants import ErrorConstants, KnowledgeSourceConstants, KnowledgeSourceTypes, InternalJsonConstants, Constants

from ConnectedCustomerPlatform.exceptions import CustomException, ResourceNotFoundException
from ConnectedCustomerPlatform.azure_service_utils import AzureBlobManager

from ChatBot.dao.interface.knowledge_sources_dao_interface import IKnowledgeSourcesDao
from ChatBot.dao.interface.error_dao_interface import ErrorCorrectionDaoInterface
from ChatBot.dao.interface.sme_dao_interface import ISMEDao

from ChatBot.dao.daos import get_dao
from django.conf import settings
from ChatBot.utils import get_collection_names, get_default_entity_file_attributes, get_knowledge_source_type, get_knowledge_source_path, get_base_url, validate_url, hit_url,get_knowledge_source_path
from DatabaseApp.models import KnowledgeSources
from EventHub.send_sync import EventHubProducerSync
import requests
import io
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import status
from AIServices.VectorStore.chromavectorstore import chroma_obj
import mimetypes

from ChatBot.dataclasses.knowledge_sources_data import FormattedJson
from ChatBot.utils import is_valid_uuid

from ce_shared_services.configuration_models.configuration_models import AzureBlobConfig
from ce_shared_services.factory.storage.azure_storage_factory import CloudStorageFactory


knowledge_source_processing_producer = EventHubProducerSync(settings.FILE_CONSUMER_EVENT_TOPIC)

azure_service_utils = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)

logger = logging.getLogger(__name__)


class KnowledgeSourceServiceImpl(IKnowledgeSource):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KnowledgeSourceServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, knowledge_source_dao=None,error_dao=None,entity_dao=None,media_dao=None,sme_dao=None, **kwargs,):
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            self.__knowledge_sources_dao: IKnowledgeSourcesDao = knowledge_source_dao or get_dao("knowledge_source_dao")
            self.__error_dao: ErrorCorrectionDaoInterface = error_dao or get_dao("error_dao")
            self.__entity_dao = entity_dao or get_dao("entity_dao")
            self.__media_dao = media_dao or get_dao("media_dao")

            self.__sme_dao: ISMEDao = sme_dao or get_dao("sme_dao")

            self.__sme_dao = sme_dao or get_dao("sme_dao")
            self.__azure_blob_manager = CloudStorageFactory.instantiate("AzureStorageManager", AzureBlobConfig(**settings.STORAGE_CONFIG))

            self.initialized = True
            logger.info("KnowledgeSourceServiceImpl initialized.")

    def get_knowledge_sources_for_question_and_answer(self, customer_uuid, application_uuid):
        
        reviewed_sources = self.__knowledge_sources_dao.get_reviewed_knowledge_sources_by_customer_and_application(
            customer_uuid, application_uuid)
        
        for ks in reviewed_sources:
            
            meta:dict = ks.pop('knowledge_source_metadata', {})
            message = None
            
            if meta.get('qa_reached', False) == True:
                message = 'Contents of this document have been updated. Please regenerate Q&A.'
                
            ks['message'] = message
        
        return reviewed_sources

    def get_video_type_knowledge_sources_in_application(self, customer_uuid, application_uuid):
        knowledge_sources = self.__knowledge_sources_dao.get_video_type_knowledge_sources_by_customer_and_application(
            customer_uuid, application_uuid)
        video_data = []
        for video in knowledge_sources:
            # Append the file data to the list
            video_data.append({
                'knowledge_source_name': video['knowledge_source_name'],
                'knowledge_source_uuid': str(video['knowledge_source_uuid']),
                'knowledge_source_url': video['knowledge_source_path'],
                'duration': video['knowledge_source_metadata'].get('duration')
            })
        response = {"videos": video_data, "message": "videos fetched successfully"}
        return response

    def get_knowledge_source_internal_json(self, knowledge_source_uuid):
        knowledge_source = self.__knowledge_sources_dao.get_knowledge_source_with_uuid(knowledge_source_uuid)

        knowledge_source_path = knowledge_source['knowledge_source_path']

        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path),
                                          KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(
            self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))

        if knowledge_source['knowledge_source_type'] != KnowledgeSourceTypes.WEB.value:
            blocks = internal_json['blocks']
            metadata = internal_json['metadata']
        else:
            blocks = []
            metadata = internal_json[knowledge_source['knowledge_source_name']]['metadata']
            for key, value in internal_json.items():
                blocks.extend(value['blocks'])

        pages = dict()
        for block in blocks:
            page_number = block.get('page', 1)
            pages[page_number] = pages.get(page_number, [])
            pages[page_number].append(block)

        review_json = {
            'metadata': metadata,
            'pages': pages
        }
        
        has_errors:bool = self.__error_dao.has_unresolved_errors(knowledge_source_uuid)
        ks_metadata:dict = knowledge_source['knowledge_source_metadata']
        
        chunked = ks_metadata.get('chunked', False)
        edited = ks_metadata.get('edited', False)

        if chunked:
            
            button_text = 'Rechunk'
            
            if edited:
                enable_review = True
            else:
                enable_review = False

        else:
            
            button_text = 'Review & Approve'

            if has_errors:
                enable_review = False
            else:
                enable_review = True

        response = {
            "message": "internal json fetched successfully",
            "review_json": review_json,
            "knowledge_source_status": knowledge_source['knowledge_source_status'],
            "enable_review": enable_review,
            "button_text" : button_text
        }
        return response
    

    def generate_formatted_json_from_internal_json(self, knowledge_source_uuid, page_number):
        """
            method to format internal_json into editable json format so that user can edit data

        """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        knowledge_source, internal_json = self.fetch_internal_json(knowledge_source_uuid=knowledge_source_uuid)
        if knowledge_source['knowledge_source_type'] != KnowledgeSourceTypes.WEB.value:
            blocks = internal_json[InternalJsonConstants.BLOCKS]
            metadata = internal_json[InternalJsonConstants.METADATA]
        else:
            blocks = []
            metadata = internal_json[knowledge_source['knowledge_source_name']][InternalJsonConstants.METADATA]
            for key, value in internal_json.items():
                blocks.extend(value[InternalJsonConstants.BLOCKS])

        internal_format_json = dict()
        for block in blocks:
            if str(block.get(InternalJsonConstants.PAGE)) == str(page_number):
                if block.get(InternalJsonConstants.CONTENT_TYPE) == InternalJsonConstants.TEXT:
                    self.__process_text_data(block=block, internal_format_json=internal_format_json)
                elif block.get(InternalJsonConstants.CONTENT_TYPE) == InternalJsonConstants.TABLE:
                    self.__process_table_data(block=block, internal_format_json=internal_format_json)
                elif block.get(InternalJsonConstants.CONTENT_TYPE) == InternalJsonConstants.IMAGE:
                    self.__process_image_data(block=block, internal_format_json=internal_format_json)

        review_json = {
            'metadata': metadata,
            'pages': internal_format_json
        }
        errs = self.__error_dao.has_unresolved_errors(knowledge_source_uuid)
        enable_review = True
        if errs:
            enable_review = False

        response = {
            "message": "internal json fetched successfully",
            "review_json": review_json,
            "knowledge_source_status": knowledge_source['knowledge_source_status'],
            "enable_review": enable_review,
        }
        return response

    def __process_text_data(self, block, internal_format_json):
        """process text data """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        block_id = block.get(InternalJsonConstants.BLOCK_ID)
        content_type = block.get(InternalJsonConstants.CONTENT_TYPE)
        logger.debug(f"processing text data of block_id:: {block_id}")
        text = block.get(InternalJsonConstants.TEXT) or {}
        content = text.get(InternalJsonConstants.CONTENT)
        text_type = text.get(InternalJsonConstants.TYPE)
        # empty string/text are not required
        if isinstance(content, str) and len(content.strip()) > 0:
            text_formatted_block = FormattedJson(value=content, block_id=block.get(InternalJsonConstants.BLOCK_ID), type=KnowledgeSourceConstants.STRING, content_type=content_type, page=str(block.get(InternalJsonConstants.PAGE)), label=KnowledgeSourceConstants.PLAIN_TEXT, required=True, text_type=text_type).to_dict()
            internal_format_json[block_id] = text_formatted_block

    def __process_table_data(self, block, internal_format_json):
        """process table data and convert into list of objects"""
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        block_id = block.get(InternalJsonConstants.BLOCK_ID)
        content_type = block.get(InternalJsonConstants.CONTENT_TYPE)
        logger.debug(f"processing table data of block_id:: {block_id}")
        table = block.get(InternalJsonConstants.TABLE) or {}
        name = table.get(InternalJsonConstants.NAME) or []
        table_name = name[-1] if len(name) > 0 else "Table_Data"
        data = table.get(InternalJsonConstants.DATA)
        if data:
            type_of_data = type(data).__name__
            if self.is_simple_table_view_data(data):
                logger.debug(f"table data with block_id::{block_id} is tabular_view")
                table_formatted_block = FormattedJson(value=data, block_id=block.get(InternalJsonConstants.BLOCK_ID),
                                                      type=KnowledgeSourceConstants.LIST, content_type=content_type,
                                                      page=str(block.get(InternalJsonConstants.PAGE)), label=table_name,
                                                      required=True, json_key=KnowledgeSourceConstants.DATA, is_simple_table_view=True).to_dict()
                internal_format_json[block_id] = table_formatted_block
            else:
                logger.debug(f"table data with block_id::{block_id} is not tabular_view")
                table_formatted_block = FormattedJson(value=data, block_id=block.get(InternalJsonConstants.BLOCK_ID),
                                                      type=type_of_data, content_type=content_type,
                                                      page=str(block.get(InternalJsonConstants.PAGE)), label=table_name,
                                                      required=True, json_key=KnowledgeSourceConstants.DATA).to_dict()
                internal_format_json[block_id] = table_formatted_block
        else:
            logger.error(f"table data of block_id::{block_id} is null or empty")

    def __process_image_data(self, block, internal_format_json):
        """ process image data based image classification """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        block_id = block.get(InternalJsonConstants.BLOCK_ID)
        logger.debug(f"processing image data of block_id:: {block_id}")
        content_type = block.get(InternalJsonConstants.CONTENT_TYPE)
        image = block.get(InternalJsonConstants.IMAGE) or {}
        name = image.get(InternalJsonConstants.NAME) or []
        image_name = name[-1] if len(name) > 0 else "Image-Data"
        image_classification = image.get(InternalJsonConstants.CLASSIFICATION)
        logger.debug(f"fetching {image_classification} type image data of block_id::{block_id}")
        data = image.get(InternalJsonConstants.DATA)
        logger.debug(f"block_id::{block_id} data::{data}")
        # if image is of Miscellaneous type we don't need to send data
        if (isinstance(image_classification, str) and image_classification.lower() != KnowledgeSourceConstants.MISCELLANEOUS.lower()) or isinstance(image_classification, list):
            # check whether data is falsy like not none , not empty etc..
            if data:
                type_of_data = type(data).__name__
                # is_simple_table_view_data = self.is_simple_table_view_data(data)
                if self.is_simple_table_view_data(data):
                    logger.debug(f"image data with block_id::{block_id} is tabular_view")
                    image_formatted_block = FormattedJson(
                        value=data, block_id=block.get(InternalJsonConstants.BLOCK_ID),
                        type=KnowledgeSourceConstants.LIST, content_type=content_type,
                        classification=image_classification,
                        page=str(block.get(InternalJsonConstants.PAGE)), label=image_name,
                        required=True, json_key=KnowledgeSourceConstants.DATA, is_simple_table_view=True
                    ).to_dict()
                    internal_format_json[block_id] = image_formatted_block
                elif self.is_hierarchical_data(data):
                    logger.debug(f"image data with block_id::{block_id} is hierarchy_data")
                    image_formatted_block = FormattedJson(
                        value=data, block_id=block.get(InternalJsonConstants.BLOCK_ID),
                        type=KnowledgeSourceConstants.DICT, content_type=content_type,
                        classification=image_classification,
                        page=str(block.get(InternalJsonConstants.PAGE)), label=image_name,
                        required=True, json_key=KnowledgeSourceConstants.DATA, is_hierarchy=True
                    ).to_dict()
                    internal_format_json[block_id] = image_formatted_block
                else:
                    image_formatted_block = FormattedJson(
                        value=data, block_id=block.get(InternalJsonConstants.BLOCK_ID),
                        type=type_of_data, content_type=content_type,
                        classification=image_classification,
                        page=str(block.get(InternalJsonConstants.PAGE)), label=image_name,
                        required=True, json_key=KnowledgeSourceConstants.DATA
                    ).to_dict()
                    internal_format_json[block_id] = image_formatted_block
            else:
                logger.error(f"image data for block_id :: {block_id} is null or empty")
        else:
            logger.debug(f"image with block_id::{block_id} is {KnowledgeSourceConstants.MISCELLANEOUS.lower()} type")

    def is_simple_table_view_data(self, data):
        """check whether data is list of objects where each object has key-value pair with 1-level"""
        # if it is not list we cant show as table in UI
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        if not isinstance(data, list):
            return False
        for item in data:
            if not isinstance(item, dict):
                return False
            for key, value in item.items():
                if isinstance(value, (list, tuple, dict, set)):
                    return False
        return True

    def is_hierarchical_data(self, data):
        """
            Verifies if the provided JSON data is hierarchical.
            Returns:
                - bool: True if the data is hierarchical, False otherwise.
        """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Base case: The data must be a dictionary
        if not isinstance(data, dict):
            return False
        list_value_key = []
        for key, value in data.items():
            if isinstance(value, list):
                list_value_key.append(key)
        if len(list_value_key) != 1:
            return False
        children_key = list_value_key[0]
        return self.is_hierarchical_data_with_child_key(data=data, children_key=children_key)

    def is_hierarchical_data_with_child_key(self, data, children_key):
        """verify whether json is hierarchical or not"""
        # Base case: The data must be a dictionary
        if not isinstance(data, dict):
            return False
        # Validate all keys except the `children_key`
        for key, value in data.items():
            if key != children_key:
                # Ensure the value is a primitive type (str, int, float, bool, None)
                if not isinstance(value, (str, int, float, bool, type(None))):
                    return False

        # Validate the `children_key`
        if children_key in data:
            # The value of `children_key` must be a list
            if not isinstance(data[children_key], list):
                return False
            # Recursively validate all children in the list
            for child in data[children_key]:
                if not self.is_hierarchical_data_with_child_key(child, children_key):
                    return False
        else:
            # If `children_key` is missing, it's invalid
            return False

        return True

    def editable_internal_json(self, knowledge_source_uuid, request_blocks):
        """
            making internal_json as editable
            Args:
               knowledge_source_uuid (str): unique identifier of knowledge_source
               request_blocks (dict): dict of page block objects
        """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        knowledge_source, internal_json = self.fetch_internal_json(knowledge_source_uuid=knowledge_source_uuid)
        knowledge_source_path = knowledge_source['knowledge_source_path']
        # check knowledge_source_type , whether web , pdf or etc..
        if knowledge_source['knowledge_source_type'] != KnowledgeSourceTypes.WEB.value:
            metadata = internal_json['metadata']
            blocks = internal_json[InternalJsonConstants.BLOCKS]
        else:
            blocks = []
            metadata = internal_json[knowledge_source['knowledge_source_name']]['metadata']
            for key, value in internal_json.items():
                blocks.extend(value[InternalJsonConstants.BLOCKS])
        total_page_count = metadata.get('page_count')
        is_valid = self.validate_request_blocks(request_blocks, total_page_count)
        # method to format list of blocks into dict of page list blocks
        formatted_internal_json_blocks = self.format_internal_json_blocks(blocks)
        # iterate over client request dict of page blocks
        newly_added_page = []
        for page, page_blocks in request_blocks.items():
            if page in formatted_internal_json_blocks:
                # update internal json page blocks with client request page blocks
                formatted_internal_json_blocks[str(page)] = page_blocks
            else:
                newly_added_page.append(str(page))
        # if user adding new list blocks for a page which don't have any blocks
        if len(newly_added_page)>0:
            formatted_internal_json_blocks = self.add_error_page_blocks(newly_added_page=newly_added_page, formatted_internal_json_blocks=formatted_internal_json_blocks, request_blocks=request_blocks)

        # revert dict formatted internal json blocks into list of blocks
        list_internal_json_blocks_format = self.revert_formatted_internal_json(formatted_internal_json_blocks)

        # update blocks field with new blocks
        internal_json[InternalJsonConstants.BLOCKS] = list_internal_json_blocks_format

        self.__update_internal_json(knowledge_source_uuid=knowledge_source_uuid, knowledge_source_path=knowledge_source_path, internal_json=internal_json)

        self._update_internal_json_edit_metadata(knowledge_source_uuid, knowledge_source['knowledge_source_metadata'])

    def _update_internal_json_edit_metadata(self, knowledge_source_uuid: str, knowledge_source_metadata: dict) -> None:
        
        knowledge_source_metadata.update({
            'edited' : True
        })
        self.__knowledge_sources_dao.update_metadata(knowledge_source_uuid, knowledge_source_metadata) 

    def add_error_page_blocks(self, newly_added_page, formatted_internal_json_blocks, request_blocks):
        """ method to add new page blocks if that page doesn't have blocks """
        if len(newly_added_page) > 1:
            raise CustomException(f"add new error page blocks one each time not multiple pages at a time")
        new_added_page_number = int(newly_added_page[0])
        list_format_internal_json = list(formatted_internal_json_blocks.items())
        for index, item in enumerate(list_format_internal_json):
            page_number = int(item[0])
            if new_added_page_number - page_number < 0:
                list_format_internal_json.insert(index, ( str(new_added_page_number), request_blocks[str(new_added_page_number)] ) )
                break
            elif index == len(list_format_internal_json)-1 and new_added_page_number - page_number > 0:
                list_format_internal_json.insert(index+1, ( str(new_added_page_number), request_blocks[str(new_added_page_number)] ) )
                break
        formatted_internal_json_blocks = dict(list_format_internal_json)
        return formatted_internal_json_blocks
    def format_internal_json_blocks(self, blocks):
        """ method to format internal json list block into dict blocks """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        pages = dict()
        for block in blocks:
            page_number = block.get(InternalJsonConstants.PAGE)
            pages[page_number] = pages.get(page_number, [])
            pages[page_number].append(block)
        return pages

    def revert_formatted_internal_json(self, formatted_blocks):
        """ method to format internal json dict block into list of blocks """
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        blocks = []
        for page, page_blocks in formatted_blocks.items():
            blocks.extend(page_blocks)
        return blocks

    def validate_request_blocks(self, blocks, total_page_count):
        if blocks is None:
            raise CustomException(f"blocks field cannot be empty or null")
        if not isinstance(blocks, dict):
            raise CustomException(f"The `blocks` field must be a dict.")
        unique_block_id_page = {}
        for key, value_list in blocks.items():
            if not isinstance(value_list, list):
                raise CustomException(f"page::{key} value must be list.")
            for index, single_block in enumerate(value_list):
                if not isinstance(single_block, dict):
                    raise CustomException(f"Block:{index+1} of Page:{key} is not a object or dict")
                self.validate_content_type_field(single_block, index, key)
                self.validate_page_field(single_block, index, key, total_page_count)
                self.validate_block_id_field(single_block, index, key)
                self.validate_level_field(single_block, index, key)
                block_id = single_block.get('block_id')
                if block_id in unique_block_id_page:
                    raise CustomException(f"Block:{index + 1} of Page:{key} This block ID already exists. Please use a unique ID.")
                unique_block_id_page[block_id] = single_block.get("page")
                if single_block.get("content_type") == "text":
                    self.validate_text_block(single_block, index, key)
                if single_block.get("content_type") == "table":
                    self.validate_table_block(single_block, index, key)
                if single_block.get("content_type") == "image":
                    self.validate_image_block(single_block, index, key)
        return True

    def validate_text_block(self, block, index, page_number):
        """check whether text block contains text, content field and valid values or not"""
        if 'text' not in block or not isinstance(block.get("text"), dict):
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have 'text' field, and it should not be empty or null. it should be object")
        text = block.get("text")
        if "type" not in text or text.get("type") is None or not isinstance(text.get("type"), str) or len(text.get("type")) <= 0:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'text' field's 'type' field, and it should not be empty or null. It should be a valid string.")
        if text.get("type") not in ["Body", "H1", "H2", "H3"]:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'text' field's 'type' field with a valid string value. possible values are 'Body', 'H1', 'H2', 'H3'")
        if "content" not in text or text.get("content") is None:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'text' field's 'content' field, and it should not be null.")
        if not isinstance(text.get("content"), str):
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'text' field's 'content' field with a valid string value.")
        if len(text.get("content")) <= 0:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'text' field's 'content' field, and it should not be empty.")
        return True

    def validate_table_block(self, block, index, page_number):
        """check whether table block contains table, name field and valid values or not"""
        if 'table' not in block or not isinstance(block.get("table"), dict):
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'table' field, and it should not be empty or null. it should be object")
        table = block.get("table")
        if "name" not in table or table.get("name") is None or not isinstance(table.get("name"), list) or len(table.get("name")) <= 0:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'table' field's 'name' field and it should not be null or empty. It should be list of valid strings")
        if "image_path" not in table or table.get("image_path") is None or not isinstance(table.get("image_path"), str) or len(table.get("image_path")) <= 0:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'table' field's 'image_path' field and it should not be null or empty. it should be a valid URL.")
        return True

    def validate_image_block(self, block, index, page_number):
        """check whether image block contains image, name field and valid values or not"""
        if 'image' not in block or not isinstance(block.get("image"), dict):
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'image' field, and it should not be empty or null. it should be object")
        image = block.get("image")
        if "name" not in image or image.get("name") is None or not isinstance(image.get("name"), list) or len(image.get("name")) <= 0:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'image' field's 'name' field and it should not be null or empty. It should be list of valid strings")
        if "image_path" not in image or image.get("image_path") is None or not isinstance(image.get("image_path"), str) or len(image.get("image_path")) <= 0:
            raise CustomException(f"Block:{index + 1} of Page:{page_number} should have the 'image' field's 'image_path' field and it should not be null or empty. it should be a valid URL.")
        return True

    def validate_page_field(self, block, block_index, page_number, total_page_count):
        """ method to validate page field in current block"""
        if "page" not in block or block.get("page") is None:
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should have the 'page' field, and it should not be empty or null.")
        if not isinstance(block.get("page"), str):
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should be string integer")
        if not block.get("page").isdigit():
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should have a valid 'page' field. It should be a positive integer.")
        if page_number != block.get("page"):
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} has an invalid page number. The current page is {page_number}. Please provide a page number that matches the current page.")
        if not (1 <= int(block.get("page")) <= total_page_count):
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} has an invalid page number. The file has only {total_page_count} pages. Please provide a valid page number within the range of 1 to {total_page_count}.")
        return True

    def validate_content_type_field(self, block, block_index, page_number):
        """ method to validate content_type field in current block """
        if "content_type" not in block or block.get("content_type") is None:
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should have 'content_type' field and it should not be empty or null")
        if not isinstance(block.get("content_type"), str) or block.get("content_type") not in ["text", "table", "image"]:
            raise CustomException(f"Block {block_index + 1} of Page:{page_number} the content_type field should be \"text,\" or \"table,\" or \"image.\"")
        return True

    def validate_block_id_field(self, block, block_index, page_number):
        """ method to validate block_id field in current block """
        if "block_id" not in block or block.get("block_id") is None:
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should have 'block_id' field and it should not be null")
        if isinstance(block.get("block_id"), str) and len(block.get("block_id")) <= 0:
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} 'block_id' should not be empty string")
        if not is_valid_uuid(block.get("block_id")):
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} 'block_id' should be valid uuid")
        return True

    def validate_level_field(self, block, block_index, page_number):
        """check whether each and every block contains 'level' field or not """
        if "level" not in block or block.get("level") is None:
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should have the 'level' field, and it should not be empty or null. It should be a valid integer.")
        if not isinstance(block.get("level"), int):
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should have a valid 'level' field. It should be an integer value.")
        if block.get("level") not in [1, 2, 3, 4]:
            raise CustomException(f"Block:{block_index + 1} of Page:{page_number} should have the 'level' field within a valid range(1 to 4). Please provide a valid level.")
        return True

    def format_blocks_to_dict(self, blocks:dict):
        """ helper method to format list of objects into dict"""
        blocks_dict = {}
        for page, block_list in blocks.items():
            page_number = str(page)
            if page_number not in blocks_dict:
                blocks_dict[page_number] = {}
            for single_block in block_list:
                block_id = single_block.get(InternalJsonConstants.BLOCK_ID)
                blocks_dict[page_number][block_id] = single_block
        return blocks_dict

    def check_keywords_in_classification(self, classification: str, keywords: list):
        """method check whether image classification contains certain keywords"""
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        classification = classification.lower()
        # Check if any of the keywords are in classification
        for keyword in keywords:
            if keyword.lower() in classification:
                return True  # Return True if any keyword is found
        return False  # Return False if none of the keywords are found

    def check_image_is_hierarchical(self, classification: str):
        """ check if image data is of hierarchical or not"""
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        if "hierarch" in classification.lower() or "organization" in classification.lower():
            return True
        return False

    def validate_image_data(self, data):
        """check whether data is list of objects where each object has key-value pair with 1-level"""
        # if it is not list we cant show as table in UI
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        if not isinstance(data, list):
            return False
        for item in data:
            if not isinstance(item, dict):
                return False
            for key, value in item.items():
                if isinstance(value, (list, tuple, dict, set)):
                    return False
        return True
      
    def update_knowledge_source_internal_json(self, knowledge_source_uuid, pages):
            """
                updates internal_json for a particular knowledge_source
            """
            logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
            knowledge_source, internal_json = self.fetch_internal_json(knowledge_source_uuid=knowledge_source_uuid)
            knowledge_source_path = knowledge_source['knowledge_source_path']
            pages = self.__format_pages_into_dict(pages=pages)
            # check knowledge_source_type , whether web , pdf or etc..
            if knowledge_source['knowledge_source_type'] != KnowledgeSourceTypes.WEB.value:
                blocks = internal_json[InternalJsonConstants.BLOCKS]
            else:
                blocks = []
                for key, value in internal_json.items():
                    blocks.extend(value[InternalJsonConstants.BLOCKS])

            # iterate to update blocks which are changed by user
            for block in blocks:
                # check if block is present in request page dict
                if block.get(InternalJsonConstants.BLOCK_ID) in pages:
                    self.__update_block(block=block, block_id=block.get(InternalJsonConstants.BLOCK_ID), page_dict=pages.get(block.get(InternalJsonConstants.BLOCK_ID)))
                    pages.pop(block.get(InternalJsonConstants.BLOCK_ID), None)
                if len(pages) <= 0:
                    break

            self.__update_internal_json(knowledge_source_uuid=knowledge_source_uuid, knowledge_source_path=knowledge_source_path, internal_json=internal_json)

            self._update_internal_json_edit_metadata(knowledge_source_uuid, knowledge_source['knowledge_source_metadata'])

    def __update_block(self, block, block_id, page_dict):
        """ update block according content_type of block"""
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        content_type = block.get(InternalJsonConstants.CONTENT_TYPE)
        logger.debug(f"trying to update {content_type} type block with block_id:: {block_id}")
        if content_type == InternalJsonConstants.TEXT:
            value = page_dict.get(KnowledgeSourceConstants.VALUE)
            text = block.get(InternalJsonConstants.TEXT) or {}
            text[InternalJsonConstants.CONTENT] = value

        elif content_type == InternalJsonConstants.TABLE:
            value = page_dict.get(KnowledgeSourceConstants.VALUE)
            table = block.get(InternalJsonConstants.TABLE) or {}
            if value:
                table[InternalJsonConstants.DATA] = value

        elif content_type == InternalJsonConstants.IMAGE:
            value = page_dict.get(KnowledgeSourceConstants.VALUE)
            json_key = page_dict.get(KnowledgeSourceConstants.JSON_KEY)
            image = block.get(InternalJsonConstants.IMAGE) or {}
            # if image_data exist then only update
            if value:
                image[InternalJsonConstants.DATA] = value

    def __format_pages_into_dict(self, pages: list):
            """method to format list of (block) objects into dict of key(block_id) and values(object)"""
            logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
            new_pages_dict = {}
            for page in pages:
                new_pages_dict.update(page)
            return new_pages_dict


    def __update_internal_json(self, knowledge_source_uuid, knowledge_source_path, internal_json):
            """update internal_json with updated internal_json in azure blob storage"""
            logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
            logger.debug(f"updating internal_json for knowledge_source_uuid:: {knowledge_source_uuid}")
            internal_json_path = os.path.join(os.path.dirname(knowledge_source_path),
                                              KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
            self.__azure_blob_manager.update_data(blob_name=unquote(internal_json_path),data = json.dumps(internal_json).encode('utf-8'),return_type=ReturnTypes.URL.value,file_name = unquote(internal_json_path))
            return True

    def fetch_internal_json(self, knowledge_source_uuid):
        """fetch internal json based on knowledge_source"""
        logger.debug(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"fetching internal_json from azure storage for knowledge_source_uuid:: {knowledge_source_uuid}")
        knowledge_source = self.__knowledge_sources_dao.get_knowledge_source_with_uuid(knowledge_source_uuid)

        knowledge_source_path = knowledge_source['knowledge_source_path']

        internal_json_path = os.path.join(os.path.dirname(knowledge_source_path),
                                          KnowledgeSourceConstants.INTERNALFORMAT_JSON_FILE_NAME)
        internal_json = json.loads(
            self.__azure_blob_manager.download_data(unquote(internal_json_path)).decode('utf-8'))
        logger.debug(f"successfully fetched internal_json for knowledge_source_uuid:: {knowledge_source_uuid}")
        return knowledge_source, internal_json
    @transaction.atomic
    def add_knowledge_sources_in_application(self, data, user_uuid, customer_uuid, application_uuid, operation_type='create', knowledge_source_obj=None):
        """
        Adds or updates a knowledge source in the specified application based on the operation type.
        Supports both 'create' for new additions and 'update' for modifying existing knowledge sources.
        """
        logger.info("Performing '%s' operation on knowledge source for customer UUID: %s, application UUID: %s by user UUID: %s",
            operation_type, customer_uuid, application_uuid, user_uuid
        )
        knowledge_sources = data.get('knowledge_sources', [])
        i3s_flags=data.get('i3s',[])
        web_url = data.get('web_url')

        # If creating a new knowledge source, obtain or create a default entity for the application
        if operation_type=='create':
            default_entity = self.__entity_dao.get_or_create_default_entity(customer_uuid, application_uuid, user_uuid)
            default_entity_uuid = str(default_entity.entity_uuid)
            default_attribute_details_json = get_default_entity_file_attributes(default_entity.attribute_details_json)
        else:
            default_entity_uuid = default_attribute_details_json = None    
        
         # Prepare and process each knowledge source provided in the request          
        self.__prepare_knowledge_sources(knowledge_sources,i3s_flags, application_uuid, customer_uuid, user_uuid, default_entity_uuid, default_attribute_details_json,operation_type,knowledge_source_obj)
        
        # If a web URL knowledge source is provided, process it separately
        if web_url:
            self.__process_web_url_knowledge_source(web_url, application_uuid, customer_uuid, user_uuid,default_entity_uuid, default_attribute_details_json, operation_type,knowledge_source_obj
        )
  
            
    def __prepare_knowledge_sources(self,knowledge_sources, i3s_flags,application_uuid, customer_uuid, user_uuid, default_entity_uuid, default_attribute_details_json,operation_type,knowledge_source_obj):
        """
        Prepares knowledge sources for processing by checking their validity and creating or updating them as necessary.
        Valid sources are queued for further processing.
        """
        for idx,knowledge_source in enumerate(knowledge_sources):
            knowledge_source_name = knowledge_source.name
            knowledge_source_type = get_knowledge_source_type(knowledge_source_name)
            knowledge_source_uuid=uuid4() if operation_type=='create' else knowledge_source_obj['knowledge_source_uuid']

            # Check if metadata for this knowledge source already exists (only if operation is 'create')
            knowledge_source_exists = self.__knowledge_sources_dao.check_knowledge_sources_exists([knowledge_source_name],knowledge_source_uuid,customer_uuid,application_uuid)

            reason_for_failure = None
            is_i3s_enabled = False
            # Determine the processing status based on the type and metadata existence
            if knowledge_source_type is None:
                status = KnowledgeSources.KnowledgeSourceStatus.FAILED
                reason_for_failure = ErrorMessages.UNSUPPORTED_FILE
            elif len(knowledge_source_exists) > 0:
                status = KnowledgeSources.KnowledgeSourceStatus.FAILED
                reason_for_failure = ErrorMessages.KNOWLEDGE_SOURCE_ALREADY_EXISTS
            else:
                status = KnowledgeSources.KnowledgeSourceStatus.PROCESSING

            event_obj={'knowledge_source_name':knowledge_source_name,
                    'knowledge_source_type':knowledge_source_type, 
                    'knowledge_source_uuid':knowledge_source_uuid,
                    'implementation_type':'default',
                    }            # Create or update the knowledge source based on the operation type

            if i3s_flags and idx < len(i3s_flags) and i3s_flags[idx]:
                event_obj.update({'implementation_type':'i3s'})
                is_i3s_enabled = True
            if operation_type=='create':
                self.__knowledge_sources_dao.create_knowledge_source(
                    knowledge_source_uuid=knowledge_source_uuid,
                    knowledge_source_name=knowledge_source_name,
                    application_uuid=application_uuid,
                    knowledge_source_type=knowledge_source_type,
                    status=status,
                    user_uuid=user_uuid,
                    customer_uuid=customer_uuid,
                    entity_uuid=default_entity_uuid,
                    attribute_details_json=default_attribute_details_json,
                    reason_for_failure = reason_for_failure,
                    is_i3s_enabled = is_i3s_enabled
                )
                logger.info(f"Created knowledge source '{knowledge_source_name}'")
            else:
                metadata = knowledge_source_obj['knowledge_source_metadata']
                metadata['fail_cause']=reason_for_failure
                self.__knowledge_sources_dao.update_knowledge_source_details(knowledge_source_uuid,knowledge_source_name,knowledge_source_type,status,metadata,user_uuid,customer_uuid,application_uuid)
                logger.info(f"Updated knowledge source '{knowledge_source_name}'")
                event_obj['knowledge_source_path']=knowledge_source_obj['knowledge_source_path']


            if status==KnowledgeSources.KnowledgeSourceStatus.PROCESSING:  
                self.__process_knowledge_source_consumer_event(event_obj,operation_type,knowledge_source,customer_uuid,application_uuid)



    def __process_web_url_knowledge_source(self,web_url, application_uuid, customer_uuid, user_uuid,default_entity_uuid, default_attribute_details_json, operation_type,knowledge_source_obj):
            """
            Validates and processes a web URL knowledge source if provided.
            """
            status=KnowledgeSources.KnowledgeSourceStatus.PROCESSING
            reason_for_failure = None
            # Validate the URL format; raise exception if invalid
            if not validate_url(web_url):
                status = KnowledgeSources.KnowledgeSourceStatus.FAILED
                reason_for_failure = ErrorMessages.INVALID_WEB_URL
            
            # Extract the base URL to ensure uniformity in metadata checks
            web_url = get_base_url(web_url)
            logger.info(f"Base URL extracted: {web_url}")
            
            knowledge_source_uuid=uuid4() if operation_type=='create' else knowledge_source_obj['knowledge_source_uuid']

            # Check if a knowledge source with the same URL already exists
            knowledge_source_exists = (self.__knowledge_sources_dao.check_knowledge_sources_exists([web_url],knowledge_source_uuid,customer_uuid,application_uuid))
            # Determine the processing status based on the type and metadata existence

            if len(knowledge_source_exists)>0:
                status = KnowledgeSources.KnowledgeSourceStatus.FAILED
                reason_for_failure = ErrorMessages.DUPLICATE_WEB_URL

            
            # Verify that the URL is reachable; raise exception if unreachable
            if not hit_url(web_url):
                status = KnowledgeSources.KnowledgeSourceStatus.FAILED
                reason_for_failure = ErrorMessages.WEB_URL_NOT_REACHABLE

            
            event_obj={'knowledge_source_name':web_url, 
                    'knowledge_source_type':KnowledgeSourceTypes.WEB.value, 
                    'knowledge_source_uuid':knowledge_source_uuid,
                    'implementation_type':'default',
                    }            # Create or update the knowledge source based on the operation type
            if operation_type=='create':
                self.__knowledge_sources_dao.create_knowledge_source(
                    knowledge_source_uuid=knowledge_source_uuid,
                    knowledge_source_name=web_url,
                    application_uuid=application_uuid,
                    knowledge_source_type=KnowledgeSourceTypes.WEB.value,
                    customer_uuid=customer_uuid,
                    user_uuid=user_uuid,
                    status=status,
                    entity_uuid=default_entity_uuid,
                    attribute_details_json=default_attribute_details_json,
                    reason_for_failure = reason_for_failure,
                    is_i3s_enabled = False
                ) 
                logger.info(f"Created knowledge source '{web_url}'")

            else:
                metadata = knowledge_source_obj['knowledge_source_metadata']
                metadata['fail_cause']=reason_for_failure
                self.__knowledge_sources_dao.update_knowledge_source_details(knowledge_source_uuid,web_url,KnowledgeSourceTypes.WEB.value,status,metadata,user_uuid,customer_uuid,application_uuid)
                logger.info(f"Updated knowledge source '{web_url}'")
                event_obj['knowledge_source_path']=knowledge_source_obj['knowledge_source_path']

            # Trigger event processing for the knowledge source
            if status==KnowledgeSources.KnowledgeSourceStatus.PROCESSING:  
                self.__process_knowledge_source_consumer_event(event_obj,operation_type,None,customer_uuid,application_uuid,web_url)


    def __process_knowledge_source_consumer_event(self,knowledge_source_obj,operation_type,knowledge_source,customer_uuid,application_uuid, web_url=None):
        """
        Prepares and triggers the processing event for a knowledge source.
        Handles storage paths for web or file-based knowledge sources and sends an event for processing.
        """
        knowledge_source_name = knowledge_source_obj['knowledge_source_name']
        web_url_path = None
        knowledge_source_path=None
        
        # Check the knowledge source type and configure paths accordingly
        if knowledge_source_obj['knowledge_source_type'] == KnowledgeSourceTypes.WEB.value:
            folder_name = knowledge_source_name.replace('/', '-').replace('.', '_')
            web_url_path = get_knowledge_source_path(application_uuid,customer_uuid, knowledge_source_obj['knowledge_source_type'], folder_name)
            knowledge_source_path = web_url_path
        else:
            folder_name, _ = os.path.splitext(knowledge_source_name)
            knowledge_source_path = get_knowledge_source_path(application_uuid,customer_uuid, knowledge_source_obj['knowledge_source_type'], folder_name)
            file_name = f"{knowledge_source_obj['knowledge_source_type']}/{folder_name}/{knowledge_source_name}"
            knowledge_source_path = self.__azure_blob_manager.upload_data(data=knowledge_source.read(),file_name=file_name,over_write=True,customer_uuid=customer_uuid,
                                                         application_uuid=application_uuid,channel_type=Constants.CHAT)

        self.__knowledge_sources_dao.update_knowledge_source_path(knowledge_source_obj['knowledge_source_uuid'],knowledge_source_path)

        if operation_type == 'update' and knowledge_source_path != knowledge_source_obj['knowledge_source_path']:
            try:
                # Attempt to delete the old Azure Blob (exceptions are caught)
                self.__delete_blob_from_azure(
                    knowledge_source_name, 
                    knowledge_source_obj['knowledge_source_path']
                )
                logger.info(f"Updated knowledge source in application for UUID: '{knowledge_source_obj['knowledge_source_uuid']}'.")
            except Exception as e:
                # Log the exception, but do not raise it, allowing the transaction to proceed
                logger.error("Failed to delete blobs in Azure, Error: %s", e)

        # Prepare event details for the knowledge source processing consumer
        event = {
            'event_type': 'file-processing',
            'file_uuid': str(knowledge_source_obj['knowledge_source_uuid']),
            'file_name': knowledge_source_name,
            'file_type': knowledge_source_obj['knowledge_source_type'],
            'implementation_type':knowledge_source_obj['implementation_type']
        }

        # Send the event for asynchronous processing
        knowledge_source_processing_producer.send_event_data_batch(event)
        logger.info(f"Event sent for processing knowledge source: {knowledge_source_name} with event data: {event}")


    def reupload_knowledge_source(self,data, user_uuid, customer_uuid, application_uuid):
        """
        Reuploads a knowledge source by processing new data provided by the user.

        Args:
            data (dict): The updated knowledge source data for reupload.
            user_uuid (str): UUID of the user performing the reupload.
            customer_uuid (str): UUID of the customer to which the knowledge source belongs.
            application_uuid (str): UUID of the application associated with the knowledge source.

        Returns:
            Response or status indicating success or failure of the reupload process.
        """
        logger.info("Reuploading knowledge source for customer UUID: %s, application UUID: %s by user UUID: %s", 
                customer_uuid, application_uuid, user_uuid)
            
        knowledge_source_uuid = str(data.get('knowledge_source_uuid'))
        
        with transaction.atomic():

            knowledge_source = self.__knowledge_sources_dao.get_knowledge_source_with_uuid(knowledge_source_uuid)
            
            # Update in-cache answers for the knowledge source
            answers_with_questions = self.__sme_dao.questions_answers_of_knowledge_source(knowledge_source_uuid)
            
            answer_uuid_list, question_list = zip(*[
                (item['answer_uuid'], item['questions__question_uuid']) 
                for item in answers_with_questions 
                if item.get('questions__question_uuid') is not None
            ]) if answers_with_questions else ([], [])
            
            answer_uuid_list = list(answer_uuid_list)
            question_list = list(question_list)
            
            self.__sme_dao.in_cache_update_for_answers_of_knowledge_source(set(answer_uuid_list))
            logger.info(f"Updated in-cache answers for knowledge source: '{knowledge_source_uuid}'.")

            
            # Delete errors associated with the knowledge source
            self.__error_dao.delete_errors_of_knowledge_source(knowledge_source_uuid)
            logger.info(f"Deleted errors for knowledge source UUID: '{knowledge_source_uuid}'.")

            self.__media_dao.delete_media_of_knowledge_source(knowledge_source_uuid)
            logger.info(f"Deleted media for knowledge source UUID: '{knowledge_source_uuid}'.")

            knowledge_source_obj = {
                'knowledge_source_uuid': knowledge_source_uuid,
                'knowledge_source_metadata': knowledge_source['knowledge_source_metadata'],
                'knowledge_source_path':knowledge_source['knowledge_source_path']
            }
            # Update the knowledge source in the application
            self.add_knowledge_sources_in_application(
                data, user_uuid, customer_uuid, application_uuid, operation_type='update', knowledge_source_obj=knowledge_source_obj
            )
            collection_name, _ = get_collection_names(customer_uuid, application_uuid)

            #added chroma obj deletion in the end bcoz if any errors raised rollback will happen , finally this should happen
            chroma_obj.updating_deleted_metadata_in_cache(question_list, (answer_uuid_list), collection_name, True)

            # If the knowledge source status is REVIEWED, delete documents from the associated collection
            self.__delete_documents_from_chromadb(knowledge_source['knowledge_source_name'],knowledge_source['knowledge_source_status'], collection_name)
        

   
    def upload_image_to_azure(self, data, customer_uuid, application_uuid):
        """
        Uploads image files to Azure Blob Storage and returns a dictionary of presigned URLs.

        1. Validates image files in the input data; raises an error if none are found.
        2. Uploads each image to Azure Blob Storage and generates a presigned URL for access.
        3. Returns a dictionary mapping original image names to their presigned URLs.
        """
        logger.info("Starting image upload to Azure for application UUID: %s, customer UUID: %s", application_uuid, customer_uuid)
        
        image_files = data.get('images', [])
        
        # Check if image files are present
        if not image_files:
            logger.warning("No images found in data for upload.")
            return []

        response = []
        
        for image_file in image_files:
            obj = {'image_name': image_file.name}

            try:
                max_size_in_mb = KnowledgeSourceConstants.MAXIMUM_IMAGE_SIZE  # Maximum file size in MB
                mime_type,_ = mimetypes.guess_type(image_file.name)
                file_size_mb = image_file.size / (1024 * 1024) 

                # Check if the MIME type starts with 'image/'
                if not mime_type.startswith('image/'):
                    obj.update({'url': '', 'status': ErrorMessages.UNSUPPORTED_FORMAT})
                    logger.warning("Skipping non-image file: %s with MIME type: %s", image_file.name, mime_type)
                    response.append(obj)
                    continue

                # Check if the image file type is in the valid list
                image_extension = mime_type.split('/')[1].lower()
                if image_extension not in KnowledgeSourceConstants.VALID_IMAGE_TYPES:
                    obj.update({'url': '', 'status': ErrorMessages.INVALID_IMAGE})
                    logger.warning("Skipping invalid image file: %s with extension: %s", image_file.name, image_extension)
                    response.append(obj)
                    continue

                # Check if the file size is greater than the allowed limit (5 MB)
                if file_size_mb > max_size_in_mb:
                    obj.update({'url': '', 'status': ErrorMessages.INVALID_IMAGE_SIZE})
                    logger.warning("Skipping file: %s with size: %.2f MB", image_file.name, file_size_mb)
                    response.append(obj)
                    continue

                image_path = get_knowledge_source_path(application_uuid, customer_uuid, KnowledgeSourceConstants.SME, KnowledgeSourceTypes.IMAGE.value)
                _, extension = os.path.splitext(image_file.name)
                
                # Upload the image and get the blob URL
                blob_path = os.path.join(image_path, f"{uuid4()}{extension}")
                image_url = self.__azure_blob_manager.update_data(blob_name=blob_path,data=image_file,file_name=blob_path,return_type=ReturnTypes.URL.value)
                
                # Generate a presigned URL for accessing the image
                obj.update({
                    'url': image_url,
                    'status': KnowledgeSourceConstants.VALID_IMAGE
                })
                logger.info("Successfully uploaded and generated presigned URL for image: %s", image_file.name)

            except Exception as e:
                obj.update({'url': '', 'status':  ErrorMessages.FAILED_TO_GET_IMAGE})
                logger.error("Failed to upload or generate URL for image: %s, Error: %s", image_file.name, e)

            response.append(obj)
        
        logger.info("Completed image upload process for application UUID: %s, customer UUID: %s", application_uuid, customer_uuid)
        return response
        
    @transaction.atomic    
    def resolve_knowledge_source(self,knowledge_source_uuid: str,customer_uuid: str,application_uuid: str) -> None: 
        """
        Resolves a knowledge source identified by its UUID by sending a chunking event to the processing producer.
        
        :param knowledge_source_uuid: UUID of the knowledge source to resolve
        :raises ResourceNotFoundException: If the knowledge source is not found
        :raises CustomException: If the knowledge source is already resolved or has an invalid status
        """
        
        logger.info(f"Resolving knowledge source with UUID: {knowledge_source_uuid}")

        # Retrieve the knowledge source object from the DAO
        knowledge_source = self.__knowledge_sources_dao.get_knowledge_source_with_uuid(knowledge_source_uuid)

        total_errors = self.__error_dao.knowledge_source_errors_count(knowledge_source_uuid)
        if total_errors > 0:
            
            logger.error(f"Cannot resolve knowledge source UUID {knowledge_source_uuid} with unresolved errors '{total_errors}'.")
            raise CustomException(ErrorMessages.FILE_RESOLVE_ERROR, status_code=status.HTTP_403_FORBIDDEN)
        
        # fetch the chunk and cache collection names.
        chunk_collection_name, cache_collection_name = get_collection_names(customer_uuid,application_uuid)
        
        # Check if the knowledge source can be resolved.
        if knowledge_source['knowledge_source_status'] in (
            KnowledgeSources.KnowledgeSourceStatus.PROCESSING, 
            KnowledgeSources.KnowledgeSourceStatus.CHUNKING,
            KnowledgeSources.KnowledgeSourceStatus.QA_GENERATING
        ):
            
            logger.error(f"Cannot resolve knowledge source UUID {knowledge_source_uuid} with status '{knowledge_source['knowledge_source_status']}'.")
            raise CustomException(ErrorMessages.FILE_RESOLVE_STATUS_ERROR, status_code=status.HTTP_403_FORBIDDEN)

        # delete chunks.
        self._delete_chunks_by_knowledge_source_name(knowledge_source['knowledge_source_name'], chunk_collection_name)
        
        # delete Q&A.
        self._delete_qa_by_knowledge_source_name(knowledge_source['knowledge_source_name'], cache_collection_name, customer_uuid, application_uuid)

        # update the knowledge source status to False.
        self.__error_dao.update_knowledge_source_status(knowledge_source_uuid,KnowledgeSources.KnowledgeSourceStatus.CHUNKING)
        
        # update the qa status of the knowledge source
        self.__knowledge_sources_dao.update_qa_status(knowledge_source_uuid, False)
        
        # update the knowledge source metadata.
        ks_metadata: dict = knowledge_source['knowledge_source_metadata']
        ks_metadata.update({
            'chunked' : True,
            'edited' : False
        })
        
        # update the chunking metadata.
        self.__knowledge_sources_dao.update_metadata(knowledge_source_uuid, ks_metadata)
        
        # sending a chunking event to the producer.
        event = {
            'event_type': 'chunking',
            'collection_name': chunk_collection_name,
            'file_uuid': str(knowledge_source_uuid),
            'file_name':knowledge_source['knowledge_source_name'],
            'file_type':knowledge_source['knowledge_source_type']
        }
        knowledge_source_processing_producer.send_event_data_batch(event)

    def _delete_chunks_by_knowledge_source_name(self, knowledge_source_name: str, chunk_collection_name: str) -> None:
        
        """ 
        Delete knwoledge base chunks by knowledge_source_name
                
        :param knowledge_source_uuid: UUID of the knowledge source whose chunks have to be deleted
        :param customer_uuid: UUID of the customer
        :param application_uuid: UUID of the application
        """
        
        logger.info("In KnowledgeSourceServiceImpl class :: _delete_chunks_by_knowledge_source_name method")

        logger.info('Deleting chunks from multi vector retriever collection')
        mvr_collection_name = 'mvr_' + chunk_collection_name.removeprefix('cw_')
        chroma_obj.delete_docs_from_collection(mvr_collection_name, knowledge_source_name)
        
        logger.info('Deleting chunks from chunk collection')
        chroma_obj.delete_docs_from_collection(chunk_collection_name, knowledge_source_name)
        
    def _delete_qa_by_knowledge_source_name(self, knowledge_source_name: str, cache_collection_name: str, customer_uuid: str, application_uuid: str) -> None:
                
        """ 
        Delete questions and answers by knowledge_source_name
                
        :param knowledge_source_name: Name of the knowledge source whose Q&A have to be deleted
        :param cache_collection_name: name of the cache collection from which records have to be deleted
        :param customer_uuid: UUID of the customer
        :param application_uuid: UUID of the application
        """

        logger.info("In KnowledgeSourceServiceImpl class :: _delete_qa_by_knowledge_source_name method")
        
        answer_uuids = self.__sme_dao.get_answer_uuids_by_source(knowledge_source_name, customer_uuid, application_uuid)
        logger.info(f'length of answer uuids with source :: {len(answer_uuids)}')
        
        logger.info('Deleting cache questions from cache collection.')
        chroma_obj.delete_cache_by_answer_uuids(cache_collection_name, answer_uuids)
        
        logger.info('Deleting answers and db')
        self.__sme_dao.delete_by_answer_uuids(answer_uuids)
        
    def upload_files_via_drives(self, data, user_uuid, customer_uuid, application_uuid):   
        """
        Uploads files from specified cloud drives (Google Drive or OneDrive) 
        to the application, retrieving files based on provided file IDs and 
        access tokens.
        """
        
        uploaded_files = []  # List to hold the uploaded file objects
        files_list = data.get('files')
        access_token = data.get('access_token')
        file_upload_source = data.get('file_upload_source')
        
        for file in files_list:
            file_id = file.get('file_id')
            mimetype = file.get('mime_type')
            filename = file.get('file_name')
            # Generate the download URL for the file using its ID, name, MIME type, and upload source
            download_url = self.__generate_download_url(file_id, filename, mimetype, file_upload_source)

            # Set the Authorization header for the API request (bearer token for authentication)
            headers = {"Authorization": "Bearer " + access_token}

            # Download the file using the generated URL and the headers for authorization
            file_obj = self.__download_file(filename, headers, download_url)

            # Append the downloaded file object to the list of uploaded files
            uploaded_files.append(file_obj)

        if data.get('send_url',False):
            data={'images':uploaded_files}
            drive_image_urls=self.upload_image_to_azure(data, customer_uuid, application_uuid)
            return drive_image_urls
        data = {'knowledge_sources': uploaded_files}


        # Add the knowledge sources to the application
        self.add_knowledge_sources_in_application(data, user_uuid, customer_uuid, application_uuid)
        logger.info(f"Uploaded {len(uploaded_files)} files to the application for user UUID: '{user_uuid}'.")


    def __generate_download_url(self, file_id, filename, mimetype, file_upload_source):
        # Generate download URL based on file upload source, MIME type, and file extension
        if file_upload_source == KnowledgeSourceConstants.FILE_UPLOAD_SOURCE_CHOICES[0]:  
            if mimetype.startswith(KnowledgeSourceConstants.GOOGLE_APPS_MIME_TYPE_PREFIX):  
                # For Google Apps file, return export URL with appropriate MIME type
                return f"{KnowledgeSourceConstants.GOOGLE_DRIVE_API_BASE_URL}{file_id}/export?mimeType={KnowledgeSourceConstants.GOOGLE_DRIVE_MIME_TYPE_MAP.get(get_knowledge_source_type(filename))}"
            else:
                # For regular Google Drive file, return direct download URL
                return f"{KnowledgeSourceConstants.GOOGLE_DRIVE_API_BASE_URL}{file_id}?alt=media"

        else: 
            # For OneDrive file, return direct download URL
            return f"{KnowledgeSourceConstants.ONEDRIVE_API_BASE_URL}{file_id}/content"


    def __download_file(self,filename,headers,download_url):
        """
        downloads a file from a given URL, handles errors, and returns it as a ContentFile object.
        """
        try:
                # Fetch and store the file content
                file_bytes = io.BytesIO()
                
                with requests.get(download_url, headers=headers, stream=True) as response:
                    response.raise_for_status()  # Raise an error for bad responses

                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file_bytes.write(chunk)
                
                # Create a file object from the downloaded bytes
                file_obj = ContentFile(file_bytes.getbuffer(), filename)
                return file_obj

        except requests.exceptions.HTTPError:
            if response.status_code == 401:  # Unauthorized
                error_message = f"Unauthorized access: Please check your access token for file: '{filename}'"
            elif response.status_code == 403:  # Forbidden
                error_message = f"Access forbidden: for file: '{filename}"
            elif response.status_code == 404:  # Not Found or Gone
                error_message = f"File not found: for file: '{filename}"
            logger.error(error_message)
            raise CustomException(error_message, status_code=response.status_code)
        except requests.exceptions.ConnectionError:
            error_message = f"Network error occurred while trying to access file: '{filename}''."
            logger.error(error_message)
            raise CustomException(error_message, status_code=response.status_code)

        except requests.exceptions.Timeout:
            error_message = f"Timeout occurred while trying to access file: '{filename}''."
            logger.error(error_message)
            raise CustomException(error_message, status_code=response.status_code)

        except Exception:
            error_message = f"An unexpected error occurred while processing file: '{filename}'"
            logger.error(error_message)
            raise CustomException(error_message, status_code=response.status_code)


    def get_knowledge_sources_by_customer_and_application_ids(self, customer_uuid, application_uuid, params):
        """
        Retrieves a list of knowledge_sources based on customer and application UUIDs.
        """
        logger.debug("Retrieving knowledge_sources for customer_uuid: %s, application_uuid: %s", customer_uuid, application_uuid)

        # Fetch knowledge sources associated with the given customer and application
        knowledge_sources_queryset = self.__knowledge_sources_dao.get_knowledge_sources_by_customer_and_application_ids(customer_uuid, application_uuid,params)

        page, paginator =  paginate_queryset(knowledge_sources_queryset, params)

        total_entries = paginator.count

        data = page.object_list

        knowledge_sources_list = []
        # Iterate through each knowledge source and gather additional data
        for knowledge_source in data:
            knowledge_source_uuid = getattr(knowledge_source, 'knowledge_source_uuid', None)

            json_edited = False
            chunked = getattr(knowledge_source, 'knowledge_source_metadata', {}).get('chunked', False)
            edited =  getattr(knowledge_source, 'knowledge_source_metadata', {}).get('edited', False)
            
            if chunked and edited:
                json_edited = True
            
            # Fetch errors for the current knowledge source
            errors_queryset = self.__error_dao.get_errors_with_knowledge_source_uuid({'knowledge_source_uuid': knowledge_source_uuid})
            
            error_type_counts = Counter(
                error['error_type'] for error in errors_queryset if error['error_status'] == ErrorConstants.UNRESOLVED
            )

            # Prepare a dictionary with relevant details for the knowledge source
            knowledge_source_data = {
                'file_name': getattr(knowledge_source, 'knowledge_source_name', None),
                'file_uuid': knowledge_source_uuid,
                'is_i3s_enabled': getattr(knowledge_source, 'knowledge_source_metadata', {}).get('is_i3s_enabled', False),
                'errors':error_type_counts,
                'last_modified_time': str(getattr(knowledge_source, 'updated_ts', '')),
                'status': getattr(knowledge_source, 'knowledge_source_status', None),
                'file_type': getattr(knowledge_source, 'knowledge_source_type', None),
                'page_count': getattr(knowledge_source, 'knowledge_source_metadata', {}).get('page_count', None),
                'entity_details': {
                    'entity_uuid': getattr(knowledge_source.entity_uuid, 'entity_uuid',None),
                    'attributes': getattr(knowledge_source, 'attribute_details_json', {}),
                    'attribute_details_json': getattr(knowledge_source.entity_uuid, 'attribute_details_json', {})
                },
                'json_edited' : json_edited
            }
            knowledge_sources_list.append(knowledge_source_data)


        response = {
            'total_entries': total_entries,
            'knowledge_sources': knowledge_sources_list
        }
        logger.info("Knowledge Sources retrieved successfully.")
        return response
    
    def get_knowledge_sources_errors(self, params):
        """
        Retrieves knowledge source errors associated with a knowledge source uuid.
        """  

        logger.debug(f"Fetching knowledge source errors with for params: {params}")

        # Fetch errors associated with the given knowledge source UUID from the database
        errors_queryset = self.__error_dao.get_errors_with_knowledge_source_uuid(params)

        page, paginator = paginate_queryset(errors_queryset, params)

        # Construct the response containing the total count of errors and the paginated error entries
        response = {
            'total_entries': paginator.count,
            'errors': page.object_list
        }

        logger.debug("Errors of knowledge source retrieved: %d", paginator.count)
        return response


    def check_knowledge_sources_exists(self,data,customer_uuid, application_uuid):
        """
        Checks if specified knowledge source files exist in the database for a given user, 
        customer, and application UUID, returning a list of matching file names or IDs.
        """
        logger.debug(f"Fetching knowledge source errors with for params: {data} ,customer uuid :{customer_uuid},application uuid :{application_uuid}")

        knowledge_source_names = data.get("knowledge_source_names", [])
    
        # Query the database for knowledge sources with names in the provided list
        existing_knowledge_sources = self.__knowledge_sources_dao.check_knowledge_sources_exists(knowledge_source_names,data.get("knowledge_source_uuid"),customer_uuid,application_uuid)
        existing_knowledge_sources = [name.lower() for name in existing_knowledge_sources]

        # Constructing a response that checks the existence of each knowledge source in the provided list
        return {
            "knowledge_sources": [
                {
                    "knowledge_source_name": name,
                    "exists": name.lower() in existing_knowledge_sources
                }
                for name in knowledge_source_names
            ]
        }
    
    def delete_knowledge_source_by_uuid(self,knowledge_source_uuid, customer_uuid, application_uuid):
        """
        deletes knowledge source based on knowledge_source_uuid
        """ 
        logger.debug("Retrieving knowledge_sources for customer_uuid: %s, application_uuid: %s,knowledge_source_uuid :%s", customer_uuid, application_uuid,knowledge_source_uuid)

        knowledge_source = self.__knowledge_sources_dao.get_knowledge_source_with_uuid(knowledge_source_uuid)
        with transaction.atomic():
            self.__knowledge_sources_dao.delete_knowledge_source_by_uuid(knowledge_source_uuid)
            # Delete media associated with the knowledge source
            self.__media_dao.delete_media_of_knowledge_source(knowledge_source_uuid)
            logger.info(f"Deleted media for knowledge source UUID: '{knowledge_source_uuid}'.")

            self.__sme_dao.delete_answers_of_knowledge_source(str(knowledge_source_uuid))
            collection_name, _ = get_collection_names(customer_uuid, application_uuid)

            # Attempt to delete associated documents from ChromaDB if the status is REVIEWED
            self.__delete_documents_from_chromadb(knowledge_source['knowledge_source_name'],knowledge_source['knowledge_source_status'], collection_name)

        # Separate try-except block for Azure Blob deletion (no atomic transaction here)
        self.__delete_blob_from_azure(knowledge_source['knowledge_source_name'],knowledge_source['knowledge_source_path'])
        # Delete the knowledge source itself
        logger.info(f"Knowledge source '{knowledge_source['knowledge_source_name']}' deleted successfully.")
        

    def get_knowledge_source_by_knowledge_source_uuid(self, knowledge_source_uuid):
        """
        retrieves knowledge source info based on knowledge_source_uuid
        """

        knowledge_source = self.__knowledge_sources_dao.get_knowledge_source_with_uuid(knowledge_source_uuid)
       
        # Validate knowledge source status
        if knowledge_source['knowledge_source_status'] in [KnowledgeSources.KnowledgeSourceStatus.PROCESSING, KnowledgeSources.KnowledgeSourceStatus.FAILED]:
            logger.error(f"Cannot retrieve knowledge source with knowledge source status: {knowledge_source['knowledge_source_status']}")
            raise CustomException(f"Cannot retrieve knowledge source with knowledge source status: {knowledge_source['knowledge_source_status']}")

        knowledge_source_path = knowledge_source['knowledge_source_path']
        knowledge_source_name = knowledge_source['knowledge_source_name']
        knowledge_source_type = knowledge_source['knowledge_source_type']
        return self.__get_blob_url_for_knowledge_source(knowledge_source_name, knowledge_source_path, knowledge_source_type)
    


    def __get_blob_url_for_knowledge_source(self,knowledge_source_name, knowledge_source_path, knowledge_source_type):
        """
        Generates a presigned blob URL for a knowledge source based on its type or returns None if the type is unrecognized.
        """
        blob_url = None
        ext = get_knowledge_source_type(knowledge_source_name)
        file_type = KnowledgeSourceTypes.PDF.value

        # Handle different types of knowledge sources (Word, PPT, Excel)
        if ext in [KnowledgeSourceTypes.WORD.value, KnowledgeSourceTypes.PPT.value, KnowledgeSourceTypes.EXCEL.value]:
            parts = knowledge_source_path.split(".")
            parts[-1] = KnowledgeSourceTypes.PDF.value  # Convert to PDF
            updated_knowledge_source_path = ".".join(parts)
            blob_url = updated_knowledge_source_path

        # Handle PDF and Video types
        elif ext in [KnowledgeSourceTypes.PDF.value, KnowledgeSourceTypes.VIDEO.value,KnowledgeSourceTypes.IMAGE.value]:
            blob_url = knowledge_source_path
            file_type = ext

        # Handle Web URLs
        elif knowledge_source_type == KnowledgeSourceTypes.WEB.value:
            blob_url = knowledge_source_path

        # Return the blob URL if it was set; otherwise, return None
        response = {
            'knowledge_source_url': blob_url,
            'knowledge_source_type': file_type,
            'knowledge_source_name': knowledge_source_name
        }

        logger.info(f"Successfully generated presigned URL for knowledge source: {knowledge_source_name}")
        return response

    def __delete_documents_from_chromadb(self,knowledge_source_name,knowledge_source_status, collection_name: str):
        "Deletes documents from ChromaDB if the knowledge source status is 'REVIEWED'."
        if knowledge_source_status == KnowledgeSources.KnowledgeSourceStatus.REVIEWED:
                try:
                    
                    mvr_collection_name = 'mvr_' + collection_name.removeprefix('cw_')
                    logger.info(f'mvr collection name :: {mvr_collection_name}')
                    
                    chroma_obj.delete_docs_from_collection(mvr_collection_name, knowledge_source_name)
                    logger.info(f"Deleted documents from multi vector collection '{mvr_collection_name}' for knowledge source '{knowledge_source_name}'.")
                    
                    chroma_obj.delete_docs_from_collection(collection_name, knowledge_source_name)
                    logger.info(f"Deleted documents from collection '{collection_name}' for knowledge source '{knowledge_source_name}'.")
                    
                except Exception as e:
                    logger.error(f"Failed to delete documents from collection '{collection_name}' for knowledge source '{knowledge_source_name}': {e}")
                    raise CustomException(f"Failed to delete documents from collection '{collection_name}' for knowledge source '{knowledge_source_name}'")


    def __delete_blob_from_azure(self,knowledge_source_name,knowledge_source_path):
        """
        Deletes a blob from Azure Blob Storage based on the knowledge source metadata.
        """
        try:
            folder_name = os.path.dirname(knowledge_source_path)
            azure_service_utils.delete_blob(folder_name)
            logger.info(f"Deleted blob for knowledge source '{knowledge_source_name}'.")
        except Exception as e:
            logger.error(f"Failed to delete blob for knowledge source '{knowledge_source_name}': {e}")        



