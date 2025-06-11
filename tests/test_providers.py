import pytest
from unittest.mock import Mock, patch
import openai

from src.ai_agent.providers.openai_provider import OpenAIProvider
from src.ai_agent.providers.base_provider import Message, ChatResponse
from src.ai_agent.core.exceptions import APIException, ConfigurationException


class TestOpenAIProvider:

    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises error."""
        with pytest.raises(ConfigurationException):
            OpenAIProvider(api_key="")

    def test_initialization_with_api_key(self):
        """Test successful initialization."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.model == "gpt-3.5-turbo"

    @patch("openai.OpenAI")
    def test_validate_config_success(self, mock_openai_client):
        """Test successful configuration validation."""
        mock_client = Mock()
        mock_client.models.list.return_value = []
        mock_openai_client.return_value = mock_client

        provider = OpenAIProvider(api_key="test-key")
        assert provider.validate_config() is True

    @patch("openai.OpenAI")
    def test_validate_config_failure(self, mock_openai_client):
        """Test configuration validation failure."""
        mock_client = Mock()
        mock_client.models.list.side_effect = (openai
                                               .APIError("Invalid API key"))
        mock_openai_client.return_value = mock_client

        provider = OpenAIProvider(api_key="test-key")
        assert provider.validate_config() is False

    @pytest.mark.asyncio
    @patch("openai.OpenAI")
    async def test_chat_success(self, mock_openai_client):
        """Test successful chat."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help?"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 8
        mock_response.usage.total_tokens = 18

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client

        provider = OpenAIProvider(api_key="test-key")

        messages = [Message(role="user", content="Hello")]
        response = await provider.chat(messages)

        assert isinstance(response, ChatResponse)
        assert response.content == "Hello! How can I help?"
        assert response.usage["total_tokens"] == 18

    @pytest.mark.asyncio
    @patch("openai.OpenAI")
    async def test_chat_api_error(self, mock_openai_client):
        """Test chat with API error."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = openai.APIError(
            "Rate limit exceeded"
        )
        mock_openai_client.return_value = mock_client

        provider = OpenAIProvider(api_key="test-key")

        messages = [Message(role="user", content="Hello")]

        with pytest.raises(APIException):
            await provider.chat(messages)
