# Grok CLI 🚀

> **The intelligent command-line companion for developers**

A powerful, agent-style CLI tool that brings the Grok AI model directly to your terminal. Think of it as your personal AI pair programmer that understands your codebase, suggests improvements, and helps you write better code - all through natural conversation.

## ✨ Features

### 🤖 **Agent-Style Interaction**
- **Conversational AI**: Chat naturally with Grok about your code
- **Context Awareness**: Automatically understands your project structure
- **Memory**: Maintains conversation history for iterative development
- **Smart Suggestions**: Get intelligent code suggestions and explanations

### 📁 **Intelligent Context Management**
- **Auto-Scan**: Automatically reads and understands your project files
- **Directory Trees**: Visual representation of your project structure
- **File Analysis**: Deep understanding of your codebase
- **Multi-Format Support**: Works with Python, JavaScript, TypeScript, and 50+ file types

### ⚡ **Command Execution**
- **Safe Execution**: Confirms shell commands before running
- **Real-time Output**: See command results as they happen
- **Safety Checks**: Built-in protection against dangerous commands
- **Smart Parsing**: Automatically detects code blocks and shell commands

### 🛠 **Developer-Friendly**
- **Zero Configuration**: Works out of the box with your Grok API key
- **Simple Interface**: Just `grok-cli` or `grok-cli <path>`
- **Rich Output**: Beautiful, informative terminal interface
- **Cross-Platform**: Works on macOS, Linux, and Windows

## 🚀 Quick Start

### 1. Install
```bash
pip install grok-cli
```

### 2. Configure
Set your Grok API key:
```bash
export GROK_API_KEY="your-api-key-here"
```

### 3. Use
```bash
# Chat with Grok about your current project
grok-cli

# Chat with Grok about a specific file or directory
grok-cli src/
grok-cli app.py
```

## 📖 Usage Examples

### **Code Review & Analysis**
```bash
grok-cli src/
# Ask: "What are the main issues with this codebase?"
# Ask: "How can I improve the error handling?"
# Ask: "Suggest refactoring for the User class"
```

### **Debugging Help**
```bash
grok-cli debug.py
# Ask: "Why is this function failing?"
# Ask: "What's wrong with this error message?"
# Ask: "How can I fix this bug?"
```

### **Feature Development**
```bash
grok-cli
# Ask: "Help me implement user authentication"
# Ask: "Create a function to validate email addresses"
# Ask: "How should I structure this new feature?"
```

### **Learning & Documentation**
```bash
grok-cli complex_algorithm.py
# Ask: "Explain how this algorithm works"
# Ask: "What are the time and space complexities?"
# Ask: "Write documentation for this function"
```

## 🏗 Architecture

Built with production-grade modular architecture:

```
grok-cli/
├── core/           # Business logic & session management
├── api/            # Grok API integration
├── services/       # Application services & dependency injection
├── utils/          # Utilities (file handling, command parsing)
└── cli/            # Clean command-line interface
```

## 🔧 Configuration

### Environment Variables
- `GROK_API_KEY`: Your Grok API key (required)
- `MODEL_NAME`: Specific Grok model to use (optional)

### API Key Setup
1. Get your API key from [x.ai](https://x.ai)
2. Set the environment variable:
   ```bash
   export GROK_API_KEY="your-key-here"
   ```
3. Or create a `.env` file:
   ```
   GROK_API_KEY=your-key-here
   MODEL_NAME=grok-4-0709
   ```

## 🛡 Safety Features

- **Command Confirmation**: All shell commands require explicit approval
- **Dangerous Command Detection**: Built-in protection against risky operations
- **Safe Defaults**: Conservative approach to command execution
- **Clear Feedback**: Always shows what commands will be executed

## 🧪 Development

### Local Development
```bash
# Clone and setup
git clone <repository>
cd grok-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/
```

### Project Structure
```
grok-cli/
├── src/grok_cli/      # Main package
├── tests/             # Test suite
├── docs/              # Documentation
├── pyproject.toml     # Package configuration
└── README.md          # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/grok-cli/issues)
- **Documentation**: [GitHub Wiki](https://github.com/yourusername/grok-cli/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/grok-cli/discussions)

## 🎯 Why Grok CLI?

- **Productive**: Get instant help with coding tasks
- **Intelligent**: Understands context and provides relevant suggestions
- **Safe**: Built-in protections for command execution
- **Simple**: Clean, intuitive interface
- **Powerful**: Full access to Grok's capabilities

---

**Ready to supercharge your development workflow?** 🚀

```bash
pip install grok-cli
grok-cli
```
