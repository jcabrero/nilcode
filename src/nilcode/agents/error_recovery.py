"""
Error Recovery Agent - Monitors errors and implements self-correction.

This agent is responsible for:
1. Detecting errors from linters, tests, and command execution
2. Analyzing error messages to understand root causes
3. Proposing and implementing fixes
4. Retrying failed operations with corrections
5. Learning from failures to avoid repeating mistakes
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.terminal_tools import terminal_tools
from ..tools.code_analysis import code_analysis_tools
from .utils import determine_next_agent


ERROR_RECOVERY_SYSTEM_PROMPT = """You are an Error Recovery Agent in a multi-agent software development system.

Your role is to:
1. Monitor for errors in linting, testing, and code execution
2. Analyze error messages to understand what went wrong
3. Propose specific fixes for the errors
4. Implement the fixes using available tools
5. Verify that fixes resolve the issues

You have access to tools:
- run_linter: Check for code style and syntax issues
- run_tests: Execute tests and see results
- read_file: Read file contents to understand context
- write_file: Create corrected versions of files
- edit_file: Make targeted edits to fix issues
- analyze_python_syntax: Check Python syntax validity

Error Analysis Process:
1. Identify the type of error (syntax, import, logic, test failure, etc.)
2. Locate the exact file and line number
3. Understand the context around the error
4. Determine the root cause
5. Propose a specific fix
6. Implement the fix
7. Verify the fix resolves the error

Common Error Patterns and Fixes:

**Syntax Errors:**
- Missing colons, parentheses, brackets
- Indentation issues
- Invalid Python/JS syntax

**Import Errors:**
- Missing packages (suggest installation)
- Wrong import paths
- Circular imports

**Type Errors:**
- Incorrect types passed to functions
- Missing type annotations
- Type mismatches

**Test Failures:**
- Incorrect assertions
- Missing test data
- Logic errors in implementation

**Runtime Errors:**
- Division by zero
- None type errors
- Index out of bounds

Best Practices:
- Be specific about fixes - don't just describe them, implement them
- Test fixes before moving on
- Don't make changes that aren't directly related to the error
- If a fix doesn't work, try a different approach
- Keep track of what you've tried to avoid loops
- If stuck after 3 attempts, escalate to orchestrator

When you complete error recovery:
1. Summarize what errors were found
2. List the fixes you implemented
3. Verify that errors are resolved
4. Report success or remaining issues
"""


class ErrorRecoveryAgent:
    """
    Error recovery agent that detects and fixes errors in code.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Error Recovery agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + terminal_tools + code_analysis_tools
        self.model = model.bind_tools(all_tools)
        self.name = "error_recovery"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the error recovery agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with error fixes
        """
        print("\n🔧 Error Recovery Agent: Checking for errors...")

        # Check iteration count to prevent infinite loops
        iteration = state.get("iteration_count", 0)
        if iteration >= 5:
            print("  ⚠️  Max iterations reached, escalating to orchestrator...")
            return {
                "next_agent": "orchestrator",
                "overall_status": "failed",
                "error": "Max error recovery iterations reached",
                "messages": state.get("messages", []),
            }

        # Check for errors in recent activity
        errors = self._detect_errors(state)

        if not errors:
            print("  ✅ No errors detected, continuing workflow...")
            tasks = state.get("tasks", [])
            next_agent = determine_next_agent(tasks)
            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
            }

        print(f"  ⚠️  Found {len(errors)} error(s) to fix")

        # Build error summary
        error_summary = "\n\n".join([
            f"Error {i+1}:\n{error}" for i, error in enumerate(errors)
        ])

        # Get modified files for context
        modified_files = state.get("modified_files", [])
        files_context = ""
        if modified_files:
            files_context = f"\n\nRecently modified files:\n" + "\n".join([f"- {f}" for f in modified_files[-10:]])

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", ERROR_RECOVERY_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Errors detected:
{error_summary}
{files_context}

Please analyze these errors and fix them:
1. Read the relevant files to understand context
2. Identify the root cause of each error
3. Implement specific fixes using the file operation tools
4. Run linters or tests to verify fixes
5. Summarize what you fixed

Focus on fixing the errors completely, not just partially.""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            error_summary=error_summary,
            files_context=files_context
        )

        # Get response from model
        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_tool_iterations = 15
        tool_iteration = 0
        all_tools = file_tools + terminal_tools + code_analysis_tools

        while response.tool_calls and tool_iteration < max_tool_iterations:
            tool_iteration += 1

            for tool_call in response.tool_calls:
                # Find the tool
                tool = next((t for t in all_tools if t.name == tool_call["name"]), None)

                if tool:
                    print(f"    🔧 Using tool: {tool.name}")
                    result = tool.invoke(tool_call["args"])

                    # Add tool response to messages
                    from langchain_core.messages import ToolMessage
                    messages_history.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    ))

            # Get next response
            response = self.model.invoke(messages_history)
            messages_history.append(response)

        # Generate final summary
        print("    📝 Generating fix summary...")
        from langchain_core.messages import HumanMessage
        messages_history.append(HumanMessage(
            content="Please provide a summary of the errors you fixed and verify that the fixes resolved the issues."
        ))
        response = self.model.invoke(messages_history)
        messages_history.append(response)

        print(f"\n✅ Error recovery completed!")
        summary = response.content if response.content else "Error fixes applied"
        print(f"Summary: {summary[:200]}..." if len(summary) > 200 else f"Summary: {summary}")

        # Increment iteration count
        new_iteration = iteration + 1

        # Determine next agent
        tasks = state.get("tasks", [])
        next_agent = determine_next_agent(tasks)

        return {
            "messages": messages_history,
            "next_agent": next_agent,
            "iteration_count": new_iteration,
            "error": "",  # Clear error flag after recovery attempt
        }

    def _detect_errors(self, state: AgentState) -> List[str]:
        """
        Detect errors from state.

        Args:
            state: Current agent state

        Returns:
            List of error descriptions
        """
        errors = []

        # Check for explicit error flag
        if state.get("error"):
            errors.append(f"System Error: {state['error']}")

        # Check linter results
        linter_results = state.get("linter_results", {})
        if linter_results.get("issues"):
            errors.append(f"Linter Issues:\n{linter_results['issues']}")

        # Check test results
        test_results = state.get("test_results", {})
        if test_results.get("failed_tests"):
            errors.append(f"Test Failures:\n{test_results.get('summary', 'Tests failed')}")

        # Check test execution results
        test_exec_results = state.get("test_execution_results", [])
        if test_exec_results:
            last_test = test_exec_results[-1]
            if last_test.get("exit_code", 0) != 0:
                errors.append(f"Test Execution Failed:\n{last_test.get('output', 'Unknown error')}")

        # Check command history for errors
        cmd_history = state.get("command_history", [])
        if cmd_history:
            last_cmd = cmd_history[-1]
            if last_cmd.get("exit_code", 0) != 0:
                errors.append(f"Command Failed: {last_cmd.get('command', 'Unknown')}\n{last_cmd.get('stderr', '')}")

        return errors


def create_error_recovery_agent(api_key: str, base_url: str = None) -> ErrorRecoveryAgent:
    """
    Factory function to create an error recovery agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured ErrorRecoveryAgent
    """
    model_kwargs = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return ErrorRecoveryAgent(model)

