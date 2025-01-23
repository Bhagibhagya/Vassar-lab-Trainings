from dataclasses import dataclass, field
import logging
from typing import Union, Dict, List, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class State:
    uuid: str


@dataclass
class Country:
    uuid: str
    states: Union[List[State], str]

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, dict):
            country_uuid = json_data.get("uuid", "")
            states = [State(uuid=state_data.get("uuid", "")) for state_data in json_data.get("state", [])]
            return cls(uuid=country_uuid, states=states)
        elif isinstance(json_data, str):
            return cls(uuid=json_data, states="")

    def set_data(self, states: Union[List[State], str]) -> None:
        self.states = states

    def get_data(self) -> Union[List[State], str]:
        return self.states


@dataclass
class GeographyData:
    countries: Union[List[Country], str] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, list):
            countries = [Country.from_json(country_data) for country_data in json_data]
            return cls(countries=countries)
        elif isinstance(json_data, str):
            return cls(countries=json_data)

    def set_data(self, countries: Union[List[Country], str]) -> None:
        self.countries = countries

    def get_data(self) -> Union[List[Country], str]:
        return self.countries


@dataclass
class SubIntent:
    uuid: str


from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class SubIntent:
    uuid: str


@dataclass
class Intent:
    uuid: str
    sub_intents: Union[List[SubIntent], str]

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, dict):
            intent_uuid = json_data.get("uuid", "")
            sub_intents = [SubIntent(uuid=sub_intent_data.get("uuid", "")) for sub_intent_data in
                           json_data.get("sub_intent", [])]
            return cls(uuid=intent_uuid, sub_intents=sub_intents)
        elif isinstance(json_data, str):
            return cls(uuid=json_data, sub_intents="")

    def set_data(self, sub_intents: Union[List[SubIntent], str]) -> None:
        self.sub_intents = sub_intents

    def get_data(self) -> Union[List[SubIntent], str]:
        return self.sub_intents


@dataclass
class IntentData:
    intents: Union[List[Intent], str] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, list):
            intents = [Intent.from_json(intent_data) for intent_data in json_data]
            return cls(intents=intents)
        elif isinstance(json_data, str):
            return cls(intents=json_data)

    def set_data(self, intents: Union[List[Intent], str]) -> None:
        self.intents = intents

    def get_data(self) -> Union[List[Intent], str]:
        return self.intents


@dataclass
class Sentiment:
    uuid: str


@dataclass
class SentimentData:
    sentiments: Union[List[Sentiment], str] = field(default_factory=list)

    def __str__(self):
        return f"SentimentData{{sentiments={self.sentiments}}}"

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, list):
            sentiments = [Sentiment(uuid=sentiment_data.get("uuid", "")) for sentiment_data in json_data]
            return cls(sentiments=sentiments)
        elif isinstance(json_data, str):
            return cls(sentiments=json_data)

    def set_data(self, sentiments: Union[List[Sentiment], str]) -> None:
        self.sentiments = sentiments

    def get_data(self) -> Union[List[Sentiment], str]:
        return self.sentiments


@dataclass
class CustomerTier:
    uuid: str


@dataclass
class CustomerTierData:
    tiers: Union[List[CustomerTier], str] = field(default_factory=list)

    def __str__(self):
        return f"CustomerTierData{{tiers={self.tiers}}}"

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, list):
            tiers = [CustomerTier(uuid=tier_data.get('uuid', "")) for tier_data in json_data]
            return cls(tiers=tiers)
        elif isinstance(json_data, str):
            return cls(tiers=json_data)

    def set_data(self, tiers: Union[List[CustomerTier], str]) -> None:
        self.tiers = tiers

    def get_data(self) -> Union[List[CustomerTier], str]:
        return self.tiers


