from abc import ABC, abstractmethod


class PageCorrectionServiceInterface(ABC):
    
    @abstractmethod
    def get_page_blocks(self, file_uuid, page_number):
        pass
    
    @abstractmethod
    def page_correction(self, file_uuid, error_uuid, page_number, blocks):
        pass