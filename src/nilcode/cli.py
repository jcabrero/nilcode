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
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print the NilCode banner with version information."""
    banner = get_banner()
    print(f"{Colors.OKCYAN}{banner}{Colors.ENDC}")


def print_section(title: str, symbol: str = "="):
    """Print a section separator."""
    width = 70
    print(f"\n{Colors.BOLD}{symbol * width}{Colors.ENDC}")
    print(f"{Colors.BOLD}{title.center(width)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{symbol * width}{Colors.ENDC}\n")


def print_agent_status(agent_name: str, status: str = "running"):
    """Print agent status with formatting."""
    status_icons = {
        "running": "▶️",
        "completed": "✅",
        "failed": "❌",
        "waiting": "⏸️"
    }
    
    icon = status_icons.get(status, "❓")
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    agent_display = {
        "preplanner": "PrePlanner",
        "planner": "Planner",
        "software_architect": "Software Architect",
        "coder": "Coder",
        "tester": "Tester & Validator",
        "error_recovery": "Error Recovery",
        "orchestrator": "Orchestrator",
        "onchain_detective": "Onchain Detective",
    }
    
    display_name = agent_display.get(agent_name, agent_name.replace("_", " ").title())
    
    color = Colors.OKGREEN if status == "completed" else Colors.OKBLUE
    print(f"{color}[{timestamp}] {icon} {display_name}: {status.upper()}{Colors.ENDC}")


def print_progress(current: int, total: int, task_name: str = ""):
    """Print a progress bar."""
    bar_length = 40
    progress = current / total if total > 0 else 0
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    percent = int(progress * 100)
    
    task_display = f" - {task_name}" if task_name else ""
    print(f"\r{Colors.OKCYAN}Progress: [{bar}] {percent}%{task_display}{Colors.ENDC}", end="", flush=True)
    
    if current >= total:
        print()  # New line when complete


def print_task_list(tasks: list):
    """Print a formatted task list."""
    if not tasks:
        print(f"{Colors.WARNING}No tasks to display{Colors.ENDC}")
        return
    
    print(f"\n{Colors.BOLD}Task List:{Colors.ENDC}")
    print(f"{Colors.BOLD}{'─' * 70}{Colors.ENDC}")
    
    status_colors = {
        "pending": Colors.WARNING,
        "in_progress": Colors.OKBLUE,
        "completed": Colors.OKGREEN
    }
    
    status_icons = {
        "pending": "⏸️",
        "in_progress": "▶️",
        "completed": "✅"
    }
    
    for i, task in enumerate(tasks, 1):
        status = task.get("status", "pending")
        content = task.get("content", "Unknown task")
        assigned_to = task.get("assignedTo", "unassigned")
        
        color = status_colors.get(status, Colors.ENDC)
        icon = status_icons.get(status, "❓")
        
        print(f"{color}{icon} [{i}/{len(tasks)}] {content}{Colors.ENDC}")
        print(f"   {Colors.OKCYAN}Assigned to: {assigned_to} | Status: {status}{Colors.ENDC}")
        
        if task.get("result") and status == "completed":
            result = task["result"][:100] + "..." if len(task["result"]) > 100 else task["result"]
            print(f"   {Colors.OKGREEN}Result: {result}{Colors.ENDC}")
    
    print(f"{Colors.BOLD}{'─' * 70}{Colors.ENDC}\n")


def print_files_modified(files: list):
    """Print list of modified files."""
    if not files:
        return
    
    print(f"\n{Colors.BOLD}Modified Files:{Colors.ENDC}")
    for file_path in files:
        print(f"  {Colors.OKGREEN}📝 {file_path}{Colors.ENDC}")


def print_summary(state: dict):
    """Print final summary of the execution."""
    print_section("EXECUTION SUMMARY", "═")
    
    status = state.get("overall_status", "unknown")
    
    if status == "completed":
        print(f"{Colors.OKGREEN}✅ Status: COMPLETED{Colors.ENDC}")
    elif status == "failed":
        print(f"{Colors.FAIL}❌ Status: FAILED{Colors.ENDC}")
        if state.get("error"):
            print(f"{Colors.FAIL}Error: {state['error']}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️  Status: {status.upper()}{Colors.ENDC}")
    
    # Show plan if available
    if state.get("plan"):
        print(f"\n{Colors.BOLD}Plan:{Colors.ENDC}")
        print(f"{state['plan']}")
    
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
        print(f"\n{Colors.BOLD}Context Analysis:{Colors.ENDC}")
        summary = state["context_summary"]
        print(f"{summary[:500]}..." if len(summary) > 500 else summary)
    
    # Show test results
    if state.get("test_results"):
        print(f"\n{Colors.BOLD}Test Results:{Colors.ENDC}")
        test_results = state["test_results"]
        if test_results.get("passed"):
            print(f"{Colors.OKGREEN}✅ Passed: {test_results['passed']}{Colors.ENDC}")
        if test_results.get("failed"):
            print(f"{Colors.FAIL}❌ Failed: {test_results['failed']}{Colors.ENDC}")


def get_user_input(prompt: str = "What would you like to build?") -> str:
    """Get user input with formatting."""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{prompt}{Colors.ENDC}")
    print(f"{Colors.BOLD}> {Colors.ENDC}", end="")
    return input().strip()


def confirm_action(question: str) -> bool:
    """Ask for user confirmation."""
    print(f"\n{Colors.WARNING}{question} (y/n): {Colors.ENDC}", end="")
    response = input().strip().lower()
    return response in ['y', 'yes']


def print_error(message: str):
    """Print an error message."""
    print(f"\n{Colors.FAIL}❌ ERROR: {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠️  WARNING: {message}{Colors.ENDC}")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


def print_streaming_update(agent_name: str, content: str):
    """Print a streaming update from an agent."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{Colors.OKCYAN}[{timestamp}] {agent_name}:{Colors.ENDC}")
    print(f"  {content[:200]}..." if len(content) > 200 else f"  {content}")


def interactive_mode(agent_system):
    """Run the CLI in interactive mode."""
    print_banner()
    
    print_info("Interactive Mode - Type 'help' for commands")
    print_info("Type 'exit' or 'quit' to end the session")
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
                print(f"\n{Colors.BOLD}Available Commands:{Colors.ENDC}")
                for cmd, desc in commands.items():
                    print(f"  {Colors.OKCYAN}{cmd:<10}{Colors.ENDC} - {desc}")
                continue
            
            if user_input.lower() == 'status':
                print_info("System ready and waiting for tasks")
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
            print_section(f"Processing: {user_input[:50]}...", "─")
            
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
            print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
            if confirm_action("Do you want to exit?"):
                print_success("Goodbye!")
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
        print_section(f"Executing: {command}", "─")
    
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
