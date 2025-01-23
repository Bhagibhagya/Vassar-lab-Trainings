import logging
from EmailApp.Exceptions.api_exception import InvalidValueProvidedException
from ConnectedCustomerPlatform.exceptions import CustomException
from EmailApp.constant.error_messages import ErrorMessages
from urllib.parse import urlencode
from rest_framework import status
import requests
logger = logging.getLogger(__name__)
class UserManagementServices:

    def make_request(self, method, api_url,headers=None, data=None, query_params=None):
        logger.info(f"user_management_service.py :: UserManagementServices :: make_request")
        if query_params:
            api_url = f"{api_url}?{urlencode(query_params)}"

        if method.upper()=='GET':
            response = requests.get(api_url,headers=headers)
            print(response)

        elif method.upper()=='POST':
            response = requests.post(api_url, json=data,headers=headers)

        elif method.upper()=='PUT':
            response = requests.put(api_url, json=data,headers=headers)
            print(response.text)
        else:
            raise InvalidValueProvidedException(ErrorMessages.INVALID_HTTP_METHOD)

        if response.json().get("statusCode"):
            return response.json()
        
        else:
            return response.json().get('message',{})