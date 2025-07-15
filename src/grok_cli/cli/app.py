"""Main CLI application for grok-cli."""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
import re
import shlex
import subprocess
import os

from grok_cli.utils.file_handler import (
    validate_paths,
    get_file_context,
    get_directory_context,
    format_directory_tree,
    scan_directory,
)
from grok_cli.api.client import GrokAPIClient, test_grok_connection

console = Console()

SHELL_CMD_PATTERN = re.compile(
    r"```(?:bash|sh)?\n([\s\S]+?)\n```|\$ (.+)", re.MULTILINE
)


def extract_shell_commands(text: str) -> list:
    """Extract shell commands from model output."""
    commands = []
    for match in SHELL_CMD_PATTERN.finditer(text):
        code_block, dollar_cmd = match.groups()
        if code_block:
            commands.append(code_block.strip())
        elif dollar_cmd:
            commands.append(dollar_cmd.strip())
    return commands


def run_shell_command(command: str) -> int:
    """Run a shell command and stream output to the console."""
    console.print(
        Panel(
            f"[bold]Executing:[/bold]\n[blue]{command}[/blue]",
            title="Shell Command",
            border_style="yellow",
        )
    )
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in process.stdout:
            console.print(line.rstrip())
        process.wait()
        return process.returncode
    except Exception as e:
        console.print(f"[red]✗[/red] Error executing command: {e}")
        return 1


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
            "[yellow]Phase 4: Interactive Agent Mode[/yellow]",
            title="Welcome",
            border_style="blue",
        )
    )

    # Initialize Grok API client
    try:
        grok_client = GrokAPIClient()
        console.print("[green]✓[/green] Grok API client initialized")
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        console.print(
            "[yellow]Please set your GROK_API_KEY environment variable:[/yellow]"
        )
        console.print("export GROK_API_KEY='your-api-key-here'")
        return
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize Grok client: {e}")
        return

    # Determine context path
    if path:
        # Use specified path
        context_path = Path(path)
        if not context_path.exists():
            console.print(f"[red]✗[/red] Path does not exist: {path}")
            return
        context_paths = [str(context_path)]
        console.print(f"[bold]Using specified path: {path}[/bold]")
    else:
        # Use current directory
        context_paths = ["."]
        console.print(f"[bold]Using current directory: {os.getcwd()}[/bold]")

    # Process context
    console.print("\n[bold]Processing context...[/bold]")
    valid_files, valid_dirs = validate_paths(context_paths)

    if not valid_files and not valid_dirs:
        console.print("[red]No valid files or directories found. Exiting.[/red]")
        return

    # Display summary
    summary_table = Table(title="Context Summary")
    summary_table.add_column("Type", style="cyan")
    summary_table.add_column("Path", style="green")
    summary_table.add_column("Status", style="yellow")

    for file_path in valid_files:
        summary_table.add_row("📄 File", str(file_path), "✅ Valid")
    for dir_path in valid_dirs:
        summary_table.add_row("📁 Directory", str(dir_path), "✅ Valid")

    console.print(summary_table)

    # Process files and directories
    total_context = ""

    if valid_files:
        console.print(f"\n[bold]Reading {len(valid_files)} file(s)...[/bold]")
        file_context = get_file_context(valid_files)
        total_context += file_context + "\n"
        console.print(f"[green]✓[/green] Successfully read {len(valid_files)} file(s)")

    if valid_dirs:
        console.print(f"\n[bold]Scanning {len(valid_dirs)} directory(ies)...[/bold]")
        for dir_path in valid_dirs:
            console.print(f"  Scanning: {dir_path}")
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

    # Set context in Grok client
    if total_context:
        grok_client.set_context(total_context)
        context_preview = (
            total_context[:500] + "..." if len(total_context) > 500 else total_context
        )
        console.print(f"\n[bold]Context Preview:[/bold]")
        console.print(Panel(context_preview, title="Context", border_style="green"))
        console.print(
            f"\n[dim]Total context size: {len(total_context)} characters[/dim]"
        )
    else:
        console.print("\n[dim]No context found. Starting with empty context.[/dim]")

    # Interactive chat loop
    console.print(
        Panel(
            "[bold green]Entering interactive chat mode. Type 'exit' or 'quit' to leave.[/bold green]",
            title="Agent Mode",
            border_style="green",
        )
    )

    while True:
        try:
            user_input = Prompt.ask(
                "[bold blue]You[/bold blue]", default="", show_default=False
            )
            if user_input.strip().lower() in {"exit", "quit"}:
                console.print("[yellow]Exiting interactive session...[/yellow]")
                break
            if not user_input.strip():
                continue

            # Send message to Grok
            response = grok_client.send_message(user_input)
            if response:
                console.print(Panel(response, title="Grok", border_style="cyan"))

                # Detect shell commands
                commands = extract_shell_commands(response)
                if commands:
                    for cmd in commands:
                        console.print(
                            Panel(
                                cmd,
                                title="Suggested Shell Command",
                                border_style="yellow",
                            )
                        )
                        if Confirm.ask(
                            f"[bold yellow]Run this command?[/bold yellow]",
                            default=False,
                        ):
                            run_shell_command(cmd)
                        else:
                            console.print("[dim]Command not executed.[/dim]")
            else:
                console.print("[red]✗[/red] No response from Grok.")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Session interrupted. Exiting...[/yellow]")
            break

    console.print("[bold green]Goodbye![/bold green]")


if __name__ == "__main__":
    main()
