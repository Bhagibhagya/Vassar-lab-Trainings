from EmailApp.Exceptions.api_exception import InvalidValueProvidedException
from ConnectedCustomerPlatform.exceptions import CustomException
from EmailApp.constant.error_messages import ErrorMessages
from urllib.parse import urlencode
from rest_framework import status
import requests

class UserManagementServices:

    def make_request(self, method, api_url, headers, data=None, query_params=None):

        if query_params:
            api_url = f"{api_url}?{urlencode(query_params)}"

        if method.upper()=='GET':
            response = requests.get(api_url, headers=headers)

        elif  method.upper()=='POST':
            response = requests.post(api_url, json=data, headers=headers)

        else:
            raise InvalidValueProvidedException(ErrorMessages.INVALID_HTTP_METHOD)

        if response.ok:
            return response.json().get('response',{})
        
        else: 
            if response.json().get('message'):
                raise CustomException(detail = response.json().get('message'), status_code=response.status_code)

            elif  response.json().get('statusCodeDescription'):
                raise CustomException(detail = response.json().get('statusCodeDescription'), status_code=response.status_code)

            else:
                raise CustomException(detail = ErrorMessages.ERROR_FROM_USERMGMT_API, status_code=response.status_code)