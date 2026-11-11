"""Offline scripted showcase of the same orchestration and tool interfaces.

This model is deliberately scripted: it DOES NOT call OpenAI or demonstrate
model planning. It verifies the agent protocol and file effects without API keys.
"""

import json
import re
from pathlib import Path
from typing import Any

from ai_agent.core.tool_agent import FunctionCall, ModelTurn


SAMPLE_BRIEF = """# Example consulting estimate
Project: Customer-support knowledge base prototype
Discovery hours: 12
Implementation hours: 28
Hourly rate (USD): 85
Deliverable: One-page estimate and implementation plan.
"""


def ensure_sample_input(workspace: Path) -> None:
    inputs = workspace / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    brief = inputs / "brief.md"
    if not brief.exists():
        brief.write_text(SAMPLE_BRIEF, encoding="utf-8")


class ScriptedDemoModel:
    """Deterministic four-turn fake model for an honest, reproducible demo."""

    def __init__(self, report_path: str = "reports/example-estimate.md") -> None:
        self.turn = 0
        self.brief = ""
        self.total = ""
        self.report_path = report_path
        self.discovery_hours = ""
        self.implementation_hours = ""
        self.hourly_rate = ""

    async def complete_tool_turn(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        **kwargs: Any,
    ) -> ModelTurn:
        self.turn += 1
        if self.turn == 1:
            return ModelTurn(
                tool_calls=[
                    FunctionCall("demo-read", "read_text", '{"path":"inputs/brief.md"}')
                ]
            )
        if self.turn == 2:
            result = json.loads(messages[-1]["content"])
            if not result["ok"]:
                return ModelTurn(content=f"Could not read input: {result['error']}")
            self.brief = result["result"]
            discovery = re.search(r"Discovery hours:\s*(\d+)", self.brief)
            implementation = re.search(r"Implementation hours:\s*(\d+)", self.brief)
            rate = re.search(r"Hourly rate \(USD\):\s*(\d+)", self.brief)
            if not (discovery and implementation and rate):
                return ModelTurn(content="Demo brief is missing expected number fields.")
            self.discovery_hours = discovery.group(1)
            self.implementation_hours = implementation.group(1)
            self.hourly_rate = rate.group(1)
            expression = (
                f"({self.discovery_hours} + {self.implementation_hours}) "
                f"* {self.hourly_rate}"
            )
            return ModelTurn(
                tool_calls=[
                    FunctionCall(
                        "demo-calc", "calculate", json.dumps({"expression": expression})
                    )
                ]
            )
        if self.turn == 3:
            result = json.loads(messages[-1]["content"])
            if not result["ok"]:
                return ModelTurn(content=f"Calculation failed: {result['error']}")
            self.total = result["result"]
            report = (
                "# Example project estimate\n\n"
                "## Scope\n"
                "Customer-support knowledge base prototype\n\n"
                "## Effort and pricing\n"
                f"Discovery: {self.discovery_hours} hours; "
                f"implementation: {self.implementation_hours} hours.\n"
                f"Hourly rate: ${self.hourly_rate}; "
                f"estimated total: ${self.total} USD.\n\n"
                "## Plan\n"
                "1. Gather requirements and identify source documents.\n"
                "2. Build a small searchable knowledge-base prototype.\n"
                "3. Validate against representative user questions.\n\n"
                "*Illustrative estimate; no client data was used.*\n"
            )
            return ModelTurn(
                tool_calls=[
                    FunctionCall(
                        "demo-write",
                        "write_report",
                        json.dumps(
                            {"path": self.report_path, "content": report}
                        ),
                    )
                ]
            )
        result = json.loads(messages[-1]["content"])
        if not result["ok"]:
            return ModelTurn(content=f"Could not save report: {result['error']}")
        return ModelTurn(
            content=(
                f"Calculated the estimate (${self.total} USD) and saved "
                f"{result['result']}. This was an offline scripted demo."
            )
        )
