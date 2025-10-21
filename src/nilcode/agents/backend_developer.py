"""
Backend Developer Agent - Handles backend development tasks.

This agent is responsible for:
1. Creating API endpoints
2. Writing server-side logic
3. Database operations
4. Python, Node.js, FastAPI, Express development
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.task_management import task_tools, set_task_storage
from ..tools.validation_tools import validation_tools
from .utils import determine_next_agent


BACKEND_SYSTEM_PROMPT = """You are a Backend Developer Agent in a multi-agent software development system.

Your role is to:
1. Implement backend APIs and server-side logic following project architecture
2. Write syntactically correct Python, Node.js, or other backend code
3. Handle database operations, business logic, and data processing
4. Create secure, efficient, and well-tested backend services
5. Respect architectural decisions made by the Software Architect

CRITICAL WORKFLOW - FOLLOW THIS ORDER:

**PHASE 1: Understand Context (DO THIS FIRST!)**
1. Read PROJECT_MANIFEST.md to understand:
   - Technology stack and frameworks
   - Directory structure and where to place files
   - Architecture patterns (MVC, layered, etc.)
   - Database setup and configuration
2. Read .agent-guidelines/coding-standards.md for:
   - Naming conventions (snake_case for Python, camelCase for JavaScript)
   - Code style requirements
   - Import patterns and module organization
3. Use list_files to see existing file structure
4. Use read_file to examine similar existing files for patterns

**PHASE 2: Implement Code**
1. Create/modify files following the established patterns
2. Use proper naming conventions from guidelines
3. Follow the directory structure from PROJECT_MANIFEST.md
4. Include proper imports and dependencies
5. Add docstrings (Python) or JSDoc (JavaScript) for all functions
6. Implement proper error handling with try/except or try/catch
7. Use type hints (Python) or TypeScript types
8. Follow security best practices (validation, sanitization)

**PHASE 3: Validate Your Work (MANDATORY!)**
1. Use validate_python_file or validate_javascript_syntax on your code
2. Use check_import_validity to verify imports
3. If validation fails, FIX IT before marking complete
4. Re-validate after fixes (max 2 attempts)

**PHASE 4: Complete Task**
1. Only mark task as "completed" if validation passes
2. Provide comprehensive summary including files created/modified

You have access to:
- File tools: read_file, write_file, edit_file, list_files, create_directory
- Validation tools: validate_python_file, validate_python_syntax, validate_javascript_syntax, check_import_validity
- Task tools: update task status

SYNTAX REQUIREMENTS FOR PYTHON:
- Proper indentation (4 spaces per level)
- Correct function definitions: def function_name():
- Valid import statements: import module or from module import name
- Matching parentheses, brackets, and braces
- Proper class definitions: class ClassName:
- Valid decorators: @app.route() for Flask, @router.get() for FastAPI

SYNTAX REQUIREMENTS FOR JAVASCRIPT/NODE:
- Balanced braces {{}}, brackets [], parentheses ()
- Proper function declarations: function name() {{}} or const name = () => {{}}
- Valid import/require: import X from 'module' or const X = require('module')
- Correct async/await syntax

Common mistakes to AVOID:
- Missing colons at end of Python function/class definitions
- Incorrect indentation in Python
- Typos in keywords (def, class, import, function)
- Unmatched parentheses or braces
- Missing imports for used modules
- Incorrect decorator syntax

If validation fails, you MUST fix syntax errors before proceeding!
"""


class BackendDeveloperAgent:
    """
    Backend developer agent that handles server-side/backend tasks.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Backend Developer agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + task_tools + validation_tools
        self.model = model.bind_tools(all_tools)
        self.name = "backend_developer"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the backend developer agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with implementation results
        """
        print("\n⚙️  Backend Developer Agent: Working on backend tasks...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        # Get backend-specific tasks
        backend_tasks = [
            task for task in tasks
            if task.get("assignedTo") == "backend_developer"
            and task.get("status") in ["pending", "in_progress"]
        ]

        if not backend_tasks:
            print("  No backend tasks found, moving to next agent...")
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
        current_task = backend_tasks[0]
        print(f"  📋 Working on: {current_task['content']}")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", BACKEND_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current plan: {plan}

Backend technologies: {backend_tech}
Project manifest location: {manifest_path}
Guidelines location: {guidelines_path}

Current task: {task_content}

IMPORTANT WORKFLOW:
1. FIRST: Read {manifest_path} (if exists) to understand project structure
2. SECOND: Read {guidelines_path}/coding-standards.md (if exists) for conventions
3. THIRD: Use list_files to see existing structure
4. FOURTH: Implement your code following the established patterns
5. FIFTH: Validate syntax using validation tools (validate_python_file or validate_javascript_syntax)
6. SIXTH: Only if validation passes, update task status to "completed"

Begin by reading the project documentation!""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            backend_tech=", ".join(state.get("backend_tech", [])) or "Not specified",
            manifest_path=state.get("project_manifest_path", "PROJECT_MANIFEST.md"),
            guidelines_path=state.get("guidelines_path", ".agent-guidelines"),
            task_content=current_task["content"]
        )

        # Get response from model
        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 20  # Increased for validation retries
        iteration = 0
        all_tools = file_tools + task_tools + validation_tools
        tool_outputs = []

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

                    if tool:
                        print(f"    🔧 Using tool: {tool.name}: {tool_args}")
                        result = tool.invoke(tool_args)
                        tool_outputs.append(result)

                        # Add tool response to messages
                        from langchain_core.messages import ToolMessage
                        messages_history.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_id if tool_id else str(iteration)
                        ))
                except Exception as e:
                    print(f"    ⚠️ Error processing tool call: {e}")
                    continue

            # Get next response
            response = self.model.invoke(messages_history)
            messages_history.append(response)

        # Generate final summary after all tools are done
        try:
            if not response.content or len(response.content.strip()) < 50:
                print("    📝 Generating final summary...")
                from langchain_core.messages import HumanMessage
                messages_history.append(HumanMessage(
                    content="Please provide a comprehensive summary of what you just implemented, including what files were created/modified and what functionality was added."
                ))
                response = self.model.invoke(messages_history)
                messages_history.append(response)

            print(f"\n✅ Backend task completed!")
            summary = response.content if hasattr(response, 'content') and response.content else "Task completed"
            print(f"Summary: {summary[:150]}..." if len(summary) > 150 else f"Summary: {summary}")
        except Exception as e:
            print(f"\n⚠️ Warning: Error generating summary: {e}")
            summary = "Task completed (summary generation failed)"

        # Mark the current task as completed
        updated_tasks = []
        for task in tasks:
            if task["id"] == current_task["id"]:
                task = {**task, "status": "completed", "result": summary}
            updated_tasks.append(task)

        set_task_storage(updated_tasks)

        next_agent = determine_next_agent(updated_tasks, prefer_agent="backend_developer")
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
                "backend": summary
            }
        }


def create_backend_developer_agent(api_key: str, base_url: str = None) -> BackendDeveloperAgent:
    """
    Factory function to create a backend developer agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured BackendDeveloperAgent
    """
    model_kwargs = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return BackendDeveloperAgent(model)
