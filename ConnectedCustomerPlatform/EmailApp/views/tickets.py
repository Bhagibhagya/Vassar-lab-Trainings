from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action

from EmailApp.services.impl.ticket_service_impl import TicketServiceImpl
from EmailApp.utils import  validate_uuids_dict

import logging
from EmailApp.serializers import EmailConversationSerializer
from ConnectedCustomerPlatform.exceptions import CustomException
from ConnectedCustomerPlatform.responses import CustomResponse
from EmailApp.constant.constants import EmailDashboardParams


logger = logging.getLogger(__name__)

class TicketViewSet(ViewSet):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TicketViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print(f"Inside TicketViewSet - Singleton Instance ID: {id(self)}")
            self.ticket_service = TicketServiceImpl()
            self.initialized = True

    @action(detail=False, methods=['post'])
    def get_email_tickets(self, request):
        """
        API to retrieve email tickets based on customer uuid, application uuid , email_conversation_flow_status and other filters
        """
        logger.info("In tickets.py :: :: ::  TicketViewSet :: :: :: get_email_Tickets ")

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        validate_uuids_dict({
                EmailDashboardParams.APPLICATION_UUID.value:application_uuid,
                EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid,
                EmailDashboardParams.USER_UUID.value : user_uuid
        })

        ticket_serializer = EmailConversationSerializer(data=request.data)

        if not ticket_serializer.is_valid():
            raise CustomException(ticket_serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        response_data = self.ticket_service.get_email_tickets(customer_uuid, application_uuid,user_uuid, ticket_serializer.validated_data)

        return CustomResponse(result=response_data,code=status.HTTP_200_OK)