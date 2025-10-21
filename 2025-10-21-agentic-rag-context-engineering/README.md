# Agentic RAG Context Engineering

An agent system built with BAML that can execute various tools using pattern matching.

## Overview

This project demonstrates an agentic system that:
- Uses BAML to define tool schemas and agent behavior
- Implements tool handlers using Python's `match` statement
- Supports 16 different tool types for file operations, code execution, web fetching, and more

## Architecture

### BAML Components

- **`baml_src/agent-tools.baml`**: Defines all tool types with full descriptions embedded in `@description` annotations
- **`baml_src/agent.baml`**: Defines the agent loop function that decides which tools to call
- **`main.py`**: Python implementation with tool handlers using pattern matching

### Tool Types

The agent supports the following tools:

1. **AgentTool** - Launch recursive sub-agents (fully implemented)
2. **BashTool** - Execute bash commands (fully implemented)
3. **GlobTool** - Find files by glob patterns (fully implemented)
4. **GrepTool** - Search file contents with regex (fully implemented)
5. **LSTool** - List directory contents (fully implemented)
6. **ReadTool** - Read files with line numbers (fully implemented)
7. **EditTool** - Edit files with string replacement (fully implemented)
8. **MultiEditTool** - Multiple edits in one operation (fully implemented)
9. **WriteTool** - Write new files (fully implemented)
10. **NotebookReadTool** - Read Jupyter notebooks (fully implemented)
11. **NotebookEditTool** - Edit Jupyter notebook cells (fully implemented)
12. **WebFetchTool** - Fetch and process web content (requires `requests` + `beautifulsoup4`)
13. **TodoReadTool** - Read todo list (in-memory storage)
14. **TodoWriteTool** - Write todo list (in-memory storage)
15. **WebSearchTool** - Search the web (stub - requires search API)
16. **ExitPlanModeTool** - Exit planning mode

## Tool Handler Pattern

All tools are handled through a single async `execute_tool()` function using Python 3.10+ match statements on the `action` field:

```python
async def execute_tool(tool: types.AgentTools) -> str:
    """Execute a tool based on its type using match statement"""
    match tool.action:
        case "Bash":
            return execute_bash(tool)
        case "Glob":
            return execute_glob(tool)
        case "Agent":
            return await execute_agent(tool)  # Async for recursive calls
        # ... etc for all 16 tools
        case other:
            return f"Unknown tool type: {other}"
```

## Setup

### Prerequisites

- Python 3.10+ (required for match statements)
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

### Installation

```bash
# Install dependencies
uv sync

# Generate BAML client
uv run baml-cli generate
```

### Running

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run the agent
uv run python main.py
```

## Agent Loop

The agent loop:
1. Takes a user message
2. Calls the BAML `AgentLoop` function
3. Executes any tools the LLM requests
4. Feeds tool results back to the LLM
5. Repeats until the LLM replies to the user (or hits max iterations)

## Key Features

### Type-Safe Tool Calling

BAML generates Pydantic models for all tools, ensuring type safety:

```python
class BashTool(BaseModel):
    action: Literal['Bash']
    command: str
    timeout: Optional[int] = None
    description: Optional[str] = None
```

### Rich Tool Descriptions

Each tool includes its full usage documentation in the `@description` annotation, providing the LLM with comprehensive context about when and how to use each tool.

### Modular Tool Handlers

Each tool has its own handler function that can be tested and maintained independently:

```python
def execute_bash(tool: types.BashTool) -> str:
    """Execute a bash command and return the output"""
    try:
        result = subprocess.run(
            tool.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=tool.timeout / 1000 if tool.timeout else 120,
            cwd=os.getcwd()
        )
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"
```

## Dependencies

Core dependencies:
- `baml-py` - BAML Python SDK
- `pydantic` - Data validation
- `typing-extensions` - Type hints support
- `python-dotenv` - Environment variable management

Optional dependencies for specific tools:
- `requests` + `beautifulsoup4` - For WebFetch tool (install with `uv add requests beautifulsoup4`)
- `ripgrep` (system package) - For Grep tool (usually pre-installed)

## In-Memory State

The agent maintains in-memory state for:
- **Todo list** - Stored in `_todo_store` global variable, persists for the lifetime of the process
- **Agent loop** - Supports recursive sub-agent calls with reduced max iterations

## Recursive Sub-Agents

The agent can launch sub-agents recursively to handle complex tasks:

```python
# Main agent (max_iterations=10)
#   └─> Sub-agent (max_iterations=5)
#        └─> Sub-sub-agent (max_iterations=5)
#             └─> ... and so on
```

The `execute_agent` and `execute_tool` functions are async, allowing proper nesting within the event loop. Sub-agents share the same todo list and can coordinate on tasks.

## Example Usage

```python
# Find package.json files
user_query = 'What directory contains the file "package.json"?'
result = asyncio.run(agent_loop(user_query))
```

The agent will:
1. Use GlobTool to find all `package.json` files
2. Analyze the results
3. Reply to the user with the answer

## Project Structure

```
2025-10-21-agentic-rag-context-engineering/
├── baml_src/
│   ├── agent-tools.baml      # Tool type definitions
│   ├── agent.baml             # Agent loop function
│   ├── clients.baml           # LLM client configs
│   └── generators.baml        # Code generation config
├── baml_client/               # Auto-generated BAML client
├── main.py                    # Tool handlers & agent loop
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

## Notes

- The agent uses `gpt-4o-mini` by default (configurable in `agent.baml`)
- Tool handlers include error handling and user-friendly error messages
- Some tools (WebSearch, TodoRead/Write) are stubs requiring external services
- The agent loop has a configurable max iteration limit (default: 10)

