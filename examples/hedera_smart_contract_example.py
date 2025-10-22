"""
Example: Creating Hedera Smart Contracts with NilCode

This example demonstrates how to use the NilCode multi-agent system
to create and deploy smart contracts on Hedera.
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
    Example of creating Hedera smart contracts using NilCode.
    """
    print("📜 Hedera Smart Contract Example with NilCode")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: No API key found!")
        print("Please set OPENROUTER_API_KEY or OPENAI_API_KEY in your environment")
        return
    
    # Create the workflow
    workflow = create_workflow(api_key)
    
    # Example request for Hedera smart contracts
    user_request = """
    Create a comprehensive Hedera smart contract project with the following features:
    
    Smart Contract Development:
    1. Token contract (HTS) with custom functionality
    2. Multi-signature wallet contract
    3. Escrow contract for secure transactions
    4. Voting contract for governance
    5. NFT contract with metadata support
    6. DeFi contract for lending/borrowing
    
    Development Environment:
    1. Hardhat or Truffle setup for Hedera
    2. TypeScript configuration
    3. Testing framework with comprehensive test suites
    4. Deployment scripts for testnet/mainnet
    5. Contract verification tools
    6. Gas optimization utilities
    
    Frontend Integration:
    1. React application for contract interaction
    2. Web3 provider integration for Hedera
    3. Contract ABI integration
    4. Transaction signing interface
    5. Event monitoring and display
    6. Error handling and user feedback
    
    Backend Services:
    1. Contract deployment service
    2. Event monitoring service
    3. Transaction indexing service
    4. API for contract interactions
    5. WebSocket for real-time updates
    6. Database for contract state tracking
    
    AI Agent Integration:
    1. Natural language contract interaction
    2. Smart contract code generation
    3. Contract analysis and optimization
    4. Security vulnerability detection
    5. Gas usage optimization suggestions
    6. Contract documentation generation
    
    Security and Testing:
    1. Comprehensive unit tests
    2. Integration tests
    3. Security audit tools
    4. Gas optimization analysis
    5. Contract upgrade mechanisms
    6. Emergency pause functionality
    
    Documentation:
    1. Contract documentation with examples
    2. API documentation
    3. Deployment guides
    4. Security considerations
    5. User guides for frontend
    6. Developer guides for integration
    """
    
    print(f"📝 User Request: {user_request[:100]}...")
    print("\n🤖 Starting multi-agent workflow...")
    
    # Create initial state
    initial_state = create_initial_state(user_request)
    
    # Add blockchain context to the state
    initial_state.update({
        "blockchain_tech": ["hedera", "solidity"],
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
        
        print("\n🎉 Hedera smart contract project created successfully!")
        print("\nNext steps:")
        print("1. Navigate to the project directory")
        print("2. Copy .env.example to .env and add your credentials")
        print("3. Run 'npm install' to install dependencies")
        print("4. Run 'npm run compile' to compile contracts")
        print("5. Run 'npm test' to run the test suite")
        print("6. Run 'npm run deploy' to deploy to testnet")
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        print("This might be due to:")
        print("- Rate limiting (try again in a moment)")
        print("- Invalid API key")
        print("- Network connectivity issues")


if __name__ == "__main__":
    main()

