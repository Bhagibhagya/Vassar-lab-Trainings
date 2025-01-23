import inspect
import os
import logging
import requests
from rest_framework import status
from urllib.parse import urlencode

from ChatBot.services.interface.user_management_service_interface import IUserManagementService

from ChatBot.dataclasses.make_request_data import MakeRequestData

from ChatBot.constant.constants import RequestMethodConstants, UsermgmtApiResponseConstants

from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException, CustomException

from ChatBot.constant.error_messages import ErrorMessages

logger = logging.getLogger(__name__)


class UserManagementServiceImpl(IUserManagementService):

    _instance = None

    # to make sure only single instance of this class is created
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserManagementServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside UserManagementServiceImpl __init__ method")
            print(f"Inside UserManagementServiceImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True

    def make_request(self, request_data: MakeRequestData):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        logger.info(f"make_request_data :: {request_data.to_dict()}")
        # access the fields from the MakeRequestData object
        request_method = request_data.request_method
        api_url = request_data.api_url
        headers = request_data.headers
        payload = request_data.payload
        query_params = request_data.query_params

        if query_params:
            api_url = f"{api_url}?{urlencode(query_params)}"

        # calling GET api
        if request_method.upper() == RequestMethodConstants.GET:
            response = requests.get(api_url, headers=headers)

        # calling POST api
        elif request_method.upper() == RequestMethodConstants.POST:
            response = requests.post(api_url, json=payload, headers=headers)

        # calling PUT api
        elif request_method.upper() == RequestMethodConstants.PUT:
            response = requests.put(api_url, json=payload, headers=headers)
        # add if you need any other api method calls here
        else:
            raise InvalidValueProvidedException(ErrorMessages.INVALID_HTTP_METHOD)

        if response.ok:
            return response.json()
        else:
            logger.debug("got error while calling usermgmt api")
            logger.debug(f"usermgmt error response :: {response.json()}")
            if response.json().get(UsermgmtApiResponseConstants.MESSAGE):
                raise CustomException(detail=response.json().get(UsermgmtApiResponseConstants.MESSAGE), status_code=response.status_code)

            elif response.json().get(UsermgmtApiResponseConstants.STATUS_CODE_DESCRIPTION):
                raise CustomException(detail=response.json().get(UsermgmtApiResponseConstants.STATUS_CODE_DESCRIPTION), status_code=response.status_code)

            else:
                raise CustomException(detail=ErrorMessages.ERROR_FROM_USERMGMT_API, status_code=response.status_code)

    def build_make_request_object(self, request_method, api_url, headers=None, payload=None, query_params=None):
            logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
            # Validate required parameters
            if not request_method:
                raise CustomException(ErrorMessages.REQUEST_METHOD_NOT_PROVIDED,
                                      status_code=status.HTTP_400_BAD_REQUEST)

            if not api_url:
                raise CustomException(ErrorMessages.API_URL_NOT_PROVIDED, status_code=status.HTTP_400_BAD_REQUEST)

            make_request_data = MakeRequestData(
                request_method=request_method,
                api_url=api_url,
                headers=headers,
                payload=payload,
                query_params=query_params

            )
            return make_request_data
