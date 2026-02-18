// Thumbnail generation functions for podcast episodes

class EpisodeContent {
  topic_content string @description("Fleshed out content of the topic of the episode")
  subtitle string @description("The subtitle of the episode")
}

// Generate a concise subtitle based on the episode title
function GenerateEpisodeContent(title: string) -> EpisodeContent {
  client CustomSonnet4
  prompt #"
    You are creating artifacts for a podcast episode of the AI That Works podcast. 
    Our goal is to have discussions that demonstrate how to make artificial intelligence 
    that works beyond just demos but actually is useful in a production environment.
    Given the topic, generate the following artifacts:
    - A fleshed out content outline for the episode
    - A subtitle for the episode

    The subtitle should be 3-5 words.

    The content outline should first describe the issue or problem referenced in the title in 2-4 sentences.
    Then, it should add a couple of points that will be covered in the episode.

    Here is an example of a content outline:
    <example>
    Title: Understanding Latency
    topic_content: "This episode is all about latency. How do we stop users from twiddling their thumbs when LLM apis are getting faster, but still too slow? The answer shouldn't be "LLMs will eventually get faster".

    We'll talk about:

    - why time-to-first-token is not time-to-useful-content
    - why streaming partially-complete JSON data is hard from a tech perspective
    - balancing perceived performance with actual utility with semantic streaming
    - designing to keep users engaged during longer operations"

    subtitle: "Waiting for LLMs to Respond is Boring"
    </example>

    <example>
    Title: Prompt Optimization

    topic_content: "No one wants to write prompts, and we all want systems that "just work". GEPA and DSPy have taken the internet by storm with attempts at making this promise. 

    The question remains, does this work for real problems? We'll dive deep and explain what is GEPA, how does one use it, and what are realistic expectations to set accordingly."

    </example>

    Match the tone and style of the examples.

    Episode Title: {{ title }}


    {{ ctx.output_format }}
  "#
}

// Generate an image prompt for the episode icon
function GenerateIconPrompt(title: string, subtitle: string, episode_number: string) -> string {
  client CustomSonnet4
  prompt #"
    You are creating an image prompt for a small icon that will appear on a podcast thumbnail.
    The icon should visually represent the episode's topic.
    
    Requirements:
    - The icon should be simple and recognizable at small sizes
    - Use a flat, modern illustration style
    - The icon should work well on a dark blue background
    - Keep it minimal - one main object or symbol
    - Do NOT include text in the icon
    
    Generate a concise image generation prompt (1-2 sentences) for this icon.
    

    {{ _.role("user") }}
    Episode title: {{ title }}
    
    {{ ctx.output_format }}
  "#
}

// Test the subtitle generation
test test_subtitle {
  functions [GenerateEpisodeContent]
  args {
    title "Multimodal Evals"
  }
}

// Test the icon prompt generation
test test_icon_prompt {
  functions [GenerateIconPrompt]
  args {
    title "Semantic Streaming"
  }
}
