class Message {
  role "user" | "assistant"
  message string | AgentTools
}

// class ReplyToUser {
//   action "reply_to_user"
//   message string
// }

type ReplyString = string @assert({{ this[0] != "[" and this[0] != "{" }})

function AgentLoop(state: Message[]) -> AgentTools[] | ReplyString {
  client "openai/gpt-4o-mini"
  prompt #"
    {{ _.role("system") }}
    You are BAMMY. A helpful assistant that can help with pretty much any task.

    {{ ctx.output_format(prefix="Answer with the following format:\n") }}

    {% for message in state %}
    {{ _.role(message.role) }}
    {{ message.message }}
    {% endfor %}
  "#
}

test TestName {
  functions [AgentLoop]
  args {
    state [
      {
          role "user"
          message #"
          what directory contains the file "package.json"?
        "#
      }
    ]
  }
}
