import pytest
from unittest.mock import AsyncMock

from src.ai_agent.core.agent import AIAgent
from src.ai_agent.core.exceptions import ValidationException, AIAgentException
from src.ai_agent.providers.base_provider import Message, ChatResponse


class TestAIAgent:

    def test_agent_initialization(self, mock_settings, mock_openai_provider):
        """Test agent initialization."""
        agent = AIAgent(settings=mock_settings, provider=mock_openai_provider)

        assert agent.settings == mock_settings
        assert agent.provider == mock_openai_provider
        assert len(agent.conversation_history) == 0
        assert agent.system_prompt is not None

    def test_set_system_prompt(self, agent_with_mock_provider):
        """Test setting system prompt."""
        new_prompt = "You are a test assistant."
        agent_with_mock_provider.set_system_prompt(new_prompt)

        assert agent_with_mock_provider.system_prompt == new_prompt

    def test_set_empty_system_prompt_raises_error(self,
                                                  agent_with_mock_provider):
        """Test that empty system prompt raises validation error."""
        with pytest.raises(ValidationException):
            agent_with_mock_provider.set_system_prompt("")

    @pytest.mark.asyncio
    async def test_chat_success(self, agent_with_mock_provider):
        """Test successful chat interaction."""
        # Mock provider response
        mock_response = ChatResponse(
            content="Hello! How can I help you?",
            model="gpt-3.5-turbo",
            usage={"total_tokens": 50},
        )
        agent_with_mock_provider.provider.chat = (
            AsyncMock(return_value=mock_response)
        )

        # Send message
        response = await agent_with_mock_provider.chat("Hello")

        # Assertions
        assert response == "Hello! How can I help you?"
        assert (
            len(agent_with_mock_provider.conversation_history) == 2
        )  # user + assistant
        assert (agent_with_mock_provider.conversation_history[0]
                .role == "user")
        assert (agent_with_mock_provider.conversation_history[1]
                .role == "assistant")

    @pytest.mark.asyncio
    async def test_chat_empty_message_raises_error(self,
                                                   agent_with_mock_provider):
        """Test that empty message raises validation error."""
        with pytest.raises(ValidationException):
            await agent_with_mock_provider.chat("")

    def test_get_conversation_summary(self,
                                      agent_with_mock_provider):
        """Test conversation summary."""
        # Add some mock messages
        agent_with_mock_provider.conversation_history = [
            Message(role="user", content="Hello",
                    timestamp="2023-01-01T00:00:00"),
            Message(role="assistant", content="Hi!",
                    timestamp="2023-01-01T00:00:01"),
        ]

        summary = agent_with_mock_provider.get_conversation_summary()

        assert summary["total_messages"] == 2
        assert summary["user_messages"] == 1
        assert summary["assistant_messages"] == 1

    def test_clear_history(self, agent_with_mock_provider):
        """Test clearing conversation history."""
        # Add some mock messages
        agent_with_mock_provider.conversation_history = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!"),
        ]

        agent_with_mock_provider.clear_history()

        assert len(agent_with_mock_provider.conversation_history) == 0

    def test_save_conversation(self, agent_with_mock_provider, tmp_path):
        """Test saving conversation."""
        # Add some mock messages
        agent_with_mock_provider.conversation_history = [
            Message(role="user", content="Hello",
                    timestamp="2023-01-01T00:00:00"),
            Message(role="assistant", content="Hi!",
                    timestamp="2023-01-01T00:00:01"),
        ]

        filepath = tmp_path / "test_conversation.json"
        agent_with_mock_provider.save_conversation(str(filepath))

        assert filepath.exists()

        # Load and verify content
        import json

        with open(filepath) as f:
            data = json.load(f)

        assert len(data["conversation"]) == 2
        assert data["conversation"][0]["role"] == "user"
        assert data["conversation"][1]["role"] == "assistant"

    def test_load_conversation(self, agent_with_mock_provider, tmp_path):
        """Test loading conversation."""
        # Create test conversation file
        test_data = {
            "agent_name": "Test Agent",
            "model": "gpt-3.5-turbo",
            "system_prompt": "Test prompt",
            "conversation": [
                {
                    "role": "user",
                    "content": "Hello",
                    "timestamp": "2023-01-01T00:00:00",
                },
                {
                    "role": "assistant",
                    "content": "Hi!",
                    "timestamp": "2023-01-01T00:00:01",
                },
            ],
            "saved_at": "2023-01-01T00:00:00",
        }

        filepath = tmp_path / "test_conversation.json"
        import json

        with open(filepath, "w") as f:
            json.dump(test_data, f)

        # Load conversation
        agent_with_mock_provider.load_conversation(str(filepath))

        assert len(agent_with_mock_provider.conversation_history) == 2
        assert agent_with_mock_provider.system_prompt == "Test prompt"

    def test_load_nonexistent_file_raises_error(
            self, agent_with_mock_provider
    ):
        """Test loading nonexistent file raises error."""
        with pytest.raises(AIAgentException):
            agent_with_mock_provider.load_conversation("nonexistent.json")
