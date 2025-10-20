# Quick Start Guide

Get up and running with the Multi-Agent Development System in 5 minutes!

## Installation

```bash
# 1. Install dependencies
uv sync

# 2. Set up environment variables
echo "OPENROUTER_API_KEY=your_key_here" >> .env
echo "OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1" >> .env
```

## Run Your First Task

### Option 1: Interactive CLI

```bash
uv run python src/main_agent.py
```

Then type a request like:
```
Create a Python function that calculates fibonacci numbers
```

### Option 2: Demo Script

```bash
uv run python examples/multi_agent_demo.py
```

Choose from pre-built demos or run in interactive mode.

### Option 3: Python Code

```python
from src.main_agent import create_agent_system

# Create system
agent_system = create_agent_system()

# Run a task
result = agent_system.run(
    "Create a simple REST API with FastAPI"
)

print(f"Status: {result['overall_status']}")
```

## Example Tasks

Try these example requests:

### Simple Function
```
Create a Python function that checks if a string is a palindrome
```

### Web Page
```
Create an HTML page with a contact form (name, email, message)
```

### API
```
Create a FastAPI endpoint that returns the current time in JSON format
```

### Full Application
```
Create a simple calculator web app with HTML frontend and Python backend
```

## Understanding the Output

The system will:

1. **Plan** - Break down your request into tasks
2. **Prepare Architecture** - Scaffold directories, configs, and shared assets
3. **Implement** - Write frontend and/or backend code
4. **Test** - Validate code quality and create tests
5. **Summarize** - Provide a comprehensive report

Look for these indicators:

- 🏗️ **Software Architect** - Preparing repository structure
- 🔍 **Planner Agent** - Creating plan
- 💻 **Frontend Developer** - Writing UI code
- ⚙️  **Backend Developer** - Writing server code
- 🧪 **Tester** - Validating and testing
- 🎯 **Orchestrator** - Final summary

## Viewing Results

Generated files are saved in the current directory. Check:
- Created files and directories
- Test results in the output
- Recommendations in the summary

## Common Issues

### API Key Error
```
Error: API key not provided
```
**Solution**: Make sure `.env` file has `OPENROUTER_API_KEY` or `OPENAI_API_KEY`

### Module Not Found
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution**: Run `uv sync` to install dependencies

### Import Errors
```
ImportError: cannot import name 'create_agent_system'
```
**Solution**: Make sure you're running from the project root directory

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore example scripts in [examples/](examples/)
3. Customize agent behavior in [src/agents/](src/agents/)
4. Add new tools in [src/tools/](src/tools/)

## Tips

- **Be specific**: More detailed requests = better results
- **Iterate**: Start simple, then add complexity
- **Review code**: Always check generated code before using
- **Use streaming**: See progress in real-time with `agent_system.stream()`

## Getting Help

- Check examples in `examples/` directory
- Review agent prompts in `src/agents/`
- Look at tool implementations in `src/tools/`
- Read the main README for architecture details

Happy coding! 🚀
