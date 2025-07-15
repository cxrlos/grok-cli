"""Command execution utilities for grok-cli."""

import subprocess
import sys
from typing import Optional, Tuple

from rich.console import Console

console = Console()


def run_shell_command(command: str) -> int:
    """
    Execute a shell command safely.

    Args:
        command: Shell command to execute

    Returns:
        Exit code of the command
    """
    try:
        console.print(f"[dim]Executing: {command}[/dim]")

        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
        )

        # Display output
        if result.stdout:
            console.print(f"[green]Output:[/green]\n{result.stdout}")

        if result.stderr:
            console.print(f"[yellow]Errors:[/yellow]\n{result.stderr}")

        return result.returncode

    except subprocess.TimeoutExpired:
        console.print("[red]✗[/red] Command timed out after 60 seconds")
        return 1
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to execute command: {e}")
        return 1


def run_shell_command_interactive(command: str) -> int:
    """
    Execute a shell command with interactive output.

    Args:
        command: Shell command to execute

    Returns:
        Exit code of the command
    """
    try:
        console.print(f"[dim]Executing: {command}[/dim]")

        # Run the command with real-time output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                console.print(output.rstrip())

        return process.poll() or 0

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to execute command: {e}")
        return 1


def validate_command_safety(command: str) -> Tuple[bool, str]:
    """
    Validate if a command is safe to execute.

    Args:
        command: Command to validate

    Returns:
        Tuple of (is_safe, reason)
    """
    from .command_parser import is_dangerous_command

    # Check for dangerous commands
    if is_dangerous_command(command):
        return False, "Command is potentially dangerous"

    # Check for system-critical operations
    dangerous_keywords = [
        "rm -rf /",
        "rm -rf /home",
        "rm -rf /usr",
        "rm -rf /etc",
        "dd if=/dev/zero",
        "mkfs",
        "fdisk",
        "format",
        ":(){ :|:& };:",
        "wget | bash",
        "curl | bash",
    ]

    command_lower = command.lower()
    for keyword in dangerous_keywords:
        if keyword in command_lower:
            return False, f"Command contains dangerous keyword: {keyword}"

    return True, "Command appears safe"


def get_command_preview(command: str) -> str:
    """
    Get a preview of what a command will do.

    Args:
        command: Command to preview

    Returns:
        Preview description
    """
    from .command_parser import get_command_description

    description = get_command_description(command)

    # Add safety warning if needed
    is_safe, reason = validate_command_safety(command)
    if not is_safe:
        description += f" ⚠️  {reason}"

    return description
