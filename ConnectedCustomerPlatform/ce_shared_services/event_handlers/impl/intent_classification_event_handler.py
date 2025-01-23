import asyncio
import json

import logging
from typing import List

from ce_shared_services.configuration_models.configuration_models import IntentClassificationConfig, \
    VariableConfig, IntentValue, IntentSubIntentsConfig
from ce_shared_services.event_handlers.constants import IntentPrompt, PromptParams, ChromaOperators, \
    ChromadbMetaDataParams, Chromadb, NO_SIMILAR_QUERIES_FOUND, Variables, VariableTypes, VariableOwner
from ce_shared_services.event_handlers.error_messages import IntentClassificationHandler
from ce_shared_services.event_handlers.interface.event_handler import IEventHandler
from ce_shared_services.event_handlers.utils import \
    create_prompt_with_chat_history_query, format_chroma_examples, format_conversation_history, format_intents_sub_intents, \
    get_metadata_for_intent_examples
from ce_shared_services.llm.interface.llm import LLM
from ce_shared_services.vectordb.interface.vectordb import VectorDB

logger=logging.getLogger(__name__)
class IntentClassificationEventHandler(IEventHandler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IntentClassificationEventHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self,intent_classification_config:IntentClassificationConfig, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            logger.debug(f"Inside IntentClassificationEventHandler - Singleton Instance ID: {id(self)}")
            self.initialized = True
            self.intent_classification_config=intent_classification_config
            self.intent_variable = None
            self.sub_intent_variable = None



    async def run_event_handler(self, conversation_history: list, user_input: str):
        """
        Main handler for intent classification.

        This method handles the classification of intents based on the provided conversation history and user input.
        It determines whether to perform parallel or sequential classification based on whether a previous intent
        is available in the configuration. The intent classification logic is executed by invoking appropriate helper methods.

        Args:
            conversation_history (list): A list of previous chat messages that provide context for intent classification.
            user_input (str): The current user query that needs to be classified.

        Returns:
            dict: The model's output after performing intent classification, represented as a dictionary.
        """
        logger.debug("In IntentClassificationEventHandler :: run_intent_classification_event_handler")
        # Get the selected intents from the configuration
        # Check if there is a previous intent in the configuration
        variables = self.intent_classification_config.variables or []
        for variable in variables:
            if variable.name == Variables.INTENT.value:
                self.intent_variable = variable
            elif variable.name == Variables.SUB_INTENT.value:
                self.sub_intent_variable = variable

        if not self.intent_variable:
            self.intent_variable=VariableConfig(name=Variables.INTENT.value,type=VariableTypes.STRING.value,owner=VariableOwner.SYSTEM.value,value=IntentValue().model_dump())
        if not self.sub_intent_variable:
            self.sub_intent_variable=VariableConfig(name=Variables.SUB_INTENT.value,type=VariableTypes.STRING.value,owner=VariableOwner.SYSTEM.value,value=IntentValue().model_dump())
        intents = self.intent_classification_config.selected_intents
        # Format the intents to fit the classification model
        intent_details = format_intents_sub_intents(intents)

        # Format the chat history for the classification model
        formatted_conversation_history = format_conversation_history(conversation_history,self.intent_classification_config.conversation_history_n)


        # Perform classification and get results
        if self.intent_variable.name:
            # If a previous intent exists, perform parallel classification
            identified_intent, identified_sub_intent=await self._parallel_classification_of_intent_sub_intent(formatted_conversation_history, intent_details, intents, user_input,self.intent_variable)
        else:
            # If no previous intent exists, perform sequential classification
            identified_intent, identified_sub_intent=await self._sequential_classification(formatted_conversation_history, intent_details, intents, user_input)

        if identified_intent:
            self.intent_variable.value['name'] = identified_intent.name
            self.intent_variable.value['id'] = identified_intent.id

        if identified_sub_intent:
            self.sub_intent_variable.value['name'] = identified_sub_intent.name
            self.sub_intent_variable.value['id'] = identified_sub_intent.id
        # Return the final intent after classification, represented as a dictionary
        return [self.intent_variable.model_dump(),self.sub_intent_variable.model_dump()]

    async def _parallel_classification_of_intent_sub_intent(self,
            formatted_conversation_history: list,
            intent_details: str,
            intents: list,
            user_input: str,
            intent_variable: IntentValue
    ):
        """
        Handle parallel classification for both intent and sub-intent using asyncio.

        This method handles concurrent classification of both intent and sub-intent using
        asyncio.gather(). It creates tasks for intent and sub-intent classification to be
        processed concurrently. Once both tasks are completed, it processes the results.

        Args:
            formatted_conversation_history (list): Formatted previous chat messages for classification
            intent_details (str): Formatted intent details for classification
            intents (list): List of selected intents to be classified
            user_input (str): Current user query to be classified
            intent_variable (IntentVariableConfig): Current intent configuration
        """
        logger.debug("In IntentClassificationEventHandler :: _parallel_classification_of_intent_sub_intent")

        # Create the intent classification task
        intent_task = self._identify_intent(
            formatted_conversation_history,
            intents,
            intent_details,
            self.intent_classification_config.intent_prompt,
            self.intent_classification_config.llm,
            user_input,
            self.intent_classification_config.vector_store
        )

        # Check if there are sub-intents assigned to the identified intent to process
        sub_intents = next((intent.sub_intents for intent in intents if intent.name == intent_variable.name), [])
        if sub_intents:
            # Create the sub-intent classification task
            sub_intent_task = self._identify_sub_intent(
                formatted_conversation_history,
                sub_intents,
                intent_variable.name,
                self.intent_classification_config.sub_intent_prompt,
                user_input,
                self.intent_classification_config.llm,
                self.intent_classification_config.vector_store
            )


            # Run both tasks concurrently
            new_intent, parallel_sub_intent = await asyncio.gather(intent_task, sub_intent_task)
        else:
            # If no sub-intents, just run the intent task
            new_intent = await intent_task
            parallel_sub_intent = None

        # Determine if a new sub-intent is needed
        # If a new sub-intent is required, identify it using the new intent's sub-intents
        if new_intent and new_intent.name != intent_variable.name and  new_intent.sub_intents:
            final_sub_intent = await self._identify_sub_intent(
                formatted_conversation_history,
                new_intent.sub_intents,
                new_intent.name,
                self.intent_classification_config.sub_intent_prompt,
                user_input,
                self.intent_classification_config.llm,
                self.intent_classification_config.vector_store
            )
        else:
            # If no new sub-intent is needed, use the parallel sub-intent results
            final_sub_intent = parallel_sub_intent
        return new_intent, final_sub_intent

    async def _sequential_classification(self, formatted_conversation_history: list, intent_details: str,
                                          intents: list, user_input: str):
        logger.debug("In IntentClassificationEventHandler :: _sequential_classification")

        """
        Handle sequential intent and sub-intent classification.

        This method performs sequential classification for both intent and sub-intent. It first identifies the main intent
        based on the provided chat history, intent details, and user query. Once the intent is identified, it proceeds to
        classify the sub-intent, if available. This method is used when the classification process follows a sequential
        order, where the identification of the intent precedes the identification of the sub-intent.

        Args:
            formatted_conversation_history (list): A list of formatted previous chat messages to be used for classification.
            intent_details (str): A string containing the formatted intent details used for classification.
            intents (list): A list of selected intents that are to be classified.
            user_input (str): The current user query that is to be classified.

        Returns:
            None: The method does not return a value but processes the classification results sequentially.
        """
        # Step 1: Identify the main intent based on the provided inputs
        identified_intent = await self._identify_intent(
            formatted_conversation_history,
            intents,
            intent_details,
            self.intent_classification_config.intent_prompt,
            self.intent_classification_config.llm,
            user_input,
            self.intent_classification_config.vector_store
        )

        # Step 2: If the intent is identified and has sub-intents, classify the sub-intent
        identified_sub_intent = None
        if identified_intent and identified_intent.sub_intents:
            identified_sub_intent=await self._identify_sub_intent(
                formatted_conversation_history,
                identified_intent.sub_intents,
                identified_intent.name,
                self.intent_classification_config.sub_intent_prompt,
                user_input,
                self.intent_classification_config.llm,
                self.intent_classification_config.vector_store
            )
        return identified_intent, identified_sub_intent

    async def _identify_intent(self,formatted_conversation_history,intent_and_sub_intents:List[IntentSubIntentsConfig],formatted_intents:str,intent_prompt:dict,llm:LLM,user_input:str,vector_store):
        """
        Identifies the intent of  user query based on formatted chat history,
        intent details, and prompt-based LLM analysis.

        Steps:
        1. Construct and execute the final prompt using LLM to classify the intent.
        2. Process the identified intent and, if applicable, sub-intents.
        """
        logger.debug("In IntentClassificationEventHandler :: __identify_intent")


        # Extract the system message from the prompt and validate it
        intent_prompt_system_message:str=intent_prompt.get(PromptParams.SYSTEM.value)
        if not intent_prompt_system_message:
            raise ValueError(IntentClassificationHandler.SYSTEM_MESSAGE_NOT_FOUND.value)


        # Fetch examples for the intent classification from Chroma
        # The examples are retrieved based on metadata and similarity search based on user query
        intent_metadata=get_metadata_for_intent_examples(intent_and_sub_intents)
        intent_examples=await self._fetch_examples_from_chroma(metadata_combination=intent_metadata,collection_name=self.intent_classification_config.collection_name,user_input=user_input,vector_store=vector_store)

        # Replace placeholders in the system message with actual intent details and examples
        final_intent_prompt = intent_prompt_system_message.replace(IntentPrompt.INTENT_DETAILS.value, formatted_intents).replace(IntentPrompt.EXAMPLES.value,intent_examples or NO_SIMILAR_QUERIES_FOUND)
        logger.debug(f"Final Intent Prompt \n:: {final_intent_prompt}\n")
        llm_input = create_prompt_with_chat_history_query(final_intent_prompt, formatted_conversation_history,user_input)

        #Execute the prompt using LLM and parse the result
        # run prompt
        llm_response = await llm.run_async(llm_input, json_mode=True, max_retries=self.intent_classification_config.llm_max_retires,
                                          initial_delay=self.intent_classification_config.llm_initial_delay)
        #todo after implementation of complete json mode this json parsing should be removed
        try:
            llm_response=json.loads(llm_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while querying the LLM: {e}")
            raise
        intent_identified = llm_response.get(IntentPrompt.INTENT.value)

        # Handle cases where no valid intent is identified or the intent is "Others"
        if not intent_identified or intent_identified.lower() ==IntentPrompt.OTHERS.value.lower():
            logger.debug(f"Intent Unidentified :: {intent_identified}")
            return
        #Process the identified intent
        for intent in intent_and_sub_intents:
            if intent.name.lower() == intent_identified.lower():
                # Update the intent in the action JSON with the identified intent details
                return intent

    async def _identify_sub_intent(self,formatted_conversation_history,sub_intents_list,intent_identified,sub_intent_prompt:dict,user_input:str,llm:LLM,vector_store):
        """
       Identifies the sub-intent  with identified intent using formatted chat history,
       sub-intent details, and LLM prompt-based analysis.

       Steps:
       1. Retrieve and format sub-intent details (names and descriptions).
       2. Fetch examples within the intent identified for the sub-intent classification based on metadata.
       3. Construct and execute the final prompt using LLM to classify the sub-intent.
       4. Process the identified sub-intent and update the final result JSON.
       """
        logger.debug("In IntentClassificationEventHandler :: __identify_sub_intent")

        if not sub_intent_prompt:
            raise ValueError(IntentClassificationHandler.SUB_INTENT_PROMPT_UNIDENTIFIED.value)

        # Extract the system message from the prompt
        sub_intent_prompt_system_message: str = sub_intent_prompt.get(PromptParams.SYSTEM.value)
        if not sub_intent_prompt_system_message:
            raise ValueError(IntentClassificationHandler.SYSTEM_MESSAGE_NOT_FOUND.value)
        #Format sub-intent details(names and description) to fit the prompt structure
        sub_intent_details = format_intents_sub_intents(sub_intents_list)

        # Fetch examples with in the intent examples for sub-intent classification from Chroma
        # Metadata includes the category and related intent and sub-intent identifiers
        #fetch examples from chroma by user query with in the examples of intent identified.---metadata:[{category:intent_classification},{INTENT,intent_name:True},{SUBINTENT,intent_name,sub_intent_name:True}]
        sub_intent_examples=await self._fetch_examples_from_chroma({ChromaOperators.AND:[{ChromadbMetaDataParams.CATEGORY.value: Chromadb.INTENT_CLASSIFICATION_CATEGORY.value},{f"{ChromadbMetaDataParams.INTENT.value}{ChromadbMetaDataParams.SEPARATOR.value}{intent_identified.lower()}":True},{ChromadbMetaDataParams.SUB_INTENT_FILTER.value:True}]},intent_identified=intent_identified,collection_name=self.intent_classification_config.collection_name,user_input=user_input,vector_store=vector_store)

        # Replace placeholders in the system message with intent and sub-intent details and examples
        final_sub_intent_prompt = sub_intent_prompt_system_message.replace(IntentPrompt.INTENT_NAME.value, intent_identified.replace('_',' ').lower()).replace(IntentPrompt.SUB_INTENT_DETAILS.value, sub_intent_details).replace(IntentPrompt.EXAMPLES.value,sub_intent_examples or NO_SIMILAR_QUERIES_FOUND)
        logger.debug(f"Sub-Intent Prompt \n:: {final_sub_intent_prompt}\n")
        llm_input = create_prompt_with_chat_history_query(final_sub_intent_prompt, formatted_conversation_history,user_input)

        #Execute the prompt using LLM and parse the result
        llm_response = await llm.run_async(llm_input, json_mode=True, max_retries=self.intent_classification_config.llm_max_retires,
                                    initial_delay=self.intent_classification_config.llm_initial_delay)
        try:
            llm_response=json.loads(llm_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while querying the LLM: {e}")
            raise
        #Extract the identified sub-intent from the prompt result
        sub_intent_identified=llm_response.get(IntentPrompt.SUB_INTENT.value)
        if sub_intent_identified and sub_intent_identified.lower() != IntentPrompt.OTHERS.value.lower():
            for sub_intent in sub_intents_list:
                if sub_intent_identified.lower() == sub_intent.name.lower():
                    return sub_intent

    async def _fetch_examples_from_chroma(self,metadata_combination,collection_name,user_input,vector_store:VectorDB,intent_identified=None):
        """
        Fetches examples from ChromaDB based on the provided metadata combination and intent_identified(optional).

        Steps:
        1. Validate the metadata combination.
        3. Fetch examples using the ChromaDB semantic search for the provided metadata and user Query.
        4. Format and return the results based on the prompt structure.

        Args:
            metadata_combination (dict): dict of metadata filters for semantic search.
            intent_identified (str, optional): The identified intent to help format results. Defaults to None.

        Returns:
            list or None: Formatted examples for the prompt or None if no examples are found or an error occurs.
        """
        logger.debug("In IntentClassificationEventHandler :: __fetch_examples_from_chroma")
        if not metadata_combination:
            return None
        # Fetch Previous Examples from Chromadb
        try:

            # Perform a semantic search in the Chroma collection with the given query and metadata
            try:
                chunks = await vector_store.similarity_search_with_score_async(
                    collection_name, user_input, metadata_combination, top_n=self.intent_classification_config.examples_n
                )
                chunks=[chunk for chunk in chunks if isinstance(chunk.score,float) and chunk.score*100>=self.intent_classification_config.similarity_threshold]
                logger.debug("Similarity search completed. Retrieved %d chunks.", len(chunks))
            except Exception as e:
                logger.error("Error during similarity search: %s", str(e))
                raise
            #Format the search results based on the prompt requirements
            return format_chroma_examples(chunks,main_intent=intent_identified,limit=self.intent_classification_config.examples_n)
        except Exception as e:
            logger.error(f"Exception occurred in chromaDB :: {e}")
        return None




