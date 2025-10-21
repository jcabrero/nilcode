"""
Terminal and command execution tools.
These tools allow agents to run commands, tests, and install packages.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
from langchain.tools import tool


@tool
def run_command(command: str, working_dir: str = ".", timeout: int = 30) -> str:
    """
    Execute a shell command and return its output.
    
    Args:
        command: The command to execute
        working_dir: Directory to run the command in
        timeout: Maximum seconds to wait for command (default: 30)
    
    Returns:
        Command output (stdout and stderr combined)
    """
    try:
        work_path = Path(working_dir)
        if not work_path.exists():
            return f"Error: Directory {working_dir} does not exist"
        
        # Security: Don't allow dangerous commands
        dangerous_patterns = ['rm -rf /', 'mkfs', 'dd if=', ':(){ :|:& };:']
        if any(pattern in command for pattern in dangerous_patterns):
            return f"Error: Command rejected for security reasons"
        
        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(work_path),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = []
        if result.stdout:
            output.append("STDOUT:")
            output.append(result.stdout)
        if result.stderr:
            output.append("STDERR:")
            output.append(result.stderr)
        
        output.append(f"\nExit code: {result.returncode}")
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error running command: {str(e)}"


@tool
def run_python_script(script_path: str, args: str = "", working_dir: str = ".") -> str:
    """
    Run a Python script and return its output.
    
    Args:
        script_path: Path to the Python script
        args: Command-line arguments to pass to the script
        working_dir: Directory to run the script from
    
    Returns:
        Script output and exit status
    """
    try:
        script = Path(script_path)
        if not script.exists():
            return f"Error: Script {script_path} does not exist"
        
        work_path = Path(working_dir)
        if not work_path.exists():
            return f"Error: Directory {working_dir} does not exist"
        
        # Use the same Python interpreter
        python_exe = sys.executable
        command = f"{python_exe} {script_path} {args}".strip()
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(work_path),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = [f"Running: {command}\n"]
        
        if result.stdout:
            output.append("Output:")
            output.append(result.stdout)
        
        if result.stderr:
            output.append("\nErrors:")
            output.append(result.stderr)
        
        if result.returncode == 0:
            output.append("\n✅ Script completed successfully")
        else:
            output.append(f"\n❌ Script failed with exit code {result.returncode}")
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Script timed out after 30 seconds"
    except Exception as e:
        return f"Error running script: {str(e)}"


@tool
def install_package(package_name: str, package_manager: str = "auto") -> str:
    """
    Install a package using the appropriate package manager.
    
    Args:
        package_name: Name of the package to install
        package_manager: Package manager to use (auto, pip, npm, uv)
    
    Returns:
        Installation result
    """
    try:
        if package_manager == "auto":
            # Detect based on project files
            if Path("package.json").exists():
                package_manager = "npm"
            elif Path("pyproject.toml").exists():
                # Check if uv is available
                try:
                    subprocess.run(["uv", "--version"], capture_output=True, check=True)
                    package_manager = "uv"
                except:
                    package_manager = "pip"
            elif Path("requirements.txt").exists():
                package_manager = "pip"
            else:
                return "Error: Could not detect package manager. Please specify explicitly."
        
        commands = {
            "pip": f"pip install {package_name}",
            "npm": f"npm install {package_name}",
            "uv": f"uv add {package_name}",
        }
        
        if package_manager not in commands:
            return f"Error: Unknown package manager '{package_manager}'"
        
        command = commands[package_manager]
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120  # Longer timeout for installations
        )
        
        if result.returncode == 0:
            return f"✅ Successfully installed {package_name} using {package_manager}"
        else:
            return f"❌ Failed to install {package_name}:\n{result.stderr}"
    
    except subprocess.TimeoutExpired:
        return f"Error: Installation timed out after 120 seconds"
    except Exception as e:
        return f"Error installing package: {str(e)}"


@tool
def run_tests(test_path: str = "tests", framework: str = "auto") -> str:
    """
    Run tests using the appropriate testing framework.
    
    Args:
        test_path: Path to tests directory or file
        framework: Testing framework to use (auto, pytest, jest, unittest)
    
    Returns:
        Test results
    """
    try:
        if framework == "auto":
            # Detect based on project
            if Path("package.json").exists():
                framework = "jest"
            elif Path("pytest.ini").exists() or Path("pyproject.toml").exists():
                framework = "pytest"
            else:
                framework = "pytest"  # Default for Python
        
        commands = {
            "pytest": f"pytest {test_path} -v",
            "unittest": f"python -m unittest discover {test_path}",
            "jest": "npm test",
        }
        
        if framework not in commands:
            return f"Error: Unknown test framework '{framework}'"
        
        command = commands[framework]
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = [f"Running tests with {framework}:\n"]
        
        if result.stdout:
            output.append(result.stdout)
        
        if result.stderr:
            output.append("\nErrors:")
            output.append(result.stderr)
        
        if result.returncode == 0:
            output.append("\n✅ All tests passed")
        else:
            output.append(f"\n❌ Tests failed with exit code {result.returncode}")
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Tests timed out after 60 seconds"
    except Exception as e:
        return f"Error running tests: {str(e)}"


@tool
def run_linter(file_path: str = ".", linter: str = "auto") -> str:
    """
    Run a linter on code files.
    
    Args:
        file_path: File or directory to lint
        linter: Linter to use (auto, pylint, flake8, eslint)
    
    Returns:
        Linter output with issues found
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: Path {file_path} does not exist"
        
        if linter == "auto":
            # Detect based on file type
            if path.is_file():
                if path.suffix == ".py":
                    linter = "flake8"
                elif path.suffix in [".js", ".jsx", ".ts", ".tsx"]:
                    linter = "eslint"
                else:
                    return "Error: Could not detect linter for file type"
            else:
                # Check for Python or JS files
                if any(path.rglob("*.py")):
                    linter = "flake8"
                elif any(path.rglob("*.js")):
                    linter = "eslint"
                else:
                    return "Error: Could not detect code type"
        
        commands = {
            "pylint": f"pylint {file_path}",
            "flake8": f"flake8 {file_path} --max-line-length=120",
            "eslint": f"eslint {file_path}",
        }
        
        if linter not in commands:
            return f"Error: Unknown linter '{linter}'"
        
        command = commands[linter]
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = [f"Linting with {linter}:\n"]
        
        if result.stdout:
            output.append(result.stdout)
        
        if result.stderr:
            output.append("\nWarnings/Errors:")
            output.append(result.stderr)
        
        if result.returncode == 0:
            output.append("\n✅ No linting issues found")
        else:
            output.append(f"\n⚠️  Linting found issues (exit code {result.returncode})")
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Linter timed out after 30 seconds"
    except Exception as e:
        return f"Error running linter: {str(e)}"


