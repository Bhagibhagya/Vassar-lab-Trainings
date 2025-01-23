from abc import ABC, abstractmethod


class HeaderCorrectionServiceInterface(ABC):
    
    @abstractmethod
    def get_h1_headings(self, file_uuid):
        pass
    
    @abstractmethod
    def get_child_blocks(self, file_uuid, block_id):
        pass
    
    @abstractmethod
    def insert_text_block(self, file_uuid, text_type, content, prev_id):
        pass
    
    @abstractmethod
    def delete_block(self, file_uuid, block_id):
        pass
    
    @abstractmethod
    def update_headers(self, file_uuid, error_uuid, blocks):
        pass