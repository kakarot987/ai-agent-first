# AI Agent First — bounded tool-using AI agent

An extensible Python application with **two modes**:

- **Chat mode**: OpenAI-backed conversational assistant with CLI, saved
  conversations and an asynchronous provider interface.
- **Task mode**: A bounded multi-step agent that can read a local brief,
  calculate an estimate, and create a Markdown report with execution traces.

The model selects the next function/tool call using OpenAI tool calling. All
tool execution happens in Python using a strict three-tool allowlist.
No shell execution, internet browsing, arbitrary Python execution, or
unrestricted filesystem access is provided.

## Portfolio demonstration

Try a fully **offline scripted walkthrough** (does not require an API key):

```bash
git clone https://github.com/kakarot987/ai-agent-first.git
cd ai-agent-first
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
ai-agent demo
```

This creates `agent-demo/inputs/brief.md` containing an **invented** consulting
estimate, calls three real local tools, and writes:

- `agent-demo/reports/example-estimate.md` (40 hours × $85 = $3,400)
- `agent-demo/reports/example-estimate-trace.json`

The scripted demo demonstrates deterministic orchestration, **not model
reasoning or planning**. It uses `ScriptedDemoModel` in place of the API.
Repeated runs write new report filenames rather than overwriting existing work.

## Run a model-driven tool agent

Requires Python 3.10+, an OpenAI API key, and an API account with billing
enabled. **OpenAI API usage may incur charges.**

```bash
cp .env.example .env      # Windows: copy .env.example .env
# Edit .env and set OPENAI_API_KEY
mkdir -p agent-workspace/inputs
cp agent-demo/inputs/brief.md agent-workspace/inputs/brief.md
ai-agent run "Read inputs/brief.md, calculate the estimated total, and write reports/estimate.md with a project plan." \
  --workspace agent-workspace --max-steps 6 --max-tool-calls 10 \
  --trace agent-workspace/reports/run-trace.json
```

Run `ai-agent demo` before copying the sample brief, or create your own
`agent-workspace/inputs/brief.md`. Model-driven decisions and the final
report vary by model response and have **not** been validated against a live API.

### Tool permissions and safety limits

| Tool | Allowed operation |
|---|---|
| `read_text` | Read UTF-8 `.md`, `.txt`, `.csv`, `.json` under `inputs/`, max 32 KiB |
| `calculate` | Decimal arithmetic with `+ - * /` and parentheses, bounded |
| `write_report` | Create (never overwrite) `.md` or `.txt` files under `reports/`, max 16 KiB |

The loop defaults to **6 model turns** and **10 total tool calls**; additional
hard caps are 12 model turns and 40 tool calls. Requests above the remaining
tool budget are rejected. Path traversal, symlink escape, unknown tools,
unrecognized argument fields, and unsupported expressions are rejected.

**Security limitations:** Input documents are untrusted; this is a learning
project, not a hardened agent sandbox. The model can still produce incorrect
answers or include sensitive input content in reports. Only use a dedicated
workspace with non-sensitive data. Trace files may contain paths, expressions,
and model-token statistics; keep them private if needed. No human approval
flow or model cost budget is implemented.

## Chat CLI

```bash
ai-agent chat
ai-agent ask "What is an AI agent?"
ai-agent load conversations/a-saved-chat.json
```

Inside chat: `help`, `save`, `load <path>`, `summary`, `clear`, `exit`.
Use `python -m ai_agent.cli.main --help` for all commands.

## Docker

Create `.env` with a valid API key. Docker runs the **chat CLI**:

```bash
docker compose build
docker compose run --rm ai-agent
```

For task/demo mode, use a local Python installation as described above.
The Docker image does not bundle a sample workspace.

## Python API

```python
import asyncio
from ai_agent import AIAgent

async def main():
    agent = AIAgent()
    print(await agent.chat("Hello!"))

asyncio.run(main())
```

## Tests

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

Tests mock OpenAI and cover chat, CLI, tool routing, multi-step execution,
step/tool limits, path restrictions and the offline walkthrough. GitHub Actions
runs on Python 3.11 and 3.13.

## Architecture

```text
CLI
 ├─ chat / ask → AIAgent → OpenAIProvider (async) → OpenAI API
 └─ run → ToolAgent → OpenAIProvider tool-call response
                     ↓
                     WorkspaceTools (allowlist)
                     ├─ read_text (inputs/)
                     ├─ calculate (bounded arithmetic)
                     └─ write_report (reports/)
      ↳ tool results → model → final answer or bounded termination

demo → ToolAgent → ScriptedDemoModel (offline) → same WorkspaceTools
```

## Remaining limitations and possible improvements

The model-driven workflow needs a live API smoke test, evaluation against
more sample tasks, user confirmation for external actions, budget tracking and
structured runtime telemetry. The agent is bounded and tool-using; it is
**not** an unrestricted autonomous assistant or production-ready consultancy
platform. Only OpenAI is implemented as a live model provider.
