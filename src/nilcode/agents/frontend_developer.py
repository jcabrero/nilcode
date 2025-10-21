"""
Frontend Developer Agent - Handles frontend development tasks.

This agent is responsible for:
1. Creating React/Vue components
2. Writing HTML, CSS, JavaScript, TypeScript
3. Implementing UI features
4. Styling and responsive design
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.task_management import task_tools, set_task_storage
from .utils import determine_next_agent


FRONTEND_SYSTEM_PROMPT = """You are a Frontend Developer Agent in a multi-agent software development system.

Your role is to:
1. Implement frontend features and components
2. Write HTML, CSS, JavaScript, TypeScript, React, Vue code
3. Create responsive and accessible UI components
4. Follow frontend best practices

You have access to file operation tools:
- read_file: Read existing files
- write_file: Create new files
- edit_file: Modify existing files
- list_files: List files in directories
- create_directory: Create directories

You also have task management tools to update task status.

Best Practices:
- Write clean, modular code
- Use semantic HTML
- Follow component-based architecture
- Add comments for complex logic
- Consider accessibility (a11y)
- Use modern ES6+ JavaScript syntax

When you complete a task:
1. Use file tools to create/modify files
2. Update task status to "completed"
3. Provide clear summary of what you implemented

Focus on creating functional, well-structured frontend code.
"""


class FrontendDeveloperAgent:
    """
    Frontend developer agent that handles UI/frontend tasks.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Frontend Developer agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + task_tools
        self.model = model.bind_tools(all_tools)
        self.name = "frontend_developer"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the frontend developer agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with implementation results
        """
        print("\n💻 Frontend Developer Agent: Working on frontend tasks...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        # Get frontend-specific tasks
        frontend_tasks = [
            task for task in tasks
            if task.get("assignedTo") == "frontend_developer"
            and task.get("status") in ["pending", "in_progress"]
        ]

        if not frontend_tasks:
            print("  No frontend tasks found, moving to next agent...")
            next_agent = determine_next_agent(tasks)
            status = "testing" if next_agent == "tester" else (
                "architecting" if next_agent == "software_architect" else "implementing"
            )
            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
                "overall_status": status,
            }

        # Work on the first pending task
        current_task = frontend_tasks[0]
        print(f"  📋 Working on: {current_task['content']}")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", FRONTEND_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current plan: {plan}

Current task: {task_content}

Please implement this task. Use file tools to create/modify files as needed.
After implementation, update the task status to completed and provide a summary.""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            task_content=current_task["content"]
        )

        # Get response from model
        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 15
        iteration = 0
        all_tools = file_tools + task_tools
        tool_outputs = []

        while response.tool_calls and iteration < max_iterations:
            iteration += 1

            for tool_call in response.tool_calls:
                # Find the tool
                tool = next((t for t in all_tools if t.name == tool_call["name"]), None)

                if tool:
                    print(f"    🔧 Using tool: {tool.name}: {tool_call['args']}")
                    result = tool.invoke(tool_call["args"])
                    tool_outputs.append(result)

                    # Add tool response to messages
                    from langchain_core.messages import ToolMessage
                    messages_history.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    ))

            # Get next response
            response = self.model.invoke(messages_history)
            messages_history.append(response)

        # Generate final summary after all tools are done
        if not response.content or len(response.content.strip()) < 50:
            print("    📝 Generating final summary...")
            from langchain_core.messages import HumanMessage
            messages_history.append(HumanMessage(
                content="Please provide a comprehensive summary of what you just implemented, including what files were created/modified and what functionality was added."
            ))
            response = self.model.invoke(messages_history)
            messages_history.append(response)

        print(f"\n✅ Frontend task completed!")
        summary = response.content if response.content else "Task completed"
        print(f"Summary: {summary[:150]}..." if len(summary) > 150 else f"Summary: {summary}")

        # Mark the current task as completed
        updated_tasks = []
        for task in tasks:
            if task["id"] == current_task["id"]:
                task = {**task, "status": "completed", "result": summary}
            updated_tasks.append(task)

        set_task_storage(updated_tasks)

        # Check if there are more frontend tasks
        next_agent = determine_next_agent(updated_tasks, prefer_agent="frontend_developer")
        status = "testing" if next_agent == "tester" else (
            "architecting" if next_agent == "software_architect" else "implementing"
        )

        return {
            "messages": messages_history,
            "tasks": updated_tasks,
            "next_agent": next_agent,
            "overall_status": status,
            "implementation_results": {
                **state.get("implementation_results", {}),
                "frontend": summary
            }
        }


def create_frontend_developer_agent(api_key: str, base_url: str = None) -> FrontendDeveloperAgent:
    """
    Factory function to create a frontend developer agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured FrontendDeveloperAgent
    """
    model_kwargs = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return FrontendDeveloperAgent(model)
