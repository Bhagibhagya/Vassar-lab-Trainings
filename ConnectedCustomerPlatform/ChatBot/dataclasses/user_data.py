from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from datetime import datetime
import uuid


@dataclass
class UserData:
    user_name: str
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_id: Optional[str] = None
    mobile_number: Optional[str] = None
    auth_type: Optional[str] = None
    title: Optional[str] = None
    user_details_json: Optional[Any] = None
    customer_name: Optional[str] = None
    customer_id: Optional[str] = None
    status: Optional[bool] = True
    password_hash: Optional[str] = None
    activation_ts: Optional[datetime] = None
    password_last_updated_at: Optional[datetime] = None
    last_login_ts: Optional[datetime] = None
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
