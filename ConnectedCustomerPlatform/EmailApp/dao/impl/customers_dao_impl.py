


from ConnectedCustomerPlatform.exceptions import CustomException
from DatabaseApp.models import Customers
from EmailApp.constant.error_messages import ErrorMessages
from EmailApp.dao.interface.customers_dao_interface import CustomersDaoInterface
from rest_framework import status

class CustomersDaoImpl(CustomersDaoInterface):

    def get_customer_name(self, customer_uuid):

        try:
            return Customers.objects.values_list('cust_name', flat=True).get(cust_uuid=customer_uuid)

        except Customers.DoesNotExist:
            # Handle case where no record is found
            raise CustomException(
                ErrorMessages.CUSTOMER_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND
            )