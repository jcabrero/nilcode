# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent LangChain/LangGraph system that coordinates specialized AI agents to handle software development tasks. The system mimics Claude Code and GitHub Codex functionality by breaking down requests into tasks, creating architecture, implementing code, and validating results.

## Commands

### Development Setup
```bash
# Install dependencies using uv package manager
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and add OPENROUTER_API_KEY or OPENAI_API_KEY
```

### Running the System
```bash
# Interactive CLI
uv run python src/nilcode/main_agent.py
# Or using the installed command
uv run nilcode

# Run demo examples
uv run python examples/multi_agent_demo.py

# Run from main.py (legacy)
uv run python main.py
```

### Testing
```bash
# Run planner tests
uv run python test_planner.py
```

## Architecture

### Multi-Agent Workflow

The system uses LangGraph's StateGraph to coordinate 6 specialized agents:

1. **Planner** (`src/nilcode/agents/planner.py`) - Entry point that analyzes requests, creates task breakdowns, and manages the todo list
2. **Software Architect** (`src/nilcode/agents/software_architect.py`) - Establishes repository structure, creates shared configuration/boilerplate, and documents architectural decisions
3. **Frontend Developer** (`src/nilcode/agents/frontend_developer.py`) - Writes HTML/CSS/JS/TS and React/Vue components
4. **Backend Developer** (`src/nilcode/agents/backend_developer.py`) - Writes Python (FastAPI/Flask/Django) or Node.js services, implements APIs
5. **Tester & Validator** (`src/nilcode/agents/tester.py`) - Validates code syntax/style, writes unit tests, performs code analysis
6. **Orchestrator** (`src/nilcode/agents/orchestrator.py`) - Coordinates workflow, routes tasks, aggregates results, provides final summaries

### State Management

All agents share a single `AgentState` object defined in `src/nilcode/state/agent_state.py` that contains:
- **messages**: Conversation history between agents
- **tasks**: Task list with status tracking (pending/in_progress/completed)
- **project_files**: Dictionary of file paths to content
- **next_agent**: Routing decision for which agent executes next
- **overall_status**: Workflow status (planning/architecting/implementing/testing/completed/failed)

The state is passed through the workflow and updated by each agent.

### Agent Tools

Agents have access to tools defined in `src/nilcode/tools/`:

**File Operations** (`file_operations.py`):
- read_file, write_file, edit_file, list_files, create_directory

**Task Management** (`task_management.py`):
- create_task, update_task_status, update_task_result, get_all_tasks, get_pending_tasks

**Code Analysis** (`code_analysis.py`):
- analyze_python_syntax, count_functions, check_imports, find_todos_in_code, check_code_complexity, validate_code_style

### Workflow Execution

1. User request → Planner creates tasks
2. Software Architect sets up structure (if needed)
3. Developer agents implement code (Frontend/Backend)
4. Tester validates and writes tests
5. Orchestrator aggregates results

Agents use the `next_agent` field in state to route to the next agent. The workflow compiles these routing decisions into conditional edges in the LangGraph.

### Agent Creation Pattern

Each agent follows this pattern:
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

### LLM Configuration
- Default model: `openai/gpt-oss-20b` via OpenRouter
- Temperature varies by agent: Planner (0.3), Developers (0.2), Tester (0.1)
- Supports OpenAI-compatible endpoints via base_url parameter

### Package Structure
The project uses `src/nilcode/` as the package root:
- Package name: `nilcode`
- Entry point: `nilcode = "nilcode.main_agent:main"` in pyproject.toml
- All imports should be relative to `nilcode` package

### State Persistence
- Task storage is in-memory only (resets between sessions)
- File operations are local filesystem only
- No persistent project state across runs

## Python Version
Requires Python 3.14+
