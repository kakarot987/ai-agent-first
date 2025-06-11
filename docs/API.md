# AI Agent API Documentation

## Core Classes

### AIAgent

The main agent class that handles conversation and interaction with AI providers.

#### Initialization

```python
from ai_agent import AIAgent, Settings

# With default settings
agent = AIAgent()

# With custom settings
settings = Settings(
    openai_api_key="your-key",
    openai_model="gpt-4",
    agent_personality="professional"
)
agent = AIAgent(settings=settings)
```

#### Methods

##### `async chat(message: str, **kwargs) -> str`
Send a message and get a response.

**Parameters:**
- `message` (str): The user's message
- `**kwargs`: Additional parameters passed to the provider

**Returns:**
- `str`: The AI's response

**Example:**
```python
response = await agent.chat("Hello, how are you?")
print(response)
```

##### `set_system_prompt(prompt: str) -> None`
Set a custom system prompt.

**Parameters:**
- `prompt` (str): The system prompt

**Example:**
```python
agent.set_system_prompt("You are a helpful coding assistant.")
```

##### `get_conversation_summary() -> Dict[str, Any]`
Get a summary of the current conversation.

**Returns:**
- `Dict[str, Any]`: Summary statistics

##### `clear_history() -> None`
Clear the conversation history.

##### `save_conversation(filepath: str) -> None`
Save the conversation to a JSON file.

##### `load_conversation(filepath: str) -> None`
Load a conversation from a JSON file.

### Settings

Configuration class for the AI agent.

#### Parameters

- `openai_api_key` (str): OpenAI API key
- `openai_model` (str): Model name (default: "gpt-3.5-turbo")
- `openai_max_tokens` (int): Maximum response tokens (default: 150)
- `openai_temperature` (float): Creativity level (default: 0.7)
- `agent_name` (str): Agent name (default: "AI Assistant")
- `agent_personality` (str): Personality type (default: "friendly")
- `conversation_history_limit` (int): Max messages to keep (default: 20)
- `log_level` (str): Logging level (default: "INFO")

#### Example

```python
from ai_agent import Settings

settings = Settings(
    openai_api_key="sk-...",
    openai_model="gpt-4",
    openai_temperature=0.8,
    agent_personality="creative"
)
```

### Providers

#### OpenAIProvider

Provider for OpenAI API integration.

```python
from ai_agent.providers import OpenAIProvider

provider = OpenAIProvider(
    api_key="your-key",
    model="gpt-3.5-turbo"
)
```

#### Creating Custom Providers

Extend `BaseProvider` to create custom providers:

```python
from ai_agent.providers import BaseProvider, Message, ChatResponse

class CustomProvider(BaseProvider):
    async def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        # Your implementation here
        pass
    
    def validate_config(self) -> bool:
        # Validation logic
        return True
```

## CLI Usage

### Interactive Chat

```bash
ai-agent chat
ai-agent chat --model gpt-4 --temperature 0.8
```

### Single Question

```bash
ai-agent ask "What is machine learning?"
```

### Load Conversation

```bash
ai-agent load conversation_20231201_123456.json
```

## Environment Variables

All settings can be configured via environment variables:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4"
export OPENAI_TEMPERATURE="0.8"
export AGENT_PERSONALITY="professional"
```

## Error Handling

The library provides specific exceptions:

- `AIAgentException`: Base exception
- `APIException`: API-related errors
- `ConfigurationException`: Configuration errors
- `ValidationException`: Input validation errors

```python
from ai_agent.core.exceptions import AIAgentException

try:
    response = await agent.chat("Hello")
except AIAgentException as e:
    print(f"Agent error: {e}")
```