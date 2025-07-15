"""Interactive prompts and user input handling for grok-cli."""

from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table

console = Console()


def prompt_for_directory_selection(current_dir: Path) -> Optional[Path]:
    """Prompt user for directory selection when no path is specified.

    Args:
        current_dir: Current working directory

    Returns:
        Selected directory path, None for empty context, or "EXIT" for cancellation
    """
    console.print(
        "\n[bold]No specific path provided. What would you like to do?[/bold]"
    )

    # Show current directory structure
    console.print(f"\n[dim]Current directory: {current_dir}[/dim]")

    # Get directory tree for preview
    from grok_cli.utils.file_handler import scan_directory, format_directory_tree

    directory_data = scan_directory(current_dir, max_depth=2)

    if directory_data:
        tree = format_directory_tree(directory_data)
        console.print(Panel(tree, title="Directory Structure", border_style="green"))

    # Present options
    console.print("\n[bold]Options:[/bold]")
    console.print("1. [green]Yes[/green] - Use current directory contents")
    console.print("2. [yellow]No[/yellow] - Start with empty context")
    console.print("3. [blue]Custom[/blue] - Specify a different directory")
    console.print("4. [red]Cancel[/red] - Exit")

    while True:
        choice = Prompt.ask(
            "\n[bold]What would you like to do?[/bold]",
            choices=["1", "2", "3", "4"],
            default="1",
        )

        if choice == "1":
            return current_dir
        elif choice == "2":
            return None
        elif choice == "3":
            return prompt_for_custom_directory()
        elif choice == "4":
            console.print("[yellow]Exiting...[/yellow]")
            return "EXIT"


def prompt_for_custom_directory() -> Optional[Path]:
    """Prompt user to specify a custom directory.

    Returns:
        Selected directory path or None if user cancels
    """
    console.print("\n[bold]Enter a custom directory path:[/bold]")
    console.print("[dim]Examples:[/dim]")
    console.print("  - [blue]src/[/blue] (relative to current directory)")
    console.print("  - [blue]/home/user/project[/blue] (absolute path)")
    console.print("  - [blue]../parent-project[/blue] (parent directory)")

    while True:
        path_input = Prompt.ask("\n[bold]Directory path[/bold]", default="")

        if not path_input:
            if Confirm.ask(
                "[yellow]Cancel directory selection?[/yellow]", default=True
            ):
                return None
            continue

        try:
            custom_path = Path(path_input)

            # Resolve relative paths
            if not custom_path.is_absolute():
                custom_path = Path.cwd() / custom_path

            if not custom_path.exists():
                console.print(f"[red]✗[/red] Path does not exist: {custom_path}")
                if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                    return None
                continue

            if not custom_path.is_dir():
                console.print(f"[red]✗[/red] Path is not a directory: {custom_path}")
                if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                    return None
                continue

            console.print(f"[green]✓[/green] Selected directory: {custom_path}")
            return custom_path

        except Exception as e:
            console.print(f"[red]✗[/red] Invalid path: {e}")
            if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                return None


def prompt_for_file_selection(directory: Path) -> Optional[List[Path]]:
    """Prompt user to select specific files from a directory.

    Args:
        directory: Directory to select files from

    Returns:
        List of selected file paths or None if user cancels
    """
    from grok_cli.utils.file_handler import scan_directory, is_text_file, get_file_emoji

    console.print(f"\n[bold]Select files from: {directory}[/bold]")

    # Get all text files in directory
    text_files = []
    for item in directory.rglob("*"):
        if item.is_file() and is_text_file(item):
            text_files.append(item)

    if not text_files:
        console.print("[yellow]No text files found in directory.[/yellow]")
        return None

    # Display files in a table with emojis
    table = Table(title="Available Files")
    table.add_column("#", style="cyan")
    table.add_column("Type", style="blue")
    table.add_column("File", style="green")
    table.add_column("Size", style="yellow")

    for i, file_path in enumerate(text_files, 1):
        size = file_path.stat().st_size
        size_str = f"{size:,} bytes" if size > 1024 else f"{size} bytes"
        emoji = get_file_emoji(file_path)
        table.add_row(str(i), emoji, str(file_path.relative_to(directory)), size_str)

    console.print(table)

    console.print("\n[bold]Select files:[/bold]")
    console.print("- Enter file numbers separated by commas (e.g., 1,3,5)")
    console.print("- Enter 'all' to select all files")
    console.print("- Enter 'none' to skip file selection")

    while True:
        selection = Prompt.ask("\n[bold]File selection[/bold]", default="all")

        if selection.lower() == "none":
            return None
        elif selection.lower() == "all":
            return text_files
        else:
            try:
                # Parse comma-separated numbers
                indices = [int(x.strip()) - 1 for x in selection.split(",")]
                selected_files = [
                    text_files[i] for i in indices if 0 <= i < len(text_files)
                ]

                if not selected_files:
                    console.print("[red]✗[/red] No valid files selected.")
                    if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                        return None
                    continue

                console.print(f"[green]✓[/green] Selected {len(selected_files)} files")
                return selected_files

            except (ValueError, IndexError):
                console.print(
                    "[red]✗[/red] Invalid selection. Please enter valid file numbers."
                )
                if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                    return None


def confirm_action(message: str, default: bool = False) -> bool:
    """Display a confirmation prompt with styling.

    Args:
        message: Confirmation message
        default: Default answer

    Returns:
        True if user confirms, False otherwise
    """
    return Confirm.ask(f"[bold]{message}[/bold]", default=default)


def prompt_for_input(message: str, default: str = "") -> str:
    """Display an input prompt with styling.

    Args:
        message: Input message
        default: Default value

    Returns:
        User input
    """
    return Prompt.ask(f"[bold]{message}[/bold]", default=default)
