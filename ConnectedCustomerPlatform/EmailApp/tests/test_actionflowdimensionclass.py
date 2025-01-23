import unittest
from EmailApp.ActionFlowDimensionClass import Country, State, Intent,SubIntent,Sentiment,CustomerTier
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from EmailApp.ActionFlowDimensionClass import DimensionsDetails, DimensionsValidator, CustomerTierData, GeographyData, IntentData, SentimentData


class TestCountry(unittest.TestCase):
    def test_from_json_with_dict(self):
        json_data = {
            "uuid": "country-123",
            "state": [
                {"uuid": "state-1"},
                {"uuid": "state-2"}
            ]
        }
        country = Country.from_json(json_data)
        self.assertEqual(country.uuid, "country-123")
        self.assertEqual(len(country.states), 2)
        self.assertEqual(country.states[0].uuid, "state-1")
        self.assertEqual(country.states[1].uuid, "state-2")
    
    def test_from_json_with_str(self):
        json_data = "country-123"
        country = Country.from_json(json_data)
        self.assertEqual(country.uuid, "country-123")
        self.assertEqual(country.states, "")
    
    def test_set_data_with_list(self):
        country = Country(uuid="country-123", states=[])
        states = [State(uuid="state-1"), State(uuid="state-2")]
        country.set_data(states)
        self.assertEqual(len(country.states), 2)
        self.assertEqual(country.states[0].uuid, "state-1")
        self.assertEqual(country.states[1].uuid, "state-2")
    
    def test_set_data_with_str(self):
        country = Country(uuid="country-123", states=[])
        country.set_data("state-123")
        self.assertEqual(country.states, "state-123")
    
    def test_get_data_with_list(self):
        states = [State(uuid="state-1"), State(uuid="state-2")]
        country = Country(uuid="country-123", states=states)
        self.assertEqual(country.get_data(), states)
    
    def test_get_data_with_str(self):
        country = Country(uuid="country-123", states="state-123")
        self.assertEqual(country.get_data(), "state-123")


class TestGeographyData(unittest.TestCase):
    def test_from_json_with_list(self):
        json_data = [
            {
                "uuid": "country-123",
                "state": [
                    {"uuid": "state-1"},
                    {"uuid": "state-2"}
                ]
            },
            {
                "uuid": "country-456",
                "state": [
                    {"uuid": "state-3"},
                    {"uuid": "state-4"}
                ]
            }
        ]
        geography_data = GeographyData.from_json(json_data)
        self.assertEqual(len(geography_data.countries), 2)
        self.assertEqual(geography_data.countries[0].uuid, "country-123")
        self.assertEqual(geography_data.countries[0].states[0].uuid, "state-1")
        self.assertEqual(geography_data.countries[1].uuid, "country-456")
        self.assertEqual(geography_data.countries[1].states[1].uuid, "state-4")
    
    def test_from_json_with_str(self):
        json_data = "country-123"
        geography_data = GeographyData.from_json(json_data)
        self.assertEqual(geography_data.countries, "country-123")
    
    def test_set_data_with_list(self):
        geography_data = GeographyData()
        countries = [
            Country(uuid="country-123", states=[State(uuid="state-1"), State(uuid="state-2")]),
            Country(uuid="country-456", states=[State(uuid="state-3"), State(uuid="state-4")])
        ]
        geography_data.set_data(countries)
        self.assertEqual(len(geography_data.countries), 2)
        self.assertEqual(geography_data.countries[0].uuid, "country-123")
        self.assertEqual(geography_data.countries[1].uuid, "country-456")
    
    def test_set_data_with_str(self):
        geography_data = GeographyData()
        geography_data.set_data("country-123")
        self.assertEqual(geography_data.countries, "country-123")
    
    def test_get_data_with_list(self):
        countries = [
            Country(uuid="country-123", states=[State(uuid="state-1"), State(uuid="state-2")]),
            Country(uuid="country-456", states=[State(uuid="state-3"), State(uuid="state-4")])
        ]
        geography_data = GeographyData(countries=countries)
        self.assertEqual(geography_data.get_data(), countries)
    
    def test_get_data_with_str(self):
        geography_data = GeographyData(countries="country-123")
        self.assertEqual(geography_data.get_data(), "country-123")


