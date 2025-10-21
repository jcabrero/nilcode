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
from ..prompts.claude import PROMPT


ARCHITECT_SYSTEM_PROMPT = PROMPT.replace("{", "{{").replace("}", "}}") + """

## Code References

When referencing specific functions or pieces of code include the pattern `file_path:line_number` to allow the user to easily navigate to the source code location.

You are a Software Architect Agent in a multi-agent software development system.

Your role is to:
1. Establish the foundational project structure (directories, scaffolding)
2. Create a PROJECT_MANIFEST.md documenting all architectural decisions
3. Create .agent-guidelines/ directory with specific coding standards
4. Set up configuration files, base modules, and shared interfaces
5. Ensure all other agents can follow your established patterns

CRITICAL REQUIREMENTS - YOU MUST DO THESE FIRST:

1. **Read existing project state**:
   - ALWAYS use list_files to check what exists before creating files
   - Use read_file to understand existing patterns and conventions
   - Never overwrite files without checking their contents first

2. **Create PROJECT_MANIFEST.md** containing:
   - Project name and description
   - Technology stack (languages, frameworks, libraries)
   - Directory structure with explanations
   - File naming conventions
   - Architecture patterns being used
   - Dependencies and how to install them

3. **Create .agent-guidelines/ directory** with:
   - `coding-standards.md`: Language-specific coding standards
   - `file-structure.md`: Where different types of files should go
   - `naming-conventions.md`: How to name files, functions, classes, variables

4. **Follow these patterns**:
   - For Python: Use snake_case for functions/variables, PascalCase for classes
   - For JavaScript/TypeScript: Use camelCase for functions/variables, PascalCase for components
   - Always include proper imports/exports
   - Create README.md if it doesn't exist

You have access to file operation tools:
- read_file: Read existing files (USE THIS FIRST!)
- write_file: Create new files
- edit_file: Modify existing files
- list_files: List files in directories (USE THIS BEFORE CREATING!)
- create_directory: Create directories

Task completion checklist:
1. ✓ Listed existing files to understand current state
2. ✓ Created PROJECT_MANIFEST.md with complete documentation
3. ✓ Created .agent-guidelines/ with coding standards
4. ✓ Set up proper directory structure
5. ✓ Updated task status to "completed"
6. ✓ Provided comprehensive summary
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
                "coder",
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

Detected languages: {languages}
Frontend technologies: {frontend_tech}
Backend technologies: {backend_tech}

Current task: {task_content}

IMPORTANT: Before creating any files, use list_files to see what already exists.
Create PROJECT_MANIFEST.md and .agent-guidelines/ directory first.
Document the technology stack ({languages}) and all architectural decisions.

After completing all setup, update the task status to completed and provide a comprehensive summary.""")
        ])

        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            languages=", ".join(state.get("detected_languages", [])) or "Not specified",
            frontend_tech=", ".join(state.get("frontend_tech", [])) or "None",
            backend_tech=", ".join(state.get("backend_tech", [])) or "None",
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
                try:
                    # Handle both dict and object-style tool calls
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get("name")
                        tool_args = tool_call.get("args", {})
                        tool_id = tool_call.get("id")
                    else:
                        # Handle as object with attributes
                        tool_name = getattr(tool_call, "name", None)
                        tool_args = getattr(tool_call, "args", {})
                        tool_id = getattr(tool_call, "id", None)

                    if not tool_name:
                        print(f"    ⚠️ Skipping invalid tool call")
                        continue

                    # Find the tool
                    tool = next((t for t in all_tools if t.name == tool_name), None)
                    if not tool:
                        print(f"    ⚠️ Tool '{tool_name}' not found")
                        continue

                    print(f"    🔧 Using tool: {tool.name}: {tool_args}")
                    result = tool.invoke(tool_args)

                    from langchain_core.messages import ToolMessage

                    messages_history.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id if tool_id else str(iteration)
                    ))
                except Exception as e:
                    print(f"    ⚠️ Error processing tool call: {e}")
                    continue

            response = self.model.invoke(messages_history)
            messages_history.append(response)

        # Generate final summary after all tools are done
        try:
            if not response.content or len(response.content.strip()) < 50:
                print("    📝 Generating final summary...")
                from langchain_core.messages import HumanMessage
                messages_history.append(HumanMessage(
                    content="Please provide a comprehensive summary of what you just implemented, including what files/directories were created and what structure was set up."
                ))
                response = self.model.invoke(messages_history)
                messages_history.append(response)

            print(f"\n✅ Architecture task completed!")
            summary = response.content if hasattr(response, 'content') and response.content else "Task completed"
            print(f"Summary: {summary[:150]}..." if len(summary) > 150 else f"Summary: {summary}")
        except Exception as e:
            print(f"\n⚠️ Warning: Error generating summary: {e}")
            summary = "Task completed (summary generation failed)"

        updated_tasks = []
        for task in tasks:
            if task["id"] == current_task["id"]:
                task = {**task, "status": "completed", "result": summary}
            updated_tasks.append(task)

        set_task_storage(updated_tasks)

        next_agent = determine_next_agent(updated_tasks, prefer_agent="software_architect")
        status = "architecting" if next_agent == "software_architect" else (
            "implementing" if next_agent == "coder" else "testing"
        )

        # Determine manifest and guidelines paths from working directory
        working_dir = state.get("working_directory", ".")
        import os
        manifest_path = os.path.join(working_dir, "PROJECT_MANIFEST.md")
        guidelines_path = os.path.join(working_dir, ".agent-guidelines")

        return {
            "messages": messages_history,
            "tasks": updated_tasks,
            "next_agent": next_agent,
            "overall_status": status,
            "project_manifest_path": manifest_path,
            "guidelines_path": guidelines_path,
            "implementation_results": {
                **state.get("implementation_results", {}),
                "architecture": summary
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
        "model": "openai/gpt-oss-120b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return SoftwareArchitectAgent(model)
