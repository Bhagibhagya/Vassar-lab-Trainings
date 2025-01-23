from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class CustomerTier:
    uuid: Optional[str] = None
    name: Optional[str] = None


@dataclass
class CustomerClient:
    uuid: Optional[str] = None
    name: Optional[str] = None


@dataclass
class State:
    uuid: Optional[str] = None
    name: Optional[str] = None


@dataclass
class Country:
    uuid: Optional[str] = None
    name: Optional[str] = None
    state: State = field(default_factory=State)


@dataclass
class Geography:
    country: Country = field(default_factory=Country)


@dataclass
class SubIntent:
    uuid: Optional[str] = None
    name: Optional[str] = None

#Each instance of the dataclass gets its own unique default value for mutable types, avoiding unintended shared state between instances
@dataclass
class Intent:
    uuid: Optional[str] = None
    name: Optional[str] = None
    sub_intent: SubIntent = field(default_factory=SubIntent)


@dataclass
class Sentiment:
    uuid: Optional[str] = None
    name: Optional[str] = None
