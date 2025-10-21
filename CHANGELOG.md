# Changelog

All notable changes to NilCode will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] - 2025-01-21 "Validator"

### Added

#### Import Validation System
- **NEW TOOLS**: Import validation and fixing (`import_validator.py`)
- **scan_all_imports**: Extracts all import statements from Python and JavaScript files
- **validate_import_consistency**: Checks for missing modules, incorrect paths, non-existent references
- **suggest_import_fixes**: Provides automated fix suggestions for import issues
- Detects relative import errors in both Python and JavaScript/TypeScript
- Validates module existence and path correctness

#### Test Code Generation System
- **NEW TOOLS**: Test template generators (`test_templates.py`)
- **generate_python_test**: Creates pytest/unittest test code with real assertions
- **generate_fastapi_test**: Creates FastAPI endpoint tests with TestClient
- **generate_javascript_test**: Creates Jest/Vitest test code for functions
- **generate_react_test**: Creates React Testing Library component tests
- **get_test_framework_for_language**: Recommends appropriate testing framework
- Templates include: AAA pattern, edge cases, error handling, proper assertions

#### Enhanced Tester Agent
- **5-Phase Validation Workflow**:
  1. Import Validation & Fixing (scans and fixes all import issues)
  2. Comprehensive Syntax Validation
  3. Code Quality Analysis
  4. **ACTUAL Test Code Generation** (not just empty files)
  5. Comprehensive Reporting
- Tester now WRITES REAL TEST CODE with working assertions
- Automatically detects and fixes import inconsistencies
- Creates complete test files with multiple test cases per function/component
- Includes concrete examples in system prompt for Python and JavaScript tests

### Changed

#### Tester Agent Behavior
- **CRITICAL**: Tester now generates actual test code instead of empty test file shells
- Import validation runs FIRST before other validation phases
- Test files include at least 3 test cases: success, edge cases, error handling
- Uses test generation tools to ensure proper test structure
- Increased emphasis on writing runnable, complete tests

#### Tool Access
- Tester agent now has access to 6 new tools:
  - 3 import validation tools
  - 5 test generation tools (including framework selection)
- Max iterations remains at 30 to accommodate additional validation phases

### Fixed

- **MAJOR**: Tester agent now writes actual test code instead of empty files
- **MAJOR**: Import mismatches between files are now detected and fixed automatically
- Missing test assertions - templates now include proper assertion patterns
- Import validation catches relative path errors, missing modules, incorrect references

### User Feedback Addressed

From user: "The tester is still shit, it does not create tests. The imports do not match with one another"

- ✅ Tester now creates ACTUAL test code with real assertions
- ✅ Import validation and fixing system implemented
- ✅ Test templates provide complete, runnable test code
- ✅ 5-phase workflow ensures thorough validation

---

## [2.0.1] - 2025-01-21 "Validator"

### Added

#### Dependency Manager Agent
- **NEW AGENT**: Dependency Manager creates all project configuration files
- **package.json**: Automatically generated for JavaScript/TypeScript/Node.js projects
  - Includes all required dependencies (React, Next.js, Vue, Express, etc.)
  - Includes dev dependencies (TypeScript, ESLint, testing frameworks)
  - Adds appropriate scripts (dev, build, start, test, lint)
- **pyproject.toml**: Automatically generated for Python projects
  - Includes all required dependencies (FastAPI, Flask, Django, etc.)
  - Includes dev dependencies (pytest, black, mypy)
  - Modern Python packaging format
- **.env.example**: Template for environment variables
  - API keys, database URLs, configuration
  - Comments explaining each variable
- **.gitignore**: Language-appropriate ignore files
  - Node.js: node_modules/, .env, dist/, build/
  - Python: __pycache__/, .venv/, *.pyc
- **Framework configs**: tsconfig.json, next.config.js, vite.config.js, etc.
- **README.md**: Installation and run instructions

