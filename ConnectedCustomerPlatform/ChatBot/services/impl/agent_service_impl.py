import inspect
import json
import os
import logging

from ChatBot.dao.impl.user_details_dao_impl import UserDetailsViewDaoImpl
from ChatBot.services.interface.agent_service_interface import IAgentService


logger = logging.getLogger(__name__)


class AgentServiceImpl(IAgentService):
    """
        Service layer for handling agents logic such as retrieving agents.
        Interacts with the DAO layers
    """
    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AgentServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.info(f"Inside AgentServiceImpl - Singleton Instance ID: {id(self)}")
            self.__user_details_view_dao = UserDetailsViewDaoImpl()
            self.initialized = True

    def get_all_agents_except_current_agent(self, customer_uuid, application_uuid, user_uuid):
        """
            Retrieve all online agents/users for a given customer and application, excluding current agent/user
            Args:
                :param customer_uuid: UUID of the customer.
                :param application_uuid: UUID of the application.
                :param user_uuid : current user_uuid to exclude current csr in agents list
            Returns:
                List online users data
            Raises:
                CustomException: If there is an error retrieving agents.

        """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.debug(f"Retrieving all agents by customer: {customer_uuid} and application: {application_uuid}")
        # calling dao to retrieve agents
        user_details_data = self.__user_details_view_dao.get_online_user_details_by_customer_and_application_excluding_current_user(customer_uuid=customer_uuid, application_uuid=application_uuid, user_uuid=user_uuid)
        logger.debug(f"successfully Retrieved online agents for customer:{customer_uuid}, application:{application_uuid}")
        return user_details_data
