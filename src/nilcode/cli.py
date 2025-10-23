"""
Enhanced CLI interface for NilCode with streaming and better UX.
"""

import os
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path

# Import version information
try:
    from .version import get_banner, get_version, get_version_info
except ImportError:
    from version import get_banner, get_version, get_version_info


class Colors:
    """ANSI color codes for terminal output - Claude Code inspired."""
    # Primary Claude colors
    PURPLE = '\033[38;5;141m'      # Claude's signature purple
    BLUE = '\033[38;5;111m'        # Soft blue
    LIGHT_PURPLE = '\033[38;5;183m' # Light purple for highlights
    
    # Status colors
    SUCCESS = '\033[38;5;114m'     # Soft green
    ERROR = '\033[38;5;203m'       # Soft red
    WARNING = '\033[38;5;222m'     # Soft yellow
    INFO = '\033[38;5;117m'        # Soft cyan
    
    # Text formatting
    GRAY = '\033[38;5;245m'        # Subtle gray for secondary text
    DIM = '\033[2m'                # Dimmed text
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    
    # Legacy aliases for compatibility
    HEADER = '\033[38;5;141m'
    OKBLUE = '\033[38;5;111m'
    OKCYAN = '\033[38;5;117m'
    OKGREEN = '\033[38;5;114m'
    FAIL = '\033[38;5;203m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print the NilCode banner with version information."""
    banner = get_banner()
    print(banner)


def print_section(title: str, symbol: str = "─"):
    """Print a section separator with Claude Code styling."""
    print(f"\n{Colors.PURPLE}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.GRAY}{symbol * 70}{Colors.ENDC}\n")


def print_agent_status(agent_name: str, status: str = "running"):
    """Print agent status with Claude Code styling."""
    status_symbols = {
        "running": "→",
        "completed": "✓",
        "failed": "✗",
        "waiting": "·"
    }
    
    symbol = status_symbols.get(status, "·")
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    agent_display = {
        "planner": "Planner",
        "software_architect": "Software Architect",
        "coder": "Coder",
        "tester": "Tester & Validator",
        "error_recovery": "Error Recovery",
        "orchestrator": "Orchestrator",
        "a2a_client": "External Agent"
    }
    
    display_name = agent_display.get(agent_name, agent_name.replace("_", " ").title())
    
    if status == "completed":
        color = Colors.SUCCESS
    elif status == "failed":
        color = Colors.ERROR
    else:
        color = Colors.PURPLE
    
    print(f"{Colors.GRAY}{timestamp}{Colors.ENDC} {color}{symbol} {display_name}{Colors.ENDC} {Colors.DIM}{status}{Colors.ENDC}")


def print_progress(current: int, total: int, task_name: str = ""):
    """Print a progress bar with Claude Code styling."""
    bar_length = 40
    progress = current / total if total > 0 else 0
    filled = int(bar_length * progress)
    bar = "━" * filled + "─" * (bar_length - filled)
    percent = int(progress * 100)
    
    task_display = f" {task_name}" if task_name else ""
    print(f"\r{Colors.PURPLE}[{bar}]{Colors.ENDC} {Colors.BOLD}{percent}%{Colors.ENDC}{Colors.GRAY}{task_display}{Colors.ENDC}", end="", flush=True)
    
    if current >= total:
        print()  # New line when complete


def print_task_list(tasks: list):
    """Print a formatted task list with Claude Code styling."""
    if not tasks:
        print(f"{Colors.GRAY}No tasks to display{Colors.ENDC}")
        return
    
    print(f"\n{Colors.PURPLE}{Colors.BOLD}Tasks{Colors.ENDC}")
    print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
    
    status_colors = {
        "pending": Colors.GRAY,
        "in_progress": Colors.PURPLE,
        "completed": Colors.SUCCESS
    }
    
    status_symbols = {
        "pending": "○",
        "in_progress": "◐",
        "completed": "●"
    }
    
    for i, task in enumerate(tasks, 1):
        status = task.get("status", "pending")
        content = task.get("content", "Unknown task")
        assigned_to = task.get("assignedTo", "unassigned")
        
        color = status_colors.get(status, Colors.ENDC)
        symbol = status_symbols.get(status, "○")
        
        print(f"{color}{symbol} {content}{Colors.ENDC}")
        print(f"   {Colors.GRAY}{assigned_to} · {status}{Colors.ENDC}")
        
        if task.get("result") and status == "completed":
            result = task["result"][:100] + "..." if len(task["result"]) > 100 else task["result"]
            print(f"   {Colors.DIM}{result}{Colors.ENDC}")
        print()
    
    print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}\n")


def print_files_modified(files: list):
    """Print list of modified files with Claude Code styling."""
    if not files:
        return
    
    print(f"\n{Colors.PURPLE}{Colors.BOLD}Files Modified{Colors.ENDC}")
    print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
    for file_path in files:
        print(f"  {Colors.SUCCESS}+ {file_path}{Colors.ENDC}")


