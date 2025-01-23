from dataclasses import dataclass, asdict
from typing import Optional, Dict


@dataclass
class MakeRequestData:
    request_method: str
    api_url: str
    headers: Optional[Dict[str, str]] = None
    payload: Optional[Dict] = None
    query_params: Optional[Dict[str, str]] = None

    def to_dict(self):
        """
                        Converts the dataclass instance to a dictionary.
                """
        # Convert the dataclass instance to a dictionary using asdict
        request_dict = asdict(self)
        return request_dict