#### Workflow Improvements
- Execution order updated: Architect → **Dependency Manager** → Developers → Tester
- Planner updated to assign dependency_manager tasks
- All generated projects are now immediately runnable
- No manual configuration needed

### Changed

#### Agent Coordination
- Dependency Manager runs AFTER Software Architect
- Dependency Manager runs BEFORE Developer agents
- Ensures config files exist before code is written

### Fixed

- Projects now include complete dependency lists
- Missing package.json/pyproject.toml issue resolved
- Environment variable setup documented
- Installation instructions provided

---

## [2.0.0] - 2025-01-21 "Validator"

### Major Features

#### Syntax Validation System
- **Added** comprehensive syntax validation tools (`validation_tools.py`)
- **Added** 7 new validation functions:
  - `validate_python_syntax()` - AST-based Python validation
  - `validate_python_file()` - File-based Python validation
  - `validate_javascript_syntax()` - JavaScript/TypeScript validation
  - `validate_html_syntax()` - HTML tag matching validation
  - `validate_json_syntax()` - JSON format validation
  - `check_import_validity()` - Import statement validation
  - `auto_detect_language()` - Automatic language detection
- **Added** mandatory validation phase before task completion
- **Added** self-correction with retry mechanism (up to 2 attempts)

#### Language-Agnostic Design
- **Added** automatic language and framework detection in planner
- **Added** tech stack categorization (frontend vs backend)
- **Added** language-specific coding patterns and validation
- **Added** support for: Python, JavaScript, TypeScript, HTML, CSS, JSON
- **Added** framework awareness: React, Vue, Angular, FastAPI, Flask, Django, Express

#### Project Manifest System
- **Added** `PROJECT_MANIFEST.md` creation by software architect
- **Added** `.agent-guidelines/` directory with coding standards
- **Added** `coding-standards.md` for language-specific rules
- **Added** `file-structure.md` for directory organization
- **Added** `naming-conventions.md` for naming rules
- **Changed** all developer agents to read manifest before implementing

#### Enhanced Agent Coordination
- **Added** shared context through project documentation
- **Added** 4-phase developer workflow:
  1. Context gathering (read manifest and guidelines)
  2. Code implementation (following established patterns)
  3. Syntax validation (mandatory)
  4. Task completion (only if validation passes)
- **Added** tech stack information to agent state
- **Added** `detected_languages`, `frontend_tech`, `backend_tech` state fields
- **Added** `project_manifest_path` and `guidelines_path` tracking

#### Error Handling & Robustness
- **Added** robust error handling in all agent summary generation
- **Added** graceful degradation on response errors
- **Added** fallback summaries when generation fails
- **Added** warning messages for debugging
- **Fixed** "tuple index out of range" error in response handling

#### Version Management
- **Added** comprehensive version system (`version.py`)
- **Added** ASCII art banner with version information
- **Added** `--version` and `-v` command line flags
- **Added** `version` command in interactive mode
- **Added** `--changelog` command line flag
- **Added** `changelog` command in interactive mode
- **Added** version history tracking
- **Updated** banner display with release date and features

### Changed

#### System Prompts
- **Enhanced** planner prompt with language detection requirements
- **Enhanced** software architect prompt with manifest creation requirements
- **Enhanced** frontend developer prompt with validation workflow
- **Enhanced** backend developer prompt with validation workflow
- **Enhanced** tester prompt with comprehensive validation requirements
- **Added** explicit syntax requirements to all developer prompts
- **Added** common mistakes to avoid in prompts

#### State Management
- **Extended** `AgentState` with new fields for tech stack and documentation
- **Added** language detection data propagation through workflow
- **Improved** state consistency across agents

#### Tool Access
- **Added** validation tools to frontend developer
- **Added** validation tools to backend developer
- **Added** validation tools to tester
- **Increased** max_iterations to 20 for developers (validation retries)
- **Increased** max_iterations to 30 for tester (comprehensive validation)

