# Multi-Agent Development System

A sophisticated LangChain-based multi-agent system that mimics Claude Code and GitHub Codex functionality. This system uses specialized AI agents working together to handle software development tasks from planning to implementation to testing.

## Features

- **Multi-Agent Architecture**: Specialized agents for planning, architecture, implementation, and validation
- **Intelligent Planning**: Automatic task breakdown and prioritization
- **Full-Stack Development**: Support for both frontend and backend code generation
- **Code Validation**: Automated testing and quality checks
- **LangGraph Orchestration**: Sophisticated state management and agent coordination

## Architecture

The system consists of six specialized agents:

### 1. Planner Agent
- Analyzes user requests
- Creates detailed task breakdowns
- Assigns tasks to appropriate agents
- Manages todo list

### 2. Software Architect Agent
- Establishes repository/file structure
- Creates shared configuration and boilerplate
- Documents architectural decisions
- Keeps task storage aligned across agents

### 3. Frontend Developer Agent
- Writes HTML, CSS, JavaScript, TypeScript
- Creates React/Vue components
- Implements UI features
- Follows frontend best practices

### 4. Backend Developer Agent
- Writes Python (FastAPI, Flask, Django)
- Creates Node.js/Express services
- Implements API endpoints
- Handles database operations

### 5. Tester & Validator Agent
- Validates code syntax and style
- Writes unit tests
- Performs code analysis
- Provides quality feedback

### 6. Orchestrator Agent
- Coordinates workflow between agents
- Routes tasks appropriately
- Aggregates results
- Provides final summaries

## Installation

### Prerequisites
- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd a2a_testagent
```

2. Install dependencies:
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:
```
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1
# OR
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Command Line Interface

Run the interactive CLI:
```bash
uv run python src/main_agent.py
```

### Demo Scripts

Run the comprehensive demo:
```bash
uv run python examples/multi_agent_demo.py
```

### Programmatic Usage

```python
from src.main_agent import create_agent_system

# Create the agent system
agent_system = create_agent_system()

# Run a request
final_state = agent_system.run(
    "Create a Python calculator module with add, subtract, multiply, and divide functions"
)

# Check results
print(f"Status: {final_state['overall_status']}")
print(f"Plan: {final_state['plan']}")
```

### Streaming Mode

For real-time progress updates:

```python
from src.main_agent import create_agent_system

agent_system = create_agent_system()

for state_update in agent_system.stream("Create a REST API with FastAPI"):
    agent_name = list(state_update.keys())[0]
    print(f"Agent '{agent_name}' is executing...")
```

## Examples

### Example 1: Simple Calculator

```python
agent_system.run("""
Create a Python calculator module with:
- add(a, b)
- subtract(a, b)
- multiply(a, b)
- divide(a, b) with error handling for division by zero
Include unit tests.
""")
```

### Example 2: Web Application

```python
agent_system.run("""
Create a simple todo list web app:
- Frontend: HTML/CSS/JS with a form and list display
- Backend: FastAPI server with /todos endpoints
- In-memory storage
""")
```

### Example 3: API Development

```python
agent_system.run("""
Create a REST API for a blog:
- User authentication endpoints
- CRUD operations for blog posts
- Python FastAPI implementation
- Include validation and error handling
""")
```

## Project Structure

```
a2a_testagent/
├── src/
│   ├── __init__.py
│   ├── main_agent.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── backend_developer.py
│   │   ├── frontend_developer.py
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   ├── software_architect.py
│   │   ├── tester.py
│   │   └── utils.py
│   ├── state/
│   │   ├── __init__.py
│   │   └── agent_state.py
│   └── tools/
│       ├── __init__.py
│       ├── code_analysis.py
│       ├── file_operations.py
│       └── task_management.py
├── examples/
│   ├── a2a_example.py
│   └── multi_agent_demo.py
├── ARCHITECTURE.md
├── QUICKSTART.md
├── README.md
├── main.py
├── pyproject.toml
├── test_planner.py
└── uv.lock
```

## Agent Tools

### File Operations
- `read_file`: Read file contents
- `write_file`: Create or overwrite files
- `edit_file`: Modify existing files
- `list_files`: List directory contents
- `create_directory`: Create directories

### Task Management
- `create_task`: Create new tasks
- `update_task_status`: Update task progress
- `update_task_result`: Record task results
- `get_all_tasks`: View all tasks
- `get_pending_tasks`: View pending tasks

### Code Analysis
- `analyze_python_syntax`: Check Python syntax
- `count_functions`: Count functions and classes
- `check_imports`: List imports
- `find_todos_in_code`: Find TODO/FIXME comments
- `check_code_complexity`: Analyze complexity
- `validate_code_style`: Check style issues

## Workflow

```
User Request
    �
Planner Agent (creates task breakdown)
    �
Frontend Developer Agent (if UI needed)
    �
Backend Developer Agent (if server-side needed)
    �
Tester & Validator Agent (validates & tests)
    �
Orchestrator Agent (aggregates & summarizes)
    �
Final Output
```

## Configuration

### Model Selection

The system uses OpenAI-compatible models. Configure in agent creation:

```python
from src.agents import create_planner_agent

planner = create_planner_agent(
    api_key="your_api_key",
    base_url="https://your-api-endpoint.com"  # Optional
)
```

Default model: `openai/gpt-oss-20b` (via OpenRouter)

### Temperature Settings

- Planner: 0.3 (balanced creativity and structure)
- Developers: 0.2 (more deterministic code)
- Tester: 0.1 (consistent validation)

## Limitations

- Code generation quality depends on the underlying LLM
- File operations are local only (no remote access)
- Task storage is in-memory (resets between sessions)
- No persistent project state across runs
- Limited to text-based code generation

## Future Enhancements

- [ ] Persistent task and project storage
- [ ] Integration with version control (Git)
- [ ] Support for more programming languages
- [ ] Web UI for better visualization
- [ ] Agent-to-agent communication improvements
- [ ] Context window management for large projects
- [ ] Integration with package managers
- [ ] Code execution and testing capabilities

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenRouter](https://openrouter.ai/)

Inspired by:
- Claude Code (Anthropic)
- GitHub Codex
- Multi-agent systems research

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review example scripts

---

**Note**: This is a demonstration system. While it can generate functional code, always review and test generated code before using it in production.
