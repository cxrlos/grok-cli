"""Main CLI application for grok-cli."""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from grok_cli.services.app_factory import AppFactory

console = Console()


@click.command()
@click.argument("path", required=False)
def main(path: str = None) -> None:
    """Grok CLI - A command-line interface for interacting with Grok API.

    Usage:
        grok-cli                    # Use current directory as context
        grok-cli <file_or_dir>      # Use specific file or directory as context
    """
    console.print(
        Panel(
            "[bold blue]Grok CLI[/bold blue]\n"
            "[dim]A CLI tool for interacting with Grok API[/dim]\n\n"
            "[yellow]Modular Architecture - Production Ready[/yellow]",
            title="Welcome",
            border_style="blue",
        )
    )

    try:
        # Parse context path
        context_path = None
        if path:
            context_path = Path(path)
            if not context_path.exists():
                console.print(f"[red]✗[/red] Path does not exist: {path}")
                return

        # Create and start the application using the factory
        agent = AppFactory.create_app_with_context(context_path)

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        console.print(
            "[yellow]Please set your GROK_API_KEY environment variable:[/yellow]"
        )
        console.print("export GROK_API_KEY='your-api-key-here'")
        return
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize application: {e}")
        return


if __name__ == "__main__":
    main()
