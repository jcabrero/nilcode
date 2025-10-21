"""
Planner Agent - Analyzes user requests and creates task breakdowns.

This agent is responsible for:
1. Understanding the user's request
2. Breaking it down into actionable tasks
3. Identifying which agents should handle each task
4. Creating a structured plan
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.task_management import set_task_storage
from .utils import determine_next_agent


PLANNER_SYSTEM_PROMPT = """You are a Planning Agent in a multi-agent software development system.

Your role is to analyze user requests and create a structured task breakdown in JSON format.

You have access to these agent types (ONLY use these, no others):
- software_architect: Designs repository structure, scaffolding, and shared configuration
- dependency_manager: Creates package.json, pyproject.toml, .env.example, .gitignore, and all config files
- frontend_developer: Handles React, Vue, HTML, CSS, JavaScript, TypeScript, UI design
- backend_developer: Handles Python, Node.js, APIs, databases, server logic
- tester: Validates code, writes tests, checks quality

CRITICAL PLANNING REQUIREMENTS:
1. Identify all programming languages and frameworks mentioned or implied in the request
2. ALWAYS assign software_architect as the FIRST task to establish project structure
3. ALWAYS assign dependency_manager as the SECOND task to create package.json/pyproject.toml
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
      "content": "Create package.json with React/Vite dependencies and pyproject.toml with FastAPI dependencies",
      "activeForm": "Creating project configuration files",
      "assignedTo": "dependency_manager"
    }},
    {{
      "content": "Create login form UI component with username and password fields in React",
      "activeForm": "Creating login form UI",
      "assignedTo": "frontend_developer"
    }},
    {{
      "content": "Style the login form with CSS following modern design patterns",
      "activeForm": "Styling login form",
      "assignedTo": "frontend_developer"
    }},
    {{
      "content": "Create FastAPI authentication endpoint with JWT token generation",
      "activeForm": "Creating authentication API",
      "assignedTo": "backend_developer"
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

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the planner agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with plan and tasks
        """
        print("\n🔍 Planner Agent: Analyzing request and creating plan...")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT),
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
                task = {
                    "id": task_id,
                    "content": task_def.get("content", ""),
                    "status": "pending",
                    "activeForm": task_def.get("activeForm", ""),
                    "assignedTo": task_def.get("assignedTo", "unassigned"),
                    "result": ""
                }
                created_tasks.append(task)
                print(f"  📝 Task: {task['content']} → {task['assignedTo']}")

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
            "frontend_developer": "implementing",
            "backend_developer": "implementing",
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
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return PlannerAgent(model)
