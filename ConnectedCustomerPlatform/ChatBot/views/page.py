from Platform.constant import constants

from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.constants import KnowledgeSourceConstants

from ChatBot.serializers import PageCorrectionSerializer, get_error_messages

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse

from ChatBot.services.impl.page_service_impl import PageCorrectionServiceImpl
from ChatBot.services.interface.page_service_interface import PageCorrectionServiceInterface

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class PageCorrectionViewSet(ViewSet):
    
    """
    PageCorrectionViewSet:
    
    APIs
    
    1.get_page_blocks : API to fetch the blocks of a page of the internal json of a file
    2.page_correction : API to update the blocks of a page of the internal json of a file
    """
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self._page_service : PageCorrectionServiceInterface = PageCorrectionServiceImpl()
        
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="file_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING),
                           openapi.Parameter(name="page", in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['get'])
    def get_page_blocks(self, request, file_uuid, page):
        
        """
        Retrieves blocks from a specific page of a file's internal JSON structure.

        Parameters:
            - request: HTTP request object
            - file_uuid (required): ID of the file to retrieve blocks from
            - page (required): Page number to retrieve blocks from
        """
        logger.info("In page_view.py :: PageCorrectionViewSet :: get_page_blocks")
        
        page_blocks = self._page_service.get_page_blocks(file_uuid, page)
        
        response = {
            "message": "fetched page blocks of the file successfully",
            "page": page,
            "blocks": page_blocks,
            "no_of_blocks": len(page_blocks)
        }
        return CustomResponse(response)

    @swagger_auto_schema(
        request_body=PageCorrectionSerializer,
        manual_parameters=[constants.customer_uuid_header],
        responses={
            status.HTTP_200_OK: SuccessMessages.PAGE_CORRECTION_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['post'])
    def page_correction(self, request):
        
        """
        Processes page correction for a file, including adding or updating blocks on a specified page.

        Parameters:
            - request: HTTP request object containing data for page correction
            - file_uuid (required): ID of the file to perform page correction on
            - page (required): Page number to correct within the file
            - blocks (required): List of blocks containing text, image, or table data to add or update
        """
        logger.info("In page_view.py :: PageCorrectionViewSet :: page_correction")
        
        serializer = PageCorrectionSerializer(data=request.data)
        if not serializer.is_valid():
            
            errors = serializer.errors
            error_messages = get_error_messages(errors)
            raise CustomException({"message" : error_messages[0]}, status_code=status.HTTP_400_BAD_REQUEST)
             
        data = serializer.validated_data
        file_uuid = data.get('file_uuid')
        error_uuid = data.get('error_uuid')
        page = data.get('page')
        blocks = data.get('blocks')

        self._page_service.page_correction(str(file_uuid), str(error_uuid), page, blocks)

        return CustomResponse(SuccessMessages.PAGE_CORRECTION_SUCCESS)