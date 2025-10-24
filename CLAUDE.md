# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NilCode is a production-ready multi-agent LangChain/LangGraph system that coordinates specialized AI agents to handle software development tasks. The system breaks down requests into tasks, creates architecture, implements code, validates results, and can integrate with external AI agents via the A2A (Agent-to-Agent) protocol.

## Commands

### Development Setup
```bash
# Install dependencies using uv package manager
uv sync

# Or install globally as a tool
uv tool install .

# Set up environment variables
cp .env.example .env
# Edit .env and add OPENROUTER_API_KEY or OPENAI_API_KEY
```

### Running the System
```bash
# Interactive CLI (recommended)
uv run nilcode

# If installed globally with 'uv tool install .'
nilcode

# Alternative: Run main entry point directly
uv run python src/nilcode/main_agent.py

# Run demo examples
uv run python examples/multi_agent_demo.py
uv run python examples/a2a_integration_demo.py
```

### Testing
```bash
# Run planner tests
uv run python test_planner.py

# Run specific tests
uv run pytest tests/
```

### A2A External Agent Integration
```bash
# Configure external agents via environment variable
export A2A_AGENTS='[{"name":"agent1","base_url":"http://localhost:9999"}]'

# Or use a config file
export A2A_CONFIG_PATH=a2a_agents.json

# Start A2A server for testing
uv run python -m nilcode.a2a.server
```

## Architecture

### Multi-Agent System

The system uses LangGraph's StateGraph to coordinate **9 specialized agents**:

1. **Orchestrator** - Coordinates workflow, routes tasks, aggregates results, provides summaries
2. **Preplanner** - Initial analysis of requests to determine scope and approach
3. **Planner** - Creates detailed task breakdowns, detects languages/frameworks, discovers A2A agents
4. **Software Architect** - Establishes repository structure, creates PROJECT_MANIFEST.md and .agent-guidelines/
5. **Coder** - Implements all code (dependencies, frontend, backend, config), validates syntax
6. **Tester & Validator** - Validates code syntax/style, writes unit tests, performs code analysis
7. **Error Recovery** - Fixes syntax errors and handles code recovery with self-correction
8. **A2A Client** - Communicates with external agents via Agent-to-Agent protocol
9. **Onchain Detective** - Blockchain-specific agent for analyzing onchain data (Ethereum, Hedera, etc.)

### Workflow Execution

The typical workflow follows this pattern:

```
User Request → Orchestrator → Preplanner → Planner
    ↓
Software Architect (creates manifest & guidelines)
    ↓
Coder (implements with validation)
    ↓
Tester (validates & tests)
    ↓
Error Recovery (if needed)
    ↓
Orchestrator (aggregates results)
```

**Key workflow features:**
- Agents route via `next_agent` field in shared state
- Planner detects tech stack and passes to all agents
- Architect creates documentation that all agents must read
- Coder validates syntax before marking tasks complete
- Tester performs comprehensive validation on all files
- Error Recovery can fix issues with up to 2 retries
- A2A Client handles tasks assigned to external agents

### State Management

All agents share a single `AgentState` object (`src/nilcode/state/agent_state.py`) containing:
- **messages**: Conversation history between agents
- **tasks**: Task list with status tracking (pending/in_progress/completed)
- **project_files**: Dictionary of file paths to content
- **next_agent**: Routing decision for which agent executes next
- **overall_status**: Workflow status (planning/architecting/implementing/testing/completed/failed)
- **detected_languages**: Languages identified by planner
- **frontend_tech**: Frontend frameworks/libraries
- **backend_tech**: Backend frameworks/libraries
- **project_manifest_path**: Path to PROJECT_MANIFEST.md
- **guidelines_path**: Path to .agent-guidelines/ directory

### Agent Creation Pattern

Each agent follows this standard pattern:

```python
def create_agent(api_key: str, base_url: Optional[str] = None):
    model = ChatOpenAI(...)
    tools = [tool1, tool2, ...]
    agent_with_tools = model.bind_tools(tools)

    def agent(state: AgentState) -> AgentState:
        # Process state, call LLM, update state
        return updated_state

    return agent
```

## Key Implementation Details

### Package Structure
- Package name: `nilcode`
- Source root: `src/nilcode/`
- Entry point: `nilcode = "nilcode.main_agent:main"` in pyproject.toml
- All imports are relative to `nilcode` package (e.g., `from nilcode.state.agent_state import AgentState`)

### Agent Tools

Agents have access to tools in `src/nilcode/tools/`:

**File Operations** (`file_operations.py`):
- read_file, write_file, edit_file, list_files, create_directory

**Task Management** (`task_management.py`):
- create_task, update_task_status, update_task_result, get_all_tasks, get_pending_tasks

