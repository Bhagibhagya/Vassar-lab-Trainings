from abc import ABC, abstractmethod

class IEmailServerDao(ABC):
    """Interface for EmailServer model."""
    @abstractmethod
    def get_default_email_servers_by_ids(self, email_server_uuids):
        """
            Retrieves a list of email servers based on their UUIDs.

            :param email_server_uuids: List of UUIDs of the email servers to retrieve.
            :return: A Django QuerySet containing email server instances that match the provided UUIDs.
        """

    @abstractmethod
    def get_default_email_servers_by_ids_excluded(self, email_server_uuids):
        """
            Retrieves email servers excluding those with the specified UUIDs.

            :param email_server_uuids: List of UUIDs to exclude from the query.
            :return: Queryset of email servers excluding the specified UUIDs.
        """

    @abstractmethod
    def get_default_msal_server(self):
        """ Returns default msal server object"""