class TestIntent(unittest.TestCase):
    def test_from_json_with_dict(self):
        json_data = {
            "uuid": "intent-123",
            "sub_intent": [
                {"uuid": "sub_intent-1"},
                {"uuid": "sub_intent-2"}
            ]
        }
        intent = Intent.from_json(json_data)
        self.assertEqual(intent.uuid, "intent-123")
        self.assertEqual(len(intent.sub_intents), 2)
        self.assertEqual(intent.sub_intents[0].uuid, "sub_intent-1")
        self.assertEqual(intent.sub_intents[1].uuid, "sub_intent-2")
    
    def test_from_json_with_str(self):
        json_data = "intent-123"
        intent = Intent.from_json(json_data)
        self.assertEqual(intent.uuid, "intent-123")
        self.assertEqual(intent.sub_intents, "")
    
    def test_set_data_with_list(self):
        intent = Intent(uuid="intent-123", sub_intents=[])
        sub_intents = [SubIntent(uuid="sub_intent-1"), SubIntent(uuid="sub_intent-2")]
        intent.set_data(sub_intents)
        self.assertEqual(len(intent.sub_intents), 2)
        self.assertEqual(intent.sub_intents[0].uuid, "sub_intent-1")
        self.assertEqual(intent.sub_intents[1].uuid, "sub_intent-2")
    
    def test_set_data_with_str(self):
        intent = Intent(uuid="intent-123", sub_intents=[])
        intent.set_data("sub_intent-123")
        self.assertEqual(intent.sub_intents, "sub_intent-123")
    
    def test_get_data_with_list(self):
        sub_intents = [SubIntent(uuid="sub_intent-1"), SubIntent(uuid="sub_intent-2")]
        intent = Intent(uuid="intent-123", sub_intents=sub_intents)
        self.assertEqual(intent.get_data(), sub_intents)
    
    def test_get_data_with_str(self):
        intent = Intent(uuid="intent-123", sub_intents="sub_intent-123")
        self.assertEqual(intent.get_data(), "sub_intent-123")

class TestIntentData(unittest.TestCase):
    def test_from_json_with_list(self):
        json_data = [
            {
                "uuid": "intent-123",
                "sub_intent": [
                    {"uuid": "sub_intent-1"},
                    {"uuid": "sub_intent-2"}
                ]
            },
            {
                "uuid": "intent-456",
                "sub_intent": [
                    {"uuid": "sub_intent-3"},
                    {"uuid": "sub_intent-4"}
                ]
            }
        ]
        intent_data = IntentData.from_json(json_data)
        self.assertEqual(len(intent_data.intents), 2)
        self.assertEqual(intent_data.intents[0].uuid, "intent-123")
        self.assertEqual(intent_data.intents[0].sub_intents[0].uuid, "sub_intent-1")
        self.assertEqual(intent_data.intents[1].uuid, "intent-456")
        self.assertEqual(intent_data.intents[1].sub_intents[1].uuid, "sub_intent-4")
    
    def test_from_json_with_str(self):
        json_data = "intent-123"
        intent_data = IntentData.from_json(json_data)
        self.assertEqual(intent_data.intents, "intent-123")
    
    def test_set_data_with_list(self):
        intent_data = IntentData()
        intents = [
            Intent(uuid="intent-123", sub_intents=[SubIntent(uuid="sub_intent-1"), SubIntent(uuid="sub_intent-2")]),
            Intent(uuid="intent-456", sub_intents=[SubIntent(uuid="sub_intent-3"), SubIntent(uuid="sub_intent-4")])
        ]
        intent_data.set_data(intents)
        self.assertEqual(len(intent_data.intents), 2)
        self.assertEqual(intent_data.intents[0].uuid, "intent-123")
        self.assertEqual(intent_data.intents[1].uuid, "intent-456")
    
    def test_set_data_with_str(self):
        intent_data = IntentData()
        intent_data.set_data("intent-123")
        self.assertEqual(intent_data.intents, "intent-123")
    
    def test_get_data_with_list(self):
        intents = [
            Intent(uuid="intent-123", sub_intents=[SubIntent(uuid="sub_intent-1"), SubIntent(uuid="sub_intent-2")]),
            Intent(uuid="intent-456", sub_intents=[SubIntent(uuid="sub_intent-3"), SubIntent(uuid="sub_intent-4")])
        ]
        intent_data = IntentData(intents=intents)
        self.assertEqual(intent_data.get_data(), intents)
    
    def test_get_data_with_str(self):
        intent_data = IntentData(intents="intent-123")
        self.assertEqual(intent_data.get_data(), "intent-123")

