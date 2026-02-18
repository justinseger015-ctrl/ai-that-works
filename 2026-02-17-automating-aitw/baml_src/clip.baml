// High-impact clip extraction from episode transcripts

// Represents a timestamp in the transcript (e.g., "33:46.326")
class Timestamp {
  minutes int
  seconds int
  milliseconds int @description("Optional, defaults to 0")
}

// A high-impact clip extracted from the transcript
class HighImpactClip {
  rationale string @description(#"
    Explain why this clip would be high-impact:
    - What key insight or takeaway does it contain?
    - Why would this resonate with viewers?
    - How does it relate to the main themes of the episode?
  "#)
  start_timestamp string @description("The timestamp where the clip starts, e.g., '33:46'")
  end_timestamp string @description("The timestamp where the clip ends, e.g., '35:15'")
  speaker string @description("The primary speaker in this clip")
  transcript_excerpt string @description(#"
    The exact text from the transcript that should be included in the clip.
    Include speaker names and timestamps as they appear in the original.
  "#)
  hook string @description("A short, punchy summary (1-2 sentences) that could be used as a caption or title for the clip")
}

// Extract high-impact clips from a transcript given the key takeaways
function ExtractHighImpactClips(
  transcript: string,
  episode_title: string,
  key_takeaways: string[],
  one_thing_to_remember: string
) -> HighImpactClip[] {
  client Gemini25Flash
  prompt #"
    {{ _.role('user') }}
    You are finding the most impactful clip from an AI That Works episode transcript.

    Episode Title: {{ episode_title }}

    Key Takeaways from this episode:
    {% for takeaway in key_takeaways %}
    - {{ takeaway }}
    {% endfor %}

    The one thing to remember from this episode:
    {{ one_thing_to_remember }}

    Full Transcript:
    {{ transcript }}

    {{ _.role('user') }}
    Find the THREE best portions of this transcript that would make high-impact clips for social media or promotional use.

    Each high-impact clip should:
    1. Be self-contained and understandable without additional context
    2. Contain a concrete insight, surprising or counterintuitive fact, or actionable advice
    3. Should be an "aha" moment - a moment where the speaker has a "lightbulb moment" or breakthrough realization
    4. Be succinct - less than 60 seconds when spoken (roughly 120-180 words)
    5. Relate directly to one of the key takeaways
    6. Have a clear "hook" that grabs attention
    7. Avoid rambling setup - get to the point quickly

    Look for moments where the speakers:
    - Share a surprising insight or counterintuitive advice
    - Explain something complex in a simple, memorable way
    - Give a concrete example that illustrates an abstract concept
    - Have a "lightbulb moment" or breakthrough realization
    - State a strong, quotable opinion

    IMPORTANT:
    - Return exactly 3 clips, ordered from most impactful to least impactful
    - The clips should be less than 60 seconds when spoken (roughly 120-180 words)
    - The clips should not overlap - pick different moments from the transcript
    - Include the exact transcript text including speaker names and timestamps as they appear in the original

    {{ ctx.output_format }}
  "#
}

// Test for ExtractHighImpactClips
test ExtractHighImpactClipsTest {
  functions [ExtractHighImpactClips]
  args {
    transcript #"
      Dex (05:30.123)
      So the key thing about prompts is that they're not magic.

      Vaibhav (05:35.456)
      Exactly. And this is what people get wrong. They think if they just find the right words, the model will suddenly work perfectly.

      Dex (05:42.789)
      Right, it's like they're looking for an incantation.

      Vaibhav (05:45.012)
      But really, prompts are just instructions. The clearer you are about what you want, the better the output. It's not about finding magic words, it's about being specific.

      Dex (05:55.345)
      And that's why iteration matters so much. Your first prompt is never going to be perfect.

      Vaibhav (06:01.678)
      Never. You have to test, see what works, refine. It's software engineering, not poetry.
    "#
    episode_title "Prompt Engineering Best Practices"
    key_takeaways [
      "Prompts are instructions, not magic incantations",
      "Be specific about what you want",
      "Iterate and refine your prompts systematically"
    ]
    one_thing_to_remember "Treat prompt engineering like software engineering: test, iterate, and be specific."
  }
}
