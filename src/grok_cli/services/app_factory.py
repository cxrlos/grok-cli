"""Factory for creating and configuring the Grok CLI application."""

from pathlib import Path
from typing import Optional

from grok_cli.api.client import GrokAPIClient
from grok_cli.core.agent import GrokAgent


class AppFactory:
    """Factory for creating and configuring the Grok CLI application."""

    @staticmethod
    def create_api_client() -> GrokAPIClient:
        """Create and configure a Grok API client.

        Returns:
            Configured Grok API client

        Raises:
            ValueError: If API key is not configured
        """
        return GrokAPIClient()

    @staticmethod
    def create_agent(api_client: Optional[GrokAPIClient] = None) -> GrokAgent:
        """Create a Grok agent with optional API client.

        Args:
            api_client: Optional API client (will create one if not provided)

        Returns:
            Configured Grok agent
        """
        if api_client is None:
            api_client = AppFactory.create_api_client()

        return GrokAgent(api_client)

    @staticmethod
    def create_app_with_context(context_path: Optional[Path] = None) -> GrokAgent:
        """Create a complete application with context.

        Args:
            context_path: Optional path to use as context

        Returns:
            Configured Grok agent ready for session
        """
        agent = AppFactory.create_agent()

        # Start the session with the given context
        agent.start_session(context_path)

        return agent
