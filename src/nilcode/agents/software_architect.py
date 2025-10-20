"""
Software Architect Agent - Establishes project scaffolding and structure.

This agent is responsible for:
1. Designing repository layout and directories
2. Creating initial configuration files
3. Establishing coding standards or shared utilities
4. Coordinating foundational decisions before implementation begins
"""

from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.task_management import task_tools, set_task_storage
from .utils import determine_next_agent


ARCHITECT_SYSTEM_PROMPT = """You are a Software Architect Agent in a multi-agent software development system.

Your role is to:
1. Propose and create the initial project structure (directories, scaffolding)
2. Set up configuration files, base modules, and shared interfaces
3. Document architectural decisions and guidelines for other agents
4. Ensure the repository is ready for frontend, backend, and testing work

You have access to file operation tools:
- read_file: Read existing files
- write_file: Create new files
- edit_file: Modify existing files
- list_files: List files in directories
- create_directory: Create directories

You also have task management tools to update task status.

Best Practices:
- Keep structure consistent and easy to navigate
- Document decisions using concise markdown when helpful
- Avoid overwriting existing user files without reason
- Prepare placeholders so other agents can implement features efficiently

When you complete a task:
1. Use file tools to scaffold the repository
2. Update the task status to "completed"
3. Provide a summary of changes and rationale
"""


class SoftwareArchitectAgent:
    """
    Software architect agent that establishes repository scaffolding.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Software Architect agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + task_tools
        self.model = model.bind_tools(all_tools)
        self.name = "software_architect"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the software architect agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with architectural scaffolding details
        """
        print("\n🏗️  Software Architect Agent: Preparing project structure...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        # Get architect-specific tasks
        architect_tasks = [
            task for task in tasks
            if task.get("assignedTo") == "software_architect"
            and task.get("status") in ["pending", "in_progress"]
        ]

        if not architect_tasks:
            print("  No architecture tasks found, handing off to next agent...")
            next_agent = determine_next_agent(tasks)
            status = "implementing" if next_agent in {
                "software_architect",
                "frontend_developer",
                "backend_developer",
            } else "testing"

            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
                "overall_status": status,
            }

        # Work on the first pending task
        current_task = architect_tasks[0]
        print(f"  📋 Working on: {current_task['content']}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", ARCHITECT_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current plan: {plan}

Current task: {task_content}

Please prepare the repository structure and supporting documentation as needed.
Use file tools to scaffold the project. After implementation, update the task
status to completed and provide a concise summary.""")
        ])

        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            task_content=current_task["content"],
        )

        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        max_iterations = 15
        iteration = 0
        all_tools = file_tools + task_tools

        while response.tool_calls and iteration < max_iterations:
            iteration += 1

            for tool_call in response.tool_calls:
                tool = next((t for t in all_tools if t.name == tool_call["name"]), None)
                if not tool:
                    continue

                print(f"    🔧 Using tool: {tool.name}: {tool_call['args']}")
                result = tool.invoke(tool_call["args"])

                from langchain_core.messages import ToolMessage

                messages_history.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                ))

            response = self.model.invoke(messages_history)
            messages_history.append(response)

        print(f"\n✅ Architecture task completed!")
        print(f"Summary: {response.content[:150]}...")

        updated_tasks = []
        for task in tasks:
            if task["id"] == current_task["id"]:
                task = {**task, "status": "completed", "result": response.content}
            updated_tasks.append(task)

        set_task_storage(updated_tasks)

        next_agent = determine_next_agent(updated_tasks, prefer_agent="software_architect")
        status = "architecting" if next_agent == "software_architect" else (
            "implementing" if next_agent in {"frontend_developer", "backend_developer"} else "testing"
        )

        return {
            "messages": messages_history,
            "tasks": updated_tasks,
            "next_agent": next_agent,
            "overall_status": status,
            "implementation_results": {
                **state.get("implementation_results", {}),
                "architecture": response.content
            },
        }


def create_software_architect_agent(api_key: str, base_url: str = None) -> SoftwareArchitectAgent:
    """
    Factory function to create a software architect agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured SoftwareArchitectAgent
    """
    model_kwargs: Dict[str, Any] = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
        "temperature": 0.2,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return SoftwareArchitectAgent(model)
