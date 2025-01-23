import logging
import re

from rest_framework import status
from django.conf import settings

"""
Middleware to log all requests and responses.
Uses a logger configured by the name of django.request
to log all requests and responses according to configuration
specified for django.request.
"""
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
import requests
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def authenticate_and_authorise_apis(url, payload_data, header_info, request):
    # variable to check if the user is having access to requested resource
    has_valid_access = None
    try:
        # Calling User-management api to validate the incoming request
        result = requests.post(url, data=json.dumps(payload_data), headers=header_info)
        response_data = json.loads(result.content)
        logger.info(f"Received response from UM api : {response_data}")
        # if api call is success getting the permission
        if response_data['statusCode'] == 200:
            has_valid_access = response_data['response']['resourceAccessInfo'][0]['hasValidAccess']
            # if api called failed throwing exception
        else:
            data = {"result": "UM api failure", "status": False, "code": response_data['statusCode']}
            response = Response(data=data, status=response_data['statusCode'])
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()
            return response
    # if any issue occurred while api calling
    except Exception as e:
        logger.info(f"An exception occurred ::{str(e)}")
        data = {"result": "UM api exception occurred", "status": False, "code": 401}
        response = Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()
        return response

    
    scope = response_data['response']['resourceAccessInfo'][0]['scope']
    if scope is None:
        scope = []
    customer_id = None
    if 'customerId' in response_data['response'] and response_data['response']['customerId'] is not None:
        customer_id = response_data['response']['customerId']

    request.customerId = customer_id
    user_id = response_data['response']['userId']
    request.userId = user_id

    if customer_id is None and len(scope) == 0:
        scope = [{"scopeName": "Resource", "scopeType": "NON_HIERARCHY", "scopeValue": ["*"], "hasAccess": True}]

    request.scope = scope
    return request


    # # If the user is having permission allow it to access application
    # if has_valid_access:
    #     # Build payload for the User
    #     payload = None
    #     # Super Admin User
    #     if customer_id is None:
    #         if len(scope) == 0:
    #             payload = [{"scopeName": "Resource", "scopeType": "NON_HIERARCHY", "scopeValue": ["*"], "hasAccess": True}]
    #         else:
    #             payload = scope
    #
    #     #  If user is under a Customer or user is customer admin and has scope specified either Hierarchy or Non-Hierarchy
    #     else:
    #         payload = scope
    #
    #     request.scope = payload
    #     return request
    # else:
    #     data = {"code": 403, "status": False, "result": "User Id " + json.loads(result.content)['response'][
    #             'userId'] + " does not have permission register in usermgmt for resource " +
    #              json.loads(result.content)['response']['resourceAccessInfo'][0]['resourceName']}
    #     response = Response(data=data, status=status.HTTP_403_FORBIDDEN)
    #     response.accepted_renderer = JSONRenderer()
    #     response.accepted_media_type = "application/json"
    #     response.renderer_context = {}
    #     response.render()
    #     return response



class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = {
            r"^/api/platform/chat_configuration/activate$": "GET",
            r"^/api/chatbot/dimension/intents$": None,
            r"^/api/chatbot/conversations/[^/]+/history$": None,
            r"^/api/chatbot/upload_attachment$": None,
            r"^/api/chatbot/chat_conversation/feedback$": None,
            r"^/api/chatbot/captcha/image$": None,
            r"^/api/email/healthCheck$": None,
            r"^/api/wiseflow/test_entity_prompt$":None,
            r"^/api/wiseflow/entity_examples$":None
        }

    def __call__(self, request, *args, **kwargs):

        request_path = request.path
        # Skip request if path matches and method is correct
        for path_pattern, method in self.excluded_paths.items():
            if re.match(path_pattern, request_path) and (method is None or request.method == method):
                return self.get_response(request)

        api_end_point = request.path.split('/')[2]
        auth_token = request.headers.get('Authorization')
        csrf_token = request.headers.get('Csrf-Token')
        user_id = request.headers['User-Uuid']

        application_id = request.headers['Application-Uuid']
        payload_data = {
            "userId": user_id,
            "applicationId": application_id,
            "multiResourceAuthRequest": [{
                "resourceName": api_end_point,
                "actions": ["READ", "EDIT"],
                "scope": None
            }]
        }
        header_info = {
            "Content-Type": "application/json",
            "Authorization": auth_token,
            "Csrf-Token": csrf_token
        }
        url = settings.USERMGMT_AUTH_URL
        request = authenticate_and_authorise_apis(url, payload_data, header_info, request)
        if not isinstance(request,Response):
            response = self.get_response(request)
        else:
            response = request
        return response
