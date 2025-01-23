import inspect
import logging

from ChatBot.constant.constants import RawSqlQueryConstants, UserConstants
from ChatBot.dao.interface.user_details_dao_interface import IUserDetailsViewDao
from DatabaseApp.models import UserDetailsView
from Platform.utils import execute_to_dict

logger = logging.getLogger(__name__)


class UserDetailsViewDaoImpl(IUserDetailsViewDao):
    """
        Data Access Object (DAO) for UserDetailsView operations.
        Implements the Singleton pattern to ensure only one instance of this class is created.
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        """
                Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(UserDetailsViewDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
                Initialize the UserDetailsViewDao instance only once.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside UserDetailsViewDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def get_online_user_details_by_customer_and_application_excluding_current_user(self, customer_uuid,
                                                                                   application_uuid, user_uuid):
        """
                    Retrieve all online unique users by customer_uuid and application_uuid
                    Args:
                        customer_uuid (str): unique identifier of customer
                        application_uuid (str): unique identifier of application
                        user_uuid (str): unique identifier of user
                    Returns:
                        list of online UserDetailsView queryset
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(
            f"fetching online users from user details db view with customer:{customer_uuid}, application:{application_uuid}")
        query = RawSqlQueryConstants.QUERY_TO_FETCH_ONLINE_USERS_BY_EXCLUDE_CURRENT_USER
        result = execute_to_dict(query=query, params=[customer_uuid, application_uuid, user_uuid])
        return result

