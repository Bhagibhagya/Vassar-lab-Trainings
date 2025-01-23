

from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import EmailServer
from EmailApp.constant.error_messages import ErrorMessages

from rest_framework import status

from EmailApp.dao.interface.email_server_dao_interface import EmailServerDaoInterface

class EmailServerDaoImpl(EmailServerDaoInterface):

    def get_email_server(self, server_type, customer_uuid, application_uuid):
        """
        Method to retrieve SMTP server details based on the provided filter.
        
        Args:
            smtp_filter (dict): A dictionary containing filters such as customer_uuid, application_uuid, server_type, etc.
        
        Returns:
            tuple: (server_url, port) if a matching record is found.
        
        Raises:
            CustomException: If no matching record is found, a 404 error is raised.
        """
        try:
            # Execute the query
            return EmailServer.objects.values_list('server_url', 'port').get(
                emailservercustomerapplicationmapping__customer_uuid=customer_uuid,
                emailservercustomerapplicationmapping__application_uuid=application_uuid,
                emailservercustomerapplicationmapping__status=True,
                server_type=server_type,
                is_deleted=False,
                status=True
            )

        except EmailServer.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.SMTP_SERVER_DETAILS_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )
