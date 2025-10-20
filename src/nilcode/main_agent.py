"""
Main Multi-Agent System Entry Point

This module sets up the LangGraph workflow with all specialized agents
and provides the main interface for the multi-agent system.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from langgraph.graph import StateGraph, END

# Handle both direct script execution and module imports
if __name__ == "__main__" and __package__ is None:
    # Add parent directory to path when running as script
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from .state.agent_state import AgentState, create_initial_state
    from .agents.orchestrator import create_orchestrator_agent
    from .agents.planner import create_planner_agent
    from .agents.software_architect import create_software_architect_agent
    from .agents.frontend_developer import create_frontend_developer_agent
    from .agents.backend_developer import create_backend_developer_agent
    from .agents.tester import create_tester_agent
else:
    from .state.agent_state import AgentState, create_initial_state
    from .agents.orchestrator import create_orchestrator_agent
    from .agents.planner import create_planner_agent
    from .agents.software_architect import create_software_architect_agent
    from .agents.frontend_developer import create_frontend_developer_agent
    from .agents.backend_developer import create_backend_developer_agent
    from .agents.tester import create_tester_agent


class MultiAgentSystem:
    """
    Main multi-agent system that coordinates all specialized agents.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the multi-agent system.

        Args:
            api_key: API key for the LLM provider
            base_url: Optional base URL for the API endpoint
        """
        self.api_key = api_key
        self.base_url = base_url

        # Create all agents
        self.orchestrator = create_orchestrator_agent(api_key, base_url)
        self.planner = create_planner_agent(api_key, base_url)
        self.software_architect = create_software_architect_agent(api_key, base_url)
        self.frontend_developer = create_frontend_developer_agent(api_key, base_url)
        self.backend_developer = create_backend_developer_agent(api_key, base_url)
        self.tester = create_tester_agent(api_key, base_url)

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow with all agents.

        Returns:
            Compiled workflow graph
        """
        # Create the state graph
        workflow = StateGraph(AgentState)

        # Add all agent nodes
        workflow.add_node("orchestrator", self.orchestrator)
        workflow.add_node("planner", self.planner)
        workflow.add_node("software_architect", self.software_architect)
        workflow.add_node("frontend_developer", self.frontend_developer)
        workflow.add_node("backend_developer", self.backend_developer)
        workflow.add_node("tester", self.tester)

        # Define the routing logic
        def route_next(state: AgentState) -> str:
            """Determine which agent should execute next."""
            next_agent = state.get("next_agent", "end")

            if next_agent == "end":
                return "end"

            return next_agent or "end"

        # Set entry point
        workflow.set_entry_point("planner")

        # Add conditional edges from each agent
        workflow.add_conditional_edges(
            "planner",
            route_next,
            {
                "software_architect": "software_architect",
                "frontend_developer": "frontend_developer",
                "backend_developer": "backend_developer",
                "tester": "tester",
                "orchestrator": "orchestrator",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "software_architect",
            route_next,
            {
                "software_architect": "software_architect",
                "frontend_developer": "frontend_developer",
                "backend_developer": "backend_developer",
                "tester": "tester",
                "orchestrator": "orchestrator",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "frontend_developer",
            route_next,
            {
                "software_architect": "software_architect",
                "frontend_developer": "frontend_developer",
                "backend_developer": "backend_developer",
                "tester": "tester",
                "orchestrator": "orchestrator",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "backend_developer",
            route_next,
            {
                "software_architect": "software_architect",
                "frontend_developer": "frontend_developer",
                "backend_developer": "backend_developer",
                "tester": "tester",
                "orchestrator": "orchestrator",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "tester",
            route_next,
            {
                "software_architect": "software_architect",
                "frontend_developer": "frontend_developer",
                "backend_developer": "backend_developer",
                "tester": "tester",
                "orchestrator": "orchestrator",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "orchestrator",
            route_next,
            {
                "software_architect": "software_architect",
                "planner": "planner",
                "frontend_developer": "frontend_developer",
                "backend_developer": "backend_developer",
                "tester": "tester",
                "orchestrator": "orchestrator",
                "end": END
            }
        )

        # Compile the workflow
        return workflow.compile()

    def run(self, user_request: str) -> AgentState:
        """
        Run the multi-agent system on a user request.

        Args:
            user_request: The user's request/query

        Returns:
            Final state after all agents have executed
        """
        print("\n" + "=" * 70)
        print("MULTI-AGENT SYSTEM STARTED")
        print("=" * 70)
        print(f"User Request: {user_request}")
        print("=" * 70 + "\n")

        # Create initial state
        initial_state = create_initial_state(user_request)

        # Run the workflow
        final_state = self.workflow.invoke(initial_state)

        return final_state

    def stream(self, user_request: str):
        """
        Stream the execution of the multi-agent system.

        Args:
            user_request: The user's request/query

        Yields:
            State updates as agents execute
        """
        print("\n" + "=" * 70)
        print("MULTI-AGENT SYSTEM STARTED (STREAMING)")
        print("=" * 70)
        print(f"User Request: {user_request}")
        print("=" * 70 + "\n")

        # Create initial state
        initial_state = create_initial_state(user_request)

        # Stream the workflow execution
        for state_update in self.workflow.stream(initial_state):
            yield state_update


def create_agent_system(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
) -> MultiAgentSystem:
    """
    Factory function to create a multi-agent system.

    Args:
        api_key: API key for the LLM provider (reads from env if not provided)
        base_url: Optional base URL for the API endpoint

    Returns:
        Configured MultiAgentSystem

    Raises:
        ValueError: If API key is not provided or found in environment
    """
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "API key not provided. Set OPENROUTER_API_KEY or OPENAI_API_KEY "
            "environment variable, or pass api_key parameter."
        )

    if base_url is None:
        base_url = os.getenv("OPENROUTER_ENDPOINT")

    return MultiAgentSystem(api_key, base_url)


# CLI interface
def main():
    """Command-line interface for the multi-agent system."""
    from dotenv import load_dotenv
    load_dotenv()

    print("Multi-Agent Development System")
    print("Type 'exit' or 'quit' to end the session")
    print("-" * 70)

    # Create the agent system
    try:
        agent_system = create_agent_system()
    except ValueError as e:
        print(f"Error: {e}")
        return

    while True:
        user_input = input("\nWhat would you like to build? ").strip()

        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            # Run the agent system
            final_state = agent_system.run(user_input)

            # Display summary
            if final_state.get("overall_status") == "completed":
                print("\n✅ Task completed successfully!")
            else:
                print("\n⚠️  Task completed with warnings")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
