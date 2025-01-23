from rest_framework.viewsets import ViewSet
import logging

from ConnectedCustomerPlatform.responses import CustomResponse
from rest_framework.decorators import action

from Platform.services.impl.customer_service_impl import CustomerServiceImpl

logger = logging.getLogger(__name__)

class CustomersViewSet(ViewSet):
    """
    This ViewSet provides method retrieve Customers. It ensures that only a single instance is created using the Singleton pattern.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the CustomersViewSet is created.

        Args:
            cls: The class reference.
            *args: Positional arguments for initialization.
            **kwargs: Keyword arguments for initialization.

        Returns:
            CustomersViewSet: The singleton instance of the ViewSet.
        """
        if cls._instance is None:
            cls._instance = super(CustomersViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the CustomersViewSet.

        This method is called only once due to the singleton pattern. It initializes the
        LLMConfigurationService for handling business logic related to LLM configurations.

        Args:
            **kwargs: Keyword arguments for initialization.
        """
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.__customer_service = CustomerServiceImpl()  # Instantiate the service to handle business logic
            logger.info(f"Inside CustomerViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    @action(detail=False, methods=['get'])
    def get_customers(self, request):
        logger.info("In customers.py :: :: :: CustomersViewSet :: :: :: get_customers ")

        """
        Retrieve all the customer Ids and customer names.

        :return: Response object with a list of customer ids and customer names.
        """

        # Retrieve Customers using the service layer
        customers = self.__customer_service.get_customers()
        logger.info("Successfully retrieved customers")
        return CustomResponse(customers)