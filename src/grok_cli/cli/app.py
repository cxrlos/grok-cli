"""Main CLI application for grok-cli."""

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.version_option(version="0.1.0")
@click.help_option()
def main() -> None:
    """Grok CLI - A command-line interface for interacting with Grok API.

    This tool provides an interactive session for conversing with the Grok model,
    with support for file and directory context, command execution, and conversation history.
    """
    console.print(
        Panel(
            "[bold blue]Grok CLI[/bold blue]\n"
            "[dim]A CLI tool for interacting with Grok API[/dim]\n\n"
            "[yellow]Phase 1 Complete: Project scaffolding and dependencies set up![/yellow]\n"
            "Ready for Phase 2: Core CLI and File Handling",
            title="Welcome",
            border_style="blue",
        )
    )
    console.print("\n[green]✓[/green] Project structure created")
    console.print("[green]✓[/green] Dependencies defined in pyproject.toml")
    console.print("[green]✓[/green] Console script entry point configured")
    console.print("\n[dim]Next: Implement file and directory handling...[/dim]")


if __name__ == "__main__":
    main()