class TestSentimentData(unittest.TestCase):
    def test_from_json_with_list(self):
        json_data = [
            {"uuid": "sentiment-1"},
            {"uuid": "sentiment-2"}
        ]
        sentiment_data = SentimentData.from_json(json_data)
        self.assertEqual(len(sentiment_data.sentiments), 2)
        self.assertEqual(sentiment_data.sentiments[0].uuid, "sentiment-1")
        self.assertEqual(sentiment_data.sentiments[1].uuid, "sentiment-2")
    
    def test_from_json_with_str(self):
        json_data = "sentiment-123"
        sentiment_data = SentimentData.from_json(json_data)
        self.assertEqual(sentiment_data.sentiments, "sentiment-123")
    
    def test_set_data_with_list(self):
        sentiment_data = SentimentData()
        sentiments = [Sentiment(uuid="sentiment-1"), Sentiment(uuid="sentiment-2")]
        sentiment_data.set_data(sentiments)
        self.assertEqual(len(sentiment_data.sentiments), 2)
        self.assertEqual(sentiment_data.sentiments[0].uuid, "sentiment-1")
        self.assertEqual(sentiment_data.sentiments[1].uuid, "sentiment-2")
    
    def test_set_data_with_str(self):
        sentiment_data = SentimentData()
        sentiment_data.set_data("sentiment-123")
        self.assertEqual(sentiment_data.sentiments, "sentiment-123")
    
    def test_get_data_with_list(self):
        sentiments = [Sentiment(uuid="sentiment-1"), Sentiment(uuid="sentiment-2")]
        sentiment_data = SentimentData(sentiments=sentiments)
        self.assertEqual(sentiment_data.get_data(), sentiments)
    
    def test_get_data_with_str(self):
        sentiment_data = SentimentData(sentiments="sentiment-123")
        self.assertEqual(sentiment_data.get_data(), "sentiment-123")
    
    def test_str_method(self):
        sentiments = [Sentiment(uuid="sentiment-1"), Sentiment(uuid="sentiment-2")]
        sentiment_data = SentimentData(sentiments=sentiments)
        self.assertEqual(str(sentiment_data), "SentimentData{sentiments=[Sentiment(uuid='sentiment-1'), Sentiment(uuid='sentiment-2')]}")
        sentiment_data_str = SentimentData(sentiments="sentiment-123")
        self.assertEqual(str(sentiment_data_str), "SentimentData{sentiments=sentiment-123}")

