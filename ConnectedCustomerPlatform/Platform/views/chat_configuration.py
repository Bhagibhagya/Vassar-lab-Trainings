# import copy
# import json
# import logging
# import os
# import uuid
# from dataclasses import asdict
# from datetime import datetime
# from PIL import Image
# from io import BytesIO
# from django.db import DatabaseError
# from django.db.models import Q
# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.viewsets import ViewSet
# from rest_framework.decorators import action
#
# from ConnectedCustomerPlatform.exceptions import CustomException
# from DBServices.models import ChatConfiguration
# from Platform.serializers import ChatConfigurationSerializer
# from Platform.utils import validate_input, get_current_timestamp, get_filter_query_set
# from Platform.constant.success_messages import SuccessMessages
# from Platform.dataclass import LandingPageData
#
# from Platform.serializers import TestChatConfigurationSerializer
# from ConnectedCustomerPlatform.responses import CustomResponse
# from Platform.constant import constants
# from Platform.constant.error_messages import ErrorMessages
# from Platform.dataclass import validate_json_landing_page
# from Platform.dataclass import validate_json_intent_page, IntentPageData
# from Platform.views.whatsapp_configuration import WhatsappConfigurationViewSet
# from StorageServices.azure_services import AzureBlobManager
# from django.conf import settings
# # from ConnectedCustomerPlatform.azure_key_vault_config import SecretClientService
#
#
# logger = logging.getLogger(__name__)
#
#
# class ChatConfigurationViewSet(ViewSet):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.azure_blob_manager = AzureBlobManager(connection_string=settings.AZURE_CONNECTION_STRING)
#         self.whatsapp_configuration = WhatsappConfigurationViewSet()
#
#     @swagger_auto_schema(
#         tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
#         operation_description="Get Chat Configuration",
#         manual_parameters=[
#             openapi.Parameter(
#                 'chat_configuration_uuid', openapi.IN_QUERY, description="UUID of the chat configuration",
#                 type=openapi.TYPE_STRING, required=True
#             )],
#         responses={
#             status.HTTP_200_OK: ChatConfigurationSerializer
#         }
#     )
#     @action(detail=False, methods=['get'])
#     def get_chat_configuration(self, request):
#         """
#             Method to get a specific Chat configuration by UUID.
#             Headers:
#                 chat_configuration-uuid (required):  UUID of the chat_configuration,
#             Returns:
#                 Response: JSON response containing the details of the retrieved chat configuration.
#             """
#         logger.info("In views.py :: :: ::  ChatConfigurationViewSet :: :: :: get_chat_configuration ")
#         chat_configuration_provider = request.query_params.get('chat_configuration_provider')
#         application_uuid = request.headers.get("Application-Uuid")
#         customer_uuid = request.headers.get("Customer-Uuid")
#
#         if chat_configuration_provider == constants.WHATSAPP:
#             # client = SecretClientService.get_client()
#             configuration_queryset = ChatConfiguration.objects.filter(application_uuid=application_uuid , customer_uuid = customer_uuid , chat_configuration_provider = constants.WHATSAPP)
#             serializer = ChatConfigurationSerializer(configuration_queryset, many=True)
#             if not serializer.data:
#                 return CustomResponse({})
#             configuration = serializer.data[0]
#             chat_configuration_json = configuration['chat_details_json']
#             # api_key = chat_configuration_json.get("whatsApp",{}).get("apiKey")
#             # chat_configuration_json["whatsApp"]["apiKey"] = client.get_secret(api_key)
#             blob_name = chat_configuration_json.get("profile", {}).get("profilePicture", {}).get("picture")
#
#             if blob_name:
#                 blob_url = self.azure_blob_manager.create_presigned_url(settings.AZURE_CONTAINER, blob_name)
#                 chat_configuration_json["profile"]["profilePicture"]["picture"] = blob_url
#
#         else:
#             chat_configuration_uuid = request.query_params.get('chat_configuration_uuid')
#             if not validate_input(chat_configuration_uuid):
#                 raise CustomException(ErrorMessages.CHAT_CONFIGURATION_UUID_NOT_NULL,
#                                       status_code=status.HTTP_400_BAD_REQUEST)
#             configuration_queryset = ChatConfiguration.objects.filter(chat_configuration_uuid=chat_configuration_uuid)
#
#             serializer = ChatConfigurationSerializer(configuration_queryset, many=True)
#
#             if not serializer.data:
#                 raise CustomException(ErrorMessages.CHAT_CONFIGURATION_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)
#             configuration = serializer.data[0]
#             chat_configuration_json = configuration['chat_details_json']
#
#
#         configuration_object = {
#             'chat_configuration_uuid': configuration['chat_configuration_uuid'],
#             'chat_configuration_name': configuration['chat_configuration_name'] if configuration[
#                 'chat_configuration_name'] else None,
#             'description': configuration['description'] if configuration['description'] else None,
#             'chat_details_json': chat_configuration_json if chat_configuration_json else None,
#             'chat_configuration_provider': configuration['chat_configuration_provider'] if configuration['chat_configuration_provider'] else None,
#             'code': configuration['code'] if configuration['code'] else None,
#             'application_uuid': configuration['application_uuid'] if configuration['application_uuid'] else None,
#             'customer_uuid': configuration['customer_uuid'] if configuration['customer_uuid'] else None,
#             'insert_ts': configuration['insert_ts'] if configuration['insert_ts'] else None,
#             'updated_ts': configuration['updated_ts'] if configuration['updated_ts'] else None,
#             'created_by': configuration['created_by'] if configuration['created_by'] else None,
#             'updated_by': configuration['updated_by'] if configuration['updated_by'] else None,
#             'status': configuration['status'] if configuration['status'] else False,
#             'chat_configuration_type': configuration['chat_configuration_type'] if configuration['chat_configuration_type'] else None,
#             'is_default': configuration['is_default'] if configuration['is_default'] else False,
#         }
#
#         return CustomResponse(configuration_object)
#
#
#
#     @swagger_auto_schema(
#         tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
#         operation_description="Update chat configuration.",
#         request_body=ChatConfigurationSerializer,
#         responses={
#             status.HTTP_200_OK: SuccessMessages.CHAT_CONFIGURATION_UPDATED_SUCCESSFULLY
#         }
#     )
#
#     @action(detail=False, methods=['post'])
#     def update_chat_configuration(self, request):
#         """
#         Method to update an existing Chat configuration.
#         Data from Request:
#             - chat_configuration_type (required): type of chat configuration
#             - chat_configuration_name (required): name of the theme
#             - application_uuid (required): uuid of the application
#             - customer_uuid (required): uuid of the customer
#             - other optional fields: Any other fields you want to update
#         Returns:
#             Response indicating the status of the update operation.
#         """
#         logger.info("In views.py :: :: :: ChatConfigurationViewSet :: :: :: update_chat_configuration ")
#         data = request.data
#         attachment = None
#         if request.FILES:
#             attachment = request.FILES['chat_details_json[profile][profilePicture][picture]']
#         provider = request.query_params.get("provider")
#         if provider == constants.WHATSAPP:
#             data = self.convert_querydict_to_formdata(data)
#         chat_configuration_name = data.get('chat_configuration_name')
#         application_uuid = request.headers.get('Application-Uuid')
#         customer_uuid = request.headers.get('Customer-Uuid')
#         data['application_uuid'] = application_uuid
#         data['customer_uuid'] = customer_uuid
#         serializer = TestChatConfigurationSerializer(data=data)
#
#         if not serializer.is_valid():
#             raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
#
#         chat_configuration_provider = data.get('chat_configuration_provider','web')
#         instance = self.retrieve_or_create_configuration_instance(data)
#
#         chat_configuration_data = ''
#         if chat_configuration_provider == constants.WEB:
#             chat_configuration_data = self.process_web_configuration(data)
#
#         elif chat_configuration_provider == constants.WHATSAPP:
#
#             chat_configuration_data = self.handle_whatsapp_templates(data,instance,attachment)
#
#         chat_configuration_json = chat_configuration_data
#         try:
#             instance.chat_configuration_name = chat_configuration_name
#             instance.chat_details_json = chat_configuration_json
#             instance.updated_ts = get_current_timestamp()
#             instance.updated_by = data.get('updated_by', instance.updated_by)
#             instance.description = data.get('description', instance.description)
#             instance.code = data.get('code', instance.code)
#             instance.save()
#         except DatabaseError as e:
#             logger.error(ErrorMessages.DATABASE_ERROR, e)
#             raise CustomException(ErrorMessages.DATABASE_ERROR, status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)
#         if chat_configuration_provider == constants.WEB:
#             return CustomResponse(SuccessMessages.CHAT_CONFIGURATION_UPDATED_SUCCESSFULLY)
#         elif chat_configuration_provider == constants.WHATSAPP:
#             return CustomResponse(chat_configuration_json)
#
#
#
#     def convert_querydict_to_formdata(self,querydict):
#         form_data = {}
#
#         for key, value in querydict.items():
#             # Handle nested keys, e.g., "chat_details_json[whatsApp][apiKey]"
#             if '[' in key and ']' in key:
#                 keys = key.replace(']', '').split('[')
#                 current_dict = form_data
#
#                 for i in range(len(keys)):
#                     if i == len(keys) - 1:  # Last key
#                         current_dict[keys[i]] = value
#                     else:
#                         if keys[i] not in current_dict:
#                             current_dict[keys[i]] = {}
#                         current_dict = current_dict[keys[i]]
#             else:
#                 form_data[key] = value
#
#         return form_data
#
#
#     def retrieve_or_create_configuration_instance(self, data):
#         chat_configuration_uuid = data.get('chat_configuration_uuid')
#         configuration_queryset = ChatConfiguration.objects.filter(chat_configuration_uuid=chat_configuration_uuid)
#
#         if configuration_queryset.exists():
#             return configuration_queryset.first()
#
#         else:
#             return ChatConfiguration(
#                 chat_configuration_uuid=uuid.uuid4(),
#                 application_uuid=data['application_uuid'],
#                 customer_uuid=data['customer_uuid'],
#                 chat_configuration_type=data.get('chat_configuration_type'),
#                 insert_ts=get_current_timestamp(),
#                 chat_configuration_provider=data.get('chat_configuration_provider','web'),
#                 created_by=data.get('created_by')
#             )
#
#
#     def process_web_configuration(self, data):
#         chat_configuration_type = data.get('chat_configuration_type')
#         chat_configuration_json = data.get('chat_details_json')
#
#         if chat_configuration_type == 'landing_page':
#             try:
#                 landing_page_config = validate_json_landing_page(chat_configuration_json)
#                 return asdict(LandingPageData(landing_page_configuration=landing_page_config))
#             except ValueError as e:
#                 raise CustomException({"detail": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
#         else:
#             try:
#                 intent_page_config = validate_json_intent_page(chat_configuration_json)
#                 return asdict(IntentPageData(intent_page_configuration=intent_page_config))
#             except ValueError as e:
#                 raise CustomException({"detail": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
#
#
#     def handle_whatsapp_templates(self, data,instance,attachment):
#         chat_configuration_data = data.get('chat_details_json')
#         profile_details = chat_configuration_data.get("profile", {})
#         profile_picture = profile_details.get("profilePicture",{})
#         file_type = profile_picture.get('fileType',{})
#         api_key_details = chat_configuration_data.get("whatsApp", {})
#         # api_key = api_key_details.get('apiKey')
#         # business_id = api_key_details.get('businessId')
#         # app_id = api_key_details.get('appId')
#         # Uploading profile picture
#         if attachment:
#             try:
#                 if file_type not in constants.VALID_FILE_TYPE:
#                     raise CustomException(ErrorMessages.INVALID_FILE_TYPE, status_code=status.HTTP_400_BAD_REQUEST)
#                 image = Image.open(BytesIO(attachment.read()))
#                 width, height = image.size
#                 if width < 192 or height < 192:
#                     raise CustomException(ErrorMessages.IMAGE_TOO_SMALL, status_code=status.HTTP_400_BAD_REQUEST)
#             except IOError as e:
#                 raise CustomException(ErrorMessages.INVALID_IMAGE_FORMAT, status_code=status.HTTP_400_BAD_REQUEST)
#             attachment.seek(0)
#             response_status = self.whatsapp_configuration.update_profile_picture(profile_details, api_key_details)
#             if response_status == 200:
#                 attachment.seek(0)
#                 blob_name = self.azure_blob_manager.create_blob_name(
#                     project=constants.PROJECT_NAME,
#                     organization_uuid=data['customer_uuid'],
#                     application_uuid=data['application_uuid'],
#                     channel_type=constants.CHAT_CHANNEL,
#                     folder_type=constants.WHATSAPP_PROFILE_IMAGE,
#                     attachment_uuid=str(uuid.uuid4())
#                 )
#                 self.azure_blob_manager.upload_attachments(attachment, container_name=AZURE_CONTAINER,
#                                                            blob_name=blob_name)
#                 profile_details['profilePicture']['picture'] = blob_name
#                 chat_configuration_data['profile'] = profile_details
#             else:
#                 raise CustomException(ErrorMessages.UNABLE_TO_UPDATE_PROFILE, status_code=status.HTTP_400_BAD_REQUEST)
#
#         welcome_message = chat_configuration_data.get("welcomeMessage")
#         database_templates = []
#         if instance.chat_details_json:
#             database_templates = instance.chat_details_json.get('templates', [])
#         updated_templates = []
#
#         templates_data = chat_configuration_data.get('templates', {})
#         active_template_count = 0
#         for key, template in templates_data.items():
#             template['active'] = self.convert_to_bool(template.get('active', 'false'))
#             for message_key, message in template.get('messages', {}).items():
#                 message['isEditable'] = self.convert_to_bool(message.get('isEditable', 'false'))
#             if template['active']:
#                 active_template_count += 1
#                 if active_template_count > 1:
#                     raise CustomException(ErrorMessages.MORE_THAN_ONE_TEMPLATE_CANNOT_BE_ACTIVE,
#                                           status_code=status.HTTP_400_BAD_REQUEST)
#         if active_template_count == 0:
#             raise CustomException(ErrorMessages.ONE_TEMPLATE_SHOULD_BE_ACTIVE, status_code=status.HTTP_400_BAD_REQUEST)
#
#         for key, template in templates_data.items():
#             template_uuid = template.get('templateUUID',"")
#             existing_template = None
#             if template_uuid:
#                 existing_template = next((t for t in database_templates if t.get('templateUUID') == template_uuid), None)
#             if existing_template :
#                 # Template exists and not changed
#                 if existing_template == template:
#                     updated_templates.append(template)
#                 else:
#                     #Template exists and modified
#                     updated_template = self.update_existing_template(existing_template, template, api_key_details,
#                                                                 welcome_message)
#                     updated_templates.append(updated_template)
#             else:
#                 template_name = template.get('templateName', "")
#                 template_duplication = next(
#                     (t for t in database_templates if t.get('templateName') == template_name), None)
#                 if template_duplication:
#                     raise CustomException(ErrorMessages.TEMPLATE_NAME_ALREADY_EXISTS.format(template_name = template_name),status_code = status.HTTP_400_BAD_REQUEST)
#                 # Creating new template
#                 new_template = self.create_new_template(template, api_key_details, welcome_message)
#                 updated_templates.append(new_template)
#         # client = SecretClientService.get_client()
#         # api_key_name =constants.API_KEY+'_'+business_id+'_'+app_id
#         # client.set_secret(api_key_name,api_key)
#         # chat_configuration_data['whatsApp']['apiKey'] = api_key_name
#         chat_configuration_data['templates'] = updated_templates
#         return chat_configuration_data
#
#     def convert_to_bool(self,value: str) -> bool:
#         """
#         Converts string 'true'/'false' to boolean True/False.
#         """
#         return value.lower() == 'true'
#
#
#     def update_existing_template(self,existing_template, template, api_key_details, welcome_message):
#         """Update an existing template and return the updated template."""
#         response = self.whatsapp_configuration.edit_intents_template(existing_template, template, api_key_details,
#                                                                 welcome_message)
#         if response.status_code == 200:
#             logger.info(response.json())
#             current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
#             template['lastEditTime'] = current_time
#             template['templateStatus'] = constants.APPROVED
#             return template
#         else:
#             logger.info(response.json())
#             raise CustomException(ErrorMessages.CANNOT_EDIT_TEMPLATE, status_code=status.HTTP_400_BAD_REQUEST)
#
#     def create_new_template(self,template, api_key_details, welcome_message):
#         """Create a new template and return the created template."""
#         response = self.whatsapp_configuration.create_intents_template(welcome_message, template, api_key_details)
#         if response.status_code == 200:
#             logger.info(response.json())
#             response_data = response.json()
#             template['templateUUID'] = response_data.get("id")
#             template['templateStatus'] = response_data.get("status")
#             return template
#         else:
#             logger.info(response.json())
#             raise CustomException(ErrorMessages.CANNOT_CREATE_TEMPLATE, status_code=status.HTTP_400_BAD_REQUEST)
#
#
#
#
#     @swagger_auto_schema(
#             tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
#             operation_description="Get All Chat Configuration",
#             manual_parameters=[
#                 openapi.Parameter(
#                     'Application-Uuid', openapi.IN_HEADER, description="UUID of the application", type=openapi.TYPE_STRING,
#                     required=True
#                 ),
#                 openapi.Parameter(
#                     'Customer-Uuid', openapi.IN_HEADER, description="UUID of the customer", type=openapi.TYPE_STRING,
#                     required=True
#                 )],
#             responses={
#                 status.HTTP_200_OK: openapi.Response(
#                     description="Successful response",
#                     schema=openapi.Schema(
#                         type=openapi.TYPE_ARRAY,
#                         items=openapi.Schema(
#                             type=openapi.TYPE_OBJECT,
#                             properties={
#                                 'chat_configuration_uuid': openapi.Schema(type=openapi.TYPE_STRING),
#                                 'chat_configuration_name': openapi.Schema(type=openapi.TYPE_STRING),
#                                 'status': openapi.Schema(type=openapi.TYPE_BOOLEAN)
#                             })))
#             }
#         )
#     @action(detail=False, method='get')
#     def get_all_chat_configurations(self,request):
#         """
#             Method to retrieve all chat configurations for a specific application and customer.
#             Query Parameters:
#                 chat_configuration_type : type of chat configuration to filter by.
#             Headers:
#                 Application-Uuid: UUID of the application.
#                 Customer-Uuid: UUID of the customer.
#             Returns:
#                 CustomResponse: A list of chat configurations.
#             """
#         logger.info("In views.py :: :: ::  ChatConfigurationViewSet :: :: :: get_all_chat_configurations ")
#         application_uuid = request.headers.get('Application-Uuid')
#         customer_uuid = request.headers.get('Customer-Uuid')
#         chat_configuration_type = request.query_params.get('chat_configuration_type')
#
#         chat_configurations = ChatConfiguration.objects.filter(
#             Q(application_uuid=application_uuid, customer_uuid=customer_uuid) |
#             Q(is_default=True)
#         ).order_by('-updated_ts')
#
#         serializer = ChatConfigurationSerializer(chat_configurations, many=True)
#         serialized_data = serializer.data
#
#         default_themes = []
#         other_themes = []
#
#         for data in serialized_data:
#             if data['chat_configuration_provider'] == constants.WEB:
#                 read_only = data.get('is_default')
#                 if data['chat_configuration_type'] == chat_configuration_type:
#                     item = {
#                         "chat_configuration_uuid": data.get("chat_configuration_uuid", ""),
#                         "chat_configuration_name": data.get("chat_configuration_name", ""),
#                         "status": data.get("status", False),
#                         "read_only": read_only
#                     }
#
#                     chat_details_json = data.get("chat_details_json", {})
#
#                     configuration = (chat_details_json.get("landing_page_configuration", {})
#                                      .get("home_screen_configuration", {})
#                                      if chat_configuration_type == "landing_page"
#                                      else chat_details_json.get("intent_page_configuration", {}).get("intent_page_panel_configuration", {}).get("header", {}))
#
#                     item["background_fill_type"] = configuration.get("background_fill_type")
#                     item["background_color"] = configuration.get("background_color")
#                     if read_only:
#                         default_themes.append(item)
#                     else:
#                         other_themes.append(item)
#
#         template_data = default_themes + other_themes
#         return CustomResponse(template_data)
#
#
#
#
#
#     @swagger_auto_schema(
#         tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
#         operation_description="Update Activation Status.",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'chat_configuration_uuid': openapi.Schema(
#                     type=openapi.TYPE_STRING,
#                     description='UUID of the chat configuration to update'
#                 )
#             },
#             required=['chat_configuration_uuid']
#         ),
#         responses={
#             status.HTTP_200_OK: SuccessMessages.CHAT_CONFIGURATION_STATUS_UPDATED_SUCCESSFULLY,
#             status.HTTP_400_BAD_REQUEST: ErrorMessages.SAVE_CONFIGURATION_BEFORE_PUBLISHING
#         }
#     )
#     @action(detail=False, method='post')
#     def update_activation_status(self,request):
#         """
#             Method to update the activation status of a specific chat configuration.
#             Data from Request:
#                 - chat_configuration_uuid (required): UUID of the chat configuration to activate.
#                 - chat_configuration_type (required): Type of the chat configuration.
#             Headers:
#                 - Application-Uuid: UUID of the application.
#                 - Customer-Uuid: UUID of the customer.
#             Returns:
#                 CustomResponse: Success message if the activation status is updated successfully.
#             """
#         logger.info("In views.py :: :: ::  ChatConfigurationViewSet :: :: :: get_all_chat_configurations ")
#         data = request.data
#         chat_configuration_uuid = data.get('chat_configuration_uuid')
#         chat_configuration_type = data.get('chat_configuration_type')
#         application_uuid = request.headers.get('Application-Uuid')
#         customer_uuid = request.headers.get('Customer-Uuid')
#         if not validate_input(chat_configuration_uuid):
#             raise CustomException(ErrorMessages.CHAT_CONFIGURATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(chat_configuration_type):
#             raise CustomException(ErrorMessages.CHAT_CONFIGURATION_TYPE_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
#         configuration_queryset = ChatConfiguration.objects.filter(chat_configuration_uuid=chat_configuration_uuid)
#         if configuration_queryset.exists():
#             instance = configuration_queryset.first()
#             instance.status = True
#             instance.save()
#             conditions = (
#                     Q(application_uuid=application_uuid, customer_uuid=customer_uuid,
#                       chat_configuration_type=chat_configuration_type) |
#                     Q(is_default=True,chat_configuration_type=chat_configuration_type)
#             )
#             ChatConfiguration.objects.filter(conditions).exclude(
#                 chat_configuration_uuid=chat_configuration_uuid
#             ).update(status=False)
#             return CustomResponse(SuccessMessages.CHAT_CONFIGURATION_STATUS_UPDATED_SUCCESSFULLY)
#         else:
#             raise CustomException(ErrorMessages.SAVE_CONFIGURATION_BEFORE_PUBLISHING, status_code=status.HTTP_400_BAD_REQUEST)
#
#
#
#     @swagger_auto_schema(
#         tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
#         operation_description="Delete a specific Chat configuration by UUID",
#         manual_parameters=[
#             openapi.Parameter(
#                 'chat_configuration_uuid', openapi.IN_QUERY, description="UUID of the chat configuration", type=openapi.TYPE_STRING,
#                 required=True
#             )
#          ],
#         responses={
#                       status.HTTP_200_OK: SuccessMessages.CHAT_CONFIGURATION_DELETED_SUCCESSFULLY,
#                       status.HTTP_400_BAD_REQUEST: ErrorMessages.CHAT_CONFIGURATION_NOT_FOUND
#                   }
#     )
#
#     @action(detail=False, methods=['delete'])
#     def delete_chat_configuration(self, request):
#         """
#             Method to delete a specific Chat configuration by UUID.
#             Query Parameters:
#                 chat_configuration_uuid (required):  UUID of the chat configuration to delete.
#             Returns:
#                 Response: HTTP 204 No Content if deletion is successful,
#                           HTTP 400 Bad Request if UUID is invalid or configuration not found.
#         """
#         logger.info("In views.py :: :: ::  ChatConfigurationViewSet :: :: :: delete_chat_configuration ")
#         chat_configuration_uuid = request.query_params.get('chat_configuration_uuid')
#         if not validate_input(chat_configuration_uuid):
#             raise CustomException(ErrorMessages.CHAT_CONFIGURATION_UUID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
#
#         configuration_queryset = ChatConfiguration.objects.filter(chat_configuration_uuid=chat_configuration_uuid)
#
#         if configuration_queryset.exists():
#             configuration = configuration_queryset.first()
#             serializer = ChatConfigurationSerializer(configuration)
#             data = serializer.data
#             if(data['is_default']):
#                 return CustomException(ErrorMessages.CANNOT_DELETE_DEFAULT_TEMPLATE,status_code=status.HTTP_404_NOT_FOUND)
#             else:
#                 configuration.delete()
#                 return CustomResponse(SuccessMessages.CHAT_CONFIGURATION_DELETED_SUCCESSFULLY)
#         else:
#             raise CustomException(ErrorMessages.CHAT_CONFIGURATION_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)
#
#
#
#     @swagger_auto_schema(
#         tags=constants.CHAT_CONFIGURATION_TEMPLATE_TAG,
#         operation_description="Get active Chat configurations by application UUID and customer UUID",
#         manual_parameters=[
#             openapi.Parameter(
#                 'application_uuid', openapi.IN_QUERY, description="UUID of the application", type=openapi.TYPE_STRING,
#                 required=True
#             ),
#             openapi.Parameter(
#                 'customer_uuid', openapi.IN_QUERY, description="UUID of the customer", type=openapi.TYPE_STRING,
#                 required=True
#             )
#         ],
#         responses={
#             status.HTTP_200_OK: openapi.Response(
#                 description="Successful response",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'chat_details_json': openapi.Schema(type=openapi.TYPE_OBJECT)
#                     }
#                 )
#             ),
#             status.HTTP_400_BAD_REQUEST: openapi.Response(description="Invalid input or missing UUIDs")
#         }
#     )
#     @action(detail=False, methods=['get'])
#     def get_active_chat_configurations(self, request):
#         """
#                     Method to get active Chat configuration.
#                     Query Parameters:
#                         application_uuid (required):  UUID of the application.
#                         customer_uuid (required): UUID of the customer
#                     Returns:
#                         Response: Active chat configurations.
#
#                 """
#         logger.info("In views.py :: :: ::  ChatConfigurationViewSet :: :: :: get_active_chat_configurations ")
#         application_uuid = request.headers.get('Application-Uuid')
#         customer_uuid = request.headers.get('Customer-Uuid')
#         if not validate_input(application_uuid):
#             raise CustomException(ErrorMessages.APPLICATION_UUID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         if not validate_input(customer_uuid):
#             raise CustomException(ErrorMessages.CUSTOMER_UUID_NOT_NULL,
#                                   status_code=status.HTTP_400_BAD_REQUEST)
#         configuration_queryset = ChatConfiguration.objects.filter(
#             Q(application_uuid=application_uuid, customer_uuid=customer_uuid) | Q(is_default=True),
#             status=True
#         )
#         active_configurations = {}
#         if configuration_queryset.exists():
#             for configuration in configuration_queryset:
#                 chat_details_json = configuration.chat_details_json
#                 active_configurations.update(chat_details_json)
#         result = {"chat_details_json": active_configurations}
#         return CustomResponse(result)
#
