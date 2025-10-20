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


TESTER_SYSTEM_PROMPT = """You are a Tester & Validator Agent in a multi-agent software development system.

Your role is to:
1. Validate code quality and correctness
2. Write comprehensive unit tests
3. Check syntax and style issues
4. Analyze code complexity
5. Provide constructive feedback for improvements

You have access to:
- File operation tools (read_file, write_file, edit_file, etc.)
- Task management tools (update task status, etc.)
- Code analysis tools:
  * analyze_python_syntax: Check Python syntax
  * count_functions: Count functions and classes
  * check_imports: List all imports
  * find_todos_in_code: Find TODO/FIXME comments
  * check_code_complexity: Analyze code complexity
  * validate_code_style: Check style issues

Testing Best Practices:
- Write clear, descriptive test names
- Test edge cases and error conditions
- Aim for good code coverage
- Use appropriate assertions
- Follow AAA pattern (Arrange, Act, Assert)
- Write both positive and negative tests

Validation Approach:
1. First, read the implemented code files
2. Use code analysis tools to check quality
3. Write appropriate tests
4. Provide a summary of findings
5. Update task status to completed

Be thorough but constructive in your feedback.
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
        all_tools = file_tools + task_tools + code_analysis_tools
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

Frontend implementation: {frontend_impl}

Backend implementation: {backend_impl}

Task: {task_content}

Please:
1. Read and analyze the implemented code
2. Use code analysis tools to validate quality
3. Write appropriate tests
4. Provide a comprehensive validation report
5. Update task status if applicable""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            frontend_impl=state.get("implementation_results", {}).get("frontend", "No frontend code"),
            backend_impl=state.get("implementation_results", {}).get("backend", "No backend code"),
            task_content=task_description
        )

        # Get response from model
        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 20
        iteration = 0
        all_tools = file_tools + task_tools + code_analysis_tools
        test_outputs = []

        while response.tool_calls and iteration < max_iterations:
            iteration += 1

            for tool_call in response.tool_calls:
                # Find the tool
                tool = next((t for t in all_tools if t.name == tool_call["name"]), None)

                if tool:
                    print(f"    🔧 Using tool: {tool.name}")
                    result = tool.invoke(tool_call["args"])
                    test_outputs.append({
                        "tool": tool.name,
                        "result": result
                    })

                    # Add tool response to messages
                    from langchain_core.messages import ToolMessage
                    messages_history.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    ))

            # Get next response
            response = self.model.invoke(messages_history)
            messages_history.append(response)

        print(f"\n✅ Testing and validation completed!")
        print(f"Summary: {response.content[:200]}...")

        return {
            "messages": messages_history,
            "next_agent": "orchestrator",  # Return to orchestrator
            "test_results": {
                "summary": response.content,
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
        "temperature": 0.1  # Lower temperature for more consistent validation
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return TesterAgent(model)
