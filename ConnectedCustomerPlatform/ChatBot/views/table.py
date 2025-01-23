from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse

from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.error_messages import ErrorMessages

from ChatBot.serializers import ProcessCSVSerializer, UpdateTableSerializer, get_error_messages

from ChatBot.services.impl.table_service_impl import TableCorrectionServiceImpl
from ChatBot.services.interface.table_service_interface import TableCorrectionServiceInterface

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, JSONParser
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class TableCorrectionViewSet(ViewSet):

    """
    TableCorrectionViewSet:
    
    APIs
    
    1.get_table : API to fetch the table data of table in the internal json of a file
    2.get_table_from_csvfile : API to get the table data of an uploaded csv or excel file 
    3.update_table : API to update the table data of a tbale of the internal json of a file
    """
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self._table_service : TableCorrectionServiceInterface = TableCorrectionServiceImpl()

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="file_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING),
                           openapi.Parameter(name="table_id", in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['get'])
    def get_table(self, request, file_uuid, table_id):
        
        """
        Retrieves table information based on the provided file_uuid and table_id.

        Parameters:
            - request: HTTP request object
            - file_uuid: ID of the file containing the table
            - table_id: ID of the specific table within the file
        """  
        logger.info("In table_view.py :: TableCorrectionViewSet :: get_table") 
        
        columns, matrix, image_url = self._table_service.get_table(file_uuid, table_id)    
        
        response = {
            "message": SuccessMessages.TABLE_RETRIEVAL_SUCCESS,
            "table_image_url": image_url,
            "columns": columns,
            "matrix": matrix
        }
        return CustomResponse(response)

    @swagger_auto_schema(
        request_body=ProcessCSVSerializer,
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['post'])
    def get_table_from_csvfile(self, request):
        
        """
        Processes a CSV or XLSX file uploaded via request data.

        Parameters:
            - request: HTTP request object containing the uploaded file
        """
        logger.info("In table_view.py :: TableCorrectionViewSet :: get_table_from_csvfile")

        serializer = ProcessCSVSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        file = data.get('csvfile')

        columns, matrix = self._table_service.get_table_from_file(file)

        response = {
            "message": "csv file processed successfully",
            "matrix": matrix,
            "columns": columns
        }
        return CustomResponse(response)

    @swagger_auto_schema(
        request_body=UpdateTableSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.TABLE_UPDATE_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['put'])
    def update_table(self, request):
        
        """
        Updates a table identified by file_uuid and table_id with new columns and matrix data.

        Parameters:
            - request: HTTP request object containing serialized update data
        """
        logger.info("In table_view.py :: TableCorrectionViewSet :: update_table")

        serializer = UpdateTableSerializer(data=request.data)
        if not serializer.is_valid():
            
            errors  = serializer.errors
            error_messages = get_error_messages(errors)
            raise CustomException({"message" : error_messages[0]}, status_code=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        file_uuid = data.get('file_uuid')
        error_uuid = data.get('error_uuid')
        table_id = data.get('table_id')
        columns = data.get('columns')
        matrix = data.get('matrix')
        
        self._table_service.update_table(str(file_uuid), str(error_uuid), table_id, columns, matrix)

        return CustomResponse(SuccessMessages.TABLE_UPDATE_SUCCESS)