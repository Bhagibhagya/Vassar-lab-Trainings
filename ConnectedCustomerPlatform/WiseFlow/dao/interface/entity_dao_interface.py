from abc import abstractmethod, ABC


class IEntityDaoInterface(ABC):
    @abstractmethod
    def get_entity_details(self,entity_uuid:str):
        """Fetches ownership of entity (system or custom)"""
        pass

    @abstractmethod
    def create_wiseflow_entity(self, entity_uuid, entity_name, description, parent_entity_uuid, output_format, instructions, ownership, application_uuid, customer_uuid, user_uuid):
        """ create an entity """

    @abstractmethod
    def get_wiseflow_entities_by_customer_and_application(self, customer_uuid, application_uuid, ownership):
        """ fetches wiseflow entities based customer and application """

    @abstractmethod
    def get_entity_by_entity_uuid(self, entity_uuid):
        """ fetch a particular entity """
    @abstractmethod
    def delete_entity_by_customer_and_application(self, customer_uuid, application_uuid, entity_uuid):
        """ deletes an entity """

    @abstractmethod
    def is_system_entity(self, entity_uuid):
        """check whether a entity is system entity or not"""

    @abstractmethod
    def get_entity_by_uuid(self, entity_uuid):
        """ get an entity by entity_uuid"""

    @abstractmethod
    def save_entity(self, entity_instance):
        """update the entity"""

    @abstractmethod
    def fetch_parent_entities(self, ownership):
        """ fetch parent entities by ownership """
    @abstractmethod
    def is_valid_parent_entity(self, entity_uuid):
        """ check whether entity is parent entity or not """
