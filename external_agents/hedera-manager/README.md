# Hedera A2A Agent

An A2A (Agent-to-Agent) compliant AI agent that interacts with the Hedera blockchain network. This agent can perform various blockchain operations including account management, token operations, and smart contract interactions.

## Features

- **A2A Protocol Compliant**: Fully implements the Agent-to-Agent protocol for seamless integration
- **Hedera Blockchain Operations**: Interact with Hedera testnet/mainnet
- **LangChain Integration**: Powered by LangChain for advanced agent capabilities
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Streaming Support**: Real-time task updates via Server-Sent Events

## Prerequisites

- Node.js 20+
- Docker and Docker Compose (for containerized deployment)
- Hedera testnet account (get one at https://portal.hedera.com/)
- OpenAI API key or OpenRouter API key

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# A2A Agent Configuration
PORT=9000
AGENT_URL=http://localhost:9000/

# Hedera Network Configuration
ACCOUNT_ID=0.0.xxxxx
PRIVATE_KEY=302e020100300506032b657004220420xxxxxxxx...

# OpenAI/LLM Configuration
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-oss-20b:free
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Local Development

Install dependencies:

```bash
npm install
```

Run the A2A server:

```bash
npm run start
```

The agent will be available at `http://localhost:9000/`

### 3. Docker Deployment

Build and run with Docker Compose:

```bash
# Build the Docker image
npm run docker:build

# Start the agent
npm run docker:up

# Stop the agent
npm run docker:down
```

Or use Docker Compose directly:

```bash
docker-compose up -d
```

## Usage

### Agent Card

The agent's capabilities and metadata are described in its Agent Card, available at:

```
http://localhost:9000/.well-known/agent-card.json
```

### A2A Client Example

Here's how to interact with the Hedera agent using the A2A JavaScript SDK:

```typescript
import { A2AClient } from "@a2a-js/sdk/client";
import { v4 as uuidv4 } from "uuid";

// Connect to the Hedera agent
const client = await A2AClient.fromCardUrl(
  "http://localhost:9000/.well-known/agent-card.json"
);

// Send a message to the agent
const response = await client.sendMessage({
  message: {
    messageId: uuidv4(),
    role: "user",
    parts: [{ 
      kind: "text", 
      text: "What is the balance of account 0.0.12345?" 
    }],
    kind: "message",
  },
});

if ("error" in response) {
  console.error("Error:", response.error.message);
} else {
  const result = response.result;
  if (result.kind === "task") {
    console.log("Task:", result);
  } else {
    console.log("Response:", result.parts[0].text);
  }
}
```

### Streaming Example

For real-time updates, use the streaming API:

```typescript
const stream = client.sendMessageStream({
  message: {
    messageId: uuidv4(),
    role: "user",
    parts: [{ 
      kind: "text", 
      text: "Transfer 10 HBAR to account 0.0.67890" 
    }],
    kind: "message",
  },
});

for await (const event of stream) {
  if (event.kind === "task") {
    console.log(`Task created: ${event.id}`);
  } else if (event.kind === "status-update") {
    console.log(`Status: ${event.status.state}`);
  } else if (event.kind === "message") {
    console.log(`Agent: ${event.parts[0].text}`);
  }
}
```

## Integration with NilCode

To use this agent with the NilCode multi-agent system, configure it in your A2A registry:

### Option 1: Environment Variable

```bash
export A2A_AGENTS='[{"name":"Hedera Agent","base_url":"http://localhost:9000"}]'
```

### Option 2: Configuration File

Create `a2a_agents.json`:

```json
[
  {
    "name": "Hedera Agent",
    "base_url": "http://localhost:9000"
  }
]
```

Then set the config path:

```bash
export A2A_CONFIG_PATH=a2a_agents.json
```

## Hedera Agent Capabilities

The agent can perform various Hedera operations:

- **Account Operations**: Check balances, create accounts, manage account info
- **Token Operations**: Create tokens, transfer tokens, mint/burn tokens
- **Smart Contracts**: Deploy contracts, call contract functions
- **Consensus Service**: Submit messages to HCS topics
- **File Service**: Create and manage files on Hedera

Example requests:

```text
"What is my account balance?"
"Create a new account with an initial balance of 100 HBAR"
"Transfer 50 HBAR to account 0.0.12345"
"Create a new fungible token named MyToken with symbol MTK"
```

## API Endpoints

The agent exposes the following A2A-compliant endpoints:

- `GET /.well-known/agent-card.json` - Agent card metadata
- `POST /message` - Send a message to the agent
- `POST /message/stream` - Send a message and receive streaming updates
- `GET /task/{taskId}` - Get task status
- `DELETE /task/{taskId}` - Cancel a task

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `9000` |
| `AGENT_URL` | Public URL of the agent | `http://localhost:9000/` |
| `ACCOUNT_ID` | Hedera account ID | Required |
| `PRIVATE_KEY` | Hedera account private key | Required |
| `OPENAI_API_KEY` | OpenAI/OpenRouter API key | Required |
| `OPENAI_MODEL` | LLM model to use | `gpt-oss-20b:free` |
| `OPENAI_BASE_URL` | LLM API base URL | `` |
| `NODE_ENV` | Node environment | `production` |

## Health Check

The Docker container includes a health check that verifies the agent is running:

```bash
curl http://localhost:9000/.well-known/agent-card.json
```

## Troubleshooting

### Agent won't start

1. Verify your Hedera credentials are correct
2. Check that the account has sufficient HBAR for operations
3. Ensure your API key is valid

### Connection refused

1. Check that the port (9000) is not already in use
2. Verify firewall settings allow connections on the port
3. In Docker, ensure the port mapping is correct

### LLM errors

1. Verify your API key is valid
2. Check the base URL is correct for your provider
3. Ensure the model name is supported by your provider

## Development

### Project Structure

```
hedera-manager/
├── src/
│   ├── a2a-server.ts           # Main A2A server implementation
│   └── tool-calling-agent.ts   # Original CLI agent
├── Dockerfile                   # Docker image configuration
├── docker-compose.yml           # Docker Compose configuration
├── package.json                 # Node.js dependencies
├── tsconfig.json               # TypeScript configuration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

### Scripts

- `npm run start` - Start the A2A server
- `npm run a2a:server` - Same as start
- `npm run docker:build` - Build Docker image
- `npm run docker:up` - Start with Docker Compose
- `npm run docker:down` - Stop Docker Compose

## License

Apache-2.0

## Support

For issues and questions:
- Hedera Agent Kit: https://github.com/hashgraph/hedera-agent-kit
- A2A Protocol: https://google-a2a.github.io/A2A
- NilCode: https://github.com/jcabrero/nilcode
