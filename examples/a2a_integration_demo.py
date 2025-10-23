"""
A2A Integration Demo

This example demonstrates how to use the A2A external agent integration
with the nilcode multi-agent system.

Prerequisites:
1. Start an A2A-compatible agent server (e.g., http://localhost:9999)
2. Configure external agents via environment variables or config file
3. Run this demo to see nilcode delegate tasks to external agents

Setup:
    # Option 1: Using environment variables
    export A2A_AGENTS='[{"name":"currency_converter","base_url":"http://localhost:9999"}]'

    # Option 2: Using a config file
    export A2A_CONFIG_PATH=a2a_agents.json

    # Then run the demo
    uv run python examples/a2a_integration_demo.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.nilcode.main_agent import create_agent_system
from src.nilcode.a2a.registry import initialize_registry_from_config


async def main():
    """Run the A2A integration demo."""
    print("=" * 70)
    print("A2A EXTERNAL AGENT INTEGRATION DEMO")
    print("=" * 70)
    print()

    # Load environment variables
    load_dotenv()

    # Step 1: Initialize the A2A registry
    print("📡 Step 1: Initializing A2A agent registry...")
    print()

    try:
        registry = await initialize_registry_from_config()
        external_agents = registry.list_agents()

        if not external_agents:
            print("⚠️  No external agents configured!")
            print()
            print("To configure external agents, set one of the following:")
            print()
            print("1. Environment variable A2A_AGENTS:")
            print('   export A2A_AGENTS=\'[{"name":"agent1","base_url":"http://localhost:9999"}]\'')
            print()
            print("2. Environment variable A2A_CONFIG_PATH:")
            print("   export A2A_CONFIG_PATH=a2a_agents.json")
            print()
            print("3. Create a2a_agents.json with:")
            print("   {")
            print('     "external_agents": [')
            print('       {"name": "currency_converter", "base_url": "http://localhost:9999"}')
            print("     ]")
            print("   }")
            print()
            return

        print(f"✅ Successfully discovered {len(external_agents)} external agents:")
        print()

        for agent in external_agents:
            print(f"  🤖 {agent.name}")
            print(f"     URL: {agent.base_url}")
            print(f"     Description: {agent.description}")
            if agent.capabilities:
                print(f"     Capabilities: {', '.join(agent.capabilities[:3])}")
            print()

    except Exception as e:
        print(f"❌ Error initializing registry: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 2: Create the multi-agent system
    print("🔧 Step 2: Creating multi-agent system...")
    print()

    try:
        agent_system = create_agent_system()
        print("✅ Multi-agent system created successfully")
        print()
    except Exception as e:
        print(f"❌ Error creating agent system: {e}")
        return

    # Step 3: Run a task that uses an external agent
    print("🚀 Step 3: Running demo task...")
    print()
    print("This will test if the planner can detect and assign tasks to external agents.")
    print()

    # Example request that might be suitable for an external agent
    # Adjust based on your external agent's capabilities
    example_requests = [
        "Convert 100 USD to EUR",  # For currency converter agent
        "What is the weather in San Francisco?",  # For weather agent
        "Analyze this data: [1, 2, 3, 4, 5]",  # For data analysis agent
    ]

    # Use the first external agent's likely capability
    if external_agents:
        first_agent = external_agents[0]
        print(f"Detected external agent: {first_agent.name}")
        print(f"Capabilities: {first_agent.description}")
        print()

        # Ask user for request or use example
        user_request = input("Enter your request (or press Enter for example): ").strip()

        if not user_request:
            user_request = example_requests[0]
            print(f"Using example request: {user_request}")

        print()
        print("-" * 70)
        print()

        try:
            # Run the agent system
            final_state = agent_system.run(user_request)

            print()
            print("-" * 70)
            print()
            print("📊 RESULTS:")
            print()
            print(f"Status: {final_state.get('overall_status')}")
            print(f"Tasks completed: {len([t for t in final_state.get('tasks', []) if t['status'] == 'completed'])}")
            print()

            # Show implementation results
            impl_results = final_state.get("implementation_results", {})
            if impl_results:
                print("Implementation Results:")
                for agent_name, result in impl_results.items():
                    print(f"  - {agent_name}: {result[:200]}...")
                print()

            # Show errors if any
            if final_state.get("error"):
                print(f"⚠️  Error: {final_state.get('error')}")
                print()

        except Exception as e:
            print(f"❌ Error running agent system: {e}")
            import traceback
            traceback.print_exc()

    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
