from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Message(BaseModel):
    """Message model."""

    role: str
    content: str
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""

    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None


class BaseProvider(ABC):
    """Base class for AI providers."""

    def __init__(self, **kwargs: Any):
        self.config = kwargs

    @abstractmethod
    async def chat(self, messages: List[Message],
                   **kwargs: Any) -> ChatResponse:
        """Send chat messages and get response."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        pass
