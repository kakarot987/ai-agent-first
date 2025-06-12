import pytest
from unittest.mock import Mock
from src.ai_agent.core.config import Settings
from src.ai_agent.core.agent import AIAgent
from src.ai_agent.providers.openai_provider import OpenAIProvider


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        OPENAI_API_KEY="test-key",
        OPENAI_MODEL="gpt-3.5-turbo",
        OPENAI_MAX_TOKENS=100,
        OPENAI_TEMPERATURE=0.5,
        AGENT_NAME="Test Agent",
        AGENT_PERSONALITY="Friendly",
        LOG_LEVEL="DEBUG",
    )


@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider."""
    provider = Mock(spec=OpenAIProvider)
    provider.model = "gpt-3.5-turbo"
    provider.validate_config.return_value = True
    return provider


@pytest.fixture
def agent_with_mock_provider(mock_settings, mock_openai_provider):
    """AI Agent with mocked provider."""
    return AIAgent(settings=mock_settings, provider=mock_openai_provider)
