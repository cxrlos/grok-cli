"""Command parsing utilities for grok-cli."""

import re
from typing import List


def extract_shell_commands(text: str) -> List[str]:
    """
    Extract shell commands from text.

    Looks for code blocks that contain shell commands and extracts them.

    Args:
        text: Text to search for shell commands

    Returns:
        List of shell commands found
    """
    commands = []

    # Pattern to match code blocks with shell commands
    # Matches ```bash, ```sh, ```shell, ```zsh, ```fish, or just ```
    code_block_pattern = r"```(?:bash|sh|shell|zsh|fish)?\s*\n(.*?)\n```"

    # Find all code blocks
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)

    for block in code_blocks:
        # Split by lines and filter out empty lines
        lines = [line.strip() for line in block.split("\n") if line.strip()]

        for line in lines:
            # Skip comments and empty lines
            if line.startswith("#") or not line:
                continue

            # Check if it looks like a shell command
            if _is_shell_command(line):
                commands.append(line)

    # Also look for inline commands (commands prefixed with $ or >)
    inline_pattern = r"(?:^|\n)(?:\$|>)\s*([^\n]+)"
    inline_commands = re.findall(inline_pattern, text)

    for cmd in inline_commands:
        if _is_shell_command(cmd):
            commands.append(cmd)

    return list(set(commands))  # Remove duplicates


def _is_shell_command(text: str) -> bool:
    """
    Check if a line of text looks like a shell command.

    Args:
        text: Text to check

    Returns:
        True if it looks like a shell command
    """
    # Common shell command patterns
    shell_patterns = [
        r"^(ls|cd|pwd|mkdir|rmdir|cp|mv|rm|cat|head|tail|grep|find|chmod|chown)",
        r"^(git|npm|yarn|pip|python|node|docker|kubectl)",
        r"^(curl|wget|ssh|scp|rsync)",
        r"^(echo|printf|export|source|\.)",
        r"^(sudo|su|whoami|id|ps|top|kill)",
        r"^[a-zA-Z_][a-zA-Z0-9_]*=.*",  # Variable assignment
        r"^\./",  # Relative path execution
        r"^[a-zA-Z_][a-zA-Z0-9_]*\s+",  # Command with arguments
    ]

    text = text.strip()

    # Check against patterns
    for pattern in shell_patterns:
        if re.match(pattern, text):
            return True

    # Check for common file operations
    if any(op in text for op in [">", "<", ">>", "|", "&&", "||", ";"]):
        return True

    return False


def is_dangerous_command(command: str) -> bool:
    """
    Check if a command is potentially dangerous.

    Args:
        command: Command to check

    Returns:
        True if command is potentially dangerous
    """
    dangerous_patterns = [
        r"rm\s+-rf",  # Recursive force delete
        r"rm\s+--recursive",  # Recursive delete
        r"rm\s+--force",  # Force delete
        r"dd\s+if=",  # Direct disk operations
        r"mkfs\.",  # Filesystem operations
        r"fdisk",  # Partition operations
        r"format",  # Format operations
        r"chmod\s+777",  # Dangerous permissions
        r"chown\s+root",  # Root ownership
        r"sudo\s+rm",  # Sudo with delete
        r"sudo\s+dd",  # Sudo with direct disk
        r"sudo\s+mkfs",  # Sudo with filesystem
        r"sudo\s+format",  # Sudo with format
        r">\s*/dev/",  # Writing to device files
        r":\(\)\s*\{\s*:\|:\s*&\s*\};",  # Fork bomb
        r"wget\s+.*\|\s*bash",  # Download and execute
        r"curl\s+.*\|\s*bash",  # Download and execute
    ]

    command_lower = command.lower()

    for pattern in dangerous_patterns:
        if re.search(pattern, command_lower):
            return True

    return False


def get_command_description(command: str) -> str:
    """
    Get a human-readable description of what a command does.

    Args:
        command: Command to describe

    Returns:
        Description of the command
    """
    # Basic command descriptions
    command_descriptions = {
        "ls": "List directory contents",
        "cd": "Change directory",
        "pwd": "Print working directory",
        "mkdir": "Create directory",
        "rmdir": "Remove empty directory",
        "cp": "Copy files or directories",
        "mv": "Move or rename files",
        "rm": "Remove files or directories",
        "cat": "Display file contents",
        "head": "Display first lines of file",
        "tail": "Display last lines of file",
        "grep": "Search for patterns in files",
        "find": "Search for files",
        "chmod": "Change file permissions",
        "chown": "Change file ownership",
        "git": "Git version control operations",
        "npm": "Node.js package manager",
        "yarn": "Node.js package manager",
        "pip": "Python package installer",
        "python": "Python interpreter",
        "node": "Node.js runtime",
        "docker": "Docker container operations",
        "kubectl": "Kubernetes command line tool",
        "curl": "Transfer data from or to a server",
        "wget": "Retrieve files from the web",
        "ssh": "Secure shell connection",
        "scp": "Secure copy files",
        "rsync": "Synchronize files",
        "echo": "Display a line of text",
        "printf": "Format and print data",
        "export": "Set environment variable",
        "source": "Execute commands from a file",
        "sudo": "Execute command as superuser",
        "su": "Switch user",
        "whoami": "Display current user",
        "id": "Display user identity",
        "ps": "Display process status",
        "top": "Display system processes",
        "kill": "Terminate processes",
    }

    # Get the base command (first word)
    base_command = command.split()[0] if command.split() else ""

    if base_command in command_descriptions:
        return command_descriptions[base_command]

    # Check for dangerous commands
    if is_dangerous_command(command):
        return "⚠️  DANGEROUS: This command could cause data loss or system damage"

    return "Unknown command"