class TestCustomerTierData(unittest.TestCase):
    def test_from_json_with_list(self):
        json_data = [
            {"uuid": "tier-1"},
            {"uuid": "tier-2"}
        ]
        customer_tier_data = CustomerTierData.from_json(json_data)
        self.assertEqual(len(customer_tier_data.tiers), 2)
        self.assertEqual(customer_tier_data.tiers[0].uuid, "tier-1")
        self.assertEqual(customer_tier_data.tiers[1].uuid, "tier-2")
    
    def test_from_json_with_str(self):
        json_data = "tier-123"
        customer_tier_data = CustomerTierData.from_json(json_data)
        self.assertEqual(customer_tier_data.tiers, "tier-123")
    
    def test_set_data_with_list(self):
        customer_tier_data = CustomerTierData()
        tiers = [CustomerTier(uuid="tier-1"), CustomerTier(uuid="tier-2")]
        customer_tier_data.set_data(tiers)
        self.assertEqual(len(customer_tier_data.tiers), 2)
        self.assertEqual(customer_tier_data.tiers[0].uuid, "tier-1")
        self.assertEqual(customer_tier_data.tiers[1].uuid, "tier-2")
    
    def test_set_data_with_str(self):
        customer_tier_data = CustomerTierData()
        customer_tier_data.set_data("tier-123")
        self.assertEqual(customer_tier_data.tiers, "tier-123")
    
    def test_get_data_with_list(self):
        tiers = [CustomerTier(uuid="tier-1"), CustomerTier(uuid="tier-2")]
        customer_tier_data = CustomerTierData(tiers=tiers)
        self.assertEqual(customer_tier_data.get_data(), tiers)
    
    def test_get_data_with_str(self):
        customer_tier_data = CustomerTierData(tiers="tier-123")
        self.assertEqual(customer_tier_data.get_data(), "tier-123")
    
    def test_str_method(self):
        tiers = [CustomerTier(uuid="tier-1"), CustomerTier(uuid="tier-2")]
        customer_tier_data = CustomerTierData(tiers=tiers)
        self.assertEqual(str(customer_tier_data), "CustomerTierData{tiers=[CustomerTier(uuid='tier-1'), CustomerTier(uuid='tier-2')]}")
        customer_tier_data_str = CustomerTierData(tiers="tier-123")
        self.assertEqual(str(customer_tier_data_str), "CustomerTierData{tiers=tier-123}")


