"""Command execution utilities for running shell commands."""

import subprocess
from typing import Optional
from rich.console import Console
from rich.panel import Panel

console = Console()


def run_shell_command(command: str, cwd: Optional[str] = None) -> int:
    """Run a shell command and stream output to the console.

    Args:
        command: Shell command to execute
        cwd: Working directory for command execution

    Returns:
        Exit code of the command
    """
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
            cwd=cwd,
        )

        # Stream output in real-time
        for line in process.stdout:
            console.print(line.rstrip())

        process.wait()
        return process.returncode

    except Exception as e:
        console.print(f"[red]✗[/red] Error executing command: {e}")
        return 1


def run_shell_command_silent(
    command: str, cwd: Optional[str] = None
) -> tuple[int, str]:
    """Run a shell command silently and return output.

    Args:
        command: Shell command to execute
        cwd: Working directory for command execution

    Returns:
        Tuple of (exit_code, output)
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, cwd=cwd
        )
        return result.returncode, result.stdout

    except Exception as e:
        return 1, str(e)


def validate_command_safety(command: str) -> bool:
    """Validate if a command is safe to execute.

    Args:
        command: Command to validate

    Returns:
        True if command is considered safe
    """
    # List of potentially dangerous commands
    dangerous_patterns = [
        r"\brm\s+-rf\b",  # rm -rf
        r"\bdd\b",  # dd command
        r"\bformat\b",  # format commands
        r"\bchmod\s+777\b",  # chmod 777
        r"\bchown\s+root\b",  # chown root
        r"\bmkfs\b",  # filesystem creation
        r"\bdd\s+if=",  # dd with input file
        r"\b>.*\.\*",  # redirect to wildcard
        r"\brm\s+.*\*",  # rm with wildcards
    ]

    import re

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False

    return True


def execute_with_confirmation(command: str, cwd: Optional[str] = None) -> int:
    """Execute a command with safety validation and confirmation.

    Args:
        command: Command to execute
        cwd: Working directory

    Returns:
        Exit code
    """
    if not validate_command_safety(command):
        console.print(f"[red]⚠️  Warning: Potentially dangerous command detected[/red]")
        console.print(f"[yellow]Command: {command}[/yellow]")

        from rich.prompt import Confirm

        if not Confirm.ask(
            "[bold red]Are you sure you want to run this command?[/bold red]",
            default=False,
        ):
            console.print("[dim]Command execution cancelled.[/dim]")
            return 0

    return run_shell_command(command, cwd)
