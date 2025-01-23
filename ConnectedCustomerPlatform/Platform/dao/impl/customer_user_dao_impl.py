import inspect
import logging

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import ClientUser
from datetime import datetime
from django.db import IntegrityError, connection

from Platform.constant.error_messages import ErrorMessages
from Platform.dao.interface.customer_user_dao_interface import ICustomerUserDao
from rest_framework import status
from django.utils import timezone



logger = logging.getLogger(__name__)
class CustomerUserDaoImpl(ICustomerUserDao):
    """
        Dao for managing ClientUsers, providing methods to add, edit,
        delete, and retrieve.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(CustomerUserDaoImpl, cls).__new__(cls)
            logger.info("Creating a new instance of CustomerUserDaoImpl")
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the CustomerUserDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):
            super().__init__(**kwargs)
            logger.info(f"Inside CustomerUserDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def save_customer_user(self, customer_user):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            Saves customer user object in the database.
            :param customer_user: The customer user instance object to be created.
            :return: can raise an exception.
        """
        try :
            customer_user.save()
        except IntegrityError as e:
            if  'client_user_first_name_last_name_key' in str(e):
                logger.error(f"Duplicate name found for: {customer_user.first_name,customer_user.last_name}")
                raise CustomException(ErrorMessages.CUSTOMER_USER_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
            elif  'client_user_email_id_key' in str(e):
                logger.error(f"Duplicate email found for: {customer_user.email_id} ")
                raise CustomException(ErrorMessages.CUSTOMER_USER_EMAIL_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
            elif 'client_user_customer_client_uuid_fkey' in str(e) or 'client_user_geography_uuid_fkey' in str(e):
                logger.error("Customer client not found")
                raise CustomException(ErrorMessages.FAILED_TO_CREATE_CUSTOMER_USER, status_code=status.HTTP_400_BAD_REQUEST)

            else:
                raise e

    # Updates the customer client user in the database
    def update_customer_user(self,client_user_uuid,first_name,last_name,email_id,user_info_json_dict,customer_client_uuid,geography_uuid,user_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            Updates the  customer client user object in the database.
            :return: No of rows updated
        """
        try :
            updated_rows = ClientUser.objects.filter(client_user_uuid=client_user_uuid,is_deleted=False).update(
                first_name=first_name,
                last_name=last_name,
                email_id=email_id,
                user_info_json=user_info_json_dict,
                customer_client_uuid=customer_client_uuid,
                geography_uuid=geography_uuid,updated_ts=timezone.now(), updated_by=user_uuid
            )
            return updated_rows
        except IntegrityError as e:
            if  'client_user_first_name_last_name_key' in str(e):
                logger.error(f"Duplicate name found for: {first_name,last_name}")
                raise CustomException(ErrorMessages.CUSTOMER_USER_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
            elif  'client_user_email_id_key' in str(e):
                logger.error(f"Duplicate email found for: {email_id} ")
                raise CustomException(ErrorMessages.CUSTOMER_USER_EMAIL_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
            elif 'client_user_customer_client_uuid_fkey' in str(e) or 'client_user_geography_uuid_fkey' in str(e):
                logger.error("Customer client not found")
                raise CustomException(ErrorMessages.FAILED_TO_CREATE_CUSTOMER_USER, status_code=status.HTTP_400_BAD_REQUEST)

            else:
                raise e

    def delete_customer_user_by_id(self, client_user_uuid, user_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Start")

        """
            Marks the customer user as deleted by updating the is_deleted flag and timestamps.

            Parameters:
                - customer_user_uuid: The unique identifier of the customer user to delete.
                - user_id: The unique identifier of the user performing the delete operation.

            Returns:
                - Number of rows updated (i.e., customers marked as deleted).
        """

        # Perform the delete operation by marking the customer client as deleted
        updated_rows = ClientUser.objects.filter(
            client_user_uuid=client_user_uuid,
            is_deleted=False
        ).update(
            is_deleted=True,
            updated_ts=datetime.now(),
            updated_by=user_uuid
        )

        # Log the result of the update operation
        logger.info(f"delete_customer_user_by_id :: Rows updated: {updated_rows}")

        # Return the number of rows updated
        return updated_rows

    def get_customer_users_by_customer_client_uuid(self, customer_client_uuid, customer_uuid):
        """
        Fetches customer users based on the provided customer_client_uuid.

        Args:
            customer_client_uuid (str): The UUID of the customer_client. If not provided, fetches all customer_users who are not deleted.
            :param customer_client_uuid:
            :param customer_uuid:

        Returns:
            QuerySet: A queryset of customer users with the relevant geography and application data pre-fetched.
        """

        # Raw SQL query to fetch customer clients based on customer_uuid
        query = """
                    SELECT * FROM
                    (    SELECT DISTINCT ON (cu.client_user_uuid)
                            cu.*, 
                            CASE 
                                WHEN dcam.parent_dimension_uuid IS NOT NULL THEN d.dimension_name 
                                ELSE NULL 
                            END AS state,
                            COALESCE(pd.dimension_name, d.dimension_name) AS country,
                            cc.customer_client_name,
                            CONCAT(cu.first_name, ' ', cu.last_name) AS username,
                            cu.user_info_json::json AS user_info_json
                        FROM client_user cu
                        LEFT JOIN dimension_customer_application_mapping dcam 
                            ON cu.geography_uuid = dcam.dimension_uuid AND dcam.customer_uuid = %s
                        LEFT JOIN dimension d 
                            ON d.dimension_uuid = dcam.dimension_uuid
                        LEFT JOIN dimension pd 
                            ON pd.dimension_uuid = dcam.parent_dimension_uuid
                        LEFT JOIN customer_client cc 
                            ON cc.customer_client_uuid = cu.customer_client_uuid
                        WHERE cu.customer_client_uuid = %s AND cu.is_deleted = false  
                        ORDER BY cu.client_user_uuid, cu.updated_ts DESC
                        ) subquery 
                        ORDER BY updated_ts DESC
                    """

        with connection.cursor() as cursor:
            cursor.execute(query, [customer_uuid, customer_client_uuid])
            columns = [col[0] for col in cursor.description]  # Get column names
            customer_users = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Format results as a list of dictionaries

        return customer_users

