"""AI Agent - A simple, extensible conversational AI assistant."""

from src.ai_agent.core.agent import AIAgent
from src.ai_agent.core.config import Settings
from src.ai_agent.core.exceptions import AIAgentException
from src.ai_agent.providers.base_provider import BaseProvider
from src.ai_agent.providers.openai_provider import OpenAIProvider

__version__ = "0.1.0"
__all__ = ["AIAgent", "Settings",
           "AIAgentException", "BaseProvider",
           "OpenAIProvider"]
