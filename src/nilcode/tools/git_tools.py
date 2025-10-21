"""
Git integration tools for version control operations.
These tools help agents understand git state and work with version control.
"""

import subprocess
from pathlib import Path
from typing import Optional
from langchain.tools import tool


@tool
def git_status(repo_path: str = ".") -> str:
    """
    Get the current git status of the repository.
    
    Args:
        repo_path: Path to the git repository
    
    Returns:
        Git status output showing modified, staged, and untracked files
    """
    try:
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Directory {repo_path} does not exist"
        
        if not (path / ".git").exists():
            return f"Error: {repo_path} is not a git repository"
        
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"Error getting git status: {result.stderr}"
        
        status = result.stdout.strip()
        if not status:
            return "✅ Working directory clean - no changes"
        
        # Parse status
        modified = []
        staged = []
        untracked = []
        
        for line in status.split('\n'):
            if not line:
                continue
            status_code = line[:2]
            file_path = line[3:]
            
            if status_code.startswith('M') or status_code.endswith('M'):
                modified.append(file_path)
            if status_code.startswith('A') or status_code.startswith('M'):
                staged.append(file_path)
            if status_code.startswith('??'):
                untracked.append(file_path)
        
        output = ["Git Status:", "=" * 50, ""]
        
        if staged:
            output.append("📦 Staged files:")
            for f in staged:
                output.append(f"  • {f}")
            output.append("")
        
        if modified:
            output.append("📝 Modified files:")
            for f in modified:
                output.append(f"  • {f}")
            output.append("")
        
        if untracked:
            output.append("❓ Untracked files:")
            for f in untracked:
                output.append(f"  • {f}")
            output.append("")
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def git_diff(file_path: Optional[str] = None, repo_path: str = ".") -> str:
    """
    Show git diff for changes in the repository.
    
    Args:
        file_path: Optional specific file to diff (if None, shows all changes)
        repo_path: Path to the git repository
    
    Returns:
        Git diff output
    """
    try:
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Directory {repo_path} does not exist"
        
        if not (path / ".git").exists():
            return f"Error: {repo_path} is not a git repository"
        
        cmd = ["git", "diff"]
        if file_path:
            cmd.append(file_path)
        
        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"Error getting git diff: {result.stderr}"
        
        diff = result.stdout.strip()
        if not diff:
            return "No changes to show"
        
        # Limit output size
        lines = diff.split('\n')
        if len(lines) > 100:
            return '\n'.join(lines[:100]) + f"\n\n... (truncated, {len(lines) - 100} more lines)"
        
        return diff
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def git_log(max_count: int = 10, repo_path: str = ".") -> str:
    """
    Show recent git commit history.
    
    Args:
        max_count: Maximum number of commits to show
        repo_path: Path to the git repository
    
    Returns:
        Git log output with recent commits
    """
    try:
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Directory {repo_path} does not exist"
        
        if not (path / ".git").exists():
            return f"Error: {repo_path} is not a git repository"
        
        result = subprocess.run(
            ["git", "log", f"--max-count={max_count}", "--oneline", "--decorate"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"Error getting git log: {result.stderr}"
        
        log = result.stdout.strip()
        if not log:
            return "No commits found"
        
        output = [f"Recent Commits (last {max_count}):", "=" * 50, ""]
        output.append(log)
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def git_branch_info(repo_path: str = ".") -> str:
    """
    Get information about git branches.
    
    Args:
        repo_path: Path to the git repository
    
    Returns:
        Current branch and available branches
    """
    try:
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Directory {repo_path} does not exist"
        
        if not (path / ".git").exists():
            return f"Error: {repo_path} is not a git repository"
        
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error getting branch info: {result.stderr}"
        
        current_branch = result.stdout.strip()
        
        # Get all branches
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error getting branches: {result.stderr}"
        
        branches = result.stdout.strip()
        
        output = [
            "Git Branch Information:",
            "=" * 50,
            "",
            f"🌿 Current Branch: {current_branch}",
            "",
            "Available Branches:",
            branches
        ]
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def git_show_file(file_path: str, commit: str = "HEAD", repo_path: str = ".") -> str:
    """
    Show the contents of a file at a specific commit.
    
    Args:
        file_path: Path to the file in the repository
        commit: Commit reference (default: HEAD)
        repo_path: Path to the git repository
    
    Returns:
        File contents at the specified commit
    """
    try:
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Directory {repo_path} does not exist"
        
        if not (path / ".git").exists():
            return f"Error: {repo_path} is not a git repository"
        
        result = subprocess.run(
            ["git", "show", f"{commit}:{file_path}"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        content = result.stdout
        
        # Limit output size
        lines = content.split('\n')
        if len(lines) > 200:
            return '\n'.join(lines[:200]) + f"\n\n... (truncated, {len(lines) - 200} more lines)"
        
        return f"File: {file_path} at {commit}\n\n{content}"
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def git_file_history(file_path: str, max_count: int = 5, repo_path: str = ".") -> str:
    """
    Show the commit history for a specific file.
    
    Args:
        file_path: Path to the file
        max_count: Maximum number of commits to show
        repo_path: Path to the git repository
    
    Returns:
        Commit history for the file
    """
    try:
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Directory {repo_path} does not exist"
        
        if not (path / ".git").exists():
            return f"Error: {repo_path} is not a git repository"
        
        result = subprocess.run(
            ["git", "log", f"--max-count={max_count}", "--oneline", "--", file_path],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        log = result.stdout.strip()
        if not log:
            return f"No history found for {file_path}"
        
        output = [
            f"History for {file_path}:",
            "=" * 50,
            "",
            log
        ]
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def git_check_conflicts(repo_path: str = ".") -> str:
    """
    Check for merge conflicts in the repository.
    
    Args:
        repo_path: Path to the git repository
    
    Returns:
        List of files with conflicts, if any
    """
    try:
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Directory {repo_path} does not exist"
        
        if not (path / ".git").exists():
            return f"Error: {repo_path} is not a git repository"
        
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return f"Error checking conflicts: {result.stderr}"
        
        conflicts = result.stdout.strip()
        if not conflicts:
            return "✅ No merge conflicts detected"
        
        output = [
            "⚠️  Merge Conflicts Detected:",
            "=" * 50,
            "",
            "Files with conflicts:"
        ]
        
        for file_path in conflicts.split('\n'):
            output.append(f"  • {file_path}")
        
        return '\n'.join(output)
    
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


# Export all tools
git_tools = [
    git_status,
    git_diff,
    git_log,
    git_branch_info,
    git_show_file,
    git_file_history,
    git_check_conflicts,
]

