"""ASCII art and visual enhancements for grok-cli."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

GROK_ASCII_ART = """

  /$$$$$$ /$$$$$$$  /$$$$$$ /$$   /$$        /$$$$$$ /$$      /$$$$$$
 /$$__  $| $$__  $$/$$__  $| $$  /$$/       /$$__  $| $$     |_  $$_/
| $$  \__| $$  \ $| $$  \ $| $$ /$$/       | $$  \__| $$       | $$
| $$ /$$$| $$$$$$$| $$  | $| $$$$$/        | $$     | $$       | $$
| $$|_  $| $$__  $| $$  | $| $$  $$        | $$     | $$       | $$
| $$  \ $| $$  \ $| $$  | $| $$\  $$       | $$    $| $$       | $$
|  $$$$$$| $$  | $|  $$$$$$| $$ \  $$      |  $$$$$$| $$$$$$$$/$$$$$$
 \______/|__/  |__/\______/|__/  \__/       \______/|________|______/



"""

GROK_LOGO_SIMPLE = GROK_ASCII_ART


def display_grok_banner() -> None:
    """Display the Grok CLI banner with ASCII art."""
    console.print(
        Panel(
            Text(GROK_ASCII_ART, style="bold blue")
            + "\n"
            + Text(
                "The intelligent command-line companion for developers", style="dim"
            ),
            title="Welcome to",
            border_style="blue",
            padding=(1, 2),
        )
    )


def display_loading_spinner(message: str = "Processing...") -> None:
    """Display a loading spinner with message.

    Args:
        message: Message to display with the spinner
    """
    from rich.spinner import Spinner
    from rich.live import Live

    with Live(Spinner("dots", text=message), console=console, refresh_per_second=10):
        pass


def display_success_message(message: str) -> None:
    """Display a success message with styling.

    Args:
        message: Success message to display
    """
    console.print(f"[green]✓[/green] {message}")


def display_error_message(message: str, details: str = None) -> None:
    """Display an error message with optional details.

    Args:
        message: Error message to display
        details: Optional error details
    """
    console.print(f"[red]✗[/red] {message}")
    if details:
        console.print(Panel(details, title="Error Details", border_style="red"))


def display_warning_message(message: str) -> None:
    """Display a warning message with styling.

    Args:
        message: Warning message to display
    """
    console.print(f"[yellow]⚠️[/yellow] {message}")


def display_info_message(message: str) -> None:
    """Display an info message with styling.

    Args:
        message: Info message to display
    """
    console.print(f"[blue]ℹ️[/blue] {message}")


def display_progress_bar(description: str, total: int, current: int) -> None:
    """Display a progress bar.

    Args:
        description: Description of the progress
        total: Total number of items
        current: Current progress
    """
    from rich.progress import Progress, BarColumn, TextColumn

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task(description, total=total)
        progress.update(task, completed=current)
