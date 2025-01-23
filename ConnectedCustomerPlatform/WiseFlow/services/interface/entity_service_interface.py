from abc import abstractmethod, ABC


class IEntityInterface(ABC):
    @abstractmethod
    def add_entity_examples(self, customer_uuid: str, application_uuid: str, validated_payload: dict):
        pass

    @abstractmethod
    def create_wiseflow_entity(self, customer_uuid, application_uuid, user_uuid, data):
        """ method to create a custom entity"""

    @abstractmethod
    def get_wiseflow_entities(self, customer_uuid, application_uuid, validated_data):
        """fetches all wiseflow entities under customer and application"""

    @abstractmethod
    def get_entity_by_entity_uuid(self, entity_uuid, customer_uuid, application_uuid):
        """fetch a particular entity under customer and application"""

    @abstractmethod
    def delete_wiseflow_entity(self, customer_uuid, application_uuid, entity_uuid):
        """deletes a particular entity under customer and application"""

    @abstractmethod
    def update_entity(self, customer_uuid, application_uuid, validated_data):
        """update a particular entity under customer and application"""

    @abstractmethod
    def get_parent_entities(self):
        """fetches parent entities"""