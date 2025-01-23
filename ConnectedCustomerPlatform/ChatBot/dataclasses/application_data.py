from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


@dataclass
class ApplicationData:
    application_name: str
    application_url: str
    scope_end_point: str
    application_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
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
