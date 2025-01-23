import unittest
from unittest.mock import patch, MagicMock


class TestFormatChatHistory(unittest.TestCase):

    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.get_ai_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")  # Patch the logger
    def test_empty_chat_history_list(self, mock_logger, mock_get_ai_message, mock_get_human_message):
        """Test when chat_history_list is empty or None."""
        from WiseFlow.utils import format_chat_history

        # Test with None
        result = format_chat_history(None)
        self.assertIsNone(result)

        # Test with empty list
        result = format_chat_history([])
        self.assertIsNone(result)

        mock_logger.info.assert_called_with("In Utils::get_previous_email_history")

    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.get_ai_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")  # Patch the logger
    def test_valid_chat_history(self, mock_logger, mock_get_ai_message, mock_get_human_message):
        """Test when chat_history_list has valid entries."""
        from WiseFlow.utils import format_chat_history, ChatHistoryFormatKeys, MessageSourceType

        # Mock the behavior of external functions
        mock_get_human_message.return_value = "Formatted User Message"
        mock_get_ai_message.return_value =  "Formatted AI Message"

        # Sample input
        chat_history_list = [
            {ChatHistoryFormatKeys.SOURCE.value: MessageSourceType.USER.value,
             ChatHistoryFormatKeys.MESSAGE.value: "User Message"},
            {ChatHistoryFormatKeys.SOURCE.value: MessageSourceType.AI.value,
             ChatHistoryFormatKeys.MESSAGE.value: "AI Message"},
        ]

        # Expected output
        expected_result = ["Formatted User Message", "Formatted AI Message"]

        # Run the function
        result = format_chat_history(chat_history_list)

        # Assertions
        self.assertEqual(result, expected_result)
        mock_logger.info.assert_called_once_with("In Utils::get_previous_email_history")
        mock_get_human_message.assert_called_once_with("User Message")
        mock_get_ai_message.assert_called_once_with(
             "AI Message"
        )

    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.get_ai_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")  # Patch the logger
    def test_invalid_source(self, mock_logger, mock_get_ai_message, mock_get_human_message):
        """Test when chat_history_list has an invalid source."""
        from WiseFlow.utils import format_chat_history, ChatHistoryFormatKeys

        # Sample input with an invalid source
        chat_history_list = [
            {ChatHistoryFormatKeys.SOURCE.value: "INVALID_SOURCE", ChatHistoryFormatKeys.MESSAGE.value: "Message"}
        ]

        # Run the function
        result = format_chat_history(chat_history_list)

        # Assertions
        self.assertEqual(result, [])  # Invalid source should not add anything to the result
        mock_logger.info.assert_called_once_with("In Utils::get_previous_email_history")
        mock_get_human_message.assert_not_called()
        mock_get_ai_message.assert_not_called()

    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.get_ai_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")  # Patch the logger
    def test_case_insensitive_source(self, mock_logger, mock_get_ai_message, mock_get_human_message):
        """Test when source values are case-insensitive."""
        from WiseFlow.utils import format_chat_history, ChatHistoryFormatKeys, MessageSourceType

        # Mock the behavior of external functions
        mock_get_human_message.return_value = "Formatted User Message"
        mock_get_ai_message.return_value = "Formatted AI Message"

        # Sample input with mixed-case source values
        chat_history_list = [
            {ChatHistoryFormatKeys.SOURCE.value: "uSeR", ChatHistoryFormatKeys.MESSAGE.value: "User Message"},
            {ChatHistoryFormatKeys.SOURCE.value: "aI", ChatHistoryFormatKeys.MESSAGE.value: "AI Message"},
        ]

        # Expected output
        expected_result = ["Formatted User Message", "Formatted AI Message"]

        # Run the function
        result = format_chat_history(chat_history_list)

        # Assertions
        self.assertEqual(result, expected_result)
        mock_logger.info.assert_called_once_with("In Utils::get_previous_email_history")
        mock_get_human_message.assert_called_once_with("User Message")
        mock_get_ai_message.assert_called_once_with(
            "AI Message"
        )
import unittest
from unittest.mock import patch, MagicMock

