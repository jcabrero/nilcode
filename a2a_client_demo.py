#!/usr/bin/env python3
"""
Simple A2A Client Demo

This script demonstrates how to:
1. Discover the Hedera agent via A2A protocol
2. Query its capabilities and agent card
3. Send a simple message to test communication

Usage:
    python a2a_client_demo.py [agent_url] [timeout_seconds]
    
Examples:
    python a2a_client_demo.py                                    # Use defaults
    python a2a_client_demo.py http://localhost:9000              # Custom URL
    python a2a_client_demo.py http://localhost:9000 60           # Custom URL + 60s timeout
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import httpx
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import MessageSendParams, SendMessageRequest
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


class SimpleA2AClient:
    """Simple A2A client for testing agent communication."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize the A2A client.
        
        Args:
            base_url: Base URL of the A2A agent server
            timeout: Request timeout in seconds (default: 30 seconds)
        """
        self.base_url = base_url
        self.timeout = timeout
        # Create HTTP client with extended timeout
        self.httpx_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,  # Connection timeout
                read=timeout,  # Read timeout (for server response)
                write=10.0,    # Write timeout
                pool=5.0       # Pool timeout
            )
        )
        self.agent_card = None
        self.a2a_client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.httpx_client.aclose()
    
    async def discover_agent(self) -> bool:
        """
        Discover the agent by fetching its agent card.
        
        Returns:
            True if discovery successful, False otherwise
        """
        print(f"🔍 Discovering agent at {self.base_url}")
        print(f"⏱️  Using timeout: {self.timeout} seconds")
        
        try:
            # Create card resolver
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=self.base_url
            )
            
            # Fetch agent card
            print(f"📋 Fetching agent card from {self.base_url}{AGENT_CARD_WELL_KNOWN_PATH}")
            self.agent_card = await resolver.get_agent_card()
            
            print("✅ Agent discovered successfully!")
            print(f"   Name: {getattr(self.agent_card, 'name', 'Unknown')}")
            print(f"   Description: {getattr(self.agent_card, 'description', 'No description')}")
            print(f"   Version: {getattr(self.agent_card, 'version', 'Unknown')}")
            
            # Try different attribute names for protocol version
            protocol_version = getattr(self.agent_card, 'protocolVersion', None) or getattr(self.agent_card, 'protocol_version', None)
            if protocol_version:
                print(f"   Protocol Version: {protocol_version}")
            
            # Display capabilities
            capabilities = getattr(self.agent_card, 'capabilities', None)
            if capabilities:
                print("   Capabilities:")
                if isinstance(capabilities, dict):
                    for key, value in capabilities.items():
                        print(f"     - {key}: {value}")
                else:
                    print(f"     - {capabilities}")
            
            # Display skills
            skills = getattr(self.agent_card, 'skills', None)
            if skills:
                print("   Skills:")
                if isinstance(skills, list):
                    for skill in skills:
                        if isinstance(skill, dict):
                            skill_name = skill.get('name', 'Unknown')
                            skill_desc = skill.get('description', 'No description')
                            print(f"     - {skill_name}: {skill_desc}")
                        else:
                            print(f"     - {skill}")
                else:
                    print(f"     - {skills}")
            
            # Display additional info
            print(f"   URL: {getattr(self.agent_card, 'url', 'Unknown')}")
            print(f"   Preferred Transport: {getattr(self.agent_card, 'preferred_transport', 'Unknown')}")
            
            # Create A2A client
            self.a2a_client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=self.agent_card
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to discover agent: {e}")
            return False
    
    async def query_capabilities(self) -> Optional[dict]:
        """
        Query the agent's capabilities by sending a capabilities request.
        
        Returns:
            Agent capabilities as dict, or None if failed
        """
        if not self.a2a_client:
            print("❌ Agent not discovered. Call discover_agent() first.")
            return None
        
        print(f"\n🔍 Querying agent capabilities...")
        print(f"⏱️  Using timeout: {self.timeout} seconds")
        
        try:
            # Send a capabilities query message
            message_text = "What are your capabilities? Please describe what you can do with Hedera blockchain operations."
            
            # Prepare message payload
            send_message_payload = {
                "message": {
                    "role": "user",
                    "parts": [
                        {"kind": "text", "text": message_text}
                    ],
                    "messageId": "capabilities-query-001",
                }
            }
            
            # Create and send request
            request = SendMessageRequest(
                id="capabilities-request-001",
                params=MessageSendParams(**send_message_payload)
            )
            
            print(f"📤 Sending capabilities query...")
            response = await self.a2a_client.send_message(request)
            
            # Extract response
            response_data = response.model_dump(mode='json', exclude_none=True)
            
            print("✅ Received capabilities response!")
            
            # Extract text from response
            
            # Try different response structures
            capabilities_text = ""
            
            # Method 1: Standard A2A response structure
            if 'result' in response_data and 'message' in response_data['result']:
                message_data = response_data['result']['message']
                if 'parts' in message_data:
                    for part in message_data['parts']:
                        if part.get('kind') == 'text':
                            capabilities_text += part.get('text', '')
            
            # Method 2: Direct message structure
            elif 'message' in response_data:
                message_data = response_data['message']
                if 'parts' in message_data:
                    for part in message_data['parts']:
                        if part.get('kind') == 'text':
                            capabilities_text += part.get('text', '')
            
            # Method 3: Look for any text content
            elif 'content' in response_data:
                capabilities_text = response_data['content']
            
            # Method 4: Look for text in any nested structure
            else:
                def find_text_recursive(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key in ['text', 'content', 'message'] and isinstance(value, str):
                                return value
                            elif isinstance(value, (dict, list)):
                                result = find_text_recursive(value)
                                if result:
                                    return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_text_recursive(item)
                            if result:
                                return result
                    return None
                
                capabilities_text = find_text_recursive(response_data) or ""
            
            if capabilities_text:
                print(f"📋 Agent Response:")
                print(f"   {capabilities_text}")
                
                return {
                    "agent_card": self.agent_card,
                    "capabilities_response": capabilities_text
                }
            
            print("⚠️  No text response found in agent reply")
            return None
            
        except Exception as e:
            print(f"❌ Failed to query capabilities: {e}")
            return None
    
    async def test_hedera_operation(self) -> bool:
        """
        Test a simple Hedera operation to verify the agent is working.
        
        Returns:
            True if test successful, False otherwise
        """
        if not self.a2a_client:
            print("❌ Agent not discovered. Call discover_agent() first.")
            return False
        
        print("\n🧪 Testing Hedera operation...")
        print(f"⏱️  Using timeout: {self.timeout} seconds")
        
        try:
            # Send a test message
            message_text = "Can you query the balance of my hedera account?"
            
            # Prepare message payload
            send_message_payload = {
                "message": {
                    "role": "user",
                    "parts": [
                        {"kind": "text", "text": message_text}
                    ],
                    "messageId": "test-query-001",
                }
            }
            
            # Create and send request
            request = SendMessageRequest(
                id="test-request-001",
                params=MessageSendParams(**send_message_payload)
            )
            
            print(f"📤 Sending test message...")
            response = await self.a2a_client.send_message(request)
            
            # Extract response
            response_data = response.model_dump(mode='json', exclude_none=True)
            
            print("✅ Received test response!")
            
            # Extract text from response using the same logic as capabilities query
            response_text = ""
            
            # Method 1: Standard A2A response structure
            if 'result' in response_data and 'message' in response_data['result']:
                message_data = response_data['result']['message']
                if 'parts' in message_data:
                    for part in message_data['parts']:
                        if part.get('kind') == 'text':
                            response_text += part.get('text', '')
            
            # Method 2: Direct message structure
            elif 'message' in response_data:
                message_data = response_data['message']
                if 'parts' in message_data:
                    for part in message_data['parts']:
                        if part.get('kind') == 'text':
                            response_text += part.get('text', '')
            
            # Method 3: Look for any text content
            elif 'content' in response_data:
                response_text = response_data['content']
            
            # Method 4: Look for text in any nested structure
            else:
                def find_text_recursive(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key in ['text', 'content', 'message'] and isinstance(value, str):
                                return value
                            elif isinstance(value, (dict, list)):
                                result = find_text_recursive(value)
                                if result:
                                    return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_text_recursive(item)
                            if result:
                                return result
                    return None
                
                response_text = find_text_recursive(response_data) or ""
            
            if response_text:
                print(f"📋 Agent Response:")
                print(f"   {response_text}")
                return True
            
            print("⚠️  No text response found in agent reply")
            return False
            
        except Exception as e:
            print(f"❌ Failed to test Hedera operation: {e}")
            return False


async def main():
    """Main function to run the A2A client demo."""
    print("🚀 A2A Client Demo - Hedera Agent")
    print("=" * 50)
    
    # Configuration
    hedera_agent_url = "http://localhost:9000"
    timeout = 30.0  # Default timeout in seconds
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        hedera_agent_url = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            timeout = float(sys.argv[2])
        except ValueError:
            print(f"⚠️  Invalid timeout value: {sys.argv[2]}. Using default: {timeout}s")
    
    print(f"🎯 Target agent URL: {hedera_agent_url}")
    print(f"⏱️  Request timeout: {timeout} seconds")
    print()
    
    # Create and run client
    async with SimpleA2AClient(hedera_agent_url, timeout=timeout) as client:
        # Step 1: Discover agent
        if not await client.discover_agent():
            print("❌ Failed to discover agent. Make sure the Hedera agent is running.")
            return 1
        
        print()
        
        # Step 2: Query capabilities
        capabilities = await client.query_capabilities()
        if not capabilities:
            print("❌ Failed to query capabilities.")
            return 1
        
        print()
        
        # Step 3: Test Hedera operation
        if not await client.test_hedera_operation():
            print("❌ Failed to test Hedera operation.")
            return 1
        
        print()
        print("🎉 A2A Client Demo completed successfully!")
        print("✅ Agent discovery: SUCCESS")
        print("✅ Capabilities query: SUCCESS") 
        print("✅ Hedera operation test: SUCCESS")
        
        return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)
