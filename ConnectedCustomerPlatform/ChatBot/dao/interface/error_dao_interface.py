from abc import ABC, abstractmethod


class ErrorCorrectionDaoInterface(ABC):
    
    @abstractmethod
    def get_filedetails_by_fileuuid(self, file_uuid):
        pass
    
    @abstractmethod
    def update_error_status(self, error_uuid, error_status):
        pass
    
    @abstractmethod
    def get_collections_by_customer_application(self, customer, applicatiton):
        pass
    
    @abstractmethod
    def update_knowledge_source_status(self, knowledge_source_uuid, status):
        pass
    
    @abstractmethod
    def add_media(self, id, name, path, details, source_uuid, customer_uuid, application_uuid):
        pass

    @abstractmethod
    def delete_errors_of_knowledge_source(self,knowledge_source_uuid):
        """
        Deletes all errors associated with the specified knowledge source UUID.
        
        Args:
            knowledge_source_uuid (str): UUID of the knowledge source.
        """

    @abstractmethod
    def get_errors_with_knowledge_source_uuid(self,filters):
        """
        Retrieves knowledge source errors associated with a knowledge source uuid and error type in filters.
        """ 

    @abstractmethod
    def knowledge_source_errors_count(self, knowledge_source_uuid: str) -> int:
        
        """
        returns knowledge source errors count
        """    
    @abstractmethod
    def has_unresolved_errors(self,knowledge_source_uuid):
        pass    

    @abstractmethod
    def create_error_data(self, error_uuid, error_type, error_status, knowledge_source_uuid, application_uuid, customer_uuid):
        """ creates a error record """