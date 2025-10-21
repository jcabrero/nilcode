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
- frontend_developer: Handles React, Vue, HTML, CSS, JavaScript, TypeScript, UI design
- backend_developer: Handles Python, Node.js, APIs, databases, server logic
- tester: Validates code, writes tests, checks quality

IMPORTANT: You MUST respond with a JSON object in this exact format:

{{
  "tasks": [
    {{
      "content": "Task description in imperative form",
      "activeForm": "Task description in present continuous form",
      "assignedTo": "agent_type"
    }}
  ],
  "summary": "Brief summary of the plan"
}}

Example for "Create a login page with authentication":

{{
  "tasks": [
    {{
      "content": "Design project structure and required files",
      "activeForm": "Designing project structure",
      "assignedTo": "software_architect"
    }},
    {{
      "content": "Create login form UI with username and password fields",
      "activeForm": "Creating login form UI",
      "assignedTo": "frontend_developer"
    }},
    {{
      "content": "Style the login form with CSS",
      "activeForm": "Styling login form",
      "assignedTo": "frontend_developer"
    }},
    {{
      "content": "Create authentication API endpoint",
      "activeForm": "Creating authentication API",
      "assignedTo": "backend_developer"
    }},
    {{
      "content": "Write tests for authentication",
      "activeForm": "Writing authentication tests",
      "assignedTo": "tester"
    }}
  ],
  "summary": "Built a complete login system with frontend form, backend authentication, and tests"
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

        return {
            "plan": plan_summary,
            "tasks": created_tasks,
            "messages": [response],
            "next_agent": next_agent,
            "overall_status": overall_status,
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
