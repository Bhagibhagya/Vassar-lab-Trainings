from dataclasses import dataclass, field, asdict
from typing import Optional, Any
import uuid
from datetime import datetime


@dataclass
class RoleData:
    role_name: str
    role_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    role_details_json: Optional[Any] = None
    application_uuid: Optional[str] = None
    customer_uuid: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = True
    created_ts: datetime = field(default_factory=datetime.now)
    updated_ts: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    def to_dict(self):
        """
            Converts the dataclass instance to a dictionary.
        """
        # Convert the dataclass instance to a dictionary using asdict
        user_dict = asdict(self)
        return user_dict

