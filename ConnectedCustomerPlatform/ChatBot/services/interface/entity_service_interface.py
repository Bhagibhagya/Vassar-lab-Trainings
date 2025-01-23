from abc import ABC, abstractmethod

class IEntityService(ABC):
    """
    Interface defining the contract for Entity Service implementations.
    Each method is abstract and should be implemented by a subclass.
    """

    @abstractmethod
    def add_entity(self, entity, customer_uuid, application_uuid, user_uuid):
        """
        Adds a new entity to the system.

        Args:
            entity (dict): Dictionary containing entity details.
            customer_uuid (UUID): The UUID of the customer.
            application_uuid (UUID): The UUID of the application.
            user_uuid (UUID): The UUID of the user performing the operation.

        Raises:
            CustomException: If the entity cannot be added.
        """


    @abstractmethod
    def delete_entity(self, entity_uuid, customer_uuid, application_uuid, user_uuid):
        """
        Deletes an existing entity from the system.

        Args:
            entity_uuid (UUID): The UUID of the entity to delete.
            customer_uuid (UUID): The UUID of the customer.
            application_uuid (UUID): The UUID of the application.
            user_uuid (UUID): The UUID of the user.

        Raises:
            ResourceNotFoundException: If the entity is not found.
        """


    @abstractmethod
    def update_entity(self, entity, customer_uuid, application_uuid, user_uuid):
        """
        Updates an existing entity in the system.

        Args:
            entity (dict): Dictionary containing updated entity details.
            customer_uuid (UUID): The UUID of the customer.
            application_uuid (UUID): The UUID of the application.
            user_uuid (UUID): The UUID of the user performing the operation.

        Raises:
            ResourceNotFoundException: If the entity is not found.
        """

    @abstractmethod
    def get_entity_details(self, entity_uuid):
        """
        Retrieves entities associated with a specific customer and application.

        Args:
            entity_uuid (UUID): The UUID of the entity.

        Returns:
            dict: entity with given entity_uuid
        """

    @abstractmethod
    def get_entities_by_customer_and_application(self, customer_uuid, application_uuid, user_uuid, params):
        """
        Retrieves entities associated with a specific customer and application.

        Args:
            customer_uuid (UUID): The UUID of the customer.
            application_uuid (UUID): The UUID of the application.
            user_uuid (UUID): The UUID of the user.
            params: page nation params

        Returns:
            dict: Contains the list of entities and the total entity count.
        """

    @abstractmethod
    def update_knowledge_source_entity_assignment(self, data, customer_uuid, application_uuid, user_uuid):
        """
        Assigns or unassigns an entity of a knowledge source based on the provided data.
        If unassigning, it reassigns the default entity to the knowledge source.
        
        Args:
            data (dict): Contains knowledge source and entity details.
            customer_uuid (str): The customer UUID.
            application_uuid (str): The application UUID.
            user_uuid (str): The user UUID who is making the request.
        """
