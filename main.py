import os
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENROUTER_ENDPOINT"] = os.getenv("OPENROUTER_ENDPOINT")
# Configure OpenAI with OpenRouter endpoint
model = ChatOpenAI(
    model="openai/gpt-oss-20b",  # or another model available on OpenRouter
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_ENDPOINT"),
)


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


# Augment the LLM with tools
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


def run_agent(user_input: str):
    """Run the agent with a user input and handle tool calls."""
    messages = [HumanMessage(content=user_input)]

    # Agent loop - continue until no more tool calls
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get response from model
        response = model_with_tools.invoke(messages)
        messages.append(response)

        # Check if there are tool calls
        if not response.tool_calls:
            # No more tool calls, return final response
            return response.content

        # Execute each tool call
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            print(f"Calling tool: {tool_name} with args: {tool_args}")

            # Execute the tool
            selected_tool = tools_by_name[tool_name]
            tool_output = selected_tool.invoke(tool_args)

            print(f"Tool output: {tool_output}")

            # Add tool response to messages
            messages.append(ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_id
            ))

    return "Max iterations reached"


def main():
    """Main interactive loop."""
    print("LangChain Agent Demo")
    print("Type 'exit' or 'quit' to end the session")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\nAgent is thinking...")
        response = run_agent(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()