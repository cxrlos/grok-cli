# Grok CLI

A command-line interface (CLI) tool for interacting with the Grok API, inspired by `claude-code`. This tool provides an interactive session for conversing with the Grok model, with support for file and directory context, command execution, and conversation history.

## Features

- **Grok API Integration**: Direct integration with the official Grok API
- **File & Directory Context**: Read file contents and recursively scan directories
- **Interactive Chat Loop**: Conversational interface with the Grok model
- **Command Execution**: Parse and execute shell commands with confirmation
- **Conversation History**: Maintain context across multiple interactions
- **Performance**: Handle large amounts of context gracefully

## Installation

### Development Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd grok-cli
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Verify installation:
   ```bash
   grok-cli --help
   ```

### Production Installation

```bash
pip install grok-cli
```

## Usage

```bash
# Basic usage
grok-cli

# With specific files or directories
grok-cli --file path/to/file.py --dir path/to/directory
```

## Development

### Project Structure

```
grok-cli/
├── src/
│   └── grok_cli/
│       ├── __init__.py
│       ├── main.py
│       ├── api/           # Grok API integration
│       ├── cli/           # Command-line interface
│       └── utils/         # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
├── pyproject.toml         # Package configuration
└── README.md
```

### Development Dependencies

Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Configuration

The tool uses environment variables for configuration:

- `GROK_API_KEY`: Your Grok API key (required)
- `GROK_API_BASE_URL`: Grok API base URL (optional, defaults to official endpoint)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Status

**Phase 1 Complete**: Project scaffolding and dependencies set up
- ✅ Project structure created
- ✅ Dependencies defined in pyproject.toml
- ✅ Console script entry point configured
- ✅ Basic CLI framework implemented

**Next**: Phase 2 - Core CLI and File Handling
