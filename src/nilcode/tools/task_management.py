"""
Task management tools for creating and tracking tasks (todo list).
These tools allow agents to manage a structured task list.
"""

import uuid
from typing import List, Dict, Literal, Any
from langchain.tools import tool


# In-memory task storage (in a real system, this would be in the state)
_task_storage: Dict[str, Dict] = {}


@tool
def create_task(
    content: str,
    active_form: str,
    assigned_to: str = "unassigned"
) -> str:
    """
    Create a new task in the todo list.

    Args:
        content: Description of the task (imperative form, e.g., "Fix bug in login")
        active_form: Present continuous form (e.g., "Fixing bug in login")
        assigned_to: Which agent is assigned to this task

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
        "result": ""
    }

    _task_storage[task_id] = task

    return f"Created task {task_id}: {content}"


@tool
def update_task_status(
    task_id: str,
    status: Literal["pending", "in_progress", "completed"]
) -> str:
    """
    Update the status of a task.

    Args:
        task_id: ID of the task to update
        status: New status (pending, in_progress, or completed)

    Returns:
        Confirmation message
    """
    if task_id not in _task_storage:
        return f"Error: Task {task_id} not found"

    _task_storage[task_id]["status"] = status

    return f"Updated task {task_id} to {status}"


@tool
def update_task_result(task_id: str, result: str) -> str:
    """
    Update the result of a completed task.

    Args:
        task_id: ID of the task to update
        result: Result or output from completing the task

    Returns:
        Confirmation message
    """
    if task_id not in _task_storage:
        return f"Error: Task {task_id} not found"

    _task_storage[task_id]["result"] = result

    return f"Updated result for task {task_id}"


@tool
def get_all_tasks() -> str:
    """
    Get all tasks in the todo list.

    Returns:
        Formatted list of all tasks
    """
    if not _task_storage:
        return "No tasks found"

    output = ["Current Tasks:", "=" * 50]

    for task_id, task in _task_storage.items():
        status_emoji = {
            "pending": "⏸️",
            "in_progress": "▶️",
            "completed": "✅"
        }[task["status"]]

        output.append(
            f"{status_emoji} [{task_id}] {task['content']} "
            f"(assigned to: {task['assignedTo']}, status: {task['status']})"
        )

        if task["result"]:
            output.append(f"   Result: {task['result']}")

    return "\n".join(output)


@tool
def get_pending_tasks() -> str:
    """
    Get all pending tasks.

    Returns:
        Formatted list of pending tasks
    """
    pending = [t for t in _task_storage.values() if t["status"] == "pending"]

    if not pending:
        return "No pending tasks"

    output = ["Pending Tasks:"]
    for task in pending:
        output.append(f"- [{task['id']}] {task['content']}")

    return "\n".join(output)


@tool
def clear_all_tasks() -> str:
    """
    Clear all tasks from the todo list.

    Returns:
        Confirmation message
    """
    count = len(_task_storage)
    _task_storage.clear()
    return f"Cleared {count} tasks"


def set_task_storage(tasks: List[Dict[str, Any]]) -> None:
    """
    Synchronize the internal task storage with the shared agent state.

    Args:
        tasks: Task definitions managed in the shared AgentState.
    """
    _task_storage.clear()
    for task in tasks:
        task_id = task.get("id")
        if task_id:
            _task_storage[task_id] = dict(task)


# Export all tools
task_tools = [
    create_task,
    update_task_status,
    update_task_result,
    get_all_tasks,
    get_pending_tasks,
    clear_all_tasks
]
