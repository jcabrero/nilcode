"""
Version management for NilCode multi-agent system.
"""

from typing import Dict, Any
from datetime import datetime

# Version information
__version__ = "2.1.0"
__version_name__ = "Claude"
__release_date__ = "2025-01-21"

# Version history
VERSION_HISTORY = {
    "2.1.0": {
        "name": "Claude",
        "date": "2025-01-21",
        "description": "Redesigned CLI with Claude Code-inspired aesthetic",
        "features": [
            "Clean, minimal banner design with purple/blue theme",
            "Refined color palette inspired by Claude Code",
            "Improved status indicators with subtle symbols (→, ✓, ✗, ·)",
            "Enhanced task list visualization with minimal styling",
            "Better use of whitespace and typography",
            "Dimmed secondary text for better hierarchy",
            "More professional, less emoji-heavy interface",
            "Updated version info and changelog displays",
        ],
        "breaking_changes": [],
    },
    "2.0.2": {
        "name": "Validator",
        "date": "2025-01-21",
        "description": "Enhanced tester agent with actual test code generation and import validation",
        "features": [
            "Import validation and fixing tools (scan_all_imports, validate_import_consistency)",
            "Test code generation templates for Python (pytest/unittest) and JavaScript (Jest/Vitest)",
            "FastAPI test generation with TestClient",
            "React component test generation with React Testing Library",
            "Tester agent now writes ACTUAL test code, not empty test files",
            "5-phase validation workflow: Imports → Syntax → Quality → Tests → Report",
            "Automatic import issue detection and fixing",
        ],
        "breaking_changes": [],
    },
    "2.0.1": {
        "name": "Validator",
        "date": "2025-01-21",
        "description": "Added Dependency Manager agent for complete project configuration",
        "features": [
            "New Dependency Manager agent creates package.json/pyproject.toml",
            "Automatic generation of .env.example files",
            "Framework-specific config files (tsconfig.json, next.config.js, etc.)",
            "Language-appropriate .gitignore files",
            "Complete dependency specifications with versions",
            "README.md with installation and run instructions",
        ],
        "breaking_changes": [],
    },
    "2.0.0": {
        "name": "Validator",
        "date": "2025-01-21",
        "description": "Major upgrade with syntax validation and language-agnostic design",
        "features": [
            "Comprehensive syntax validation for Python, JavaScript, HTML, JSON",
            "Project manifest system for architectural consistency",
            "Language/framework auto-detection",
            "Enhanced agent coordination with shared documentation",
            "Multi-stage validation with self-correction",
            "Robust error handling across all agents",
        ],
        "breaking_changes": [],
    },
    "1.0.0": {
        "name": "Genesis",
        "date": "2025-01-15",
        "description": "Initial release of multi-agent development system",
        "features": [
            "Basic multi-agent workflow (Planner, Architect, Developers, Tester, Orchestrator)",
            "LangGraph state management",
            "File operations and task management",
            "Python code analysis tools",
        ],
        "breaking_changes": [],
    },
}


def get_version() -> str:
    """Get the current version string."""
    return __version__


def get_version_info() -> Dict[str, Any]:
    """Get detailed version information."""
    return {
        "version": __version__,
        "name": __version_name__,
        "release_date": __release_date__,
        "history": VERSION_HISTORY.get(__version__, {}),
    }


