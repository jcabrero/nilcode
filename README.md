# NilCode v3.0 - AI Development Assistant

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0+-green.svg)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-orange.svg)](https://github.com/langchain-ai/langgraph)
[![A2A Protocol](https://img.shields.io/badge/A2A-Protocol-purple.svg)](https://github.com/a2aproject/A2A)

A sophisticated multi-agent AI system that rivals Claude Code, built with LangChain and LangGraph. NilCode uses **9 specialized AI agents** working together to understand codebases, implement features, fix errors, validate results, and integrate with external agents - all autonomously.

## 🚀 What's New in v3.0

**Major Enhancements:**
- ✅ **9 Specialized Agents** - Preplanner, Coder, Error Recovery, A2A Client, Onchain Detective
- ✅ **A2A External Agent Integration** - Connect to external AI agents via Agent-to-Agent protocol
- ✅ **Project Manifest System** - Structured documentation and guidelines for all agents
- ✅ **Syntax Validation** - Mandatory validation before task completion
- ✅ **Enhanced Error Recovery** - Self-correcting with up to 2 retries
- ✅ **Onchain Detective** - Blockchain-specific agent for Ethereum, Hedera, etc.
- ✅ **Production-Ready** - Comprehensive validation, error handling, and logging

## ✨ Key Features

- **🤖 Multi-Agent Architecture**: 9 specialized agents for different development tasks
- **🔗 A2A External Agent Integration**: Connect to external AI agents via Agent-to-Agent protocol
- **📋 Project Manifest System**: Structured documentation and coding standards
- **🔍 Codebase Intelligence**: Semantic search, definition finding, and project analysis
- **🛠️ Autonomous Development**: From planning to implementation to testing to error fixing
- **🌐 Full-Stack Support**: Frontend (React, Vue) and backend (Python, Node.js) code generation
- **🔧 Self-Correction**: Automatic error detection and fixing with retry logic
- **✅ Syntax Validation**: Mandatory validation before marking tasks complete
- **🧪 Test Execution**: Run tests and validate code automatically
- **📊 Git Awareness**: Understands version control state
- **⚡ LangGraph Orchestration**: Sophisticated state management and agent coordination
- **🔗 Blockchain Integration**: Onchain Detective for Ethereum, Hedera, and other chains

## 🏗️ Architecture

The system consists of **9 specialized agents** working together in a sophisticated workflow:

### Core Agents

#### 1. **Orchestrator Agent** 🎯
- Coordinates workflow between all agents
- Routes tasks appropriately based on capabilities
- Aggregates results from all agents
- Provides final summaries and status updates

#### 2. **Preplanner Agent** 📋
- Initial analysis of user requests
- Determines scope and approach
- Identifies required technologies and frameworks
- Sets up high-level project structure

#### 3. **Planner Agent** 📝
- Creates detailed task breakdowns in JSON format
- Detects programming languages and frameworks
- Discovers and integrates A2A external agents
- Assigns tasks to appropriate agents (internal or external)
- Manages todo list and priorities

#### 4. **Software Architect Agent** 🏗️
- Establishes repository and file structure
- Creates PROJECT_MANIFEST.md with tech stack and conventions
- Sets up .agent-guidelines/ directory with coding standards
- Documents architectural decisions and patterns
- Creates shared configuration and boilerplate

#### 5. **Coder Agent** 💻
- Implements all code (dependencies, frontend, backend, config)
- Validates syntax before marking tasks complete (MANDATORY)
- Handles both frontend and backend development
- Integrates with existing codebases
- Self-corrects errors with up to 2 retries

#### 6. **Tester & Validator Agent** 🧪
- Validates code syntax and style across all files
- Writes comprehensive unit tests
- Executes tests automatically
- Performs code analysis and quality checks
- Provides detailed quality feedback

#### 7. **Error Recovery Agent** 🔧
- Monitors for errors in code and tests
- Analyzes error messages and stack traces
- Proposes and implements fixes
- Retries failed operations with intelligent strategies
- Self-corrects with iterative refinement

#### 8. **A2A Client Agent** 🔗
- Communicates with external agents via A2A protocol
- Handles task delegation to external services
- Manages authentication and error handling
- Integrates external results into main workflow

#### 9. **Onchain Detective Agent** ⛓️
- Blockchain-specific agent for onchain data analysis
- Supports Ethereum, Hedera, and other chains
- Analyzes smart contracts and transactions
- Integrates blockchain data into applications

## 🔗 A2A External Agent Integration

NilCode supports connecting to external AI agents using the **Agent-to-Agent (A2A) protocol**. This allows you to:

- **Delegate specialized tasks** to external expert agents
- **Extend capabilities** without modifying core code
- **Build distributed agent systems** across multiple services
- **Integrate third-party agents** that support A2A protocol

### Quick Setup

#### Option 1: Environment Variable (Inline JSON)
```bash
export A2A_AGENTS='[
  {
    "name": "currency_converter",
    "base_url": "http://localhost:9999",
    "auth_token": "optional-token"
  },
  {
    "name": "weather_service",
    "base_url": "http://localhost:8888"
  }
]'
```

#### Option 2: Configuration File
Create `a2a_agents.json`:
```json
{
  "external_agents": [
    {
      "name": "hedera-manager",
      "base_url": "http://localhost:9000",
      "auth_token": null
    },
    {
      "name": "data_analyzer",
      "base_url": "http://localhost:8888",
      "auth_token": "your-auth-token-if-needed"
    }
  ]
}
```

Then set the config path:
```bash
export A2A_CONFIG_PATH=a2a_agents.json
```

### Example Usage
```bash
# Start an external A2A agent server
python your_a2a_agent.py

# Configure nilcode to use it
export A2A_AGENTS='[{"name":"data_analyzer","base_url":"http://localhost:9999"}]'

# Run nilcode - it can now delegate tasks to the external agent
uv run nilcode "Analyze this dataset: [1, 2, 3, 4, 5]"
```

**📚 See [docs/A2A_INTEGRATION.md](docs/A2A_INTEGRATION.md) for complete documentation**

**🚀 Run [examples/a2a_integration_demo.py](examples/a2a_integration_demo.py) for a working demo**

## 🚀 Installation

### Prerequisites
- **Python 3.14+** (required)
- **[uv](https://github.com/astral-sh/uv)** package manager (recommended)
- **API Key**: OpenRouter or OpenAI API key

### Quick Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd nilcode
```

2. **Install dependencies:**
```bash
uv sync
```

3. **Set up environment variables:**
```bash
# Create .env file
touch .env
```

4. **Configure your API key in `.env`:**
```bash
# Required: Choose ONE of these options
OPENROUTER_API_KEY=sk-or-v1-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here

# Optional: Custom endpoints
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional: Debug mode
DEBUG=1

# Optional: A2A External Agents (see A2A section above)
A2A_AGENTS='[{"name":"agent1","base_url":"http://localhost:9999"}]'
# OR
A2A_CONFIG_PATH=a2a_agents.json
```

### Environment Variables Reference

#### Required API Keys (Choose One)
```bash
# OpenRouter API Key (recommended)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# OpenAI API Key (alternative)
OPENAI_API_KEY=sk-your-key-here
```

#### Optional Configuration
```bash
# Custom API endpoints
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENAI_BASE_URL=https://api.openai.com/v1

# Debug mode (enables verbose logging)
DEBUG=1

# A2A External Agents Configuration
A2A_AGENTS='[{"name":"agent1","base_url":"http://localhost:9999"}]'
A2A_CONFIG_PATH=a2a_agents.json

# LangSmith tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=nilcode
```

## 🎯 Usage

### Command Line Interface

#### Interactive Mode (Recommended)
```bash
uv run nilcode
```

#### Single Command Mode
```bash
uv run nilcode "Create a Python calculator with unit tests"
```

#### Global Installation (Optional)
```bash
# Install globally as a tool
uv tool install .

# Then use anywhere
nilcode "Create a REST API with FastAPI"
```

### Demo Scripts

#### Multi-Agent Demo
```bash
uv run python examples/multi_agent_demo.py
```

#### A2A Integration Demo
```bash
uv run python examples/a2a_integration_demo.py
```

## 🔄 Workflow

The typical workflow follows this sophisticated pattern:

```
User Request
    ↓
Orchestrator (coordinates workflow)
    ↓
Preplanner (analyzes scope and approach)
    ↓
Planner (creates detailed task breakdown)
    ├── Discovers A2A external agents
    ├── Detects tech stack and frameworks
    └── Assigns tasks to appropriate agents
    ↓
Software Architect (creates manifest & guidelines)
    ├── Creates PROJECT_MANIFEST.md
    ├── Sets up .agent-guidelines/
    └── Documents architecture
    ↓
Coder (implements with validation)
    ├── Validates syntax (MANDATORY)
    ├── Self-corrects errors (up to 2 retries)
    └── Only marks complete if validation passes
    ↓
Tester (validates & tests)
    ├── Comprehensive validation
    ├── Unit test generation
    └── Quality analysis
    ↓
Error Recovery (if needed)
    ├── Analyzes errors
    ├── Proposes fixes
    └── Implements corrections
    ↓
A2A Client (for external tasks)
    ├── Communicates with external agents
    ├── Handles authentication
    └── Integrates results
    ↓
Orchestrator (aggregates results)
    ├── Combines all outputs
    ├── Provides final summary
    └── Reports overall status
```

## ⚙️ Configuration

### Model Selection

The system uses OpenAI-compatible models. Configure via environment variables:

```bash
# Default model (OpenRouter)
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Alternative: OpenAI
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

**Default model**: `openai/gpt-oss-20b` (via OpenRouter)

## 📁 Project Structure

```
nilcode/
├── src/nilcode/                    # Main package
│   ├── agents/                     # Specialized agents
│   │   ├── orchestrator.py        # Workflow coordination
│   │   ├── preplanner.py          # Initial analysis
│   │   ├── planner.py             # Task breakdown
│   │   ├── software_architect.py  # Architecture & manifest
│   │   ├── coder.py               # Code implementation
│   │   ├── tester.py              # Validation & testing
│   │   ├── error_recovery.py      # Error fixing
│   │   ├── a2a_client.py          # External agent communication
│   │   ├── onchain_detective.py   # Blockchain analysis
│   │   └── utils.py               # Agent utilities
│   ├── state/                     # State management
│   │   └── agent_state.py         # Shared state definition
│   ├── tools/                     # Agent tools
│   │   ├── file_operations.py     # File management
│   │   ├── task_management.py     # Task handling
│   │   ├── validation_tools.py    # Code validation
│   │   ├── terminal_tools.py      # Command execution
│   │   ├── git_tools.py           # Git operations
│   │   └── onchain_tools.py       # Blockchain tools
│   ├── a2a/                       # A2A integration
│   │   └── registry.py            # External agent registry
│   ├── main_agent.py               # Main entry point
│   ├── cli.py                     # Command-line interface
│   └── config.py                  # Configuration management
├── examples/                       # Demo scripts
│   ├── multi_agent_demo.py        # Multi-agent demonstration
│   └── a2a_integration_demo.py    # A2A integration demo
├── docs/                          # Documentation
│   └── A2A_INTEGRATION.md         # A2A protocol guide
├── external_agents/               # Example external agents
│   └── hedera-manager/            # Hedera blockchain agent
├── a2a_agents.json               # A2A configuration
├── pyproject.toml                 # Project configuration
├── README.md                      # This file
└── CLAUDE.md                      # Development guidelines
```

### Creating Custom Agents

Follow the agent implementation pattern:

```python
from nilcode.state.agent_state import AgentState
from nilcode.tools.file_operations import read_file, write_file

def create_custom_agent(api_key: str, base_url: str = None):
    """Create a custom agent following the standard pattern."""
    from langchain_openai import ChatOpenAI
    
    model = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
        max_tokens=4096
    )
    
    tools = [read_file, write_file]  # Add your tools
    agent_with_tools = model.bind_tools(tools)
    
    def agent(state: AgentState) -> AgentState:
        # Process state, call LLM, update state
        # Return updated state
        return state
    
    return agent
```

## 🚨 Troubleshooting

### Common Issues

#### API Key Not Found
```bash
# Error: Missing API key
❌ Error: API key not found!

# Solution: Set one of these in .env
OPENROUTER_API_KEY=sk-or-v1-your-key
# OR
OPENAI_API_KEY=sk-your-key
```

#### A2A Agents Not Discovered
```bash
# Problem: No external agents found
⚠️  No external agents configured!

# Solutions:
# 1. Set environment variable
export A2A_AGENTS='[{"name":"agent1","base_url":"http://localhost:9999"}]'

# 2. Create config file
echo '{"external_agents":[{"name":"agent1","base_url":"http://localhost:9999"}]}' > a2a_agents.json
export A2A_CONFIG_PATH=a2a_agents.json

# 3. Verify external agent is running
curl http://localhost:9999/.well-known/agent-card.json
```

#### Syntax Validation Errors
```bash
# Problem: Coder agent fails validation
❌ Syntax validation failed

# Solutions:
# 1. Check Python version (requires 3.14+)
python --version

# 2. Enable debug mode
export DEBUG=1

# 3. Check validation tools
uv run python -c "from nilcode.tools.validation_tools import validate_python_syntax; print('OK')"
```

#### Import Errors
```bash
# Problem: Module not found
ModuleNotFoundError: No module named 'nilcode'

# Solution: Install in development mode
uv sync
# OR
pip install -e .
```

### Debug Mode

Enable debug output for troubleshooting:

```bash
export DEBUG=1
uv run nilcode "Your request here"
```

This will show:
- Agent execution details
- Tool calls and responses
- State transitions
- Error details and stack traces


## 🤝 Contributing

Contributions are welcome! Please:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the coding standards
4. **Add tests** if applicable
5. **Update documentation** as needed
6. **Submit a pull request**

### Development Guidelines

- Follow the agent implementation patterns in `.cursor/rules/`
- Use the project's coding standards defined in `.agent-guidelines/`
- Test your changes with the demo scripts
- Update documentation for new features
- Ensure all agents follow the state management patterns

## 📄 License

MIT

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [OpenRouter](https://openrouter.ai/) - Model access
- [A2A SDK](https://pypi.org/project/a2a-sdk/) - Agent-to-Agent protocol

Inspired by:
- Claude Code (Anthropic)
- OpenAI Codex
- Multi-agent systems research
- Agent-to-Agent protocol specification
