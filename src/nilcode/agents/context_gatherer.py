"""
Context Gatherer Agent - Analyzes existing codebases and gathers relevant context.

This agent is responsible for:
1. Understanding the existing project structure
2. Identifying relevant files for a task
3. Reading and analyzing code to provide context
4. Building a semantic understanding of the codebase
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.codebase_tools import codebase_tools
from ..tools.git_tools import git_tools
from .utils import determine_next_agent


CONTEXT_GATHERER_SYSTEM_PROMPT = """You are a Context Gatherer Agent in a multi-agent software development system.

Your role is to:
1. Analyze existing codebases to understand their structure and organization
2. Identify which files are relevant to the current task
3. Read and summarize key code files
4. Build context about dependencies, imports, and relationships
5. Provide this context to other agents so they can work more effectively

You have access to powerful tools:
- analyze_project_structure: Get overview of project organization
- find_definition: Find where functions/classes are defined
- find_usages: See where code is used
- list_files_recursively: List files matching patterns
- search_code_content: Search for specific code patterns
- read_file: Read file contents
- git_status: Check what files have changed
- git_diff: See what modifications were made

Your Process:
1. Start with analyze_project_structure to understand the overall project
2. Use search and find tools to locate relevant code
3. Read key files that are relevant to the current task
4. Summarize findings in a clear, actionable way
5. Identify files that need to be read or modified

Best Practices:
- Focus on files relevant to the current task
- Don't read entire large files - use search tools first
- Identify dependencies and imports
- Note any patterns or conventions used in the codebase
- Flag potential issues or conflicts
- Be selective - don't gather too much irrelevant context

When you finish gathering context:
1. Summarize what you found
2. List relevant files for the task
3. Note any important patterns or conventions
4. Identify potential challenges or conflicts
"""


class ContextGathererAgent:
    """
    Context gatherer agent that analyzes codebases and gathers relevant information.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Context Gatherer agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + codebase_tools + git_tools
        self.model = model.bind_tools(all_tools)
        self.name = "context_gatherer"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the context gatherer agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with gathered context
        """
        print("\n🔍 Context Gatherer Agent: Analyzing codebase...")

        tasks = state.get("tasks", [])
        user_request = state["user_request"]
        
        # Check if we need context gathering
        need_context = self._should_gather_context(state)
        
        if not need_context:
            print("  No context gathering needed, moving to next agent...")
            next_agent = determine_next_agent(tasks)
            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
            }

        # Get tasks relevant to context gathering
        current_tasks = [
            task for task in tasks
            if task.get("assignedTo") in ["frontend_developer", "backend_developer", "software_architect"]
            and task.get("status") == "pending"
        ]

        if not current_tasks:
            print("  No tasks requiring context, moving to next agent...")
            next_agent = determine_next_agent(tasks)
            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
            }

        # Build context about what we need to do
        task_summary = "\n".join([f"- {t['content']}" for t in current_tasks[:5]])

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", CONTEXT_GATHERER_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Upcoming tasks:
{task_summary}

Please analyze the codebase and gather relevant context for these tasks:
1. Use analyze_project_structure to understand the project
2. Search for relevant files and code
3. Read key files that will be modified or that provide context
4. Check git status to see what's already been changed
5. Summarize your findings

Focus on gathering context that will help the developer agents complete their tasks effectively.""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=user_request,
            task_summary=task_summary
        )

        # Get response from model
        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 20  # More iterations for context gathering
        iteration = 0
        all_tools = file_tools + codebase_tools + git_tools
        gathered_context = []

        while response.tool_calls and iteration < max_iterations:
            iteration += 1

            for tool_call in response.tool_calls:
                # Find the tool
                tool = next((t for t in all_tools if t.name == tool_call["name"]), None)

                if tool:
                    print(f"    🔧 Using tool: {tool.name}")
                    result = tool.invoke(tool_call["args"])
                    gathered_context.append(f"[{tool.name}] {result}")

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
        print("    📝 Generating context summary...")
        from langchain_core.messages import HumanMessage
        messages_history.append(HumanMessage(
            content="Please provide a comprehensive summary of the context you gathered, including: 1) Project structure and organization, 2) Relevant files for the upcoming tasks, 3) Key patterns and conventions, 4) Any important dependencies or relationships, 5) Potential challenges or conflicts to watch out for."
        ))
        response = self.model.invoke(messages_history)
        messages_history.append(response)

        print(f"\n✅ Context gathered successfully!")
        summary = response.content if response.content else "Context analysis completed"
        print(f"Summary: {summary[:200]}..." if len(summary) > 200 else f"Summary: {summary}")

        # Store gathered context in state
        context_data = {
            "summary": summary,
            "detailed_context": "\n\n".join(gathered_context[:10]),  # Store top 10 results
            "analysis_complete": True
        }

        next_agent = determine_next_agent(tasks)

        return {
            "messages": messages_history,
            "next_agent": next_agent,
            "codebase_context": context_data,
        }

    def _should_gather_context(self, state: AgentState) -> bool:
        """
        Determine if context gathering is needed.
        
        Args:
            state: Current agent state
            
        Returns:
            True if context should be gathered
        """
        # Check if we've already gathered context
        if state.get("codebase_context", {}).get("analysis_complete"):
            return False
        
        # Check if there are existing project files to analyze
        # (If this is a brand new project, we don't need context gathering)
        import os
        from pathlib import Path
        
        # Check if there are Python, JS, or TS files in the current directory
        current_dir = Path(".")
        has_code_files = (
            any(current_dir.rglob("*.py")) or
            any(current_dir.rglob("*.js")) or
            any(current_dir.rglob("*.ts"))
        )
        
        return has_code_files


def create_context_gatherer_agent(api_key: str, base_url: str = None) -> ContextGathererAgent:
    """
    Factory function to create a context gatherer agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured ContextGathererAgent
    """
    model_kwargs = {
        "model": "openai/gpt-oss-20b:free",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return ContextGathererAgent(model)

