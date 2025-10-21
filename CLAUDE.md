# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **production-ready** multi-agent LangChain/LangGraph system that coordinates specialized AI agents to handle software development tasks. The system mimics Claude Code and GitHub Codex functionality by breaking down requests into tasks, creating architecture, implementing code, and validating results.

**Recent Major Upgrades** (see IMPROVEMENTS.md for details):
- ✅ Comprehensive syntax validation to eliminate code errors
- ✅ Project manifest system for architectural consistency
- ✅ Language-agnostic design supporting any programming language
- ✅ Enhanced agent coordination through shared documentation
- ✅ Multi-stage validation with self-correction

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

1. **Planner** (`src/nilcode/agents/planner.py`) - Entry point that analyzes requests, detects languages/frameworks, creates task breakdowns
2. **Software Architect** (`src/nilcode/agents/software_architect.py`) - Establishes repository structure, creates PROJECT_MANIFEST.md and architectural guidelines
3. **Coder** (`src/nilcode/agents/coder.py`) - Handles ALL implementation including dependencies, frontend, backend, and configuration files
4. **Tester & Validator** (`src/nilcode/agents/tester.py`) - Validates code syntax/style, writes unit tests, performs code analysis
5. **Error Recovery** (`src/nilcode/agents/error_recovery.py`) - Fixes syntax errors and handles code recovery
6. **Orchestrator** (`src/nilcode/agents/orchestrator.py`) - Coordinates workflow, routes tasks, aggregates results, provides final summaries

### State Management

All agents share a single `AgentState` object defined in `src/nilcode/state/agent_state.py` that contains:
- **messages**: Conversation history between agents
- **tasks**: Task list with status tracking (pending/in_progress/completed)
- **project_files**: Dictionary of file paths to content
- **next_agent**: Routing decision for which agent executes next
- **overall_status**: Workflow status (planning/architecting/implementing/testing/completed/failed)
- **detected_languages**: Languages identified by planner (NEW)
- **frontend_tech**: Frontend frameworks/libraries (NEW)
- **backend_tech**: Backend frameworks/libraries (NEW)
- **project_manifest_path**: Path to PROJECT_MANIFEST.md (NEW)
- **guidelines_path**: Path to .agent-guidelines/ directory (NEW)

The state is passed through the workflow and updated by each agent.

### Agent Tools

Agents have access to tools defined in `src/nilcode/tools/`:

**File Operations** (`file_operations.py`):
- read_file, write_file, edit_file, list_files, create_directory

**Task Management** (`task_management.py`):
- create_task, update_task_status, update_task_result, get_all_tasks, get_pending_tasks

**Code Analysis** (`code_analysis.py`):
- analyze_python_syntax, count_functions, check_imports, find_todos_in_code, check_code_complexity, validate_code_style

**Validation Tools** (`validation_tools.py`):
- validate_python_syntax, validate_python_file, validate_javascript_syntax, validate_html_syntax, validate_json_syntax, check_import_validity, auto_detect_language

**Terminal Tools** (`terminal_tools.py`):
- run_command - Execute shell commands (used by error_recovery agent)

### Workflow Execution

**Simplified workflow:**

1. **Planner** → Analyzes request, detects languages/frameworks, creates tasks
2. **Software Architect** → Creates PROJECT_MANIFEST.md and .agent-guidelines/, sets up structure
3. **Coder** → Implements all code (dependencies, frontend, backend), validates syntax
4. **Tester** → Validates ALL files, checks syntax, writes tests
5. **Error Recovery** → Fixes any syntax errors or issues found
6. **Orchestrator** → Aggregates results and provides summary

**Key improvements:**
- Planner detects tech stack and passes to all agents
- Architect creates documentation that all agents must read
- Developers validate code before marking tasks complete
- Tester performs comprehensive syntax validation on all files

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

## Recent System Improvements

### Syntax Validation System
All developer agents now:
1. Read PROJECT_MANIFEST.md and .agent-guidelines/ before coding
2. Implement code following established patterns
3. **Validate syntax using validation tools** (MANDATORY)
4. Fix any errors found (up to 2 retries)
5. Only mark tasks complete if validation passes

### Language Detection & Support
The planner automatically detects:
- **Languages**: Python, JavaScript, TypeScript, HTML, CSS, Java, Go, etc.
- **Frameworks**: React, Vue, FastAPI, Flask, Django, Express, etc.
- **Categorization**: Automatically separates frontend vs backend tech

Supported validation:
- Python: AST-based syntax validation
- JavaScript/TypeScript: Brace/bracket matching, import validation
- HTML: Tag matching validation
- JSON: Format validation

### Project Manifest System
Software architect creates foundational documentation:
- **PROJECT_MANIFEST.md**: Tech stack, directory structure, naming conventions
- **.agent-guidelines/coding-standards.md**: Language-specific standards
- **.agent-guidelines/file-structure.md**: Where files should go
- **.agent-guidelines/naming-conventions.md**: Naming rules

All developer agents read these before implementing code.

### Enhanced Testing
Tester agent now:
- Validates syntax of EVERY code file
- Uses appropriate validator per file type (.py → Python, .js → JavaScript, etc.)
- Checks import validity
- Reports syntax errors with file names and line numbers
- Writes comprehensive unit tests

## Documentation

- **IMPROVEMENTS.md**: Detailed technical documentation of all improvements
- **UPGRADE_SUMMARY.md**: Quick reference guide to changes
- **CLAUDE.md**: This file - project overview and guidance
