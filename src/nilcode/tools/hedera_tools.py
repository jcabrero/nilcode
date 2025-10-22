"""
Hedera-specific tools for blockchain operations and project setup.

This module provides tools for:
1. Creating Hedera project templates
2. Managing Hedera dependencies
3. Setting up Hedera client configurations
4. Validating Hedera project structure
"""

from typing import Dict, Any, List
from langchain_core.tools import tool
import json
import os


@tool
def create_hedera_package_json(project_name: str, description: str = "Hedera-powered application") -> str:
    """
    Create a package.json file for a Hedera project with all necessary dependencies.
    
    Args:
        project_name: Name of the project
        description: Project description
        
    Returns:
        Success message with created file path
    """
    try:
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": description,
            "main": "dist/index.js",
            "scripts": {
                "build": "tsc",
                "start": "node dist/index.js",
                "dev": "ts-node src/index.ts",
                "test": "jest",
                "lint": "eslint src/**/*.ts",
                "format": "prettier --write src/**/*.ts"
            },
            "dependencies": {
                "hedera-agent-kit": "^1.0.0",
                "@hashgraph/sdk": "^2.7.0",
                "@langchain/openai": "^0.3.0",
                "@langchain/core": "^0.3.0",
                "langchain": "^0.3.0",
                "dotenv": "^16.4.0"
            },
            "devDependencies": {
                "typescript": "^5.3.0",
                "@types/node": "^20.10.0",
                "@types/jest": "^29.5.0",
                "ts-node": "^10.9.0",
                "jest": "^29.7.0",
                "eslint": "^8.55.0",
                "@typescript-eslint/eslint-plugin": "^6.15.0",
                "@typescript-eslint/parser": "^6.15.0",
                "prettier": "^3.1.0"
            },
            "keywords": ["hedera", "blockchain", "ai", "agent", "typescript"],
            "author": "",
            "license": "MIT"
        }
        
        with open("package.json", "w") as f:
            json.dump(package_json, f, indent=2)
            
        return f"✅ Created package.json for Hedera project '{project_name}' with all necessary dependencies"
        
    except Exception as e:
        return f"❌ Error creating package.json: {str(e)}"


@tool
def create_tsconfig_json() -> str:
    """
    Create a tsconfig.json file optimized for Hedera TypeScript projects.
    
    Returns:
        Success message with created file path
    """
    try:
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
                "removeComments": False,
                "noImplicitAny": True,
                "strictNullChecks": True,
                "strictFunctionTypes": True,
                "noImplicitReturns": True,
                "noFallthroughCasesInSwitch": True,
                "noUncheckedIndexedAccess": True,
                "exactOptionalPropertyTypes": True
            },
            "include": [
                "src/**/*"
            ],
            "exclude": [
                "node_modules",
                "dist",
                "**/*.test.ts"
            ]
        }
        
        with open("tsconfig.json", "w") as f:
            json.dump(tsconfig, f, indent=2)
            
        return "✅ Created tsconfig.json optimized for Hedera TypeScript projects"
        
    except Exception as e:
        return f"❌ Error creating tsconfig.json: {str(e)}"


@tool
def create_hedera_env_example() -> str:
    """
    Create a .env.example file with Hedera and AI provider configuration.
    
    Returns:
        Success message with created file path
    """
    try:
        env_content = """# Hedera Configuration
# Get free testnet account at https://portal.hedera.com/dashboard
HEDERA_ACCOUNT_ID="0.0.xxxxx"
HEDERA_PRIVATE_KEY="0x..." # ECDSA encoded private key

# Hedera Network (testnet, mainnet, previewnet)
HEDERA_NETWORK="testnet"

# AI Provider Configuration (choose one)
# OpenAI (requires API key from https://platform.openai.com/api-keys)
OPENAI_API_KEY="sk-proj-..."

# Anthropic Claude (requires API key from https://console.anthropic.com)
# ANTHROPIC_API_KEY="sk-ant-..."

# Groq (free tier available at https://console.groq.com/keys)
# GROQ_API_KEY="gsk_..."

# Ollama (free, local - requires Ollama installed and running)
# OLLAMA_BASE_URL="http://localhost:11434"
# OLLAMA_MODEL="llama3.2"

# Application Configuration
PORT=3000
NODE_ENV="development"
LOG_LEVEL="info"
"""
        
        with open(".env.example", "w") as f:
            f.write(env_content)
            
        return "✅ Created .env.example with Hedera and AI provider configuration"
        
    except Exception as e:
        return f"❌ Error creating .env.example: {str(e)}"


