# AI Agent First — OpenAI Chat CLI

A small **conversational AI application**, built with Python, OpenAI, Pydantic,
and Click. It demonstrates a replaceable provider interface, asynchronous chat,
configurable prompts, local conversation history, JSON save/load, and unit tests.

> **Scope:** This is a chat assistant, not an autonomous or tool-using agent.
> OpenAI is the only implemented model provider. The provider interface makes
> future integrations possible but they are not included today.

## Requirements

- Python **3.10+**
- An OpenAI API key (API usage may incur charges)

## Quick start

```bash
git clone https://github.com/kakarot987/ai-agent-first.git
cd ai-agent-first
python -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
cp .env.example .env           # Windows: copy .env.example .env
# Edit .env and set OPENAI_API_KEY to your actual key
ai-agent chat
```

Commands: `ai-agent chat` for interactive chat, `ai-agent ask "Hello"`
for one response, and `ai-agent load path/to/conversation.json` to inspect a
saved conversation. In chat, type `help`, `save`, `load <path>`,
`summary`, `clear`, or `exit`.

For the installed module, `python -m ai_agent.cli.main chat` also works.

## Docker

Create `.env` from `.env.example` with a valid key, then run:

```bash
docker compose build
docker compose run --rm ai-agent
```

Conversation files are stored in a named Docker volume at
`/app/conversations`. For local installation, conversations are saved to
`./conversations` by default. No HTTP service is provided; this is a CLI.

## Python API

```python
import asyncio
from ai_agent import AIAgent

async def main():
    agent = AIAgent()
    print(await agent.chat("Hello!"))

asyncio.run(main())
```

Configuration is read from environment variables or `.env`. See
[`.env.example`](.env.example) for supported values. Never commit your API key.

## Development and tests

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m pytest --cov=ai_agent
```

Tests use mocks, so no OpenAI API key or live network request is required.
CI executes the tests on Python 3.11 and 3.13. Runtime Docker and live
API behavior require separate verification with an API key.

## Future improvements

Potential extensions include additional providers, a tool registry, bounded
tool-execution loops, structured tracing, and a real multi-step evaluation.
These are **not** current features.
