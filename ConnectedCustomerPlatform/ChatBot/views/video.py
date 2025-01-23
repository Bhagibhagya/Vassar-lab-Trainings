from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.constant.constants import KnowledgeSourceConstants

from ChatBot.serializers import VideoTranscriptionSerializer,get_error_messages

from ChatBot.services.impl.video_service_impl import VideoCorrectionServiceImpl
from ChatBot.services.interface.video_service_interface import VideoCorrectionServiceInterface

from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class VideoCorrectionViewSet(ViewSet):
    
    """
    VideoCorrectionViewSet:
    
    APIs:
    
    1.get_video_transcription : API to fetch the transcription blocks of the internal json of a video
    1.update_video_transcription : API to update the transcription blocks of the internal json of a video
    """
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self._video_service : VideoCorrectionServiceInterface = VideoCorrectionServiceImpl()

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="file_uuid", in_=openapi.IN_PATH, type=openapi.TYPE_STRING)],
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=["get"])
    def get_video_transcription(self, request, file_uuid):
        
        """
        Retrieves video transcription information based on the provided file_uuid.

        Parameters:
            - request: HTTP request object
            - file_uuid: ID of the video file to retrieve transcription for
        """
        logger.info("In video_transcript_view.py :: VideoCorrectionViewSet :: get_video_transcription")

        blocks, video_path,knowledge_source_name = self._video_service.get_video_transcription(file_uuid)

        response = {
            'message': "fetched video transcription successfully",
            'knowledge_source_name':knowledge_source_name,
            'video_path': video_path,
            'transcription': blocks
        }

        return CustomResponse(response)

    @swagger_auto_schema(
        request_body=VideoTranscriptionSerializer,
        responses={
            status.HTTP_200_OK: SuccessMessages.VIDEO_TRANSCRIPTION_UPDATE_SUCCESS,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST,
        }
    )
    @action(detail=False, methods=['post'])
    def update_video_transcription(self, request):
        
        """
        Updates the transcription blocks of a video identified by file_uuid.

        Parameters:
            - request: HTTP request object containing serialized video transcription data
        """
        logger.info("In video_transcript_view.py :: VideoCorrectionViewSet :: update_video_transcription")
        
        serializer = VideoTranscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            error_messages = get_error_messages(serializer.errors)
            raise CustomException({"message" : error_messages[0]}, status_code=status.HTTP_400_BAD_REQUEST)
                     
        data = serializer.validated_data
        file_uuid = data.get('file_uuid')
        error_uuid = data.get('error_uuid')
        transcription = data.get('transcription')
        
        self._video_service.update_video_transcription(str(file_uuid), str(error_uuid), transcription)

        return CustomResponse(SuccessMessages.VIDEO_TRANSCRIPTION_UPDATE_SUCCESS)