import inspect
import json
import uuid
from uuid import uuid4

from rest_framework import status

from AIServices.VectorStore.chromavectorstore import ChromaVectorStore
from ConnectedCustomerPlatform.exceptions import InvalidValueProvidedException, CustomException
from ConnectedCustomerPlatform.utils import Utils
from WiseFlow.constants.constants import EntityExamplesKeys, ChromaOperators, \
    TOP_N_TO_FETCH_EXAMPLES, OwnerShipTypes, ENTITY_PROMPT_TEMPLATE, ENTITY_ORIGIN, EXAMPLE_TYPE, EntityNames, PREFIX_FOR_ENTITY_CHROMA_COLLECTION_NAME
from Platform.utils import paginate_queryset
from WiseFlow.constants.error_messages import EntityErrorMessages
from WiseFlow.dao.impl.entity_dao_impl import EntityDaoImpl
from WiseFlow.dao.interface.entity_dao_interface import IEntityDaoInterface
from WiseFlow.constants.success_messages import EntitySuccessMessages
from WiseFlow.dataclass import ExampleMetadata
from WiseFlow.services.interface.entity_service_interface import IEntityInterface
from WiseFlow.utils import format_chat_history, create_prompt_with_chat_history_query, get_todays_date_and_day
from ce_shared_services import VectorDB, LLM
from ce_shared_services.datatypes import Chunk
from ce_shared_services.factory.embedding.embedding_factory import EmbeddingModelFactory
from ce_shared_services.factory.llm.llm_factory import LLMFactory
from ce_shared_services.factory.vectordb.vectordb_factory import VectorDBFactory
from django.conf import settings
import logging