@dataclass
class DimensionsValidator:
    @staticmethod
    def validate_customer_tier(customer_tier: CustomerTierData, customer_tier_uuid) -> bool:
        customer_tier_data = customer_tier.get_data()
        if isinstance(customer_tier_data, str) and customer_tier_data == "*":
            return True
        if not isinstance(customer_tier_data, list):
            return False

        return customer_tier_uuid in [tier.uuid for tier in customer_tier_data]

    @staticmethod
    def validate_geography(geography: GeographyData, country_uuid: str, state_uuid: str) -> bool:
        countries = geography.get_data()
        if isinstance(countries, str) and countries == "*":
            return True
        if not isinstance(countries, list):
            return False
        for country in countries:
            if country.uuid != country_uuid:
                return False
            if not state_uuid:
                return True
            if isinstance(country.states, str) and country.states == "*":
                return True
            if isinstance(country.states, list) and state_uuid in [state.uuid for state in country.states]:
                return True
        return False

    @staticmethod
    def validate_intent(intent: IntentData, intent_uuid, sub_intent_uuid) -> bool:
        intents = intent.get_data()
        if isinstance(intents, str) and intents == "*":
            return True
        if not isinstance(intents, list):
            return False
        for intent_obj in intents:
            if intent_obj.uuid != intent_uuid:
                return False
            if not sub_intent_uuid:
                return True
            if isinstance(intent_obj.sub_intents, str) and intent_obj.sub_intents == "*":
                return True
            if isinstance(intent_obj.sub_intents, list) and sub_intent_uuid in [sub_intent.uuid for sub_intent in
                                                                                intent_obj.sub_intents]:
                return True
        return False

    @staticmethod
    def validate_sentiment(sentiment: SentimentData, sentiment_uuid) -> bool:
        sentiments = sentiment.get_data()
        if isinstance(sentiments, str) and sentiments == "*":
            return True
        if not isinstance(sentiments, list):
            return False
        return sentiment_uuid in [sentiment.uuid for sentiment in sentiments]


@dataclass
class DimensionsDetails:
    geography: GeographyData = field(default_factory=GeographyData)
    intent: IntentData = field(default_factory=IntentData)
    sentiment: SentimentData = field(default_factory=SentimentData)
    customer_tier: CustomerTierData = field(default_factory=CustomerTierData)

    @classmethod
    def from_json(cls, json_data):
        try:
            geography_data = json_data.get('geography', {}).get('country', [])
            intent_data = json_data.get('intent', [])
            sentiment_data = json_data.get('sentiment', [])
            customer_tier_data = json_data.get('customer_tier', [])

            return cls(
                geography=GeographyData.from_json(geography_data),
                intent=IntentData.from_json(intent_data),
                sentiment=SentimentData.from_json(sentiment_data),
                customer_tier=CustomerTierData.from_json(customer_tier_data)
            )
        except Exception as e:
            logger.error(f"Error while parsing JSON data: {e}")
            return cls()

    def action_rule_validation(self, dimension_action_json: Dict[str, Any]) -> bool:

        try:
            customer_tier_uuid = dimension_action_json.get("customer_tier", {}).get("uuid", "")
            country_uuid = dimension_action_json.get("geography", {}).get("country", {}).get("uuid", "")
            state_uuid = dimension_action_json.get("geography", {}).get("country", {}).get("state", {}).get("uuid", "")
            intent_uuid = dimension_action_json.get("intent", {}).get("uuid", "")
            sub_intent_uuid = dimension_action_json.get("intent", {}).get("sub_intent", {}).get("uuid", "")
            sentiment_uuid = dimension_action_json.get("sentiment", {}).get("uuid", "")

            validation_results = {}

            if customer_tier_uuid:
                validation_results['customer_tier'] = DimensionsValidator.validate_customer_tier(self.customer_tier,
                                                                                                 customer_tier_uuid)
            if country_uuid:
                validation_results['geography'] = DimensionsValidator.validate_geography(self.geography, country_uuid,
                                                                                         state_uuid)
            if intent_uuid:
                validation_results['intent'] = DimensionsValidator.validate_intent(self.intent, intent_uuid,
                                                                                   sub_intent_uuid)
            if sentiment_uuid:
                validation_results['sentiment'] = DimensionsValidator.validate_sentiment(self.sentiment, sentiment_uuid)

            return all(validation_results.values())
        except Exception as e:
            logger.error(f"Error during action rule validation: {e}")
            return False

    def __str__(self):
        return f"DimensionsDetails{{geography={self.geography}, intent={self.intent}, sentiment={self.sentiment}, customer_tier={self.customer_tier}}}"

    def get_geography_data(self) -> List[Country]:
        return self.geography.get_data()

    def get_intent_data(self) -> List[Intent]:
        return self.intent.get_data()

    def get_sentiment_data(self) -> List[Sentiment]:
        return self.sentiment.get_data()

    def get_customer_tier_data(self) -> List[CustomerTier]:
        return self.customer_tier.get_data()