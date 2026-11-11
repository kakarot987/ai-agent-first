import json

import pytest

from ai_agent.tools.workspace import ToolError, WorkspaceTools, calculate


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("(12 + 28) * 85", "3400"),
        ("10 / 4", "2.5"),
        ("-3 + 8", "5"),
        ("2.50 * 4", "10"),
    ],
)
def test_calculate_valid(expression, expected):
    assert calculate(expression) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('echo nope')",
        "2**1000000",
        "2/0",
        "3 < 7",
        "1e100",
        "a+1",
        "1 + (2 * [3])",
    ],
)
def test_calculate_rejects_unsafe_expressions(expression):
    with pytest.raises(ToolError):
        calculate(expression)


def test_path_traversal_and_absolute_paths_rejected(tmp_path):
    tools = WorkspaceTools(tmp_path)
    for path in [
        "../secret.txt",
        "/etc/passwd",
        "inputs/../../secret.txt",
        "reports/../../secret.md",
        "inputs\\secret.txt",
    ]:
        tool = "write_report" if path.endswith(".md") else "read_text"
        args = (
            {"path": path, "content": "unsafe"}
            if tool == "write_report" else {"path": path}
        )
        result, _ = tools.execute(tool, json.dumps(args))
        assert not result["ok"]


def test_symlink_escape_blocked(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "-outside")
    outside.mkdir()
    (outside / "secret.txt").write_text("secret")
    workspace = WorkspaceTools(tmp_path)
    (tmp_path / "inputs" / "linked.txt").symlink_to(outside / "secret.txt")
    result, _ = workspace.execute(
        "read_text", '{"path":"inputs/linked.txt"}'
    )
    assert not result["ok"]


def test_write_no_overwrite(tmp_path):
    tools = WorkspaceTools(tmp_path)
    assert tools.write_report("reports/report.md", "Hello") == "reports/report.md"
    with pytest.raises(ToolError, match="already exists"):
        tools.write_report("reports/report.md", "New text")
    assert (tmp_path / "reports" / "report.md").read_text() == "Hello"


def test_malformed_and_extra_args_rejected(tmp_path):
    tools = WorkspaceTools(tmp_path)
    for arguments in [
        "not-json",
        "[]",
        '{"expression":"2+2","shell":"yes"}',
    ]:
        result, _ = tools.execute("calculate", arguments)
        assert not result["ok"]


def test_traces_redact_report_contents(tmp_path):
    tools = WorkspaceTools(tmp_path)
    response, public = tools.execute("write_report", json.dumps({
        "path": "reports/test.md", "content": "confidential details"
    }))
    assert response["ok"]
    assert public == {"path": "reports/test.md", "content_chars": 20}
    assert "confidential" not in str(public)
