from abc import ABC, abstractmethod


class IUserDetailsViewDao(ABC):
    """
    Interface for managing data access operations related to UserDetailsView.
    This defines methods for retrieving UserDetails along with his customer,role and application
    It follows the Data Access Object (DAO) pattern.
    """

    @abstractmethod
    def get_online_user_details_by_customer_and_application_excluding_current_user(self, customer_uuid, application_uuid, user_uuid):
        """
                    Retrieve all online unique users by customer_uuid and application_uuid
                    Args:
                        customer_uuid (str): unique identifier of customer
                        application_uuid (str): unique identifier of application
                        user_uuid (str): unique identifier of user
                    Returns:
                        list of online UserDetailsView queryset
        """