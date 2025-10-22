"""
Example: Creating a Hedera AI Agent with NilCode

This example demonstrates how to use the NilCode multi-agent system
to create a Hedera-powered AI agent application.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nilcode.main_agent import create_workflow
from nilcode.state.agent_state import create_initial_state


def main():
    """
    Example of creating a Hedera AI agent using NilCode.
    """
    print("🚀 Hedera AI Agent Example with NilCode")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: No API key found!")
        print("Please set OPENROUTER_API_KEY or OPENAI_API_KEY in your environment")
        return
    
    # Create the workflow
    workflow = create_workflow(api_key)
    
    # Example request for a Hedera AI agent
    user_request = """
    Create a Hedera AI agent application that can:
    
    1. Set up a TypeScript/Node.js project with Hedera Agent Kit
    2. Create a conversational AI agent that can interact with Hedera
    3. Implement account balance checking and token operations
    4. Support multiple AI providers (OpenAI, Anthropic, Groq, Ollama)
    5. Include proper error handling and security best practices
    6. Provide a CLI interface for interacting with the agent
    
    The application should be production-ready with:
    - Comprehensive documentation
    - TypeScript configuration
    - Environment variable management
    - Proper project structure
    - Example usage and setup instructions
    """
    
    print(f"📝 User Request: {user_request[:100]}...")
    print("\n🤖 Starting multi-agent workflow...")
    
    # Create initial state
    initial_state = create_initial_state(user_request)
    
    # Add blockchain context to the state
    initial_state.update({
        "blockchain_tech": ["hedera"],
        "hedera_network": "testnet",
        "ai_provider": "openai",  # or detect from environment
    })
    
    try:
        # Execute the workflow
        final_state = workflow.invoke(initial_state)
        
        print("\n✅ Workflow completed successfully!")
        print(f"📊 Overall Status: {final_state.get('overall_status', 'unknown')}")
        
        # Display results
        if "implementation_results" in final_state:
            print("\n📋 Implementation Results:")
            for agent, result in final_state["implementation_results"].items():
                print(f"  {agent}: {result[:100]}...")
        
        # Display modified files
        if "modified_files" in final_state:
            print(f"\n📁 Files Created/Modified: {len(final_state['modified_files'])}")
            for file_path in final_state["modified_files"][:10]:  # Show first 10
                print(f"  - {file_path}")
            if len(final_state["modified_files"]) > 10:
                print(f"  ... and {len(final_state['modified_files']) - 10} more files")
        
        print("\n🎉 Hedera AI agent project created successfully!")
        print("\nNext steps:")
        print("1. Navigate to the project directory")
        print("2. Copy .env.example to .env and add your credentials")
        print("3. Run 'npm install' to install dependencies")
        print("4. Run 'npm run build' to build the project")
        print("5. Run 'npm start' to start the Hedera agent")
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        print("This might be due to:")
        print("- Rate limiting (try again in a moment)")
        print("- Invalid API key")
        print("- Network connectivity issues")


if __name__ == "__main__":
    main()

