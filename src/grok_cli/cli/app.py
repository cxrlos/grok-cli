"""Main CLI application for grok-cli."""

import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.prompt import Confirm
from rich.live import Live
from rich.table import Table
from rich.text import Text
from time import sleep

from grok_cli.services.app_factory import AppFactory
from grok_cli.utils.file_handler import scan_directory, format_directory_tree
from grok_cli.utils.ui import print_ascii_art, loading_spinner, error_panel, info_panel

console = Console()


def show_context_menu() -> str:
    """Show a visually appealing context selection menu."""
    console.print("\n[bold cyan]Context Selection[/bold cyan]")
    console.print("=" * 50)

    # Create a table for the options
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold yellow")
    table.add_column("Description", style="white")

    table.add_row("1", "Use current directory as context")
    table.add_row("2", "Start without context (empty session)")
    table.add_row("3", "Add specific files or directories to context")
    table.add_row("4", "Exit")

    console.print(table)
    console.print("=" * 50)

    return Prompt.ask(
        "[bold]Select an option[/bold]", choices=["1", "2", "3", "4"], default="1"
    )


def get_custom_context() -> Optional[Path]:
    """Get custom context from user input."""
    console.print("\n[bold cyan]Custom Context Selection[/bold cyan]")
    console.print("Enter the path to a file or directory you want to use as context:")

    while True:
        custom_path = Prompt.ask("[bold]Path[/bold]")
        context_path = Path(custom_path)

        if not context_path.exists():
            console.print(error_panel(f"Path does not exist: {custom_path}"))
            retry = Confirm.ask("Try again?", default=True)
            if not retry:
                return None
            continue

        return context_path


@click.command()
@click.argument("path", required=False)
def main(path: Optional[str] = None) -> None:
    """Grok CLI - A command-line interface for interacting with Grok API.

    Usage:
        grok-cli                    # Use current directory as context
        grok-cli <file_or_dir>      # Use specific file or directory as context
    """
    print_ascii_art(console)

    try:
        # Context selection logic
        context_path: Optional[Path] = None

        if not path:
            # Show tree view of current directory
            with Live(
                loading_spinner("Scanning current directory..."),
                refresh_per_second=8,
                console=console,
            ):
                sleep(0.5)
                directory_data = scan_directory(Path("."), max_depth=2)

            tree = format_directory_tree(directory_data)
            console.print(
                Panel(tree, title="Current Directory Structure", border_style="cyan")
            )

            # Show improved context menu
            choice = show_context_menu()

            if choice == "1":
                # Use current directory
                context_path = Path(".")
                console.print(info_panel("Using current directory as context"))

            elif choice == "2":
                # No context
                context_path = None
                console.print(info_panel("Starting session without context"))

            elif choice == "3":
                # Custom context
                context_path = get_custom_context()
                if context_path is None:
                    console.print(info_panel("No context selected. Exiting."))
                    return
                console.print(info_panel(f"Using custom context: {context_path}"))

            elif choice == "4":
                # Exit
                console.print(info_panel("Exiting. Goodbye!"))
                return

        else:
            # Use provided path
            context_path = Path(path)
            if not context_path.exists():
                console.print(error_panel(f"Path does not exist: {path}"))
                return
            console.print(info_panel(f"Using specified path: {path}"))

        # Create and start the application using the factory
        with Live(
            loading_spinner("Initializing Grok agent..."),
            refresh_per_second=8,
            console=console,
        ):
            sleep(0.5)
            agent = AppFactory.create_app_with_context(context_path)

    except ValueError as e:
        console.print(error_panel(str(e)))
        console.print(
            info_panel(
                "Please set your GROK_API_KEY environment variable:\nexport GROK_API_KEY='your-api-key-here'"
            )
        )
        return
    except Exception as e:
        console.print(error_panel(f"Failed to initialize application: {e}"))
        return


if __name__ == "__main__":
    main()
