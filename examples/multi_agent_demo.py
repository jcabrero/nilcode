"""
Multi-Agent System Demo

This script demonstrates the multi-agent system with example requests.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.main_agent import create_agent_system


def demo_simple_task():
    """Demo: Simple task to create a calculator function."""
    print("\n" + "=" * 70)
    print("DEMO 1: Simple Calculator Function")
    print("=" * 70)

    agent_system = create_agent_system()

    request = """
    Create a simple calculator module in Python with functions for add, subtract,
    multiply, and divide. Include proper error handling for division by zero.
    """

    final_state = agent_system.run(request)

    print("\n📊 Demo 1 completed!")
    print(f"Status: {final_state.get('overall_status')}")


def demo_web_app():
    """Demo: Create a simple web application."""
    print("\n" + "=" * 70)
    print("DEMO 2: Simple Todo Web App")
    print("=" * 70)

    agent_system = create_agent_system()

    request = """
    Create a simple todo list web application:
    - Frontend: HTML page with a form to add todos and a list to display them
    - Backend: Python FastAPI server with endpoints to create and list todos
    - Use in-memory storage (no database needed)
    """

    final_state = agent_system.run(request)

    print("\n📊 Demo 2 completed!")
    print(f"Status: {final_state.get('overall_status')}")


def demo_interactive():
    """Demo: Interactive mode."""
    print("\n" + "=" * 70)
    print("DEMO 3: Interactive Mode")
    print("=" * 70)
    print("Type your requests below. Type 'exit' to quit.")
    print("-" * 70)

    agent_system = create_agent_system()

    while True:
        user_input = input("\nYour request: ").strip()

        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Exiting interactive mode...")
            break

        if not user_input:
            continue

        try:
            final_state = agent_system.run(user_input)
            print(f"\n✅ Status: {final_state.get('overall_status')}")
        except Exception as e:
            print(f"\n❌ Error: {e}")


def demo_streaming():
    """Demo: Streaming mode to see agent execution in real-time."""
    print("\n" + "=" * 70)
    print("DEMO 4: Streaming Mode")
    print("=" * 70)

    agent_system = create_agent_system()

    request = """
    Create a simple greeting module with a function that takes a name and
    returns a personalized greeting message. Include a test.
    """

    print(f"\nRequest: {request}\n")
    print("Streaming agent execution...\n")

    for state_update in agent_system.stream(request):
        agent_name = list(state_update.keys())[0]
        print(f"\n🔄 Agent '{agent_name}' executed")

    print("\n✅ Streaming demo completed!")


def main():
    """Run the demo."""
    load_dotenv()

    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: No API key found!")
        print("Please set OPENROUTER_API_KEY or OPENAI_API_KEY in your .env file")
        return

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                  Multi-Agent Development System Demo                 ║
║                                                                      ║
║  This system uses multiple specialized AI agents to:                 ║
║  • Plan and break down development tasks                            ║
║  • Write frontend code (HTML, CSS, JavaScript, React)               ║
║  • Write backend code (Python, Node.js, APIs)                       ║
║  • Test and validate code quality                                   ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    print("\nAvailable demos:")
    print("1. Simple Calculator Function")
    print("2. Todo Web Application")
    print("3. Interactive Mode")
    print("4. Streaming Mode")
    print("5. Run all demos")
    print("0. Exit")

    choice = input("\nSelect a demo (0-5): ").strip()

    try:
        if choice == "1":
            demo_simple_task()
        elif choice == "2":
            demo_web_app()
        elif choice == "3":
            demo_interactive()
        elif choice == "4":
            demo_streaming()
        elif choice == "5":
            print("\n🚀 Running all demos...\n")
            demo_simple_task()
            input("\nPress Enter to continue to next demo...")
            demo_web_app()
            input("\nPress Enter to continue to next demo...")
            demo_streaming()
            print("\n✅ All demos completed!")
        elif choice == "0":
            print("Goodbye!")
        else:
            print("Invalid choice!")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
