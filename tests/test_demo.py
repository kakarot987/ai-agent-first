"""End-to-end offline smoke test for the CLI without OpenAI credentials."""

import json

from click.testing import CliRunner

from ai_agent.cli.main import cli


def test_demo_creates_report_and_trace(tmp_path):
    target = tmp_path / "workspace"
    runner = CliRunner()
    outcome = runner.invoke(cli, ["demo", "--workspace", str(target)])
    assert outcome.exit_code == 0, outcome.output
    report = target / "reports" / "example-estimate.md"
    assert report.exists()
    assert "$3400" in report.read_text()
    trace = json.loads(
        (target / "reports" / "example-estimate-trace.json").read_text()
    )
    assert trace["status"] == "completed"
    assert trace["tool_calls"] == 3
    events = [row for row in trace["trace"] if row["event"] == "tool_call"]
    assert all(event["ok"] for event in events)


def test_demo_second_run_does_not_overwrite(tmp_path):
    target = tmp_path / "workspace"
    runner = CliRunner()
    one = runner.invoke(cli, ["demo", "--workspace", str(target)])
    two = runner.invoke(cli, ["demo", "--workspace", str(target)])
    assert one.exit_code == 0, one.output
    assert two.exit_code == 0, two.output
    assert (target / "reports" / "example-estimate-2.md").exists()
