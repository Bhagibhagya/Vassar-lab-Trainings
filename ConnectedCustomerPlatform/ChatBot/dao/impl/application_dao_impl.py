import inspect
import logging

from ChatBot.dao.interface.application_dao_interface import IApplicationDao

from ChatBot.dataclasses.application_data import ApplicationData

from DatabaseApp.models import Applications


logger = logging.getLogger(__name__)


class ApplicationDaoImpl(IApplicationDao):
    """
            Data Access Object (DAO) for Application operations.
            Implements the Singleton pattern to ensure only one instance of this class is created.
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        """
            Ensure that only one instance of the DAO is created using the Singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(ApplicationDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
                Initialize the ApplicationDaoImpl instance only once.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside ApplicationDaoImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # creating application record using ApplicationData dataclass/pojo
    def create_application(self, application_data: ApplicationData):
        """
                    create a application record in user application table
                    Args:
                        application_data (ApplicationData): ApplicationData dataclass instance
                    Returns:
                        returns created application queryset
        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.info(f"creating a application :: application_data :: {application_data.to_dict()}")
        # Use the ApplicationData fields to create a new Customer record
        application_create_response = Applications.objects.create(
            application_uuid=application_data.application_uuid,
            application_name=application_data.application_name,
            application_url=application_data.application_url,
            scope_end_point=application_data.scope_end_point,
            description=application_data.description,
            status=application_data.status,
            created_ts=application_data.created_ts,
            updated_ts=application_data.updated_ts,
            created_by=application_data.created_by,
            updated_by=application_data.updated_by
        )
        return application_create_response
