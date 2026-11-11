"""Unit tests for the asynchronous OpenAI provider."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import openai
import pytest

from ai_agent.core.exceptions import APIException, ConfigurationException
from ai_agent.providers.base_provider import ChatResponse, Message
from ai_agent.providers.openai_provider import OpenAIProvider


def mock_api_response(content="Hello!"):
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = content
    response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    return response


class TestOpenAIProvider:
    def test_requires_api_key(self):
        with pytest.raises(ConfigurationException):
            OpenAIProvider(api_key="")

    @patch("ai_agent.providers.openai_provider.openai.AsyncOpenAI")
    def test_initializes_async_client_with_timeout(self, client_class):
        provider = OpenAIProvider("test-key", timeout=12.0, max_retries=1)
        assert provider.validate_config() is True
        client_class.assert_called_once_with(
            api_key="test-key", timeout=12.0, max_retries=1
        )

    @pytest.mark.asyncio
    @patch("ai_agent.providers.openai_provider.openai.AsyncOpenAI")
    async def test_chat_success(self, client_class):
        client = client_class.return_value
        client.chat.completions.create = AsyncMock(
            return_value=mock_api_response("Hello!")
        )
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.chat([Message(role="user", content="Hi")])
        assert isinstance(result, ChatResponse)
        assert result.content == "Hello!"
        assert result.usage["total_tokens"] == 15
        client.chat.completions.create.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("ai_agent.providers.openai_provider.openai.AsyncOpenAI")
    async def test_chat_empty_response(self, client_class):
        client_class.return_value.chat.completions.create = AsyncMock(
            return_value=mock_api_response(None)
        )
        provider = OpenAIProvider(api_key="test-key")
        with pytest.raises(APIException, match="empty response"):
            await provider.chat([Message(role="user", content="Hi")])

    @pytest.mark.asyncio
    @patch("ai_agent.providers.openai_provider.openai.AsyncOpenAI")
    async def test_chat_connection_failure(self, client_class):
        client_class.return_value.chat.completions.create = AsyncMock(
            side_effect=openai.APIConnectionError(
                request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
            )
        )
        provider = OpenAIProvider(api_key="test-key")
        with pytest.raises(APIException, match="Could not reach OpenAI"):
            await provider.chat([Message(role="user", content="Hi")])

    @pytest.mark.asyncio
    @patch("ai_agent.providers.openai_provider.openai.AsyncOpenAI")
    async def test_chat_api_status_error(self, client_class):
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        response = httpx.Response(429, request=request)
        client_class.return_value.chat.completions.create = AsyncMock(
            side_effect=openai.APIStatusError("Rate limited", response=response, body=None)
        )
        provider = OpenAIProvider(api_key="test-key")
        with pytest.raises(APIException, match="OpenAI API request failed"):
            await provider.chat([Message(role="user", content="Hi")])
