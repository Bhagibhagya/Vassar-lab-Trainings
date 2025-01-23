from dataclasses import dataclass
from typing import List

@dataclass
class Customer:
    customer_client_uuid: str
    customer_client_name: str
    geography: str
    customer_tier: str
    total_mails: int
    inserted_ts: int
    updated_ts: int