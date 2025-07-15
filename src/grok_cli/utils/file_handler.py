"""File and directory handling utilities for grok-cli."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.syntax import Syntax

console = Console()

# Common text file extensions that we can read
TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".md",
    ".txt",
    ".rst",
    ".log",
    ".sql",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".dockerfile",
    ".dockerignore",
    ".gitignore",
    ".env",
    ".env.example",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".properties",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
    ".go",
    ".rs",
    ".swift",
    ".kt",
    ".scala",
    ".clj",
    ".hs",
    ".ml",
    ".fs",
    ".vue",
    ".svelte",
    ".astro",
    ".elm",
    ".cljs",
    ".ex",
    ".exs",
    ".lock",
    ".lockfile",
    ".package-lock.json",
    ".yarn.lock",
}

# Directories to skip when scanning
SKIP_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".env",
    ".pytest_cache",
    ".mypy_cache",
    ".coverage",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode",
    ".DS_Store",
    "Thumbs.db",
    "*.egg-info",
    "*.pyc",
    "*.pyo",
    "*.pyd",
}


def is_text_file(file_path: Path) -> bool:
    """Check if a file is a text file based on its extension."""
    return file_path.suffix.lower() in TEXT_EXTENSIONS


def should_skip_directory(dir_name: str) -> bool:
    """Check if a directory should be skipped during scanning."""
    return dir_name in SKIP_DIRS or dir_name.startswith(".")


def read_file_contents(file_path: Path, max_size: int = 1024 * 1024) -> Optional[str]:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read
        max_size: Maximum file size to read (default: 1MB)

    Returns:
        File contents as string, or None if file cannot be read
    """
    try:
        if not file_path.exists():
            console.print(f"[red]Error: File {file_path} does not exist[/red]")
            return None

        if not file_path.is_file():
            console.print(f"[red]Error: {file_path} is not a file[/red]")
            return None

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            console.print(
                f"[yellow]Warning: File {file_path} is too large ({file_size} bytes). Skipping.[/yellow]"
            )
            return None

        # Read file contents
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return content

    except UnicodeDecodeError:
        console.print(
            f"[yellow]Warning: File {file_path} is not a text file. Skipping.[/yellow]"
        )
        return None
    except PermissionError:
        console.print(f"[red]Error: Permission denied reading {file_path}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return None


def scan_directory(directory_path: Path, max_depth: int = 3) -> Dict[str, any]:
    """
    Recursively scan a directory and create a tree structure.

    Args:
        directory_path: Path to the directory to scan
        max_depth: Maximum depth for recursive scanning

    Returns:
        Dictionary containing directory structure and file contents
    """
    if not directory_path.exists():
        console.print(f"[red]Error: Directory {directory_path} does not exist[/red]")
        return {}

    if not directory_path.is_dir():
        console.print(f"[red]Error: {directory_path} is not a directory[/red]")
        return {}

    result = {
        "path": str(directory_path),
        "name": directory_path.name,
        "type": "directory",
        "contents": {},
        "files": [],
        "directories": [],
    }

    try:
        for item in sorted(directory_path.iterdir()):
            if item.name.startswith("."):
                continue

            if item.is_file() and is_text_file(item):
                file_content = read_file_contents(item)
                if file_content is not None:
                    result["files"].append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "size": item.stat().st_size,
                            "content": file_content,
                        }
                    )

            elif item.is_dir() and not should_skip_directory(item.name):
                if max_depth > 0:
                    sub_result = scan_directory(item, max_depth - 1)
                    if sub_result:
                        result["directories"].append(sub_result)
                        result["contents"][item.name] = sub_result

    except PermissionError:
        console.print(f"[red]Error: Permission denied accessing {directory_path}[/red]")
        return {}
    except Exception as e:
        console.print(f"[red]Error scanning {directory_path}: {e}[/red]")
        return {}

    return result


def format_directory_tree(directory_data: Dict, indent: str = "") -> str:
    """
    Format directory data into a readable tree structure.

    Args:
        directory_data: Directory data from scan_directory
        indent: Current indentation string

    Returns:
        Formatted tree structure as string
    """
    if not directory_data:
        return ""

    lines = []
    path = directory_data.get("path", "")
    name = directory_data.get("name", "")

    # Add directory line
    lines.append(f"{indent}📁 {name}/")

    # Add files
    for file_info in directory_data.get("files", []):
        file_name = file_info["name"]
        file_size = file_info["size"]
        size_str = f" ({file_size} bytes)" if file_size > 1024 else ""
        lines.append(f"{indent}  📄 {file_name}{size_str}")

    # Add subdirectories
    for subdir in directory_data.get("directories", []):
        sub_lines = format_directory_tree(subdir, indent + "  ")
        lines.extend(sub_lines.split("\n"))

    return "\n".join(lines)


def get_file_context(file_paths: List[Path]) -> str:
    """
    Get context from multiple files.

    Args:
        file_paths: List of file paths to read

    Returns:
        Formatted string with file contents
    """
    context_parts = []

    for file_path in file_paths:
        content = read_file_contents(file_path)
        if content:
            context_parts.append(f"# File: {file_path}\n{content}\n")

    return "\n".join(context_parts)


def get_directory_context(directory_paths: List[Path]) -> str:
    """
    Get context from multiple directories.

    Args:
        directory_paths: List of directory paths to scan

    Returns:
        Formatted string with directory structure and file contents
    """
    context_parts = []

    for directory_path in directory_paths:
        directory_data = scan_directory(directory_path)
        if directory_data:
            tree = format_directory_tree(directory_data)
            context_parts.append(f"# Directory: {directory_path}\n{tree}\n")

            # Add file contents
            for file_info in directory_data.get("files", []):
                context_parts.append(
                    f"# File: {file_info['path']}\n{file_info['content']}\n"
                )

    return "\n".join(context_parts)


def validate_paths(paths: List[str]) -> Tuple[List[Path], List[Path]]:
    """
    Validate and categorize file and directory paths.

    Args:
        paths: List of path strings

    Returns:
        Tuple of (file_paths, directory_paths)
    """
    file_paths = []
    directory_paths = []

    for path_str in paths:
        path = Path(path_str)

        if not path.exists():
            console.print(f"[red]Warning: Path {path} does not exist[/red]")
            continue

        if path.is_file():
            if is_text_file(path):
                file_paths.append(path)
            else:
                console.print(
                    f"[yellow]Warning: {path} is not a supported text file type[/yellow]"
                )
        elif path.is_dir():
            directory_paths.append(path)
        else:
            console.print(f"[red]Warning: {path} is neither a file nor directory[/red]")

    return file_paths, directory_paths
