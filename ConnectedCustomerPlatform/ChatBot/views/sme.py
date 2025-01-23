from ChatBot.services.impl.sme_service_impl import SMEServiceImpl
from ChatBot.services.interface.sme_service_interface import ISMEService
from Platform.constant import constants

from ChatBot.constant.success_messages import SuccessMessages
from ChatBot.constant.error_messages import ErrorMessages
from ChatBot.serializers import AddQuestionSerializer, UpdateAnswerSerializer, ListQuestionsSerializer, VerifyAnswerSerializer, FeedbackSerializer, GenerateQASerializer, RelevantChunksRequestSerializer, ReferenceChunkSerializer, NeighbouringChunkSerializer
from ConnectedCustomerPlatform.exceptions import CustomException, UnauthorizedByScopeException

from ConnectedCustomerPlatform.responses import CustomResponse
from Platform.utils import get_headers
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, JSONParser
import logging
logger = logging.getLogger(__name__)


class SMEViewSet(ViewSet):
    """
    A view set that handles the management of questions and answers.
    Uses SMEServiceImpl to interact with business logic.
    Supports actions like adding, updating, and deleting drafts/questions/answers.
    """

    parser_classes = (JSONParser, MultiPartParser)

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensures that the SMEViewSet class is a singleton."""
        if cls._instance is None:
            cls._instance = super(SMEViewSet, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """Initializes the SMEViewSet and the SME service instance."""
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            self.initialized = True
            self.__sme_service: ISMEService = SMEServiceImpl()
            logger.info("SMEServiceImpl instance initialized.")

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name='feedback', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Feedback'),
                           constants.application_uuid_header,
                           constants.customer_uuid_header],
        responses={status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=['get'])
    def get_questions(self, request):
        """
        Retrieves a list of questions based on the query parameters.
        """
        customer_uuid, application_uuid, _ = get_headers(request.headers)
        entity_ids_list = self.__sme_service.get_entity_ids_from_request(request)
        logger.debug("Processing request to get questions.")
        serializer = ListQuestionsSerializer(data=request.query_params)
        if not serializer.is_valid(raise_exception=True):
            logger.error("Invalid query parameters for getting questions.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        response = self.__sme_service.get_questions(data, customer_uuid, application_uuid, entity_ids_list)
        logger.debug("Successfully retrieved questions.")
        return CustomResponse(result=response)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name='question_uuid', in_=openapi.IN_PATH, type=openapi.TYPE_STRING,
                                             description='Question ID')],
        responses={status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=['get'])
    def get_question_details(self, request, question_uuid):
        """
        Retrieves details of a specific question using the question UUID.
        """
        logger.info(f"Fetching details for question: {question_uuid}")
        entity_uuids_list = self.__sme_service.get_entity_ids_from_request(request)
        response = self.__sme_service.get_question_details(question_uuid, entity_uuids_list)
        return CustomResponse(result=response)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name='answer_uuid', in_=openapi.IN_PATH, type=openapi.TYPE_STRING,
                                             description='Answer ID')],
        responses={status.HTTP_200_OK: SuccessMessages.QUESTION_DELETED_SUCCESS,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=["delete"])
    def delete_answer(self, request, answer_uuid):
        """
        Deletes an answer based on the answer UUID.
        """
        logger.info(f"Deleting answer: {answer_uuid}")
        customer_uuid, application_uuid, _ = get_headers(request.headers)
        entity_uuids_list = self.__sme_service.get_entity_ids_from_request(request)

        self.__sme_service.delete_answer(answer_uuid, customer_uuid, application_uuid, entity_uuids_list)
        logger.info(f"Answer {answer_uuid} deleted successfully.")
        return CustomResponse(result=SuccessMessages.QUESTION_DELETED_SUCCESS)

    @swagger_auto_schema(
        request_body=AddQuestionSerializer,
        manual_parameters=[constants.customer_uuid_header, constants.application_uuid_header],
        responses={status.HTTP_201_CREATED: SuccessMessages.QUESTION_ADDED_SUCCESS,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=['post'])
    def add_question(self, request):
        """
        Adds a new question to the system.
        """
        logger.info("Adding a new question.")
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        entity_uuids_list = self.__sme_service.get_entity_ids_from_request(request)

        serializer = AddQuestionSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            logger.error("Invalid data for adding question.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if (entity_uuids_list and all(item in entity_uuids_list for item in data.get('entity_uuids'))) or not entity_uuids_list:
            response = self.__sme_service.add_question(data, customer_uuid, application_uuid, user_uuid)
            logger.info("Question added successfully.")
            return CustomResponse(result=response, code=status.HTTP_201_CREATED)
        else:
            logger.error("User don't have the scope to add question.")
            raise UnauthorizedByScopeException(ErrorMessages.BEYOND_SCOPE)

    @swagger_auto_schema(
        request_body=UpdateAnswerSerializer,
        responses={status.HTTP_200_OK: SuccessMessages.ANSWER_UPDATED_SUCCESS,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=['put'])
    def update_answer(self, request):
        """
        Updates an existing answer.
        """
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        entity_uuids_list = self.__sme_service.get_entity_ids_from_request(request)

        logger.info("Updating answer.")
        serializer = UpdateAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Invalid data for updating answer.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if (entity_uuids_list and all(item in entity_uuids_list for item in data.get('entity_uuids'))) or not entity_uuids_list:
            response = self.__sme_service.update_answer(data, customer_uuid, application_uuid, user_uuid, entity_uuids_list)
            logger.info("Answer updated successfully.")
            return CustomResponse(result=response)
        else:
            logger.error("User don't have the scope to add question.")
            raise UnauthorizedByScopeException(ErrorMessages.BEYOND_SCOPE)

    @swagger_auto_schema(
        request_body=VerifyAnswerSerializer,
        responses={status.HTTP_200_OK: SuccessMessages.ANSWER_VERIFIED_SUCCESS,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=['put'])
    def verify_answer(self, request):
        """
        Verifies an answer.
        """
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        entity_uuids_list = self.__sme_service.get_entity_ids_from_request(request)

        logger.info("Verifying answer.")
        serializer = VerifyAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Invalid data for verifying answer.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        self.__sme_service.verify_answer(data, customer_uuid, application_uuid, user_uuid, entity_uuids_list)
        logger.info("Answer verified successfully.")
        return CustomResponse(SuccessMessages.ANSWER_VERIFIED_SUCCESS)

    @swagger_auto_schema(
        request_body=FeedbackSerializer,
        responses={status.HTTP_200_OK: SuccessMessages.FEEDBACK_SUBMIT_SUCCESS,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=['put'])
    def update_feedback(self, request):
        """
        Submits feedback for an answer.
        """
        logger.info("Submitting feedback.")
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        entity_uuids_list = self.__sme_service.get_entity_ids_from_request(request)

        serializer = FeedbackSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            logger.error("Invalid data for submitting feedback.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        self.__sme_service.update_feedback(data, customer_uuid, application_uuid, user_uuid, entity_uuids_list)
        logger.info("Feedback submitted successfully.")
        return CustomResponse(result=SuccessMessages.FEEDBACK_SUBMIT_SUCCESS)

    @swagger_auto_schema(
        request_body=GenerateQASerializer,
        responses={status.HTTP_200_OK: SuccessMessages.QA_GENERATE_SUCCESS,
                   status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST}
    )
    @action(detail=False, methods=['post'])
    def generate_qa(self, request):
        """
        Generates a question-answer pairs for given knowledge sources.
        """
        logger.info("Generating Q/A for knowledge sources.")
        customer_uuid, application_uuid, user_uuid = get_headers(request.headers)
        entity_uuids_list = self.__sme_service.get_entity_ids_from_request(request)

        serializer = GenerateQASerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            logger.error("Invalid data for generating QA.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        _ = self.__sme_service.generate_qa(data, customer_uuid, application_uuid, user_uuid, entity_uuids_list)
        logger.info("QA pair generated successfully.")
        return CustomResponse(result=SuccessMessages.QA_GENERATE_SUCCESS)
    

    @swagger_auto_schema(
        request_body=RelevantChunksRequestSerializer,
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['post'])
    def get_relevant_chunks(self, request):
        
        """ 
        API to fetch the relevant chunks to a query from vectordb.
        """

        logger.info("Fetching relevant chunks.")
        
        customer_uuid, application_uuid, _ = get_headers(request.headers)
        
        logger.info("Validating request body.")
        logger.info(f"request data :: {request.data}")
        
        serializer = RelevantChunksRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            
            logger.error("Invalid data for fetching relevant chunks.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    
        data = serializer.validated_data
        
        query = data['query']
        top_n = data['top_n']
        
        entity_filter = data['entity_filter']
        logger.info(f'Entity filter in request :: {entity_filter}')
        
        sort_by_sequence = data['sort_by_sequence']
        metadata_keys = data['metadata_keys']
        
        relevant_chunks = self.__sme_service.get_relevant_chunks(customer_uuid, application_uuid, query, entity_filter, top_n, sort_by_sequence, metadata_keys)
        return CustomResponse(relevant_chunks, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=ReferenceChunkSerializer,
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['post'])
    def get_parent_chunks(self, request): 
        
        """ 
        API to fetch the parent chunks for the references present in the chunk with the given id.
        """   
        
        logger.debug('fetching parent chunks')
        
        customer_uuid, application_uuid, _ = get_headers(request.headers)
        
        logger.info("Validating request body.")
        logger.info(f"request data :: {request.data}")
        
        serializer = ReferenceChunkSerializer(data=request.data)
        
        if not serializer.is_valid():
            
            logger.error("Invalid data for fetching parent chunks.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    
        data = serializer.validated_data
        
        chunk_id = data['chunk_id']
        sort_by_sequence = data['sort_by_sequence']
        metadata_keys = data['metadata_keys']
        
        parent_chunks = self.__sme_service.get_parent_chunks(customer_uuid, application_uuid, chunk_id, sort_by_sequence, metadata_keys)
        return CustomResponse(parent_chunks, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=NeighbouringChunkSerializer,
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorMessages.BAD_REQUEST
        }
    )
    @action(detail=False, methods=['post'])
    def get_neighbouring_chunks(self, request):
        
        """ 
        API to fetch the neighbouring chunks for the references present in the chunk with the given id.
        """   
        
        logger.debug('fetching neighbouring chunks')
        
        customer_uuid, application_uuid, _ = get_headers(request.headers)
  
        logger.info("Validating request body.")
        logger.info(f"request data :: {request.data}")
        
        serializer = NeighbouringChunkSerializer(data=request.data)
        
        if not serializer.is_valid():
            
            logger.error("Invalid data for fetching neighbouring chunks.")
            raise CustomException(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    
        data = serializer.validated_data
    
        chunk_ids = data['chunk_ids']
        sort_by_sequence = data['sort_by_sequence']
        metadata_keys = data['metadata_keys']
        
        neighbouring_chunks = self.__sme_service.get_neighbouring_chunks(
            customer_uuid, application_uuid, chunk_ids, sort_by_sequence, metadata_keys
        )
        return CustomResponse(neighbouring_chunks, status=status.HTTP_200_OK)

