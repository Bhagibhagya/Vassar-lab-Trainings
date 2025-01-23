from django.http import HttpResponse
from rest_framework.fields import BooleanField
from ConnectedCustomerPlatform.exceptions import CustomException,ResourceNotFoundException,InvalidValueProvidedException
import json

from AIServices.BOT.LLMChain import LLMChain
from AIServices.prompts import Utterances_prompt
from ConnectedCustomerPlatform.exceptions import CustomException, InvalidValueProvidedException
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
import logging

from EmailApp.constant.success_messages import PersonalizationSuccessMessages, SuccessMessages
from EmailApp.constant.constants import BULK_IMPORT_EXCEL_FILE, EXCEL_CONTENT_TYPE, SPREAD_SHEET_CONTENT_TYPE, \
    ChromadbMetaDataParams, DimensionTypeNames, FileExtensions, UtterancesGeneratorParams, SPREAD_SHEET_MACRO_ENABLED
from EmailApp.utils import validate_input, validate_uuids_dict
from ConnectedCustomerPlatform.responses import CustomResponse
from rest_framework import status


from Platform.constant import constants
from Platform.constant.constants import FALSE
from Platform.constant.error_messages import ErrorMessages as PlatformErrorMessages
from Platform.utils import paginate_queryset

from EmailApp.constant.constants import EmailDashboardParams,CsrChromaDbFields
from EmailApp.utils import validate_input
from EmailApp.constant.error_messages import ErrorMessages, PersonalizationErrorMessages
from EmailApp.serializers import ResponseConfigurationRequestPayloadSerializer, PaginationParamsSerializer
from EmailApp.services.impl.personalization_service_impl import PersonalizationServiceImpl
from EmailApp.constant.swagger_constants import ChromaDBSwaggerParams
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


