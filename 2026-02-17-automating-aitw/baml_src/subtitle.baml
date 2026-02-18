class SubtitleContent {
  
  rationale string @description("Rationale around the choice of the subtitle")
  subtitle string @description("The subtitle of the episode")
}


function GenerateSubtitle(title: string, description: string, feedback: string?) -> SubtitleContent {
  client Gemini25Flash
  prompt #"
    You are creating artifacts for a podcast episode of the AI That Works podcast.
    Our goal is to have discussions that demonstrate how to make artificial intelligence
    that works beyond just demos but actually is useful in a production environment.
    Given the topic, generate the following artifacts:
    - A rationale for the choice of the subtitle of the episode
    - A subtitle for the episode

    The subtitle should be 8 words or fewer.

    Here are some examples of titles, descriptions, and subtitles:
    <example>
    Title: Understanding Latency
    Description: This episode is all about latency. How do we stop users from twiddling their thumbs when LLM apis are getting faster, but still too slow? The answer shouldn't be "LLMs will eventually get faster".
    Subtitle: Waiting for LLMs to Respond is Boring
    </example>

    <example>
    Title: Prompt Optimization
    Description: No one wants to write prompts, and we all want systems that "just work". GEPA and DSPy have taken the internet by storm with attempts at making this promise. The question remains, does this work for real problems? We'll dive deep and explain what is GEPA, how does one use it, and what are realistic expectations to set accordingly.
    Subtitle: DSPy, GEPA, and BAML
    </example>

    <example>
    Title: Agentic RAG
    Description: RAG vs. Agentic RAG is the hot new debate at the forefront of AI Engineering. On this week's episode we'll dive deep on the differences, why it matters, and cut through the buzzword hype with hands-on whiteboarding and live working code.
    Subtitle: tools are all you need
    </example>

    Match the tone and style of the examples. The tone should be casual and conversational.

    Here is the title and description of the episode:
    Episode Title: {{ title }}
    Episode Description: {{ description }}

    {% if feedback %}
    IMPORTANT: The user provided the following feedback on the previous subtitle:
    {{ feedback }}

    Please incorporate this feedback and generate an improved subtitle.
    {% endif %}

    {{ ctx.output_format }}
  "#
}

test test_subtitle {
  functions [GenerateSubtitle]
  args {
    title "Applying 12 Factor Agent Principles to Coding Agent SDKs"
    description "We've done a lot of talking in the last few months about prompting coding agents and context engineering w/ markdown files, but today we'll talk about how to squeeze even more out of agents by using agent loops as smaller elements of a deterministic workflow.\nIn this session we'll cover:\n- using the claude agent sdk to stitch together microagent workflows\n- accumulating user rules across context windows\n- json state and structured outputs with zod\n- session continuation and forking vs. direct compaction"
  }
}