logger=logging.getLogger(__name__)
class EntityServiceImpl(IEntityInterface):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EntityServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print(f"Inside EntityServiceImpl - Singleton Instance ID: {id(self)}")
            self.entity_dao = EntityDaoImpl()
            self.initialized = True

        self.chroma_vector_store=ChromaVectorStore()

        self.__embedding_model = EmbeddingModelFactory.instantiate(settings.EMBEDDING_CLASS_NAME,
                                                                   settings.EMBEDDING_CONFIG)

        chroma_db_config = {'database': settings.CHROMADB_NAME,
                            'host': settings.CHROMADB_HOST,
                            'port': settings.CHROMADB_PORT,
                            'embedding_model': self.__embedding_model}
        self.__chroma_db_service: VectorDB = VectorDBFactory.instantiate(settings.CHROMADB_CLASS_NAME,chroma_db_config)
        self.__entity_dao:IEntityDaoInterface=EntityDaoImpl()

        self._llm: LLM = LLMFactory.instantiate(settings.LLM_CLASS_NAME, settings.LLM_CONFIG)
    def add_entity_examples(self, customer_uuid: str, application_uuid: str, validated_payload: dict):
        """
        Add examples to chroma vector store for an entity
        """
        logger.info("In EntityServiceImpl :: add_entity_examples")
        entity_uuid = validated_payload.get("entity_uuid")
        entity_name = validated_payload.get("entity_name")
        examples = validated_payload.get("examples")
        is_default = validated_payload.get("is_default")
        #is default means System entities
        if is_default:
            collection_name=settings.DEFAULT_ENTITY_COLLECTION_NAME
        #Customer Specific entities
        else:
            # collection_name=self.chroma_vector_store.get_chroma_collection_name_by_customer_application(customer_uuid, application_uuid)
            collection_name = Utils.get_chroma_collection_name(
                customer_uuid, application_uuid, PREFIX_FOR_ENTITY_CHROMA_COLLECTION_NAME
            )
        #iterate and add each example
        logger.info(f"Adding examples to collection{collection_name}")
        for example in examples:
            prompt_input=example["input"]
            output=example["output"]
            chunk = Chunk(
                id=str(uuid4()),
                document=prompt_input,
                metadata=ExampleMetadata(entity_uuid=entity_uuid,entity_name=entity_name,prompt_output=output,origin=ENTITY_ORIGIN,type=EXAMPLE_TYPE).__dict__
            )
            try:
                self.__chroma_db_service.add_chunks_sync(collection_name, [chunk])
                logger.info("Successfully added example to chroma db")
            except Exception as e:
                logger.info(f"Cannot add examples to chroma str{e}")
                raise CustomException(EntityErrorMessages.ADD_EXAMPLES_FAILED.format(e=e),status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_entity_prompt(self,customer_uuid: str, application_uuid: str, validated_payload: dict):
        """Test entity prompt"""
        logger.info("In EntityServiceImpl :: test_entity_prompt")
        entity_uuid = validated_payload.get("entity_uuid")
        chat_history = validated_payload.get("chat_history")
        previous_value_of_entity = validated_payload.get("previous_value_of_entity")
        user_query=validated_payload.get("user_query")

        entity_name,ownership,instructions,description,output_format=self.__entity_dao.get_entity_details(entity_uuid)

        if entity_name.lower()==EntityNames.DATE.value.lower() or entity_name.lower()==EntityNames.DATE_RANGE.value.lower():

            instructions=instructions.format(today_date=get_todays_date_and_day())

        examples=self.__fetch_rag_examples(entity_uuid,entity_name,customer_uuid,application_uuid,ownership,user_query)
        prompt = ENTITY_PROMPT_TEMPLATE.format(
            entity_name=entity_name,
            entity_description=description,
            instructions=instructions,
            previous_value_of_entity=previous_value_of_entity,
            examples=json.dumps(examples, indent=2) , # Convert examples to a JSON string
            output_format=json.dumps(output_format)
        )
        #Formats chat history into a structured format based on the message source (AI or user).
        formatted_chat_history=format_chat_history(chat_history)
        #Constructs a list of inputs for the Language Learning Model (LLM) by combining a system message,chat history, and the user's query.
        llm_input = create_prompt_with_chat_history_query(prompt, formatted_chat_history,user_query)
        #run prompt
        llm_response = self._llm.run_sync(llm_input, json_mode=True,max_retries=settings.LLM_MAX_RETRIES,initial_delay=settings.LLM_INITIAL_DELAY)

        try:
            json_response = json.loads(llm_response)
            return {"prompt_response":json_response,
            "prompt":prompt}

        except json.JSONDecodeError as exception:

            logger.error(f"JSON decode error while decoding llm response :: {exception}")
            return {"prompt_response":llm_response,
            "prompt":prompt}
            # raise CustomException(EntityErrorMessages.DECODE_JSON_FAILED,status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __fetch_rag_examples(
            self,
            entity_uuid: str,
            entity_name: str,
            customer_uuid: str,
            application_uuid: str,
            ownership: str,
            search_query: str
    ):
        """
        Fetch relevant examples for a given entity using similarity search.

        This method uses metadata and a similarity search mechanism to retrieve
        examples from a vector store. The result is a list of input-output pairs
        (examples) relevant to the provided query.

        Args:
            entity_uuid (str): Unique identifier for the entity.
            entity_name (str): Name of the entity.
            customer_uuid (str): Unique identifier for the customer.
            application_uuid (str): Unique identifier for the application.
            ownership (str): system or custom
            search_query (str): The query to find similar examples.

        Returns:
            List[Dict]: A list of dictionaries containing 'input' and 'output' pairs.
        """
        logger.info("In EntityServiceImpl :: __fetch_rag_examples - Starting process")
        logger.debug(
            "Parameters - entity_uuid: %s, entity_name: %s, customer_uuid: %s, application_uuid: %s, ownership: %s, search_query: %s",
            entity_uuid, entity_name, customer_uuid, application_uuid, ownership, search_query
        )

        # Determine which collection to use based on the is_default flag
        if ownership.lower()==OwnerShipTypes.SYSTEM.value.lower():
            collection_name = settings.DEFAULT_ENTITY_COLLECTION_NAME
            logger.info("Using default collection: %s", collection_name)
        elif ownership.lower()==OwnerShipTypes.CUSTOM.value.lower():
            collection_name = Utils.get_chroma_collection_name(
                customer_uuid, application_uuid, PREFIX_FOR_ENTITY_CHROMA_COLLECTION_NAME
            )
            logger.info("Using custom collection: %s", collection_name)
        else:
            raise InvalidValueProvidedException(EntityErrorMessages.INVALID_OWNERSHIP)

        # Build metadata filter for the query
        metadata_filter = {
            ChromaOperators.AND: [
                {EntityExamplesKeys.ENTITY_UUID: entity_uuid},
                {EntityExamplesKeys.TYPE: EXAMPLE_TYPE},
                {EntityExamplesKeys.ORIGIN:ENTITY_ORIGIN}
            ]
        }
        logger.debug("Filter constructed: %s", metadata_filter)

        # Perform similarity search asynchronously
        logger.info("Performing similarity search in collection: %s", collection_name)
        try:
            chunks = self.__chroma_db_service.similarity_search_sync(
                collection_name, search_query, metadata_filter, top_n=TOP_N_TO_FETCH_EXAMPLES
            )
            logger.info("Similarity search completed. Retrieved %d chunks.", len(chunks))
        except Exception as e:
            logger.error("Error during similarity search: %s", str(e))
            raise

        # Extract input-output pairs from the chunks
        examples = []
        logger.info("Processing retrieved chunks to construct examples.")
        for chunk in chunks:
            try:
                example = {
                    "input": chunk.document,
                    "output": chunk.metadata[EntityExamplesKeys.PROMPT_OUTPUT]
                }
                examples.append(example)
                logger.debug("Processed chunk: %s", example)
            except KeyError as e:
                logger.warning("Missing key in chunk metadata: %s", str(e))
                continue

        logger.info("Successfully constructed %d examples.", len(examples))
        return examples

    def __fetch_custom_list_items(
            self,
            entity_uuid: str,
            customer_uuid: str,
            application_uuid: str,
            ownership: str,
            collection_name: str
        ):
        """ helper function to fetch custom list items """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Build metadata filter for the query
        metadata_filter = {
            ChromaOperators.AND: [
                {EntityExamplesKeys.ENTITY_UUID: entity_uuid},
                {EntityExamplesKeys.TYPE: "list_items"},
                {EntityExamplesKeys.ORIGIN:"entity"}
            ]
        }

        try:
            chunks = self.__chroma_db_service.get_by_filter_sync(collection_name=collection_name,filter=metadata_filter)
            logger.info("Similarity search completed. Retrieved %d chunks.", len(chunks))
        except Exception as e:
            logger.error("Error during similarity search: %s", str(e))
            raise
        list_items_dict = {}
        for chunk in chunks:
            list_items_dict[str(chunk.id)] = chunk.document
        return list_items_dict

    def __fetch_entity_examples(
            self,
            entity_uuid: str,
            customer_uuid: str,
            application_uuid: str,
            ownership: str,
            collection_name: str
        ):
        """ helper function to fetch entity examples """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Build metadata filter for the query
        metadata_filter = {
            ChromaOperators.AND: [
                {EntityExamplesKeys.ENTITY_UUID: entity_uuid},
                {EntityExamplesKeys.TYPE: "example"},
                {EntityExamplesKeys.ORIGIN: "entity"}
            ]
        }
        try:
            chunks = self.__chroma_db_service.get_by_filter_sync(collection_name=collection_name, filter=metadata_filter)
            logger.info("Similarity search completed. Retrieved %d chunks.", len(chunks))
        except Exception as e:
            logger.error("Error during similarity search: %s", str(e))
            raise

        # Extract input-output pairs from the chunks
        examples = []
        logger.info("Processing retrieved chunks to construct examples.")
        for chunk in chunks:
            try:
                example = {
                    "input": chunk.document,
                    "output": chunk.metadata[EntityExamplesKeys.PROMPT_OUTPUT],
                    "id": chunk.id
                }
                examples.append(example)
                logger.debug("Processed chunk: %s", example)
            except KeyError as e:
                logger.warning("Missing key in chunk metadata: %s", str(e))
                continue

        logger.info("Successfully constructed %d examples.", len(examples))
        return examples

    def fetch_collection_name(self, ownership:str, application_uuid:str, customer_uuid:str):
        """ helper function to fetch collection_name dynamically """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        # Determine which collection to use based on the is_default flag
        if ownership.lower()==OwnerShipTypes.SYSTEM.value.lower():
            collection_name = settings.DEFAULT_ENTITY_COLLECTION_NAME
            logger.info("Using default collection: %s", collection_name)
            return collection_name
        elif ownership.lower()==OwnerShipTypes.CUSTOM.value.lower():
            collection_name = Utils.get_chroma_collection_name(
                customer_uuid, application_uuid, PREFIX_FOR_ENTITY_CHROMA_COLLECTION_NAME
            )
            logger.info("Using custom collection: %s", collection_name)
            return collection_name
        else:
            raise InvalidValueProvidedException(EntityErrorMessages.INVALID_OWNERSHIP)

    def __store_list_items(self, list_items:list, entity_uuid, entity_name, application_uuid, customer_uuid, collection_name):
        """ helper function to add list items in vectordb """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        if collection_name is None:
            collection_name = self.fetch_collection_name(ownership="CUSTOM", application_uuid=application_uuid, customer_uuid=customer_uuid)
        for item in list_items:
            chunk = Chunk(
                id=str(uuid4()),
                document=item,
                metadata={"entity_uuid": entity_uuid, "entity_name": entity_name, "origin": "entity", "type": "list_items"}
            )
            try:
                self.__chroma_db_service.add_chunks_sync(collection_name, [chunk])
            except Exception as e:
                logger.info(f"Cannot add list_item::{item} to chroma str{e}")
                raise CustomException(EntityErrorMessages.ADD_LIST_ITEM_FAILED.format(e=e),status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_wiseflow_entity(self, customer_uuid, application_uuid, user_uuid, data):
        """ method to create a custom entity"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        entity_name = data.get('entity_name')
        parent_entity_name = data.get('parent_entity_name')
        parent_entity_uuid = data.get('parent_entity_uuid')
        description = data.get('description')
        output_format = data.get('output_format')
        instructions = data.get('instructions')
        examples = data.get('examples')
        list_items = data.get('list_items')
        entity_uuid = str(uuid.uuid4())
        is_valid_parent_entity = self.entity_dao.is_valid_parent_entity(entity_uuid=parent_entity_uuid)
        if not is_valid_parent_entity:
            raise CustomException(f"Invalid parent_entity_uuid")
        if parent_entity_name == "regex":
            pattern = data.get("pattern")
            output_format = {"pattern": pattern}
        entity = self.entity_dao.create_wiseflow_entity(entity_uuid=entity_uuid, entity_name=entity_name, description=description, parent_entity_uuid=parent_entity_uuid, output_format=output_format, instructions=instructions, ownership="CUSTOM", application_uuid=application_uuid, customer_uuid=customer_uuid, user_uuid=user_uuid)
        try:
            # if examples not falsy value i.e not empty
            if examples:
                self.add_entity_examples(customer_uuid=customer_uuid, application_uuid=application_uuid, validated_payload={"entity_uuid": entity.entity_uuid, "entity_name": entity.entity_name, "examples": examples, "is_default": False})
        except Exception as e:
            logger.error(f"Error while adding examples to chroma {str(e)}")
            logger.debug(f"deleteing entity, since adding examples to chroma failed")
            self.entity_dao.delete_entity_by_customer_and_application(customer_uuid=customer_uuid, application_uuid=application_uuid, entity_uuid=entity.entity_uuid)
            raise CustomException(f"{str(e)}")

        try:
            # if list_items not falsy value i.e not empty
            if list_items:
                self.__store_list_items(list_items=list_items, entity_uuid=entity_uuid, entity_name=entity_name, application_uuid=application_uuid, customer_uuid=customer_uuid, collection_name=None)
        except Exception as e:
            logger.error(f"Error while adding list items to chroma {str(e)}")
            logger.debug(f"deleteing entity, since adding list items to chroma failed")
            self.entity_dao.delete_entity_by_customer_and_application(customer_uuid=customer_uuid, application_uuid=application_uuid, entity_uuid=entity.entity_uuid)
            raise CustomException(f"{str(e)}")
        return {"entity_name": entity.entity_name, "entity_uuid": entity.entity_uuid, "message": EntitySuccessMessages.ENTITY_CREATION_SUCCESS.format(entity_name=entity_name)}

    def get_wiseflow_entities(self, customer_uuid, application_uuid, validated_data):
        """fetches all wiseflow entities under customer and application"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        ownership = validated_data.get("ownership")
        if ownership.lower() == OwnerShipTypes.CUSTOM.value.lower():
            wiseflow_entities = self.entity_dao.get_wiseflow_entities_by_customer_and_application(customer_uuid=customer_uuid, application_uuid=application_uuid, ownership=ownership)
        elif ownership.lower() == OwnerShipTypes.SYSTEM.value.lower():
            wiseflow_entities = self.entity_dao.get_wiseflow_entities_by_customer_and_application(customer_uuid=None, application_uuid=None, ownership=ownership)
        else:
            raise InvalidValueProvidedException(EntityErrorMessages.INVALID_OWNERSHIP)
        # Paginate the combined queryset
        paginated_data, paginator = paginate_queryset(wiseflow_entities, validated_data)
        data = list(paginated_data.object_list)
        collections_name = self.fetch_collection_name(ownership="CUSTOM",application_uuid=application_uuid, customer_uuid=customer_uuid)
        for entity in data:
            if entity.get("parent_entity_name") == "list":
                list_items = self.__fetch_custom_list_items(entity_uuid=entity.get('entity_uuid'), customer_uuid=customer_uuid, application_uuid=application_uuid, ownership="CUSTOM",collection_name=collections_name)
                entity['list_items'] = list_items
            # if entity.get("ownership") == "SYSTEM":
            examples = self.__fetch_entity_examples(entity_uuid=entity.get('entity_uuid'), customer_uuid=customer_uuid, application_uuid=application_uuid, ownership=entity.get("ownership"),collection_name=collections_name)
            entity['examples'] = examples
        return {
            'page_number': paginated_data.number,
            'total_pages': paginator.num_pages,
            'total_entries': paginator.count,
            'data': data
        }

    def get_entity_by_entity_uuid(self, entity_uuid, customer_uuid, application_uuid):
        """fetch a particular entity under customer and application"""
        logger.info(f"Inside {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}")
        entity = self.entity_dao.get_entity_by_entity_uuid(entity_uuid=entity_uuid)
        single_entity = entity[0] if len(entity) > 0 else {}
        collections_name = self.fetch_collection_name(ownership="CUSTOM", application_uuid=application_uuid, customer_uuid=customer_uuid)
        if single_entity:
            if single_entity.get("parent_entity_name") == "list":
                list_items = self.__fetch_custom_list_items(entity_uuid=entity_uuid, customer_uuid=customer_uuid, application_uuid=application_uuid, ownership="CUSTOM", collection_name=collections_name)
                single_entity["list_items"] = list_items
            examples = self.__fetch_entity_examples(entity_uuid=entity_uuid, customer_uuid=customer_uuid, application_uuid=application_uuid, ownership=single_entity.get("ownership"), collection_name=collections_name)
            single_entity["examples"] = examples
        return single_entity

    def delete_wiseflow_entity(self, customer_uuid, application_uuid, entity_uuid):
        """deletes a particular entity under customer and application"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        is_system_entity = self.entity_dao.is_system_entity(entity_uuid)
        if is_system_entity:
            raise CustomException(f"This is system entity, which can't be deleted")
        self.__delete_chroma_data(entity_uuid=entity_uuid, customer_uuid=customer_uuid, application_uuid=application_uuid, ownership="CUSTOM")
        deleted, _ = self.entity_dao.delete_entity_by_customer_and_application(customer_uuid=customer_uuid, application_uuid=application_uuid, entity_uuid=entity_uuid)

        if deleted == 0:
            raise CustomException("No entity found with given entity_uuid")

        logger.debug(f"entity with entity_uuid:{entity_uuid} is deleted successfully for customer:{customer_uuid} and application_uuid:{application_uuid}")

    def __delete_chroma_data(self, entity_uuid: str, customer_uuid: str, application_uuid: str, ownership: str):
        """ helper function to delete chroma data """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        collection_name = self.fetch_collection_name(ownership=ownership, application_uuid=application_uuid, customer_uuid=customer_uuid)
        try:
            self.__chroma_db_service.delete_by_filter_sync(collection_name=collection_name, filter={"entity_uuid":entity_uuid})
        except Exception as e:
            logger.error(f"Error while deleting chroma data for entity_uuid::{entity_uuid} :: {str(e)}")
            raise CustomException(f"error while deleting chroma data:: {str(e)}")

    def update_entity(self, customer_uuid, application_uuid, validated_data):
        """update a particular entity under customer and application"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        entity_uuid = validated_data.get("entity_uuid")
        entity_name = validated_data.get("entity_name")
        description = validated_data.get("description")
        instructions = validated_data.get("instructions")
        output_format = validated_data.get("output_format")
        parent_entity_name = validated_data.get("parent_entity_name")
        pattern = validated_data.get("pattern")
        entity = self.entity_dao.get_entity_by_uuid(entity_uuid=entity_uuid)
        if not entity:
            raise CustomException(f"Entity doesn't exist")
        collection_name = self.fetch_collection_name("CUSTOM", application_uuid=application_uuid, customer_uuid=customer_uuid)

        if parent_entity_name == "list":
            self.__update_list_items(entity_uuid=entity_uuid, entity_name=entity.entity_name, customer_uuid=customer_uuid, application_uuid=application_uuid, validated_data=validated_data, collection_name=collection_name)
        self.__update_examples(entity_uuid=entity_uuid, entity_name=entity.entity_name, customer_uuid=customer_uuid, application_uuid=application_uuid, validated_data=validated_data, collection_name=collection_name)

        # updating entity fields
        entity.entity_name = entity_name
        entity.description = description
        entity.instructions = instructions
        if parent_entity_name == "regex":
            output_format = {"pattern": pattern}
        entity.output_format = output_format
        # calling save method to update entity
        self.entity_dao.save_entity(entity_instance=entity)

    def __update_list_items(self, entity_uuid, entity_name, customer_uuid, application_uuid, validated_data, collection_name):
        """ helper function to update list items for an entity in vectordb """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        edit_list_item = validated_data.get("edit_list_item")
        add_list_item = validated_data.get("add_list_item")
        delete_list_item = validated_data.get("delete_list_item")
        if add_list_item:
            self.__store_list_items(list_items=add_list_item,entity_uuid=entity_uuid,entity_name=entity_name,application_uuid=application_uuid, customer_uuid=customer_uuid, collection_name=collection_name)
        if edit_list_item:
            ids = list(edit_list_item.keys())
            list_items = list(edit_list_item.values())
            self.__chroma_db_service.update_documents_sync(collection_name=collection_name,ids=ids, documents=list_items)
        if delete_list_item:
                self.__chroma_db_service.delete_by_ids_sync(collection_name=collection_name, ids=delete_list_item)

    def __update_examples(self, entity_uuid, entity_name, customer_uuid, application_uuid, validated_data, collection_name):
        """ helper function to update examples for an entity in vectordb """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        edit_example = validated_data.get("edit_example")
        add_example = validated_data.get("add_example")
        delete_example = validated_data.get("delete_example")
        if add_example:
            self.add_entity_examples(customer_uuid=customer_uuid, application_uuid=application_uuid, validated_payload={"entity_uuid": entity_uuid, "entity_name": entity_name, "examples": add_example, "is_default": False})
        if edit_example:
            example_chunk_ids, input, chunk_id_output_mapping = self.__fetch_example_chunk_ids_input(edit_example=edit_example)
            self.__chroma_db_service.update_documents_sync(collection_name=collection_name, ids=example_chunk_ids, documents=input)
            new_metadata_list = self.__fetch_new_metadata_with_updated_output(collection_name=collection_name, example_chunk_ids=example_chunk_ids, chunk_id_output_mapping=chunk_id_output_mapping)
            self.__chroma_db_service.update_metadatas_sync(collection_name=collection_name,ids=example_chunk_ids,metadatas=new_metadata_list)
        if delete_example:
            self.__chroma_db_service.delete_by_ids_sync(collection_name=collection_name, ids=delete_example)

    def __fetch_example_chunk_ids_input(self, edit_example):
        """ helper function to fetch chunk ids, mapping with output from request edit_example"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        chunk_ids = []
        input = []
        chunk_id_output_mapping = {}
        for example in edit_example:
            chunk_ids.append(example.get("id"))
            input.append(example.get("input"))
            chunk_id_output_mapping[example.get("id")] = example.get("output")
        return chunk_ids, input, chunk_id_output_mapping

    def __fetch_new_metadata_with_updated_output(self, collection_name, example_chunk_ids, chunk_id_output_mapping):
        """ helper function to fetch updated metadata to update in vectordb """
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        chunks_list = self.__chroma_db_service.get_by_ids_sync(collection_name=collection_name, ids=example_chunk_ids)
        new_metadata_list = []
        for chunk in chunks_list:
            metadata = chunk.metadata
            metadata["prompt_output"] = chunk_id_output_mapping.get(chunk.id)
            new_metadata_list.append(metadata)
        return new_metadata_list

    def get_parent_entities(self):
        """fetches parent entities"""
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        parent_entities = self.entity_dao.fetch_parent_entities("CUSTOM")

        return parent_entities
