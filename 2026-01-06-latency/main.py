"""
Minimal synchronous agent for latency optimization experiments.
No streaming, no parallelism, no sub-agents - just a simple loop.
"""
import subprocess
import os
import glob as glob_module
from pathlib import Path

from dotenv import load_dotenv
from baml_client import types
from baml_client.sync_client import b
from baml_py.errors import BamlValidationError


def execute_bash(tool: types.BashTool, working_dir: str) -> str:
    """Execute a bash command"""
    try:
        timeout = (tool.timeout / 1000) if tool.timeout else 120
        result = subprocess.run(
            tool.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return output if output else "Command executed (no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {tool.timeout}ms"
    except Exception as e:
        return f"Error: {e}"


def execute_glob(tool: types.GlobTool, working_dir: str) -> str:
    """Find files matching a glob pattern"""
    try:
        search_path = tool.path or working_dir
        pattern = os.path.join(search_path, tool.pattern)
        matches = glob_module.glob(pattern, recursive=True)
        if not matches:
            return f"No files found matching: {tool.pattern}"
        # Sort by modification time, limit to 50
        matches.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        return "\n".join(matches[:50])
    except Exception as e:
        return f"Error: {e}"


def execute_grep(tool: types.GrepTool, working_dir: str) -> str:
    """Search for pattern in files using ripgrep"""
    try:
        search_path = tool.path or working_dir
        cmd = ["rg", tool.pattern, search_path, "--files-with-matches"]
        if tool.include:
            cmd.extend(["--glob", tool.include])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            files = result.stdout.strip().split("\n")
            return "\n".join(files[:50])
        elif result.returncode == 1:
            return f"No matches found for: {tool.pattern}"
        else:
            return f"Error: {result.stderr}"
    except FileNotFoundError:
        return "Error: ripgrep (rg) not found"
    except Exception as e:
        return f"Error: {e}"


def execute_read(tool: types.ReadTool, working_dir: str) -> str:
    """Read a file"""
    try:
        path = Path(tool.file_path) if os.path.isabs(tool.file_path) else Path(working_dir) / tool.file_path
        if not path.exists():
            return f"File not found: {tool.file_path}"
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        start = tool.offset or 0
        end = start + (tool.limit or len(lines))
        # Limit to 2000 lines max
        if end - start > 2000:
            end = start + 2000
        result = []
        for i, line in enumerate(lines[start:end], start=start + 1):
            if len(line) > 500:
                line = line[:500] + "...[truncated]\n"
            result.append(f"{i:4d}| {line.rstrip()}")
        if end < len(lines):
            result.append(f"\n... [{len(lines) - end} more lines]")
        return "\n".join(result) if result else "Empty file"
    except Exception as e:
        return f"Error: {e}"


def execute_ls(tool: types.LSTool, working_dir: str) -> str:
    """List directory contents"""
    try:
        path = Path(tool.path) if os.path.isabs(tool.path) else Path(working_dir) / tool.path
        if not path.exists():
            return f"Directory not found: {tool.path}"
        if not path.is_dir():
            return f"Not a directory: {tool.path}"
        items = []
        for item in sorted(path.iterdir()):
            prefix = "[DIR] " if item.is_dir() else "[FILE]"
            items.append(f"{prefix} {item.name}")
        return "\n".join(items) if items else "Empty directory"
    except Exception as e:
        return f"Error: {e}"


def execute_edit(tool: types.EditTool, working_dir: str) -> str:
    """Edit a file with find/replace"""
    try:
        path = Path(tool.file_path) if os.path.isabs(tool.file_path) else Path(working_dir) / tool.file_path
        if not path.exists():
            return f"File not found: {tool.file_path}"
        content = path.read_text()
        if tool.old_string not in content:
            return "Error: old_string not found in file"
        count = content.count(tool.old_string)
        if count > 1:
            return f"Error: old_string found {count} times (must be unique)"
        new_content = content.replace(tool.old_string, tool.new_string, 1)
        path.write_text(new_content)
        return f"Edited {tool.file_path}"
    except Exception as e:
        return f"Error: {e}"


def execute_write(tool: types.WriteTool, working_dir: str) -> str:
    """Write a file"""
    try:
        path = Path(tool.file_path) if os.path.isabs(tool.file_path) else Path(working_dir) / tool.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(tool.content)
        return f"Wrote {tool.file_path}"
    except Exception as e:
        return f"Error: {e}"


def execute_tool(tool: types.AgentTools, working_dir: str) -> str:
    """Dispatch tool execution"""
    match tool.action:
        case "Bash":
            return execute_bash(tool, working_dir)
        case "Glob":
            return execute_glob(tool, working_dir)
        case "Grep":
            return execute_grep(tool, working_dir)
        case "Read":
            return execute_read(tool, working_dir)
        case "LS":
            return execute_ls(tool, working_dir)
        case "Edit":
            return execute_edit(tool, working_dir)
        case "Write":
            return execute_write(tool, working_dir)
        case _:
            return f"Unknown tool: {tool.action}"


def agent_loop(user_message: str, working_dir: str, max_iterations: int = 20) -> str:
    """
    Simple synchronous agent loop.
    Returns the final response message.
    """
    messages: list[types.Message] = [
        types.Message(role="user", content=user_message)
    ]

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        # Call the LLM
        try:
            response = b.AgentLoop(messages=messages, working_dir=working_dir)
        except BamlValidationError as e:
            # If it looks like plain text, treat as reply
            if not e.raw_output.startswith(("{", "[", "```")):
                return e.raw_output
            messages.append(types.Message(
                role="assistant",
                content=f"Invalid response format: {e.raw_output[:200]}"
            ))
            continue
        except Exception as e:
            return f"Error: {e}"

        # Check if done
        if isinstance(response, types.ReplyToUser):
            print(f"Agent: {response.message}")
            return response.message

        # Execute tool
        tool_name = response.action
        print(f"Tool: {tool_name}")

        result = execute_tool(response, working_dir)
        print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")

        # Add to history
        tool_call = f"[Tool: {tool_name}] {response.model_dump_json(exclude={'action'})}"
        messages.append(types.Message(role="assistant", content=tool_call))
        messages.append(types.Message(role="assistant", content=f"[Result] {result}"))

    return "Reached max iterations"


def main():
    load_dotenv()

    working_dir = os.getcwd()
    print(f"Working directory: {working_dir}")
    print("Simple Agent (type 'quit' to exit)")
    print("-" * 40)

    while True:
        try:
            query = input("\n> ").strip()
            if not query:
                continue
            if query.lower() in ("quit", "exit", "q"):
                break

            result = agent_loop(query, working_dir)
            print(f"\n{'='*40}")
            print(f"Final: {result}")
            print('='*40)

        except KeyboardInterrupt:
            print("\nInterrupted")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