### Documentation

- **Added** `IMPROVEMENTS.md` - Detailed technical documentation (10,000+ words)
- **Added** `UPGRADE_SUMMARY.md` - Quick reference guide
- **Added** `BUGFIX.md` - Bug fix documentation
- **Added** `CHANGELOG.md` - This file
- **Updated** `CLAUDE.md` with new features and workflow
- **Updated** `README.md` with version 2.0 information

### Breaking Changes

None. All improvements are backward compatible.

### Migration Guide

No migration needed. Version 2.0 is fully backward compatible with 1.0 workflows.

Simply update and run:
```bash
uv sync
uv run nilcode
```

---

## [1.0.0] - 2025-01-15 "Genesis"

### Initial Release

#### Core Features
- Multi-agent LangGraph workflow system
- 6 specialized agents:
  - Planner: Task breakdown and planning
  - Software Architect: Repository scaffolding
  - Frontend Developer: UI implementation
  - Backend Developer: Server-side logic
  - Tester: Code validation and testing
  - Orchestrator: Workflow coordination

#### State Management
- Shared `AgentState` between all agents
- Task tracking with status management
- Project files dictionary
- Agent routing system

#### Tools
- **File Operations**: read_file, write_file, edit_file, list_files, create_directory
- **Task Management**: create_task, update_task_status, get_all_tasks
- **Code Analysis**: analyze_python_syntax, count_functions, check_imports

#### CLI
- Interactive mode with streaming
- Single command mode
- Colored terminal output
- Progress indicators

#### LLM Integration
- OpenRouter API support
- OpenAI API support
- Configurable model selection
- Temperature tuning per agent type

---

## Version Comparison

| Feature | v1.0.0 | v2.0.0 | v2.0.1 | v2.0.2 |
|---------|--------|--------|--------|--------|
| Syntax Validation | ❌ | ✅ | ✅ | ✅ |
| Language Detection | ❌ | ✅ | ✅ | ✅ |
| Project Manifest | ❌ | ✅ | ✅ | ✅ |
| Self-Correction | ❌ | ✅ | ✅ | ✅ |
| Multi-language Support | Partial | Full | Full | Full |
| Error Handling | Basic | Robust | Robust | Robust |
| Version System | ❌ | ✅ | ✅ | ✅ |
| Comprehensive Docs | ❌ | ✅ | ✅ | ✅ |
| Dependency Manager | ❌ | ❌ | ✅ | ✅ |
| Config File Generation | ❌ | ❌ | ✅ | ✅ |
| Import Validation | ❌ | ❌ | ❌ | ✅ |
| Test Code Generation | ❌ | ❌ | ❌ | ✅ |
| Actual Test Code | ❌ | ❌ | ❌ | ✅ |
| Import Fixing | ❌ | ❌ | ❌ | ✅ |

---

## Upgrade Instructions

### From 1.0.0 to 2.0.0

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Sync dependencies:
   ```bash
   uv sync
   ```

3. Test the new version:
   ```bash
   uv run nilcode --version
   ```

4. Try the new features:
   ```bash
   uv run nilcode
   # In interactive mode, try:
   # - version
   # - changelog
   # - Create a NextJS app with React
   ```

No configuration changes needed!

---

## Links

- **Documentation**: See `IMPROVEMENTS.md` for detailed technical docs
- **Quick Start**: See `UPGRADE_SUMMARY.md` for quick reference
- **Bug Fixes**: See `BUGFIX.md` for recent bug fixes
- **Project Info**: See `CLAUDE.md` for project overview

---

## Contributing

To propose changes:
1. Update version in `src/nilcode/version.py`
2. Add entry to this CHANGELOG.md
3. Update `pyproject.toml` version
4. Document in `IMPROVEMENTS.md` if major change

---

[2.0.0]: https://github.com/yourusername/nilcode/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/yourusername/nilcode/releases/tag/v1.0.0
