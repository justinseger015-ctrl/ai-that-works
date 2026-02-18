// Email generation functions for AI That Works episodes

// Example email template for reference
template_string EmailExample() #"
    Hello First Name,

    This weeks 🦄 ai that works session was on "Entity Resolution: Extraction, Deduping, and Enriching"!

    The full recording, code, and diagrams from the session are now available on GitHub:
    https://github.com/hellovai/ai-that-works

    We covered a lot on building robust entity resolution pipelines. Here's a super quick recap:

    It's a Multi-Stage System, Not Just One Prompt: Effective entity resolution involves an initial LLM pass for extraction, crucial validation against your existing database of known entities (because you can't just stuff your whole DB into the prompt!), and then targeted enrichment for anything new or unconfirmed.
    Your Entity Database is a Living Asset: The real power comes from continuously growing and refining your canonical entity list. For new entities (like "BoundaryML" from our example), kick off an asynchronous enrichment pipeline – think LLM-powered research and web search – with a review process to keep your master list accurate and evolving.

    If you remember one thing from this session:
    Entity Resolution is an engineered system. It's an initial LLM pass for extraction, robust validation logic against your known entities, and a separate, resilient pipeline to research, verify, and add new entities to your database over time.

    We also had a fascinating session last week about "Cracking the Prompting Interview" for algorithms to make prompts better, video/whiteboards/code are on the Github!

    Our next session tomorrow will be all about "Building an AI Content Pipeline" – exploring how to use an AI pipeline to write emails like this from zoom recordings and transcripts.
    Sign up here: https://lu.ma/zcf5c8yd
    If you have any questions, reply to this email or ask on Discord: https://www.boundaryml.com/discord. We read every message! Happy coding 🧑‍💻

    Vaibhav & Dex
"#

