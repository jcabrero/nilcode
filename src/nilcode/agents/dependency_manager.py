"""
Dependency Manager Agent - Creates project configuration and dependency files.

This agent is responsible for:
1. Creating package.json for JavaScript/TypeScript/Node.js projects
2. Creating pyproject.toml or requirements.txt for Python projects
3. Creating .env.example with environment variable placeholders
4. Creating .gitignore appropriate for the language/framework
5. Creating framework-specific config files (tsconfig.json, next.config.js, etc.)
6. Ensuring all dependencies are properly specified
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.task_management import task_tools, set_task_storage
from .utils import determine_next_agent


DEPENDENCY_MANAGER_SYSTEM_PROMPT = """You are a Dependency Manager Agent in a multi-agent software development system.

Your role is to create ALL project configuration and dependency files needed for the project to be runnable.

CRITICAL RESPONSIBILITIES:

1. **Read Project Context First**:
   - Read PROJECT_MANIFEST.md to understand the tech stack
   - Check detected_languages and frameworks from the context
   - Use list_files to see what already exists

2. **For JavaScript/TypeScript/Node.js Projects**:
   Create these files:
   - `package.json` with ALL required dependencies:
     * React projects: react, react-dom, react-scripts OR vite
     * Next.js projects: next, react, react-dom
     * Vue projects: vue, @vitejs/plugin-vue
     * Express projects: express, cors, dotenv
     * TypeScript: typescript, @types/node, @types/react (if React)
   - `tsconfig.json` if TypeScript is detected
   - `next.config.js` if Next.js is detected
   - `vite.config.js` or `vite.config.ts` if using Vite
   - `.env.example` with API_KEY, DATABASE_URL, etc.
   - `.gitignore` for Node.js projects
   - Add scripts: `dev`, `build`, `start`, `test`, `lint`

3. **For Python Projects**:
   Create these files:
   - `pyproject.toml` (modern, preferred) with dependencies:
     * FastAPI projects: fastapi, uvicorn, pydantic
     * Flask projects: flask, flask-cors
     * Django projects: django, djangorestframework
     * Always include: python-dotenv, pytest (dev)
   - OR `requirements.txt` if legacy project
   - `.env.example` with environment variables
   - `.gitignore` for Python projects

4. **For All Projects**:
   - `README.md` with:
     * Project description
     * Installation instructions (`npm install` or `pip install`)
     * How to run (`npm run dev` or `python main.py`)
     * Environment variable setup
   - `.gitignore` appropriate for the languages used
   - `.env.example` with ALL required environment variables

DEPENDENCY VERSION GUIDELINES:
- Use latest stable versions when possible
- For React: "^18.2.0" or latest
- For Next.js: "^14.0.0" or latest
- For TypeScript: "^5.0.0" or latest
- For Python packages: Use version ranges like ">=1.0.0,<2.0.0"

PACKAGE.JSON TEMPLATE (React + TypeScript + Vite):
```json
{{
  "name": "project-name",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "test": "vitest"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "eslint": "^8.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }}
}}
```

PACKAGE.JSON TEMPLATE (Next.js + TypeScript):
```json
{{
  "name": "project-name",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  }},
  "dependencies": {{
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "typescript": "^5.0.0"
  }}
}}
```

PYPROJECT.TOML TEMPLATE (FastAPI):
```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Description here"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
```

.ENV.EXAMPLE TEMPLATE:
```
# API Keys
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# App Configuration
PORT=3000
NODE_ENV=development
```

.GITIGNORE TEMPLATE (Node.js):
```
node_modules/
.env
.env.local
dist/
build/
*.log
.DS_Store
coverage/
```

.GITIGNORE TEMPLATE (Python):
```
__pycache__/
*.py[cod]
*$py.class
.env
venv/
.venv/
*.so
.pytest_cache/
.mypy_cache/
```

WORKFLOW:
1. Use list_files to check what exists
2. Read PROJECT_MANIFEST.md
3. Based on detected languages/frameworks, create appropriate config files
4. Use write_file to create each configuration file
5. Update task status to "completed"
6. Provide summary of files created

