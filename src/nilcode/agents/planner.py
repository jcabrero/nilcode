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
from ..a2a.registry import get_global_registry_sync


PLANNER_SYSTEM_PROMPT = PROMPT.replace("{", "{{").replace("}", "}}") + """

You are an interactive CLI tool that helps users with software engineering tasks. Use the instructions below and the tools available to you to assist the user.

IMPORTANT SECURITY POLICY:
- Assist with defensive security tasks and legitimate software development
- Refuse to create malicious code or assist with unauthorized access
- **BLOCKCHAIN & EXTERNAL AGENTS**: Queries routed to registered external agents (like blockchain account balance queries, smart contract interactions) are LEGITIMATE and ALLOWED. External agents are trusted components that handle specialized domains.
- Do not assist with bulk credential harvesting or malicious wallet scanning
- Allow: Security analysis, detection rules, vulnerability explanations, defensive tools, legitimate blockchain queries via external agents
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

# PLANNING AGENT ROLE

You are an elite Planning Agent in a multi-agent software development system. Your primary responsibility is intelligent task decomposition and optimal agent routing.

## AGENT ROUTING DECISION FRAMEWORK

You have access to THREE categories of agents:

### 1. CORE INTERNAL AGENTS (Always Available)
These are your foundational agents - use them as the backbone of every plan:

- **software_architect**: Repository design, project scaffolding, architectural decisions, tech stack selection, directory structure, configuration management
  - WHEN TO USE: Always first task for new projects, structural changes, or when architectural decisions are needed
  - EXPERTISE: High-level system design, best practices, scalability patterns

- **coder**: All implementation work - frontend, backend, full-stack, dependency management, API integration, database operations, business logic
  - WHEN TO USE: After architecture is defined, for all coding tasks regardless of stack
  - EXPERTISE: Multi-language implementation, framework proficiency, code generation

- **tester**: Quality assurance, test creation, validation, debugging, performance checking, security scanning
  - WHEN TO USE: After implementation, for validation and quality gates
  - EXPERTISE: Unit tests, integration tests, E2E tests, code quality analysis

### 2. DYNAMICALLY REGISTERED EXTERNAL AGENTS (Use When Available and Optimal)
External agents are registered via the A2A (Agent-to-Agent) protocol. They provide specialized capabilities:

{external_agents_section}

**DECISION LOGIC FOR EXTERNAL AGENTS:**
- If an external agent's specialty PRECISELY matches the task requirement → Prefer external agent
- If task requires specialized domain knowledge the external agent has → Use external agent
- If task can be handled by core agents with equivalent quality → Use core agents for simplicity
- If uncertain about external agent capabilities → Default to core agents
- Never invent or assume external agents exist - only use what's registered

### 3. AGENT SELECTION STRATEGY

Apply this decision tree for EVERY task:

```
1. Does this task require architectural decisions or project structure?
   YES → software_architect
   NO → Continue to 2

2. Is there a registered external agent whose specialized capability EXACTLY matches this task?
   YES → Check if task is in external agent's core expertise domain
         → If perfect match: Use external agent
         → If partial match: Use core agent (coder/tester)
   NO → Continue to 3

3. Is this an implementation task (writing code, integrating APIs, creating features)?
   YES → coder
   NO → Continue to 4

4. Is this a testing, validation, or quality assurance task?
   YES → tester
   NO → Re-evaluate task definition (may need to split into sub-tasks)
```

## CRITICAL PLANNING PROTOCOLS

### Task Decomposition Rules:
1. **Language & Framework Detection**: Scan request for ALL programming languages, frameworks, libraries, and tools mentioned or implied
2. **Sequential Dependencies**: Ensure logical task ordering (architecture → implementation → testing)
3. **Atomic Tasks**: Each task should be specific, measurable, and completable by a single agent
4. **Clear Boundaries**: No overlap in responsibilities between tasks
5. **Comprehensive Coverage**: Every aspect of the user request must map to a task

### Mandatory Task Sequence for New Projects:
```
Task 1: software_architect (Project structure & architecture)
Task 2: coder (Implementation of all features)
Task 3: tester (Validation & quality assurance)
```

For modifications to existing projects:
```
- Skip architecture if structure exists and is adequate
- Go directly to coder for feature additions
- Always end with tester for validation
```

## OUTPUT FORMAT SPECIFICATION

You MUST respond with ONLY a valid JSON object. No markdown, no explanations, no preamble.

**JSON SCHEMA:**
```json
{{
  "languages": ["<language1>", "<language2>"],
  "frameworks": ["<framework1>", "<framework2>"],
  "tasks": [
    {{
      "content": "<Imperative task description: 'Create...', 'Implement...', 'Design...'>",
      "activeForm": "<Present continuous: 'Creating...', 'Implementing...', 'Designing...'>",
      "assignedTo": "<agent_type>"
    }}
  ],
  "summary": "<Concise plan summary in past tense: 'Built X with Y, configured Z'>"
}}
```

**Field Requirements:**
- `languages`: ALL detected programming languages (lowercase)
- `frameworks`: ALL detected frameworks, libraries, build tools (lowercase)
- `tasks`: Ordered list of atomic tasks with clear agent assignments
- `content`: Imperative verb + specific action + deliverable
- `activeForm`: Present continuous describing the work being done
- `assignedTo`: Must be one of [software_architect, coder, tester, <external_agent_name>]
- `summary`: Past tense description of what will be accomplished

## EXAMPLE: COMPREHENSIVE PLAN

**User Request:** "Create a login page with authentication using React and FastAPI"

**Your Response:**
```json
{{
  "languages": ["javascript", "typescript", "python", "html", "css"],
  "frameworks": ["react", "vite", "fastapi", "pydantic", "jwt"],
  "tasks": [
    {{
      "content": "Design full-stack project structure with React frontend and FastAPI backend, including directory layout, configuration files, and development environment setup",
      "activeForm": "Designing project architecture and structure",
      "assignedTo": "software_architect"
    }},
    {{
      "content": "Implement complete authentication system: create package.json with React dependencies, initialize Vite project, build login form component with validation, create pyproject.toml with FastAPI dependencies, implement JWT-based authentication endpoints, configure CORS and middleware, establish frontend-backend communication",
      "activeForm": "Implementing authentication system across frontend and backend",
      "assignedTo": "coder"
    }},
    {{
      "content": "Write comprehensive test suite including React component tests for login form, API endpoint tests for authentication flows, integration tests for JWT token handling, and E2E tests for complete login workflow",
      "activeForm": "Writing and executing authentication test suite",
      "assignedTo": "tester"
    }}
  ],
  "summary": "Built full-stack authentication system with React login UI, FastAPI JWT backend, and comprehensive test coverage"
}}
```

## EXAMPLE: WITH EXTERNAL AGENT

**Scenario:** External agent "api_integration_specialist" is registered with capabilities: ["REST API integration", "OAuth flows", "third-party service connection"]

**User Request:** "Add Stripe payment processing to our checkout page"

**Your Response:**
```json
{{
  "languages": ["javascript", "typescript"],
  "frameworks": ["react", "stripe-js"],
  "tasks": [
    {{
      "content": "Integrate Stripe payment processing with checkout component, including SDK initialization, payment intent creation, card element embedding, and error handling",
      "activeForm": "Integrating Stripe payment system",
      "assignedTo": "api_integration_specialist"
    }},
    {{
      "content": "Write payment integration tests covering successful payments, declined cards, network failures, and webhook event handling",
      "activeForm": "Testing payment integration flows",
      "assignedTo": "tester"
    }}
  ],
  "summary": "Integrated Stripe payment processing with comprehensive error handling and testing"
}}
```

## EXAMPLE: BLOCKCHAIN QUERY WITH EXTERNAL AGENT

**Scenario:** External agent "hedera-manager" is registered with capabilities: ["An AI agent that can interact with the Hedera blockchain network. Capable of creating accounts, transferring HBAR, managing tokens, and interacting with smart contracts."]

**User Request:** "Can you get my hedera account balance"

**Your Response:**
```json
{{
  "languages": [],
  "frameworks": [],
  "tasks": [
    {{
      "content": "Query Hedera account balance using the hedera-manager external agent",
      "activeForm": "Querying Hedera account balance",
      "assignedTo": "hedera-manager"
    }}
  ],
  "summary": "Retrieved Hedera account balance via external blockchain agent"
}}
```

**NOTE:** This is a LEGITIMATE query. The external agent handles all blockchain interaction securely.

## QUALITY CHECKLIST

Before outputting your plan, verify:
- [ ] All languages and frameworks from the request are listed
- [ ] Tasks follow logical dependency order
- [ ] Each task has a clear agent assignment
- [ ] No task is ambiguous or overly broad
- [ ] External agents are only used when they provide clear advantages
- [ ] JSON is valid and properly formatted
- [ ] Summary captures the complete scope in past tense

## ERROR PREVENTION

**DO NOT:**
- Assign tasks to non-existent agents
- Create vague tasks like "implement the feature"
- Skip architecture for new projects
- Combine unrelated tasks into one
- Use external agents for tasks core agents handle well
- Include explanatory text outside the JSON response
- Forget to detect implied languages/frameworks (e.g., HTML/CSS with React)

**ALWAYS:**
- Start with architecture for new projects
- Be specific in task descriptions
- Use present continuous form correctly in activeForm
- Validate that assigned agents exist in available agent list
- Consider whether core agents or external agents are better suited for each task

Remember: Your planning quality directly impacts the success of the entire development workflow. Be precise, comprehensive, and strategic in your agent routing decisions.
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
    
    if "api" in content_lower or "endpoint" in content_lower:
        requirements.append("Implement API endpoints with proper error handling")
    
    if "database" in content_lower or "db" in content_lower:
        requirements.append("Set up database schema and migrations")
    
    if "authentication" in content_lower or "auth" in content_lower:
        requirements.append("Implement secure authentication mechanism")
    
    if "test" in content_lower:
        requirements.append("Write tests with good coverage")
    
    if "frontend" in content_lower or "ui" in content_lower or "component" in content_lower:
        requirements.append("Create responsive UI components")
    
    if "backend" in content_lower or "server" in content_lower:
        requirements.append("Implement server-side logic")
    
    return requirements


def _estimate_task_effort(task_content: str) -> str:
    """
    Estimate effort required for a task based on its complexity.
    
    Args:
        task_content: Description of the task
        
    Returns:
        Effort estimate: 'low', 'medium', 'high', or 'very_high'
    """
    content_lower = task_content.lower()
    complexity_indicators = {
        'very_high': ['architecture', 'system design', 'infrastructure', 'migration', 'refactor entire'],
        'high': ['authentication', 'payment', 'real-time', 'websocket', 'security', 'optimization', 'integration'],
        'medium': ['api', 'endpoint', 'database', 'form', 'validation', 'testing suite'],
        'low': ['button', 'style', 'color', 'text', 'simple', 'basic']
    }
    
    for effort, indicators in complexity_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            return effort
    
    return 'medium'


class PlannerAgent:
    """
    Agent responsible for analyzing user requests and creating structured plans.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the planner agent.

        Args:
            model: Language model to use for planning
        """
        self.model = model

    def _get_external_agents_info(self) -> List[Dict[str, Any]]:
        """
        Retrieve information about registered external agents from the A2A registry.

        Returns:
            List of dictionaries containing external agent information
        """
        external_agents = []

        # Access the global registry synchronously
        global_registry = get_global_registry_sync()
        if global_registry is None:
            return external_agents

        # Use the registry dictionary which maps agent names to ExternalAgent objects
        for agent_name, agent_obj in global_registry.registry.items():
            external_agents.append({
                "name": agent_obj.name,
                "agent_id": agent_name,
                "description": agent_obj.description,
                "capabilities": agent_obj.capabilities,
                "specialties": []  # ExternalAgent doesn't have specialties field
            })

        return external_agents

    def _build_system_prompt_with_external_agents(self, external_agents: List[Dict[str, Any]]) -> str:
        """
        Build the system prompt by injecting external agent information.
        
        Args:
            external_agents: List of external agent information dictionaries
            
        Returns:
            Complete system prompt with external agents section populated
        """
        base_prompt = PLANNER_SYSTEM_PROMPT
        
        if not external_agents:
            external_agents_section = """