@tool
def create_hedera_client_template() -> str:
    """
    Create a Hedera client configuration template.
    
    Returns:
        Success message with created file path
    """
    try:
        client_code = """import { Client, PrivateKey, AccountId } from '@hashgraph/sdk';
import dotenv from 'dotenv';

dotenv.config();

export class HederaClient {
    private client: Client;
    private accountId: AccountId;
    private privateKey: PrivateKey;

    constructor() {
        // Validate environment variables
        if (!process.env.HEDERA_ACCOUNT_ID) {
            throw new Error('HEDERA_ACCOUNT_ID is required');
        }
        if (!process.env.HEDERA_PRIVATE_KEY) {
            throw new Error('HEDERA_PRIVATE_KEY is required');
        }

        this.accountId = AccountId.fromString(process.env.HEDERA_ACCOUNT_ID);
        this.privateKey = PrivateKey.fromStringECDSA(process.env.HEDERA_PRIVATE_KEY);

        // Initialize client based on network
        const network = process.env.HEDERA_NETWORK || 'testnet';
        switch (network.toLowerCase()) {
            case 'mainnet':
                this.client = Client.forMainnet();
                break;
            case 'previewnet':
                this.client = Client.forPreviewnet();
                break;
            case 'testnet':
            default:
                this.client = Client.forTestnet();
                break;
        }

        this.client.setOperator(this.accountId, this.privateKey);
    }

    getClient(): Client {
        return this.client;
    }

    getAccountId(): AccountId {
        return this.accountId;
    }

    getPrivateKey(): PrivateKey {
        return this.privateKey;
    }

    async getAccountBalance(): Promise<number> {
        try {
            const { AccountBalanceQuery } = await import('@hashgraph/sdk');
            const query = new AccountBalanceQuery()
                .setAccountId(this.accountId);
            
            const balance = await query.execute(this.client);
            return balance.hbars.toNumber();
        } catch (error) {
            console.error('Error getting account balance:', error);
            throw error;
        }
    }

    async getAccountInfo() {
        try {
            const { AccountInfoQuery } = await import('@hashgraph/sdk');
            const query = new AccountInfoQuery()
                .setAccountId(this.accountId);
            
            return await query.execute(this.client);
        } catch (error) {
            console.error('Error getting account info:', error);
            throw error;
        }
    }
}

export default HederaClient;
"""
        
        # Create src directory if it doesn't exist
        os.makedirs("src", exist_ok=True)
        
        with open("src/hedera-client.ts", "w") as f:
            f.write(client_code)
            
        return "✅ Created Hedera client configuration template at src/hedera-client.ts"
        
    except Exception as e:
        return f"❌ Error creating Hedera client template: {str(e)}"


