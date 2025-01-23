import inspect
import os
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from ConnectedCustomerPlatform.responses import CustomResponse
from ChatBot.constant.constants import CaptchaConstants
from ChatBot.services.impl.captcha_service_impl import CaptchaServiceImpl
import logging
from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.serializers import CaptchaSerializer
from drf_yasg.utils import swagger_auto_schema
from ChatBot.constant.error_messages import ErrorMessages

logger = logging.getLogger(__name__)

class CaptchaImageViewSet(ViewSet):
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CaptchaImageViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.captcha_service = CaptchaServiceImpl()  # Injecting the implementation class
            self.initialized = True

    @swagger_auto_schema(
        operation_description="Generates a CAPTCHA image and its corresponding encoded text.",
        responses={
            status.HTTP_200_OK: CaptchaSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorMessages.FAILED_T0_GENERATE_IMAGE
        },
    )
    @action(detail=False, methods=['get'])
    def generate_captcha_image(self, request):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        img_base64, captcha_text = self.captcha_service.generate_captcha_image(
            CaptchaConstants.WIDTH,
            CaptchaConstants.HEIGHT,
            CaptchaConstants.LENGTH
        )
        # Check if the generated values are None

        if img_base64 is None or captcha_text is None:
            raise CustomException(ErrorMessages.FAILED_T0_GENERATE_IMAGE)
        # Encode the CAPTCHA text to base64 for security purposesSS

        response_data = {
            CaptchaConstants.CAPTCHA_IMAGE: img_base64,
            CaptchaConstants.ENCODE_TEXT: captcha_text
        }
        return CustomResponse(response_data)