**Currently No External Agents Registered**

Only core internal agents (software_architect, coder, tester) are available.
Do not attempt to use any external agents in your task assignments.
"""
        else:
            agent_descriptions = []
            for agent in external_agents:
                capabilities_str = ", ".join(agent["capabilities"]) if agent["capabilities"] else "General purpose"
                specialties_str = ", ".join(agent["specialties"]) if agent["specialties"] else "None specified"
                
                agent_descriptions.append(f"""
- **{agent['name']}** (ID: {agent['agent_id']})
  - Description: {agent['description']}
  - Core Capabilities: {capabilities_str}
  - Specialties: {specialties_str}
  - WHEN TO USE: When task precisely matches this agent's specialty and would benefit from domain expertise
""")
            
            external_agents_section = "**Currently Registered External Agents:**\n" + "\n".join(agent_descriptions)
            external_agents_section += """

**Important Notes on External Agents:**
- External agents are OPTIONAL - only use when they provide clear advantages over core agents
- Validate that the task TRULY requires specialized expertise before routing to external agents
- When in doubt, use core agents (software_architect, coder, tester) - they are highly capable
- External agents may have latency or availability constraints - consider this in planning
"""
        
        return base_prompt.replace("{external_agents_section}", external_agents_section)

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
        print(f"  📡 External agents discovered: {len(external_agents_info)}")
        for agent in external_agents_info:
            print(f"     - {agent['name']}: {agent['description'][:80]}...")

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
        "model": "openai/gpt-oss-20b:free",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return PlannerAgent(model)