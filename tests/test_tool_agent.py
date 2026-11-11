"""Agent behavior tests using deterministic provider stubs, no network or API keys."""

import json

import pytest

from ai_agent.core.tool_agent import FunctionCall, ModelTurn, ToolAgent
from ai_agent.tools.workspace import WorkspaceTools


class FakeModel:
    def __init__(self, turns):
        self.turns = iter(turns)
        self.received = []

    async def complete_tool_turn(self, messages, tools, **kwargs):
        self.received.append(list(messages))
        return next(self.turns)


def call(name, args, ident="call-1"):
    return FunctionCall(ident, name, json.dumps(args))


@pytest.mark.asyncio
async def test_multi_step_real_tool_execution(tmp_path):
    workspace = WorkspaceTools(tmp_path)
    (tmp_path / "inputs" / "brief.txt").write_text("Price: 25\nUnits: 4")
    fake = FakeModel([
        ModelTurn(tool_calls=[call("read_text", {"path": "inputs/brief.txt"}, "1")]),
        ModelTurn(tool_calls=[call("calculate", {"expression": "25 * 4"}, "2")]),
        ModelTurn(tool_calls=[call("write_report", {
            "path": "reports/estimate.md", "content": "Total: $100"
        }, "3")]),
        ModelTurn(content="Created reports/estimate.md with total $100."),
    ])
    result = await ToolAgent(fake, workspace, max_steps=5).run("Estimate project")
    assert result.completed
    assert result.tool_calls == 3
    assert result.model_steps == 4
    assert (tmp_path / "reports" / "estimate.md").read_text() == "Total: $100"
    assert [e["name"] for e in result.trace if e["event"] == "tool_call"] == [
        "read_text", "calculate", "write_report"
    ]
    assert fake.received[1][-1]["role"] == "tool"
    assert json.loads(fake.received[2][-1]["content"]) == {"ok": True, "result": "100"}


@pytest.mark.asyncio
async def test_step_limit_stops_model_without_extra_requests(tmp_path):
    fake = FakeModel([
        ModelTurn(tool_calls=[call("calculate", {"expression": "1+1"}, "1")]),
        ModelTurn(tool_calls=[call("calculate", {"expression": "2+2"}, "2")]),
    ])
    result = await ToolAgent(fake, WorkspaceTools(tmp_path), max_steps=2).run("Add")
    assert result.status == "step_limit"
    assert result.model_steps == 2
    assert result.tool_calls == 2


@pytest.mark.asyncio
async def test_tool_budget_rejects_batch_atomically(tmp_path):
    fake = FakeModel([
        ModelTurn(tool_calls=[
            call("calculate", {"expression": "1+1"}, "1"),
            call("calculate", {"expression": "2+2"}, "2"),
        ])
    ])
    result = await ToolAgent(
        fake, WorkspaceTools(tmp_path), max_tool_calls=1
    ).run("Add")
    assert result.status == "tool_limit"
    assert result.tool_calls == 0


@pytest.mark.asyncio
async def test_unknown_tool_is_not_executed(tmp_path):
    fake = FakeModel([
        ModelTurn(tool_calls=[call("run_shell", {"command": "echo unsafe"})]),
        ModelTurn(content="No shell tool is permitted."),
    ])
    result = await ToolAgent(fake, WorkspaceTools(tmp_path)).run("Run shell")
    assert result.completed
    tool_events = [e for e in result.trace if e["event"] == "tool_call"]
    assert tool_events[0]["ok"] is False


@pytest.mark.asyncio
async def test_invalid_model_response(tmp_path):
    result = await ToolAgent(
        FakeModel([ModelTurn(content=None)]), WorkspaceTools(tmp_path)
    ).run("Do it")
    assert result.status == "invalid_response"


@pytest.mark.asyncio
async def test_budget_validation(tmp_path):
    with pytest.raises(ValueError):
        ToolAgent(FakeModel([]), WorkspaceTools(tmp_path), max_steps=0)
