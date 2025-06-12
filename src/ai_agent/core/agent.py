import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .config import Settings
from .exceptions import AIAgentException, ValidationException
from src.ai_agent.providers.base_provider import BaseProvider, Message
from src.ai_agent.providers.openai_provider import OpenAIProvider
from src.ai_agent.utils.logger import setup_logger


class AIAgent:
    """Main AI Agent class."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        provider: Optional[BaseProvider] = None,
    ):
        self.settings = settings or Settings()
        self.logger = setup_logger("AIAgent", level=self.settings.log_level)

        # Initialize provider
        if provider:
            self.provider = provider
        else:
            self.provider = OpenAIProvider(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_model
            )

        # Validate provider
        if not self.provider.validate_config():
            raise AIAgentException("Provider configuration is invalid")

        # Initialize conversation
        self.conversation_history: List[Message] = []
        self.system_prompt = self._get_default_system_prompt()

        self.logger.info(
            f"AI Agent initialized with {self.provider.__class__.__name__}"
        )

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt based on personality."""
        personalities = {
            "friendly": "You are a friendly and helpful AI assistant. "
                        "You're warm, approachable, and "
                        "always try to be genuinely useful.",
            "professional": "You are a professional AI assistant. "
                            "You provide accurate, concise, and"
                            "well-structured responses.",
            "creative": "You are a creative AI assistant. "
                        "You think outside the box and provide "
                        "innovative solutions and ideas.",
            "technical": "You are a technical AI assistant. "
                         "You provide detailed, accurate technical "
                         "information and explanations.",
        }

        return personalities.get(
            self.settings.agent_personality, personalities["friendly"]
        )

    def set_system_prompt(self, prompt: str) -> None:
        """Set custom system prompt."""
        if not prompt.strip():
            raise ValidationException("System prompt cannot be empty")

        self.system_prompt = prompt
        self.logger.info("System prompt updated")

    async def chat(self, message: str, **kwargs: Any) -> str:
        """Send a message and get response."""
        if not message.strip():
            raise ValidationException("Message cannot be empty")

        # Add user message to history
        user_message = Message(
            role="user", content=message.strip(),
            timestamp=datetime.now().isoformat()
        )
        self.conversation_history.append(user_message)

        # Prepare messages for API
        messages = [Message(role="system", content=self.system_prompt)]

        # Add recent conversation history
        recent_history = self.conversation_history[
                         -self.settings.conversation_history_limit:
                         ]
        messages.extend(recent_history)

        try:
            # Get response from provider
            response = await self.provider.chat(
                messages=messages,
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature,
                **kwargs,
            )

            # Add assistant response to history
            assistant_message = Message(
                role="assistant",
                content=response.content,
                timestamp=datetime.now().isoformat(),
            )
            self.conversation_history.append(assistant_message)

            self.logger.info(f"Chat completed - tokens used: {response.usage}")

            return response.content

        except Exception as e:
            self.logger.error(f"Chat failed: {e}")
            raise

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary."""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len(
                [m for m in self.conversation_history if m.role == "user"]
            ),
            "assistant_messages": len(
                [m for m in self.conversation_history if m.role == "assistant"]
            ),
            "model": (
                self.provider.model if hasattr(
                    self.provider, "model") else "unknown"
            ),
            "last_message_time": (
                self.conversation_history[-1].timestamp
                if self.conversation_history
                else None
            ),
        }

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")

    def save_conversation(self, filepath: str) -> None:
        """Save conversation to file."""
        try:
            data = {
                "agent_name": self.settings.agent_name,
                "model": (
                    self.provider.model
                    if hasattr(self.provider, "model")
                    else "unknown"
                ),
                "system_prompt": self.system_prompt,
                "conversation": [msg.model_dump() for msg in
                                 self.conversation_history],
                "saved_at": datetime.now().isoformat(),
                "summary": self.get_conversation_summary(),
            }

            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Conversation saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")
            raise AIAgentException(f"Failed to save conversation: {e}")

    def load_conversation(self, filepath: str) -> None:
        """Load conversation from file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load conversation history
            self.conversation_history = [
                Message(**msg) for msg in data.get("conversation", [])
            ]

            # Load system prompt if available
            if "system_prompt" in data:
                self.system_prompt = data["system_prompt"]

            self.logger.info(f"Conversation loaded from {filepath}")

        except FileNotFoundError:
            raise AIAgentException(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            raise AIAgentException(f"Invalid JSON in file: {e}")
        except Exception as e:
            raise AIAgentException(f"Failed to load conversation: {e}")

    def get_recent_messages(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent messages."""
        recent = self.conversation_history[-count:] \
            if self.conversation_history \
            else []
        return [msg.dict() for msg in recent]
