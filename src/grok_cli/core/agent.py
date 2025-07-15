"""Core Agent class for managing interactive Grok sessions."""

import re
from typing import Optional, List
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from grok_cli.api.client import GrokAPIClient
from grok_cli.utils.file_handler import (
    validate_paths,
    get_file_context,
    get_directory_context,
)
from grok_cli.utils.command_parser import extract_shell_commands
from grok_cli.utils.command_executor import run_shell_command

console = Console()

SHELL_CMD_PATTERN = re.compile(
    r"```(?:bash|sh)?\n([\s\S]+?)\n```|\$ (.+)", re.MULTILINE
)


class GrokAgent:
    """Main agent class for managing interactive Grok sessions."""

    def __init__(self, api_client: GrokAPIClient):
        """Initialize the Grok agent.

        Args:
            api_client: Configured Grok API client
        """
        self.api_client = api_client
        self.is_running = False

    def start_session(self, context_path: Optional[Path] = None) -> None:
        """Start an interactive session with optional context.

        Args:
            context_path: Optional path to use as context (file or directory)
        """
        self._setup_context(context_path)
        self._run_interactive_loop()

    def _setup_context(self, context_path: Optional[Path] = None) -> None:
        """Set up the context for the session.

        Args:
            context_path: Optional path to use as context
        """
        if context_path:
            self._setup_specific_context(context_path)
        else:
            self._setup_current_directory_context()

    def _setup_specific_context(self, context_path: Path) -> None:
        """Set up context from a specific path.

        Args:
            context_path: Path to use as context
        """
        if not context_path.exists():
            console.print(f"[red]✗[/red] Path does not exist: {context_path}")
            return

        console.print(f"[bold]Using specified path: {context_path}[/bold]")
        self._process_context([str(context_path)])

    def _setup_current_directory_context(self) -> None:
        """Set up context from current directory."""
        current_dir = Path.cwd()
        console.print(f"[bold]Using current directory: {current_dir}[/bold]")
        self._process_context(["."])

    def _process_context(self, context_paths: List[str]) -> None:
        """Process context paths and set up API client context.

        Args:
            context_paths: List of paths to process
        """
        console.print("\n[bold]Processing context...[/bold]")

        valid_files, valid_dirs = validate_paths(context_paths)

        if not valid_files and not valid_dirs:
            console.print("[red]No valid files or directories found. Exiting.[/red]")
            return

        self._display_context_summary(valid_files, valid_dirs)
        self._build_and_set_context(valid_files, valid_dirs)

    def _display_context_summary(
        self, valid_files: List[Path], valid_dirs: List[Path]
    ) -> None:
        """Display a summary of the context being processed.

        Args:
            valid_files: List of valid files
            valid_dirs: List of valid directories
        """
        from rich.table import Table

        summary_table = Table(title="Context Summary")
        summary_table.add_column("Type", style="cyan")
        summary_table.add_column("Path", style="green")
        summary_table.add_column("Status", style="yellow")

        for file_path in valid_files:
            summary_table.add_row("📄 File", str(file_path), "✅ Valid")
        for dir_path in valid_dirs:
            summary_table.add_row("📁 Directory", str(dir_path), "✅ Valid")

        console.print(summary_table)

    def _build_and_set_context(
        self, valid_files: List[Path], valid_dirs: List[Path]
    ) -> None:
        """Build context from files and directories and set it in the API client.

        Args:
            valid_files: List of valid files
            valid_dirs: List of valid directories
        """
        total_context = ""

        if valid_files:
            console.print(f"\n[bold]Reading {len(valid_files)} file(s)...[/bold]")
            file_context = get_file_context(valid_files)
            total_context += file_context + "\n"
            console.print(
                f"[green]✓[/green] Successfully read {len(valid_files)} file(s)"
            )

        if valid_dirs:
            console.print(
                f"\n[bold]Scanning {len(valid_dirs)} directory(ies)...[/bold]"
            )
            for dir_path in valid_dirs:
                console.print(f"  Scanning: {dir_path}")
                from grok_cli.utils.file_handler import scan_directory

                directory_data = scan_directory(dir_path, max_depth=3)
                if directory_data:
                    console.print(
                        f"  [green]✓[/green] Found {len(directory_data.get('files', []))} files"
                    )
                    console.print(
                        f"  [green]✓[/green] Found {len(directory_data.get('directories', []))} subdirectories"
                    )
                else:
                    console.print(f"  [red]✗[/red] Failed to scan {dir_path}")

            directory_context = get_directory_context(valid_dirs)
            total_context += directory_context + "\n"
            console.print(
                f"[green]✓[/green] Successfully scanned {len(valid_dirs)} directory(ies)"
            )

        if total_context:
            self.api_client.set_context(total_context)
            self._display_context_preview(total_context)
        else:
            console.print("\n[dim]No context found. Starting with empty context.[/dim]")

    def _display_context_preview(self, context: str) -> None:
        """Display a preview of the context.

        Args:
            context: The context string to preview
        """
        context_preview = context[:500] + "..." if len(context) > 500 else context
        console.print(f"\n[bold]Context Preview:[/bold]")
        console.print(Panel(context_preview, title="Context", border_style="green"))
        console.print(f"\n[dim]Total context size: {len(context)} characters[/dim]")

    def _run_interactive_loop(self) -> None:
        """Run the main interactive chat loop."""
        console.print(
            Panel(
                "[bold green]Entering interactive chat mode. Type 'exit' or 'quit' to leave.[/bold green]",
                title="Agent Mode",
                border_style="green",
            )
        )

        self.is_running = True

        while self.is_running:
            try:
                user_input = Prompt.ask(
                    "[bold blue]You[/bold blue]", default="", show_default=False
                )

                if self._should_exit(user_input):
                    break

                if not user_input.strip():
                    continue

                self._process_user_input(user_input)

            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Session interrupted. Exiting...[/yellow]")
                break

        self._end_session()

    def _should_exit(self, user_input: str) -> bool:
        """Check if the user wants to exit.

        Args:
            user_input: User's input

        Returns:
            True if user wants to exit
        """
        if user_input.strip().lower() in {"exit", "quit"}:
            console.print("[yellow]Exiting interactive session...[/yellow]")
            return True
        return False

    def _process_user_input(self, user_input: str) -> None:
        """Process user input and handle response.

        Args:
            user_input: User's input message
        """
        response = self.api_client.send_message(user_input)

        if response:
            console.print(Panel(response, title="Grok", border_style="cyan"))
            self._handle_shell_commands(response)
        else:
            console.print("[red]✗[/red] No response from Grok.")

    def _handle_shell_commands(self, response: str) -> None:
        """Extract and handle shell commands from the response.

        Args:
            response: Grok's response text
        """
        commands = extract_shell_commands(response)

        if commands:
            for cmd in commands:
                console.print(
                    Panel(cmd, title="Suggested Shell Command", border_style="yellow")
                )
                if Confirm.ask(
                    f"[bold yellow]Run this command?[/bold yellow]", default=False
                ):
                    run_shell_command(cmd)
                else:
                    console.print("[dim]Command not executed.[/dim]")

    def _end_session(self) -> None:
        """Clean up and end the session."""
        self.is_running = False
        console.print("[bold green]Goodbye![/bold green]")
