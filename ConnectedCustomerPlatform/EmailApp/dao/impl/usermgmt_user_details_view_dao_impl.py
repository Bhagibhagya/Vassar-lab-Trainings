from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import UserDetailsView
from EmailApp.constant.error_messages import ErrorMessages
from rest_framework import status

from EmailApp.dao.interface.usermgmt_user_details_view_dao_interface import IUsersDetailsViewDaoInterface
import logging
logger=logging.getLogger(__name__)

class UsersDetailsViewDaoImpl(IUsersDetailsViewDaoInterface):
    def get_role_name_of_user(self, user_uuid,customer_uuid,application_uuid):
        """Returns role_name, application_name, customer_name for the user and application"""
        logger.info("In UsersDetailsViewDaoImpl :: get_role_name_of_user")

        # Retrieve only role_name,application_name and customer_name fields as a tuple
        user_details = UserDetailsView.objects.filter(user_id=user_uuid,customer_id=customer_uuid,application_id=application_uuid).values_list('role_name','application_name','customer_name').first()
        logger.debug(f"user_details{user_details}")
        if user_details is None:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.USER_NOT_FOUND_IN_USERMGMT,
                status_code=status.HTTP_404_NOT_FOUND
            )
        return user_details