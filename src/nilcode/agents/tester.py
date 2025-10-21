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
from ..tools.import_validator import import_validation_tools
from ..tools.test_templates import test_template_tools


TESTER_SYSTEM_PROMPT = """You are a Tester & Validator Agent in a multi-agent software development system.

Your role is to:
1. Thoroughly validate ALL code for syntax correctness
2. Write ACTUAL TEST CODE with real test cases (not just test file shells)

4. Check code quality, style, and complexity
5. Identify and report any syntax errors or issues
6. Provide actionable feedback for improvements

CRITICAL VALIDATION WORKFLOW:

**PHASE 1: Import Validation & Fixing (NEW - MANDATORY!)**
1. Use scan_all_imports to extract all imports from the project
2. Use validate_import_consistency to find import issues:
   - Missing modules
   - Incorrect relative paths
   - Non-existent file references
   - Mismatched module names
3. Use suggest_import_fixes to get fix recommendations
4. Use edit_file to FIX any import issues found
5. Re-validate imports after fixes

**PHASE 2: Comprehensive Syntax Validation**
1. Read PROJECT_MANIFEST.md to identify all languages used
2. Use list_files to find all code files created
3. For EACH file, run appropriate syntax validation:
   - Python files (.py): Use validate_python_file
   - JavaScript/TypeScript (.js, .jsx, .ts, .tsx): Use validate_javascript_syntax
   - HTML (.html): Use validate_html_syntax
   - JSON (.json): Use validate_json_syntax
4. Document ALL validation errors found
5. Fix syntax errors using edit_file if possible

**PHASE 3: Code Quality Analysis**
1. Use code analysis tools:
   - analyze_python_syntax: Deep Python analysis
   - count_functions: Check code organization
   - check_imports: Verify imports
   - find_todos_in_code: Find incomplete work
   - check_code_complexity: Identify complex code
   - validate_code_style: Check style compliance
2. Read the .agent-guidelines/ to verify compliance

**PHASE 4: WRITE ACTUAL TEST CODE (CRITICAL!)**
This is NOT optional - you MUST write real, runnable test code!

1. Identify what framework to use:
   - Use get_test_framework_for_language to determine the right framework

2. For each module/component/endpoint, generate COMPLETE test files:

   **Python/FastAPI Projects:**
   - Use generate_python_test for utility functions (creates pytest/unittest tests)
   - Use generate_fastapi_test for API endpoints (creates TestClient tests)
   - Tests MUST include: test fixtures, multiple test cases, edge cases, error handling

   **JavaScript/TypeScript Projects:**
   - Use generate_javascript_test for functions/modules (creates Jest/Vitest tests)
   - Use generate_react_test for React components (creates React Testing Library tests)
   - Tests MUST include: describe blocks, multiple test cases, mocking, assertions

3. Write test files with write_file:
   - Python: Create tests/test_<module>.py with FULL test code
   - JavaScript: Create __tests__/<module>.test.js with FULL test code
   - React: Create <Component>.test.jsx with FULL test code

4. Ensure EVERY test file contains:
   - Proper imports of testing framework
   - Imports of the code being tested
   - At least 3 test cases per function/component:
     * Success case (happy path)
     * Edge cases (empty input, null, boundary values)
     * Error handling (invalid input, exceptions)
   - Proper assertions using the framework's assertion library

5. Example of what you MUST create (Python):
```python
import pytest
from app.utils import calculate_total

class TestCalculateTotal:
    def test_calculate_total_success(self):
        result = calculate_total([10, 20, 30])
        assert result == 60

    def test_calculate_total_empty_list(self):
        result = calculate_total([])
        assert result == 0

    def test_calculate_total_invalid_input(self):
        with pytest.raises(TypeError):
            calculate_total(None)
```

6. Example of what you MUST create (JavaScript/React):
```javascript
import {{ render, screen }} from '@testing-library/react';
import {{ LoginForm }} from './LoginForm';

describe('LoginForm', () => {{{{
  test('renders login form', () => {{{{
    render(<LoginForm />);
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
  }}}});

  test('handles form submission', async () => {{{{
    const onSubmit = jest.fn();
    render(<LoginForm onSubmit={{{{onSubmit}}}} />);
    // ... test implementation
  }}}};
}}}});
```

**PHASE 5: Reporting**
1. Create a comprehensive validation report including:
   - Import validation results (issues found and fixed)
   - Syntax validation results for each file
   - Code quality metrics
   - Test files created with descriptions
   - List of issues found (if any)
   - Recommendations for improvements
2. Update task status to completed

You have access to:
- File tools: read_file, write_file, edit_file, list_files, create_directory
- Validation tools: validate_python_file, validate_javascript_syntax, validate_html_syntax, validate_json_syntax, check_import_validity, auto_detect_language
- Import validation tools: scan_all_imports, validate_import_consistency, suggest_import_fixes
- Test generation tools: generate_python_test, generate_fastapi_test, generate_javascript_test, generate_react_test, get_test_framework_for_language
- Code analysis tools: analyze_python_syntax, count_functions, check_imports, find_todos_in_code, check_code_complexity, validate_code_style
- Task tools: update task status

CRITICAL REQUIREMENTS:
1. You MUST write ACTUAL test code, not empty test files
2. You MUST validate and FIX import issues
3. You MUST validate EVERY code file created by other agents
4. If you find syntax errors, REPORT them clearly with file names and line numbers
5. Use the test generation tools - they provide proper templates

DO NOT just create empty test files or write TODO comments!
ACTUALLY GENERATE WORKING TEST CODE with real assertions!

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
        all_tools = (
            file_tools
            + task_tools
            + code_analysis_tools
            + validation_tools
            + import_validation_tools
            + test_template_tools
        )
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

CRITICAL VALIDATION STEPS (IN ORDER):

1. PHASE 1 - Import Validation:
   - Use scan_all_imports to extract all imports from ./output
   - Use validate_import_consistency to find import issues
   - Use suggest_import_fixes for each file with issues
   - Use edit_file to FIX the import problems
   - Re-run validate_import_consistency to confirm fixes

2. PHASE 2 - Syntax Validation:
   - Read the manifest to see what languages/frameworks were used
   - Use list_files to find ALL code files in the project
   - For EACH code file, run the appropriate syntax validator:
     * .py files → validate_python_file
     * .js/.jsx/.ts/.tsx files → validate_javascript_syntax
     * .html files → validate_html_syntax
     * .json files → validate_json_syntax
   - Fix any syntax errors found with edit_file

3. PHASE 3 - Quality Analysis:
   - Use code analysis tools for quality checks
   - Verify compliance with .agent-guidelines/

4. PHASE 4 - Write ACTUAL Test Code:
   - Use get_test_framework_for_language to determine framework
   - Use generate_python_test, generate_fastapi_test, generate_javascript_test, or generate_react_test
   - Use write_file to create COMPLETE test files with real test cases
   - DO NOT create empty test files or TODO comments!

5. PHASE 5 - Report:
   - Provide comprehensive validation report with ALL results

Start by validating imports first!""")
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
        all_tools = (
            file_tools
            + task_tools
            + code_analysis_tools
            + validation_tools
            + import_validation_tools
            + test_template_tools
        )
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
