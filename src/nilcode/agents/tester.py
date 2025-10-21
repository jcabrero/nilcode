"""
Tester & Validator Agent - Handles testing and code validation.

This agent is responsible for:
1. Writing unit tests
2. Validating code quality
3. Checking syntax and style
4. Running code analysis
5. Providing feedback on code improvements
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.task_management import task_tools, set_task_storage
from ..tools.code_analysis import code_analysis_tools
from ..tools.validation_tools import validation_tools


TESTER_SYSTEM_PROMPT = """You are a Tester & Validator Agent in a multi-agent software development system.

Your role is to:
1. Thoroughly validate ALL code for syntax correctness
2. Write comprehensive unit tests
3. Check code quality, style, and complexity
4. Identify and report any syntax errors or issues
5. Provide actionable feedback for improvements

CRITICAL VALIDATION WORKFLOW:

**PHASE 1: Comprehensive Syntax Validation (MANDATORY!)**
1. Read PROJECT_MANIFEST.md to identify all languages used
2. Use list_files to find all code files created
3. For EACH file, run appropriate syntax validation:
   - Python files (.py): Use validate_python_file
   - JavaScript/TypeScript (.js, .jsx, .ts, .tsx): Use validate_javascript_syntax
   - HTML (.html): Use validate_html_syntax
   - JSON (.json): Use validate_json_syntax
4. Check import validity with check_import_validity
5. Document ALL validation errors found

**PHASE 2: Code Quality Analysis**
1. Use code analysis tools:
   - analyze_python_syntax: Deep Python analysis
   - count_functions: Check code organization
   - check_imports: Verify imports
   - find_todos_in_code: Find incomplete work
   - check_code_complexity: Identify complex code
   - validate_code_style: Check style compliance
2. Read the .agent-guidelines/ to verify compliance

**PHASE 3: Test Implementation**
1. Write unit tests for all implemented functionality
2. Follow testing frameworks appropriate to the language:
   - Python: pytest or unittest
   - JavaScript: Jest, Mocha, or Vitest
3. Test edge cases and error handling
4. Ensure tests follow AAA pattern (Arrange, Act, Assert)

**PHASE 4: Reporting**
1. Create a comprehensive validation report including:
   - Syntax validation results for each file
   - Code quality metrics
   - Test coverage summary
   - List of issues found (if any)
   - Recommendations for improvements
2. Update task status to completed

You have access to:
- File tools: read_file, write_file, edit_file, list_files, create_directory
- Validation tools: validate_python_file, validate_javascript_syntax, validate_html_syntax, validate_json_syntax, check_import_validity, auto_detect_language
- Code analysis tools: analyze_python_syntax, count_functions, check_imports, find_todos_in_code, check_code_complexity, validate_code_style
- Task tools: update task status

CRITICAL: You MUST validate EVERY code file created by other agents!
If you find syntax errors, report them clearly with file names and line numbers.

Be thorough, precise, and constructive in your validation and feedback.
"""


class TesterAgent:
    """
    Tester agent that validates code and writes tests.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Tester agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + task_tools + code_analysis_tools + validation_tools
        self.model = model.bind_tools(all_tools)
        self.name = "tester"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the tester agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with test results
        """
        print("\n🧪 Tester & Validator Agent: Validating code and writing tests...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        # Get tester-specific tasks
        tester_tasks = [
            task for task in tasks
            if task.get("assignedTo") == "tester"
            and task.get("status") in ["pending", "in_progress"]
        ]

        if not tester_tasks:
            # If no specific tester tasks, validate the implementation
            print("  No specific test tasks found, performing general validation...")
            task_description = "Validate all implemented code"
        else:
            current_task = tester_tasks[0]
            task_description = current_task["content"]
            print(f"  📋 Working on: {task_description}")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", TESTER_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current plan: {plan}

Detected languages: {languages}
Frontend technologies: {frontend_tech}
Backend technologies: {backend_tech}

Frontend implementation: {frontend_impl}
Backend implementation: {backend_impl}
Architecture implementation: {arch_impl}

Project manifest: {manifest_path}
Guidelines: {guidelines_path}

Task: {task_content}

CRITICAL VALIDATION STEPS:
1. Read {manifest_path} to see what languages/frameworks were used
2. Use list_files to find ALL code files in the project
3. For EACH code file, run the appropriate syntax validator:
   - .py files → validate_python_file
   - .js/.jsx/.ts/.tsx files → validate_javascript_syntax
   - .html files → validate_html_syntax
   - .json files → validate_json_syntax
4. Check import validity for each file
5. Use code analysis tools for quality checks
6. Write unit tests
7. Provide comprehensive validation report with ALL syntax errors found

Start by listing all files and validating each one!""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            languages=", ".join(state.get("detected_languages", [])) or "Not specified",
            frontend_tech=", ".join(state.get("frontend_tech", [])) or "None",
            backend_tech=", ".join(state.get("backend_tech", [])) or "None",
            frontend_impl=state.get("implementation_results", {}).get("frontend", "No frontend code"),
            backend_impl=state.get("implementation_results", {}).get("backend", "No backend code"),
            arch_impl=state.get("implementation_results", {}).get("architecture", "No architecture details"),
            manifest_path=state.get("project_manifest_path", "PROJECT_MANIFEST.md"),
            guidelines_path=state.get("guidelines_path", ".agent-guidelines"),
            task_content=task_description
        )

        # Get response from model
        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 30  # Increased for comprehensive validation
        iteration = 0
        all_tools = file_tools + task_tools + code_analysis_tools + validation_tools
        test_outputs = []

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
                        test_outputs.append({
                            "tool": tool.name,
                            "result": result
                        })

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
                    content="Please provide a comprehensive summary of the test results and validation you just performed, including any issues found or confirmations that the code is working correctly."
                ))
                response = self.model.invoke(messages_history)
                messages_history.append(response)

            print(f"\n✅ Testing and validation completed!")
            summary = response.content if hasattr(response, 'content') and response.content else "Testing completed"
            print(f"Summary: {summary[:200]}..." if len(summary) > 200 else f"Summary: {summary}")
        except Exception as e:
            print(f"\n⚠️ Warning: Error generating summary: {e}")
            summary = "Testing completed (summary generation failed)"

        return {
            "messages": messages_history,
            "next_agent": "orchestrator",  # Return to orchestrator
            "test_results": {
                "summary": summary,
                "tool_outputs": test_outputs
            },
            "overall_status": "completed"
        }


def create_tester_agent(api_key: str, base_url: str = None) -> TesterAgent:
    """
    Factory function to create a tester agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured TesterAgent
    """
    model_kwargs = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return TesterAgent(model)
