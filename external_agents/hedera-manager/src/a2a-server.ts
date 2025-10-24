// A2A Server for Hedera Agent
import express from "express";
import { v4 as uuidv4 } from "uuid";
import type { AgentCard, Message, Task } from "@a2a-js/sdk";
import {
  AgentExecutor,
  RequestContext,
  ExecutionEventBus,
  DefaultRequestHandler,
  InMemoryTaskStore,
} from "@a2a-js/sdk/server";
import { A2AExpressApp } from "@a2a-js/sdk/server/express";
import { ChatOpenAI } from '@langchain/openai';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { AgentExecutor as LangChainAgentExecutor, createToolCallingAgent } from 'langchain/agents';
import { BufferMemory } from 'langchain/memory';
import { Client, PrivateKey } from '@hashgraph/sdk';
import { AgentMode, HederaLangchainToolkit } from 'hedera-agent-kit';
import * as dotenv from 'dotenv';

dotenv.config();

// Define the Hedera Agent Card
const hederaAgentCard: AgentCard = {
  name: "Hedera Agent",
  description: "An AI agent that can interact with the Hedera blockchain network. Capable of creating accounts, transferring HBAR, managing tokens, and interacting with smart contracts.",
  protocolVersion: "0.3.0",
  version: "1.0.0",
  url: process.env.AGENT_URL || "http://localhost:9000/",
  skills: [
    {
      id: "hedera-blockchain",
      name: "Hedera Blockchain Operations",
      description: "Perform operations on the Hedera blockchain including account management, token operations, and smart contract interactions",
      tags: ["blockchain", "hedera", "crypto", "smart-contracts"]
    }
  ],
  capabilities: {
    streaming: true,
    pushNotifications: false,
    stateTransitionHistory: true,
  },
  defaultInputModes: ["text/plain"],
  defaultOutputModes: ["text/plain"],
};

// Hedera Agent Executor
class HederaAgentExecutor implements AgentExecutor {
  private langchainAgent: LangChainAgentExecutor;
  private memory: BufferMemory;

  constructor() {
    // Initialize the LangChain agent (this will be done in init method)
  }

  async init(): Promise<void> {
    console.log('Initializing Hedera Agent...');
    // Initialize OpenAI LLM
    console.log('Setting up LLM...');
    const llm = new ChatOpenAI({
      model: process.env.OPENAI_MODEL || 'gpt-oss-20b:free',
      openAIApiKey: process.env.OPENAI_API_KEY,
      configuration: {
        baseURL: process.env.OPENAI_BASE_URL,
      },
      timeout: 30000,
    });

    // Hedera client setup (Testnet by default)
    // Strip 0x prefix from private key if present
    const privateKeyStr = process.env.PRIVATE_KEY!.startsWith('0x')
      ? process.env.PRIVATE_KEY!.slice(2)
      : process.env.PRIVATE_KEY!;

    console.log('Setting up Hedera client...');
    const client = Client.forTestnet().setOperator(
      process.env.ACCOUNT_ID!,
      PrivateKey.fromStringECDSA(privateKeyStr),
    );

    // Prepare Hedera toolkit
    console.log('Initializing Hedera toolkit...');
    const hederaAgentToolkit = new HederaLangchainToolkit({
      client,
      configuration: {
        tools: [], // empty array loads all tools
        context: {
          mode: AgentMode.AUTONOMOUS,
        },
        plugins: [],
      },
    });

    // Load the chat prompt template
    console.log('Setting up agent prompt and tools...');
    const prompt = ChatPromptTemplate.fromMessages([
      ['system', 'You are a helpful Hedera blockchain assistant. You can help users interact with the Hedera network, manage accounts, tokens, and smart contracts. Always provide clear explanations of what you are doing. Focus especially on the user\'s request and the context of the request related to querying and interacting with the Hedera network. Do not make up information or guess. If you are not sure about the answer, say so and ask the user for more information. '],
      ['placeholder', '{chat_history}'],
      ['human', '{input}'],
      ['placeholder', '{agent_scratchpad}'],
    ]);

    // Fetch tools from toolkit
    const tools = hederaAgentToolkit.getTools();

    // Create the underlying agent
    const agent = createToolCallingAgent({
      llm,
      tools,
      prompt,
    });

    // In-memory conversation history
    this.memory = new BufferMemory({
      memoryKey: 'chat_history',
      inputKey: 'input',
      outputKey: 'output',
      returnMessages: true,
    });

    // Wrap everything in an executor
    this.langchainAgent = new LangChainAgentExecutor({
      agent,
      tools,
      memory: this.memory,
      returnIntermediateSteps: true,
    });
    console.log('Hedera Agent initialization complete!');
  }

