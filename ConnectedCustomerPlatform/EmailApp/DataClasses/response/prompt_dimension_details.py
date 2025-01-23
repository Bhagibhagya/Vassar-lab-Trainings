from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any

@dataclass
class CustomerClient:
    uuid: Optional[str] = None
    name: Optional[str] = None

@dataclass
class SubIntent:
    uuid: Optional[str] = None
    name: Optional[str] = None

#each instance of the dataclass gets its own unique default value for mutable types, avoiding unintended shared state between instances
@dataclass
class Intent:
    uuid: Optional[str] = None
    name: Optional[str] = None
    sub_intent: SubIntent = field(default_factory=SubIntent)

@dataclass
class PromptDimensionDetails:
    customer_client: CustomerClient = field(default_factory=CustomerClient)
    intent: Intent = field(default_factory=Intent)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'PromptDimensionDetails':
        customer_client_data = data.get('customer_client', {})
        intent_data = data.get('intent', {})
        sub_intent_data = intent_data.get('sub_intent', {})

        customer_client = CustomerClient(**customer_client_data)
        sub_intent = SubIntent(**sub_intent_data)
        intent = Intent(
            uuid=intent_data.get('uuid',''),
            name=intent_data.get('name',''),
            sub_intent=sub_intent
        )

        return cls(
            customer_client=customer_client,
            intent=intent
        )

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)
