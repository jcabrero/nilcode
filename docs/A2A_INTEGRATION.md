# A2A External Agent Integration

This document explains how to integrate external agents using the Agent-to-Agent (A2A) protocol with nilcode.

## Overview

The A2A integration allows nilcode to discover and communicate with external agents running on different servers. This enables:

- **Delegation of specialized tasks** to external expert agents
- **Distributed agent architectures** across multiple services
- **Integration with third-party AI agents** that support the A2A protocol
- **Extensibility** without modifying core nilcode code

## Architecture

### Components

1. **A2A Agent Registry** (`src/nilcode/a2a/registry.py`)
   - Discovers external agents by fetching their agent cards
   - Maintains a registry of available external agents
   - Supports both public and authenticated agent cards

2. **A2A Client Agent** (`src/nilcode/agents/a2a_client.py`)
   - Executes tasks on external agents
   - Handles A2A protocol communication
   - Supports streaming and non-streaming responses

3. **Enhanced Planner** (`src/nilcode/agents/planner.py`)
   - Queries the A2A registry for available external agents
   - Includes external agents in task planning
   - Assigns tasks to external agents based on capabilities

4. **Workflow Integration** (`src/nilcode/main_agent.py`)
   - Initializes A2A registry at startup
   - Routes tasks to A2A client agent when needed
   - Coordinates between internal and external agents

## Configuration

### Option 1: Environment Variable (Inline JSON)

```bash
export A2A_AGENTS='[
  {
    "name": "currency_converter",
    "base_url": "http://localhost:9999",
    "auth_token": "optional-token"
  },
  {
    "name": "weather_service",
    "base_url": "http://localhost:8888"
  }
]'
```

### Option 2: Configuration File

1. Create `a2a_agents.json`:

```json
{
  "external_agents": [
    {
      "name": "currency_converter",
      "base_url": "http://localhost:9999",
      "auth_token": "your-auth-token-if-needed"
    },
    {
      "name": "data_analyzer",
      "base_url": "http://localhost:8888",
      "auth_token": null
    }
  ]
}
```

2. Set the config path:

```bash
export A2A_CONFIG_PATH=a2a_agents.json
```

### Option 3: Programmatic Configuration

```python
from nilcode.a2a.registry import initialize_registry_from_config

# Initialize with specific config file
registry = await initialize_registry_from_config("path/to/config.json")
```

## Agent Card Discovery

The A2A integration follows the A2A protocol for agent discovery:

### Public Agent Card

- **Endpoint**: `{base_url}/.well-known/agent-card.json`
- **Authentication**: None required
- **Purpose**: Advertise basic agent capabilities

### Extended Agent Card (Optional)

- **Endpoint**: `{base_url}/agent-card`
- **Authentication**: Bearer token (if required)
- **Purpose**: Provide additional capabilities for authenticated clients

The registry automatically:
1. Fetches the public agent card
2. Checks if extended card is supported
3. Fetches extended card if auth token is provided
4. Extracts capabilities for task planning

## Usage

### Running with External Agents

1. **Start your external A2A agent server**:
   ```bash
   # Example: Run the a2a-sdk example server
   python your_a2a_server.py
   ```

2. **Configure external agents** (see Configuration above)

3. **Run nilcode**:
   ```bash
   uv run nilcode
   ```

4. **The planner will automatically**:
   - Discover available external agents
   - Include them in task planning
   - Assign tasks based on capabilities

### Example Request

```bash
# Request that could be delegated to external agent
uv run nilcode "Convert 100 USD to EUR"
```

If a `currency_converter` agent is configured, the planner may assign this task to that external agent instead of handling it internally.

## Task Flow

```
User Request
    ↓
Planner Agent
    ├── Queries A2A Registry
    ├── Discovers external agents
    ├── Creates task plan with external agents
    ↓
Orchestrator
    ↓
A2A Client Agent (for external tasks)
    ├── Gets external agent from registry
    ├── Sends message via A2A protocol
    ├── Receives response
    ├── Updates task status
    ↓
Orchestrator (aggregates results)
    ↓
Final Summary
```

## Development

### Creating an A2A-Compatible Agent

