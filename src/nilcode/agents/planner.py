"""
Planner Agent - Analyzes user requests and creates task breakdowns.

This agent is responsible for:
1. Understanding the user's request
2. Breaking it down into actionable tasks
3. Identifying which agents should handle each task
4. Creating a structured plan
"""

from typing import Dict, Any, List
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.task_management import set_task_storage
from .utils import determine_next_agent

from ..prompts.claude import PROMPT
from ..a2a.registry import get_global_registry


PLANNER_SYSTEM_PROMPT = PROMPT.replace("{", "{{").replace("}", "}}") + """

You are an interactive CLI tool that helps users with software engineering tasks. Use the instructions below and the tools available to you to assist the user.

IMPORTANT: Assist with defensive security tasks only. Refuse to create, modify, or improve code that may be used maliciously. Do not assist with credential discovery or harvesting, including bulk crawling for SSH keys, browser cookies, or cryptocurrency wallets. Allow security analysis, detection rules, vulnerability explanations, defensive tools, and security documentation.
IMPORTANT: You must NEVER generate or guess URLs for the user unless you are confident that the URLs are for helping the user with programming. You may use URLs provided by the user in their messages or local files.

If the user asks for help or wants to give feedback inform them of the following: 
- /help: Get help with using nilCode Code
- To give feedback, users should report the issue at https://github.com/anthropics/nilCode-code/issues

When the user directly asks about nilCode Code (eg. "can nilCode Code do...", "does nilCode Code have..."), or asks in second person (eg. "are you able...", "can you do..."), or asks how to use a specific nilCode Code feature (eg. implement a hook, or write a slash command), use the WebFetch tool to gather information to answer the question from nilCode Code docs. The list of available docs is available at https://docs.nilCode.com/en/docs/nilCode-code/nilCode_code_docs_map.md.

## Tone and style
You should be concise, direct, and to the point, while providing complete information and matching the level of detail you provide in your response with the level of complexity of the user's query or the work you have completed. 
A concise response is generally less than 4 lines, not including tool calls or code generated. You should provide more detail when the task is complex or when the user asks you to.
IMPORTANT: You should minimize output tokens as much as possible while maintaining helpfulness, quality, and accuracy. Only address the specific task at hand, avoiding tangential information unless absolutely critical for completing the request. If you can answer in 1-3 sentences or a short paragraph, please do.
IMPORTANT: You should NOT answer with unnecessary preamble or postamble (such as explaining your code or summarizing your action), unless the user asks you to.
Do not add additional code explanation summary unless requested by the user. After working on a file, briefly confirm that you have completed the task, rather than providing an explanation of what you did.
Answer the user's question directly, avoiding any elaboration, explanation, introduction, conclusion, or excessive details. Brief answers are best, but be sure to provide complete information. You MUST avoid extra preamble before/after your response, such as "The answer is <answer>.", "Here is the content of the file..." or "Based on the information provided, the answer is..." or "Here is what I will do next...".

## Proactiveness
You are allowed to be proactive, but only when the user asks you to do something. You should strive to strike a balance between:
- Doing the right thing when asked, including taking actions and follow-up actions
- Not surprising the user with actions you take without asking
For example, if the user asks you how to approach something, you should do your best to answer their question first, and not immediately jump into taking actions.

## Professional objectivity
Prioritize technical accuracy and truthfulness over validating the user's beliefs. Focus on facts and problem-solving, providing direct, objective technical info without any unnecessary superlatives, praise, or emotional validation. It is best for the user if nilCode honestly applies the same rigorous standards to all ideas and disagrees when necessary, even if it may not be what the user wants to hear. Objective guidance and respectful correction are more valuable than false agreement. Whenever there is uncertainty, it's best to investigate to find the truth first rather than instinctively confirming the user's beliefs.

## Task Management
You have access to the TodoWrite tools to help you manage and plan tasks. Use these tools VERY frequently to ensure that you are tracking your tasks and giving the user visibility into your progress.
These tools are also EXTREMELY helpful for planning tasks, and for breaking down larger complex tasks into smaller steps. If you do not use this tool when planning, you may forget to do important tasks - and that is unacceptable.

It is critical that you mark todos as completed as soon as you are done with a task. Do not batch up multiple tasks before marking them as completed.

## Code References

When referencing specific functions or pieces of code include the pattern `file_path:line_number` to allow the user to easily navigate to the source code location.

You are a Planning Agent in a multi-agent software development system.

Your role is to analyze user requests and create a structured task breakdown in JSON format.

You have access to these agent types (ONLY use these, no others):
- software_architect: Designs repository structure, scaffolding, and shared configuration
- coder: Handles ALL implementation tasks including frontend, backend, and dependency management
- tester: Validates code, writes tests, checks quality

CRITICAL PLANNING REQUIREMENTS:
1. Identify all programming languages and frameworks mentioned or implied in the request
2. ALWAYS assign software_architect as the FIRST task to establish project structure
3. ALWAYS assign coder as the SECOND task to handle all implementation (frontend, backend, dependencies)
4. Ensure tasks follow a logical dependency order
5. Break down complex features into specific, testable tasks

IMPORTANT: You MUST respond with a JSON object in this exact format:

{{
  "languages": ["python", "javascript"],  // List all detected languages
  "frameworks": ["fastapi", "react"],     // List all frameworks/libraries
  "tasks": [
    {{
      "content": "Task description in imperative form",
      "activeForm": "Task description in present continuous form",
      "assignedTo": "agent_type"
    }}
  ],
  "summary": "Brief summary of the plan"
}}

Example for "Create a login page with authentication using React and FastAPI":

{{
  "languages": ["javascript", "python", "html", "css"],
  "frameworks": ["react", "fastapi"],
  "tasks": [
    {{
      "content": "Design project structure for React + FastAPI application with proper separation",
      "activeForm": "Designing project structure",
      "assignedTo": "software_architect"
    }},
    {{
      "content": "Create package.json with React/Vite dependencies, pyproject.toml with FastAPI dependencies, login form UI component, styling, and authentication API with JWT",
      "activeForm": "Implementing complete login system",
      "assignedTo": "coder"
    }},
    {{
      "content": "Write unit tests for both frontend component and backend authentication",
      "activeForm": "Writing authentication tests",
      "assignedTo": "tester"
    }}
  ],
  "summary": "Built a complete login system with React frontend, FastAPI backend authentication, and comprehensive tests"
}}

Always respond with valid JSON only. No additional text before or after the JSON.
"""


