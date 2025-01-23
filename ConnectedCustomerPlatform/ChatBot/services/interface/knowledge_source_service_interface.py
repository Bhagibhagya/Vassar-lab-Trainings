from abc import ABC, abstractmethod


class IKnowledgeSource(ABC):

    @abstractmethod
    def get_knowledge_sources_for_question_and_answer(self, customer_uuid, application_uuid):
        pass

    @abstractmethod
    def get_video_type_knowledge_sources_in_application(self, customer_uuid, application_uuid):
        pass

    @abstractmethod
    def get_knowledge_source_internal_json(self,knowledge_source_uuid):
        pass


    @abstractmethod
    def add_knowledge_sources_in_application(self, data, user_uuid, customer_uuid, application_uuid):
        """
        Retrieves and adds knowledge sources to an application.

        Args:
            data (dict): Contains 'files' (list of file objects) and an optional 'web_url'.
            user_uuid : User's UUID.
            customer_uuid : Customer's UUID.
            application_uuid : Application's UUID.

        Raises:
            CustomException: For file size limits, invalid URLs, or duplicate entries.
        """

    @abstractmethod
    def upload_image_to_azure(self,data, customer_uuid, application_uuid):
        """
        Uploads image files from `data` to Azure Blob Storage, associating them with the specified `customer_uuid` and `application_uuid`.
        
        Parameters:
        - data (dict): Contains file objects in the 'files' key.
        - customer_uuid , application_uuid : Identifiers for customer and application.
        """

    @abstractmethod
    def upload_files_via_drives(self,data, user_uuid, customer_uuid, application_uuid):
        """
        Uploads files from multiple drive sources (e.g., Google Drive, OneDrive) and associates them with a specified user, customer, and application.

        Parameters:
        - data (dict): Contains drive file metadata, such as file IDs and access tokens.
        - user_uuid , customer_uuid , application_uuid : Identifiers for user, customer, and application.
        """


    @abstractmethod
    def resolve_knowledge_source(self, knowledge_source_uuid: str, customer_uuid: str, application_uuid: str) -> None:
        """
        Resolves a knowledge source entry by its unique identifier, `knowledge_source_uuid`.

        Parameters:
        - knowledge_source_uuid : The UUID of the knowledge source to be resolved.
        - customer_uuid, application_uuid : Identifiers for customer, and application.
        """
        pass

    @abstractmethod
    def reupload_knowledge_source(self,data, user_uuid, customer_uuid, application_uuid):
        """
        Reuploads a knowledge source entry by its unique identifier, `knowledge_source_uuid`.

        Parameters:
        - data : It contains the UUID of the knowledge source to be resolved.
        - user_uuid , customer_uuid , application_uuid : Identifiers for user, customer, and application.

        """


    @abstractmethod
    def get_knowledge_sources_by_customer_and_application_ids(self, customer_uuid, application_uuid, params):
        """
        Retrieves knowledge sources associated with a specific customer and application.

        Args:
            customer_uuid (UUID): The UUID of the customer.
            application_uuid (UUID): The UUID of the application.
            user_uuid (UUID): The UUID of the user.
            params: page nation params

        Returns:
            dict: Contains the list of knowledge sources and the total knowledge sources count.
        """    

    @abstractmethod
    def get_knowledge_sources_errors(self, params):
        """
        Retrieves knowledge source errors associated with a knowledge source uuid.

        Args:
            params: page nation params and knowledge_source_uuid

        Returns:
            dict: Contains the list of errors and the total error count related to knowledge source.
        """    
    @abstractmethod
    def check_knowledge_sources_exists(self,data, customer_uuid, application_uuid):
        """
        Checks if specified knowledge source files exist in the database for a given user, 
        customer, and application UUID, returning a list of matching file names or IDs.
        """
       
    @abstractmethod
    def delete_knowledge_source_by_uuid(self,knowledge_source_uuid, customer_uuid, application_uuid):
        """
        deletes knowledge source based on knowledge_source_uuid
        """


    @abstractmethod
    def get_knowledge_source_by_knowledge_source_uuid(self, knowledge_source_uuid):
        """
        retrieves knowledge source info based on knowledge_source_uuid
        """

    @abstractmethod
    def generate_formatted_json_from_internal_json(self, knowledge_source_uuid, page_number):
        """
            generate a formatted json from internal_json so that user can edit fields
        """
    @abstractmethod
    def update_knowledge_source_internal_json(self, knowledge_source_uuid, pages):
        """
            updates internal_json for a particular knowledge_source
        """

    @abstractmethod
    def editable_internal_json(self, knowledge_source_uuid, request_blocks):
        """
           making internal_json as editable
        """