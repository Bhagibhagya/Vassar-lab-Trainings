import asyncio

from AIServices.VectorStore.chromavectorstore import ChromaVectorStore
from AIServices.prompts import INTENT_CLASSIFICATION_PROMPT_FOR_EVENT_HANDLER, \
    SUB_INTENT_CLASSIFICATION_PROMPT_FOR_SUB_INTENT_CLASSIFICATION
from ConnectedCustomerPlatform.exceptions import ResourceNotFoundException, InvalidValueProvidedException
from WiseFlow.constants.constants import DimensionTypeNames, PromptCategory, PromptParams
from WiseFlow.constants.error_messages import IntentIdentification
from WiseFlow.dao.impl.dimension_dao_impl import DimensionDaoImpl
from WiseFlow.dao.impl.prompt_dao_impl import PromptDaoImpl
from WiseFlow.dao.interface.dimension_dao_interface import IDimensionDao
from WiseFlow.services.interface.intent_classification_handler_service_interface import \
    IIntentClassificationHandlerService

from django.conf import settings

from WiseFlow.utils import map_dimensions_to_intent_configs
from ce_shared_services import VectorDB, LLM
from ce_shared_services.configuration_models.configuration_models import IntentClassificationConfig
from ce_shared_services.event_handlers.impl.intent_classification_event_handler import IntentClassificationEventHandler
from ce_shared_services.factory.embedding.embedding_factory import EmbeddingModelFactory
from ce_shared_services.factory.llm.llm_factory import LLMFactory
from ce_shared_services.factory.vectordb.vectordb_factory import VectorDBFactory

import logging

logger=logging.getLogger(__name__)
class IntentClassificationHandlerServiceImpl(IIntentClassificationHandlerService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IntentClassificationHandlerServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print(f"Inside EntityServiceImpl - Singleton Instance ID: {id(self)}")
            self.initialized = True
        self.dimension_dao :IDimensionDao = DimensionDaoImpl()
        self.chroma_vector_store = ChromaVectorStore()
        self.__embedding_model = EmbeddingModelFactory.instantiate(settings.EMBEDDING_CLASS_NAME,
                                                                   settings.EMBEDDING_CONFIG)
        chroma_db_config = {'database': settings.CHROMADB_NAME,
                            'host': settings.CHROMADB_HOST,
                            'port': settings.CHROMADB_PORT,
                            'embedding_model': self.__embedding_model}
        self.__chroma_db_service: VectorDB = VectorDBFactory.instantiate(settings.CHROMADB_CLASS_NAME, chroma_db_config)
        self._llm: LLM = LLMFactory.instantiate(settings.LLM_CLASS_NAME, settings.LLM_CONFIG)
        self.prompt_dao = PromptDaoImpl()


    def identify_intent_sub_intent(self,customer_uuid:str, application_uuid:str,validated_payload:dict,selected_intents,variables):
        """
        This method identifies the intent and sub-intent based on the provided input data. It fetches necessary details
        such as intent and sub-intent configurations, prompts, and then performs classification.

        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.
            validated_payload (dict): The validated input data containing relevant information for classification.
            selected_intents: A list of selected intents for classification.
            variables: Additional variables that might be used in the classification process.

        Returns:
            The identified intent and sub-intent variable.
        """
        if not selected_intents:
            # fetching intents names and descriptions and associated sub intent names and descriptions
            intent_and_sub_intents = self.dimension_dao.fetch_parent_and_child_dimension_details(
                customer_uuid=customer_uuid, application_uuid=application_uuid,
                parent_dimension_type_name=DimensionTypeNames.INTENT.value)
            if not intent_and_sub_intents:
                logger.error(f"Intent Dimension Details is not present for the customer:: {customer_uuid} and application :: {application_uuid}")
                raise ResourceNotFoundException(IntentIdentification.INTENT_SUB_INTENT_DETAILS_NOT_FOUND)
            #fetching list of dimensionsView Objects and changing them to  List[IntentConfig] Json objects
            selected_intents = map_dimensions_to_intent_configs(intent_and_sub_intents)
            selected_intents = [intent_config.model_dump() for intent_config in selected_intents]
        # fetching prompt
        # intent_prompt = self.prompt_dao.fetch_prompt_by_category_filter_json(customer_uuid=customer_uuid,
        #                                                                      application_uuid=application_uuid,
        #                                                                      category_name=PromptCategory.IntentClassification.value)
        intent_prompt = {PromptParams.SYSTEM.value:INTENT_CLASSIFICATION_PROMPT_FOR_EVENT_HANDLER}
        # sub_intent_prompt = self.prompt_dao.fetch_prompt_by_category_filter_json(customer_uuid=customer_uuid,
        #                                                                      application_uuid=application_uuid,
        #                                                                      category_name=PromptCategory.SubIntentClassification.value)
        sub_intent_prompt = {PromptParams.SYSTEM.value:SUB_INTENT_CLASSIFICATION_PROMPT_FOR_SUB_INTENT_CLASSIFICATION}

        collection_name = self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid,
                                                                                                      application_uuid)

        if not intent_prompt:
            raise InvalidValueProvidedException(IntentIdentification.INTENT_PROMPT_NOT_FOUND)


        # Format intent details to fit the prompt structure

        intent_classification_config= IntentClassificationConfig(
            conversation_history_n=6,
            examples_n=5,
            selected_intents=selected_intents,
            intent_prompt=intent_prompt,
            sub_intent_prompt=sub_intent_prompt,
            vector_store=self.__chroma_db_service,
            llm=self._llm,
            collection_name=collection_name,
            llm_max_retires=settings.LLM_MAX_RETRIES,
            llm_initial_delay=settings.LLM_INITIAL_DELAY,
            variables=variables,
            similarity_threshold=90
        )

        intent_handler=IntentClassificationEventHandler(intent_classification_config)
        result = asyncio.run(intent_handler.run_event_handler(conversation_history=validated_payload.get('conversation_history'),user_input=validated_payload.get('user_input')))

        return result