@tool
def create_hedera_agent_template() -> str:
    """
    Create a Hedera AI agent template using the Hedera Agent Kit.
    
    Returns:
        Success message with created file path
    """
    try:
        agent_code = """import { ChatPromptTemplate } from '@langchain/core/prompts';
import { AgentExecutor, createToolCallingAgent } from 'langchain/agents';
import { HederaLangchainToolkit, coreQueriesPlugin } from 'hedera-agent-kit';
import HederaClient from './hedera-client.js';

// AI Provider Factory
function createLLM() {
    // OpenAI
    if (process.env.OPENAI_API_KEY) {
        const { ChatOpenAI } = require('@langchain/openai');
        return new ChatOpenAI({ 
            model: 'gpt-4o-mini',
            apiKey: process.env.OPENAI_API_KEY
        });
    }
    
    // Anthropic Claude
    if (process.env.ANTHROPIC_API_KEY) {
        const { ChatAnthropic } = require('@langchain/anthropic');
        return new ChatAnthropic({ 
            model: 'claude-3-haiku-20240307',
            apiKey: process.env.ANTHROPIC_API_KEY
        });
    }
    
    // Groq
    if (process.env.GROQ_API_KEY) {
        const { ChatGroq } = require('@langchain/groq');
        return new ChatGroq({ 
            model: 'llama3-8b-8192',
            apiKey: process.env.GROQ_API_KEY
        });
    }
    
    // Ollama (local)
    if (process.env.OLLAMA_BASE_URL) {
        const { ChatOllama } = require('@langchain/ollama');
        return new ChatOllama({ 
            model: process.env.OLLAMA_MODEL || 'llama3.2',
            baseUrl: process.env.OLLAMA_BASE_URL
        });
    }
    
    throw new Error('No AI provider configured. Please set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, or OLLAMA_BASE_URL');
}

export class HederaAgent {
    private agentExecutor: AgentExecutor;
    private hederaClient: HederaClient;

    constructor() {
        this.hederaClient = new HederaClient();
        this.initializeAgent();
    }

    private async initializeAgent() {
        // Initialize AI model
        const llm = createLLM();

        // Create Hedera toolkit
        const hederaAgentToolkit = new HederaLangchainToolkit({
            client: this.hederaClient.getClient(),
            configuration: {
                plugins: [coreQueriesPlugin]
            },
        });

        // Create prompt template
        const prompt = ChatPromptTemplate.fromMessages([
            ['system', 'You are a helpful Hedera assistant. You can help users interact with the Hedera network, check balances, transfer tokens, and answer questions about Hedera operations.'],
            ['placeholder', '{chat_history}'],
            ['human', '{input}'],
            ['placeholder', '{agent_scratchpad}'],
        ]);

        // Get tools from toolkit
        const tools = hederaAgentToolkit.getTools();

        // Create the agent
        const agent = createToolCallingAgent({
            llm,
            tools,
            prompt,
        });

        // Create executor
        this.agentExecutor = new AgentExecutor({
            agent,
            tools,
            verbose: true,
        });
    }

    async chat(input: string): Promise<string> {
        try {
            const response = await this.agentExecutor.invoke({ input });
            return response.output;
        } catch (error) {
            console.error('Error in Hedera agent chat:', error);
            return `Sorry, I encountered an error: ${error.message}`;
        }
    }

    async getAccountBalance(): Promise<number> {
        return await this.hederaClient.getAccountBalance();
    }

    async getAccountInfo() {
        return await this.hederaClient.getAccountInfo();
    }
}

export default HederaAgent;
"""
        
        # Create src directory if it doesn't exist
        os.makedirs("src", exist_ok=True)
        
        with open("src/hedera-agent.ts", "w") as f:
            f.write(agent_code)
            
        return "✅ Created Hedera AI agent template at src/hedera-agent.ts"
        
    except Exception as e:
        return f"❌ Error creating Hedera agent template: {str(e)}"


