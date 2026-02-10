class Message {
  role "user" | "assistant"
  content string
}

class ReplyToUser {
  action "reply"
  message string
}

class BashTool {
  action "Bash"
  command string
  timeout int? @description("default 120000 if ignored")
}

class GlobTool {
  action "Glob"
  pattern string @alias("glob_pattern") @description("like **/*.py or src/**/*.ts")
  path string? @alias("override_working_directory")
}

class GrepTool {
  action "Grep"
  pattern string @description("Regex pattern to search for")
  path string?
  include string? @alias("file_pattern_filter") @description(#"
    like *.py
  "#)
}

class ReadTool {
  action "Read"
  file_path string @description("Path to file to read") @stream.done
  offset int? @alias("line_offset")
  limit int? @alias("line_limit")
}

class LSTool {
  action "LS"
  path string @alias("directory_path")
}

class EditTool {
  action "Edit"
  file_path string
  old_string string @description("Text to find and replace")
  new_string string 
}

class WriteTool {
  action "Write"
  file_path string
  content string
}

type AgentTools = BashTool | GlobTool | GrepTool | ReadTool | LSTool | EditTool | WriteTool

function AgentLoop(messages: Message[], working_dir: string) -> (AgentTools @stream.done)[] | ReplyToUser {
  client CustomGPT5Mini
  prompt #"
    {{ _.role("system") }}
    You are a helpful coding assistant. You have access to tools for file operations and bash commands.

    Default working_directory: {{ working_dir }}

    When done, reply with your findings

    {{ ctx.output_format }}

    {% for msg in messages %}
    {{ _.role(msg.role) }}
    {{ msg.content }}
    {% endfor %}
  "#
}

test agent_loop {
  functions [AgentLoop]
  args {
    messages [
      { role: "user", content: "read all teh files in the desktop" }
    ]
    working_dir "/Users/vaibhavgupta/Desktop"
  }
}


test agent_loop_read_file {
  functions [AgentLoop]
  args {
    messages [
      { role: "user", content: "read the file /Users/vaibhavgupta/Desktop/test.txt" }
    ]
    working_dir "/Users/vaibhavgupta/Desktop"
  }
}

test agent_loop_read_multiple_files {
  functions [AgentLoop]
  args {
    messages [
      { role: "user", content: "read the files /Users/vaibhavgupta/Desktop/test.txt and /Users/vaibhavgupta/Desktop/test2.txt" }
    ]
    working_dir "/Users/vaibhavgupta/Desktop"
  }
}
