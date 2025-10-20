"""
Orchestrator Agent - Main coordinator for the multi-agent system.

This agent is responsible for:
1. Routing tasks to appropriate agents
2. Managing the overall workflow
3. Aggregating results from sub-agents
4. Providing final output to the user
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState


ORCHESTRATOR_SYSTEM_PROMPT = """You are the Orchestrator Agent in a multi-agent software development system.

Your role is to:
1. Coordinate the workflow between specialized agents
2. Determine which agent should execute next
3. Aggregate results from all agents
4. Provide a comprehensive summary to the user

Available agents:
- planner: Creates task breakdowns and plans
- software_architect: Designs repository scaffolding and technical guidelines
- frontend_developer: Implements frontend/UI code
- backend_developer: Implements backend/API code
- tester: Validates code and writes tests

Workflow:
1. User request → Planner (creates plan and tasks)
2. Planner → Frontend Developer (if UI work needed)
3. Frontend Developer → Backend Developer (if backend work needed)
4. Backend Developer → Tester (validates everything)
5. Tester → Orchestrator (you aggregate and summarize)

Your final output should:
- Summarize what was accomplished
- List all files created/modified
- Highlight test results and validation
- Provide clear next steps if any
- Be concise but comprehensive

You do not have tools - you only coordinate and summarize.
"""


class OrchestratorAgent:
    """
    Orchestrator agent that coordinates the multi-agent workflow.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Orchestrator agent.

        Args:
            model: Language model to use
        """
        self.model = model
        self.name = "orchestrator"

    def route(self, state: AgentState) -> str:
        """
        Determine which agent should execute next.

        Args:
            state: Current agent state

        Returns:
            Name of next agent to execute
        """
        # Simple routing logic based on state
        status = state.get("overall_status", "planning")

        if status == "planning":
            return "planner"
        elif status == "implementing":
            # Check next_agent field
            return state.get("next_agent", "frontend_developer")
        elif status == "completed":
            return "end"
        else:
            return "end"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the orchestrator agent - provide final summary.

        Args:
            state: Current agent state

        Returns:
            Updated state with final summary
        """
        print("\n🎯 Orchestrator Agent: Aggregating results and creating summary...")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", ORCHESTRATOR_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Plan created: {plan}

Architectural setup: {architecture_impl}

Frontend implementation: {frontend_impl}

Backend implementation: {backend_impl}

Test results: {test_results}

Please provide a comprehensive summary of what was accomplished, including:
1. Overview of completed work
2. Files created/modified
3. Test and validation results
4. Any recommendations or next steps""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", "No plan created"),
            architecture_impl=state.get("implementation_results", {}).get("architecture", "No architecture work"),
            frontend_impl=state.get("implementation_results", {}).get("frontend", "No frontend work"),
            backend_impl=state.get("implementation_results", {}).get("backend", "No backend work"),
            test_results=state.get("test_results", {}).get("summary", "No test results")
        )

        # Get final summary
        response = self.model.invoke(messages)

        print("\n" + "=" * 70)
        print("FINAL SUMMARY")
        print("=" * 70)
        print(response.content)
        print("=" * 70)

        return {
            "messages": state.get("messages", []) + [response],
            "overall_status": "completed",
            "next_agent": "end",
        }


def create_orchestrator_agent(api_key: str, base_url: str = None) -> OrchestratorAgent:
    """
    Factory function to create an orchestrator agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured OrchestratorAgent
    """
    model_kwargs = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
        "temperature": 0.3
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return OrchestratorAgent(model)
