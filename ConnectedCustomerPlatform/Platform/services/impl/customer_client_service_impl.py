import inspect
import logging
import uuid
from Platform.dao.impl.customer_client_dao_impl import CustomerClientDaoImpl
from Platform.services.interface.customer_client_service_interface import ICustomerClientService
from django.db import IntegrityError
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from rest_framework import status
from DatabaseApp.models import CustomerClient
from DatabaseApp.models import Dimension
from DatabaseApp.models import Customers

logger = logging.getLogger(__name__)
class CustomerClientServiceImpl(ICustomerClientService):
    """
    ViewSet for managing CustomerClientServiceImpl, providing methods to add, edit,
    delete, and retrieve configurations.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomerClientServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.customer_client_dao = CustomerClientDaoImpl()
            print(f"Inside CustomerClientDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True


    def add_customer_client(self, customer_uuid, user_uuid, data):
        """
        This method creates a new customer client in the database after validating the uniqueness of the customer client name
        and email. It also builds the customer client instance and saves it.

        :param customer_uuid: The unique identifier of the customer.
        :param user_id: The unique identifier of the user performing the operation.
        :param data: A dictionary containing the customer client data.
        :return: None
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Started creating a customer client.")

        # Extracting customer client name and email from the input data
        customer_client_name = data.get('customer_client_name')
        customer_client_emails = data.get('customer_client_emails')
        customer_client_domain_name = data.get('customer_client_domain_name')

        # Log extracted information for debugging
        logger.debug(f"Customer UUID: {customer_uuid}, User ID: {user_uuid}, Customer Client Name: {customer_client_name}, Customer Client Email: {customer_client_emails}")

        # Build instance for customer_client
        customer_client = self.__build_customer_client_instance(customer_uuid,user_uuid, data)

        # Save the customer client to the database
        try:
            self.customer_client_dao.save_customer_client(customer_client)
        except IntegrityError as e:
            if 'unique constraint' in str(e):
                if 'customer_client_emails' in str(e):
                    logger.error(f"Duplicate email found for: {customer_client_emails} and customer UUID: {customer_uuid}")
                    raise CustomException(ErrorMessages.CUSTOMER_EMAIL_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
                elif 'customer_client_name' in str(e):
                    logger.error(f"Duplicate name found for: {customer_client_emails} and customer UUID: {customer_uuid}")
                    raise CustomException(ErrorMessages.CUSTOMER_NAME_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
                elif 'customer_client_domain_name' in str(e):
                    logger.error(f"Duplicate name found for: {customer_client_domain_name} and customer UUID: {customer_uuid}")
                    raise CustomException(ErrorMessages.CUSTOMER_DOMAIN_NAME_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)

                else:
                    raise CustomException(ErrorMessages.ADD_CUSTOMER_CLIENT_FAILED)
            logger.error("Database integrity error: %s", str(e))
            raise CustomException(ErrorMessages.ADD_CUSTOMER_CLIENT_FAILED)
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise CustomException(ErrorMessages.ADD_CUSTOMER_CLIENT_FAILED)

    def get_customer_client(self, customer_uuid):
        """
            Retrieves a list of customer clients based on the provided customer UUID.
            :param customer_uuid (str): The UUID of the customer whose client list is to be fetched.
            :return: list: A list of formatted customer client dictionaries.
        """

        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")

        # Fetch customers from the DAO using the provided customer UUID
        customers = self.customer_client_dao.get_customers_by_customer_uuid(customer_uuid)

        # Log the number of customers retrieved
        logger.info("Retrieved %d customer clients for customer_uuid: %s", len(customers), customer_uuid)

        return customers

    def edit_customer_client(self, customer_uuid, user_id, data):
        """
           Updates an existing customer client in the database.

           Parameters:
               customer_uuid (str): Unique identifier of the customer making the request.
               user_id (str): Unique identifier of the user performing the update.
               data (dict): Contains updated customer client details

           Raises:
               CustomException: If the customer client is not found or if
                                the name/email already exists.
        """
        # Extract fields from the provided data
        customer_client_uuid = data.get('customer_client_uuid')

        # Retrieve the existing customer client from the database
        customer_client = self.customer_client_dao.get_customer_client_by_customer_client_uuid(customer_client_uuid)
        if customer_client is None:
            raise CustomException(ErrorMessages.CUSTOMER_NOT_FOUND)

        customer_client.customer_client_name = data.get('customer_client_name')
        customer_client.customer_client_domain_name = data.get('customer_client_domain_name')
        customer_client.customer_client_emails = data.get('customer_client_emails')
        customer_client.customer_client_geography_uuid = Dimension(data.get('customer_client_geography_uuid'))
        customer_client.customer_client_address =  data.get('customer_client_address')
        customer_client.updated_by = user_id

        # Save changes to the database
        try:
            self.customer_client_dao.save_customer_client(customer_client)
        except IntegrityError as e:
            if 'unique constraint' in str(e):
                if 'customer_client_emails' in str(e):
                    logger.error(f"Duplicate email found for: {data.get('customer_client_emails')} and customer UUID: {customer_uuid}")
                    raise CustomException(ErrorMessages.CUSTOMER_EMAIL_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
                elif 'customer_client_name' in str(e):
                    logger.error(f"Duplicate name found for: {data.get('customer_client_name')} and customer UUID: {customer_uuid}")
                    raise CustomException(ErrorMessages.CUSTOMER_NAME_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
                elif 'customer_client_domain_name' in str(e):
                    logger.error(f"Duplicate name found for: {data.get('customer_client_domain_name')} and customer UUID: {customer_uuid}")
                    raise CustomException(ErrorMessages.CUSTOMER_DOMAIN_NAME_EXISTS, status_code=status.HTTP_400_BAD_REQUEST)
                else:
                    raise e
            logger.error("Database integrity error: %s", str(e))
            raise CustomException(ErrorMessages.EDIT_CUSTOMER_CLIENT_FAILED)
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise CustomException(ErrorMessages.EDIT_CUSTOMER_CLIENT_FAILED)

    def delete_customer_client(self, customer_client_uuid, user_id):
        """
        Marks the customer client as deleted in the database by updating the relevant fields.

        Parameters:
            - customer_client_uuid: The unique identifier of the customer client to delete.
            - user_id: The unique identifier of the user performing the delete operation.

        Returns:
            - Number of rows updated (i.e., customer client marked as deleted).
        """

        # Log the start of the delete operation
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name} :: Start")
        logger.info(f"delete_customer_client :: Deleting customer client with UUID: {customer_client_uuid} by user: {user_id}")

        # Proceed to mark the customer client as deleted and log the result
        updated_rows = self.customer_client_dao.delete_customer_client_by_customer_client_id(customer_client_uuid, user_id)
        logger.info(f"delete_customer_client :: Rows updated after delete operation: {updated_rows}")

        # Return the number of updated rows (i.e., customers marked as deleted)
        return updated_rows


    def __build_customer_client_instance(self, customer_uuid,user_uuid, data):
        """
        Build and return a new CustomerClient instance using provided headers and data.

        :param headers: Tuple containing the customer UUID and user ID.
        :param data: Dictionary containing the customer client data.
        :return: A new CustomerClient instance.
        """

        # Log the creation of a new CustomerClient instance
        logger.info(f"Building CustomerClient instance for customer_uuid: {customer_uuid} by user_id: {user_uuid}")

        # Create and return the CustomerClient instance
        customer_client = CustomerClient(
            customer_client_uuid=uuid.uuid4(),  # Generate a new unique UUID for the client
            customer_client_name=data.get('customer_client_name'),  # Get the name from data
            customer_client_domain_name=data.get('customer_client_domain_name'),  # Get domain name if provided
            customer_client_geography_uuid=Dimension(data.get('customer_client_geography_uuid')),  # Set geography
            customer_client_emails=data.get('customer_client_emails'),  # Get email from data
            customer_client_address=data.get('customer_client_address'),  # Get address from data
            customer_uuid=Customers(customer_uuid),  # Create a Customers instance from customer_uuid
            created_by=user_uuid,  # Set the creator's user ID
            updated_by=user_uuid   # Set the updater's user ID
        )

        # Log the successful creation of the CustomerClient instance
        logger.info(f"Successfully built CustomerClient instance: {customer_client.customer_client_uuid}")

        return customer_client
