"""UI utilities for grok-cli: ASCII art, spinners, error panels, file emojis."""

from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.style import Style
from typing import Optional
import os

GROK_ASCII_ART = r"""

  /$$$$$$ /$$$$$$$  /$$$$$$ /$$   /$$        /$$$$$$ /$$      /$$$$$$
 /$$__  $| $$__  $$/$$__  $| $$  /$$/       /$$__  $| $$     |_  $$_/
| $$  \__| $$  \ $| $$  \ $| $$ /$$/       | $$  \__| $$       | $$
| $$ /$$$| $$$$$$$| $$  | $| $$$$$/        | $$     | $$       | $$
| $$|_  $| $$__  $| $$  | $| $$  $$        | $$     | $$       | $$
| $$  \ $| $$  \ $| $$  | $| $$\  $$       | $$    $| $$       | $$
|  $$$$$$| $$  | $|  $$$$$$| $$ \  $$      |  $$$$$$| $$$$$$$$/$$$$$$
 \______/|__/  |__/\______/|__/  \__/       \______/|________|______/


"""

FILE_EMOJI_MAP = {
    ".py": "🐍",
    ".js": "🟨",
    ".ts": "🔷",
    ".json": "📦",
    ".md": "📄",
    ".txt": "📝",
    ".sh": "💻",
    ".yaml": "🧾",
    ".yml": "🧾",
    ".html": "🌐",
    ".css": "🎨",
    ".csv": "📊",
    ".xml": "🗂",
    ".lock": "🔒",
    ".toml": "⚙️",
    ".ini": "⚙️",
    ".cfg": "⚙️",
    ".env": "🌱",
    ".go": "🐹",
    ".rs": "🦀",
    ".java": "☕️",
    ".c": "🔵",
    ".cpp": "🔷",
    ".h": "📘",
    ".hpp": "📘",
    ".rb": "💎",
    ".php": "🐘",
    ".swift": "🦅",
    ".kt": "🟣",
    ".scala": "🔴",
    ".dart": "🎯",
    ".vue": "🟩",
    ".svelte": "🟧",
    ".dockerfile": "🐳",
    ".lockfile": "🔒",
    ".bat": "🪟",
    ".exe": "📦",
    ".zip": "🗜",
    ".tar": "🗜",
    ".gz": "🗜",
    ".pdf": "📕",
    ".jpg": "🖼",
    ".jpeg": "🖼",
    ".png": "🖼",
    ".gif": "🖼",
    ".svg": "🖼",
}

FOLDER_EMOJI = "📁"
DEFAULT_FILE_EMOJI = "📄"


def get_file_emoji(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    return FILE_EMOJI_MAP.get(ext, DEFAULT_FILE_EMOJI)


def print_ascii_art(console: Optional[Console] = None) -> None:
    c = console or Console()
    c.print(Text(GROK_ASCII_ART, style=Style(color="cyan", bold=True)))


def error_panel(message: str, title: str = "Error") -> Panel:
    return Panel(
        Text(message, style="bold red"), title=title, border_style="red", expand=False
    )


def info_panel(message: str, title: str = "Info") -> Panel:
    return Panel(
        Text(message, style="bold blue"), title=title, border_style="blue", expand=False
    )


def loading_spinner(text: str = "Loading..."):
    return Spinner("dots", text=text, style="bold magenta")
