import openai
from typing import Any, cast, List

from openai.types.chat import ChatCompletionMessageParam

from .base_provider import BaseProvider, Message, ChatResponse
from src.ai_agent.core.exceptions import APIException, ConfigurationException
from src.ai_agent.utils.logger import setup_logger


class OpenAIProvider(BaseProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str,
                 model: str = "gpt-3.5-turbo", **kwargs: Any):
        super().__init__(**kwargs)

        if not api_key:
            raise ConfigurationException("OpenAI API key is required")

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.logger = setup_logger(self.__class__.__name__)

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        try:
            self.client.models.list()
            return True
        except Exception as e:
            self.logger.error(f"OpenAI configuration validation failed: {e}")
            return False

    async def chat(
        self,
        messages: List[Message],
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat to OpenAI API."""

        try:
            # Convert messages to OpenAI format
            openai_messages: List[ChatCompletionMessageParam] = cast(
                List[ChatCompletionMessageParam],
                [{"role": m.role, "content": m.content} for m in messages]
            )

            self.logger.debug(
                f"Sending {len(openai_messages)} messages to OpenAI"
            )

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            # Extract response
            content = response.choices[0].message.content.strip()
            if response.usage is not None:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            else:
                usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                }

            self.logger.debug(f"Received response: {usage}")

            return ChatResponse(content=content, model=self.model, usage=usage)

        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise APIException(f"OpenAI API error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise APIException(f"Unexpected error: {e}")
