"""
Version management for NilCode multi-agent system.
"""

from typing import Dict, Any
from datetime import datetime

# Version information
__version__ = "2.0.0"
__version_name__ = "Validator"
__release_date__ = "2025-01-21"

# Version history
VERSION_HISTORY = {
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

    Returns:
        Formatted banner string
    """
    banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ███╗   ██╗██╗██╗      ██████╗ ██████╗ ██████╗ ███████╗       ║
║   ████╗  ██║██║██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝       ║
║   ██╔██╗ ██║██║██║     ██║     ██║   ██║██║  ██║█████╗         ║
║   ██║╚██╗██║██║██║     ██║     ██║   ██║██║  ██║██╔══╝         ║
║   ██║ ╚████║██║███████╗╚██████╗╚██████╔╝██████╔╝███████╗       ║
║   ╚═╝  ╚═══╝╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝       ║
║                                                                  ║
║              Multi-Agent AI Development System                   ║
║                                                                  ║
║  Version: {__version__} "{__version_name__}"                               ║
║  Released: {__release_date__}                                      ║
║                                                                  ║
║  Features:                                                       ║
║  ✓ Syntax Validation & Error Correction                         ║
║  ✓ Language-Agnostic Code Generation                            ║
║  ✓ Architectural Consistency Enforcement                        ║
║  ✓ Multi-Stage Quality Assurance                                ║
║                                                                  ║
║  Supported Languages: Python, JavaScript, TypeScript, HTML      ║
║  Frameworks: React, Vue, FastAPI, Flask, Django, Express        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    return banner


def get_short_banner() -> str:
    """
    Get a compact version banner.

    Returns:
        Compact banner string
    """
    return f"""
┌──────────────────────────────────────────────────────────────┐
│ NilCode v{__version__} "{__version_name__}" - Multi-Agent Development System │
│ Released: {__release_date__}                                        │
└──────────────────────────────────────────────────────────────┘
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
    """Print detailed version information."""
    info = get_version_info()

    print(f"\n{'='*70}")
    print(f"NilCode Version {info['version']} \"{info['name']}\"")
    print(f"Released: {info['release_date']}")
    print(f"{'='*70}\n")

    if info['history']:
        print(f"Description:")
        print(f"  {info['history'].get('description', 'N/A')}\n")

        if info['history'].get('features'):
            print("Features:")
            for feature in info['history']['features']:
                print(f"  ✓ {feature}")
            print()

        if info['history'].get('breaking_changes'):
            print("Breaking Changes:")
            for change in info['history']['breaking_changes']:
                print(f"  ⚠ {change}")
            print()


def print_changelog(limit: int = None) -> None:
    """
    Print the version changelog.

    Args:
        limit: Maximum number of versions to show. None shows all.
    """
    print("\n" + "="*70)
    print("VERSION CHANGELOG")
    print("="*70 + "\n")

    versions = sorted(VERSION_HISTORY.keys(), reverse=True)
    if limit:
        versions = versions[:limit]

    for version in versions:
        info = VERSION_HISTORY[version]
        print(f"Version {version} \"{info['name']}\" ({info['date']})")
        print(f"{'-'*70}")
        print(f"{info['description']}\n")

        if info.get('features'):
            print("Features:")
            for feature in info['features']:
                print(f"  ✓ {feature}")
            print()

        if info.get('breaking_changes'):
            print("Breaking Changes:")
            for change in info['breaking_changes']:
                print(f"  ⚠ {change}")
            print()

        print()


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
