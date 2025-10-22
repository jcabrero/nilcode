"""
Hedera Agent - Handles blockchain and Hedera network operations.

This agent is responsible for:
1. Creating Hedera-powered applications using the Hedera Agent Kit
2. Setting up TypeScript/Node.js projects with Hedera SDK
3. Implementing blockchain interactions and smart contracts
4. Managing Hedera account operations and token transactions
5. Creating conversational AI agents that interact with Hedera
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.file_operations import file_tools
from ..tools.task_management import task_tools, set_task_storage
from ..tools.validation_tools import validation_tools
from ..tools.terminal_tools import terminal_tools
from .utils import determine_next_agent

HEDERA_AGENT_SYSTEM_PROMPT = """
You are a Hedera Agent in a multi-agent software development system.

Your role is to handle blockchain and Hedera network operations including:
1. **Hedera Project Setup**: Create TypeScript/Node.js projects with Hedera Agent Kit
2. **Blockchain Integration**: Implement Hedera SDK, account management, and token operations
3. **AI Agent Creation**: Build conversational agents that interact with Hedera using LangChain
4. **Smart Contract Development**: Create and deploy Hedera smart contracts
5. **DApp Development**: Build decentralized applications with Hedera integration

CRITICAL WORKFLOW - FOLLOW THIS ORDER:

**PHASE 1: Understand Hedera Context (DO THIS FIRST!)**
1. Read PROJECT_MANIFEST.md to understand:
   - Technology stack and Hedera integration requirements
   - Directory structure for blockchain projects
   - Architecture patterns for DApps
2. Read .agent-guidelines/coding-standards.md for:
   - TypeScript/JavaScript conventions
   - Hedera SDK patterns
   - Security best practices for blockchain
3. Use list_files to see existing file structure
4. Check if Hedera dependencies are already installed

**PHASE 2: Hedera Project Setup (IF NEEDED)**
1. Create package.json with Hedera dependencies:
   - hedera-agent-kit (main package)
   - @hashgraph/sdk (Hedera SDK)
   - @langchain/openai, @langchain/core, langchain (AI integration)
   - typescript, @types/node (TypeScript support)
   - dotenv (environment variables)
2. Create tsconfig.json for TypeScript configuration
3. Create .env.example with Hedera credentials:
   - HEDERA_ACCOUNT_ID
   - HEDERA_PRIVATE_KEY
   - AI provider API keys (OPENAI_API_KEY, etc.)
4. Create .gitignore for Node.js/TypeScript projects
5. Create README.md with Hedera setup instructions

**PHASE 3: Implement Hedera Code**
1. Create main application files:
   - index.ts (main entry point)
   - hedera-client.ts (Hedera client configuration)
   - agents/ directory for AI agents
   - utils/ directory for helper functions
2. Implement Hedera operations:
   - Account balance queries
   - Token transfers and operations
   - Smart contract interactions
   - Consensus Service operations
3. Create AI agent integrations:
   - LangChain agent setup
   - Tool calling with Hedera operations
   - Conversational interfaces
4. Add proper error handling and validation
5. Include comprehensive TypeScript types

**PHASE 4: Validate Your Work (MANDATORY!)**
1. Use validate_javascript_syntax for .ts/.js files
2. Use validate_json_syntax for package.json, tsconfig.json
3. Use check_import_validity to verify imports
4. Verify all required files exist and have correct content
5. Test TypeScript compilation if possible

**PHASE 5: Complete Task**
1. Only mark task as "completed" if validation passes
2. Provide comprehensive summary including:
   - Files created/modified
   - Hedera operations implemented
   - AI agent capabilities
   - Setup instructions

HEDERA-SPECIFIC REQUIREMENTS:
- Always use TypeScript for type safety
- Implement proper error handling for network operations
- Include environment variable validation
- Add comprehensive logging for blockchain operations
- Follow Hedera best practices for account management
- Implement proper private key handling and security

COMMON HEDERA PATTERNS:
```typescript
// Client setup
const client = Client.forTestnet().setOperator(
  process.env.HEDERA_ACCOUNT_ID!,
  PrivateKey.fromStringECDSA(process.env.HEDERA_PRIVATE_KEY!)
);

// Balance query
const accountBalance = await new AccountBalanceQuery()
  .setAccountId(accountId)
  .execute(client);

// Token transfer
const tokenTransfer = await new TransferTransaction()
  .addTokenTransfer(tokenId, fromAccount, -amount)
  .addTokenTransfer(tokenId, toAccount, amount)
  .execute(client);
```

You have access to:
- File tools: read_file, write_file, edit_file, list_files, create_directory
- Validation tools: validate_javascript_syntax, validate_json_syntax, check_import_validity
- Terminal tools: run_command (for npm install, tsc compilation)
- Task tools: update_task_status, create_enhanced_task, update_task_progress

