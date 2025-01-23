from abc import ABC, abstractmethod


class VideoCorrectionServiceInterface(ABC):
    
    @abstractmethod
    def get_video_transcription(self, file_uuid):
        pass
    
    @abstractmethod
    def update_video_transcription(self, file_uuid, error_uuid, transcription):
        pass