logger = logging.getLogger(__name__)
class PersonalizationViewset(ViewSet):    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PersonalizationViewset, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print(f"Inside EmailConversationViewSet - Singleton Instance ID: {id(self)}")
            self.personalization_service = PersonalizationServiceImpl()
            self.initialized = True

    @swagger_auto_schema(
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER,
            ChromaDBSwaggerParams.RESPONSE_CONFIG_UUID_QUERY
        ],
        request_body=None,
        responses={
            200: "Deletion Successful",
            400: "Invalid input provided",
            500: "Internal server error",
        },
        operation_description="Delete emails based on response config",
    )

    @action(detail=False, methods=['delete'])
    def delete_response_configurations(self, request):
        """
        Takes request which contain response_config_uuid deletes the specific response_configuration
        """
        logger.info("In PersonalizationViewset: delete_response_configurations ")

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        response_config_uuid=request.query_params.get(CsrChromaDbFields.RESPONSE_CONFIG_UUID.value)

        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid,CsrChromaDbFields.RESPONSE_CONFIG_UUID.value:response_config_uuid})

        deleted_ids = self.personalization_service.delete_response_configurations(customer_uuid,application_uuid,response_config_uuid)
        if not deleted_ids:
            raise ResourceNotFoundException(PersonalizationErrorMessages.RESPONSE_CONFIG_NOT_PRESENT, status_code=status.HTTP_404_NOT_FOUND)
        logger.debug(f"Deleted documents with ids-{deleted_ids}")
        return CustomResponse(result=PersonalizationSuccessMessages.RESPONSE_RECORD_DELETED,code=status.HTTP_200_OK)



    @swagger_auto_schema(
            operation_description="Fetch intents and its asscoiated sub-intents, and sentiment",
            responses={
                200: openapi.Response('Successful Response',expected_data = {
                                            'intent_subintent': {
                                                'PURCHASE_ORDER': ['NEW_PO', 'CHECK_PO_STATUS'],
                                                'SHIPMENT_STATUS': ['CHECK_SHIPMENT_STATUS']
                                            },
                                            'sentiment': ['Positive', 'Negative']
                                        }),
                400: 'Bad Request',
            },
            manual_parameters=[
                ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
                ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
                ChromaDBSwaggerParams.USER_UUID_HEADER]
        )
    @action(detail=False, methods=['get'])
    def fetch_intents_subintents_sentiment(self, request):
        """
        fetches intents with its subintents and sentiments for given customer and application

        response format:
        {'intent_subintent':{intent1:[subintent1,subintent2]}
        'sentiment':[sentiment1,sentiment2]}
        """
        logger.info("In PersonalizationViewset : fetch_intents_subintents_sentiment")

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)

        validate_uuids_dict({EmailDashboardParams.USER_UUID.value:user_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid,EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid})
        # Check if sentiments should be included (default: False)
        include_sentiments = request.query_params.get('include_sentiments', 'false').lower() == 'true'

        intents_subintents_sentiments_data = self.personalization_service.fetch_intents_subintents_sentiment(customer_uuid,application_uuid,include_sentiments)

        return CustomResponse(result=intents_subintents_sentiments_data,code=status.HTTP_200_OK)


    @action(detail=False, methods=['get'])
    def fetch_response_configurations(self,request):
        """
        Fetch the saved response configuration (metadata_combination and excel file url)
        if is_default is True fetch configurations of csr_Admin
        else: fetch configurations uploaded by the csr user
        """
        logger.info("In :: PersonalizationViewset :: fetch_response_configurations")
        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)

        validate_uuids_dict({EmailDashboardParams.USER_UUID.value:user_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid,EmailDashboardParams.CUSTOMER_UUID:customer_uuid})

        #For identifying whether user is admin or csr_user
        is_default=request.query_params.get(CsrChromaDbFields.IS_DEFAULT.value)  
        
        if is_default is None:
            raise InvalidValueProvidedException(ErrorMessages.IS_DEFAULT_IS_NONE)
        
        # convert is_default to boolean
        try:
            is_default= BooleanField().to_internal_value(is_default)
        except Exception as e:
            raise InvalidValueProvidedException(ErrorMessages.IS_DEFAULT_SHOULD_BE_BOOLEAN) 
        
        response_configurations_data=self.personalization_service.fetch_response_configurations(customer_uuid,application_uuid,user_uuid,is_default)
        return CustomResponse(result=response_configurations_data,code=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create presigned url for default template",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful response with the downloaded template data.",
                examples={
                    "application/json": {
                        "result": {
                                "downloadable_url": "https://vassarstorage.blob.core.windows.net/connected-enterprise/connected_enterprise/sensormatic/email/2024/September/2024-09-19/Attachments/773e01d5-a4ad-4c4f-a8aa-29c4d3742414_order_status_RS.xlsx?se=2024-10-04T07%3A08%3A47Z&sp=r&sv=2024-08-04&sr=b&sig=q3ZlAKI7MVDdO32g1B1ZGd%2B1g6Fwn8W/NRUcCNRR5Jk%3D",
                                "filename": "order_status_RS.xlsx"
                            },
                    }
                }
            ),
             status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Error occured"
            )     
        }
    )
    @action(detail=False, methods=['get'])
    def download_template(self,request):    
        """
        Downloads the default template which is stored in azure and the url is stored in settings
        """     
        default_template_data=self.personalization_service.download_template()
        return CustomResponse(result=default_template_data,code=status.HTTP_200_OK)


    @swagger_auto_schema(
        method='delete',
        operation_description="Delete an utterance from the Chroma server.",
        manual_parameters=[
            openapi.Parameter(
                UtterancesGeneratorParams.ID.value,
                openapi.IN_QUERY,
                description="The ID of the utterance to delete",
                type=openapi.TYPE_STRING,
                required=True
            ),
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER
        ],
        responses={
            200: openapi.Response('Success', openapi.Schema(type=openapi.TYPE_STRING,
                                                            description="Utterance successfully deleted")),
            400: openapi.Response('Validation Error',
                                  openapi.Schema(type=openapi.TYPE_OBJECT, description="Invalid input data")),
            500: openapi.Response('Server Error',
                                  openapi.Schema(type=openapi.TYPE_STRING, description="Internal server error")),
        }
    )


    @action(detail=False, methods=['delete'])
    def delete_utterance(self, request):
        """
        API for deleting the utterance of a specific intent
        :param request: The HTTP request containing customer_uuid, application_uuid and utterance_uuid
        :return: success message on successful deletion in chroma DB
        """
        logger.info('Inside PersonalizationViewset :: delete_utterance')
        

        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        utterance_uuid = request.query_params.get(UtterancesGeneratorParams.ID.value)
        mapping_uuid = request.data.get(ChromadbMetaDataParams.MAPPING_UUID.value)
        dimension_name = request.data.get('dimension_name')
        parent_dimension_name = request.data.get('parent_dimension_name', None)

        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid,UtterancesGeneratorParams.ID.value:utterance_uuid})
        self.personalization_service.delete_utterance_from_chroma_server(customer_uuid=customer_uuid,application_uuid=application_uuid,utterance_id=utterance_uuid,mapping_uuid=mapping_uuid,parent_dimension_name=parent_dimension_name,child_dimension_names=dimension_name)
        return CustomResponse(result=SuccessMessages.UTTERANCE_SUCCESSFULLY_DELETED)

    #TODO it will be deprecated so no need to refactor
    @action(detail=False, methods=['post'])
    def generate_utterances(self,request):
        data=request.data
        intent=data.get(UtterancesGeneratorParams.INTENT.value,'')
        description=data.get(UtterancesGeneratorParams.DESCRIPTION.value,'')
        if not validate_input(intent):
            raise InvalidValueProvidedException(PlatformErrorMessages.INTENT_SHOULD_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        llm_chain = LLMChain(prompt=Utterances_prompt)
        try:
            response = llm_chain.query(
                inputs={'intent': {intent},'description':description})
            response_data = json.loads(response)
            logger.debug(f"LLM response : {response_data}")
            return CustomResponse(result=response_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {e}")
            raise CustomException(ErrorMessages.ERROR_IN_GENERATING_UTTERANCES, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An error occurred while querying the LLM: {e}")
            raise CustomException(ErrorMessages.ERROR_IN_GENERATING_UTTERANCES, status_code=status.HTTP_400_BAD_REQUEST)
    

    @swagger_auto_schema(
        method='post',
        operation_description="Upload Excel file and save response configurations.",
        request_body=ResponseConfigurationRequestPayloadSerializer,
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER],
        responses={
            200: openapi.Response('Success', openapi.Schema(type=openapi.TYPE_STRING)),
            400: openapi.Response('Validation Error', openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response('Server Error', openapi.Schema(type=openapi.TYPE_STRING)),
        }
    )
    
    @action(detail=False, methods=['post'])
    def save_response_configurations(self, request):
        """
        Handle saving of response configurations from an uploaded Excel file.
    
        :param request: The incoming HTTP request containing request data and excel file and headers.
        :return: A custom response indicating success or failure.
        
        """
        
        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)

        validate_uuids_dict({EmailDashboardParams.USER_UUID.value:user_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid,EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid})

        serializer = ResponseConfigurationRequestPayloadSerializer(data=request.data)
           
        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            raise InvalidValueProvidedException(detail=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        #Get the Excel file from request Multipart
        example_responses_excel_file = request.FILES.get(CsrChromaDbFields.RESPONSES_FILE.value)
        
        # Read the file content as byte array
        byte_array_of_excel = example_responses_excel_file.read()
        
        logger.info(f"Received request to save response configurations for user {user_uuid}")

        #build the data in the below format since upload to azure expects below format
        example_responses_excel_data={"filename":example_responses_excel_file.name,"content_type":example_responses_excel_file.content_type,"data":byte_array_of_excel}

        self.personalization_service.save_response_configurations(customer_uuid,application_uuid,user_uuid,example_responses_excel_data,serializer.validated_data)
    
        logger.info("Successfully saved response configurations")
        return CustomResponse(result=PersonalizationSuccessMessages.UPLOADED_RESPONSES_AS_EXAMPLES,code=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        operation_description="Retrieve utterances associated with a specific intent for a given customer and application.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'intent_uuid': openapi.Schema(type=openapi.TYPE_STRING, description="UUID of the intent"),
                'params': openapi.Schema(type=openapi.TYPE_OBJECT, description="Pagination and filter parameters")
            },
            required=['intent_uuid']
        ),
        manual_parameters=[
            ChromaDBSwaggerParams.CUSTOMER_UUID_HEADER,
            ChromaDBSwaggerParams.APPLICATION_UUID_HEADER,
            ChromaDBSwaggerParams.USER_UUID_HEADER,
        ],
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "result": [
                            {"utterance": "Hello, how can I help you?", "intent_uuid": "example-uuid"},
                            {"utterance": "Goodbye!", "intent_uuid": "example-uuid"}
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="Validation Error",
                examples={
                    "application/json": {
                        "error": "Customer UUID should not be null"
                    }
                }
            ),
            500: openapi.Response(
                description="Server Error",
                examples={
                    "application/json": {
                        "error": "Internal server error"
                    }
                }
            )
        })
        
    @action(detail=False, methods=['post'])
    def get_utterances_by_dimension(self, request):
        """
        retrieves utterances associated with a specific intent for a given customer and application.

        :param request: The HTTP request containing customer_uuid, application_uuid,user_uuid,intent_uuid and pagination details.
        :return: A paginated list of utterances corresponding to the specified intent.

        """


        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        dimension_names = request.data.get(ChromadbMetaDataParams.DIMENSION_NAMES.value,)
        parent_dimension_name= request.data.get(ChromadbMetaDataParams.PARENT_DIMENSION_NAME.value,None)
        validate_uuids_dict({EmailDashboardParams.CUSTOMER_UUID.value:customer_uuid,EmailDashboardParams.APPLICATION_UUID.value:application_uuid,EmailDashboardParams.USER_UUID.value:user_uuid})
        dimension_names=dimension_names or []

        # Validate request body using the serializer
        pagination_serializer = PaginationParamsSerializer(data=request.data.get(ChromadbMetaDataParams.PARAMS.value))

        if not pagination_serializer.is_valid():
            raise CustomException(pagination_serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        #fetch utterances list for the given intent with applied pagination
        utterances_response = self.personalization_service.fetch_dimension_utterances_for_customer_application(params=pagination_serializer.validated_data, customer_uuid=customer_uuid, application_uuid=application_uuid,user_uuid=user_uuid,dimension_names=dimension_names,parent_dimension_name=parent_dimension_name)
        return CustomResponse(result=utterances_response,status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def download_intents_with_training_phrases(self, request):
        """
        Generates an Excel file containing intents as separate sheets, 
        with each sheet listing training phrases and their corresponding descriptions.

        :param customer_uuid: UUID of the customer for which intents are to be fetched.
        :param application_uuid: UUID of the application associated with the intents.
        :param user_uuid: UUID of the user requesting the download.
        :return: An HTTP response containing the generated Excel file as a byte stream.
        """
        try:
            customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
            application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
            user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
            
            # Validate UUIDs
            validate_uuids_dict({
                EmailDashboardParams.CUSTOMER_UUID.value: customer_uuid,
                EmailDashboardParams.APPLICATION_UUID.value: application_uuid,
                EmailDashboardParams.USER_UUID.value: user_uuid
            })

            # Get the Excel byte array response from the service
            response_data = self.personalization_service.download_intents_with_training_phrases(
                customer_uuid=customer_uuid, application_uuid=application_uuid, user_uuid=user_uuid,Dimension_type_name=DimensionTypeNames.INTENT.value)

            if response_data is None:
                return CustomResponse("Failed to generate the Excel file", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


            return response_data

        except Exception as e:
            logger.error(f"Error while downloading intents with training phrases: {str(e)}")
            return CustomResponse(f"Error while downloading intents with training phrases: {str(e)}", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    @action(detail=False, methods=['post'])
    def bulk_import_training_phrases(self,request):
        #TODO instead ofdeleting each entry/intent from chromadb, delete all at a time
        """
        API to upload an Excel file and save the training phrases in ChromaDB directly from memory.

        :param request: HTTP request with the Excel file in multipart/form-data format.
        :param customer_uuid: UUID of the customer for whom the intents and phrases are being uploaded.
        :param application_uuid: UUID of the application.
        :param user_uuid: UUID of the user uploading the file.
        :return: Response indicating success or failure.
        """
        if BULK_IMPORT_EXCEL_FILE not in request.FILES:
            raise InvalidValueProvidedException(f"Cannot find file with key {BULK_IMPORT_EXCEL_FILE}", status_code=400)

        # Get the uploaded file from the request
        excel_file_obj = request.FILES[BULK_IMPORT_EXCEL_FILE]
        #check weather the file type is excel or not
        if not (excel_file_obj.content_type in [SPREAD_SHEET_CONTENT_TYPE, EXCEL_CONTENT_TYPE] and excel_file_obj.name.endswith((FileExtensions.XLSX.value, FileExtensions.XLS.value))):
            logger.error(f"Invalid file format. Expecting a .xlsx or .xlsm format.")
            raise InvalidValueProvidedException("Provided file is not an excel file.Please give valid excel file")
        
        # Get uuids from headers
        customer_uuid = request.headers.get(EmailDashboardParams.CUSTOMER_UUID.value)
        application_uuid = request.headers.get(EmailDashboardParams.APPLICATION_UUID.value)
        user_uuid = request.headers.get(EmailDashboardParams.USER_UUID.value)
        
        # Validate UUIDs
        validate_uuids_dict({
            EmailDashboardParams.CUSTOMER_UUID.value: customer_uuid,
            EmailDashboardParams.APPLICATION_UUID.value: application_uuid,
            EmailDashboardParams.USER_UUID.value: user_uuid
        })

        return self.personalization_service.bulk_import_training_phrases(excel_file_obj=excel_file_obj,
                customer_uuid=customer_uuid, application_uuid=application_uuid, user_uuid=user_uuid)