**Code Analysis** (`code_analysis.py`):
- analyze_python_syntax, count_functions, check_imports, find_todos_in_code, check_code_complexity, validate_code_style

**Validation Tools** (`validation_tools.py`):
- validate_python_syntax, validate_javascript_syntax, validate_html_syntax, validate_json_syntax, check_import_validity, auto_detect_language

**Terminal Tools** (`terminal_tools.py`):
- run_command, run_python_script, install_package, run_tests, run_linter, check_environment

**Git Tools** (`git_tools.py`):
- git_status, git_diff, git_log, git_branch_info, git_show_file, git_file_history, git_check_conflicts

**Codebase Tools** (`codebase_tools.py`):
- find_definition, find_usages, analyze_project_structure, list_files_recursively, search_code_content

**Onchain Tools** (`onchain_tools.py`):
- Query blockchain data, analyze smart contracts, check transactions (supports Ethereum, Hedera, etc.)

### LLM Configuration
- Default model: `openai/gpt-oss-20b` via OpenRouter
- Temperature varies by agent: Planner (0.3), Coder (0.2), Tester (0.1)
- Supports OpenAI-compatible endpoints via base_url parameter
- Configured via `.env` file with OPENROUTER_API_KEY or OPENAI_API_KEY

### A2A External Agent Integration

The system supports connecting to external AI agents via the Agent-to-Agent protocol:

**Components:**
- **A2A Agent Registry** (`src/nilcode/a2a/registry.py`) - Discovers and manages external agents
- **A2A Client Agent** (`src/nilcode/agents/a2a_client.py`) - Communicates with external agents
- **A2A Server** (`src/nilcode/a2a/server.py`) - Example server implementation

**Configuration:**
Configure external agents via environment variable or config file (see Commands section above).

**Workflow:**
1. On startup, registry discovers external agents from configured endpoints
2. Planner queries registry and includes external agents in planning
3. Tasks can be assigned to external agents by name
4. A2A Client handles communication via the A2A protocol
5. Results are aggregated back into the main workflow

**Documentation:** See `docs/A2A_INTEGRATION.md` for detailed setup and usage.

### Project Manifest System

The Software Architect creates foundational documentation:
- **PROJECT_MANIFEST.md**: Tech stack, directory structure, naming conventions
- **.agent-guidelines/coding-standards.md**: Language-specific coding standards
- **.agent-guidelines/file-structure.md**: File organization rules
- **.agent-guidelines/naming-conventions.md**: Naming conventions

All developer agents must read these before implementing code.

### Validation & Error Recovery

**Syntax Validation:**
- Python: AST-based syntax validation
- JavaScript/TypeScript: Brace/bracket matching, import validation
- HTML: Tag matching validation
- JSON: Format validation

**Error Recovery Process:**
1. Coder validates syntax using validation tools (MANDATORY)
2. If errors found, fixes them (up to 2 retries)
3. Only marks tasks complete if validation passes
4. If still failing, Error Recovery agent takes over
5. Error Recovery analyzes errors and proposes fixes
6. Implements fixes and retries validation

### State Persistence
- Task storage is in-memory only (resets between sessions)
- File operations are local filesystem only
- No persistent project state across runs

## Development Guidelines

### Cursor Rules Reference

The project includes extensive Cursor rules in `.cursor/rules/`. Key rules:

- **project-structure.mdc**: Package structure and agent overview
- **environment-setup.mdc**: Environment variables and API configuration
- **agent-implementation.mdc**: Agent implementation patterns
- **state-management.mdc**: AgentState structure and updates
- **workflow-routing.mdc**: Workflow graph and routing logic
- **tools.mdc**: Tool implementation patterns
- **specialized-agents.mdc**: Context Gatherer and Error Recovery agents
- **advanced-tools.mdc**: Git, terminal, and codebase operations

See `.cursor/rules/index.mdc` for complete reference.

### Language & Framework Support

**Automatically detected by Planner:**
- Languages: Python, JavaScript, TypeScript, HTML, CSS, Java, Go, Rust, etc.
- Frontend: React, Vue, Angular, Svelte
- Backend: FastAPI, Flask, Django, Express, NestJS
- Blockchain: Ethereum (ethers.js, web3.py), Hedera SDK

## Python Version

Requires Python 3.14+

## Documentation

- **IMPROVEMENTS.md**: Detailed technical documentation of system improvements
- **UPGRADE_SUMMARY.md**: Quick reference guide to changes
- **docs/A2A_INTEGRATION.md**: A2A protocol integration guide
- **ARCHITECTURE.md**: System architecture details
- **QUICKSTART.md**: Quick start guide
