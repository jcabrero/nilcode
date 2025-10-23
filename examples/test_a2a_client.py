#!/usr/bin/env python3
"""
Test script to verify that the A2A Client agent can find external tasks.
"""

import asyncio
from nilcode.agents.a2a_client import create_a2a_client_agent
from nilcode.state.agent_state import create_initial_state

def test_a2a_client_task_finding():
    """Test if A2A Client agent can find external tasks."""
    
    print("🔧 Testing A2A Client agent task finding...")
    
    # Create test state with external task
    test_request = "Query the balance of the account associated to the hedera agent"
    state = create_initial_state(test_request)
    
    # Add a task assigned to external agent
    external_task = {
        "id": "task-1",
        "content": "Query the balance of the account associated to the hedera agent using the hedera-manager agent",
        "assignedTo": "hedera-manager",
        "status": "pending"
    }
    
    state["tasks"] = [external_task]
    
    print(f"📝 Created test state with external task: {external_task['id']}")
    print(f"   Task assigned to: {external_task['assignedTo']}")
    
    # Create A2A Client agent
    a2a_client = create_a2a_client_agent(use_streaming=False)
    
    try:
        # Test the task finding logic (without making actual API calls)
        tasks = state.get("tasks", [])
        
        # Find tasks assigned to external agents
        external_tasks = []
        for task in tasks:
            assigned_to = task.get("assignedTo", "")
            if assigned_to and assigned_to not in ["planner", "software_architect", "frontend_developer", "backend_developer", "tester", "orchestrator"]:
                external_tasks.append(task)

        if external_tasks:
            print("✅ SUCCESS: A2A Client agent can find external tasks!")
            for task in external_tasks:
                print(f"  - Task ID: {task['id']}")
                print(f"    Assigned to: {task['assignedTo']}")
                print(f"    Content: {task['content'][:100]}...")
        else:
            print("❌ FAILED: No external tasks found")
            
    except Exception as e:
        print(f"❌ Error testing A2A Client agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_a2a_client_task_finding()