def _generate_task_requirements(task_content: str, assigned_agent: str) -> List[str]:
    """
    Generate requirements for a task based on its content and assigned agent.
    
    Args:
        task_content: Description of the task
        assigned_agent: Agent assigned to the task
        
    Returns:
        List of requirements for completing the task
    """
    requirements = []
    
    # Common requirements based on agent type
    if assigned_agent == "software_architect":
        requirements.extend([
            "Read and understand the user request",
            "Analyze existing codebase structure",
            "Design appropriate directory structure",
            "Create PROJECT_MANIFEST.md with architectural decisions",
            "Create .agent-guidelines/ directory with coding standards"
        ])
    elif assigned_agent == "coder":
        requirements.extend([
            "Read PROJECT_MANIFEST.md for architectural guidance",
            "Read .agent-guidelines/ for coding standards",
            "Implement code following established patterns",
            "Validate syntax using appropriate validation tools",
            "Verify files are actually created and contain expected content"
        ])
    elif assigned_agent == "tester":
        requirements.extend([
            "Read all created/modified files",
            "Validate syntax of all code files",
            "Write comprehensive unit tests",
            "Verify test coverage and quality",
            "Report any issues found"
        ])
    
    # Task-specific requirements based on content
    content_lower = task_content.lower()
    
    if "package.json" in content_lower or "dependencies" in content_lower:
        requirements.append("Create package.json with all necessary dependencies")
    
    if "pyproject.toml" in content_lower or "python" in content_lower:
        requirements.append("Create pyproject.toml with Python dependencies")
    
    if "react" in content_lower or "component" in content_lower:
        requirements.extend([
            "Create React components with proper JSX syntax",
            "Implement proper state management",
            "Add appropriate styling"
        ])
    
    if "api" in content_lower or "backend" in content_lower:
        requirements.extend([
            "Implement API endpoints with proper error handling",
            "Add input validation and sanitization",
            "Include proper HTTP status codes"
        ])
    
    if "test" in content_lower:
        requirements.extend([
            "Write unit tests for all functions",
            "Test edge cases and error conditions",
            "Ensure adequate test coverage"
        ])
    
    return requirements


