import inspect
import logging
from datetime import datetime

from django.db import  connection
from Platform.dao.interface.customer_client_dao_interface import ICustomerClientDao
from DatabaseApp.models import CustomerClient,CustomerClientTierMapping
logger = logging.getLogger(__name__)
class CustomerClientDaoImpl(ICustomerClientDao):

    def save_customer_client(self, customer_client):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            Saves customer client object in the database.
            :param customer_client: The customer client instance object to be created.
            :return: can raise an exception.
        """
        customer_client.save()

    def delete_customer_client_by_customer_client_id(self, customer_client_uuid, user_id):
        """
            Marks the customer client as deleted by updating the is_deleted flag and timestamps.

            Parameters:
                - customer_client_uuid: The unique identifier of the customer client to delete.
                - user_id: The unique identifier of the user performing the delete operation.

            Returns:
                - Number of rows updated (i.e., customers marked as deleted).
        """

        # Log the start of the delete operation
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Start")
        logger.info(f"delete_customer_client_by_customer_client_id :: Marking customer client with UUID: {customer_client_uuid} as deleted by user: {user_id}")

        # Perform the delete operation by marking the customer client as deleted
        updated_rows = CustomerClient.objects.filter(
            customer_client_uuid=customer_client_uuid,
            is_deleted=False
        ).update(
            is_deleted=True,
            updated_ts=datetime.now(),
            updated_by=user_id
        )

        #deleting the customer_client_tier_mapping for the particular customer_client_uuid
        CustomerClientTierMapping.objects.filter(
            customer_client_uuid=customer_client_uuid
        ).delete()

        # Log the result of the update operation
        logger.info(f"delete_customer_client_by_customer_client_id :: Rows updated: {updated_rows}")

        # Return the number of rows updated
        return updated_rows

    #get_customer_client_by_customer_client_uuid
    def get_customer_client_by_customer_client_uuid(self,customer_client_uuid):
        return CustomerClient.objects.filter(customer_client_uuid=customer_client_uuid).first()

    def get_customers_by_customer_uuid(self, customer_uuid):
        """
        Fetches customer clients based on the provided customer UUID.

        Args:
            customer_uuid (str): The UUID of the customer. If not provided, fetches all customers who are not deleted.

        Returns:
            QuerySet: A queryset of customer clients with the relevant geography and application data pre-fetched.
        """

        # Raw SQL query to fetch customer clients based on customer_uuid
        query = """
                SELECT * FROM 
                (SELECT DISTINCT ON (cc.customer_client_uuid)
                    cc.*, 
                    CASE 
                        WHEN dcam.parent_dimension_uuid IS NOT NULL THEN d.dimension_name 
                        ELSE NULL 
                    END AS state,
                    COALESCE(pd.dimension_name, d.dimension_name) AS country
                FROM customer_client cc
                LEFT JOIN dimension_customer_application_mapping dcam 
                    ON cc.customer_client_geography_uuid = dcam.dimension_uuid AND dcam.customer_uuid = %s
                LEFT JOIN dimension d 
                    ON d.dimension_uuid = dcam.dimension_uuid
                LEFT JOIN dimension pd 
                    ON pd.dimension_uuid = dcam.parent_dimension_uuid
                WHERE cc.customer_uuid = %s AND cc.is_deleted = false
                ORDER BY cc.customer_client_uuid, cc.updated_ts DESC
                ) subquery 
                ORDER BY updated_ts DESC 
            """

        with connection.cursor() as cursor:
            cursor.execute(query, [customer_uuid, customer_uuid])
            columns = [col[0] for col in cursor.description]  # Get column names
            customer_clients = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Format results as a list of dictionaries

        return customer_clients




