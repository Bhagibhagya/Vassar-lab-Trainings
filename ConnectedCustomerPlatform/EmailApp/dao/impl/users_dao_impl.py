
from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import UserMgmtUsers
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.dao.interface.users_dao_interface import UsersDaoInterface
from django.db import connection

from rest_framework import status

class UsersDaoImpl(UsersDaoInterface):
    def get_user(self, user_uuid):
        
        try:
             # Retrieve only first_name and last_name fields as a tuple
            return UserMgmtUsers.objects.values_list('first_name', 'last_name').get(user_id=user_uuid)

        except UserMgmtUsers.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.USER_NOT_FOUND_IN_USERMGMT,
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    def get_users_name(self, user_uuids):
        # Raw SQL query to fetch user details based on user UUIDs
        query = """
                    SELECT 
                        u.user_id,
                        u.username
                    FROM 
                        usermgmt.users u
                    WHERE 
                        u.user_id = ANY(%s);
                """

        with connection.cursor() as cursor:
            cursor.execute(query, [list(user_uuids)])
            results = cursor.fetchall()

        # Format as a list of tuples [(user_uuid, user_name), ...]
        user_list = [(row[0], row[1]) for row in results]
        return user_list