def _estimate_task_effort(task_content: str) -> str:
    """
    Estimate the effort required for a task based on its content.
    
    Args:
        task_content: Description of the task
        
    Returns:
        Effort level: "low", "medium", or "high"
    """
    content_lower = task_content.lower()
    
    # High effort indicators
    high_effort_keywords = [
        "complete", "full", "entire", "comprehensive", "all", "multiple",
        "authentication", "database", "api", "backend", "frontend",
        "complex", "advanced", "integration", "deployment"
    ]
    
    # Low effort indicators
    low_effort_keywords = [
        "simple", "basic", "single", "one", "create", "add", "fix",
        "update", "modify", "small", "quick"
    ]
    
    high_count = sum(1 for keyword in high_effort_keywords if keyword in content_lower)
    low_count = sum(1 for keyword in low_effort_keywords if keyword in content_lower)
    
    if high_count >= 2 or len(task_content.split()) > 20:
        return "high"
    elif low_count >= 2 or len(task_content.split()) < 8:
        return "low"
    else:
        return "medium"


class PlannerAgent:
    """
    Planner agent that analyzes requests and creates task plans.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Planner agent.

        Args:
            model: Language model to use
        """
        self.model = model  # Don't bind tools, we'll use JSON parsing
        self.name = "planner"

    def _get_external_agents_info(self) -> List[Dict[str, Any]]:
        """
        Get information about available external A2A agents.

        Returns:
            List of external agent information dictionaries
        """
        try:
            # Get the global registry (synchronous wrapper for async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            registry = loop.run_until_complete(get_global_registry())
            external_agents = registry.get_all_agent_summaries()
            loop.close()
            return external_agents
        except Exception as e:
            print(f"  ⚠️  Warning: Could not fetch external agents: {e}")
            return []

    def _build_system_prompt_with_external_agents(self, external_agents: List[Dict[str, Any]]) -> str:
        """
        Build system prompt including external agents.

        Args:
            external_agents: List of external agent information

        Returns:
            Updated system prompt
        """
        base_prompt = PLANNER_SYSTEM_PROMPT

        if external_agents:
            # Build external agents section
            external_agents_section = "\n\nADDITIONAL EXTERNAL AGENTS AVAILABLE VIA A2A PROTOCOL:\n"
            for agent in external_agents:
                agent_name = agent.get('name', 'unknown')
                description = agent.get('description', 'No description')
                capabilities = agent.get('capabilities', [])

                external_agents_section += f"\n- {agent_name}: {description}\n"
                if capabilities:
                    external_agents_section += f"  Capabilities: {', '.join(capabilities[:3])}\n"

            external_agents_section += "\nYou can assign tasks to these external agents using their exact names.\n"

            # Insert before the agent types section
            base_prompt = base_prompt.replace(
                "You have access to these agent types (ONLY use these, no others):",
                f"{external_agents_section}\nYou have access to these agent types:"
            )

            print(f"  🌐 Discovered {len(external_agents)} external A2A agents")

        return base_prompt

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the planner agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with plan and tasks
        """
        print("\n🔍 Planner Agent: Analyzing request and creating plan...")

        # Get external agents from A2A registry
        external_agents_info = self._get_external_agents_info()

        # Build dynamic system prompt with external agents
        system_prompt = self._build_system_prompt_with_external_agents(external_agents_info)

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User request: {user_request}\n\nCreate a JSON task plan.")
        ])

        # Format the prompt with user request
        messages = prompt.format_messages(user_request=state["user_request"])

        # Get response from model
        response = self.model.invoke(messages)

        # Parse JSON response
        import json
        import uuid
        import re

        created_tasks = []
        plan_summary = ""
        detected_languages = []
        detected_frameworks = []

        try:
            # Extract JSON from response (handle markdown code blocks)
            content = response.content.strip()

            # Remove markdown code blocks if present
            if "```json" in content:
                content = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL).group(1)
            elif "```" in content:
                content = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL).group(1)

            # Parse JSON
            plan_data = json.loads(content)

            # Extract languages and frameworks
            detected_languages = plan_data.get("languages", [])
            detected_frameworks = plan_data.get("frameworks", [])

            print(f"  🔍 Detected languages: {', '.join(detected_languages) if detected_languages else 'None specified'}")
            print(f"  🔧 Detected frameworks: {', '.join(detected_frameworks) if detected_frameworks else 'None specified'}")

            # Extract tasks
            for task_def in plan_data.get("tasks", []):
                task_id = str(uuid.uuid4())[:8]
                
                # Generate requirements based on task content and assigned agent
                requirements = _generate_task_requirements(task_def.get("content", ""), task_def.get("assignedTo", ""))
                
                # Estimate effort based on task complexity
                estimated_effort = _estimate_task_effort(task_def.get("content", ""))
                
                task = {
                    "id": task_id,
                    "content": task_def.get("content", ""),
                    "status": "pending",
                    "activeForm": task_def.get("activeForm", ""),
                    "assignedTo": task_def.get("assignedTo", "unassigned"),
                    "result": "",
                    # Enhanced task tracking
                    "requirements": requirements,
                    "progress": "Not started",
                    "files_created": [],
                    "files_modified": [],
                    "dependencies": [],
                    "retry_count": 0,
                    "last_error": "",
                    "estimated_effort": estimated_effort,
                    "actual_effort": "not_started"
                }
                created_tasks.append(task)
                print(f"  📝 Task: {task['content']} → {task['assignedTo']} (effort: {estimated_effort})")

            plan_summary = plan_data.get("summary", "Plan created")

        except Exception as e:
            print(f"  ⚠️  Error parsing JSON: {e}")
            print(f"  Response: {response.content[:200]}")
            plan_summary = response.content

        print(f"\n✅ Plan created successfully!")
        print(f"   Created {len(created_tasks)} tasks")

        # Synchronize task tool storage with the generated tasks
        set_task_storage(created_tasks)

        # Update state with tasks
        next_agent = determine_next_agent(created_tasks) if created_tasks else "tester"

        status_mapping = {
            "software_architect": "architecting",
            "coder": "implementing",
            "tester": "testing",
        }

        overall_status = status_mapping.get(next_agent, "planning")

        # Categorize technologies
        frontend_techs = []
        backend_techs = []

        for lang in detected_languages:
            if lang.lower() in ["javascript", "typescript", "html", "css"]:
                frontend_techs.append(lang.lower())
            elif lang.lower() in ["python", "java", "go", "rust", "ruby", "php", "csharp", "c#"]:
                backend_techs.append(lang.lower())

        for framework in detected_frameworks:
            fw_lower = framework.lower()
            if fw_lower in ["react", "vue", "angular", "svelte", "nextjs", "nuxt"]:
                frontend_techs.append(fw_lower)
            elif fw_lower in ["fastapi", "flask", "django", "express", "nestjs", "spring", "rails"]:
                backend_techs.append(fw_lower)

        return {
            "plan": plan_summary,
            "tasks": created_tasks,
            "messages": [response],
            "next_agent": next_agent,
            "overall_status": overall_status,
            "detected_languages": detected_languages,
            "frontend_tech": list(set(frontend_techs)),
            "backend_tech": list(set(backend_techs)),
        }


def create_planner_agent(api_key: str, base_url: str = None) -> PlannerAgent:
    """
    Factory function to create a planner agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured PlannerAgent
    """
    model_kwargs = {
        "model": "meta-llama/llama-4-maverick:free",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return PlannerAgent(model)
