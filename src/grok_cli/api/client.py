"""Grok API client for grok-cli."""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

import requests
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel

console = Console()

# Load environment variables
load_dotenv()

# Available Grok models - we'll try these in order if MODEL_NAME is not set
GROK_MODELS = [
    "grok-1.5-preview-0513",
    "grok-1.5-preview",
    "grok-1.5",
    "grok-beta",
    "grok",
]


@dataclass
class Message:
    """Represents a message in the conversation."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """Represents a conversation session with Grok."""

    messages: List[Message] = field(default_factory=list)
    context: str = ""
    session_id: str = ""

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))

    def get_context_length(self) -> int:
        """Get the total length of conversation context."""
        return sum(len(msg.content) for msg in self.messages) + len(self.context)

    def format_for_api(self) -> List[Dict[str, str]]:
        """Format conversation for Grok API."""
        messages = []

        # Add system context if available
        if self.context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Context:\n{self.context}\n\nYou are a helpful AI assistant. You can analyze code, suggest improvements, and help with development tasks. When you suggest shell commands, format them clearly and explain what they do.",
                }
            )

        # Add conversation messages
        for msg in self.messages:
            messages.append({"role": msg.role, "content": msg.content})

        return messages


class GrokAPIClient:
    """Client for interacting with the Grok API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """Initialize the Grok API client.

        Args:
            api_key: Grok API key (defaults to GROK_API_KEY env var)
            base_url: Grok API base URL (defaults to official endpoint)
            model_name: Model name to use (defaults to MODEL_NAME env var or .env)
        """
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROK API key is required. Set GROK_API_KEY environment variable."
            )

        self.base_url = base_url or "https://api.x.ai/v1"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        # Initialize conversation
        self.conversation = Conversation()

        # Model name: use explicit arg, then env, then discovery
        self.model = model_name or os.getenv("MODEL_NAME")
        if self.model:
            console.print(
                f"[green]✓[/green] Using model from MODEL_NAME: [bold]{self.model}[/bold]"
            )
        else:
            self.model = self._discover_available_model()

    def _discover_available_model(self) -> str:
        """Discover which Grok model is available for this API key."""
        console.print("[dim]Discovering available Grok model...[/dim]")

        for model in GROK_MODELS:
            try:
                # Test with a simple request
                test_payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10,
                }

                response = self.session.post(
                    f"{self.base_url}/chat/completions", json=test_payload, timeout=10
                )

                if response.status_code == 200:
                    console.print(f"[green]✓[/green] Using model: {model}")
                    return model
                elif response.status_code == 404:
                    console.print(f"[dim]Model {model} not available[/dim]")
                    continue
                else:
                    console.print(
                        f"[dim]Model {model} returned status {response.status_code}[/dim]"
                    )
                    continue

            except Exception as e:
                console.print(f"[dim]Error testing model {model}: {e}[/dim]")
                continue

        # If no model found, use the first one as fallback
        console.print(
            f"[yellow]Warning: No available models found, using {GROK_MODELS[0]} as fallback[/yellow]"
        )
        return GROK_MODELS[0]

    def set_context(self, context: str) -> None:
        """Set the context for the conversation.

        Args:
            context: File/directory context to include in conversation
        """
        self.conversation.context = context
        console.print(f"[green]✓[/green] Context set ({len(context)} characters)")

    def send_message(self, message: str) -> Optional[str]:
        """Send a message to Grok and get a response.

        Args:
            message: User message to send

        Returns:
            Grok's response, or None if there was an error
        """
        try:
            # Add user message to conversation
            self.conversation.add_message("user", message)

            # Prepare API request
            payload = {
                "model": self.model,
                "messages": self.conversation.format_for_api(),
                "max_tokens": 4000,
                "temperature": 0.7,
                "stream": False,
            }

            console.print(
                f"[dim]Sending message to Grok API (model: {self.model})...[/dim]"
            )

            # Make API request
            response = self.session.post(
                f"{self.base_url}/chat/completions", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]

                # Add assistant response to conversation
                self.conversation.add_message("assistant", assistant_message)

                console.print(
                    f"[green]✓[/green] Response received ({len(assistant_message)} characters)"
                )
                return assistant_message

            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                console.print(f"[red]✗[/red] {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗[/red] Network error: {e}")
            return None
        except Exception as e:
            console.print(f"[red]✗[/red] Unexpected error: {e}")
            return None

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        return {
            "message_count": len(self.conversation.messages),
            "context_length": len(self.conversation.context),
            "total_length": self.conversation.get_context_length(),
            "last_message": (
                self.conversation.messages[-1].content
                if self.conversation.messages
                else None
            ),
        }

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation.messages.clear()
        console.print("[yellow]Conversation history cleared[/yellow]")

    def save_conversation(self, filepath: str) -> bool:
        """Save the conversation to a file.

        Args:
            filepath: Path to save the conversation

        Returns:
            True if successful, False otherwise
        """
        try:
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "context": self.conversation.context,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                    }
                    for msg in self.conversation.messages
                ],
            }

            with open(filepath, "w") as f:
                json.dump(conversation_data, f, indent=2)

            console.print(f"[green]✓[/green] Conversation saved to {filepath}")
            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Failed to save conversation: {e}")
            return False

    def load_conversation(self, filepath: str) -> bool:
        """Load a conversation from a file.

        Args:
            filepath: Path to load the conversation from

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            self.conversation.context = data.get("context", "")
            self.conversation.messages.clear()

            for msg_data in data.get("messages", []):
                timestamp = datetime.fromisoformat(msg_data["timestamp"])
                self.conversation.messages.append(
                    Message(
                        role=msg_data["role"],
                        content=msg_data["content"],
                        timestamp=timestamp,
                    )
                )

            console.print(f"[green]✓[/green] Conversation loaded from {filepath}")
            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Failed to load conversation: {e}")
            return False


def test_grok_connection() -> bool:
    """Test the connection to Grok API.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = GrokAPIClient()
        console.print("[dim]Testing Grok API connection...[/dim]")

        # Send a simple test message
        response = client.send_message("Hello! This is a test message.")

        if response:
            console.print("[green]✓[/green] Grok API connection successful!")
            return True
        else:
            console.print("[red]✗[/red] Grok API connection failed!")
            return False

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize Grok client: {e}")
        return False
