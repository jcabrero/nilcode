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
    from .agents.coder import create_coder_agent
    from .agents.tester import create_tester_agent
    from .agents.error_recovery import create_error_recovery_agent
else:
    from .state.agent_state import AgentState, create_initial_state
    from .agents.orchestrator import create_orchestrator_agent
    from .agents.planner import create_planner_agent
    from .agents.software_architect import create_software_architect_agent
    from .agents.coder import create_coder_agent
    from .agents.tester import create_tester_agent
    from .agents.error_recovery import create_error_recovery_agent
    from .agents.a2a_client import create_a2a_client_agent
    from .a2a.registry import initialize_registry_from_config


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
        self.coder = create_coder_agent(api_key, base_url)
        self.tester = create_tester_agent(api_key, base_url)
        self.error_recovery = create_error_recovery_agent(api_key, base_url)
        self.a2a_client = create_a2a_client_agent(use_streaming=False)

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
        workflow.add_node("coder", self.coder)
        workflow.add_node("tester", self.tester)
        workflow.add_node("error_recovery", self.error_recovery)
        workflow.add_node("a2a_client", self.a2a_client)

        # Define the routing logic
        def route_next(state: AgentState) -> str:
            """Determine which agent should execute next."""
            next_agent = state.get("next_agent", "end")

            if next_agent == "end":
                return "end"

            return next_agent or "end"

        # Set entry point
        workflow.set_entry_point("planner")

        # Define all possible agent transitions
        all_agents = {
            "software_architect": "software_architect",
            "coder": "coder",
            "tester": "tester",
            "error_recovery": "error_recovery",
            "orchestrator": "orchestrator",
            "a2a_client": "a2a_client",
            "end": END
        }

        # Add conditional edges from each agent
        workflow.add_conditional_edges("planner", route_next, all_agents)
        workflow.add_conditional_edges("software_architect", route_next, all_agents)
        workflow.add_conditional_edges("coder", route_next, all_agents)
        workflow.add_conditional_edges("tester", route_next, all_agents)
        workflow.add_conditional_edges("error_recovery", route_next, all_agents)
        workflow.add_conditional_edges("a2a_client", route_next, all_agents)
        
        # Orchestrator can route back or end
        workflow.add_conditional_edges(
            "orchestrator",
            route_next,
            {**all_agents, "planner": "planner"}
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
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    # Import the enhanced CLI
    try:
        from .cli import interactive_mode, run_single_command, print_banner, print_error
    except ImportError:
        from cli import interactive_mode, run_single_command, print_banner, print_error

    # Initialize A2A registry at startup
    print("🌐 Initializing A2A external agent registry...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize_registry_from_config())
        loop.close()
        print("✅ A2A registry initialized successfully\n")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize A2A registry: {e}\n")

    # Check for version/changelog flags BEFORE requiring API key
    if len(sys.argv) > 1:
        # Check for version flag
        if sys.argv[1] in ['--version', '-v', 'version']:
            try:
                from .version import print_version_info
            except ImportError:
                from version import print_version_info
            print_version_info()
            return 0

        # Check for changelog flag
        if sys.argv[1] in ['--changelog', 'changelog']:
            try:
                from .version import print_changelog
            except ImportError:
                from version import print_changelog
            print_changelog()
            return 0

    # Create the agent system (requires API key)
    try:
        agent_system = create_agent_system()
    except ValueError as e:
        print_error(str(e))
        return 1

    # Check for command-line arguments
    if len(sys.argv) > 1:
        # Run single command mode
        command = " ".join(sys.argv[1:])
        return run_single_command(agent_system, command)
    else:
        # Run interactive mode
        interactive_mode(agent_system)
        return 0


if __name__ == "__main__":
    main()
