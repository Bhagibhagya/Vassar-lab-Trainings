from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass
class FileAttributeDetailsJson:
    entity_name: str
    attributes: Dict[str, str]

@dataclass
class FormattedJson:
    value: Any
    block_id: str
    type: str
    content_type: str
    page: str
    label: str
    required: bool = True
    text_type: Optional[str] = None
    classification: Optional[Any] = None
    json_key: Optional[str] = None
    is_hierarchy: Optional[bool] = False
    is_simple_table_view: Optional[bool] = False

    def to_dict(self):
        # Use asdict to recursively convert dataclasses to dictionaries
        return asdict(self)
