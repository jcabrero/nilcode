# Changelog

All notable changes to NilCode will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

| Feature | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| Syntax Validation | ❌ | ✅ |
| Language Detection | ❌ | ✅ |
| Project Manifest | ❌ | ✅ |
| Self-Correction | ❌ | ✅ |
| Multi-language Support | Partial | Full |
| Error Handling | Basic | Robust |
| Version System | ❌ | ✅ |
| Comprehensive Docs | ❌ | ✅ |

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
