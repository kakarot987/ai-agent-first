"""Asynchronous OpenAI chat-completions provider."""

from typing import Any, List, cast

import openai
from openai.types.chat import ChatCompletionMessageParam

from ai_agent.core.exceptions import APIException, ConfigurationException
from ai_agent.providers.base_provider import BaseProvider, ChatResponse, Message
from ai_agent.utils.logger import setup_logger


class OpenAIProvider(BaseProvider):
    """OpenAI-backed chat provider with bounded network timeouts and retries."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout: float = 30.0,
        max_retries: int = 2,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if not api_key or not api_key.strip():
            raise ConfigurationException("OpenAI API key is required")
        self.api_key = api_key
        self.model = model
        self.client = openai.AsyncOpenAI(
            api_key=api_key, timeout=timeout, max_retries=max_retries
        )
        self.logger = setup_logger(self.__class__.__name__)

    def validate_config(self) -> bool:
        """Validate local settings without making a network request."""
        return bool(self.api_key.strip() and self.model.strip())


    async def complete_tool_turn(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        **kwargs: Any,
    ) -> "ModelTurn":
        """Ask the model for a final reply or function calls; do not execute tools."""
        from ai_agent.core.tool_agent import FunctionCall, ModelTurn

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=cast(Any, messages),
                tools=cast(Any, tools),
                tool_choice="auto",
                max_tokens=kwargs.get("max_tokens", 900),
                temperature=kwargs.get("temperature", 0.2),
            )
            if not response.choices:
                raise APIException("OpenAI returned no choices")
            message = response.choices[0].message
            calls = []
            for tool in message.tool_calls or []:
                if tool.type != "function":
                    raise APIException("Unexpected tool-call type")
                calls.append(
                    FunctionCall(
                        id=tool.id,
                        name=tool.function.name,
                        arguments=tool.function.arguments,
                    )
                )
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            return ModelTurn(content=message.content, tool_calls=calls, usage=usage)
        except APIException:
            raise
        except (openai.APITimeoutError, openai.APIConnectionError) as exc:
            raise APIException("Could not reach OpenAI; check your connection") from exc
        except openai.APIError as exc:
            raise APIException(f"OpenAI tool request failed: {exc}") from exc

    async def chat(
        self,
        messages: List[Message],
        max_tokens: int = 300,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat to OpenAI asynchronously."""
        openai_messages = cast(
            List[ChatCompletionMessageParam],
            [{"role": m.role, "content": m.content} for m in messages],
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            if not response.choices or not response.choices[0].message.content:
                raise APIException("OpenAI returned an empty response")
            content = response.choices[0].message.content.strip()
            if not content:
                raise APIException("OpenAI returned an empty response")
            usage = None
            if response.usage is not None:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            return ChatResponse(content=content, model=self.model, usage=usage)
        except APIException:
            raise
        except (openai.APITimeoutError, openai.APIConnectionError) as exc:
            self.logger.error("OpenAI connection failed: %s", exc)
            raise APIException("Could not reach OpenAI; check your connection") from exc
        except openai.APIError as exc:
            self.logger.error("OpenAI API request failed: %s", exc)
            raise APIException(f"OpenAI API request failed: {exc}") from exc