IMPORTANT:
- Always include COMPLETE dependency lists, not placeholders
- Include both runtime AND development dependencies
- Add helpful comments in config files
- Ensure JSON is valid (no trailing commas)
- Include installation and run instructions in README
"""


class DependencyManagerAgent:
    """
    Dependency manager agent that creates project configuration files.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Dependency Manager agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + task_tools
        self.model = model.bind_tools(all_tools)
        self.name = "dependency_manager"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the dependency manager agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with configuration files created
        """
        print("\n📦 Dependency Manager Agent: Creating project configuration files...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        # Get dependency manager specific tasks
        dep_manager_tasks = [
            task for task in tasks
            if task.get("assignedTo") == "dependency_manager"
            and task.get("status") in ["pending", "in_progress"]
        ]

        if not dep_manager_tasks:
            print("  No dependency manager tasks found, moving to next agent...")
            next_agent = determine_next_agent(tasks)
            status = "implementing" if next_agent in {
                "frontend_developer",
                "backend_developer",
            } else ("testing" if next_agent == "tester" else "architecting")

            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
                "overall_status": status,
            }

        # Work on the first pending task
        current_task = dep_manager_tasks[0]
        print(f"  📋 Working on: {current_task['content']}")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", DEPENDENCY_MANAGER_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current plan: {plan}

Detected languages: {languages}
Frontend technologies: {frontend_tech}
Backend technologies: {backend_tech}

Project manifest location: {manifest_path}
Working directory: {working_dir}

Current task: {task_content}

CRITICAL INSTRUCTIONS:
1. FIRST: Read {manifest_path} to understand the full tech stack
2. SECOND: Create package.json OR pyproject.toml based on detected languages
3. THIRD: Include ALL dependencies for the frameworks detected
4. FOURTH: Create .env.example with environment variable templates
5. FIFTH: Create .gitignore for the project languages
6. SIXTH: Create README.md with setup instructions

For example, if Next.js + TypeScript is detected:
- Create package.json with next, react, react-dom, typescript, and all @types packages
- Create tsconfig.json with Next.js compatible settings
- Create next.config.js
- Create .env.example with common Next.js env vars
- Create .gitignore for Node.js

Make sure to include COMPLETE, RUNNABLE configuration files!""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            languages=", ".join(state.get("detected_languages", [])) or "Not specified",
            frontend_tech=", ".join(state.get("frontend_tech", [])) or "None",
            backend_tech=", ".join(state.get("backend_tech", [])) or "None",
            manifest_path=state.get("project_manifest_path", "PROJECT_MANIFEST.md"),
            working_dir=state.get("working_directory", "."),
            task_content=current_task["content"],
        )

        # Get response from model
        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 20
        iteration = 0
        all_tools = file_tools + task_tools
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
                    if not tool:
                        print(f"    ⚠️ Tool '{tool_name}' not found")
                        continue

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

        # Generate final summary
        try:
            if not response.content or len(response.content.strip()) < 50:
                print("    📝 Generating final summary...")
                from langchain_core.messages import HumanMessage
                messages_history.append(HumanMessage(
                    content="Please provide a comprehensive summary of what configuration files you created, including package.json/pyproject.toml and what dependencies you included."
                ))
                response = self.model.invoke(messages_history)
                messages_history.append(response)

            print(f"\n✅ Dependency management task completed!")
            summary = response.content if hasattr(response, 'content') and response.content else "Task completed"
            print(f"Summary: {summary[:150]}..." if len(summary) > 150 else f"Summary: {summary}")
        except Exception as e:
            print(f"\n⚠️ Warning: Error generating summary: {e}")
            summary = "Configuration files created (summary generation failed)"

        # Mark the current task as completed
        updated_tasks = []
        for task in tasks:
            if task["id"] == current_task["id"]:
                task = {**task, "status": "completed", "result": summary}
            updated_tasks.append(task)

        set_task_storage(updated_tasks)

        # Check if there are more dependency manager tasks
        next_agent = determine_next_agent(updated_tasks, prefer_agent="dependency_manager")
        status = "implementing" if next_agent in {
            "frontend_developer",
            "backend_developer",
        } else ("testing" if next_agent == "tester" else "architecting")

        return {
            "messages": messages_history,
            "tasks": updated_tasks,
            "next_agent": next_agent,
            "overall_status": status,
            "implementation_results": {
                **state.get("implementation_results", {}),
                "dependencies": summary
            },
        }


def create_dependency_manager_agent(api_key: str, base_url: str = None) -> DependencyManagerAgent:
    """
    Factory function to create a dependency manager agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured DependencyManagerAgent
    """
    model_kwargs: Dict[str, Any] = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return DependencyManagerAgent(model)
