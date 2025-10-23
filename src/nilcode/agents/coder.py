"""
Coder Agent - Handles ALL implementation tasks including frontend, backend, and dependency management.

This agent is responsible for:
1. Creating package.json, pyproject.toml, and all configuration files
2. Writing frontend code (React, Vue, HTML, CSS, JavaScript, TypeScript)
3. Writing backend code (Python, Node.js, APIs, databases)
4. Managing dependencies and project configuration
5. Following architectural patterns established by the Software Architect
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.task_management import task_tools, set_task_storage
from ..tools.validation_tools import validation_tools
from ..tools.file_verification import file_verification_tools
from ..tools.retry_tools import retry_tools
from ..tools.enhanced_task_management import enhanced_task_tools
from .utils import determine_next_agent

from ..prompts.claude import PROMPT

CODER_SYSTEM_PROMPT = PROMPT.replace("{", "{{").replace("}", "}}") + """
## Code References

When referencing specific functions or pieces of code include the pattern `file_path:line_number` to allow the user to easily navigate to the source code location.

You are a Coder Agent in a multi-agent software development system.

Your role is to handle ALL implementation tasks including:
1. **Dependency Management**: Create package.json, pyproject.toml, .env.example, .gitignore, and all config files
2. **Frontend Development**: Write React, Vue, HTML, CSS, JavaScript, TypeScript, UI components
3. **Backend Development**: Write Python, Node.js, APIs, databases, server logic
4. **Code Quality**: Follow architectural patterns and ensure syntactically correct code

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

**PHASE 2: Dependency Management (IF NEEDED)**
1. Create package.json for JavaScript/TypeScript/Node.js projects with ALL dependencies:
   - React projects: react, react-dom, react-scripts OR vite
   - Next.js projects: next, react, react-dom
   - Vue projects: vue, @vitejs/plugin-vue
   - Express projects: express, cors, dotenv
   - TypeScript: typescript, @types/node, @types/react (if React)
2. Create pyproject.toml for Python projects with dependencies:
   - FastAPI projects: fastapi, uvicorn, pydantic
   - Flask projects: flask, flask-cors
   - Django projects: django, djangorestframework
   - Always include: python-dotenv, pytest (dev)
3. Create .env.example with environment variables
4. Create .gitignore appropriate for the languages used
5. Create README.md with installation and run instructions

**PHASE 3: Implement Code**
1. Create/modify files following the established patterns
2. Use proper naming conventions from guidelines
3. Follow the directory structure from PROJECT_MANIFEST.md
4. Include proper imports and dependencies
5. Add docstrings (Python) or JSDoc (JavaScript) for all functions
6. Implement proper error handling with try/except or try/catch
7. Use type hints (Python) or TypeScript types
8. Follow security best practices (validation, sanitization)

**PHASE 4: Validate Your Work (MANDATORY!)**
1. Use appropriate syntax validation tools:
   - Python files (.py): Use validate_python_file
   - JavaScript/TypeScript (.js, .jsx, .ts, .tsx): Use validate_javascript_syntax
   - HTML (.html): Use validate_html_syntax
   - JSON (.json): Use validate_json_syntax
2. Use check_import_validity to verify imports
3. Use verify_file_exists and verify_file_content to confirm files are actually created
4. If validation fails, FIX IT before marking complete
5. Re-validate after fixes (max 2 attempts)

**PHASE 5: Track Progress and Context (ALWAYS!)**
1. Use update_task_progress to track what you've accomplished
2. Use update_task_requirements to document what was needed
3. Use verify_multiple_files to confirm all expected files exist
4. Use get_task_context to review what's been done
5. Document any implementation decisions in the task notes

**PHASE 6: Complete Task**
1. Only mark task as "completed" if validation passes
2. Provide comprehensive summary including files created/modified

You have access to:
- File tools: read_file, write_file, edit_file, list_files, create_directory
- Validation tools: validate_python_file, validate_python_syntax, validate_javascript_syntax, validate_html_syntax, validate_json_syntax, check_import_validity
- File verification tools: verify_file_exists, verify_file_content, verify_multiple_files, check_file_permissions, verify_directory_structure
- Task tools: update task status, create_enhanced_task, update_task_progress, get_task_context, validate_task_completion
- Retry tools: start_retry_tracking, record_retry_attempt, wait_for_retry

SYNTAX REQUIREMENTS FOR PYTHON:
- Proper indentation (4 spaces per level)
- Correct function definitions: def function_name():
- Valid import statements: import module or from module import name
- Matching parentheses, brackets, and braces
- Proper class definitions: class ClassName:
- Valid decorators: @app.route() for Flask, @router.get() for FastAPI

SYNTAX REQUIREMENTS FOR JAVASCRIPT/TYPESCRIPT:
- Balanced braces {{}}, brackets [], parentheses ()
- Proper function declarations: function name() {{}} or const name = () => {{}}
- Valid import/require: import X from 'module' or const X = require('module')
- Correct async/await syntax
- React: Proper JSX syntax with closing tags
- HTML: Matching open and close tags

