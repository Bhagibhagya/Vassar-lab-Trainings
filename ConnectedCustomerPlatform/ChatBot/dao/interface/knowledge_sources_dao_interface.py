from abc import ABC, abstractmethod

class IKnowledgeSourcesDao(ABC):

    @abstractmethod
    def update_entity_attributes_by_entity_uuid(self, prev_entity_uuid, entity_uuid, attribute_details_json, user_uuid):
        pass

    @abstractmethod
    def update_entity_attributes(self, knowledge_source_uuid, prev_entity_uuid, entity_uuid,attribute_details_json, user_uuid):
        pass

    @abstractmethod
    def create_test_knowledge_source(self, entity_uuid, customer_uuid, application_uuid, user_uuid):
        pass

    @abstractmethod
    def get_knowledge_attribute_details_by_entity_uuid(self, entity_uuid):
        pass

    @abstractmethod
    def update_qa_generation_status(self, knowledge_source_uuids, user_uuid, entity_uuids_list):
        pass

    @abstractmethod
    def get_knowledge_sources_by_entity_uuid(self, entity_uuid, customer_uuid, application_uuid):
        """Retrieve knowledge source by  entities based on customer and application UUIDs, with pagination."""
        pass

    @abstractmethod
    def create_knowledge_source(self,knowledge_source_uuid, knowledge_source_name, application_uuid, 
                                knowledge_source_type, status, user_uuid, customer_uuid, 
                                entity_uuid, attribute_details_json,reason_for_failure,is_i3s_enabled):
        """
        Abstract method to create a KnowledgeSource record.
        """

    @abstractmethod
    def get_knowledge_source_with_uuid(self, knowledge_source_uuid) -> dict:
        """
        Retrieves specific fields of a KnowledgeSource by UUID.
        Logs an error and raises an exception if the KnowledgeSource is not found.
        """ 

    @abstractmethod
    def update_knowledge_source_details(self,knowledge_source_uuid,knowledge_source_name,knowledge_source_type,status,metadata,user_uuid,customer_uuid,application_uuid):
       """
        Implementation of the abstract method to update a KnowledgeSource record.
        """       
       
    @abstractmethod
    def update_knowledge_source_path(self,knowledge_source_uuid,knowledge_source_path):
       """
        Implementation of the abstract method to update a KnowledgeSource Path.
        """
    
    @abstractmethod 
    def get_knowledge_sources_by_customer_and_application_ids(self, customer_uuid, application_uuid,filters):
        """Retrieve knowledge_sources based on customer and application UUIDs and filters."""   
   
    @abstractmethod 
    def check_knowledge_sources_exists(self,knowledge_source_names,knowledge_source_uuid, customer_uuid, application_uuid):
        """
        Checks if specified knowledge source files exist in the database for a given user, 
        customer, and application UUID, returning a list of matching file names or IDs
        """     

    @abstractmethod
    def delete_knowledge_source_by_uuid(self,knowledge_source_uuid):
        """
        deletes knowledge source based on knowledge_source_uuid
        """

    @abstractmethod
    def get_video_type_knowledge_sources_by_customer_and_application(self, customer_uuid, application_uuid):
        pass

    @abstractmethod
    def get_metadata(self, knowledge_source_uuid: str) -> dict:
        
        """
        Fetch the metadata of the knowledge source.
        Args:
            knowledge_source_uuid (_type_): UUID of knowledge source
        Returns:
            metadata of the knowledge source: dict
        Raises:
            ResourceNotFoundException: When there is no knowledge source with given uuid.
        """
        pass

    @abstractmethod
    def update_metadata(self, knowledge_source_uuid: str, metadata: dict) -> None:
        """
        Update the knowledge source metadata.

        Args:
            knowledge_source_uuid (str): UUID of the knowledge source
            metadata (dict): the knowledge source metadata to be updated with
        """
        pass
    
    @abstractmethod
    def get_reviewed_knowledge_sources_by_customer_and_application(self, customer_uuid: str, application_uuid: str) -> list[dict]:
        
        """ 
        Fetch the knwoledge sources which are reviwed but not qa generated.
        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            knwoledge source uuids and names which are reviwed but not qa generated.
        """
        pass
    
    @abstractmethod
    def get_qa_generated_knowledge_sources_with_json_edited(self, customer_uuid: str, application_uuid: str) -> list[dict]:
        
        """ 
        Fetch the knwoledge sources which are qa generated but not json has been edited.
        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            knwoledge source uuids and names which are qa generated, but json has been edited.
        """
        pass
    
    @abstractmethod
    def update_qa_status(self, knowledge_source_uuid: str, qa_status: bool) -> None:
        
        """
        Update the knowledge source qa status

        Args:
            knowledge_source_uuid (str): UUID of the knowledge source
            qa_status (bool): the boolean values the field has to be updated to
        """
        pass