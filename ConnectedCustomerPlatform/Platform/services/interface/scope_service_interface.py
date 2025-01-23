from abc import ABC, abstractmethod


class IScopeService(ABC):
    @abstractmethod
    def get_scope_type_values(self, customer_uuid, application_uuid, scope_type):
        """
        Retrieve scope type values for a given customer and application.

        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param scope_type: The scope type to retrieve values for.
        :return: List of values corresponding to the provided scope type.
        """
