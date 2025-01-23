import inspect
import logging

from django.db import connection

from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException

from ChatBot.dao.interface.user_dao_interface import IUserDao
from ChatBot.dataclasses.user_data import UserData

from DatabaseApp.models import UserMgmtUsers

logger = logging.getLogger(__name__)


class UserDaoImpl(IUserDao):
    """
            Data Access Object (DAO) for User operations.
            Implements the Singleton pattern to ensure only one instance of this class is created.
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(UserDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
                Initialize the UserDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside UserDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def create_user(self, user_data: UserData):
        """
                create a user record
                Args:
                    user_data (UserData) : UserData dataclass instance
                Returns:
                    returns created user queryset
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.info(f"create a user:: user_data :: {user_data.to_dict()}")
        # Create a new user in the UserMgmtUsers model
        user = UserMgmtUsers.objects.create(
            user_id=user_data.user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email_id=user_data.email_id,
            username=user_data.user_name,
            mobile_number=user_data.mobile_number,
            title=user_data.title,
            user_details_json=user_data.user_details_json,
            customer_name=user_data.customer_name,
            customer_id=user_data.customer_id,
            status=user_data.status,
            auth_type=user_data.auth_type,
            password_hash=user_data.password_hash,
            activation_ts=user_data.activation_ts,
            password_last_updated_at=user_data.password_last_updated_at,
            last_login_ts=user_data.last_login_ts,
            created_ts=user_data.created_ts,
            updated_ts=user_data.updated_ts,
            created_by=user_data.created_by,
            updated_by=user_data.updated_by
        )

        return user

    def get_user_info(self, user_id: str) -> tuple[str, str, str, str]:
        
        logger.debug('In UserDaoImpl class :: get_user_info method')
        
        user_info = UserMgmtUsers.objects.filter(user_id=user_id).values('first_name', 'last_name', 'email_id', 'title').first()
        if user_info is None:
            
            logger.error(f'no user with user_id :: {user_id}')
            raise ResourceNotFoundException(f'no user with user_id :: {user_id}')

        return user_info['first_name'], user_info['last_name'], user_info['email_id'], user_info['title'] or ''