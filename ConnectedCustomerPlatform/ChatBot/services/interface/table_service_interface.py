from abc import ABC, abstractmethod


class TableCorrectionServiceInterface(ABC):
    
    @abstractmethod
    def get_table(self, file_uuid, table_id):
        pass
    
    @abstractmethod
    def get_table_from_file(self, binary_file):
        pass
    
    @abstractmethod
    def update_table(self, file_uuid, error_uuid, table_id, columns, matrix):
        pass