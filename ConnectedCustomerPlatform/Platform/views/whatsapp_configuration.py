# import base64
# import json
# import logging
# import json
# from datetime import datetime, timedelta
# import re
#
# import requests
# from Platform.constant.error_messages import ErrorMessages
# from django.http import HttpResponse, JsonResponse
# from rest_framework import status
# from rest_framework.decorators import action
# from rest_framework.viewsets import ViewSet
# from rest_framework.response import Response
# from ConnectedCustomerPlatform.exceptions import CustomException
# from Platform.constant import constants
#
# from ConnectedCustomerPlatform.responses import CustomResponse
# import copy
# from Platform.utils import validate_input
#
#
# logger = logging.getLogger(__name__)
# class WhatsappConfigurationViewSet(ViewSet):
#     def create_intents_template(self,welcome_message , template_data , api_key_details):
#         logger.info("In views.py :: :: :: WhatsappConfigurationViewSet :: :: :: create_intents_template ")
#
#         access_token = api_key_details.get("apiKey")
#         business_key = api_key_details.get("businessId")
#         if not validate_input(access_token):
#             raise CustomException(ErrorMessages.ACCESS_TOKEN_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(business_key):
#             raise CustomException(ErrorMessages.BUSINESS_ID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#
#         url = constants.TEMPLATE_CREATION_URL.format(business_key=business_key)
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }
#         template_name = template_data.get('templateName')
#         if not template_name or len(template_name) > 512:
#             raise CustomException(ErrorMessages.TEMPLATE_NAME_INVALID,
#                 status_code=status.HTTP_400_BAD_REQUEST)
#         if not re.match(r'^[a-z0-9_]+$', template_name):
#             raise CustomException(
#                 ErrorMessages.INVALID_MESSAGE_TEMPLATE,
#                 status_code=status.HTTP_400_BAD_REQUEST)
#         payload = copy.deepcopy(constants.TEMPLATE_PAYLOAD)
#         payload['name'] = payload['name'].format(template_name=template_name)
#         payload['components'][0]['text'] = payload['components'][0]['text'].format(
#             header_text=welcome_message.get('message', ''))
#         payload['components'][1]['text'] = payload['components'][1]['text'].format(
#             body_text=template_data.get('question', ''))
#
#         messages = template_data.get('messages')
#         if messages:
#             buttons_component = copy.deepcopy(constants.BUTTONS_COMPONENT)
#             buttons_component['buttons'] = [
#                 {
#                     "type": constants.BUTTON_TYPE,
#                     "text": message_data['intent']
#                 } for message_data in messages.values()
#             ]
#             payload['components'].append(buttons_component)
#
#         response = requests.post(url, headers=headers, json=payload)
#         if response.status_code == 200:
#             return response
#         else:
#             error_data = response.json()
#             error_code = error_data.get('error', {}).get('code')
#             if error_code == 190:
#                 raise CustomException(ErrorMessages.INVALID_ACCESS_TOKEN,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 100:
#                 error_subcode = error_data.get('error',{}).get('error_subcode')
#                 if error_subcode == 2388024:
#                     raise CustomException(
#                         ErrorMessages.TEMPLATE_NAME_ALREADY_EXISTS.format(template_name = template_name),
#                         status_code=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     logger.info(error_data)
#                     raise CustomException(ErrorMessages.INVALID_BUSINESS_ID.format(operation = constants.TEMPLATE_CREATION),
#                                           status_code=status.HTTP_400_BAD_REQUEST)
#
#             elif error_code == 200:
#                 raise CustomException(ErrorMessages.PERMISSION_ERROR,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             else:
#                 logger.info(response.json())
#                 raise CustomException(ErrorMessages.CANNOT_CREATE_TEMPLATE,
#                                       status_code=response.status_code)
#
#
#
#     def edit_intents_template(self, existing_template,template ,api_key_details,welcome_message):
#         logger.info("In views.py :: :: :: WhatsappConfigurationViewSet :: :: :: edit_intents_template ")
#
#         template_uuid = template.get('templateUUID', "")
#         accessToken = api_key_details.get("apiKey")
#         last_edit_time = existing_template.get('lastEditTime')
#         if last_edit_time:
#             last_edit_time = datetime.strptime(last_edit_time, '%Y-%m-%d %H:%M:%S')
#             if (datetime.utcnow() - last_edit_time) < timedelta(days=1):
#                 raise CustomException(ErrorMessages.TEMPLATE_EDIT_ONCE_A_DAY,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(accessToken):
#             raise CustomException(ErrorMessages.ACCESS_TOKEN_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(template_uuid):
#             raise CustomException(ErrorMessages.TEMPLATE_UUID_NOT_NULL, status_code =status.HTTP_400_BAD_REQUEST)
#
#
#         template_status = existing_template.get("templateStatus")
#         if template_status == constants.PENDING:
#             raise CustomException(ErrorMessages.PENDING_TEMPLATE_EDITING_INVALID, status_code = status.HTTP_400_BAD_REQUEST)
#         template_data = copy.deepcopy(constants.TEMPLATE_PAYLOAD)
#         template_data['components'][0]['text'] = template_data['components'][0]['text'].format(header_text = welcome_message.get('message', ''))
#         template_data['components'][1]['text'] = template_data['components'][1]['text'].format(body_text = template.get('question', ''))
#
#         messages = template.get('messages')
#
#         if messages:
#             buttons_component = copy.deepcopy(constants.BUTTONS_COMPONENT)
#             buttons_component['buttons'] = [
#                 {
#                     "type": constants.BUTTON_TYPE,
#                     "text": message_data['intent']
#                 } for message_data in messages.values()
#             ]
#             template_data['components'].append(buttons_component)
#
#         url = constants.TEMPLATE_EDITING_URL.format(template_uuid=template_uuid)
#
#         headers = {
#             "Authorization": f"Bearer {accessToken}",
#             "Content-Type": "application/json"
#         }
#
#         payload = {}
#         if 'components' in template_data:
#             payload['components'] = template_data['components']
#
#         response = requests.post(url, headers=headers, json=payload)
#         if response.status_code == 200:
#             return response
#         else:
#             error_data = response.json()
#             error_code = error_data.get('error', {}).get('code')
#             if error_code == 190:
#                 raise CustomException(ErrorMessages.INVALID_ACCESS_TOKEN,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 100:
#                 raise CustomException(ErrorMessages.INVALID_TEMPLATE_UUID,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#
#             elif error_code == 200:
#                 raise CustomException(ErrorMessages.PERMISSION_ERROR,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             else:
#                 logger.info(response.json())
#                 raise CustomException(ErrorMessages.CANNOT_EDIT_TEMPLATE,
#                                       status_code=response.status_code)
#
#
#
#
#     @action(detail=False, methods=['get'])
#     def get_business_info(self, request):
#         business_id = request.query_params.get("businessId")
#         access_token = request.query_params.get("apiKey")
#         if not validate_input(access_token):
#             raise CustomException(ErrorMessages.ACCESS_TOKEN_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(business_id):
#             raise CustomException(ErrorMessages.BUSINESS_ID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         url = constants.BUSINESS_DETAILS_URL.format(business_id=business_id)
#
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }
#
#         params = {
#             'fields': 'id,name,phone_numbers',
#             'limit': 100
#         }
#
#         # Sending the GET request to Meta API
#         response = requests.get(url, headers=headers, params=params)
#         if response.status_code == 200:
#             data = response.json()
#
#             # Format the response data
#             formatted_businesses = [
#                 {
#                     'business_id': data.get('id'),
#                     'name': data.get('name'),
#                     'phone_numbers': data.get('phone_numbers', [])
#                 }
#             ]
#
#             return CustomResponse(formatted_businesses, status=status.HTTP_200_OK)
#
#         else:
#             error_data = response.json()
#             error_code = error_data.get('error', {}).get('code')
#
#             if error_code == 190:
#                 raise CustomException(ErrorMessages.INVALID_ACCESS_TOKEN,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 100:
#                 raise CustomException(ErrorMessages.INVALID_BUSINESS_ID.format(operation = constants.BUSINESS_INFO_FETCHING),
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#
#             elif error_code == 200:
#                 raise CustomException(ErrorMessages.PERMISSION_ERROR,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             else:
#                 logger.info(response.json())
#                 raise CustomException(ErrorMessages.CANNOT_ABLE_TO_GET_BUSINESS_INFO, status_code=response.status_code)
#
#
#
#
#     def get_profile_picture_handle(self,request):
#         logger.info("In views.py :: :: :: WhatsappConfigurationViewSet :: :: :: get_profile_picture_handle ")
#
#         data = request
#         app_id = data.get('app_id')
#         file_name = data.get('file_name')
#         file_length = data.get('file_length')
#         file_type = data.get('file_type')
#         access_token = data.get('access_token')
#         binary_picture = data.get('binary_picture')
#         if not app_id or not file_name or not file_length or not file_type or not access_token :
#             return CustomException(ErrorMessages.MISSING_PARAMETERS, status_code =status.HTTP_400_BAD_REQUEST)
#
#         # Step 1: Start an upload session
#         start_upload_url = constants.START_UPLOAD_URL.format(app_id = app_id)
#         start_upload_params = {
#             'file_name': file_name,
#             'file_length': file_length,
#             'file_type': file_type,
#             'access_token': access_token
#         }
#
#         response = requests.post(start_upload_url, params=start_upload_params)
#         response_data = response.json()
#         if 'error' in response_data:
#             error_code = response_data['error'].get('code')
#             if error_code == 190:
#                 raise CustomException(ErrorMessages.INVALID_ACCESS_TOKEN, status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 100:
#                 raise CustomException(ErrorMessages.INVALID_APPLICATION_ID,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 200:
#                 raise CustomException(ErrorMessages.PERMISSION_ERROR, status_code=status.HTTP_400_BAD_REQUEST)
#             else:
#                 logger.info(response_data)
#                 raise CustomException(ErrorMessages.CANNOT_UPLOAD_SESSION, status_code = status.HTTP_400_BAD_REQUEST)
#
#         upload_session_id = response_data['id'].split(':')[1]
#         upload_url = constants.UPLOAD_SESSION_URL.format(upload_session_id = upload_session_id)
#
#         upload_response = requests.post(
#             upload_url,
#             headers={
#                 'Authorization': f'OAuth {access_token}',
#                 'file_offset': '0',
#             },
#             data=binary_picture
#         )
#         upload_response_data = upload_response.json()
#         if 'h' not in upload_response_data:
#             logger.info(upload_response_data)
#             raise CustomException(ErrorMessages.CANNOT_GET_FILE_HANDLE, status_code = status.HTTP_400_BAD_REQUEST)
#
#         profile_picture_handle = upload_response_data['h']
#         return profile_picture_handle
#
#     def update_profile_picture(self,profile_details,api_key_details):
#         logger.info("In views.py :: :: :: WhatsappConfigurationViewSet :: :: :: update_profile_picture ")
#
#         phone_number_id = api_key_details.get("phoneNumberId")
#         access_token = api_key_details.get("apiKey")
#         app_id = api_key_details.get("appId")
#
#         if not validate_input(access_token):
#             raise CustomException(ErrorMessages.ACCESS_TOKEN_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(app_id):
#             raise CustomException(ErrorMessages.APPLICATION_ID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(phone_number_id):
#             raise CustomException(ErrorMessages.PHONE_NUMBER_ID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#
#         profile_picture = profile_details.get("profilePicture")
#         description = profile_details.get("businessDescription")
#         file_name = profile_picture.get("fileName")
#         file_length = profile_picture.get("fileLength")
#         file_type = profile_picture.get("fileType")
#         binary_picture = profile_picture.get("picture")
#         data1 = {
#             'app_id': app_id,
#             'file_name': file_name,
#             'file_length':file_length,
#             'file_type':file_type,
#             'access_token': access_token,
#             'binary_picture':binary_picture
#         }
#
#         url = constants.PROFILE_UPDATION_URL.format(phone_number_id = phone_number_id)
#
#         payload = {
#             'messaging_product': constants.WHATSAPP,
#             'description': description,
#             'profile_picture_handle': self.get_profile_picture_handle(data1)
#         }
#         # Make the request to the Meta API
#         response = requests.post(
#             url,
#             headers={
#                 'Authorization': f'Bearer {access_token}',
#                 'Content-Type': 'application/json'
#             },
#             json=payload
#         )
#         logger.info(response.json())
#         return response.status_code
#
#
#     @action(detail=False, methods=['get'])
#     def get_whatsapp_business_profile(self, request):
#         access_token = request.query_params.get("apiKey")
#         phone_number_id = request.query_params.get("phoneNumberId")
#         if not validate_input(access_token):
#             raise CustomException(ErrorMessages.ACCESS_TOKEN_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(phone_number_id):
#             raise CustomException(ErrorMessages.PHONE_NUMBER_ID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#
#         url = constants.PROFILE_UPDATION_URL.format(phone_number_id=phone_number_id)
#
#         params = {
#             'fields': 'description,profile_picture_url',
#             'access_token': access_token
#         }
#
#         response = requests.get(url, params=params)
#
#
#         if response.status_code == 200:
#             return CustomResponse(response.json())
#         else:
#             error_data = response.json()
#             error_code = error_data.get('error', {}).get('code')
#             if error_code == 190:
#                 raise CustomException(ErrorMessages.INVALID_ACCESS_TOKEN,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 100:
#                 raise CustomException(ErrorMessages.INVALID_PHONE_NUMBER_ID,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 200:
#                 raise CustomException(ErrorMessages.PERMISSION_ERROR,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             else:
#                 logger.info(error_data)
#                 raise CustomException(ErrorMessages.UNABLE_TO_FETCH_BUSINESS_PROFILE,
#                                     status_code=response.status_code)
#
#     @action(detail=False, methods=['delete'])
#     def delete_whatsapp_template(self, request):
#         access_token = request.query_params.get("apiKey")
#         template_name = request.query_params.get("templateName")
#         whatsapp_business_account_id = request.query_params.get("businessId")
#         template_id = request.query_params.get("templateUuid")
#         if not validate_input(access_token):
#             raise CustomException(ErrorMessages.ACCESS_TOKEN_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(template_name):
#             raise CustomException(ErrorMessages.TEMPLATE_NAME_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(whatsapp_business_account_id):
#             raise CustomException(ErrorMessages.WHATSAPP_BUSINESS_ACCOUNT_ID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(template_id):
#             raise CustomException(ErrorMessages.TEMPLATE_UUID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#
#         # Construct the URL for the DELETE request
#         url = constants.DELETE_TEMPLATE_URL.format(
#             whatsapp_business_account_id=whatsapp_business_account_id,
#             template_id = template_id,
#             template_name=template_name
#         )
#         headers = {
#             'Authorization': f'Bearer {access_token}'
#         }
#
#         # Make the DELETE request to the Meta Graph API
#         response = requests.delete(url, headers=headers)
#
#         if response.status_code == 200:
#             return CustomResponse(ErrorMessages.TEMPLATE_DELETED_SUCCESSFULLY)
#
#         else:
#             error_data = response.json()
#             error_code = error_data.get('error', {}).get('code')
#             if error_code == 190:
#                 raise CustomException(ErrorMessages.INVALID_ACCESS_TOKEN,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 100:
#                 raise CustomException(ErrorMessages.INVALID_BUSINESS_ID_OR_TEMPLATE_NAME,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             elif error_code == 200:
#                 raise CustomException(ErrorMessages.PERMISSION_ERROR,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#
#             raise CustomException(ErrorMessages.UNABLE_TO_DELETE_TEMPLATE,
#                                   status_code=response.status_code)