Your external agent must:

1. **Implement the A2A protocol**
2. **Provide an agent card** at `/.well-known/agent-card.json`
3. **Handle message send requests**

Example using `a2a-sdk`:

```python
from a2a.server import A2AServer
from a2a.types import AgentCard, Message

# Define your agent card
agent_card = AgentCard(
    name="My Agent",
    description="Does specialized tasks",
    # ... other fields
)

# Create server
server = A2AServer(agent_card=agent_card)

# Handle messages
@server.on_message
async def handle_message(message: Message):
    # Process message and return response
    return Message(
        role="assistant",
        parts=[{"kind": "text", "text": "Response"}]
    )

# Run server
server.run(port=9999)
```

### Testing External Agents

Use the demo script:

```bash
uv run python examples/a2a_integration_demo.py
```

## Troubleshooting

### No External Agents Discovered

**Problem**: Registry shows 0 agents

**Solutions**:
- Verify A2A_AGENTS or A2A_CONFIG_PATH is set
- Check external agent server is running
- Verify agent card endpoint is accessible
- Check logs for connection errors

### Tasks Not Routed to External Agents

**Problem**: Planner doesn't assign tasks to external agents

**Solutions**:
- Ensure agent capabilities are clear in agent card
- Check planner is receiving external agent info
- Verify task description matches agent capabilities
- Review planner logs for external agent discovery

### Communication Errors

**Problem**: A2A client fails to communicate

**Solutions**:
- Verify base_url is correct and accessible
- Check auth_token if using extended card
- Ensure external agent supports A2A protocol
- Review network connectivity

## Example: Currency Converter Agent

Here's a complete example of setting up an external currency converter agent:

### 1. Create the External Agent Server

```python
# currency_agent.py
from a2a.server import A2AServer
from a2a.types import AgentCard, Message

agent_card = AgentCard(
    name="currency_converter",
    description="Converts currency between different denominations",
    metadata={
        "capabilities": ["currency_conversion", "exchange_rates"]
    }
)

server = A2AServer(agent_card=agent_card)

@server.on_message
async def convert_currency(message: Message):
    # Simple currency conversion logic
    text = message.parts[0].text

    # Parse request (simplified)
    if "USD to EUR" in text:
        return Message(
            role="assistant",
            parts=[{"kind": "text", "text": "100 USD = 92 EUR"}]
        )

    return Message(
        role="assistant",
        parts=[{"kind": "text", "text": "Currency conversion processed"}]
    )

if __name__ == "__main__":
    server.run(port=9999)
```

### 2. Configure nilcode

```bash
export A2A_AGENTS='[{"name":"currency_converter","base_url":"http://localhost:9999"}]'
```

### 3. Run Both

```bash
# Terminal 1: Start external agent
python currency_agent.py

# Terminal 2: Run nilcode
uv run nilcode "Convert 100 USD to EUR"
```

## Best Practices

1. **Agent Naming**: Use descriptive names that reflect capabilities
2. **Capabilities**: Clearly document what your agent can do in the agent card
3. **Error Handling**: Implement proper error handling in external agents
4. **Authentication**: Use auth tokens for production external agents
5. **Monitoring**: Log all A2A communications for debugging
6. **Timeouts**: Configure appropriate timeouts for external agent calls

## Security Considerations

- **Authentication**: Always use auth_token for production agents
- **HTTPS**: Use HTTPS for external agent endpoints in production
- **Validation**: Validate inputs before sending to external agents
- **Rate Limiting**: Implement rate limiting on external agents
- **Network Security**: Ensure external agents are on trusted networks

## Future Enhancements

Potential improvements to the A2A integration:

- [ ] Agent capability matching using semantic search
- [ ] Load balancing across multiple instances of same agent
- [ ] Caching of agent card responses
- [ ] Agent health monitoring and failover
- [ ] Support for agent discovery protocols
- [ ] Integration with agent marketplaces

## References

- [A2A Protocol Specification](https://github.com/anthropics/a2a)
- [A2A SDK Documentation](https://pypi.org/project/a2a-sdk/)
- [Example A2A Agents](https://github.com/anthropics/a2a/tree/main/examples)
