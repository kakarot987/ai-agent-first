import asyncio
from typing import cast, Any, Dict

import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from pathlib import Path

from src.ai_agent.core.agent import AIAgent
from src.ai_agent.core.config import Settings
from src.ai_agent.core.exceptions import AIAgentException


console = Console()


@click.group()
@click.option("--debug", is_flag=True,
              help="Enable debug logging")
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """AI Agent CLI - A simple conversational AI assistant."""
    ctx.ensure_object(dict)
    ctx_obj = cast(Dict[str, Any], ctx.obj)
    ctx_obj["debug"] = debug


@cli.command()
@click.option("--model",
              default="gpt-3.5-turbo", help="AI model to use")
@click.option(
    "--temperature", default=0.7,
    type=float, help="Response creativity (0.0-1.0)"
)
@click.option("--max-tokens", default=150,
              type=int, help="Maximum response length")
@click.option(
    "--save-dir", default="conversations",
    help="Directory to save conversations"
)
@click.pass_context
def chat(ctx: click.Context, model: str, temperature: float,
         max_tokens: int, save_dir: str) -> None:
    """Start an interactive chat session."""

    try:
        # Initialize settings
        settings = Settings()
        settings.openai_model = model
        settings.openai_temperature = temperature
        settings.openai_max_tokens = max_tokens

        ctx_dict = cast(Dict[str, Any], ctx.obj)
        debug: bool = ctx_dict.get("debug", False)
        if debug:
            settings.log_level = "DEBUG"

        # Initialize agent
        agent = AIAgent(settings=settings)

        # Welcome message
        console.print(
            Panel.fit(
                f"🤖 Welcome to {settings.agent_name}!\n"
                f"Model: {model} | Temperature: {temperature}\n"
                f"Type 'help' for commands or 'quit' to exit.",
                title="AI Agent",
                border_style="blue",
            )
        )

        # Main chat loop
        asyncio.run(_chat_loop(agent, save_dir))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


async def _chat_loop(agent: AIAgent, save_dir: str) -> None:
    """Main chat loop."""

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]").strip()

            # Handle commands
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("👋 Goodbye!")
                break
            elif user_input.lower() == "help":
                _show_help()
                continue
            elif user_input.lower() == "clear":
                agent.clear_history()
                console.print("[green]✓ Conversation history cleared[/green]")
                continue
            elif user_input.lower() == "summary":
                _show_summary(agent)
                continue
            elif user_input.lower() == "save":
                _save_conversation(agent, save_dir)
                continue
            elif user_input.lower().startswith("load "):
                filepath = user_input[5:].strip()
                _load_conversation(agent, filepath)
                continue

            if not user_input:
                continue

            # Get AI response
            console.print("[bold green]AI:[/bold green] ", end="")

            with console.status("[bold green]Thinking...[/bold green]"):
                response = await agent.chat(user_input)

            console.print(response)

        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
            break
        except AIAgentException as e:
            console.print(f"[red]Agent Error: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Unexpected Error: {e}[/red]")


def _show_help() -> None:
    """Show help information."""
    table = Table(title="Available Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")

    commands = [
        ("quit, exit, q", "Exit the chat"),
        ("help", "Show this help message"),
        ("clear", "Clear conversation history"),
        ("summary", "Show conversation summary"),
        ("save", "Save current conversation"),
        ("load <file>", "Load conversation from file"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)


def _show_summary(agent: AIAgent) -> None:
    """Show conversation summary."""
    summary = agent.get_conversation_summary()

    table = Table(title="Conversation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    for key, value in summary.items():
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


def _save_conversation(agent: AIAgent, save_dir: str) -> None:
    """Save conversation to file."""
    try:
        # Create save directory
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        filepath = Path(save_dir) / filename

        # Save conversation
        agent.save_conversation(str(filepath))
        console.print(f"[green]✓ Conversation saved to {filepath}[/green]")

    except Exception as e:
        console.print(f"[red]Failed to save conversation: {e}[/red]")


def _load_conversation(agent: AIAgent, filepath: str) -> None:
    """Load conversation from file."""
    try:
        agent.load_conversation(filepath)
        console.print(f"[green]✓ Conversation loaded from {filepath}[/green]")

        # Show summary of loaded conversation
        summary = agent.get_conversation_summary()
        console.print(f"Loaded {summary['total_messages']} messages")

    except Exception as e:
        console.print(f"[red]Failed to load conversation: {e}[/red]")


@cli.command()
@click.argument("message")
@click.option("--model", default="gpt-3.5-turbo",
              help="AI model to use")
@click.option("--temperature", default=0.7,
              type=float, help="Response creativity")
@click.option("--max-tokens", default=150,
              type=int, help="Maximum response length")
def ask(message: str, model: str,
        temperature: float, max_tokens: int) -> None:
    """Ask the AI a single question."""

    try:
        # Initialize settings
        settings = Settings()
        settings.openai_model = model
        settings.openai_temperature = temperature
        settings.openai_max_tokens = max_tokens

        # Initialize agent
        agent = AIAgent(settings=settings)

        async def get_response() -> str:
            return await agent.chat(message)

        response = asyncio.run(get_response())
        console.print(f"[bold green]AI:[/bold green] {response}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
def load(filepath: str) -> None:
    """Load and display a conversation file."""

    try:
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Display conversation info
        console.print(
            Panel.fit(
                f"Agent: {data.get('agent_name', 'Unknown')}\n"
                f"Model: {data.get('model', 'Unknown')}\n"
                f"Saved: {data.get('saved_at', 'Unknown')}\n"
                f"Messages: {len(data.get('conversation', []))}",
                title="Conversation Info",
                border_style="blue",
            )
        )

        # Display messages
        for msg in data.get("conversation", []):
            role = msg["role"].title()
            content = msg["content"]
            timestamp = msg.get("timestamp", "")

            if role == "User":
                console.print(f"[bold blue]{role}:[/bold blue] {content}")
            else:
                console.print(f"[bold green]{role}:[/bold green] {content}")

            if timestamp:
                console.print(f"[dim]{timestamp}[/dim]")
            console.print()

    except Exception as e:
        console.print(f"[red]Error loading conversation: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    cli()
