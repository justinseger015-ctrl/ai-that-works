class FeedbackClassification {
  target string @description("The target of the feedback: 'subtitle' or 'image' or 'both'")
  subtitle_feedback string? @description("Specific feedback about the subtitle, if any")
  image_feedback string? @description("Specific feedback about the image/graphic, if any")
  rationale string @description("Explanation of why the feedback was categorized this way")
}


function ClassifyFeedback(
  title: string,
  description: string,
  current_subtitle: string,
  feedback: string
) -> FeedbackClassification {
  client Gemini25Flash
  prompt #"
    You are helping categorize user feedback for a podcast thumbnail generation system.

    The system generates two things:
    1. A SUBTITLE - A short tagline (8 words or fewer) that captures the episode theme
    2. An IMAGE - A visual graphic placed between two characters that represents the episode title

    Current episode details:
    Title: {{ title }}
    Description: {{ description }}
    Current Subtitle: {{ current_subtitle }}

    User Feedback: {{ feedback }}

    Analyze the feedback and determine:
    - Does it relate to the SUBTITLE (the text tagline)?
    - Does it relate to the IMAGE (the visual graphic)?
    - Or does it relate to BOTH?

    Extract specific feedback for each component if applicable.

    Examples:
    - "The subtitle is too generic" → target: "subtitle"
    - "The icon doesn't match the theme" → target: "image"
    - "It's too boring overall" → target: "both"
    - "I don't like the wording, and the graphic is confusing" → target: "both"

    {{ ctx.output_format }}
  "#
}
