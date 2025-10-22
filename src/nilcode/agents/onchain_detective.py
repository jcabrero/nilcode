"""
On-Chain Detective Agent - Blockchain analysis with AI reasoning.

UTF-8 safe implementation that analyzes blockchain addresses using
Blockscout-like tools and provides human-readable insights.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState
from ..tools.blockscout_tools import blockscout_tools
from ..tools.task_management import set_task_storage
from .utils import determine_next_agent


ONCHAIN_DETECTIVE_SYSTEM_PROMPT = """You are an On-Chain Detective, a blockchain analysis specialist.

Your role is to:
1. Analyze blockchain addresses, balances, and transactions
2. Provide intelligent insights (not just raw data)
3. Identify patterns and wallet classifications (EOA/contract, exchange, etc.)
4. Explain findings clearly and assess risk where applicable

Rules:
- Use tools to fetch data; do not fabricate results
- Interpret and summarize; do not dump raw JSON
- Provide an executive summary, then details in bullets
"""


class OnChainDetectiveAgent:
    """On-chain detective agent for blockchain analysis."""

    def __init__(self, model: ChatOpenAI):
        self.model = model.bind_tools(blockscout_tools)
        self.name = "onchain_detective"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        print("\n🔎 On-Chain Detective Agent: Analyzing blockchain data...")

        tasks = state.get("tasks", [])
        set_task_storage(tasks)

        detective_tasks = [
            t for t in tasks
            if t.get("assignedTo") == "onchain_detective" and t.get("status") in {"pending", "in_progress"}
        ]

        if not detective_tasks:
            print("  No on-chain detective tasks found, moving to next agent...")
            next_agent = determine_next_agent(tasks)
            return {
                "next_agent": next_agent,
                "messages": state.get("messages", []),
                "overall_status": "completed",
            }

        current_task = detective_tasks[0]
        print(f"  📋 Analyzing: {current_task['content']}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", ONCHAIN_DETECTIVE_SYSTEM_PROMPT),
            ("human", """User request: {user_request}

Current task: {task_content}

Use get_address_balance to fetch data, then provide an intelligent analysis:
- Executive summary (1–2 sentences)
- Detailed bullets (balance, activity, tags, contract/EOA)
- Classification and any notable patterns
- Risks or recommendations if applicable
"""),
        ])

        messages = prompt.format_messages(
            user_request=state["user_request"],
            task_content=current_task["content"],
        )

        response = self.model.invoke(messages)
        messages_history = list(messages) + [response]

        max_iterations = 10
        iteration = 0

        while getattr(response, "tool_calls", None) and iteration < max_iterations:
            iteration += 1
            for tool_call in response.tool_calls:
                try:
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get("name")
                        tool_args = tool_call.get("args", {})
                        tool_id = tool_call.get("id")
                    else:
                        tool_name = getattr(tool_call, "name", None)
                        tool_args = getattr(tool_call, "args", {})
                        tool_id = getattr(tool_call, "id", None)

                    if not tool_name:
                        print("    ⚠️  Skipping invalid tool call")
                        continue

                    tool = next((t for t in blockscout_tools if t.name == tool_name), None)
                    if tool is None:
                        print(f"    ⚠️  Tool '{tool_name}' not found")
                        continue

                    print(f"    🔧 Using tool: {tool.name} with args: {tool_args}")
                    result = tool.invoke(tool_args)

                    from langchain_core.messages import ToolMessage
                    messages_history.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id if tool_id else str(iteration),
                    ))
                except Exception as e:
                    print(f"    ⚠️  Error processing tool call: {e}")
                    continue

            response = self.model.invoke(messages_history)
            messages_history.append(response)

        analysis = response.content if getattr(response, "content", "") else "Analysis completed"
        print("\n✅ On-Chain Detective analysis complete!")

        # Mark the task completed
        updated_tasks = []
        for t in tasks:
            if t["id"] == current_task["id"]:
                t = {**t, "status": "completed", "result": analysis}
            updated_tasks.append(t)
        set_task_storage(updated_tasks)

        next_agent = determine_next_agent(updated_tasks)

        return {
            "messages": messages_history,
            "tasks": updated_tasks,
            "next_agent": next_agent if next_agent != "onchain_detective" else "orchestrator",
            "overall_status": "completed" if next_agent == "orchestrator" else "implementing",
            "implementation_results": {
                **state.get("implementation_results", {}),
                "onchain_detective": analysis,
            },
        }


def create_onchain_detective_agent(api_key: str, base_url: Optional[str] = None) -> OnChainDetectiveAgent:
    model_kwargs = {
        "model": "openai/gpt-oss-120b",
        "api_key": api_key,
    }
    if base_url:
        model_kwargs["base_url"] = base_url
    model = ChatOpenAI(**model_kwargs)
    return OnChainDetectiveAgent(model)
