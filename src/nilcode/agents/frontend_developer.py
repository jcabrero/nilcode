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
from ..tools.validation_tools import validation_tools
from .utils import determine_next_agent


FRONTEND_SYSTEM_PROMPT = """You are a Frontend Developer Agent in a multi-agent software development system.

Your role is to:
1. Implement frontend features following the established project structure
2. Write syntactically correct HTML, CSS, JavaScript, TypeScript, React, Vue code
3. Create responsive, accessible, and well-tested UI components
4. Respect architectural decisions made by the Software Architect

CRITICAL WORKFLOW - FOLLOW THIS ORDER:

**PHASE 1: Understand Context (DO THIS FIRST!)**
1. Read PROJECT_MANIFEST.md to understand:
   - Technology stack and frameworks
   - Directory structure and where to place files
   - Architecture patterns to follow
2. Read .agent-guidelines/coding-standards.md for:
   - Naming conventions (camelCase vs snake_case)
   - Code style requirements
   - Import/export patterns
3. Use list_files to see existing file structure
4. Use read_file to examine similar existing files for patterns

**PHASE 2: Implement Code**
1. Create/modify files following the established patterns
2. Use proper naming conventions from guidelines
3. Follow the directory structure from PROJECT_MANIFEST.md
4. Include proper imports/exports
5. Add JSDoc comments for functions and components
6. Handle errors and edge cases

**PHASE 3: Validate Your Work (MANDATORY!)**
1. Use validate_javascript_syntax or validate_html_syntax on your code
2. Use check_import_validity to verify imports
3. If validation fails, FIX IT before marking complete
4. Re-validate after fixes (max 2 attempts)

**PHASE 4: Complete Task**
1. Only mark task as "completed" if validation passes
2. Provide comprehensive summary including files created/modified

You have access to:
- File tools: read_file, write_file, edit_file, list_files, create_directory
- Validation tools: validate_javascript_syntax, validate_html_syntax, check_import_validity, validate_json_syntax
- Task tools: update task status

SYNTAX REQUIREMENTS:
- JavaScript/TypeScript: Balanced braces {{}}, brackets [], parentheses ()
- Proper function declarations: function name() {{}} or const name = () => {{}}
- Valid import statements: import {{ X }} from 'module' or import X from 'module'
- React: Proper JSX syntax with closing tags
- HTML: Matching open and close tags

Common mistakes to AVOID:
- Unmatched braces, brackets, or parentheses
- Typos in keywords (fucntion, retrun, improt)
- Missing semicolons in critical places
- Unclosed JSX tags
- Incorrect import syntax
- Missing 'from' in import statements

If validation fails, you MUST fix syntax errors before proceeding!
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
        all_tools = file_tools + task_tools + validation_tools
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

Frontend technologies: {frontend_tech}
Project manifest location: {manifest_path}
Guidelines location: {guidelines_path}

Current task: {task_content}

IMPORTANT WORKFLOW:
1. FIRST: Read {manifest_path} (if exists) to understand project structure
2. SECOND: Read {guidelines_path}/coding-standards.md (if exists) for conventions
3. THIRD: Use list_files to see existing structure
4. FOURTH: Implement your code following the established patterns
5. FIFTH: Validate syntax using validation tools
6. SIXTH: Only if validation passes, update task status to "completed"

Begin by reading the project documentation!""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            frontend_tech=", ".join(state.get("frontend_tech", [])) or "Not specified",
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

            print(f"\n✅ Frontend task completed!")
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