class TestDimensionsValidator(unittest.TestCase):

    def setUp(self):
        # Create mock data for testing
        self.customer_tier_data = CustomerTierData()
        self.geography_data = GeographyData()
        self.intent_data = IntentData()
        self.sentiment_data = SentimentData()

    def test_validate_customer_tier(self):
        # Test case where customer_tier_data is a list containing a matching tier UUID
        self.customer_tier_data.get_data = MagicMock(return_value=[MockCustomerTier(uuid="12345")])
        self.assertTrue(DimensionsValidator.validate_customer_tier(self.customer_tier_data, "12345"))

        # Test case where customer_tier_data is a string "*"
        self.customer_tier_data.get_data = MagicMock(return_value="*")
        self.assertTrue(DimensionsValidator.validate_customer_tier(self.customer_tier_data, "any_uuid"))

        # Test case where customer_tier_data is neither a list nor "*"
        self.customer_tier_data.get_data = MagicMock(return_value={"invalid_data": "123"})
        self.assertFalse(DimensionsValidator.validate_customer_tier(self.customer_tier_data, "any_uuid"))

    def test_validate_geography(self):
        # Test case where countries list contains a matching country UUID and state UUID
        mock_country = MagicMock()
        mock_country.uuid = "country_uuid"
        mock_country.states = [MockState(uuid="state_uuid")]
        self.geography_data.get_data = MagicMock(return_value=[mock_country])
        self.assertTrue(DimensionsValidator.validate_geography(self.geography_data, "country_uuid", "state_uuid"))

        # Test case where countries list contains a matching country UUID but no matching state UUID
        self.assertFalse(DimensionsValidator.validate_geography(self.geography_data, "country_uuid", "invalid_state_uuid"))

        # Test case where countries is a string "*"
        self.geography_data.get_data = MagicMock(return_value="*")
        self.assertTrue(DimensionsValidator.validate_geography(self.geography_data, "any_country_uuid", "any_state_uuid"))

        # Test case where countries is neither a list nor "*"
        self.geography_data.get_data = MagicMock(return_value={"invalid_data": "123"})
        self.assertFalse(DimensionsValidator.validate_geography(self.geography_data, "any_country_uuid", "any_state_uuid"))

    def test_validate_intent(self):
        # Test case where intents list contains a matching intent UUID and sub-intent UUID
        mock_intent = MagicMock()
        mock_intent.uuid = "intent_uuid"
        mock_intent.sub_intents = [MockSubIntent(uuid="sub_intent_uuid")]
        self.intent_data.get_data = MagicMock(return_value=[mock_intent])
        self.assertTrue(DimensionsValidator.validate_intent(self.intent_data, "intent_uuid", "sub_intent_uuid"))

        # Test case where intents list contains a matching intent UUID but no matching sub-intent UUID
        self.assertFalse(DimensionsValidator.validate_intent(self.intent_data, "intent_uuid", "invalid_sub_intent_uuid"))

        # Test case where intents is a string "*"
        self.intent_data.get_data = MagicMock(return_value="*")
        self.assertTrue(DimensionsValidator.validate_intent(self.intent_data, "any_intent_uuid", "any_sub_intent_uuid"))

        # Test case where intents is neither a list nor "*"
        self.intent_data.get_data = MagicMock(return_value={"invalid_data": "123"})
        self.assertFalse(DimensionsValidator.validate_intent(self.intent_data, "any_intent_uuid", "any_sub_intent_uuid"))

    def test_validate_sentiment(self):
        # Test case where sentiments list contains a matching sentiment UUID
        mock_sentiment = MagicMock()
        mock_sentiment.uuid = "sentiment_uuid"
        self.sentiment_data.get_data = MagicMock(return_value=[mock_sentiment])
        self.assertTrue(DimensionsValidator.validate_sentiment(self.sentiment_data, "sentiment_uuid"))

        # Test case where sentiments list does not contain the matching sentiment UUID
        self.assertFalse(DimensionsValidator.validate_sentiment(self.sentiment_data, "invalid_sentiment_uuid"))

        # Test case where sentiments is a string "*"
        self.sentiment_data.get_data = MagicMock(return_value="*")
        self.assertTrue(DimensionsValidator.validate_sentiment(self.sentiment_data, "any_sentiment_uuid"))

        # Test case where sentiments is neither a list nor "*"
        self.sentiment_data.get_data = MagicMock(return_value={"invalid_data": "123"})
        self.assertFalse(DimensionsValidator.validate_sentiment(self.sentiment_data, "any_sentiment_uuid"))

# Mock classes for testing
class MockCustomerTier:
    def __init__(self, uuid):
        self.uuid = uuid

class MockCountry:
    def __init__(self, uuid, states):
        self.uuid = uuid
        self.states = states

class MockState:
    def __init__(self, uuid):
        self.uuid = uuid

class MockIntent:
    def __init__(self, uuid, sub_intents):
        self.uuid = uuid
        self.sub_intents = sub_intents

class MockSubIntent:
    def __init__(self, uuid):
        self.uuid = uuid

class MockSentiment:
    def __init__(self, uuid):
        self.uuid = uuid


import unittest
from unittest.mock import MagicMock
from EmailApp.ActionFlowDimensionClass import DimensionsDetails, GeographyData, IntentData, SentimentData, CustomerTierData

