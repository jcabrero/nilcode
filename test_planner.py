"""Quick test for the planner agent"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.agents.planner import create_planner_agent
from src.state.agent_state import create_initial_state
import os

# Create planner
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENROUTER_ENDPOINT")

print("Creating planner agent...")
planner = create_planner_agent(api_key, base_url)

# Test with a simple request
request = "Create a simple calculator function with add and subtract operations"
state = create_initial_state(request)

print(f"\nTesting planner with: {request}\n")

result = planner(state)

print(f"\n✅ Planner completed!")
print(f"Tasks created: {len(result.get('tasks', []))}")
print(f"\nTasks:")
for task in result.get('tasks', []):
    print(f"  - [{task['assignedTo']}] {task['content']}")
print(f"\nPlan: {result.get('plan', '')[:300]}")
