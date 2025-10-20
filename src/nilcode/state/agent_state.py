"""
Shared state management for the multi-agent system using LangGraph.
This module defines the state structure that all agents will share.
"""

from typing import TypedDict, List, Dict, Any, Annotated, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class Task(TypedDict):
    """Represents a single task in the todo list."""
    id: str
    content: str
    status: Literal["pending", "in_progress", "completed"]
    activeForm: str
    assignedTo: str  # Which agent is handling this task
    result: str  # Result or output from completing the task


class AgentState(TypedDict):
    """
    Shared state between all agents in the system.

    This state is passed between agents and updated as they work.
    """
    # Conversation messages
    messages: Annotated[List[BaseMessage], add_messages]

    # User's original request
    user_request: str

    # Task management
    tasks: List[Task]
    current_task_id: str

    # Project context
    project_files: Dict[str, str]  # file_path -> content
    modified_files: List[str]  # Track which files were modified

    # Code context
    frontend_tech: List[str]  # e.g., ["react", "typescript"]
    backend_tech: List[str]   # e.g., ["python", "fastapi"]

    # Agent routing
    next_agent: str  # Which agent should execute next

    # Results and outputs
    plan: str  # The plan created by planner
    implementation_results: Dict[str, Any]  # Results from developer agents
    test_results: Dict[str, Any]  # Results from tester

    # Status tracking
    overall_status: Literal["planning", "architecting", "implementing", "testing", "completed", "failed"]
    error: str  # Any errors encountered


def create_initial_state(user_request: str) -> AgentState:
    """
    Create the initial state for a new agent workflow.

    Args:
        user_request: The user's request/query

    Returns:
        Initial AgentState
    """
    return AgentState(
        messages=[],
        user_request=user_request,
        tasks=[],
        current_task_id="",
        project_files={},
        modified_files=[],
        frontend_tech=[],
        backend_tech=[],
        next_agent="planner",
        plan="",
        implementation_results={},
        test_results={},
        overall_status="planning",
        error=""
    )
