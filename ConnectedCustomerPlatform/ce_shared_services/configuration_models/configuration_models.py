from abc import ABC
from typing import Optional, List, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict, PositiveInt

from ce_shared_services.llm.interface.llm import LLM
from ce_shared_services.vectordb.interface.vectordb import VectorDB

class HashableConfigBase(BaseModel, ABC):
    """
    Base class for configuration models that need to be hashable.
    Provides implementations for __hash__ and __eq__ methods.
    """
    model_config = ConfigDict(validate_assignment=True)

    def __hash__(self):
        """
        Creates a hash based on the model's JSON representation.
        This ensures that instances with the same values have the same hash.
        """
        return hash(frozenset(self.model_dump_json()))

    def __eq__(self, other) -> bool:
        """
        Compares two config instances based on their model data.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.model_dump() == other.model_dump()


class AzureBlobConfig(HashableConfigBase):
    """
        Configuration settings for connecting to Azure Blob Storage.

        This class encapsulates all necessary parameters to configure Azure Blob
        Storage interactions, including connection details, retry mechanisms,
        and size limitations for various operations.

        Attributes:
            azure_connection_string (str): The connection string required to access the Azure storage account.
            container_name (str): Name of the specific blob container within the Azure storage account.
            max_retries (int): Maximum number of retry attempts in case of failed operations (must be greater than 0).
            initial_backoff (int): Initial delay (in seconds) before retrying a failed operation (must be greater than 0) for azure Exponential Retry mechanism used for getting container client.
            increment_base(int): The base, in seconds, to increment the initial_backoff by after the first retry.
                                #increment_base = exponential growth factor
                                #next_backoff = initial_backoff * (increment_base ^ retry_attempt)
            memory_limit (int): The maximum memory size (in bytes) allocated for buffer or cache purposes (must be greater than 0).
            max_single_put_size (int): The maximum size (in bytes) of a single put operation to Azure Blob (must be at least 1024 bytes).
            max_single_get_size (int): The maximum size (in bytes) for a single get operation from Azure Blob (must be at least 1024 bytes).
            max_chunk_get_size (int): The size (in bytes) for each chunk when downloading data in parts (must be at least 1024 bytes).
            max_block_size (int): The size (in bytes) of each block when uploading in blocks (must be at least 1024 bytes).
            max_concurrency(int): Number of parallel connections(must be greater than 1)
        """
    azure_connection_string: str = Field(..., description="Azure connection string")
    container_name: str = Field(..., description="Azure Blob container name")
    max_retries: int = Field(3, gt=0, description="Maximum number of retries")
    initial_backoff: int = Field(15, gt=0, description="Initial backoff time in seconds for azure retry mechanism")
    increment_base: int = Field(3, gt=0, description="The base, in seconds, to increment the initial_backoff by after the first retry for azure retry mechanism.")
    memory_limit: int = Field(..., gt=0, description="Memory size in bytes")
    max_single_put_size: int = Field(64*1024*1024, ge=1024, description="Maximum single put size in bytes")
    max_single_get_size: int = Field(32*1024*1024, ge=1024, description="Maximum single get size in bytes")
    max_chunk_get_size: int = Field(4*1024*1024, ge=1024, description="Maximum chunk get size in bytes")
    max_block_size: int = Field(4*1024*1024, ge=1024, description="Maximum block size in bytes")
    max_concurrency: int = Field(1,ge=1, description = "Maximum parallel connections")
    model_config = ConfigDict(validate_assignment=True)

    # Attributes that are immutable
    _immutable_fields = {"azure_connection_string", "container_name"}

    def __setattr__(self, name, value):
        # Check if the field is immutable
        if name in self._immutable_fields:
            raise AttributeError(f"The attribute '{name}' is immutable and cannot be modified.")
        # Allow setting the attribute if it's not immutable
        super().__setattr__(name, value)

    @classmethod
    def instantiate(cls,
        azure_connection_string: str,
        container_name: str,
        memory_limit: int,
        max_concurrency: int,
        **kwargs):
        return cls(
            azure_connection_string=azure_connection_string,
            container_name=container_name,
            memory_limit=memory_limit,
            max_concurrency=max_concurrency,
            **kwargs
        )


    @field_validator('*', mode='before')
    def check_non_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError('Field cannot be empty')
        return v


class RedisConfig(HashableConfigBase):
    """
    Configuration for Redis connection.

    Attributes:
        host (str): Hostname or IP address of the Redis server.
        port (int): Port number of the Redis server.
        db (int): Redis database index to connect to.
        password (Optional[str]): Password for authenticating with Redis (if required).
        connection_pool_size (int): Maximum number of connections supported by the Redis connection pool.
        decode_responses (bool): Whether to decode Redis responses by default (default: True).
        max_retries (int): The number of maximum retry attempts (default: 3).
    """
    host: str = Field(..., description="The hostname or IP of the Redis server.")
    port: PositiveInt = Field(6379, description="The port of the Redis server.")
    db: int = Field(0, ge=0, description="The Redis database index.")
    password: str | None = Field(None, description="The password, if required, to access Redis.")
    connection_pool_size: PositiveInt = Field(10, description="The size of the Redis connection pool.")
    decode_responses: bool = Field(True, description="Whether to decode Redis responses by default.")
    max_retries: PositiveInt = Field(3, ge=0, description="The number of maximum retry attempts.")

    model_config = ConfigDict(validate_assignment=True)


class AzureKeyVaultConfig(HashableConfigBase):
    """
        Configuration settings for connecting to Azure Keyvault.

        This class encapsulates all necessary parameters to configure Azure Keyvault interactions, including connection details,
        expires_on, type, etc.

        Attributes:
            keyvault_url (str): The keyvault url to connect.
            client_id (str): Managed Identity credential client id.
        """
    vault_url: str = Field(..., description="Azure Keyvault url")
    client_id: str = Field(..., description="Client Id")

    model_config = ConfigDict(validate_assignment=True)



class VariableConfig(HashableConfigBase):
    name: str = Field(..., description="Variable name (underscore notation)")
    type: str = Field(..., description="Type of the variable (entity, string, number, boolean)")
    #if entity type then entity uuid will be stored
    entity: Optional[str] = Field(None, description="Associated entity UUID if type is 'entity'")
    #value will be updated at run time
    value: Optional[Union[str, int, bool,dict]] = Field(None, description="Value if type is string, number, or boolean")
    owner :str = Field(...,description = "ownership of variable") #'SYSTEM','flow'


class SpecificationConfig(HashableConfigBase):
    name: str = Field(..., description="Name of the specification")
    variable: VariableConfig = Field(..., description="Variable associated with the entity")
    additional_context: Optional[str] = Field(None, description="Additional instructions for handling the entity")


class IntentValue(HashableConfigBase):
    id: Optional[str] = Field(None, description="Unique identifier for the intent or sub-intent")
    name: Optional[str] = Field(None, description="Name of the intent or sub-intent")


class IntentSpecificationConfig(IntentValue):
    """Model for INTENTS/SUB_INTENTS."""
    description: Optional[str] = Field(None, description="Description of the intent or sub-intent")
    specifications: Optional[List[SpecificationConfig]] = Field(None, description="List of linked specifications")



class IntentSubIntentsConfig(IntentSpecificationConfig):
    """Model for main intents, which can include sub-intents."""
    sub_intents: Optional[List[IntentSpecificationConfig]] = Field(None, description="List of sub-intents under the intent")



# class IntentDataConfig(HashableConfigBase):
#     id: str = Field(..., description="Unique identifier for the sub-intent")
#     name: str = Field(..., description="Name of the sub-intent")
#     description: Optional[str] = Field(None, description="Description of the sub-intent")
#     specifications: Optional[List[SpecificationConfig]] = Field(None, description="List of linked specifications")
#
#
# class IntentConfig(HashableConfigBase):
#     id: Optional[str] = Field(None, description="Unique identifier for the intent")
#     name: Optional[str] = Field(None, description="Name of the intent")
#     description: Optional[str] = Field(None, description="Description of the intent")
#     sub_intents: Optional[List[IntentDataConfig]] = Field(None, description="List of sub-intents under the intent")
#     specifications: Optional[List[SpecificationConfig]] = Field(None, description="List of linked specifications")


class IntentClassificationConfig(HashableConfigBase):
    #id: str = Field(..., description="Unique identifier for the intent classification configuration")
    selected_intents: List[IntentSubIntentsConfig] = Field(
        ..., description="List of selected intents with sub-intents and specifications"
    )
    similarity_threshold : int =Field(90,description="Threshold value for similarity search")
    conversation_history_n: int = Field(..., description="Number of most recent messages to include in context")
    examples_n: int = Field(..., description="Number of examples to include in context")
    intent_prompt: dict = Field(..., description="Prompt for intent classification")
    sub_intent_prompt: Optional[dict] = Field(None, description="Prompt for sub-intent classification")
    specification_prompt: Optional[dict] = Field(None, description="Prompt for specification handling")
    vector_store: VectorDB = Field(..., description="Vector Store instance")
    llm: LLM = Field(..., description="LLM instance")
    collection_name : Optional[str] = Field(...,description="Chroma collection Name")
    llm_max_retires: int = Field(...,description="LLM max retires")
    llm_initial_delay: int = Field(...,description="LLM initial Delay")
    variables: Optional[List[VariableConfig]] = Field(None, description="variables")

    class Config:
        arbitrary_types_allowed = True
