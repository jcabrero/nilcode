"""
PrePlanner Agent - Understands the user's intent before planning.

This agent classifies what the user wants to build or do, extracts
key details (intent type, targets, technologies), and sets up state
so the Planner can produce better tasks. It does not bind tools.
"""

from typing import Dict, Any, Optional, List
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..state.agent_state import AgentState


PREPLANNER_SYSTEM_PROMPT = """
You are an intent classifier for a multi-agent software dev system.
Your job is to understand what the user wants to build or do.

Respond with STRICT JSON only (no prose, no code fences).
Required keys:
- intent: one of build, refactor, debug, explain, research, onchain_query, configure, run, unknown
- target: short description of what they want
- artifacts: array of expected outputs
- tech_stack: array of languages/frameworks if implied
- constraints: array of notable constraints
- suggested_agents: array from [planner, software_architect, coder, tester, onchain_detective]
- confidence: number between 0 and 1
- rationale: terse 1-2 sentence rationale

Output ONLY the JSON object with those keys, using double quotes.
"""


def _heuristic_intent(user_request: str) -> Dict[str, Any]:
    """
    Heuristic fallback when LLM parsing fails.
    """
    text = user_request.lower()

    # Scenario A: Next.js app build intent
    if "next.js" in text or "nextjs" in text or "next js" in text:
        return {
            "intent": "build",
            "target": "Build a Next.js application",
            "artifacts": ["Next.js app skeleton", "pages/components", "package.json"],
            "tech_stack": ["javascript", "typescript", "react", "nextjs"],
            "constraints": [],
            "suggested_agents": ["planner", "software_architect", "coder", "tester"],
            "confidence": 0.8,
            "rationale": "Mentions Next.js explicitly; clear build intent",
        }

    # Scenario B: How much ETH Vitalik has (onchain query)
    if ("how much" in text and "eth" in text) or (
        "balance" in text and "vitalik" in text
    ):
        return {
            "intent": "onchain_query",
            "target": "Find ETH holdings for Vitalik",
            "artifacts": ["ETH balance report", "data sources and method"],
            "tech_stack": ["onchain", "etherscan/api", "blockchain indexing"],
            "constraints": ["address mapping and labeling"],
            "suggested_agents": ["planner", "onchain_detective", "tester"],
            "confidence": 0.75,
            "rationale": "Direct question about ETH holdings (on-chain info)",
        }

    # Generic fallbacks
    build_keywords = ["build", "create", "implement", "make"]
    if any(k in text for k in build_keywords):
        return {
            "intent": "build",
            "target": user_request.strip()[:100],
            "artifacts": [],
            "tech_stack": [],
            "constraints": [],
            "suggested_agents": ["planner"],
            "confidence": 0.6,
            "rationale": "Generic build verbs detected",
        }

    if any(k in text for k in ["how to", "how do i", "explain", "why"]):
        return {
            "intent": "explain",
            "target": user_request.strip()[:100],
            "artifacts": ["explanation", "examples"],
            "tech_stack": [],
            "constraints": [],
            "suggested_agents": ["planner"],
            "confidence": 0.55,
            "rationale": "Question phrasing suggests explanation",
        }

    return {
        "intent": "unknown",
        "target": user_request.strip()[:100],
        "artifacts": [],
        "tech_stack": [],
        "constraints": [],
        "suggested_agents": ["planner"],
        "confidence": 0.4,
        "rationale": "No strong keywords detected",
    }


