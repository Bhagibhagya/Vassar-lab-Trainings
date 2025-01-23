from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

import logging
from EmailApp.constant.success_messages import SuccessMessages
from ConnectedCustomerPlatform.exceptions import CustomException,CustomResponse


logger = logging.getLogger(__name__)



class EmailsViewSet(ViewSet):

    @action(detail=False, methods=['get'])
    def healthCheck(self, request):
        return CustomResponse(SuccessMessages.HEALTH_CHECK_RESPONSE)
   