@tool
def create_hedera_main_template() -> str:
    """
    Create a main application template that demonstrates Hedera agent usage.
    
    Returns:
        Success message with created file path
    """
    try:
        main_code = """import HederaAgent from './hedera-agent.js';
import dotenv from 'dotenv';

dotenv.config();

async function main() {
    try {
        console.log('🚀 Starting Hedera AI Agent...');
        
        // Initialize the Hedera agent
        const hederaAgent = new HederaAgent();
        
        // Display account information
        console.log('\\n📊 Account Information:');
        const balance = await hederaAgent.getAccountBalance();
        console.log(`💰 Account Balance: ${balance} HBAR`);
        
        const accountInfo = await hederaAgent.getAccountInfo();
        console.log(`🆔 Account ID: ${accountInfo.accountId.toString()}`);
        console.log(`🔑 Key Type: ${accountInfo.key.keyType}`);
        
        // Example conversation
        console.log('\\n💬 Starting conversation with Hedera agent...');
        console.log('Type "exit" to quit\\n');
        
        // Simple CLI interface (in a real app, you'd use a proper CLI library)
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        const askQuestion = () => {
            rl.question('You: ', async (input) => {
                if (input.toLowerCase() === 'exit') {
                    console.log('👋 Goodbye!');
                    rl.close();
                    return;
                }
                
                try {
                    const response = await hederaAgent.chat(input);
                    console.log(`\\nHedera Agent: ${response}\\n`);
                } catch (error) {
                    console.error(`\\n❌ Error: ${error.message}\\n`);
                }
                
                askQuestion();
            });
        };
        
        askQuestion();
        
    } catch (error) {
        console.error('❌ Failed to start Hedera agent:', error.message);
        console.log('\\n💡 Make sure you have:');
        console.log('1. Set HEDERA_ACCOUNT_ID and HEDERA_PRIVATE_KEY in .env');
        console.log('2. Set one of the AI provider API keys in .env');
        console.log('3. Run "npm install" to install dependencies');
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\\n👋 Shutting down Hedera agent...');
    process.exit(0);
});

// Start the application
main().catch(console.error);
"""
        
        # Create src directory if it doesn't exist
        os.makedirs("src", exist_ok=True)
        
        with open("src/index.ts", "w") as f:
            f.write(main_code)
            
        return "✅ Created main application template at src/index.ts"
        
    except Exception as e:
        return f"❌ Error creating main template: {str(e)}"


@tool
def create_hedera_readme() -> str:
    """
    Create a comprehensive README.md for Hedera projects.
    
    Returns:
        Success message with created file path
    """
    try:
        readme_content = """# Hedera AI Agent

A conversational AI agent that interacts with the Hedera network using the Hedera Agent Kit and LangChain.

## Features

- 🤖 **Conversational AI**: Natural language interaction with Hedera network
- ⛓️ **Hedera Integration**: Full access to Hedera services (Account, Token, Consensus)
- 🔧 **Multiple AI Providers**: Support for OpenAI, Anthropic, Groq, and Ollama
- 📊 **Account Management**: Check balances, account info, and transaction history
- 🪙 **Token Operations**: Transfer tokens, check token balances
- 🔒 **Secure**: Proper private key handling and environment variable management

## Prerequisites

- Node.js 18+ and npm
- Hedera testnet account (get free at [portal.hedera.com](https://portal.hedera.com/dashboard))
- AI provider API key (OpenAI, Anthropic, Groq, or Ollama)

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Configure your .env file:**
   ```env
   # Hedera Configuration
   HEDERA_ACCOUNT_ID="0.0.xxxxx"
   HEDERA_PRIVATE_KEY="0x..."
   HEDERA_NETWORK="testnet"
   
   # AI Provider (choose one)
   OPENAI_API_KEY="sk-proj-..."
   # OR
   ANTHROPIC_API_KEY="sk-ant-..."
   # OR
   GROQ_API_KEY="gsk_..."
   # OR
   OLLAMA_BASE_URL="http://localhost:11434"
   ```

4. **Build and run:**
   ```bash
   npm run build
   npm start
   ```

5. **Start chatting with your Hedera agent!**

## Development

- **Development mode:** `npm run dev`
- **Build:** `npm run build`
- **Lint:** `npm run lint`
- **Format:** `npm run format`
- **Test:** `npm test`

## Usage Examples

### Check Account Balance
```
You: What's my account balance?
Hedera Agent: Your account balance is 100.5 HBAR.
```

### Transfer Tokens
```
You: Transfer 10 HBAR to account 0.0.12345
Hedera Agent: I'll help you transfer 10 HBAR to account 0.0.12345...
```

### Get Account Information
```
You: Tell me about my account
Hedera Agent: Your account ID is 0.0.xxxxx, key type is ECDSA, and you have 100.5 HBAR.
```

## Project Structure

```
src/
├── index.ts              # Main application entry point
├── hedera-client.ts      # Hedera SDK client configuration
└── hedera-agent.ts       # AI agent implementation
```

## Hedera Agent Kit

This project uses the [Hedera Agent Kit](https://github.com/hedera-dev/hedera-agent-kit) which provides:

- **Core Queries Plugin**: Account balance, token info, transaction history
- **Core Account Plugin**: Account creation and management
- **Core Token Plugin**: Token operations and transfers
- **Core Consensus Plugin**: Consensus Service operations

## AI Providers

### OpenAI
- Model: GPT-4o-mini
- Cost: Pay per use
- Setup: Get API key from [platform.openai.com](https://platform.openai.com/api-keys)

### Anthropic Claude
- Model: Claude-3-haiku
- Cost: Pay per use
- Setup: Get API key from [console.anthropic.com](https://console.anthropic.com)

### Groq
- Model: Llama3-8b
- Cost: Free tier available
- Setup: Get API key from [console.groq.com](https://console.groq.com/keys)

### Ollama (Local)
- Model: Llama3.2
- Cost: Free (runs locally)
- Setup: Install [Ollama](https://ollama.com) and run locally

## Security Notes

- Never commit your private keys to version control
- Use environment variables for all sensitive data
- Test on Hedera testnet before using mainnet
- Keep your private keys secure and backed up

## Troubleshooting

### Common Issues

1. **"No AI provider configured"**
   - Make sure you've set one of the AI provider API keys in .env

2. **"HEDERA_ACCOUNT_ID is required"**
   - Set your Hedera account ID in the .env file

3. **"HEDERA_PRIVATE_KEY is required"**
   - Set your Hedera private key in the .env file

4. **"Rate limit exceeded"**
   - Wait a moment and try again, or switch to a different AI provider

### Getting Help

- [Hedera Documentation](https://docs.hedera.com/)
- [Hedera Agent Kit](https://github.com/hedera-dev/hedera-agent-kit)
- [LangChain Documentation](https://js.langchain.com/)

## License

MIT License - see LICENSE file for details.
"""
        
        with open("README.md", "w") as f:
            f.write(readme_content)
            
        return "✅ Created comprehensive README.md for Hedera project"
        
    except Exception as e:
        return f"❌ Error creating README: {str(e)}"