Common mistakes to AVOID:
- Missing colons at end of Python function/class definitions
- Incorrect indentation in Python
- Typos in keywords (def, class, import, function)
- Unmatched parentheses or braces
- Missing imports for used modules
- Incorrect decorator syntax
- Unclosed JSX tags
- Missing 'from' in import statements

If validation fails, you MUST fix syntax errors before proceeding!
"""


class CoderAgent:
    """
    Coder agent that handles all implementation tasks.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Coder agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + task_tools + validation_tools + file_verification_tools + retry_tools + enhanced_task_tools
        self.model = model.bind_tools(all_tools)
        self.name = "coder"

    def _invoke_with_retry(self, messages, state, max_retries=3):
        """
        Invoke the model with retry handling for rate limits and other transient errors.
        
        Args:
            messages: Messages to send to the model
            state: Current agent state
            max_retries: Maximum number of retry attempts
            
        Returns:
            Model response
        """
        from openai import RateLimitError
        import time
        import random
        
        for attempt in range(max_retries + 1):
            try:
                print(f"    🤖 Calling LLM (attempt {attempt + 1}/{max_retries + 1})...")
                response = self.model.invoke(messages)
                return response
                
            except RateLimitError as e:
                if attempt == max_retries:
                    print(f"    ❌ Rate limit exceeded after {max_retries} retries")
                    print(f"    💡 Consider using a different model or adding your own API key")
                    raise e
                
                # Calculate exponential backoff with jitter
                base_delay = 2 ** attempt  # 1, 2, 4, 8 seconds
                jitter = random.uniform(0.5, 1.5)  # Add randomness
                delay = base_delay * jitter
                
                print(f"    ⚠️  Rate limit hit: {str(e)}")
                print(f"    ⏳ Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
                
                # Update task progress to show retry attempt
                if "tasks" in state:
                    tasks = state["tasks"]
                    for task in tasks:
                        if task.get("status") == "in_progress":
                            task["retry_count"] = attempt + 1
                            task["last_error"] = f"Rate limit error (attempt {attempt + 1})"
                            task["progress"] = f"Retrying due to rate limit (attempt {attempt + 1})"
                
            except Exception as e:
                if attempt == max_retries:
                    print(f"    ❌ Error after {max_retries} retries: {str(e)}")
                    raise e
                
                print(f"    ⚠️  Error: {str(e)}")
                print(f"    ⏳ Retrying in 2 seconds...")
                time.sleep(2)

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the coder agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with implementation results
        """
        print("\n💻 Coder Agent: Working on implementation tasks...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        # Get coder-specific tasks
        coder_tasks = [
            task for task in tasks
            if task.get("assignedTo") == "coder"
            and task.get("status") in ["pending", "in_progress"]
        ]

        if not coder_tasks:
            print("  No coder tasks found, moving to next agent...")
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
        current_task = coder_tasks[0]
        print(f"  📋 Working on: {current_task['content']}")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", CODER_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current plan: {plan}

Detected languages: {languages}
Frontend technologies: {frontend_tech}
Backend technologies: {backend_tech}
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
            languages=", ".join(state.get("detected_languages", [])) or "Not specified",
            frontend_tech=", ".join(state.get("frontend_tech", [])) or "None",
            backend_tech=", ".join(state.get("backend_tech", [])) or "None",
            manifest_path=state.get("project_manifest_path", "PROJECT_MANIFEST.md"),
            guidelines_path=state.get("guidelines_path", ".agent-guidelines"),
            task_content=current_task["content"]
        )

        # Get response from model with retry handling for rate limits
        response = self._invoke_with_retry(messages, state)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 25  # Increased for comprehensive implementation
        iteration = 0
        all_tools = file_tools + task_tools + validation_tools + file_verification_tools + retry_tools + enhanced_task_tools
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

            # Get next response with retry handling
            response = self._invoke_with_retry(messages_history, state)
            messages_history.append(response)

        # Generate final summary after all tools are done
        try:
            if not response.content or len(response.content.strip()) < 50:
                print("    📝 Generating final summary...")
                from langchain_core.messages import HumanMessage
                messages_history.append(HumanMessage(
                    content="Please provide a comprehensive summary of what you just implemented, including what files were created/modified and what functionality was added."
                ))
                response = self._invoke_with_retry(messages_history, state)
                messages_history.append(response)

            print(f"\n✅ Coder task completed!")
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

        # Check if there are more coder tasks
        next_agent = determine_next_agent(updated_tasks, prefer_agent="coder")
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
                "coder": summary
            }
        }


def create_coder_agent(api_key: str, base_url: str = None) -> CoderAgent:
    """
    Factory function to create a coder agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured CoderAgent
    """
    model_kwargs = {
        "model": "qwen/qwen3-coder-30b-a3b-instruct",  # More reliable than free models
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return CoderAgent(model)
