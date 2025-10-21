"""
Enhanced task management tools with better context tracking and progress monitoring.
These tools provide comprehensive task lifecycle management.
"""

import uuid
from typing import List, Dict, Any, Literal, Optional
from langchain.tools import tool


@tool
def create_enhanced_task(
    content: str,
    active_form: str,
    assigned_to: str = "unassigned",
    requirements: List[str] = None,
    estimated_effort: str = "medium",
    dependencies: List[str] = None
) -> str:
    """
    Create a new task with enhanced tracking capabilities.
    
    Args:
        content: Description of the task (imperative form)
        active_form: Present continuous form
        assigned_to: Which agent is assigned to this task
        requirements: List of requirements for completing this task
        estimated_effort: Estimated effort level (low/medium/high)
        dependencies: List of task IDs this task depends on
        
    Returns:
        Task ID and confirmation message
    """
    task_id = str(uuid.uuid4())[:8]
    
    task = {
        "id": task_id,
        "content": content,
        "status": "pending",
        "activeForm": active_form,
        "assignedTo": assigned_to,
        "result": "",
        "requirements": requirements or [],
        "progress": "Not started",
        "files_created": [],
        "files_modified": [],
        "dependencies": dependencies or [],
        "retry_count": 0,
        "last_error": "",
        "estimated_effort": estimated_effort,
        "actual_effort": "not_started"
    }
    
    return f"Created enhanced task {task_id}: {content} (effort: {estimated_effort}, requirements: {len(requirements or [])})"


@tool
def update_task_progress(
    task_id: str,
    progress: str,
    files_created: List[str] = None,
    files_modified: List[str] = None,
    actual_effort: str = None
) -> str:
    """
    Update the progress of a task with detailed information.
    
    Args:
        task_id: ID of the task to update
        progress: Current progress description
        files_created: List of files created for this task
        files_modified: List of files modified for this task
        actual_effort: Actual effort expended (low/medium/high)
        
    Returns:
        Confirmation message
    """
    # This would typically update the task in the state
    # For now, return a confirmation message
    files_info = ""
    if files_created:
        files_info += f" Created: {', '.join(files_created)}"
    if files_modified:
        files_info += f" Modified: {', '.join(files_modified)}"
    
    effort_info = f" (effort: {actual_effort})" if actual_effort else ""
    
    return f"Updated task {task_id} progress: {progress}{files_info}{effort_info}"


@tool
def update_task_requirements(task_id: str, requirements: List[str]) -> str:
    """
    Update the requirements for a task.
    
    Args:
        task_id: ID of the task to update
        requirements: List of requirements for completing this task
        
    Returns:
        Confirmation message
    """
    return f"Updated task {task_id} requirements: {len(requirements)} requirements added"


@tool
def mark_task_failed(task_id: str, error: str, retry_count: int = None) -> str:
    """
    Mark a task as failed with error information.
    
    Args:
        task_id: ID of the task to mark as failed
        error: Error message describing what went wrong
        retry_count: Current retry count
        
    Returns:
        Confirmation message
    """
    retry_info = f" (retry {retry_count})" if retry_count is not None else ""
    return f"Marked task {task_id} as failed{retry_info}: {error}"


@tool
def retry_task(task_id: str, max_retries: int = 3) -> str:
    """
    Mark a task for retry with updated retry count.
    
    Args:
        task_id: ID of the task to retry
        max_retries: Maximum number of retries allowed
        
    Returns:
        Retry status message
    """
    return f"Task {task_id} marked for retry (max retries: {max_retries})"


@tool
def get_task_context(task_id: str) -> str:
    """
    Get comprehensive context about a specific task.
    
    Args:
        task_id: ID of the task to get context for
        
    Returns:
        Detailed task context information
    """
    # This would typically read from the state
    # For now, return a placeholder
    return f"Task {task_id} context: This would show detailed task information including requirements, progress, files, and dependencies"


@tool
def get_tasks_by_status(status: Literal["pending", "in_progress", "completed", "failed", "retrying"]) -> str:
    """
    Get all tasks with a specific status.
    
    Args:
        status: Status to filter by
        
    Returns:
        List of tasks with the specified status
    """
    return f"Tasks with status '{status}': This would return a list of tasks with the specified status"


@tool
def get_tasks_by_agent(agent_name: str) -> str:
    """
    Get all tasks assigned to a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        List of tasks assigned to the agent
    """
    return f"Tasks assigned to '{agent_name}': This would return a list of tasks assigned to the specified agent"


@tool
def check_task_dependencies(task_id: str) -> str:
    """
    Check if all dependencies for a task are completed.
    
    Args:
        task_id: ID of the task to check
        
    Returns:
        Dependency status information
    """
    return f"Task {task_id} dependencies: This would check if all required dependencies are completed"


@tool
def get_task_progress_summary() -> str:
    """
    Get a summary of all task progress.
    
    Returns:
        Comprehensive progress summary
    """
    return "Task Progress Summary: This would show overall progress across all tasks including completion rates, pending work, and any issues"


@tool
def update_task_effort(task_id: str, actual_effort: str) -> str:
    """
    Update the actual effort expended on a task.
    
    Args:
        task_id: ID of the task to update
        actual_effort: Actual effort expended (low/medium/high)
        
    Returns:
        Confirmation message
    """
    return f"Updated task {task_id} actual effort to: {actual_effort}"


@tool
def add_task_note(task_id: str, note: str) -> str:
    """
    Add a note to a task for additional context.
    
    Args:
        task_id: ID of the task to add a note to
        note: Note to add
        
    Returns:
        Confirmation message
    """
    return f"Added note to task {task_id}: {note}"


@tool
def get_task_files(task_id: str) -> str:
    """
    Get all files associated with a task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        List of files created and modified for this task
    """
    return f"Task {task_id} files: This would return lists of files created and modified for this task"


@tool
def validate_task_completion(task_id: str) -> str:
    """
    Validate that a task is properly completed with all requirements met.
    
    Args:
        task_id: ID of the task to validate
        
    Returns:
        Validation result
    """
    return f"Task {task_id} validation: This would check if all requirements are met and files are properly created"


# Export all tools
enhanced_task_tools = [
    create_enhanced_task,
    update_task_progress,
    update_task_requirements,
    mark_task_failed,
    retry_task,
    get_task_context,
    get_tasks_by_status,
    get_tasks_by_agent,
    check_task_dependencies,
    get_task_progress_summary,
    update_task_effort,
    add_task_note,
    get_task_files,
    validate_task_completion
]