@tool
def validate_hedera_project_structure() -> str:
    """
    Validate that a Hedera project has all required files and structure.
    
    Returns:
        Validation results with any missing files or issues
    """
    try:
        required_files = [
            "package.json",
            "tsconfig.json",
            ".env.example",
            "src/index.ts",
            "src/hedera-client.ts",
            "src/hedera-agent.ts",
            "README.md"
        ]
        
        missing_files = []
        present_files = []
        
        for file_path in required_files:
            if os.path.exists(file_path):
                present_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        # Check package.json for Hedera dependencies
        hedera_deps = []
        if os.path.exists("package.json"):
            with open("package.json", "r") as f:
                package_data = json.load(f)
                dependencies = package_data.get("dependencies", {})
                
                required_deps = [
                    "hedera-agent-kit",
                    "@hashgraph/sdk",
                    "@langchain/openai",
                    "@langchain/core",
                    "langchain",
                    "dotenv"
                ]
                
                for dep in required_deps:
                    if dep not in dependencies:
                        hedera_deps.append(f"Missing dependency: {dep}")
        
        result = f"✅ Hedera Project Validation Results:\\n"
        result += f"Present files ({len(present_files)}): {', '.join(present_files)}\\n"
        
        if missing_files:
            result += f"❌ Missing files ({len(missing_files)}): {', '.join(missing_files)}\\n"
        else:
            result += "✅ All required files present\\n"
        
        if hedera_deps:
            result += f"❌ Dependency issues: {', '.join(hedera_deps)}\\n"
        else:
            result += "✅ All Hedera dependencies present\\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error validating Hedera project: {str(e)}"


# Export all tools
hedera_tools = [
    create_hedera_package_json,
    create_tsconfig_json,
    create_hedera_env_example,
    create_hedera_client_template,
    create_hedera_agent_template,
    create_hedera_main_template,
    create_hedera_readme,
    validate_hedera_project_structure
]