@tool
def check_environment() -> str:
    """
    Check the current development environment and available tools.
    
    Returns:
        Information about Python version, installed tools, and system info
    """
    try:
        output = ["Development Environment Check", "=" * 50, ""]
        
        # Python info
        output.append(f"🐍 Python: {sys.version.split()[0]}")
        output.append(f"   Location: {sys.executable}")
        output.append("")
        
        # Check for common tools
        tools = {
            "git": "git --version",
            "node": "node --version",
            "npm": "npm --version",
            "pytest": "pytest --version",
            "pip": "pip --version",
            "uv": "uv --version",
        }
        
        output.append("🛠️  Available Tools:")
        for tool_name, check_cmd in tools.items():
            try:
                result = subprocess.run(
                    check_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    output.append(f"  ✅ {tool_name}: {version}")
                else:
                    output.append(f"  ❌ {tool_name}: Not available")
            except:
                output.append(f"  ❌ {tool_name}: Not available")
        
        output.append("")
        output.append(f"📁 Working Directory: {os.getcwd()}")
        
        return '\n'.join(output)
    
    except Exception as e:
        return f"Error checking environment: {str(e)}"


# Export all tools
terminal_tools = [
    run_command,
    run_python_script,
    install_package,
    run_tests,
    run_linter,
    check_environment,
]

