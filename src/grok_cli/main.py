"""Main entry point for the grok-cli command."""

import sys
from pathlib import Path

# Add the src directory to the Python path for development
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from grok_cli.cli.app import main

if __name__ == "__main__":
    main()
