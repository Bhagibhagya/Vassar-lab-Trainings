from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.serializers import InsertTextBlockSerializer, UpdateHeaderSerializer, DeleteBlockSerializer

from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from ConnectedCustomerPlatform.responses import CustomResponse

from ChatBot.services.impl.header_service_impl import HeaderCorrectionServiceImpl
from ChatBot.services.interface.header_service_interface import HeaderCorrectionServiceInterface

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class HeaderCorrectionViewSet(ViewSet):
    
    """
    HeaderCorrectionViewSet:
    
    APIs
    
    1.get_h1_headings : API to fetch all the main heading blocks in the internal json of a file
    2.get_child_blocks : API to fetch the child blocks under a parent block
    3.insert_text_block : API to insert a text block in the internal json of a file
    4.delete_block : API to delete a text block of the internal json of a file
    5.update_headers : API to update the text types of the blocks of the internal json of a file
    """
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self._header_service : HeaderCorrectionServiceInterface = HeaderCorrectionServiceImpl()

    def _validate_uuid(self, id):
        
        if id is None:
            return False
        
        if len(str(id)) == 0:
            return False
        
        return True

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="file_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING,description='File ID')],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=["get"])
    def get_h1_headings(self, request, file_uuid):
        
        """
        Retrieves H1 headings from a file's internal JSON data.

        Parameters:
            - request: HTTP request object
            - file_uuid (required): ID of the file to retrieve H1 headings from
        """
        logger.info("In header_view.py ::  HeaderCorrectionViewSet :: get_h1_headings")
        
        if not self._validate_uuid(file_uuid):
            raise InvalidValueProvidedException("file_uuid invalid")
        
        level1_blocks, application_uuid = self._header_service.get_h1_headings(file_uuid)
          
        response = {
            "blocks": level1_blocks,
            "file_uuid": file_uuid,
            "application_uuid": application_uuid
        }
        
        return CustomResponse(result=response)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="file_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING),
                           openapi.Parameter(name="block_id", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['get'])
    def get_child_blocks(self, request, file_uuid, block_id):
         
        """
        Retrieves child blocks under a specified block ID from a file's internal JSON data.

        Parameters:
            - request: HTTP request object
            - file_uuid (required): ID of the file containing the block
            - block_id (required): ID of the block to retrieve child blocks 
        """
        logger.info("In header_view.py :: HeaderCorrectionViewSet :: :: :: get_child_blocks")
        
        if not self._validate_uuid(file_uuid):
            raise InvalidValueProvidedException("file_uuid invalid")
        
        if not self._validate_uuid(block_id):
            raise InvalidValueProvidedException("block_id invalid")
        
        child_blocks = self._header_service.get_child_blocks(str(file_uuid), str(block_id))

        response = {
            "message": "fetched child blocks successfully",
            "blocks": child_blocks,
            "file_uuid": file_uuid
        }
        return CustomResponse(result=response)

    @swagger_auto_schema(
        request_body=InsertTextBlockSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.BLOCK_INSERTED_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['post'])
    def insert_text_block(self, request):
         
        """
        Inserts a text block into a file's internal JSON structure.

        Parameters:
            - request: HTTP request object containing data to insert a text block
              - Expected data in request: 'file_uuid', 'previous_block_id', 'block'
            - file_uuid (required): ID of the file to insert the text block into
            - previous_block_id (optional): ID of the previous block where the new block will be inserted after
            - block (required): Dictionary containing details of the text block to insert
              - Expected keys in 'block': 'text_type', 'content'

        Returns:
            - CustomResponse: Response containing information about the inserted block
        """
        logger.info("In header_view.py :: HeaderCorrectionViewSet :: insert_text_block")
        
        serializer = InsertTextBlockSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        file_uuid = data.get('file_uuid')
        prev_id = data.get('previous_block_id')
        block = data.get('block')
        text_type = block['text_type']
        content = block['content']

        self._header_service.insert_text_block(file_uuid, text_type, content, prev_id)

        return CustomResponse(SuccessMessages.BLOCK_INSERTED_SUCCESS)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="file_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING),
                           openapi.Parameter(name="block_id", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_200_OK: SuccessMessages.BLOCK_DELETED_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_block(self, request):
           
        """
        Deletes a text block from a file's internal JSON structure.

        Parameters:
            - request: HTTP request object
            - file_uuid (required): ID of the file containing the block to delete
            - block_id (required): ID of the block to delete
        """
        logger.info("In header_view.py :: HeaderCorrectionViewSet :: delete_block")       
        
        serializer = DeleteBlockSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        file_uuid = data.get('file_uuid')
        block_id = data.get('block_id')
        
        self._header_service.delete_block(str(file_uuid), str(block_id))
        
        return CustomResponse(SuccessMessages.BLOCK_DELETED_SUCCESS)

    @swagger_auto_schema(
        request_body=UpdateHeaderSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.HEADERS_UPDATED_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['put'])
    def update_headers(self, request):
        
        """
        Updates headers in a file's internal JSON structure and triggers related events.

        Parameters:
            - request: HTTP request object containing data to update headers
            - file_uuid (required): ID of the file to update headers for
            - blocks (required): List of blocks containing header information to update
        """
        logger.info("In header_view.py :: HeaderCorrectionViewSet :: update_headers")
        
        serializer = UpdateHeaderSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        file_uuid = data.get('file_uuid')
        error_uuid = data.get('error_uuid')
        blocks = data.get('blocks')

        self._header_service.update_headers(str(file_uuid), str(error_uuid), blocks)

        return CustomResponse(SuccessMessages.HEADERS_UPDATED_SUCCESS)