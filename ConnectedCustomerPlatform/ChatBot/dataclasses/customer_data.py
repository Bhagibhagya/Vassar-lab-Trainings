from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


@dataclass
class CustomerData:
    customer_name: str
    email: str
    primary_contact: str
    customer_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    purchased_plan: Optional[str] = None
    secondary_contact: Optional[str] = None
    address: Optional[str] = None
    billing_address: Optional[str] = None
    customer_details_json: Optional[Any] = None
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
