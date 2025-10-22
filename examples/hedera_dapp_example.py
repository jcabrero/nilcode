"""
Example: Creating a Hedera DApp with NilCode

This example demonstrates how to use the NilCode multi-agent system
to create a complete decentralized application (DApp) on Hedera.
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
    Example of creating a Hedera DApp using NilCode.
    """
    print("🌐 Hedera DApp Example with NilCode")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: No API key found!")
        print("Please set OPENROUTER_API_KEY or OPENAI_API_KEY in your environment")
        return
    
    # Create the workflow
    workflow = create_workflow(api_key)
    
    # Example request for a Hedera DApp
    user_request = """
    Create a complete Hedera DApp with the following features:
    
    Frontend (React + TypeScript):
    1. Modern React application with TypeScript
    2. Wallet connection for Hedera accounts
    3. Account balance display and management
    4. Token transfer interface
    5. Transaction history viewer
    6. Real-time account updates
    7. Responsive design with modern UI components
    
    Backend (Node.js + Express):
    1. REST API for Hedera operations
    2. Account management endpoints
    3. Token operation endpoints
    4. Transaction history API
    5. WebSocket support for real-time updates
    6. Authentication and security middleware
    7. Error handling and logging
    
    Hedera Integration:
    1. Hedera SDK integration for all operations
    2. Account creation and management
    3. Token creation and transfer operations
    4. Smart contract interaction capabilities
    5. Consensus Service integration
    6. Multi-signature support
    7. Transaction signing and submission
    
    AI Agent Features:
    1. Conversational interface for Hedera operations
    2. Natural language to Hedera transaction conversion
    3. Smart contract interaction through chat
    4. Automated transaction suggestions
    5. Risk assessment and warnings
    6. Multi-language support for queries
    
    The application should include:
    - Complete project setup with all dependencies
    - Docker configuration for easy deployment
    - Comprehensive documentation
    - Unit tests for critical functionality
    - Environment configuration
    - Security best practices
    - Performance optimization
    """
    
    print(f"📝 User Request: {user_request[:100]}...")
    print("\n🤖 Starting multi-agent workflow...")
    
    # Create initial state
    initial_state = create_initial_state(user_request)
    
    # Add blockchain context to the state
    initial_state.update({
        "blockchain_tech": ["hedera"],
        "hedera_network": "testnet",
        "frontend_tech": ["react", "typescript"],
        "backend_tech": ["nodejs", "express"],
        "ai_provider": "openai",
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
            for file_path in final_state["modified_files"][:15]:  # Show first 15
                print(f"  - {file_path}")
            if len(final_state["modified_files"]) > 15:
                print(f"  ... and {len(final_state['modified_files']) - 15} more files")
        
        print("\n🎉 Hedera DApp project created successfully!")
        print("\nNext steps:")
        print("1. Navigate to the project directory")
        print("2. Copy .env.example to .env and add your credentials")
        print("3. Run 'npm install' to install dependencies")
        print("4. Run 'npm run build' to build the project")
        print("5. Run 'npm start' to start the DApp")
        print("6. Open your browser to interact with the DApp")
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        print("This might be due to:")
        print("- Rate limiting (try again in a moment)")
        print("- Invalid API key")
        print("- Network connectivity issues")


if __name__ == "__main__":
    main()

