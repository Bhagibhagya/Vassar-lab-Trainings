from dataclasses import dataclass


@dataclass
class ExampleMetadata:
    entity_uuid: str
    entity_name: str
    prompt_output: str
    origin : str
    type : str