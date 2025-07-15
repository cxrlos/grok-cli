"""Command parsing utilities for extracting shell commands from text."""

import re
from typing import List


SHELL_CMD_PATTERN = re.compile(
    r"```(?:bash|sh)?\n([\s\S]+?)\n```|\$ (.+)", re.MULTILINE
)


def extract_shell_commands(text: str) -> List[str]:
    """Extract shell commands from model output.

    Args:
        text: Text to parse for shell commands

    Returns:
        List of extracted shell commands
    """
    commands = []

    for match in SHELL_CMD_PATTERN.finditer(text):
        code_block, dollar_cmd = match.groups()

        if code_block:
            # Handle multi-line code blocks
            lines = code_block.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):  # Skip comments
                    commands.append(line)
        elif dollar_cmd:
            # Handle single-line commands with $ prefix
            commands.append(dollar_cmd.strip())

    return commands


def is_shell_command(text: str) -> bool:
    """Check if text contains shell commands.

    Args:
        text: Text to check

    Returns:
        True if text contains shell commands
    """
    return bool(SHELL_CMD_PATTERN.search(text))


def clean_command(command: str) -> str:
    """Clean a shell command by removing common prefixes and formatting.

    Args:
        command: Raw command string

    Returns:
        Cleaned command string
    """
    # Remove common prefixes
    prefixes_to_remove = ["$", "sudo ", 'bash -c "', '"']

    cleaned = command.strip()
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]

    # Remove trailing quotes
    if cleaned.endswith('"'):
        cleaned = cleaned[:-1]

    return cleaned.strip()
