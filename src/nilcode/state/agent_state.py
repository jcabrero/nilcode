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
    working_directory: str  # Current working directory for the project

    # Codebase understanding
    codebase_context: Dict[str, Any]  # Context gathered about existing code
    relevant_files: List[str]  # Files identified as relevant to current task

    # Code context
    frontend_tech: List[str]  # e.g., ["react", "typescript"]
    backend_tech: List[str]   # e.g., ["python", "fastapi"]

    # Agent routing
    next_agent: str  # Which agent should execute next

    # Results and outputs
    plan: str  # The plan created by planner
    implementation_results: Dict[str, Any]  # Results from developer agents
    test_results: Dict[str, Any]  # Results from tester
    context_summary: str  # Summary of gathered codebase context

    # Execution tracking
    command_history: List[Dict[str, Any]]  # History of commands executed
    test_execution_results: List[Dict[str, Any]]  # Results from test runs
    linter_results: Dict[str, Any]  # Linting results

    # Status tracking
    overall_status: Literal["planning", "gathering_context", "architecting", "implementing", "testing", "completed", "failed"]
    error: str  # Any errors encountered
    iteration_count: int  # Track iterations for error recovery


def create_initial_state(user_request: str, working_directory: str = ".") -> AgentState:
    """
    Create the initial state for a new agent workflow.

    Args:
        user_request: The user's request/query
        working_directory: Working directory for the project

    Returns:
        Initial AgentState
    """
    import os
    return AgentState(
        messages=[],
        user_request=user_request,
        tasks=[],
        current_task_id="",
        project_files={},
        modified_files=[],
        working_directory=os.path.abspath(working_directory),
        codebase_context={},
        relevant_files=[],
        frontend_tech=[],
        backend_tech=[],
        next_agent="planner",
        plan="",
        implementation_results={},
        test_results={},
        context_summary="",
        command_history=[],
        test_execution_results=[],
        linter_results={},
        overall_status="planning",
        error="",
        iteration_count=0
    )
