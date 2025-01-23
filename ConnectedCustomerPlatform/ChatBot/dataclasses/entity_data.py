from dataclasses import  dataclass
from typing import List, Dict, Optional
from uuid import UUID

@dataclass
class AttributeDetailsJson:
    entity_name: str
    attributes: Dict[str, List[str]]


@dataclass
class Entity:
    entity_uuid: UUID
    entity_name: str
    description: str
    attribute_details_json: AttributeDetailsJson
    customer_uuid: str
    application_uuid: str
    is_default: Optional[bool] = False