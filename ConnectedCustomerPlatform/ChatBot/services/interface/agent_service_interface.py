from abc import ABC, abstractmethod


class IAgentService(ABC):
    """
        Interface for managing Agents.
        This interface provides abstract methods for retrieving online agents/users based on customer, application.
    """
    @abstractmethod
    def get_all_agents_except_current_agent(self, customer_uuid, application_uuid, user_uuid):
        """
            get all online agents(users from usermgmt) by customer_uuid and application_uuid
            Args:
                customer_uuid: Unique identifier for the customer.
                application_uuid: Unique identifier for the application.
                user_uuid : Unique identifier for the user
            Return:
                List online users data
            Raises:
                CustomException: If there is an error retrieving agents.
        """

