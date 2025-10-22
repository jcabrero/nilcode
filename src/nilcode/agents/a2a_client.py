"""
A2A Client Agent

This agent handles communication with external agents via the A2A protocol.
It receives tasks assigned to external agents and executes them remotely.
"""

import logging
from typing import Dict, Any, Optional
from uuid import uuid4

import httpx
from a2a.client import A2AClient
from a2a.types import MessageSendParams, SendMessageRequest, SendStreamingMessageRequest

from ..state.agent_state import AgentState
from ..a2a.registry import get_global_registry


logger = logging.getLogger(__name__)


class A2AClientAgent:
    """
    Agent that communicates with external A2A agents.

    This agent:
    1. Identifies tasks assigned to external agents
    2. Sends task requests via A2A protocol
    3. Processes responses (streaming or non-streaming)
    4. Updates task status and results
    """

    def __init__(self, httpx_client: Optional[httpx.AsyncClient] = None, use_streaming: bool = False):
        """
        Initialize the A2A client agent.

        Args:
            httpx_client: Optional HTTP client for making requests
            use_streaming: Whether to use streaming responses
        """
        self.name = "a2a_client"
        self.httpx_client = httpx_client
        self.external_client_owned = httpx_client is None
        self.use_streaming = use_streaming

    async def __aenter__(self):
        """Async context manager entry."""
        if self.external_client_owned:
            self.httpx_client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.external_client_owned and self.httpx_client:
            await self.httpx_client.aclose()

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the A2A client agent (synchronous wrapper).

        Args:
            state: Current agent state

        Returns:
            Updated state with task results from external agents
        """
        import asyncio

        # Run async code in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._async_call(state))
            return result
        finally:
            loop.close()

    async def _async_call(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the A2A client agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with task results from external agents
        """
        print("\n🌐 A2A Client Agent: Communicating with external agents...")

        tasks = state.get("tasks", [])
        current_task_id = state.get("current_task_id", "")

        # Find the current task
        current_task = None
        for task in tasks:
            if task["id"] == current_task_id:
                current_task = task
                break

        if not current_task:
            logger.error(f"No task found with id {current_task_id}")
            return {
                "next_agent": "orchestrator",
                "error": f"Task {current_task_id} not found"
            }

        # Get the external agent name from assignedTo
        external_agent_name = current_task.get("assignedTo", "")

        if not external_agent_name:
            logger.error("No external agent assigned to task")
            return {
                "next_agent": "orchestrator",
                "error": "No external agent assigned to task"
            }

        # Create httpx client if needed
        if not self.httpx_client:
            self.httpx_client = httpx.AsyncClient()

        # Get the registry and find the external agent
        registry = await get_global_registry()
        external_agent = registry.get_agent(external_agent_name)

        if not external_agent:
            logger.error(f"External agent '{external_agent_name}' not found in registry")
            return {
                "next_agent": "orchestrator",
                "error": f"External agent '{external_agent_name}' not registered"
            }

        # Build the message to send to the external agent
        task_content = current_task.get("content", "")
        user_request = state.get("user_request", "")

        # Include context from the state
        context_parts = []
        if user_request:
            context_parts.append(f"Original request: {user_request}")
        if task_content:
            context_parts.append(f"Specific task: {task_content}")

        # Add project context if available
        if state.get("plan"):
            context_parts.append(f"Overall plan: {state.get('plan')}")

        message_text = "\n\n".join(context_parts)

        print(f"  🎯 Target agent: {external_agent_name}")
        print(f"  📨 Sending task: {task_content[:100]}...")

        try:
            # Create A2A client for this external agent
            client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=external_agent.agent_card
            )

            # Prepare message payload
            send_message_payload = {
                "message": {
                    "role": "user",
                    "parts": [
                        {"kind": "text", "text": message_text}
                    ],
                    "messageId": uuid4().hex,
                }
            }

            result_text = ""

            if self.use_streaming:
                # Use streaming for real-time updates
                print("  📡 Using streaming mode...")
                streaming_request = SendStreamingMessageRequest(
                    id=str(uuid4()),
                    params=MessageSendParams(**send_message_payload)
                )

                stream_response = client.send_message_streaming(streaming_request)

                async for chunk in stream_response:
                    # Extract text from chunk
                    chunk_data = chunk.model_dump(mode='json', exclude_none=True)

                    # Handle different chunk types
                    if 'result' in chunk_data and 'message' in chunk_data['result']:
                        message_data = chunk_data['result']['message']
                        if 'parts' in message_data:
                            for part in message_data['parts']:
                                if part.get('kind') == 'text':
                                    result_text += part.get('text', '')
                                    print(f"  📥 Received chunk: {part.get('text', '')[:50]}...")

            else:
                # Use non-streaming for complete response
                print("  📡 Using non-streaming mode...")
                request = SendMessageRequest(
                    id=str(uuid4()),
                    params=MessageSendParams(**send_message_payload)
                )

                response = await client.send_message(request)
                response_data = response.model_dump(mode='json', exclude_none=True)

                # Extract text from response
                if 'result' in response_data and 'message' in response_data['result']:
                    message_data = response_data['result']['message']
                    if 'parts' in message_data:
                        for part in message_data['parts']:
                            if part.get('kind') == 'text':
                                result_text += part.get('text', '')

            print(f"\n  ✅ Received response from {external_agent_name}")
            print(f"     Response length: {len(result_text)} characters")

            # Update task with result
            current_task["status"] = "completed"
            current_task["result"] = result_text
            current_task["progress"] = "Completed via external A2A agent"

            # Update the tasks list
            for i, task in enumerate(tasks):
                if task["id"] == current_task_id:
                    tasks[i] = current_task
                    break

            return {
                "tasks": tasks,
                "next_agent": "orchestrator",
                "implementation_results": {
                    **state.get("implementation_results", {}),
                    external_agent_name: result_text
                }
            }

        except Exception as e:
            logger.error(f"Error communicating with external agent '{external_agent_name}': {e}", exc_info=True)

            # Update task as failed
            current_task["status"] = "failed"
            current_task["last_error"] = str(e)
            current_task["retry_count"] = current_task.get("retry_count", 0) + 1

            # Update the tasks list
            for i, task in enumerate(tasks):
                if task["id"] == current_task_id:
                    tasks[i] = current_task
                    break

            return {
                "tasks": tasks,
                "next_agent": "orchestrator",
                "error": f"Failed to communicate with external agent: {str(e)}"
            }


def create_a2a_client_agent(use_streaming: bool = False) -> A2AClientAgent:
    """
    Factory function to create an A2A client agent.

    Args:
        use_streaming: Whether to use streaming responses

    Returns:
        Configured A2AClientAgent
    """
    return A2AClientAgent(use_streaming=use_streaming)