  async execute(
    requestContext: RequestContext,
    eventBus: ExecutionEventBus
  ): Promise<void> {
    const { taskId, contextId } = requestContext;

    try {
      // Extract the user's message from the request
      // The message is in requestContext.userMessage, not requestContext.input
      const userMessage = (requestContext as any).userMessage as Message;

      // Debug logging
      console.log('Received request context:', JSON.stringify(requestContext, null, 2));
      console.log('User message:', JSON.stringify(userMessage, null, 2));
      
      if (!userMessage || !userMessage.parts) {
        throw new Error('Invalid message format: missing parts');
      }
      
      const userText = userMessage.parts
        .filter(part => part.kind === 'text')
        .map(part => part.text)
        .join(' ');

      if (!userText) {
        throw new Error('No text content found in message');
      }

      // Create initial task
      const initialTask: Task = {
        kind: "task",
        id: taskId,
        contextId: contextId,
        status: {
          state: "submitted",
          timestamp: new Date().toISOString(),
        },
      };
      eventBus.publish(initialTask);

      // Update to working state
      eventBus.publish({
        kind: "status-update",
        taskId: taskId,
        contextId: contextId,
        status: { state: "working", timestamp: new Date().toISOString() },
        final: false,
      });

      // Execute the LangChain agent with timeout
      console.log('Invoking LangChain agent...');
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('LangChain execution timed out after 30 seconds')), 30000);
      });

      const response = await Promise.race([
        this.langchainAgent.invoke({ input: userText }),
        timeoutPromise
      ]) as any;
      console.log('LangChain agent response received');
      console.log('Response structure:', JSON.stringify(response, null, 2));

      // Extract the response
      const outputText = response?.output ?? JSON.stringify(response);
      console.log('Output text:', outputText);

      // Create response message
      const responseMessage: Message = {
        kind: "message",
        messageId: uuidv4(),
        role: "agent",
        parts: [{ kind: "text", text: outputText }],
        contextId: contextId,
      };

      // Publish the response message
      console.log('Publishing response message...');
      eventBus.publish(responseMessage);

      // Mark task as completed
      console.log('Marking task as completed...');
      eventBus.publish({
        kind: "status-update",
        taskId: taskId,
        contextId: contextId,
        status: { state: "completed", timestamp: new Date().toISOString() },
        final: true,
      });

      console.log('Finishing event bus...');
      eventBus.finished();
      console.log('Task execution complete!');
    } catch (error) {
      console.error('Error executing Hedera agent:', error);

      // Publish error message
      const errorMessage: Message = {
        kind: "message",
        messageId: uuidv4(),
        role: "agent",
        parts: [{
          kind: "text",
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`
        }],
        contextId: contextId,
      };
      eventBus.publish(errorMessage);

      // Mark task as failed
      eventBus.publish({
        kind: "status-update",
        taskId: taskId,
        contextId: contextId,
        status: {
          state: "failed",
          timestamp: new Date().toISOString(),
          reason: error instanceof Error ? error.message : 'Unknown error'
        },
        final: true,
      });

      eventBus.finished();
    }
  }

  async cancelTask(
    taskId: string,
    eventBus: ExecutionEventBus
  ): Promise<void> {
    console.log(`Cancellation requested for task: ${taskId}`);
    // For now, we don't support cancellation of in-flight LangChain operations
    // This would require more sophisticated state management
  }
}

// Bootstrap the A2A server
async function bootstrap(): Promise<void> {
  const port = parseInt(process.env.PORT || '9000', 10);

  // Validate required environment variables
  if (!process.env.ACCOUNT_ID || !process.env.PRIVATE_KEY) {
    throw new Error('ACCOUNT_ID and PRIVATE_KEY environment variables are required');
  }

  // Create and initialize the agent executor
  const agentExecutor = new HederaAgentExecutor();
  await agentExecutor.init();

  // Set up the A2A request handler
  const requestHandler = new DefaultRequestHandler(
    hederaAgentCard,
    new InMemoryTaskStore(),
    agentExecutor
  );

  // Create the Express app with A2A routes
  const appBuilder = new A2AExpressApp(requestHandler);
  const expressApp = appBuilder.setupRoutes(express());

  // Start the server
  expressApp.listen(port, () => {
    console.log(`🚀 Hedera A2A Agent started on http://localhost:${port}`);
    console.log(`📄 Agent Card: http://localhost:${port}/.well-known/agent-card.json`);
  });
}

// Run the server
bootstrap()
  .catch(err => {
    console.error('Fatal error during A2A server bootstrap:', err);
    process.exit(1);
  });