SYNTAX REQUIREMENTS FOR TYPESCRIPT:
- Proper type annotations: const variable: Type = value
- Interface definitions: interface Name { property: Type }
- Import statements: import { Name } from 'module'
- Export statements: export const/function/class Name
- Async/await syntax: async function name(): Promise<Type>
- Error handling: try/catch blocks with proper typing
"""


class HederaAgent:
    """
    Hedera agent that handles blockchain and Hedera network operations.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initialize the Hedera agent.

        Args:
            model: Language model to use
        """
        all_tools = file_tools + task_tools + validation_tools + terminal_tools
        self.model = model.bind_tools(all_tools)
        self.name = "hedera_agent"

    def _invoke_with_retry(self, messages, state, max_retries=3):
        """
        Invoke the model with retry handling for rate limits and other transient errors.
        """
        from openai import RateLimitError
        import time
        import random
        
        for attempt in range(max_retries + 1):
            try:
                print(f"    🤖 Calling LLM (attempt {attempt + 1}/{max_retries + 1})...")
                response = self.model.invoke(messages)
                return response
                
            except RateLimitError as e:
                if attempt == max_retries:
                    print(f"    ❌ Rate limit exceeded after {max_retries} retries")
                    raise e
                
                base_delay = 2 ** attempt
                jitter = random.uniform(0.5, 1.5)
                delay = base_delay * jitter
                
                print(f"    ⚠️  Rate limit hit: {str(e)}")
                print(f"    ⏳ Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
                
            except Exception as e:
                if attempt == max_retries:
                    print(f"    ❌ Error after {max_retries} retries: {str(e)}")
                    raise e
                
                print(f"    ⚠️  Error: {str(e)}")
                print(f"    ⏳ Retrying in 2 seconds...")
                time.sleep(2)

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the Hedera agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with Hedera implementation results
        """
        print("\n⛓️  Hedera Agent: Working on blockchain and Hedera operations...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        # Get Hedera-specific tasks
        hedera_tasks = [
            task for task in tasks
            if task.get("assignedTo") == "hedera_agent"
            and task.get("status") in ["pending", "in_progress"]
        ]

        if not hedera_tasks:
            print("  No Hedera tasks found, moving to next agent...")
            next_agent = determine_next_agent(tasks)
            status = "testing" if next_agent == "tester" else (
                "architecting" if next_agent == "software_architect" else "implementing"
            )
            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
                "overall_status": status,
            }

        # Work on the first pending task
        current_task = hedera_tasks[0]
        print(f"  📋 Working on: {current_task['content']}")

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", HEDERA_AGENT_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current plan: {plan}

Detected languages: {languages}
Frontend technologies: {frontend_tech}
Backend technologies: {backend_tech}
Project manifest location: {manifest_path}
Guidelines location: {guidelines_path}

Current task: {task_content}

IMPORTANT WORKFLOW:
1. FIRST: Read {manifest_path} (if exists) to understand project structure
2. SECOND: Read {guidelines_path}/coding-standards.md (if exists) for conventions
3. THIRD: Use list_files to see existing structure
4. FOURTH: Implement Hedera code following established patterns
5. FIFTH: Validate syntax using validation tools
6. SIXTH: Only if validation passes, update task status to "completed"

Begin by reading the project documentation!""")
        ])

        # Format the prompt
        messages = prompt.format_messages(
            user_request=state["user_request"],
            plan=state.get("plan", ""),
            languages=", ".join(state.get("detected_languages", [])) or "Not specified",
            frontend_tech=", ".join(state.get("frontend_tech", [])) or "None",
            backend_tech=", ".join(state.get("backend_tech", [])) or "None",
            manifest_path=state.get("project_manifest_path", "PROJECT_MANIFEST.md"),
            guidelines_path=state.get("guidelines_path", ".agent-guidelines"),
            task_content=current_task["content"]
        )

        # Get response from model with retry handling
        response = self._invoke_with_retry(messages, state)
        messages_history = list(messages) + [response]

        # Execute tool calls
        max_iterations = 25
        iteration = 0
        all_tools = file_tools + task_tools + validation_tools + terminal_tools
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

            # Get next response with retry handling
            response = self._invoke_with_retry(messages_history, state)
            messages_history.append(response)

        # Generate final summary after all tools are done
        try:
            if not response.content or len(response.content.strip()) < 50:
                print("    📝 Generating final summary...")
                from langchain_core.messages import HumanMessage
                messages_history.append(HumanMessage(
                    content="Please provide a comprehensive summary of what you just implemented, including what Hedera functionality was added, files created/modified, and setup instructions."
                ))
                response = self._invoke_with_retry(messages_history, state)
                messages_history.append(response)

            print(f"\n✅ Hedera task completed!")
            summary = response.content if hasattr(response, 'content') and response.content else "Task completed"
            print(f"Summary: {summary[:150]}..." if len(summary) > 150 else f"Summary: {summary}")
        except Exception as e:
            print(f"\n⚠️ Warning: Error generating summary: {e}")
            summary = "Task completed (summary generation failed)"

        # Mark the current task as completed
        updated_tasks = []
        for task in tasks:
            if task["id"] == current_task["id"]:
                task = {**task, "status": "completed", "result": summary}
            updated_tasks.append(task)

        set_task_storage(updated_tasks)

        # Check if there are more Hedera tasks
        next_agent = determine_next_agent(updated_tasks, prefer_agent="hedera_agent")
        status = "testing" if next_agent == "tester" else (
            "architecting" if next_agent == "software_architect" else "implementing"
        )

        return {
            "messages": messages_history,
            "tasks": updated_tasks,
            "next_agent": next_agent,
            "overall_status": status,
            "implementation_results": {
                **state.get("implementation_results", {}),
                "hedera_agent": summary
            }
        }


def create_hedera_agent(api_key: str, base_url: str = None) -> HederaAgent:
    """
    Factory function to create a Hedera agent.

    Args:
        api_key: API key for the LLM provider
        base_url: Optional base URL for the API

    Returns:
        Configured HederaAgent
    """
    model_kwargs = {
        "model": "openai/gpt-oss-120b",
        "api_key": api_key,
    }

    if base_url:
        model_kwargs["base_url"] = base_url

    model = ChatOpenAI(**model_kwargs)
    return HederaAgent(model)
