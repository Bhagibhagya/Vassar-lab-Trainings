from abc import ABC, abstractmethod

class IEmailServerCAMDao(ABC):
    """Interface for EmailServerCustomerApplicationMapping model."""

    @abstractmethod
    def bulk_create_server_mappings(self, email_server_mappings):
        """
            Creates multiple email server entries in the database.

            :param email_server_mappings: The email server data.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_mapped_servers(self, customer_uuid, application_uuid, mapped_server_uuids):
        """
            Retrieves mapped email servers for the given customer and application.

            :param customer_uuid: UUID of the customer.
            :param application_uuid: UUID of the application.
            :param mapped_server_uuids: List of UUIDs to fetch from the query.
            :return: Queryset of mapped email servers.
        """

    @abstractmethod
    def get_mapped_servers_with_join(self, customer_uuid, application_uuid):
        """
            Retrieves mapped email servers for the given customer and application with a join on the email server table.

            :param customer_uuid: UUID of the customer.
            :param application_uuid: UUID of the application.
            :return: Queryset of mapped email servers with joined email server details.
        """

    @abstractmethod
    def bulk_update_server_mappings(self, updated_servers):
        """
            Updates existing email server entries in the database.

            :param updated_servers: List of email server objects with updated values.
            :return: Successful response or error message.
        """

    @abstractmethod
    def get_mapped_servers_for_outlook(self, customer_uuid, application_uuid):
        """ Get mapped outlook server for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns Email Server CAM object
        """

    @abstractmethod
    def create_email_server_mapping(self, default_outlook_server, mapping_uuid, email_server_data, application_uuid,
                                    customer_uuid, user_uuid):
        """ Create new email server mapping directly with parameters
        :param email_server_data: dict containing sync_time_interval,microsoft_client_id,microsoft_tenant_id
        :param : default_outlook_server: default email server object
        :param : mapping_uuid: uuid of the new record
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param user_uuid: UUID of logged in user
        """

    @abstractmethod
    def update_email_server_mapping(self, mapping_uuid, email_server_data, application_uuid, customer_uuid, user_uuid):
        """ Update sync_time_interval,microsoft_client_id,microsoft_tenant_id of existing email server mapping directly with parameters
        :param email_server_data: dict containing sync_time_interval,microsoft_client_id,microsoft_tenant_id
        :param : mapping_uuid: uuid of the new record
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.
        :param user_uuid: UUID of logged in user
        """


    @abstractmethod
    def delete_all_mapped_email_server(self, customer_uuid, application_uuid):
        """
        Deletes all the mapped email servers for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Raises exception if any exception occurred
        """

    @abstractmethod
    def get_server_provider_name(self, customer_uuid, application_uuid):
        """ Fetch provider name for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns provider name, None if the customer and application not mapped
        """

    @abstractmethod
    def get_outlook_server_details(self,customer_uuid,application_uuid):
        """
        Fetches outlook server details for the customer and application
        :param customer_uuid: UUID of the customer.
        :param application_uuid: UUID of the application.

        Returns only mapping uuid,microsoft_client_id,microsoft_tenant_id as a tuple"""

