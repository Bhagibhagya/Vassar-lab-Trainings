from abc import ABC, abstractmethod
from ChatBot.dataclasses.entity_data import Entity


class IEntityDao(ABC):
    @abstractmethod
    def create_entity(self, entity: Entity, user_uuid):
        """Create a new entity in the database.

        Args:
            entity (Entity): The entity to be created.
            user_uuid (str): The UUID of the user creating the entity.
        """

    @abstractmethod
    def create_default_entity(self, customer_uuid, application_uuid, user_uuid):
        """Create a new entity in the database.
        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.
            user_uuid (str): the uuid of the user

        Returns:
            Entity: The default entity.
        """

    @abstractmethod
    def delete_entity(self, entity_uuid):
        """Delete an entity and its related data from the database.

        Args:
            entity_uuid (str): The UUID of the entity to delete.
        """

    @abstractmethod
    def get_entity(self, entity_uuid):
        """Retrieve an entity by its UUID.

        Args:
            entity_uuid (str): The UUID of the entity.

        Returns:
            dict: The entity details if found, otherwise None.
        """

    @abstractmethod
    def update_entity(self, entity: Entity, user_uuid):
        """Update an existing entity in the database.

        Args:
            entity (Entity): The entity with updated information.
            user_uuid (str): The UUID of the user updating the entity.
        """

    @abstractmethod
    def get_or_create_default_entity(self, customer_uuid, application_uuid, user_uuid):
        """Retrieve or create the default entity for a customer and application.

        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.
            user_uuid (str): the uuid of the user

        Returns:
            Entity: The default entity.
        """

    @abstractmethod
    def get_entities_by_customer_uuid_and_application_uuid(self, customer_uuid, application_uuid,params):
        """Retrieve entities based on customer and application UUIDs, with pagination.

        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            list: A list of entities.
        """

    @abstractmethod
    def create_test_entity(self, customer_uuid, application_uuid):
        """Create a test entity for a specific customer and application.

        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.

        Returns:
            Entity: The created test entity.
        """