class TestCreatePromptWithChatHistoryQuery(unittest.TestCase):

    @patch("WiseFlow.utils.get_system_message")  # Patch the external function
    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")             # Patch the logger
    def test_no_chat_history(self, mock_logger, mock_get_human_message, mock_get_system_message):
        """Test when chat_history is None or empty."""
        from WiseFlow.utils import create_prompt_with_chat_history_query

        # Mock external functions
        mock_get_system_message.return_value = "System Message"
        mock_get_human_message.return_value = "Human Query Message"

        # Test with None chat history
        prompt = "This is a system prompt."
        query = "What is the weather today?"
        chat_history = None

        # Expected result
        expected_result = ["System Message", "Human Query Message"]

        # Run the function
        result = create_prompt_with_chat_history_query(prompt, chat_history, query)

        # Assertions
        self.assertEqual(result, expected_result)
        mock_logger.info.assert_any_call("In Utils::create_prompt_with_chat_history_query")
        mock_logger.debug.assert_any_call(f"chat_history :: {chat_history} :: query :: {query}")
        mock_get_system_message.assert_called_once_with(prompt)
        mock_get_human_message.assert_called_once_with(query)

    @patch("WiseFlow.utils.get_system_message")  # Patch the external function
    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")             # Patch the logger
    def test_with_chat_history(self, mock_logger, mock_get_human_message, mock_get_system_message):
        """Test when chat_history is provided."""
        from WiseFlow.utils import create_prompt_with_chat_history_query

        # Mock external functions
        mock_get_system_message.return_value = "System Message"
        mock_get_human_message.return_value = "Human Query Message"

        # Test with chat history
        prompt = "This is a system prompt."
        query = "What is the weather today?"
        chat_history = ["Chat History Message 1", "Chat History Message 2"]

        # Expected result
        expected_result = [
            "System Message",
            "Chat History Message 1",
            "Chat History Message 2",
            "Human Query Message"
        ]

        # Run the function
        result = create_prompt_with_chat_history_query(prompt, chat_history, query)

        # Assertions
        self.assertEqual(result, expected_result)
        mock_logger.info.assert_any_call("In Utils::create_prompt_with_chat_history_query")
        mock_logger.debug.assert_any_call(f"chat_history :: {chat_history} :: query :: {query}")
        mock_logger.info.assert_any_call(f"Prompt before invoking the LLM::{expected_result}")
        mock_logger.debug.assert_any_call(f"llm_inputs::{expected_result}")
        mock_get_system_message.assert_called_once_with(prompt)
        mock_get_human_message.assert_called_once_with(query)

    @patch("WiseFlow.utils.get_system_message")  # Patch the external function
    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")             # Patch the logger
    def test_empty_query(self, mock_logger, mock_get_human_message, mock_get_system_message):
        """Test when query is an empty string."""
        from WiseFlow.utils import create_prompt_with_chat_history_query

        # Mock external functions
        mock_get_system_message.return_value = "System Message"
        mock_get_human_message.return_value = "Human Query Message"

        # Test with an empty query
        prompt = "This is a system prompt."
        query = ""
        chat_history = ["Chat History Message 1"]

        # Expected result
        expected_result = ["System Message", "Chat History Message 1", "Human Query Message"]

        # Run the function
        result = create_prompt_with_chat_history_query(prompt, chat_history, query)

        # Assertions
        self.assertEqual(result, expected_result)
        mock_logger.info.assert_any_call("In Utils::create_prompt_with_chat_history_query")
        mock_logger.debug.assert_any_call(f"chat_history :: {chat_history} :: query :: {query}")
        mock_logger.info.assert_any_call(f"Prompt before invoking the LLM::{expected_result}")
        mock_logger.debug.assert_any_call(f"llm_inputs::{expected_result}")
        mock_get_system_message.assert_called_once_with(prompt)
        mock_get_human_message.assert_called_once_with(query)

    @patch("WiseFlow.utils.get_system_message")  # Patch the external function
    @patch("WiseFlow.utils.get_human_message")  # Patch the external function
    @patch("WiseFlow.utils.logger")             # Patch the logger
    def test_empty_chat_history_and_query(self, mock_logger, mock_get_human_message, mock_get_system_message):
        """Test when both chat_history and query are empty."""
        from WiseFlow.utils import create_prompt_with_chat_history_query

        # Mock external functions
        mock_get_system_message.return_value = "System Message"
        mock_get_human_message.return_value = "Human Query Message"

        # Test with empty chat history and query
        prompt = "This is a system prompt."
        query = ""
        chat_history = []

        # Expected result
        expected_result = ["System Message", "Human Query Message"]

        # Run the function
        result = create_prompt_with_chat_history_query(prompt, chat_history, query)

        # Assertions
        self.assertEqual(result, expected_result)
        mock_logger.info.assert_any_call("In Utils::create_prompt_with_chat_history_query")
        mock_logger.debug.assert_any_call(f"chat_history :: {chat_history} :: query :: {query}")
        mock_logger.info.assert_any_call(f"Prompt before invoking the LLM::{expected_result}")
        mock_logger.debug.assert_any_call(f"llm_inputs::{expected_result}")
        mock_get_system_message.assert_called_once_with(prompt)
        mock_get_human_message.assert_called_once_with(query)
