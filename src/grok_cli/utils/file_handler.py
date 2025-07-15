"""File and directory handling utilities for grok-cli."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

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

# File type emoji mapping for fun visual display
FILE_TYPE_EMOJIS = {
    # Programming Languages
    ".py": "🐍",  # Python
    ".js": "🟨",  # JavaScript
    ".ts": "🔵",  # TypeScript
    ".jsx": "⚛️",  # React JSX
    ".tsx": "⚛️",  # React TSX
    ".html": "🌐",  # HTML
    ".css": "🎨",  # CSS
    ".scss": "🎨",  # SCSS
    ".sass": "🎨",  # SASS
    ".java": "☕",  # Java
    ".c": "🔧",  # C
    ".cpp": "⚙️",  # C++
    ".h": "🔧",  # Header files
    ".hpp": "⚙️",  # C++ Header
    ".cs": "💎",  # C#
    ".php": "🐘",  # PHP
    ".rb": "💎",  # Ruby
    ".go": "🐹",  # Go
    ".rs": "🦀",  # Rust
    ".swift": "🍎",  # Swift
    ".kt": "⚡",  # Kotlin
    ".scala": "🔴",  # Scala
    ".clj": "🍃",  # Clojure
    ".hs": "λ",  # Haskell
    ".ml": "🐫",  # OCaml
    ".fs": "🔷",  # F#
    ".vue": "💚",  # Vue
    ".svelte": "🟠",  # Svelte
    ".astro": "🚀",  # Astro
    ".elm": "🌳",  # Elm
    ".cljs": "🍃",  # ClojureScript
    ".ex": "💜",  # Elixir
    ".exs": "💜",  # Elixir Script
    # Configuration & Data
    ".json": "📄",  # JSON
    ".xml": "📋",  # XML
    ".yaml": "📄",  # YAML
    ".yml": "📄",  # YAML
    ".toml": "⚙️",  # TOML
    ".ini": "⚙️",  # INI
    ".cfg": "⚙️",  # Config
    ".conf": "⚙️",  # Config
    ".properties": "⚙️",  # Properties
    ".env": "🔐",  # Environment
    ".env.example": "🔐",  # Environment Example
    ".lock": "🔒",  # Lock files
    ".lockfile": "🔒",  # Lock files
    ".package-lock.json": "📦",  # NPM Lock
    ".yarn.lock": "🧶",  # Yarn Lock
    # Documentation
    ".md": "📝",  # Markdown
    ".txt": "📄",  # Text
    ".rst": "📚",  # reStructuredText
    ".log": "📋",  # Log files
    # Database & Scripts
    ".sql": "🗄️",  # SQL
    ".sh": "🐚",  # Shell
    ".bash": "🐚",  # Bash
    ".zsh": "🐚",  # Zsh
    ".fish": "🐟",  # Fish
    # Docker & Git
    ".dockerfile": "🐳",  # Dockerfile
    ".dockerignore": "🐳",  # Docker Ignore
    ".gitignore": "📁",  # Git Ignore
    # Build & Package files
    ".pyc": "⚡",  # Python Compiled
    ".pyo": "⚡",  # Python Optimized
    ".pyd": "⚡",  # Python Dynamic
    # Default fallbacks
    "default": "📄",  # Default file
    "directory": "📁",  # Directory
    "executable": "⚡",  # Executable
    "image": "🖼️",  # Image files
    "video": "🎬",  # Video files
    "audio": "🎵",  # Audio files
    "archive": "📦",  # Archive files
    "document": "📄",  # Document files
}

# Additional file type detection patterns
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".svg",
    ".ico",
    ".webp",
    ".tiff",
    ".tif",
}
VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".mkv",
    ".m4v",
    ".3gp",
}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"}
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lzma"}
DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".odt",
    ".ods",
    ".odp",
}


def get_file_emoji(file_path: Path) -> str:
    """Get the appropriate emoji for a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        Emoji string for the file type
    """
    if file_path.is_dir():
        return FILE_TYPE_EMOJIS["directory"]

    extension = file_path.suffix.lower()

    # Check specific file type categories
    if extension in IMAGE_EXTENSIONS:
        return FILE_TYPE_EMOJIS["image"]
    elif extension in VIDEO_EXTENSIONS:
        return FILE_TYPE_EMOJIS["video"]
    elif extension in AUDIO_EXTENSIONS:
        return FILE_TYPE_EMOJIS["audio"]
    elif extension in ARCHIVE_EXTENSIONS:
        return FILE_TYPE_EMOJIS["archive"]
    elif extension in DOCUMENT_EXTENSIONS:
        return FILE_TYPE_EMOJIS["document"]

    # Check if it's executable
    if os.access(file_path, os.X_OK):
        return FILE_TYPE_EMOJIS["executable"]

    # Check specific file type mappings
    if extension in FILE_TYPE_EMOJIS:
        return FILE_TYPE_EMOJIS[extension]

    # Default fallback
    return FILE_TYPE_EMOJIS["default"]


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


def scan_directory(directory_path: Path, max_depth: int = 3) -> Dict[str, Any]:
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
        # Get all items in directory
        items = list(directory_path.iterdir())

        # Filter out items that should be skipped
        valid_items = []
        for item in items:
            if item.name.startswith("."):
                continue
            if item.is_dir() and should_skip_directory(item.name):
                continue
            valid_items.append(item)

        # If no valid items, return empty result (skip empty folders)
        if not valid_items:
            return {}

        # Sort items for consistent output
        valid_items.sort()

        for item in valid_items:
            if item.is_file() and is_text_file(item):
                file_content = read_file_contents(item)
                if file_content is not None:
                    result["files"].append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "size": item.stat().st_size,
                            "content": file_content,
                            "emoji": get_file_emoji(item),
                        }
                    )

            elif item.is_dir():
                if max_depth > 0:
                    sub_result = scan_directory(item, max_depth - 1)
                    # Only add subdirectory if it has content (not empty)
                    if sub_result and (
                        sub_result.get("files") or sub_result.get("directories")
                    ):
                        result["directories"].append(sub_result)
                        result["contents"][item.name] = sub_result

    except PermissionError:
        console.print(f"[red]Error: Permission denied accessing {directory_path}[/red]")
        return {}
    except Exception as e:
        console.print(f"[red]Error scanning {directory_path}: {e}[/red]")
        return {}

    # Only return result if it has content (files or non-empty subdirectories)
    if result["files"] or result["directories"]:
        return result
    else:
        return {}  # Skip empty folders


def format_directory_tree(directory_data: Dict, indent: str = "") -> str:
    """
    Format directory data into a readable tree structure with emojis.

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

    # Add directory line with emoji
    dir_emoji = get_file_emoji(Path(path))
    lines.append(f"{indent}{dir_emoji} {name}/")

    # Add files with their emojis
    for file_info in directory_data.get("files", []):
        file_name = file_info["name"]
        file_size = file_info["size"]
        file_emoji = file_info.get("emoji", get_file_emoji(Path(file_info["path"])))
        size_str = (
            f" ({file_size:,} bytes)" if file_size > 1024 else f" ({file_size} bytes)"
        )
        lines.append(f"{indent}  {file_emoji} {file_name}{size_str}")

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
            emoji = get_file_emoji(file_path)
            context_parts.append(f"# {emoji} File: {file_path}\n{content}\n")

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
            dir_emoji = get_file_emoji(directory_path)
            context_parts.append(f"# {dir_emoji} Directory: {directory_path}\n{tree}\n")

            # Add file contents
            for file_info in directory_data.get("files", []):
                file_emoji = file_info.get(
                    "emoji", get_file_emoji(Path(file_info["path"]))
                )
                context_parts.append(
                    f"# {file_emoji} File: {file_info['path']}\n{file_info['content']}\n"
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