def get_banner() -> str:
    """
    Get the NilCode banner with version information.
    Claude Code-inspired design with clean, minimal aesthetic.

    Returns:
        Formatted banner string with colors
    """
    # Colors for banner
    PURPLE = '\033[38;5;141m'
    BLUE = '\033[38;5;111m'
    GRAY = '\033[38;5;245m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ENDC = '\033[0m'
    
    banner = f"""
{PURPLE}{BOLD}
  ███╗   ██╗ ██╗ ██╗       ██████╗  ██████╗  ██████╗  ███████╗
  ████╗  ██║ ██║ ██║      ██╔════╝ ██╔═══██╗ ██╔══██╗ ██╔════╝
  ██╔██╗ ██║ ██║ ██║      ██║      ██║   ██║ ██║  ██║ █████╗  
  ██║╚██╗██║ ██║ ██║      ██║      ██║   ██║ ██║  ██║ ██╔══╝  
  ██║ ╚████║ ██║ ███████╗ ╚██████╗ ╚██████╔╝ ██████╔╝ ███████╗
  ╚═╝  ╚═══╝ ╚═╝ ╚══════╝  ╚═════╝  ╚═════╝  ╚═════╝  ╚══════╝
{ENDC}
{GRAY}  Multi-Agent AI Development System{ENDC}

{DIM}  Version {__version__} "{__version_name__}" · Released {__release_date__}{ENDC}

{GRAY}  ─────────────────────────────────────────────────────────────────{ENDC}

{BLUE}  Capabilities{ENDC}
{GRAY}  • Syntax validation & error correction
  • Language-agnostic code generation
  • Architectural consistency enforcement
  • Multi-stage quality assurance{ENDC}

{BLUE}  Languages{ENDC}
{GRAY}  Python · JavaScript · TypeScript · HTML · CSS{ENDC}

{BLUE}  Frameworks{ENDC}
{GRAY}  React · Vue · FastAPI · Flask · Django · Express{ENDC}

{GRAY}  ─────────────────────────────────────────────────────────────────{ENDC}
"""
    return banner


def get_short_banner() -> str:
    """
    Get a compact version banner with Claude Code styling.

    Returns:
        Compact banner string with colors
    """
    PURPLE = '\033[38;5;141m'
    GRAY = '\033[38;5;245m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    
    return f"""
{PURPLE}{BOLD}NilCode{ENDC} {GRAY}v{__version__} "{__version_name__}"{ENDC}
{GRAY}Multi-Agent Development System · Released {__release_date__}{ENDC}
"""


def print_banner(short: bool = False) -> None:
    """
    Print the NilCode banner.

    Args:
        short: If True, print the compact banner. Default is False.
    """
    if short:
        print(get_short_banner())
    else:
        print(get_banner())


def print_version_info() -> None:
    """Print detailed version information with Claude Code styling."""
    info = get_version_info()
    
    # Colors
    PURPLE = '\033[38;5;141m'
    GRAY = '\033[38;5;245m'
    BLUE = '\033[38;5;111m'
    SUCCESS = '\033[38;5;114m'
    WARNING = '\033[38;5;222m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ENDC = '\033[0m'

    print(f"\n{PURPLE}{BOLD}NilCode{ENDC} {GRAY}v{info['version']} \"{info['name']}\"{ENDC}")
    print(f"{DIM}Released: {info['release_date']}{ENDC}")
    print(f"{GRAY}{'─'*70}{ENDC}\n")

    if info['history']:
        print(f"{info['history'].get('description', 'N/A')}\n")

        if info['history'].get('features'):
            print(f"{BLUE}{BOLD}Features{ENDC}")
            print(f"{GRAY}{'─'*70}{ENDC}")
            for feature in info['history']['features']:
                print(f"{SUCCESS}•{ENDC} {GRAY}{feature}{ENDC}")
            print()

        if info['history'].get('breaking_changes'):
            print(f"{WARNING}{BOLD}Breaking Changes{ENDC}")
            print(f"{GRAY}{'─'*70}{ENDC}")
            for change in info['history']['breaking_changes']:
                print(f"{WARNING}⚠{ENDC} {GRAY}{change}{ENDC}")
            print()


def print_changelog(limit: int = None) -> None:
    """
    Print the version changelog with Claude Code styling.

    Args:
        limit: Maximum number of versions to show. None shows all.
    """
    # Colors
    PURPLE = '\033[38;5;141m'
    GRAY = '\033[38;5;245m'
    BLUE = '\033[38;5;111m'
    SUCCESS = '\033[38;5;114m'
    WARNING = '\033[38;5;222m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ENDC = '\033[0m'
    
    print(f"\n{PURPLE}{BOLD}Version Changelog{ENDC}")
    print(f"{GRAY}{'─'*70}{ENDC}\n")

    versions = sorted(VERSION_HISTORY.keys(), reverse=True)
    if limit:
        versions = versions[:limit]

    for version in versions:
        info = VERSION_HISTORY[version]
        print(f"{BLUE}{BOLD}v{version}{ENDC} {GRAY}\"{info['name']}\" · {info['date']}{ENDC}")
        print(f"{DIM}{info['description']}{ENDC}\n")

        if info.get('features'):
            for feature in info['features']:
                print(f"  {SUCCESS}•{ENDC} {GRAY}{feature}{ENDC}")
            print()

        if info.get('breaking_changes'):
            print(f"  {WARNING}{BOLD}Breaking Changes{ENDC}")
            for change in info['breaking_changes']:
                print(f"  {WARNING}⚠{ENDC} {GRAY}{change}{ENDC}")
            print()

        print(f"{GRAY}{'─'*70}{ENDC}\n")


# Quick version check function
def check_version_compatibility(required_version: str) -> bool:
    """
    Check if current version meets the required version.

    Args:
        required_version: Minimum required version (e.g., "2.0.0")

    Returns:
        True if current version >= required version
    """
    def parse_version(v: str) -> tuple:
        return tuple(map(int, v.split('.')))

    current = parse_version(__version__)
    required = parse_version(required_version)

    return current >= required


if __name__ == "__main__":
    # Demo the banner and version info
    print_banner()
    print_version_info()
    print_changelog()