class PrePlannerAgent:
    """Classifies user intent and enriches state for planning."""

    def __init__(self, model: ChatOpenAI):
        self.model = model  # No tools needed
        self.name = "preplanner"

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        user_request = state.get("user_request", "").strip()
        print("\n🧭 PrePlanner Agent: Understanding user intent...")

        # Default values in case of errors
        intent_payload: Dict[str, Any]

        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", PREPLANNER_SYSTEM_PROMPT),
                    (
                        "human",
                        "User request: {user_request}\n\nReturn strict JSON only.",
                    ),
                ]
            )

            messages = prompt.format_messages(user_request=user_request)
            response = self.model.invoke(messages)
            content = (response.content or "").strip()

            # Extract JSON possibly inside code fences
            if "```" in content:
                m = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
                if m:
                    content = m.group(1).strip()

            import json

            # Debug: print what we're trying to parse
            if not content:
                raise ValueError("LLM returned empty content")
            
            # Additional cleaning: remove leading/trailing whitespace and find JSON object
            # Look for the first { and last } to extract just the JSON
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                content = content[start_idx:end_idx+1]
            
            parsed = json.loads(content)

            # Validate minimal keys
            intent_payload = {
                "intent": parsed.get("intent", "unknown"),
                "target": parsed.get("target", user_request[:100]),
                "artifacts": parsed.get("artifacts", []) or [],
                "tech_stack": parsed.get("tech_stack", []) or [],
                "constraints": parsed.get("constraints", []) or [],
                "suggested_agents": parsed.get("suggested_agents", ["planner"])
                or ["planner"],
                "confidence": float(parsed.get("confidence", 0.5)),
                "rationale": parsed.get("rationale", "")[:300],
            }
        except Exception as e:
            print(f"  ⚠️  PrePlanner fallback due to parse/model issue: {e}")
            intent_payload = _heuristic_intent(user_request)

        # Route directly for specific intents; default to planner
        tasks_update = state.get("tasks", [])
        user_request_lower = user_request.lower()

        # Check for Hedera-specific keywords (highest priority)
        hedera_keywords = ["hedera", "hbar", "hashgraph", "hedera account", "hedera balance", "hedera token", "hedera contract"]
        is_hedera_query = any(keyword in user_request_lower for keyword in hedera_keywords)

        if intent_payload.get("intent") == "onchain_query":
            # Hedera queries go to planner → hedera-manager (via A2A)
            if is_hedera_query:
                next_agent = "planner"
                print("  🔗 Hedera query detected - routing to planner for external hedera-manager agent")
            # General onchain queries go to onchain_detective
            else:
                next_agent = "onchain_detective"
                print("  🔍 General onchain query detected - routing to onchain_detective")
                # Ensure there is a detective task so the agent has work
                import uuid
                task = {
                    "id": str(uuid.uuid4())[:8],
                    "content": intent_payload.get("target") or user_request,
                    "status": "pending",
                    "activeForm": "Analyzing on-chain data",
                    "assignedTo": "onchain_detective",
                    "result": "",
                    # Enhanced fields (minimal defaults)
                    "requirements": ["Fetch balance and basic classification"],
                    "progress": "Not started",
                    "files_created": [],
                    "files_modified": [],
                    "dependencies": [],
                    "retry_count": 0,
                    "last_error": "",
                    "estimated_effort": "low",
                    "actual_effort": "not_started",
                }
                tasks_update = tasks_update + [task]
        else:
            next_agent = "planner"

        # Light tech hints to downstream agents
        detected_languages: List[str] = []
        frontend_tech: List[str] = []
        backend_tech: List[str] = []

        lowered = [t.lower() for t in intent_payload.get("tech_stack", [])]
        if any(t in lowered for t in ["nextjs", "next.js", "react"]):
            frontend_tech.extend(["react", "nextjs"])
            detected_languages.extend(["javascript", "typescript"])
        # minimal heuristic; planner will refine further

        print(
            f"  🔎 Intent: {intent_payload['intent']} (conf {intent_payload['confidence']:.2f})"
        )
        print(f"  🎯 Target: {intent_payload['target']}")

        return {
            "messages": state.get("messages", [])
            + ([response] if "response" in locals() else []),
            "tasks": tasks_update,
            "user_intent": intent_payload.get("intent", "unknown"),
            "intent_confidence": intent_payload.get("confidence", 0.5),
            "intent_details": intent_payload,
            "next_agent": next_agent,
            "overall_status": "planning",
            "detected_languages": list(
                {*state.get("detected_languages", []), *detected_languages}
            ),
            "frontend_tech": list({*state.get("frontend_tech", []), *frontend_tech}),
            "backend_tech": list({*state.get("backend_tech", []), *backend_tech}),
        }


def create_preplanner_agent(
    api_key: str, base_url: Optional[str] = None
) -> PrePlannerAgent:
    """Factory for PrePlanner agent."""
    model_kwargs = {
        "model": "openai/gpt-oss-20b:free",
        "api_key": api_key,
    }
    if base_url:
        model_kwargs["base_url"] = base_url
    model = ChatOpenAI(**model_kwargs)
    return PrePlannerAgent(model)