class TestFromJsonMethod(unittest.TestCase):

    def setUp(self):
        # Setup any necessary mock data or objects
        self.mock_json_data = {
            'geography': {
                'country': ['USA', 'Canada']
            },
            'intent': ['purchase', 'support'],
            'sentiment': ['positive', 'neutral'],
            'customer_tier': ['gold', 'silver']
        }

    def test_from_json_valid_data(self):
        # Mock the from_json methods of nested classes
        mock_geo_data = MagicMock(spec=GeographyData)
        mock_intent_data = MagicMock(spec=IntentData)
        mock_sentiment_data = MagicMock(spec=SentimentData)
        mock_customer_tier_data = MagicMock(spec=CustomerTierData)

        # Patching the from_json methods
        with unittest.mock.patch.object(GeographyData, 'from_json', return_value=mock_geo_data):
            with unittest.mock.patch.object(IntentData, 'from_json', return_value=mock_intent_data):
                with unittest.mock.patch.object(SentimentData, 'from_json', return_value=mock_sentiment_data):
                    with unittest.mock.patch.object(CustomerTierData, 'from_json', return_value=mock_customer_tier_data):
                        # Call the from_json method of YourClass
                        instance = DimensionsDetails.from_json(self.mock_json_data)

                        # Assertions
                        self.assertIsInstance(instance, DimensionsDetails)
                        self.assertEqual(instance.geography, mock_geo_data)
                        self.assertEqual(instance.intent, mock_intent_data)
                        self.assertEqual(instance.sentiment, mock_sentiment_data)
                        self.assertEqual(instance.customer_tier, mock_customer_tier_data)

    def test_from_json_exception_handling(self):
        # Mock logger
        mock_logger = MagicMock()
        with unittest.mock.patch('EmailApp.ActionFlowDimensionClass.logger', mock_logger):
            # Call from_json method with invalid json_data (e.g., None)
            instance = DimensionsDetails.from_json(None)

            # Assertions
            self.assertIsInstance(instance, DimensionsDetails)
            self.assertTrue(mock_logger.error.called)


class TestActionRuleValidation(unittest.TestCase):

    def setUp(self):
        # Setup any necessary mock data or objects
        self.mock_dimension_action_json = {
            "customer_tier": {"uuid": "tier_uuid"},
            "geography": {"country": {"uuid": "country_uuid", "state": {"uuid": "state_uuid"}}},
            "intent": {"uuid": "intent_uuid", "sub_intent": {"uuid": "sub_intent_uuid"}},
            "sentiment": {"uuid": "sentiment_uuid"}
        }

        # Mock instances or attributes needed by YourClass
        self.mock_customer_tier = MagicMock()
        self.mock_geography = MagicMock()
        self.mock_intent = MagicMock()
        self.mock_sentiment = MagicMock()

    def test_action_rule_validation_valid_data(self):
        # Mock validate methods of DimensionsValidator
        mock_validate_customer_tier = MagicMock(return_value=True)
        mock_validate_geography = MagicMock(return_value=True)
        mock_validate_intent = MagicMock(return_value=True)
        mock_validate_sentiment = MagicMock(return_value=True)

        with patch.object(DimensionsValidator, 'validate_customer_tier', mock_validate_customer_tier), \
             patch.object(DimensionsValidator, 'validate_geography', mock_validate_geography), \
             patch.object(DimensionsValidator, 'validate_intent', mock_validate_intent), \
             patch.object(DimensionsValidator, 'validate_sentiment', mock_validate_sentiment):

            # Mock YourClass attributes
            instance = DimensionsDetails()
            instance.customer_tier = self.mock_customer_tier
            instance.geography = self.mock_geography
            instance.intent = self.mock_intent
            instance.sentiment = self.mock_sentiment

            # Call action_rule_validation method
            result = instance.action_rule_validation(self.mock_dimension_action_json)

            # Assertions
            self.assertTrue(result)
            mock_validate_customer_tier.assert_called_once_with(self.mock_customer_tier, "tier_uuid")
            mock_validate_geography.assert_called_once_with(self.mock_geography, "country_uuid", "state_uuid")
            mock_validate_intent.assert_called_once_with(self.mock_intent, "intent_uuid", "sub_intent_uuid")
            mock_validate_sentiment.assert_called_once_with(self.mock_sentiment, "sentiment_uuid")

    def test_action_rule_validation_invalid_data(self):
        # Mock logger
        mock_logger = MagicMock()
        with patch('EmailApp.ActionFlowDimensionClass.logger', mock_logger):
            # Call action_rule_validation method with invalid json_data (e.g., None)
            instance = DimensionsDetails()
            result = instance.action_rule_validation(None)

            # Assertions
            self.assertFalse(result)
            self.assertTrue(mock_logger.error.called)