// Intermediate structure extracted from transcript
class EmailStructure {
  subject string
  we_covered string @description(#"
    Fill in the blank for: "We covered a lot on ______. Here's a quick recap:"
  "#)
  quick_recap string[] @description(#"
    2-3 key bullet points summarizing the main concepts covered
  "#)
  one_thing_to_remember string @description(#"
    The single most important takeaway from the session
  "#)
  next_session string @description(#"
    Information about the tomorrow's episode if mentioned, otherwise leave empty
  "#)
}

// Final email output
class EmailDraft {
  subject string
  body string @description(#"
    The full email body in markdown format
  "#)
  call_to_action string @description(#"
    The primary call to action for the reader
  "#)
}

// Stage 1: Extract structured bullet points from raw inputs
function ExtractEmailStructure(
  transcript: string,
  episode_title: string,
  episode_description: string
) -> EmailStructure {
  client Gemini25Flash
  prompt #"
    {{ _.role('user') }}
    You are extracting key information from an AI That Works episode to create an email newsletter.

    Episode Title: {{ episode_title }}

    Episode Description:
    {{ episode_description }}

    Full Transcript:
    {{ transcript }}

    {{ _.role('user') }}
    Extract the key information for the email newsletter. Focus on:
    1. A compelling subject line that captures the episode topic
    2. What the session covered (concise, fill-in-the-blank style)
    3. 2-3 key bullet points with the main insights
    4. The single most important takeaway
    5. Any mention of upcoming sessions

    {{ ctx.output_format }}

    Reference this example email for style and tone:
    {{ EmailExample() }}
  "#
}

// Stage 2: Compose the final email from structured data
function ComposeEmail(structure: EmailStructure) -> EmailDraft {
  client Gemini25Flash
  prompt #"
    {{ _.role('user') }}
    Transform this structured email data into a polished email newsletter.

    Subject: {{ structure.subject }}

    We covered a lot on {{ structure.we_covered }}. Here's a quick recap:

    Key Points:
    {% for point in structure.quick_recap %}
    - {{ point }}
    {% endfor %}

    One thing to remember:
    {{ structure.one_thing_to_remember }}

    {% if structure.next_session %}
    Tomorrow's episode:
    {{ structure.next_session }}
    {% endif %}

    {{ _.role('user') }}
    Write a professional, friendly email following this style and format exactly:
    {{ EmailExample() }}

    Important:
    - Keep the friendly, conversational tone
    - Include the GitHub link: https://github.com/hellovai/ai-that-works
    - Include the Discord link: https://www.boundaryml.com/discord
    - Sign off as "Vaibhav & Dex"
    - Use the 🦄 emoji in the opening
    - Use the 🧑‍💻 emoji at the end

    {{ ctx.output_format }}
  "#
}

// AI pattern identified in the email
class AIPattern {
  pattern string @description("The specific pattern or element that sounds AI-generated")
  example string @description("An example from the email that demonstrates this pattern")
  rationale string @description("Why this pattern makes the email sound artificial")
}

// Stage 3: Identify AI slop patterns in the composed email
function IdentifyAIPatterns(draft: EmailDraft) -> AIPattern[] {
  client Gemini25Flash
  prompt #"
    {{ _.role('user') }}
    The following email sounds like AI slop. Identify the patterns and elements of this email that make it sound like a human did not write it.

    Subject: {{ draft.subject }}

    Body:
    {{ draft.body }}

    Call to action: {{ draft.call_to_action }}

    {{ _.role('user') }}
    Analyze the email and identify specific patterns that make it sound AI-generated. For each pattern:
    1. Name the pattern (e.g., "overuse of em-dashes", "repetitive structure", "generic phrases")
    2. Provide a specific example from the email
    3. Explain why this makes it sound artificial

    {{ ctx.output_format }}
  "#
}

// Stage 4: Fix identified AI patterns to make the email sound human-written
function FixAIPatterns(draft: EmailDraft, patterns: AIPattern[]) -> EmailDraft {
  client Gemini25Flash
  prompt #"
    {{ _.role('user') }}
    The following email was written by AI and it sounds like AI slop. Fix the following patterns in the email to make it sound like a human wrote it.

    Original email:
    Subject: {{ draft.subject }}

    Body:
    {{ draft.body }}

    Call to action: {{ draft.call_to_action }}

    Patterns to fix:
    {% for pattern in patterns %}
    - {{ pattern.pattern }}: {{ pattern.rationale }}
      Example: "{{ pattern.example }}"
    {% endfor %}

    {{ _.role('user') }}
    Rewrite the email fixing all the identified patterns. Keep the same core information and structure, but make it sound like a human actually wrote it.

    Important:
    - Keep the friendly, conversational tone
    - Include the GitHub link: https://github.com/hellovai/ai-that-works
    - Include the Discord link: https://www.boundaryml.com/discord
    - Sign off as "Vaibhav & Dex"
    - Keep the 🦄 emoji in the opening
    - Keep the 🧑‍💻 emoji at the end

    {{ ctx.output_format }}
  "#
}

// Test for ExtractEmailStructure
test ExtractEmailStructureTest {
  functions [ExtractEmailStructure]
  args {
    transcript #"
      Welcome everyone to AI That Works! Today we're talking about prompt engineering best practices.

      The key thing to understand is that prompts are not magic incantations. They're instructions.

      First principle: Be specific. Don't say "write something good" - say exactly what you want.

      Second principle: Provide examples. Show the model what good output looks like.

      Third principle: Iterate. Your first prompt won't be perfect. Test and refine.

      If you take away one thing: treat prompt engineering like software engineering.
      Use version control, test systematically, and document your prompts.

      Tomorrow we'll cover structured outputs with BAML!
    "#
    episode_title "Prompt Engineering Best Practices"
    episode_description "Learn the fundamentals of effective prompt engineering for production AI systems."
  }
}

// Test for ComposeEmail
test ComposeEmailTest {
  functions [ComposeEmail]
  args {
    structure {
      subject "Prompt Engineering Best Practices - AI That Works Session Recap"
      we_covered "prompt engineering fundamentals for production AI systems"
      quick_recap [
        "Be specific with your instructions - prompts are instructions, not magic incantations",
        "Provide examples to show the model what good output looks like",
        "Iterate systematically - test and refine your prompts like software"
      ]
      one_thing_to_remember "Treat prompt engineering like software engineering: use version control, test systematically, and document your prompts."
      next_session "Tomorrow we'll cover structured outputs with BAML!"
    }
  }
}
