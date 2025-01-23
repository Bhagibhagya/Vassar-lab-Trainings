import uuid
import logging
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from EmailApp.dao.impl.customer_application_mapping_dao_impl import CustomerApplicationMappingDaoImpl
from Platform.constant import constants
from Platform.constant.error_messages import ErrorMessages
logger=logging.getLogger(__name__)

def create_new_uuid_4():
    """
    Generate and return a new UUID (Universally Unique Identifier).

    :return: A newly generated UUID.
    """
    return uuid.uuid4()


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Utils:

    @staticmethod
    def validate_input(data):
        """
        This is the Method to Validate the given data to ensure it is not None, not empty, and not blank.

        Args:
            data: The input data to validate.
            error message: The error message to return if validation fails.

        Returns:
            True if the data is valid, False otherwise.
        """
        if data is None:
            return False
        elif isinstance(data, str) and (data.strip() == '' or data.strip() == ''):
            return False
        elif isinstance(data, (list, tuple, dict, set)) and not data:
            return False
        else:
            return True

    @staticmethod
    def is_valid_uuid(data):
        """
            This is the Method to Validate the given data to ensure it is uuid or not
            Args:
                data: The input data to validate.
            Returns:
                True if the data is valid, False otherwise.
        """

        if isinstance(data, uuid.UUID):
            # If it's already a UUID object, it's valid
            return True
        elif isinstance(data, str):
            try:
                # Try to create a UUID object from the string
                uuid_obj = uuid.UUID(data)
                # Check if the string matches the UUID exactly
                return str(uuid_obj) == data
            except (ValueError, TypeError):
                logger.error(f"{data} should be valida UUID not {type(data)}")
                # If it raises an error, it's not a valid UUID
                return False
        else:
            logger.debug(f"data should be string or UUID to check valid uuid but not {type(data)} type")
            # If the value is neither a UUID object nor a string, it's invalid
            return False

    @staticmethod
    def get_headers(headers):
        customer_uuid = headers.get(constants.CUSTOMER_UUID)
        application_uuid = headers.get(constants.APPLICATION_UUID)
        user_uuid = headers.get(constants.USER_ID)
        if not Utils.validate_input(customer_uuid):
            raise CustomException(ErrorMessages.CUSTOMER_ID_NOT_NULL)
        if not Utils.validate_input(application_uuid):
            raise CustomException(ErrorMessages.APPLICATION_ID_NOT_NULL)
        if not Utils.validate_input(user_uuid):
            raise CustomException(ErrorMessages.USER_ID_NOT_NULL)
        if not Utils.is_valid_uuid(customer_uuid):
            raise CustomException("customer_uuid : " + ErrorMessages.NOT_VALID_UUID)
        if not Utils.is_valid_uuid(application_uuid):
            raise CustomException("application_uuid : " + ErrorMessages.NOT_VALID_UUID)
        if not Utils.is_valid_uuid(user_uuid):
            raise CustomException("user_uuid : " + ErrorMessages.NOT_VALID_UUID)
        return customer_uuid, application_uuid, user_uuid

    @staticmethod
    def get_chroma_collection_name(customer_uuid, application_uuid, prefix):
        '''
        Method to get the collection name of chroma vector for a given customer and application
        '''
        logger.info("In ChromaVectorStore :: get_chroma_collection_name_by_customer_application")
        # Get the customer application mapping Id
        customer_application_mapping_dao = CustomerApplicationMappingDaoImpl()
        cust_app_map_id = customer_application_mapping_dao.get_cust_app_mapping_uuid(customer_uuid=customer_uuid,application_uuid=application_uuid)
        if cust_app_map_id is None:
            logger.error(f"customer application mapping not found for customer_uuid{customer_uuid} and application_uuid {application_uuid}")
            raise InvalidValueProvidedException(detail=f"customer application mapping not found for customer_uuid{customer_uuid} and application_uuid {application_uuid}")
        # Collection name will be Prefix + cust_app_map_id
        custom_chroma_collection_name = prefix+str(cust_app_map_id)
        logger.debug(f"collection name is {custom_chroma_collection_name}")
        return custom_chroma_collection_name
