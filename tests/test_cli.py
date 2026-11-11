"""CLI smoke tests without live API calls."""

from click.testing import CliRunner

from ai_agent.cli.main import cli


def test_cli_help():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "chat" in result.output
    assert "ask" in result.output


def test_chat_help():
    result = CliRunner().invoke(cli, ["chat", "--help"])
    assert result.exit_code == 0
    assert "--model" in result.output
