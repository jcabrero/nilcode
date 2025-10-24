"""
Utility helpers shared across agent implementations.
"""

from typing import Dict, List, Optional


# Execution order helps route work across specialized agents.
AGENT_EXECUTION_ORDER: List[str] = [
    "software_architect",
    "coder",  # Handles all implementation including dependencies, frontend, backend
    "tester",
]

# All internal agents (special agents + execution order agents)
INTERNAL_AGENTS = ["planner", "orchestrator", "error_recovery", "a2a_client"] + AGENT_EXECUTION_ORDER


def determine_next_agent(
    tasks: List[Dict[str, str]],
    prefer_agent: Optional[str] = None,
) -> str:
    """
    Determine which agent should execute next based on task assignments.

    Args:
        tasks: List of task dictionaries with `assignedTo` and `status`.
        prefer_agent: Optional agent name to prioritize when it still has work.

    Returns:
        Name of the next agent to execute. Defaults to `tester` when no pending
        work is found so validation still runs before orchestrator.
    """
    pending_tasks = [
        task for task in tasks
        if task.get("status") in {"pending", "in_progress"}
    ]

    if prefer_agent and any(
        task.get("assignedTo") == prefer_agent for task in pending_tasks
    ):
        return prefer_agent

    # Check for internal agents in execution order FIRST
    # This ensures proper sequential execution (architect -> coder -> tester)
    for agent in AGENT_EXECUTION_ORDER:
        if any(task.get("assignedTo") == agent for task in pending_tasks):
            return agent

    # Then check for external A2A agents
    # External agents are checked after internal agents to maintain workflow order
    for task in pending_tasks:
        assigned_to = task.get("assignedTo", "")
        # If assigned to an agent that's not in our internal agents list, route to a2a_client
        if assigned_to and assigned_to not in INTERNAL_AGENTS:
            # This is an external agent - route to a2a_client
            return "a2a_client"

    # Fall back to tester so the validation stage still runs, even when all
    # implementation tasks are marked completed.
    return "tester"
