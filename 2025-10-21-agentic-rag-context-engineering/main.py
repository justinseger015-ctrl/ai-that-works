import asyncio
import subprocess
import os
import glob as glob_module
import fnmatch
import re
from pathlib import Path
from typing import Any, Union
from dotenv import load_dotenv  # type: ignore

from baml_client import b
from baml_client import types

# In-memory storage for todos
_todo_store: list[types.TodoItem] = []


def execute_bash(tool: types.BashTool) -> str:
    """Execute a bash command and return the output"""
    try:
        result = subprocess.run(
            tool.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=tool.timeout / 1000 if tool.timeout else 120,  # Convert ms to seconds
            cwd=os.getcwd()
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
            
        return output if output else "Command executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {tool.timeout}ms"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def execute_glob(tool: types.GlobTool) -> str:
    """Find files matching a glob pattern"""
    try:
        search_path = tool.path if tool.path else "."
        pattern = os.path.join(search_path, tool.pattern) if not tool.pattern.startswith("**/") else tool.pattern
        
        matches = glob_module.glob(pattern, recursive=True)
        
        if not matches:
            return f"No files found matching pattern: {tool.pattern}"
        
        # Sort by modification time
        matches.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        
        return "\n".join(matches[:50])  # Limit to first 50 matches
    except Exception as e:
        return f"Error executing glob: {str(e)}"


def execute_grep(tool: types.GrepTool) -> str:
    """Search for pattern in files"""
    try:
        search_path = tool.path if tool.path else "."
        
        # Build rg command
        cmd = ["rg", tool.pattern, search_path, "--files-with-matches"]
        
        if tool.include:
            cmd.extend(["--glob", tool.include])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            files = result.stdout.strip().split("\n")
            return "\n".join(files[:50])  # Limit to first 50 matches
        elif result.returncode == 1:
            return f"No matches found for pattern: {tool.pattern}"
        else:
            return f"Error: {result.stderr}"
    except FileNotFoundError:
        # Fallback to Python's re if rg is not available
        return "Error: ripgrep (rg) not found. Please install ripgrep."
    except Exception as e:
        return f"Error executing grep: {str(e)}"


def execute_ls(tool: types.LSTool) -> str:
    """List files in a directory"""
    try:
        path = Path(tool.path)
        
        if not path.exists():
            return f"Directory not found: {tool.path}"
        
        if not path.is_dir():
            return f"Not a directory: {tool.path}"
        
        items = []
        for item in path.iterdir():
            # Skip ignored patterns
            if tool.ignore:
                skip = False
                for pattern in tool.ignore:
                    if fnmatch.fnmatch(item.name, pattern):
                        skip = True
                        break
                if skip:
                    continue
            
            item_type = "DIR " if item.is_dir() else "FILE"
            items.append(f"{item_type} {item.name}")
        
        items.sort()
        return "\n".join(items) if items else "Empty directory"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def execute_read(tool: types.ReadTool) -> str:
    """Read a file"""
    try:
        path = Path(tool.file_path)
        
        if not path.exists():
            return f"File not found: {tool.file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = tool.offset if tool.offset else 0
        end = start + tool.limit if tool.limit else len(lines)
        
        result_lines = []
        for i, line in enumerate(lines[start:end], start=start + 1):
            # Truncate long lines
            if len(line) > 2000:
                line = line[:2000] + "... [truncated]\n"
            result_lines.append(f"{i:6d}|{line.rstrip()}")
        
        return "\n".join(result_lines) if result_lines else "Empty file"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def execute_edit(tool: types.EditTool) -> str:
    """Edit a file"""
    try:
        path = Path(tool.file_path)
        
        if not path.exists():
            return f"File not found: {tool.file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if tool.replace_all:
            new_content = content.replace(tool.old_string, tool.new_string)
            count = content.count(tool.old_string)
        else:
            if content.count(tool.old_string) > 1:
                return f"Error: old_string is not unique in file (found {content.count(tool.old_string)} occurrences)"
            new_content = content.replace(tool.old_string, tool.new_string, 1)
            count = 1 if tool.old_string in content else 0
        
        if count == 0:
            return f"Error: old_string not found in file"
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Successfully edited {tool.file_path} ({count} replacement(s))"
    except Exception as e:
        return f"Error editing file: {str(e)}"


def execute_multi_edit(tool: types.MultiEditTool) -> str:
    """Edit a file with multiple edits"""
    try:
        path = Path(tool.file_path)
        
        if not path.exists():
            return f"File not found: {tool.file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply edits sequentially
        for i, edit in enumerate(tool.edits):
            if edit.replace_all:
                content = content.replace(edit.old_string, edit.new_string)
            else:
                if content.count(edit.old_string) > 1:
                    return f"Error in edit {i+1}: old_string is not unique (found {content.count(edit.old_string)} occurrences)"
                if edit.old_string not in content:
                    return f"Error in edit {i+1}: old_string not found"
                content = content.replace(edit.old_string, edit.new_string, 1)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully applied {len(tool.edits)} edits to {tool.file_path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"


def execute_write(tool: types.WriteTool) -> str:
    """Write a file"""
    try:
        path = Path(tool.file_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(tool.content)
        
        return f"Successfully wrote {tool.file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def execute_notebook_read(tool: types.NotebookReadTool) -> str:
    """Read a Jupyter notebook"""
    try:
        import json
        path = Path(tool.notebook_path)
        
        if not path.exists():
            return f"Notebook not found: {tool.notebook_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells_output = []
        for i, cell in enumerate(notebook.get('cells', [])):
            cell_type = cell.get('cell_type', 'unknown')
            source = ''.join(cell.get('source', []))
            cells_output.append(f"Cell {i} ({cell_type}):\n{source}\n")
        
        return "\n".join(cells_output) if cells_output else "Empty notebook"
    except Exception as e:
        return f"Error reading notebook: {str(e)}"


def execute_notebook_edit(tool: types.NotebookEditTool) -> str:
    """Edit a Jupyter notebook cell"""
    try:
        import json
        path = Path(tool.notebook_path)
        
        if not path.exists():
            return f"Notebook not found: {tool.notebook_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells = notebook.get('cells', [])
        
        if tool.edit_mode == "delete":
            if 0 <= tool.cell_number < len(cells):
                cells.pop(tool.cell_number)
            else:
                return f"Error: cell index {tool.cell_number} out of range"
        elif tool.edit_mode == "insert":
            if not tool.cell_type:
                return "Error: cell_type is required for insert mode"
            new_cell = {
                'cell_type': tool.cell_type,
                'source': tool.new_source.split('\n'),
                'metadata': {}
            }
            cells.insert(tool.cell_number, new_cell)
        else:  # replace
            if 0 <= tool.cell_number < len(cells):
                cells[tool.cell_number]['source'] = tool.new_source.split('\n')
                if tool.cell_type:
                    cells[tool.cell_number]['cell_type'] = tool.cell_type
            else:
                return f"Error: cell index {tool.cell_number} out of range"
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return f"Successfully edited notebook {tool.notebook_path}"
    except Exception as e:
        return f"Error editing notebook: {str(e)}"


def execute_web_fetch(tool: types.WebFetchTool) -> str:
    """Fetch and process web content"""
    try:
        import requests  # type: ignore
        from bs4 import BeautifulSoup  # type: ignore
        
        response = requests.get(tool.url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Simple markdown conversion (just cleaning up whitespace)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        markdown_content = '\n'.join(lines)
        
        # Truncate if too long
        if len(markdown_content) > 10000:
            markdown_content = markdown_content[:10000] + "\n... [truncated]"
        
        return f"Content from {tool.url}:\n\n{markdown_content}\n\nUser prompt: {tool.prompt}"
    except ImportError:
        return "Error: requests and beautifulsoup4 packages are required for web fetching. Install with: pip install requests beautifulsoup4"
    except Exception as e:
        return f"Error fetching web content: {str(e)}"


def execute_todo_read(tool: types.TodoReadTool) -> str:
    """Read the todo list from in-memory storage"""
    global _todo_store
    
    if not _todo_store:
        return "No todos currently tracked"
    
    todo_summary = []
    for todo in _todo_store:
        status_icon = "✓" if todo.status == "completed" else "→" if todo.status == "in_progress" else "○"
        todo_summary.append(f"{status_icon} [{todo.priority}] {todo.content} (id: {todo.id}, status: {todo.status})")
    
    return f"Current todos ({len(_todo_store)}):\n" + "\n".join(todo_summary)


def execute_todo_write(tool: types.TodoWriteTool) -> str:
    """Write the todo list to in-memory storage"""
    global _todo_store
    
    # Replace entire todo list with new one
    _todo_store = tool.todos
    
    todo_summary = []
    for todo in tool.todos:
        status_icon = "✓" if todo.status == "completed" else "→" if todo.status == "in_progress" else "○"
        todo_summary.append(f"{status_icon} [{todo.priority}] {todo.content} (id: {todo.id})")
    
    return f"Updated {len(tool.todos)} todos:\n" + "\n".join(todo_summary)


def execute_web_search(tool: types.WebSearchTool) -> str:
    """Search the web (stub implementation)"""
    return f"Web search for '{tool.query}' would be executed here. This requires an external search API."


def execute_exit_plan_mode(tool: types.ExitPlanModeTool) -> str:
    """Exit plan mode"""
    return f"Plan presented to user:\n{tool.plan}\n\nWaiting for user approval..."


async def execute_agent(tool: types.AgentTool) -> str:
    """Launch a sub-agent (recursive call)"""
    try:
        print(f"\n🔄 Launching sub-agent: {tool.description}")
        print(f"   Prompt: {tool.prompt[:100]}{'...' if len(tool.prompt) > 100 else ''}")
        
        # Recursively call the agent loop with a lower max_iterations
        result = await agent_loop(tool.prompt, max_iterations=5)
        
        return f"Sub-agent completed:\nTask: {tool.description}\nResult: {result}"
    except Exception as e:
        return f"Sub-agent error: {str(e)}"


async def execute_tool(tool: types.AgentTools) -> str:
    """Execute a tool based on its type using match statement"""
    match tool.action:
        case "Bash":
            return execute_bash(tool)
        case "Glob":
            return execute_glob(tool)
        case "Grep":
            return execute_grep(tool)
        case "LS":
            return execute_ls(tool)
        case "Read":
            return execute_read(tool)
        case "Edit":
            return execute_edit(tool)
        case "MultiEdit":
            return execute_multi_edit(tool)
        case "Write":
            return execute_write(tool)
        case "NotebookRead":
            return execute_notebook_read(tool)
        case "NotebookEdit":
            return execute_notebook_edit(tool)
        case "WebFetch":
            return execute_web_fetch(tool)
        case "TodoRead":
            return execute_todo_read(tool)
        case "TodoWrite":
            return execute_todo_write(tool)
        case "WebSearch":
            return execute_web_search(tool)
        case "ExitPlanMode":
            return execute_exit_plan_mode(tool)
        case "Agent":
            return await execute_agent(tool)
        case other:
            return f"Unknown tool type: {other}"


async def agent_loop(user_message: str, max_iterations: int = 10) -> str:
    """Main agent loop that calls the BAML agent and executes tools"""
    messages: list[types.Message] = [
        types.Message(role="user", message=user_message)
    ]
    
    for iteration in range(max_iterations):
        print(f"\n{'='*60}")
        print(f"Iteration {iteration + 1}")
        print(f"{'='*60}")
        
        # Call the BAML agent
        response = b.AgentLoop(state=messages)
        
        # Check if agent wants to reply to user
        if isinstance(response, str):
            print(f"\n🤖 Agent reply: {response}")
            return response
        
        # Execute tools
        if isinstance(response, list):
            tool_results = []
            
            for tool in response:
                print(f"\n🔧 Executing tool: {tool.action}")
                print(f"   Parameters: {tool.model_dump(exclude={'action'})}")
                
                result = await execute_tool(tool)
                
                print(f"   Result: {result[:200]}{'...' if len(result) > 200 else ''}")
                tool_results.append(result)
            
            # Add tool results to conversation
            tools_message = "\n\n".join([
                f"Tool: {tool.action}\nResult: {result}"
                for tool, result in zip(response, tool_results)
            ])
            
            messages.append(types.Message(role="assistant", message=response[0]))
            messages.append(types.Message(role="user", message=tools_message))
        else:
            print(f"\n⚠️  Unexpected response type: {type(response)}")
            break
    
    print("\n⚠️  Max iterations reached")
    return "Agent reached maximum iterations without completing the task"


def main():
    """Main entry point"""
    print("🤖 BAMMY Agent - Agentic RAG Context Engineering Demo")
    print("=" * 60)
    
    # Example usage
    user_query = 'What directory contains the file "package.json"?'
    print(f"\n📝 User query: {user_query}")
    
    result = asyncio.run(agent_loop(user_query))
    
    print(f"\n{'='*60}")
    print(f"Final result: {result}")
    print(f"{'='*60}")


if __name__ == "__main__":
    load_dotenv()
    main()