def print_summary(state: dict):
    """Print final summary of the execution with Claude Code styling."""
    print_section("Summary")
    
    status = state.get("overall_status", "unknown")
    
    if status == "completed":
        print(f"{Colors.SUCCESS}✓ Completed successfully{Colors.ENDC}\n")
    elif status == "failed":
        print(f"{Colors.ERROR}✗ Failed{Colors.ENDC}")
        if state.get("error"):
            print(f"{Colors.GRAY}{state['error']}{Colors.ENDC}\n")
    else:
        print(f"{Colors.WARNING}· Status: {status}{Colors.ENDC}\n")
    
    # Show plan if available
    if state.get("plan"):
        print(f"{Colors.PURPLE}{Colors.BOLD}Plan{Colors.ENDC}")
        print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
        print(f"{state['plan']}\n")
    
    # Show tasks
    tasks = state.get("tasks", [])
    if tasks:
        print_task_list(tasks)
    
    # Show modified files
    modified_files = state.get("modified_files", [])
    if modified_files:
        print_files_modified(modified_files)
    
    # Show context if gathered
    if state.get("context_summary"):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}Context Analysis{Colors.ENDC}")
        print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
        summary = state["context_summary"]
        print(f"{Colors.DIM}{summary[:500]}...{Colors.ENDC}" if len(summary) > 500 else f"{Colors.DIM}{summary}{Colors.ENDC}\n")
    
    # Show test results
    if state.get("test_results"):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}Test Results{Colors.ENDC}")
        print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
        test_results = state["test_results"]
        if test_results.get("passed"):
            print(f"{Colors.SUCCESS}✓ Passed: {test_results['passed']}{Colors.ENDC}")
        if test_results.get("failed"):
            print(f"{Colors.ERROR}✗ Failed: {test_results['failed']}{Colors.ENDC}")


def get_user_input(prompt: str = "What would you like to build?") -> str:
    """Get user input with Claude Code styling."""
    print(f"\n{Colors.PURPLE}{prompt}{Colors.ENDC}")
    print(f"{Colors.PURPLE}› {Colors.ENDC}", end="")
    return input().strip()


def confirm_action(question: str) -> bool:
    """Ask for user confirmation."""
    print(f"\n{Colors.WARNING}{question} {Colors.GRAY}(y/n){Colors.ENDC} ", end="")
    response = input().strip().lower()
    return response in ['y', 'yes']


def print_error(message: str):
    """Print an error message with Claude Code styling."""
    print(f"{Colors.ERROR}✗ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message with Claude Code styling."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_success(message: str):
    """Print a success message with Claude Code styling."""
    print(f"{Colors.SUCCESS}✓ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message with Claude Code styling."""
    print(f"{Colors.INFO}{message}{Colors.ENDC}")


def print_streaming_update(agent_name: str, content: str):
    """Print a streaming update from an agent with Claude Code styling."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{Colors.GRAY}{timestamp}{Colors.ENDC} {Colors.PURPLE}{agent_name}{Colors.ENDC}")
    print(f"{Colors.DIM}{content[:200]}...{Colors.ENDC}" if len(content) > 200 else f"{Colors.DIM}{content}{Colors.ENDC}")


def interactive_mode(agent_system):
    """Run the CLI in interactive mode."""
    print_banner()
    
    print(f"{Colors.GRAY}Type 'help' for commands, 'exit' to quit{Colors.ENDC}")
    print()
    
    commands = {
        "help": "Show available commands",
        "version": "Show version information",
        "changelog": "Show version changelog",
        "exit": "Exit the program",
        "quit": "Exit the program",
        "clear": "Clear the screen",
        "status": "Show current system status",
    }
    
    while True:
        try:
            user_input = get_user_input()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                print_success("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()
                continue
            
            if user_input.lower() == 'help':
                print(f"\n{Colors.PURPLE}{Colors.BOLD}Available Commands{Colors.ENDC}")
                print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
                for cmd, desc in commands.items():
                    print(f"  {Colors.PURPLE}{cmd:<12}{Colors.ENDC} {Colors.GRAY}{desc}{Colors.ENDC}")
                print()
                continue
            
            if user_input.lower() == 'status':
                print(f"{Colors.SUCCESS}System ready{Colors.ENDC}")
                continue

            if user_input.lower() == 'version':
                from .version import print_version_info
                print_version_info()
                continue

            if user_input.lower() == 'changelog':
                from .version import print_changelog
                print_changelog(limit=3)
                continue

            # Execute the request
            print(f"\n{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
            print(f"{Colors.PURPLE}Processing{Colors.ENDC} {Colors.DIM}{user_input[:60]}...{Colors.ENDC}" if len(user_input) > 60 else f"{Colors.PURPLE}Processing{Colors.ENDC} {Colors.DIM}{user_input}{Colors.ENDC}")
            print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}\n")
            
            try:
                # Run with streaming
                task_count = 0
                for state_update in agent_system.stream(user_input):
                    # Extract agent name from update
                    if state_update and len(state_update.keys()) > 0:
                        agent_name = list(state_update.keys())[0]
                        print_agent_status(agent_name, "completed")
                        task_count += 1
                
                # Get final state
                print()
                print_success("Task completed successfully!")
                
            except Exception as e:
                print_error(f"Execution failed: {str(e)}")
                import traceback
                if os.getenv("DEBUG"):
                    traceback.print_exc()
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GRAY}Interrupted{Colors.ENDC}")
            if confirm_action("Exit?"):
                print(f"\n{Colors.GRAY}Goodbye{Colors.ENDC}")
                break
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            if os.getenv("DEBUG"):
                import traceback
                traceback.print_exc()


def run_single_command(agent_system, command: str, verbose: bool = True):
    """Run a single command and exit."""
    if verbose:
        print_banner()
        print(f"\n{Colors.GRAY}{'─' * 70}{Colors.ENDC}")
        print(f"{Colors.PURPLE}Executing{Colors.ENDC} {Colors.DIM}{command}{Colors.ENDC}")
        print(f"{Colors.GRAY}{'─' * 70}{Colors.ENDC}\n")
    
    try:
        final_state = agent_system.run(command)
        
        if verbose:
            print_summary(final_state)
        
        # Return exit code based on status
        status = final_state.get("overall_status", "unknown")
        return 0 if status == "completed" else 1
    
    except Exception as e:
        print_error(f"Execution failed: {str(e)} ")
        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()
        return 1

