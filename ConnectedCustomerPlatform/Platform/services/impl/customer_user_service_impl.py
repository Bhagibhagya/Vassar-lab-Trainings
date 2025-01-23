import inspect
import logging
import uuid
from dataclasses import asdict
from datetime import datetime

from Platform.dao.impl.customer_user_dao_impl import CustomerUserDaoImpl
from Platform.dataclass import ClientUserInfoJson
from DatabaseApp.models import ClientUser
from django.db import IntegrityError
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from rest_framework import status
from DatabaseApp.models import CustomerClient
from DatabaseApp.models import Dimension

from Platform.services.interface.customer_user_service_interface import ICustomerUserService

logger = logging.getLogger(__name__)
class CustomerUserServiceImpl(ICustomerUserService):
    """
    ViewSet for managing Customer Users, providing methods to add, edit,
    delete, and retrieve configurations.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerUserServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.customer_user_dao = CustomerUserDaoImpl()
            print(f"Inside CustomerUserDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True


    def add_customer_user(self, data,user_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started creating a customer user.")
        """
        This method creates a new customer user in the database after validating the uniqueness of the customer user name
        and email. It also builds the customer user instance and saves it.

        :param user_uuid: The unique identifier of the user performing the operation.
        :param data: A dictionary containing the customer client data.
        :return: None
        """

        # Extracting customer username and email from the input data
        info_json = data.get('user_info_json', {})
        # Validate the info json using dataclass
        data['user_info_json'] = asdict(ClientUserInfoJson(**info_json))

        # Build instance for customer_client
        customer_user = self.__build_customer_user_instance(user_uuid, data)

        # Save the customer client to the database
        self.customer_user_dao.save_customer_user(customer_user)


    def get_customer_users(self, customer_client_uuid, customer_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
            Retrieves a list of customer users based on the provided customer UUID.
            :param customer_client_uuid : The UUID of the customer client whose users list is to be fetched.
            :param customer_uuid : The UUID of the customer.
            :return: list: A list of formatted customer user dictionaries.
        """
        # Fetch customers from the DAO using the provided customer client uuid
        customer_users = self.customer_user_dao.get_customer_users_by_customer_client_uuid(customer_client_uuid, customer_uuid)

        # Log the number of customers retrieved
        logger.info("Retrieved %d customer users for customer_client_uuid: %s", len(customer_users), customer_client_uuid)

        return customer_users

    def edit_customer_user(self,data,user_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
           Updates an existing customer client user in the database.

           Parameters:
               user_uuid (str): Unique identifier of the user performing the update.
               data (dict): Contains updated customer user details

           Raises:
               CustomException: If the customer user is not found or if
                                the name/email already exists.
        """
        # Extract fields from the provided data
        client_user_uuid = data.get('client_user_uuid')

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email_id = data.get('email_id')
        user_info_json = data.get('user_info_json', {})
        # Validate the info json using dataclass
        user_info_json_dict = asdict(ClientUserInfoJson(**user_info_json))
        customer_client_uuid = data.get('customer_client_uuid')
        geography_uuid = data.get('geography_uuid')

        # Updating the customer client user in database
        updated_rows = self.customer_user_dao.update_customer_user(client_user_uuid,first_name,last_name,email_id,user_info_json_dict,customer_client_uuid,geography_uuid,user_uuid)
        if updated_rows == 0:
            logger.info("Customer client user not found with uuid :: %s", client_user_uuid)
            raise CustomException(ErrorMessages.CUSTOMER_USER_NOT_FOUND)


    def delete_customer_user(self, client_user_uuid, user_uuid):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
        Marks the customer user as deleted in the database by updating the relevant fields.

        Parameters:
            - customer_user_uuid: The unique identifier of the customer user to delete.
            - user_uuid: The unique identifier of the user performing the delete operation.

        Returns:
            - Number of rows updated (i.e., customer user marked as deleted).
        """
        # Proceed to mark the customer user as deleted and log the result
        updated_rows = self.customer_user_dao.delete_customer_user_by_id(client_user_uuid, user_uuid)
        logger.info(f"delete_customer_client :: Rows updated after delete operation: {updated_rows}")

        # Check if any rows were updated (i.e., customer user deleted), otherwise raise exception
        if updated_rows == 0:
            logger.error(f"delete_customer_user :: Customer user not found: {client_user_uuid}")
            raise CustomException(ErrorMessages.CUSTOMER_USER_NOT_FOUND)



    def __build_customer_user_instance(self, user_uuid, data):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Start")

        """
        Build and return a new CustomerUser instance using provided headers and data.

        :param user_uuid: user ID.
        :param data: Dictionary containing the customer client data.
        :return: A new ClientUser instance.
        """

        # Log the creation of a new CustomerUser instance
        logger.info(f"Building CustomerUser instance by user_uuid: {user_uuid}")

        # Create and return the CustomerUser instance
        customer_user = ClientUser(
            client_user_uuid=uuid.uuid4(),  # Generate a new unique UUID for the client
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email_id=data.get('email_id'),
            geography_uuid=Dimension(data.get('geography_uuid')),
            customer_client_uuid=CustomerClient(data.get('customer_client_uuid')),
            user_info_json=data.get('user_info_json'),
            created_by=user_uuid,
            updated_by=user_uuid
        )

        # Log the successful creation of the ClientUser instance
        logger.info("Successfully built CustomerUser instance")

        return customer_user
